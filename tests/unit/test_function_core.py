import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from functions import SEPARATE_FUNCTIONS as sf

# ---------- separate_preprocessing ----------
# helper for getting expected logging interval
def _expected_logging_interval_from_raw(path, sheet):
    path = Path(path)
    if path.suffix.lower() == ".xlsx":
        raw = pd.read_excel(path, sheet_name=sheet) if sheet else pd.read_excel(path)
    else:
        raw = pd.read_csv(path)

    raw_dt = pd.to_datetime(raw.iloc[:, 0], errors="coerce")
    raw_diffs = raw_dt.diff().dropna().dt.total_seconds() / 60.0
    expected = float(raw_diffs.round(6).mode().iloc[0])
    return expected


# ----------  fixed interval preprocessing ----------
def test_preprocess_fixed_interval_xlsx(fixed_input_file, preprocessed_fixed):
    path, sheet, tip_type, tip_mag = fixed_input_file
    assert tip_type == "Fixed Interval"

    tip_dt, tip_depth, log_int, start_dt, end_dt = preprocessed_fixed

    assert isinstance(tip_dt, pd.Series)
    assert isinstance(tip_depth, np.ndarray)
    assert np.isscalar(log_int)
    assert pd.to_datetime(start_dt) <= pd.to_datetime(end_dt)

    expected = _expected_logging_interval_from_raw(path, sheet)
    assert abs(float(log_int) - expected) < 1e-6  # tiny tolerance

    # Zero-depth rows should have been removed before returning
    assert (tip_depth > 0).any()


# ----------  cumulative tips preprocessing ----------
def test_preprocess_cumulative_tips_xlsx(cumulative_input_file, preprocessed_cumulative):
    path, sheet, tip_type, tip_mag = cumulative_input_file
    assert tip_type == "Cumulative Tips"

    tip_dt, tip_depth, log_int, start_dt, end_dt = preprocessed_cumulative

    assert isinstance(tip_dt, pd.Series)
    assert isinstance(tip_depth, np.ndarray)
    assert tip_dt.is_monotonic_increasing
    assert pd.to_datetime(start_dt) <= pd.to_datetime(end_dt)
    # Each tip contributes exactly tip_mag depth in the processed series
    assert np.allclose(tip_depth, tip_mag)


# ----------  Separate Storms Tests ----------
def test_separate_storms_two_storms_simple(simple_tip_series):
    tip_datetime, tip_depth = simple_tip_series

    test_interval = 2.0

    storms, interevent_times = sf.separate_storms(tip_datetime, tip_depth, test_interval)

    assert len(storms) == 2
    assert interevent_times.shape == (1,)
    assert pytest.approx(interevent_times[0], rel=1e-6) == 3.0

    tip_mag = float(tip_depth[0])
    assert np.allclose(tip_depth, tip_mag)  # uniform tip size

    # storm 1
    s0 = storms[0]
    assert s0["indices"] == [0, 1, 2]

    t0 = tip_datetime.iloc[0]
    t2 = tip_datetime.iloc[2]
    expected_dur0 = (t2 - t0).total_seconds() / 3600.0

    expected_mag0 = 3 * tip_mag
    assert pytest.approx(s0["magnitude"], rel=1e-6) == expected_mag0
    assert pytest.approx(s0["duration"], rel=1e-6) == expected_dur0
    assert pytest.approx(s0["intensity_avg"], rel=1e-6) == expected_mag0 / expected_dur0

    # storm 2
    s1 = storms[1]
    assert s1["indices"] == [3, 4]

    t3 = tip_datetime.iloc[3]
    t4 = tip_datetime.iloc[4]
    expected_dur1 = (t4 - t3).total_seconds() / 3600.0

    expected_mag1 = 2 * tip_mag
    assert pytest.approx(s1["magnitude"], rel=1e-6) == expected_mag1
    assert pytest.approx(s1["duration"], rel=1e-6) == expected_dur1
    assert pytest.approx(s1["intensity_avg"], rel=1e-6) == expected_mag1 / expected_dur1


# ----------  test tips filter ----------
def test_separate_filter_removes_small_storm(simple_tip_series):
    """
    Use the simple synthetic series:
    - Two storms separated by a 3-hour gap
    - Storm 1: 3 tips
    - Storm 2: 2 tips
    Filter by minimum magnitude so only the larger storm remains.
    """
    tip_datetime, tip_depth = simple_tip_series

    # First, split into storms with a 2-hour gap threshold
    test_interval = 2.0  # hours
    storms, interevent_times = sf.separate_storms(
        tip_datetime, tip_depth, test_interval
    )

    # Sanity: we start with 2 storms and 1 inter-event time
    assert len(storms) == 2
    assert interevent_times.shape == (1,)

    # Uniform tip size from the fixture
    tip_mag = float(tip_depth[0])
    assert np.allclose(tip_depth, tip_mag)

    # Magnitudes based on tip counts
    mag0 = 3 * tip_mag  # storm 1: 3 tips
    mag1 = 2 * tip_mag  # storm 2: 2 tips

    # Make sure storms have these magnitudes
    assert pytest.approx(storms[0]["magnitude"], rel=1e-6) == mag0
    assert pytest.approx(storms[1]["magnitude"], rel=1e-6) == mag1

    # Choose a min_mag between the two magnitudes --> keep storm 1, drop storm 2
    min_mag = (mag0 + mag1) / 2.0
    min_dur = 0.0  # effectively no duration filter

    filtered_storms, filtered_iet, N_nofilter, N_suppressed = sf.separate_filter(
        storms, interevent_times.copy(), min_mag=min_mag, min_dur=min_dur
    )

    # Before filtering: 2 storms
    assert N_nofilter == 2
    # We expect to suppress exactly 1 storm (the smaller one)
    assert N_suppressed == 1

    # After filtering: only one storm remains
    assert len(filtered_storms) == 1
    # That should be the original "big" storm
    assert filtered_storms[0]["indices"] == [0, 1, 2]

    # When the last storm is removed, there are no inter-event times left
    assert isinstance(filtered_iet, np.ndarray)
    assert filtered_iet.size == 0

# ----------  ISC I/O smoke test ----------
def test_separate_ISC_smoke(simple_tip_series, tmp_path, monkeypatch):
    """
    Smoke test for separate_ISC using a small synthetic tip series.

    We don't require convergence here. Instead, we check that:
    - The function runs without raising.
    - It always returns 7 values.
    - Types/shapes of the outputs are sensible.
    - If it fails to converge, tb0/mean_tb are None and popup_error is called.
    Note: simple tip series in this test does not converge
    """
    tip_datetime, tip_depth = simple_tip_series

    isc_t_max = 48.0       # generous upper limit in hours
    min_depth = 0.0        # no filtering
    min_duration = 0.0

    gap_plots_path = tmp_path / "isc_plots"
    gap_plots_path.mkdir()

    # Capture popup_error calls so tests don't actually open GUI dialogs
    calls = []

    def fake_popup_error(*args, **kwargs):
        calls.append((args, kwargs))

    # Patch sg.popup_error in the SEPARATE_FUNCTIONS module
    monkeypatch.setattr(sf.sg, "popup_error", fake_popup_error)

    result = sf.separate_ISC(
        tip_datetime,
        tip_depth,
        isc_t_max,
        min_depth,
        min_duration,
        str(gap_plots_path),
        "test_isc",
        ".png",
    )

    assert isinstance(result, tuple)
    assert len(result) == 7 # 7 values should be returned

    Fixed_MIT, mean_tb, CV_IET, mean_IET, std_IET, ISC_testintervals, StormNumsRec = result

    # MIT and mean_tb can be float or None (if no convergence)
    assert isinstance(Fixed_MIT, (float, type(None)))
    assert isinstance(mean_tb, (float, type(None)))

    # Arrays should always be numpy arrays with consistent lengths
    assert isinstance(CV_IET, np.ndarray)
    assert isinstance(mean_IET, np.ndarray)
    assert isinstance(std_IET, np.ndarray)
    assert isinstance(ISC_testintervals, np.ndarray)
    assert isinstance(StormNumsRec, np.ndarray)
    assert CV_IET.size == ISC_testintervals.size
    assert mean_IET.size == ISC_testintervals.size
    assert std_IET.size == ISC_testintervals.size
    assert StormNumsRec.ndim == 2
    assert StormNumsRec.shape[1] == 2  # included, suppressed

    # Behavior difference: converged vs not converged
    if Fixed_MIT is None:
        # Non-converged case: warn user via popup_error
        assert len(calls) >= 1
        # No requirement on plots here, since plotting is in the converged branch
    else:
        # Converged: expect at least one plot written
        plot_files = list(gap_plots_path.glob("*.png"))
        assert len(plot_files) >= 1


# Separate Profiler
def test_separate_profiler_basic_profile(simple_tip_series):
    """
    Use the simple synthetic tip series and the first storm to test separate_profiler.

    Check:
    - tip indices match the first storm
    - duration in minutes is consistent with start/end
    - cumulative rainfall is consistent with the tip depths
    - t_fit spans duration_min
    - intensity arrays have expected shape and at least some finite values
    """
    tip_datetime, tip_depth = simple_tip_series

    # First split into storms with the same threshold we used elsewhere
    test_interval = 2.0  # hours
    storms, interevent_times = sf.separate_storms(tip_datetime, tip_depth, test_interval)

    # Sanity: we know this fixture yields 2 storms
    assert len(storms) == 2

    # Use the first storm (indices [0, 1, 2])
    storm_idx = 0
    int_min = 30  # minutes

    iD_Mag, iD_time, R_fit, t_fit, tip_idx, cum_rain, duration_min = sf.separate_profiler(
        storm_idx, storms, tip_datetime, tip_depth, int_min)

    # Tip indices for first storm
    assert tip_idx == [0, 1, 2]

    # Duration in minutes should match start/end of that storm
    start = storms[storm_idx]["start"]
    end = storms[storm_idx]["end"]
    expected_duration_min = int(
        (end - start).total_seconds() / 60.0
    )
    assert duration_min == expected_duration_min

    # Cumulative rainfall: last value should equal sum of tip depths for this storm
    tip_mag = float(tip_depth[0])
    expected_cum = len(tip_idx) * tip_mag
    assert np.isclose(cum_rain[-1], expected_cum, rtol=1e-6)

    # t_fit should start at 0 and end at duration_min
    assert isinstance(t_fit, np.ndarray)
    assert t_fit[0] == 0
    assert t_fit[-1] == duration_min

    # Interpolated cumulative rainfall at the last time should be close to cum_rain[-1]
    assert np.isclose(R_fit[-1], cum_rain[-1], rtol=1e-6)

    # Intensity vectors should be arrays of the right length
    # num_windows = len(t_fit) - int_min (per implementation)
    expected_windows = len(t_fit) - int_min
    assert isinstance(iD_Mag, np.ndarray)
    assert isinstance(iD_time, np.ndarray)
    assert iD_Mag.shape == (expected_windows,)
    assert iD_time.shape == (expected_windows,)

    # At least one finite intensity value should exist
    assert np.isfinite(iD_Mag).any()


# ---------- separate_peak_intensity ----------

def test_separate_peak_intensity_linear_profile():
    """
    Test separate_peak_intensity on a simple linear cumulative rainfall profile.

    Setup:
    - t_fit from 0 to 120 minutes (2 hours) at 1-minute resolution.
    - R_fit = t_fit / 60 --> constant intensity of 1 mm/hr.
    All sliding windows of a given length have the same intensity, so the
    function should pick the *last* window as the peak.
    """
    start_time_abs = pd.Timestamp("2025-01-01 00:00:00")

    # Time in minutes, 0,...1,20
    t_fit = np.arange(0, 121, 1)

    # Linear cumulative rainfall: 1 mm/hr over time
    # R_fit(t) = (t minutes) / 60 = hours * 1 mm/hr
    R_fit = t_fit / 60.0

    intensity_interval = 30  # minutes

    interval_out, peakiD_Mag, peakiD_datetime, peakiD_time_relative = sf.separate_peak_intensity(
        start_time_abs, t_fit, R_fit, intensity_interval)

    # Interval should pass through unchanged
    assert interval_out == intensity_interval

    # Constant intensity profile = expect intensity ~= 1 mm/hr
    assert pytest.approx(peakiD_Mag, rel=1e-6) == 1.0

    # Peak time should be within [interval, last time]
    assert intensity_interval <= peakiD_time_relative <= t_fit[-1]

    # Check the datetime conversion: start + (minutes/1440 days)
    expected_datetime = start_time_abs + pd.Timedelta(minutes=peakiD_time_relative)
    # Implementation uses days = minutes / 1440, so this should match exactly
    assert pd.to_datetime(peakiD_datetime) == expected_datetime

# ---------- separate_outputs ----------

def test_separate_outputs_creates_summary_and_profiles(tmp_path):
    """
    Smoke test for separate_outputs.

    We pass in:
    - one simple storm in the summary `output` list
    - one storm in `storm_profiles` and `storm_raw_profiles`
    and verify that:
    - no error message is returned
    - the summary CSV and All_Storm_Profiles CSV are created
    - they contain expected identifiers/columns.
    """
    output_path = tmp_path
    output_name = "test_outputs"
    storm_id = "Storm1"

    start = pd.Timestamp("2025-01-01 00:00:00")
    end = start + pd.Timedelta(hours=1)

    # Minimal summary info for one storm
    records = [
        {
            "Storm ID": storm_id,
            "Start": start,
            "End": end,
            "Duration (hours)": 1.0,
            "Magnitude (mm)": 1.0,
            "Mean Intensity (mm/hr)": 1.0,
        }
    ]
    output = pd.DataFrame(records)

    # Profile data (already aggregated per storm)
    storm_profiles = {
        storm_id: {
            "Cumulative Storm Time (hours)": [0.0, 0.5, 1.0],
            "30-min Intensity (mm/hr)": [1.0, 1.0, 1.0],
        }
    }

    # Raw per-tip data for the same storm
    storm_raw_profiles = {
        storm_id: {
            "TBRG Time Stamp": [
                start,
                start + pd.Timedelta(minutes=30),
                start + pd.Timedelta(minutes=60),
            ],
            "Cumulative Storm Time (hours)": [0.0, 0.5, 1.0],
            "Cumulative Rainfall (mm)": [0.2, 0.6, 1.0],
        }
    }

    tip_units = "mm"
    I_intervals = [0.5]  # hours; not deeply used in the function logic for this test
    data_opt = True

    # Header parameters: order matters (they index row 1 and 2 for dates)
    header_parameters = {
        "Input File": "dummy_file",
        "Start Date": "2025-01-01",
        "End Date": "2025-01-02",
    }

    plot_start_date = "2025-01-01"
    plot_end_date = "2025-01-02"

    software_metadata = ["SEPARATE unit test"]

    # Columns + units for the summary table header row
    columns = [
        "Storm ID",
        "Start",
        "End",
        "Duration (hours)",
        "Magnitude (mm)",
        "Mean Intensity (mm/hr)",
    ]
    units = ["-", "-", "-", "hours", "mm", "mm/hr"]

    plt_ext = ".png"
    output_ext = ".csv"  # exercise the CSV branch

    errmsg = sf.separate_outputs(
        output=output,
        storm_profiles=storm_profiles,
        storm_raw_profiles=storm_raw_profiles,
        tip_units=tip_units,
        I_intervals=I_intervals,
        data_opt=data_opt,
        header_parameters=header_parameters,
        output_path=str(output_path),
        output_name=output_name,
        plot_int=30,  # 30-min intensity column name
        plt_ext=plt_ext,
        plot_start_date=plot_start_date,
        plot_end_date=plot_end_date,
        software_metadata=software_metadata,
        columns=columns,
        units=units,
        output_ext=output_ext,
    )

    # No error message expected
    assert errmsg is None

    # Summary CSV should exist and contain the storm ID somewhere
    summary_csv = output_path / f"{output_name}_SummaryTable.csv"
    assert summary_csv.exists()
    text = summary_csv.read_text()
    assert "Storm ID" in text
    assert storm_id in text

    # All_Storm_Profiles CSV should exist and have expected columns
    profiles_csv = output_path / f"{output_name}_All_Storm_Profiles.csv"
    assert profiles_csv.exists()

    profiles_df = pd.read_csv(profiles_csv)
    # Should at least contain these key columns from our construction
    assert "Storm ID" in profiles_df.columns
    assert "Cumulative Storm Time (hours)" in profiles_df.columns
    assert "Intensity Profile (mm/hr)" in profiles_df.columns
    # And at least one row
    assert len(profiles_df) >= 1

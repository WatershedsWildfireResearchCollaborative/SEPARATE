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


# fixed interval
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


# cumulative tips
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

# Separate Storms Tests
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


# test filter
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

    # Choose a min_mag between the two magnitudes → keep storm 1, drop storm 2
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

# ISC test
def test_separate_ISC_smoke(simple_tip_series, tmp_path, monkeypatch):
    """
    Smoke test for separate_ISC using a small synthetic tip series.

    We don't require convergence here. Instead, we check that:
    - The function runs without raising.
    - It always returns 7 values.
    - Types/shapes of the outputs are sensible.
    - If it fails to converge, tb0/mean_tb are None and popup_error is called.
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

import pytest
import numpy as np

from functions import SEPARATE_FUNCTIONS as sf


def test_pipeline_fixed_example_preprocess_to_filtered_storms(preprocessed_fixed, base_args):
    """
    End-to-end-ish pipeline test on ExampleData_FixedInterval.xlsx.

    Steps:
      1. Use preprocessed_fixed fixture to load and preprocess the example file.
      2. Partition into storms using the fixed MIT from base_args ("UDM").
      3. Apply separate_filter with min_duration / min_depth settings from base_args.
      4. Check that:
         - storms were identified
         - inter-event times have consistent shape
         - filtering is internally consistent
         - remaining storms honor the min_duration / min_depth thresholds.
    """
    tip_dt, tip_depth, log_int, start_dt, end_dt = preprocessed_fixed

    # Pull thresholds from the same dict you use in GUI tests
    mit_hours = base_args["fixed_mit"]          # 2.0 hrs in your current fixture
    min_depth = base_args["min_depth"] if base_args["min_depth_bool"] else None
    min_dur = base_args["min_duration"] if base_args["min_duration_bool"] else None

    # 1) Storm partitioning
    storms, interevent_times = sf.separate_storms(tip_dt, tip_depth, mit_hours)

    # We should get at least one storm from the record
    assert isinstance(storms, list)
    assert len(storms) > 0

    # IET shape should be (#storms - 1) when there are multiple storms
    if len(storms) > 1:
        assert interevent_times.shape == (len(storms) - 1,)
    else:
        assert interevent_times.size == 0

    # 2) Apply filtering
    storms_filtered, iet_filtered, N_nofilter, N_suppressed = sf.separate_filter(storms, interevent_times,
                                                                                 min_mag=min_depth, min_dur=min_dur)

    # Consistency checks on counts
    assert N_nofilter == len(storms)
    assert N_suppressed == N_nofilter - len(storms_filtered)
    assert iet_filtered.ndim == 1

    # 3) Check that all remaining storms satisfy the thresholds we asked for
    for s in storms_filtered:
        duration = s["duration"]
        magnitude = s["magnitude"]

        if min_dur is not None:
            assert duration > min_dur

        if min_depth is not None:
            assert magnitude > min_depth


def test_pipeline_fixed_example_with_isc(preprocessed_fixed, tmp_path):
    """
    Pipeline test on ExampleData_FixedInterval.xlsx using ISC to select MIT.

    Steps:
      1. Use preprocessed_fixed fixture to load and preprocess the example file.
      2. Run separate_ISC to estimate tb0 (Fixed_MIT) and write ISC plots.
      3. Partition storms using tb0.
      4. Apply a simple filter (optional thresholds).
      5. Sanity-check storm counts, IET shapes, and plot side effects.
    """
    tip_dt, tip_depth, log_int, start_dt, end_dt = preprocessed_fixed

    # Where ISC plots will be written
    gap_plots_path = tmp_path / "isc_plots_fixed_example"
    gap_plots_path.mkdir()

    # Reasonable ISC settings for the example dataset
    isc_t_max = 24.0   # hr
    min_depth = 0.0    # let ISC see everything
    min_dur = 0.0

    # 1) Run ISC to get tb0 (Fixed_MIT) and plots
    tb0, mean_tb, CV_IET, mean_IET, std_IET, ISC_testintervals, StormNumsRec = sf.separate_ISC(
        tip_dt,
        tip_depth,
        isc_t_max,
        min_depth,
        min_dur,
        str(gap_plots_path),
        output_name="ExampleFixed",
        plt_ext=".png")

    # tb0 should be defined for a real dataset
    assert tb0 is not None
    mit_hours = float(np.asarray(tb0))

    # 2) Use tb0 as MIT for partitioning
    storms, interevent_times = sf.separate_storms(tip_dt, tip_depth, mit_hours)

    assert isinstance(storms, list)
    assert len(storms) > 0

    if len(storms) > 1:
        assert interevent_times.shape == (len(storms) - 1,)
    else:
        assert interevent_times.size == 0

    # 3) Apply simple filtering (e.g., no thresholds, just smoke test)
    storms_filtered, iet_filtered, N_nofilter, N_suppressed = sf.separate_filter(storms, interevent_times,
                                                                                 min_mag=None, min_dur=None)

    assert N_nofilter == len(storms)
    assert N_suppressed == 0  # no thresholds -> nothing suppressed
    assert len(storms_filtered) == len(storms)
    assert iet_filtered.shape == interevent_times.shape

    # 4) Ensure ISC produced some plot files as a side effect
    pngs = list(gap_plots_path.glob("*.png"))
    assert len(pngs) >= 1

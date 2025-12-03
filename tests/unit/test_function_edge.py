import pytest
import numpy as np
import pandas as pd
from functions import SEPARATE_FUNCTIONS as sf


# ---------- test empty input ----------
def test_separate_storms_empty_input():
    tip_datetime = pd.Series([], dtype="datetime64[ns]")
    tip_depth = np.array([])
    storms, interevent_times = sf.separate_storms(tip_datetime, tip_depth, test_interval=2.0)
    assert storms == []
    assert isinstance(interevent_times, np.ndarray)
    assert interevent_times.size == 0


# ---------- test single tip ----------
def test_separate_storms_single_tip():
    t0 = pd.Timestamp("2025-01-01 00:00:00")
    tip_datetime = pd.Series([t0])
    tip_depth = np.array([0.2])
    storms, interevent_times = sf.separate_storms(tip_datetime, tip_depth, test_interval=2.0)
    # Current behavior: no storms are returned for a single tip
    assert storms == []
    assert isinstance(interevent_times, np.ndarray)
    assert interevent_times.size == 0


#---------- test large gap to group all storms ----------
def test_separate_storms_all_within_interval_single_storm(simple_tip_series):
    """
    If the test_interval is larger than any gap, all tips should form one storm.
    """
    tip_datetime, tip_depth = simple_tip_series

    # Use a big interval so we never declare a break
    storms, interevent_times = sf.separate_storms(tip_datetime, tip_depth, test_interval=10.0)
    assert len(storms) == 1
    assert storms[0]["indices"] == list(range(len(tip_datetime)))
    assert interevent_times.size == 0


# ---------- Tests very small interval relative to tips ----------
def test_separate_storms_every_gap_exceeds_interval():
    """
    If every gap exceeds the interval, each tip becomes its own storm.
    """
    base = pd.Timestamp("2025-01-01 00:00:00")
    tip_datetime = pd.Series([base + pd.Timedelta(hours=h) for h in [0, 3, 6, 9]])
    tip_depth = np.ones(4) * 0.2

    storms, interevent_times = sf.separate_storms(tip_datetime, tip_depth, test_interval=1.0)

    # Each tip is its own storm
    assert len(storms) == 4
    for i, s in enumerate(storms):
        assert s["indices"] == [i]
        assert s["magnitude"] == pytest.approx(0.2)
        # Duration is zero when there's only one tip
        assert s["duration"] == 0.0

    # Interevent times are the gaps
    assert interevent_times.shape == (3,)
    assert np.allclose(interevent_times, [3.0, 3.0, 3.0])

# ---------- repeating dates with no repeating dates ----------
def test_rename_repeating_dates_no_repeats():
    dates = ["2025-01-01", "2025-01-02"]
    assert sf.rename_repeating_dates(dates) == ["2025-01-01", "2025-01-02"]

# ---------- repeating dates with empty arrays ----------
def test_rename_repeating_dates_empty():
    assert sf.rename_repeating_dates([]) == []

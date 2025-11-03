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
def test_preprocess_fixed_interval_xlsx(fixed_input_file):
    path, sheet, tip_type, tip_mag = fixed_input_file
    # guard
    assert tip_type == "Fixed Interval"

    tip_dt, tip_depth, log_int, start_dt, end_dt = sf.separate_preprocessing(
        path, sheet, tip_type, tip_mag
    )

    assert isinstance(tip_dt, pd.Series)
    assert isinstance(tip_depth, np.ndarray)
    assert np.isscalar(log_int)
    assert pd.to_datetime(start_dt) <= pd.to_datetime(end_dt)

    expected = _expected_logging_interval_from_raw(path, sheet)
    assert abs(float(log_int) - expected) < 1e-6  # a tiny tolerance for floating point

    # Zero-depth rows should have been removed before returning
    assert (tip_depth > 0).any()
    fixed_tip_dt = tip_dt
    fixed_tip_depth = tip_depth
    return fixed_tip_dt, fixed_tip_depth

# cumulative tips
def test_preprocess_cumulative_tips_xlsx(cumulative_input_file):
    path, sheet, tip_type, tip_mag = cumulative_input_file
    assert tip_type == "Cumulative Tips"

    tip_dt, tip_depth, log_int, start_dt, end_dt = sf.separate_preprocessing(
        path, sheet, tip_type, tip_mag
    )

    assert isinstance(tip_dt, pd.Series)
    assert isinstance(tip_depth, np.ndarray)
    assert tip_dt.is_monotonic_increasing
    assert pd.to_datetime(start_dt) <= pd.to_datetime(end_dt)
    # Each tip contributes exactly tip_mag depth in the processed series
    assert np.allclose(tip_depth, tip_mag)
    return tip_dt, tip_depth

# compute MIT
def test_separate_isc_fixed_data(fixed_input_file):
    Fixed_MIT, mean_tb, CV_IET, mean_IET, std_IET, ISC_testintervals, StormNumsRec = sf.separate_ISC(
        tip_datetime, tip_depth, isc_t_max, min_depth, min_duration,
        gap_plots_path, output_name, plt_ext)
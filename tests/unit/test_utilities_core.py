import pytest
from functions import SEPARATE_utilities as su
import numpy as np
import pandas as pd

# ---------- is_numeric ----------
@pytest.mark.parametrize("val, expected", [
    ("3.14", True),
    ("-2.0", True),
    (5, True),
    (None, False),
    ("abc", False),
    ("NaN", True),
    (np.NaN, True)])
def test_is_numeric(val, expected):
    assert su.is_numeric(val) == expected


# ---------- convert_strings_to_floats ----------
def test_convert_strings_to_floats():
    d = {"a": "1.5", "b": "bad", "c": 2, "d": "3"}
    out = su.convert_strings_to_floats(d)
    assert out is d
    assert d == {"a": 1.5, "b": "bad", "c": 2, "d": 3.0}


# ---------- clean_input_dict ----------
def test_clean_input_dict():
    # empty strings should be replaced with None
    d = {"x": "", "y": "   ", "z": "ok", "n": None}
    out = su.clean_input_dict(d)
    assert out["x"] is None
    assert out["y"] is None
    assert out["z"] == "ok"
    assert out["n"] is None


# ---------- is_gui_filled ----------

def test_is_gui_filled():
    vals = {"A": 1, "B": 0, "C": "x", "D": None, "E": ""}
    # everything present and non-empty/non-None
    # test that should pass
    ok, missing = su.is_gui_filled(vals, ["A", "B", "C"])
    assert ok is True and missing == []
    # A test where D and E fail
    ok, missing = su.is_gui_filled(vals, ["D", "E"])
    assert ok is False and set(missing) == {"D", "E"}


# ---------- check_numerical_values ----------
def test_check_numerical_values():
    tf, msg = su.check_numerical_values([[1.0, "a"], ["bad", "b"], (None, "c")])
    assert tf is False
    # message lists offending names line-by-line
    assert "b" in msg and "c" in msg


# ---------- check_for_required_fields ----------

# base_args is defined in the conftest file
# test UDM
def test_udm_required_flds(base_args):
    a = base_args.copy()
    a["Storm_Gap_Type"] = "User-Defined MIT (UDM)"
    req = su.check_for_required_fields(a)
    assert "plot_int" not in req and "min_depth" not in req and "isc_interval" not in req
    for k in ("Storm_Gap_Type","plot_opt","min_duration_bool","min_duration","fixed_mit"):
        assert k in req

# Test ISC
def test_isc_required_flds(base_args):
    a = base_args.copy()
    a["Storm_Gap_Type"] = "Independent Storms Criterion (ISC)"
    req = su.check_for_required_fields(a)
    assert "plot_int" not in req and "min_depth" not in req and "fixed_mit" not in req
    for k in ("Storm_Gap_Type","plot_opt","min_duration_bool","min_duration","isc_interval"):
        assert k in req

# Test TTC — present in UI; core logic later
def test_ttc_required_flds(base_args):
    a = base_args.copy()
    a["Storm_Gap_Type"] = "Travel Time Criterion (TTC)"
    a["plot_opt"] = True
    a["min_depth_bool"] = True
    a["min_duration_bool"] = True
    req = su.check_for_required_fields(a)
    assert "fixed_mit" not in req and "isc_interval" not in req
    for k in ("Storm_Gap_Type","plot_opt","plot_int","min_depth_bool","min_duration_bool","min_depth","min_duration"):
        assert k in req


# ---------- check_input_type ----------
def test_check_input_type(base_args, base_types):
    dtype = base_types.copy()
    # test all pass
    required = list(base_args.keys())
    ok, msg = su.check_input_type(base_args, required, dtype)
    assert ok is True
    assert msg is None
    # test for failures; force args to wrong types
    dtype["fixed_mit"] = "str"
    dtype["min_depth_bool"] = "str"
    dtype["plt_end_date"] = "float"
    required = list(base_args.keys())
    ok, msg = su.check_input_type(base_args, required, dtype)
    assert ok is False

# ---------- validate_tip_type ----------

def test_validate_tip_type_fixed_interval(fixed_input_file):
    path, sheet, tip_type, tip_size = fixed_input_file
    valid, inferred, series = su.validate_tip_type_from_raw_file(path, sheet if sheet else "", tip_type)
    assert inferred == "Fixed Interval"
    assert valid is True
    assert isinstance(series, pd.Series)

def test_validate_tip_type_cumulative(cumulative_input_file):
    path, sheet, tip_type, tip_size = cumulative_input_file
    valid, inferred, series = su.validate_tip_type_from_raw_file(path, sheet if sheet else "", tip_type)
    assert inferred == "Cumulative Tips"
    assert valid is True
    assert isinstance(series, pd.Series)

@pytest.mark.parametrize("fixture_name, expected", [
    ("fixed_input_file", "Fixed Interval"),
    ("cumulative_input_file", "Cumulative Tips"),
])
def test_tip_type_inference_smoke(request, fixture_name, expected):
    path, sheet, tip_type, tip_size = request.getfixturevalue(fixture_name)
    valid, inferred, series = su.validate_tip_type_from_raw_file(path, sheet or "", tip_type)
    assert inferred == expected
    assert valid is True
    assert isinstance(series, pd.Series)
    assert series.notna().all()
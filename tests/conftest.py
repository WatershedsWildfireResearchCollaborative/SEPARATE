
import sys
import pathlib
import pytest
import matplotlib
import pandas as pd
import numpy as np

# Headless plotting for any figures the code may produce
matplotlib.use("Agg")

# Make repo root importable
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# setup some base input parameters
@pytest.fixture
def base_args():
    return {
        "Storm_Gap_Type": "User-Defined MIT (UDM)",
        "plot_opt": False,
        "plot_int": 60,
        "sheet_name": "",
        "plt_end_date": "",
        "plt_start_date": "",
        "min_depth_bool": False,
        "min_duration_bool": True,
        "min_depth": 0.2,
        "min_duration": 0.5,
        "fixed_mit": 2.0,
        "isc_interval": 24,
    }

# set up correct data types
@pytest.fixture
def base_types():
    return {
        "Storm_Gap_Type": "str",
        "plot_opt": "bool",
        "plot_int": "int",
        "sheet_name": "str",
        "plt_end_date": "str",
        "plt_start_date": "str",
        "min_depth_bool": "bool",
        "min_duration_bool": "bool",
        "min_depth": "float",
        "min_duration": "float",
        "fixed_mit": "float",
        "isc_interval": "int",
    }

# make a temporary directory
@pytest.fixture
def tmp_outdir(tmp_path):
    p = tmp_path / "out"
    p.mkdir()
    return p

#%% ---------- Build synthetic data/files ----------

# @pytest.fixture
# def make_times():
#     """
#     Factory to create regular or slightly irregular datetime sequences.
#     Usage:
#         times = make_times(freq="10min", periods=8, irregular=False)
#     """
#     def _make(start="2025-01-01", periods=8, freq="10min", irregular=False):
#         base = pd.date_range(start, periods=periods, freq=freq)
#         if not irregular:
#             return base
#         # Add small jitter in seconds to make intervals non-uniform
#         rng = np.random.default_rng(42)
#         jitter = rng.integers(-120, 180, size=len(base))  # [-2, +3] min
#         return base + pd.to_timedelta(jitter, unit="s")
#     return _make
#
# @pytest.fixture
# def make_csv(tmp_path):
#     """Write a DataFrame to CSV and return the path as str."""
#     def _csv(df, name="data.csv"):
#         fp = tmp_path / name
#         df.to_csv(fp, index=False)
#         return str(fp)
#     return _csv
#
# @pytest.fixture
# def make_xlsx(tmp_path):
#     """Write a DataFrame to XLSX and return (path, sheetname)."""
#     def _xlsx(df, name="data.xlsx", sheet="Sheet1"):
#         fp = tmp_path / name
#         with pd.ExcelWriter(fp, engine="openpyxl") as ew:
#             df.to_excel(ew, index=False, sheet_name=sheet)
#         return str(fp), sheet
#     return _xlsx

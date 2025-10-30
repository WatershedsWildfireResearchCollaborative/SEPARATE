
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

# --- Simple, schema-faithful synthetic data fixtures for SEPARATE ---

import pandas as pd
import numpy as np
import datetime as _dt
import os
import pytest

# ---------- File writers (revived) ----------
@pytest.fixture
def make_csv(tmp_path):
    """Write a DataFrame to CSV and return the path as str."""
    def _csv(df: pd.DataFrame, name: str = "data.csv"):
        fp = tmp_path / name
        df.to_csv(fp, index=False)
        return str(fp)
    return _csv

@pytest.fixture
def make_xlsx(tmp_path):
    """Write a DataFrame to XLSX (with a specific sheet) and return (path, sheet)."""
    def _xlsx(df: pd.DataFrame, name: str = "data.xlsx", sheet: str = "Sheet1"):
        fp = tmp_path / name
        with pd.ExcelWriter(fp, engine="openpyxl") as ew:
            df.to_excel(ew, index=False, sheet_name=sheet)
        return str(fp), sheet
    return _xlsx


# ---------- Canonical schemas (match SEPARATE I/O) ----------
@pytest.fixture(scope="session")
def rainfall_schema():
    """
    Canonical structure mirroring the real example files and the GUI expectations:
    - Fixed Interval: 1-min cadence, 'Depth_mm', optional note column.
    - Cumulative Tips: irregular cadence, 'CumulativeTips', optional note column.
    """
    return {
        "fixed_interval": {
            "sheet_name": "TBRG Data Fixed Interval",
            "columns": ["DateTime", "Depth_mm", "Note: Each Tip = 0.2 mm"],
            "freq": "1min",
            "tip_size_mm": 0.2,
        },
        "cumulative_tips": {
            "sheet_name": "TBRG Data Cumulative Tips",
            "columns": ["DateTime", "CumulativeTips", "Note: Each Tip = 0.2 mm"],
            "tip_size_mm": 0.2,
        },
    }


# ---------- Fixed-interval generator ----------
@pytest.fixture
def make_fixed_interval_example(rainfall_schema):
    """
    Factory -> build a small fixed-interval rainfall record with a known MIT (minutes).
    Produces zeros when dry and positive depths when raining. Cadence = 1 minute.
    Returns dict: {'df', 'truth', 'path'(opt), 'sheet'(opt)}.
    """
    schema = rainfall_schema["fixed_interval"]

    def _make(
        start="2025-01-01 00:00:00",
        hours_total=6,
        mit_minutes=120,
        tip_size_mm=None,
        storm_blueprint=None,
        write=None,            # e.g., {"csv": "fixed.csv"} or {"xlsx": "fixed.xlsx"}
        include_note_col=True,
        rng_seed=42,
    ):
        tip_mm = schema["tip_size_mm"] if tip_size_mm is None else float(tip_size_mm)
        freq = schema["freq"]

        # Build a 1-min time index
        periods = int(hours_total * 60)
        times = pd.date_range(start=start, periods=periods, freq=freq)

        # Default: Two simple storms with flat per-minute depth (one tip_size per minute)
        # separated by at least mit_minutes of zeros.
        if storm_blueprint is None:
            # Storm layout: [dry][storm A][dry >= MIT][storm B][dry]
            a_len = 30   # minutes raining
            gap  = max(int(mit_minutes), 60)
            b_len = 20
            # Choose positions safely inside the window
            a_start = 30
            a_end   = a_start + a_len
            b_start = a_end + gap
            b_end   = min(b_start + b_len, periods)
            storms = [(a_start, a_end), (b_start, b_end)]
            per_min_mm = np.zeros(periods, dtype=float)
            for s0, s1 in storms:
                per_min_mm[s0:s1] = tip_mm  # one tip's worth per minute (nice & simple)
        else:
            # storm_blueprint = list of (start_idx, end_idx, per_min_mm_value)
            per_min_mm = np.zeros(periods, dtype=float)
            storms = []
            for (s0, s1, val) in storm_blueprint:
                s0 = max(0, int(s0)); s1 = min(periods, int(s1))
                per_min_mm[s0:s1] = float(val)
                storms.append((s0, s1))

        # Build DataFrame
        df = pd.DataFrame({
            "DateTime": times,
            "Depth_mm": per_min_mm
        })
        if include_note_col:
            df[schema["columns"][2]] = f"Each Tip = {tip_mm} mm"

        # Truth metadata
        truth = {
            "mit_minutes": mit_minutes,
            "storm_bounds": [(times[s0], times[s1-1]) for (s0, s1) in storms if s1 > s0],
            "tip_size_mm": tip_mm,
            "freq": freq,
        }

        out = {"df": df, "truth": truth}

        # Optional write
        if write:
            if "csv" in write:
                path = write["csv"]
                if not os.path.isabs(path):
                    # Let caller’s make_csv handle location if they want; else ignore here
                    pass
            if "xlsx" in write:
                # Caller will use make_xlsx to enforce sheet naming
                pass

        return out

    return _make


# ---------- Cumulative-tips generator ----------
@pytest.fixture
def make_cumulative_tips_example(rainfall_schema):
    """
    Factory -> build an irregular cumulative-tips record from a fixed-interval series (or internal blueprint).
    Emits a tip whenever accumulated mm >= tip_size_mm. Returns dict: {'df','truth','path','sheet'}.
    """
    schema = rainfall_schema["cumulative_tips"]

    def _make(
        from_fixed=None,       # expects dict from make_fixed_interval_example or {'df': DataFrame}
        start="2025-01-01 00:00:00",
        hours_total=6,
        mit_minutes=120,
        tip_size_mm=None,
        write=None,            # {"csv": "..."} or {"xlsx": "..."}
        include_note_col=True,
    ):
        tip_mm = schema["tip_size_mm"] if tip_size_mm is None else float(tip_size_mm)

        # Source fixed-interval rainfall (mm/min)
        if from_fixed is None:
            # Build a simple internal fixed-interval first (two storms)
            _times = pd.date_range(start=start, periods=int(hours_total*60), freq="1min")
            per_min = np.zeros(len(_times), dtype=float)
            # same simple layout as above
            a_len, gap, b_len = 30, max(int(mit_minutes), 60), 20
            a_start = 30
            a_end   = a_start + a_len
            b_start = a_end + gap
            b_end   = min(b_start + b_len, len(_times))
            per_min[a_start:a_end] = tip_mm
            per_min[b_start:b_end] = tip_mm
            fixed_df = pd.DataFrame({"DateTime": _times, "Depth_mm": per_min})
        else:
            fixed_df = from_fixed["df"] if isinstance(from_fixed, dict) else from_fixed

        # Accumulate to tips
        mm_remainder = 0.0
        tip_count = 0
        tip_times = []
        tip_counts = []

        for t, mm in zip(fixed_df["DateTime"].to_numpy(), fixed_df["Depth_mm"].to_numpy()):
            if mm <= 0:
                continue
            mm_remainder += float(mm)
            # emit as many whole tips as possible (usually 1 per minute with our simple blueprint)
            while mm_remainder + 1e-12 >= tip_mm:
                tip_count += 1
                tip_times.append(pd.Timestamp(t))
                tip_counts.append(tip_count)
                mm_remainder -= tip_mm

        if len(tip_times) == 0:
            # ensure at least one row for downstream logic
            tip_times = [pd.Timestamp(fixed_df["DateTime"].iloc[0])]
            tip_counts = [0]

        df = pd.DataFrame({
            "DateTime": tip_times,
            "CumulativeTips": tip_counts
        })
        if include_note_col:
            df[schema["columns"][2]] = f"Each Tip = {tip_mm} mm"

        truth = {
            "tip_size_mm": tip_mm,
            "total_tips": int(tip_count),
            "storm_bounds": None,   # can be carried over from source fixed if needed
        }

        return {"df": df, "truth": truth}

    return _make


# ---------- Convenience: ready-to-use files on disk ----------
@pytest.fixture
def example_fixed_interval_file(make_fixed_interval_example, make_csv, make_xlsx, rainfall_schema, tmp_path):
    """
    Create and save a tiny fixed-interval example matching the real schema.
    Returns (path, sheet_name, truth) for use in I/O + preprocessing tests.
    """
    schema = rainfall_schema["fixed_interval"]
    out = make_fixed_interval_example(
        start="2025-01-01 00:00:00",
        hours_total=6,
        mit_minutes=120,
        tip_size_mm=schema["tip_size_mm"],
        include_note_col=True,
    )
    # prefer xlsx to mirror your examples
    path, sheet = make_xlsx(out["df"], name="Example_FixedInterval.xlsx", sheet=schema["sheet_name"])
    return path, sheet, out["truth"]


@pytest.fixture
def example_cumulative_tips_file(make_cumulative_tips_example, example_fixed_interval_file, make_xlsx, rainfall_schema):
    """
    Create and save a tiny cumulative-tips example derived from the fixed series.
    Returns (path, sheet_name, truth).
    """
    fixed_path, fixed_sheet, fixed_truth = example_fixed_interval_file  # not directly used here, but ensures consistency
    schema = rainfall_schema["cumulative_tips"]
    # Read the in-memory DataFrame from a fresh generation to avoid I/O dependency between fixtures
    derived = make_cumulative_tips_example(
        from_fixed=None,          # let it synthesize the same simple storms
        start="2025-01-01 00:00:00",
        hours_total=6,
        mit_minutes=120,
        tip_size_mm=schema["tip_size_mm"],
        include_note_col=True,
    )
    path, sheet = make_xlsx(derived["df"], name="Example_CumulativeTips.xlsx", sheet=schema["sheet_name"])
    return path, sheet, derived["truth"]

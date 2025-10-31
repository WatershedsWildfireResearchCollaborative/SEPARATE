
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



# # Create synthetic datetime data with constant spacing
# times = pd.date_range("2025-01-01", periods=10, freq="10min")
# df = pd.DataFrame({"datetime": times, "value": np.arange(10)})
#
# # Write to a temporary CSV
# csv_file = tmp_path / "test_fixed.csv"
# df.to_csv(csv_file, index=False)

# times = pd.to_datetime([
#     "2025-01-01 00:00:00",
#     "2025-01-01 00:15:00",
#     "2025-01-01 00:33:00",
#     "2025-01-01 01:02:00",
#     "2025-01-01 01:50:00",
# ])
# df = pd.DataFrame({"datetime": times, "value": np.arange(len(times))})
# fp = tmp_path / "test_cum.csv"
# df.to_csv(fp, index=False)

# swap this real data out with the synthetic data in the near future
@pytest.fixture(scope="session")
def fixed_input_file():
    return (
        r"tests/data/ExampleData_FixedInterval.xlsx",
        None,
        "Fixed Interval",
        0.2,
    )

@pytest.fixture(scope="session")
def cumulative_input_file():
    return (
        r"tests/data/ExampleData_CumulativeTips.xlsx",
        None,
        "Cumulative Tips",
        0.2,
    )

import numpy as np
import pytest
from pathlib import Path

from functions import SEPARATE_FUNCTIONS as sf


# ---------- ISC convergence ----------
def test_separate_ISC_converges_on_synthetic_dataset1(synthetic_isc_dataset_1, tmp_path, monkeypatch):
    """
    Use synthetic dataset to test ISC convergence.

    This test the branch of separate_ISC and checks that:
      - tb0 (Fixed_MIT) is not None
      - tb0 is within ~1 hour of the design MIT (6 hours)
      - returned arrays have consistent shapes
      - at least a couple of ISC plots are written
      - popup_error is NOT triggered in this converged case
    """
    tip_datetime, tip_depth, expected_mit_hours = synthetic_isc_dataset_1

    # Directory where ISC plots will be written
    gap_plots_path = tmp_path / "isc_plots"
    gap_plots_path.mkdir()

    # Capture sg.popup_error calls to confirm they do NOT happen here
    popup_calls = []

    def fake_popup_error(*args, **kwargs):
        popup_calls.append((args, kwargs))

    monkeypatch.setattr(sf.sg, "popup_error", fake_popup_error)

    # Reasonable upper limit for ISC interval search (hours)
    isc_t_max = 48.0

    # Synthetic datasets use ~0.2 mm tip and reasonable storms, so:
    min_depth = 0.2
    min_duration = 0.0

    tb0, mean_tb, CV_IET, mean_IET, std_IET, ISC_testintervals, StormNumsRec = sf.separate_ISC(
        tip_datetime,
        tip_depth,
        isc_t_max,
        min_depth,
        min_duration,
        str(gap_plots_path),
        output_name="Synthetic1",
        plt_ext=".png",
    )

    # tb0 and mean_tb should both be defined in a converged case
    assert tb0 is not None
    assert mean_tb is not None

    # Convert tb0 to a plain float (it may be a scalar array)
    tb0_val = float(np.asarray(tb0))

    # Check that ISC's MIT is "close enough" to the design value.
    # From your synthetic design & empirical summary, ~6–7 hours is expected.
    assert abs(tb0_val - expected_mit_hours) < 1.0  # within ±1 hour of 6.0

    # Shape consistency checks
    n = ISC_testintervals.size
    assert CV_IET.shape == (n,)
    assert mean_IET.shape == (n,)
    assert std_IET.shape == (n,)

    # StormNumsRec holds [N_storms, N_suppressed] per interval
    assert StormNumsRec.ndim == 2
    assert StormNumsRec.shape[0] == n
    assert StormNumsRec.shape[1] == 2

    # popup_error should NOT have been called
    assert popup_calls == []

    # At least IndependenceCriterion and SuppressedStorms plots should exist
    pngs = list(gap_plots_path.glob("*.png"))
    assert len(pngs) >= 2

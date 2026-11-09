"""The NumPy port agrees with the authors' PyTorch model.

Expected values are what TGAE.predict in shangshuzhao/sasp (commit 34d5f1b,
tgae_pre_trained.pth, PyTorch 2.9.1, CPU, float32) returned for inputs set to
the UKB-PPP mean of every protein plus z standard deviations (UKB means and SDs
from proteins_info.match_ukb_dist). They check implementation equivalence only.
They are not numbers printed in the paper, which prints no per-person example.
Tolerance 0.001: float32 (PyTorch) against float64 (NumPy); 200 random inputs
differed by at most 0.00023.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

pytest.importorskip("numpy")

import gaet  # noqa: E402
from presets import PROTEINS, UKB_MEAN_SD  # noqa: E402

AUTHOR_PYTORCH = {0.0: 59.640159606933594, 1.0: 65.41010284423828, -1.0: 47.55015182495117}


@pytest.mark.parametrize("z", sorted(AUTHOR_PYTORCH))
def test_matches_author_pytorch(z):
    values = [UKB_MEAN_SD[name][0] + z * UKB_MEAN_SD[name][1] for name in PROTEINS]
    assert gaet.sasp_score(values) == pytest.approx(AUTHOR_PYTORCH[z], abs=1e-3)


def test_protein_order_matters():
    values = [UKB_MEAN_SD[name][0] + UKB_MEAN_SD[name][1] for name in PROTEINS]
    assert gaet.sasp_score(values) != pytest.approx(gaet.sasp_score(values[::-1]), abs=1e-3)


def test_rejects_non_finite():
    values = [0.0] * 38
    values[3] = float("nan")
    with pytest.raises(ValueError):
        gaet.sasp_score(values)

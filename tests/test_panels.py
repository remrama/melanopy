"""Panel-robustness invariants.

Display white is panel-invariant (M/P = 1 by normalization on every panel), and the
protective -> alerting *ranking* is stable across panel archetypes (Spearman rho >= 0.99 in
practice) even though absolute M/P is panel-dependent. Locks the headline multi-panel claim so
a future coeff/panel change can't silently break it.
"""

import matplotlib.pyplot as plt
import numpy as np
import pytest

import melanopy as mp
from melanopy.coeffs import PANELS

PANEL_NAMES = list(PANELS)
OTHER_PANELS = [p for p in PANEL_NAMES if p != "representative"]
MAPS = ["hot", "copper", "inferno", "afmhot", "cividis", "magma", "plasma",
        "turbo", "viridis", "jet", "gray", "Blues", "winter", "cool"]  # fmt: skip
_T = np.linspace(0, 1, 256)


def _scores(panel):
    return [
        mp.rate_colormap(plt.get_cmap(m)(_T)[:, :3], panel=panel)["melanopic_ratio"] for m in MAPS
    ]


def _spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


@pytest.mark.parametrize("panel", PANEL_NAMES)
def test_white_is_panel_invariant(panel):
    g = np.linspace(0, 1, 256)[:, None].repeat(3, 1)
    assert abs(mp.rate_colormap(g, panel=panel)["melanopic_ratio"] - 1.0) < 1e-3


@pytest.mark.parametrize("panel", OTHER_PANELS)
def test_ranking_stable_across_panels(panel):
    # observed >= 0.99; assert 0.98 so the guard isn't fragile to float/lib drift
    assert _spearman(_scores("representative"), _scores(panel)) >= 0.98

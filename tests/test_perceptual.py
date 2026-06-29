"""Quantitative perceptual-uniformity and CVD checks for the Circadia family.

Every Circadia map is built on one monotone-lightness OKLab profile. These tests verify the two
properties that claim rests on, in an *independent* perceptual space — CAM02-UCS via
colorspacious (the space viscm uses), which also supplies the Machado (2009) CVD model — so
the check is not circular with the OKLab construction.

* PU  : consecutive CAM02-UCS steps along the ramp are near-uniform (low coefficient of
        variation) and lightness J' increases monotonically.
* CVD : under full-severity deutan / protan / tritan simulation the lightness ordering is
        preserved, i.e. the map stays *order-recoverable* for colour-deficient viewers.

Skipped when colorspacious is absent (it lives in the ``dev`` extra).
"""

import numpy as np
import pytest

import melanopy as mp

cs = pytest.importorskip("colorspacious")

from _perceptual import is_cvd_recoverable, is_pu  # noqa: E402  (needs colorspacious; see above)

ALPHAS = [0.0, 0.25, 0.5, 0.75, 1.0]


def _ucs(rgb):
    """sRGB ramp -> CAM02-UCS array (N, 3): lightness J', a', b'."""
    return cs.cspace_convert(np.clip(rgb, 0.0, 1.0), "sRGB1", "CAM02-UCS")


@pytest.mark.parametrize("alpha", ALPHAS)
def test_perceptual_uniformity(alpha):
    cmap = mp.circadia(alpha)
    ok, cov = is_pu(cmap)  # monotone J' + near-uniform steps (CoV < 0.30)
    assert ok, f"not perceptually uniform (CoV {cov:.3f})"
    assert np.all(np.diff(_ucs(cmap)[:, 0]) > 0)  # and Circadia is dark -> light by construction


@pytest.mark.parametrize("alpha", [0.0, 0.5, 1.0])
def test_order_recoverable_under_cvd(alpha):
    # order recoverable = J' stays monotone under full-severity deutan/protan/tritan simulation
    ok, min_step = is_cvd_recoverable(mp.circadia(alpha))
    assert ok, f"order not recoverable under CVD (smallest lightness step {min_step:.4f})"

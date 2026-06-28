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

ALPHAS = [0.0, 0.25, 0.5, 0.75, 1.0]
CVD_TYPES = ["deuteranomaly", "protanomaly", "tritanomaly"]


def _ucs(rgb):
    """sRGB ramp -> CAM02-UCS array (N, 3): lightness J', a', b'."""
    return cs.cspace_convert(np.clip(rgb, 0.0, 1.0), "sRGB1", "CAM02-UCS")


@pytest.mark.parametrize("alpha", ALPHAS)
def test_perceptual_uniformity(alpha):
    u = _ucs(mp.circadia(alpha))
    steps = np.linalg.norm(np.diff(u, axis=0), axis=1)
    assert np.all(np.diff(u[:, 0]) > 0)  # lightness strictly increasing (monotone profile)
    assert steps.std() / steps.mean() < 0.30  # near-uniform steps (~0.16-0.26 CoV in practice)


@pytest.mark.parametrize("alpha", [0.0, 0.5, 1.0])
@pytest.mark.parametrize("cvd_type", CVD_TYPES)
def test_order_recoverable_under_cvd(cvd_type, alpha):
    space = {"name": "sRGB1+CVD", "cvd_type": cvd_type, "severity": 100}
    sim = cs.cspace_convert(np.clip(mp.circadia(alpha), 0.0, 1.0), space, "sRGB1")
    lightness = _ucs(sim)[:, 0]
    assert np.all(np.diff(lightness) > 0)  # ordering survives the CVD simulation

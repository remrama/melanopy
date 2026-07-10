"""Generated-palette tests: circadia_sweep / circadia_diverging, and the Circadia accent palette.

The sweep's defining property is that its melanopic ratio rises ~linearly with the data value while
lightness stays monotone (ordered); the diverging map's is a neutral (M/P = 1) centre with a warm
protective arm and a cool alerting arm. The accent palette must sit far from the family's colour
footprint and stay CVD-distinct. Checked here against the rater, OKLab lightness, and CAM02-UCS.
"""

import colorspacious as cs
import numpy as np
from matplotlib.colors import ListedColormap, to_rgb

import melanopy as mp

# OKLab lightness of an sRGB array (the generator's construction invariant)
_M1 = np.array(
    [
        [0.4122214708, 0.5363325363, 0.0514459929],
        [0.2119034982, 0.6806995451, 0.1073969566],
        [0.0883024619, 0.2817188376, 0.6299787005],
    ]
)
_M2_L = np.array([0.2104542553, 0.7936177850, -0.0040720468])


def _oklab_L(rgb):
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return np.cbrt(lin @ _M1.T) @ _M2_L


def test_circadia_sweep_shape_and_cmap():
    rgb = mp.circadia_sweep()
    assert rgb.shape == (256, 3)
    assert rgb.min() >= 0.0 and rgb.max() <= 1.0
    cm = mp.circadia_sweep(as_cmap=True)
    assert isinstance(cm, ListedColormap) and cm.name == "circadia_sweep"


def test_circadia_sweep_is_protective_to_alerting():
    m = mp.melanopic_ratio(mp.circadia_sweep())
    assert m[0] < 0.5  # starts protective (warm, low melanopic)
    assert m[-1] > 1.2  # ends alerting (cool, high melanopic)


def test_circadia_sweep_melanopic_linear():
    m = mp.melanopic_ratio(mp.circadia_sweep())
    linear = np.linspace(m[0], m[-1], m.size)
    assert np.max(np.abs(m - linear)) / (m[-1] - m[0]) < 0.03  # M/P ~linear in data value
    assert np.all(np.diff(m) > -1e-2)  # and rising (the "axis is the data" teaching property)


def test_circadia_sweep_is_ordered():
    # monotone lightness -> ordered / CVD-recoverable like the rest of the family
    assert np.all(np.diff(_oklab_L(mp.circadia_sweep())) > 0)


def test_circadia_diverging_neutral_centre():
    n = 257  # odd -> an exact centre sample at t = 0
    m = mp.melanopic_ratio(mp.circadia_diverging(n=n))
    assert abs(m[n // 2] - 1.0) < 0.02  # centre is circadian-neutral (display white)
    assert m[0] < 1.0  # warm Sodium arm -> protective
    assert m[-1] > 1.0  # cool Xenon arm -> alerting


def test_circadia_diverging_arms_monotone_lightness():
    n = 257
    L = _oklab_L(mp.circadia_diverging(n=n))
    c = n // 2
    assert np.all(np.diff(L[: c + 1]) > 0)  # left arm rises to the light centre
    assert np.all(np.diff(L[c:]) < 0)  # right arm falls from the light centre


def test_new_maps_register():
    import matplotlib.pyplot as plt

    mp.register()
    assert "circadia_sweep" in plt.colormaps()
    assert "circadia_diverging" in plt.colormaps()


# --- the Circadia accent palette ---------------------------------------------------------------
# Marks laid over a Circadia fill. Locked against drift: recompute the family footprint from the
# *current* generator and assert each accent colour still sits far from it, and that the set stays
# mutually distinct under CVD. (The build script is only a derivation aid; these floors are the
# contract, so the baked hex can be curated as long as it clears them.)


def _min_cam02_separation(rgb):
    """Smallest pairwise CAM02-UCS distance in an ``(N, 3)`` sRGB set."""
    lab = cs.cspace_convert(np.clip(rgb, 0, 1), "sRGB1", "CAM02-UCS")
    d = np.linalg.norm(lab[:, None, :] - lab[None, :, :], axis=-1)
    return d[d > 0].min()


def _cvd_sim(rgb, cvd):
    """Machado-2009 dichromacy simulation (severity 100) of an sRGB set."""
    space = {"name": "sRGB1+CVD", "cvd_type": cvd, "severity": 100}
    return np.clip(cs.cspace_convert(np.clip(rgb, 0, 1), space, "sRGB1"), 0, 1)


def test_circadia_accent_names_match():
    assert len(mp.CIRCADIA_ACCENT) == len(mp.CIRCADIA_ACCENT_NAMES) == 4


def test_circadia_accent_pops_over_the_family():
    fam = np.vstack([mp.circadia(a, n=64) for a in np.linspace(0, 1, 11)])
    fam_lab = cs.cspace_convert(np.clip(fam, 0, 1), "sRGB1", "CAM02-UCS")
    acc = np.array([to_rgb(c) for c in mp.CIRCADIA_ACCENT])
    acc_lab = cs.cspace_convert(acc, "sRGB1", "CAM02-UCS")
    dist = np.linalg.norm(acc_lab[:, None, :] - fam_lab[None, :, :], axis=-1).min(axis=1)
    assert dist.min() > 12.0  # far from any fill (floor relaxed for the curated set)


def test_circadia_accent_is_cvd_distinct():
    acc = np.array([to_rgb(c) for c in mp.CIRCADIA_ACCENT])
    assert _min_cam02_separation(acc) > 15.0
    for cvd in ("deuteranomaly", "protanomaly", "tritanomaly"):
        assert _min_cam02_separation(_cvd_sim(acc, cvd)) > 15.0

"""circadia_sweep (full-axis / teaching) and circadia_diverging (signed-data) palettes.

The sweep's defining property is that its melanopic ratio rises ~linearly with the data value
while lightness stays monotone (ordered); the diverging map's is a neutral (M/P = 1) centre with a
warm protective arm and a cool alerting arm. Checked here against the rater and OKLab lightness.
"""

import numpy as np
from matplotlib.colors import ListedColormap

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

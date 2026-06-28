"""Edge-case / robustness checks for the public API."""

import numpy as np
import pytest

import melanopy as mp


@pytest.mark.parametrize("alpha", [0.0, 0.3, 0.55, 0.8, 1.0])
def test_circadia_stays_in_gamut(alpha):
    rgb = mp.circadia(alpha)
    assert rgb.shape == (256, 3)
    assert rgb.min() >= 0.0 and rgb.max() <= 1.0  # chroma clamp keeps it in sRGB


def test_rate_colormap_handles_near_black():
    ramp = np.linspace(0.0, 0.02, 256)[:, None].repeat(3, 1)  # emits ~nothing, includes black
    s = mp.rate_colormap(ramp)
    assert np.isfinite(s["melanopic_ratio"])
    assert np.isfinite(s["mp_spread"])
    assert all(np.isfinite(v) for v in s["range"])


def test_rate_colormap_profile_opt_in():
    ramp = np.linspace(0.0, 1.0, 256)[:, None].repeat(3, 1)  # grey ramp
    base = mp.rate_colormap(ramp)
    full = mp.rate_colormap(ramp, profile=True)
    assert set(base) <= set(full)  # summary keys preserved; profile only adds keys
    for k in ("positions", "ratios", "luminance"):
        assert full[k].shape == (256,)
    assert full["positions"][0] == 0.0 and full["positions"][-1] == 1.0
    assert np.all(np.diff(full["luminance"]) >= 0)  # grey ramp -> luminance rises monotonically


def test_unknown_panel_raises():
    with pytest.raises(KeyError):
        mp.melanopic_ratio([0.5, 0.5, 0.5], panel="does_not_exist")


def test_melanopic_ratio_shapes_and_white():
    one = mp.melanopic_ratio([1.0, 1.0, 1.0])  # single triple -> (1,)
    many = mp.melanopic_ratio(np.ones((4, 3)))  # (N, 3) -> (N,)
    assert one.shape == (1,)
    assert many.shape == (4,)
    assert np.allclose(one, 1.0, atol=1e-6)  # display white normalizes to 1
    assert np.all(np.isfinite(many))

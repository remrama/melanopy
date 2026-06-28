import matplotlib.pyplot as plt
import numpy as np

import melanopy as mp


def test_gray_is_neutral():
    g = np.linspace(0, 1, 256)[:, None].repeat(3, 1)
    assert abs(mp.rate_colormap(g)["melanopic_ratio"] - 1.0) < 1e-3


def test_endpoints_ordered():
    e = mp.rate_colormap(mp.circadia(0.0))["melanopic_ratio"]
    g = mp.rate_colormap(mp.circadia(1.0))["melanopic_ratio"]
    assert e < 1.0 < g


def test_generator_monotonic_in_alpha():
    vals = [mp.rate_colormap(mp.circadia(x))["melanopic_ratio"] for x in np.linspace(0, 1, 11)]
    assert all(a < b for a, b in zip(vals, vals[1:]))


def test_ranking_protective_to_alerting():
    def mpr(n):
        return mp.rate_colormap(plt.get_cmap(n)(np.linspace(0, 1, 256))[:, :3])["melanopic_ratio"]

    assert mpr("copper") < mpr("gray") < mpr("cool")

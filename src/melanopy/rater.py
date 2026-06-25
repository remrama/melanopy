"""Rate sRGB colours / colormaps on the melanopic (circadian) axis.

melanopic_ratio(rgb) -> M/P normalized so display white = 1.0
    < 1 protective (warm, low ipRGC / melatonin drive); > 1 alerting (cool, blue-rich).
rate_colormap(colors) -> {melanopic_ratio (axis position), purity_sigma, range}.
"""

import numpy as np

from .coeffs import LUM_W, get_coeffs

_W = np.array([LUM_W["R"], LUM_W["G"], LUM_W["B"]])


def _to_linear(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _white(mp):
    return float(_W @ np.array([mp["R"], mp["G"], mp["B"]]))


def melanopic_ratio(rgb, panel="representative"):
    mp = get_coeffs(panel)
    w = _white(mp)
    lin = _to_linear(np.atleast_2d(rgb))
    Yc = lin * _W
    Y = Yc.sum(1)
    M = (Yc * np.array([mp["R"], mp["G"], mp["B"]])).sum(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (M / Y) / w


def rate_colormap(colors, panel="representative"):
    mp = get_coeffs(panel)
    w = _white(mp)
    colors = np.asarray(colors, float)
    Yc = _to_linear(colors) * _W
    Y = Yc.sum(1)
    M = (Yc * np.array([mp["R"], mp["G"], mp["B"]])).sum(1)
    axis = float(M.sum() / Y.sum()) / w
    ratios = (M / np.where(Y < 1e-9, np.nan, Y)) / w
    keep = Y > 0.01 * Y.max()
    ww = Y[keep]
    rr = ratios[keep]
    wm = float((ww * rr).sum() / ww.sum())
    ws = float(np.sqrt((ww * (rr - wm) ** 2).sum() / ww.sum()))
    return {
        "melanopic_ratio": axis,
        "purity_sigma": ws,
        "range": (float(np.nanmin(rr)), float(np.nanmax(rr))),
    }

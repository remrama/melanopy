"""Rate sRGB colours / colormaps on the melanopic (circadian) axis.

melanopic_ratio(rgb) -> M/P normalized so display white = 1.0
    < 1 protective (warm, low ipRGC / melatonin drive); > 1 alerting (cool, blue-rich).
rate_colormap(colors) -> {melanopic_ratio (M/P mean), mp_spread, range}; pass profile=True
    to also get the per-position positions/ratios/luminance arrays behind those numbers.
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
    """Melanopic ratio (M/P) of one or more sRGB colours, normalized so display white = 1.0.

    ``< 1`` is protective (warm, low melatonin drive); ``> 1`` is alerting (cool, blue-rich).

    Parameters
    ----------
    rgb : array-like
        A single ``(3,)`` sRGB colour or an ``(N, 3)`` array, values in ``[0, 1]``.
    panel : str, optional
        Display archetype selecting the per-primary coefficients (see :data:`coeffs.PANELS`).

    Returns
    -------
    numpy.ndarray
        The melanopic ratio per input colour.

    Examples
    --------
    >>> import melanopy as mp
    >>> mp.melanopic_ratio([1, 1, 1])  # display white is the unit
    array([1.])
    >>> mp.melanopic_ratio([1, 0, 0])  # pure red — protective
    array([0.002])
    >>> mp.melanopic_ratio([0, 0, 1])  # pure blue — strongly alerting
    array([8.695])
    """
    mp = get_coeffs(panel)
    w = _white(mp)
    lin = _to_linear(np.atleast_2d(rgb))
    Yc = lin * _W
    Y = Yc.sum(1)
    M = (Yc * np.array([mp["R"], mp["G"], mp["B"]])).sum(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (M / Y) / w


def rate_colormap(colors, panel="representative", profile=False):
    """Rate an sRGB ramp on the melanopic axis (display white = 1.0).

    Both summary numbers are luminance-weighted and ignore near-black pixels (which emit almost
    nothing), so neither is dominated by the dark end of the ramp.

    Parameters
    ----------
    colors : array-like
        An ``(N, 3)`` sRGB ramp, values in ``[0, 1]``.
    panel : str, optional
        Display archetype selecting the per-primary coefficients (see :data:`coeffs.PANELS`).
    profile : bool, optional
        When ``True``, also return the per-position arrays behind the summary numbers.

    Returns
    -------
    dict
        ``melanopic_ratio`` — the **M/P mean** (luminance-weighted axis position; < 1 protective,
        > 1 alerting); ``mp_spread`` — the luminance-weighted **spread** of the per-position ratio
        (a tight spread reads as a "pure" ramp); and ``range`` — its (min, max) over the emitting
        ramp. With ``profile=True`` the dict also carries ``positions`` (the ``[0, 1]`` data grid),
        ``ratios`` (per-position M/P, NaN where the colour emits ~nothing), and ``luminance`` (the
        per-position photopic luminance, i.e. the weights) — enough to plot the M/P profile.

    Examples
    --------
    >>> import matplotlib.pyplot as plt, numpy as np, melanopy as mp
    >>> c = plt.get_cmap("viridis")(np.linspace(0, 1, 256))[:, :3]
    >>> mp.rate_colormap(c)
    {'melanopic_ratio': 0.834, 'mp_spread': 0.556, 'range': (0.395, 3.069)}
    """
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
    out = {
        "melanopic_ratio": axis,
        "mp_spread": ws,
        "range": (float(np.nanmin(rr)), float(np.nanmax(rr))),
    }
    if profile:
        out["positions"] = np.linspace(0.0, 1.0, len(ratios))
        out["ratios"] = ratios
        out["luminance"] = Y
    return out


def circadia_rating(alpha, *, panel="representative"):
    """Rated melanopic ratio of a Circadia map at ``alpha`` — the physical number behind the dial.

    ``alpha`` is a geometric position on the OKLab morph, not a melanopic ratio, and the M/P a
    viewer actually receives is panel-dependent. This composes the generator and the rater so a
    live UI (e.g. a labelled slider) can show the rated M/P for its configured ``panel`` rather
    than bare ``alpha``. The recompute is cheap (a vectorized 256-point rating); a hot UI may
    memoize on ``(round(alpha, 3), panel)``.

    Parameters
    ----------
    alpha : float
        Position on the Circadia axis in ``[0, 1]`` (0 protective/warm, 1 alerting/cool).
    panel : str, optional
        Display archetype selecting the per-primary coefficients (see :data:`coeffs.PANELS`).

    Returns
    -------
    tuple of float
        ``(melanopic_ratio, mp_spread)`` — the M/P mean (axis position; < 1 protective, > 1
        alerting) and its luminance-weighted spread, both for ``panel``.

    Examples
    --------
    >>> import melanopy as mp
    >>> mp.circadia_rating(0.0)  # Sodium endpoint — protective
    (0.288, 0.067)
    >>> mp.circadia_rating(0.55)  # Equilux — circadian-neutral (M/P ≈ 1)
    (0.999, 0.16)
    >>> mp.circadia_rating(1.0)  # Xenon endpoint — alerting
    (1.728, 0.423)
    """
    from .generator import circadia  # local import avoids a generator/rater import cycle

    r = rate_colormap(circadia(alpha), panel=panel)
    return r["melanopic_ratio"], r["mp_spread"]

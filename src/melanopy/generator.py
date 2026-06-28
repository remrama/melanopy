"""The Circadia family — circadian colormap generator.

circadia(alpha): a perceptually-uniform, CVD-safe colormap whose warm->cool colour temperature
is set by the input dial alpha in [0, 1]:
    0 = protective (Sodium, warm, low melanopic)   1 = alerting (Xenon, cool, high melanopic)

A shared monotonic OKLab lightness profile keeps the order recoverable under CVD and the
ramp close to perceptually uniform (both verified numerically in the tests); alpha morphs
only the chroma vector (warm -> near-neutral crossover ~0.55 -> cool).

alpha is the *input* design dial (the "melanopic temperature"), not a melanopic measurement;
the melanopic ratio is the emergent, monotonic *output* you read back with the rater
(rate_colormap / circadia_rating). You set alpha; you measure M/P.

Named anchors: SODIUM (0.0), EQUILUX (M/P=1 crossover, ~0.55), XENON (1.0).

Beyond the single-alpha ramp: circadia_sweep walks the whole axis along one ramp (melanopic
ratio rises ~linearly with the data value -- a teaching map), and circadia_diverging is a
warm<->cool diverging map for signed data.
"""

import numpy as np
from matplotlib.colors import ListedColormap

# OKLab <-> linear sRGB (Bjorn Ottosson)
_M1 = np.array(
    [
        [0.4122214708, 0.5363325363, 0.0514459929],
        [0.2119034982, 0.6806995451, 0.1073969566],
        [0.0883024619, 0.2817188376, 0.6299787005],
    ]
)
_M2 = np.array(
    [
        [0.2104542553, 0.7936177850, -0.0040720468],
        [1.9779984951, -2.4285922050, 0.4505937099],
        [0.0259040371, 0.7827717662, -0.8086757660],
    ]
)
_M1i = np.linalg.inv(_M1)
_M2i = np.linalg.inv(_M2)


def _lin2srgb(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)


def _oklab2lin(lab):
    return (lab @ _M2i.T) ** 3 @ _M1i.T


def _ingamut(lab, eps=1e-4):
    lin = _oklab2lin(lab)
    return np.all(lin >= -eps) and np.all(lin <= 1 + eps)


def _clamp(L, a, b):
    """Reduce chroma (preserve L and hue) until inside sRGB."""
    C = np.hypot(a, b)
    h = np.degrees(np.arctan2(b, a))
    for s in np.linspace(1, 0, 201):
        r = np.radians(h)
        lab = np.array([L, C * s * np.cos(r), C * s * np.sin(r)])
        if _ingamut(lab):
            return np.clip(_lin2srgb(_oklab2lin(lab)), 0, 1)
    return np.clip(_lin2srgb(_oklab2lin(np.array([L, 0, 0]))), 0, 1)


# shared lightness profile + endpoint chroma paths (C, hue_deg) at each position
_POS = np.array([0.00, 0.18, 0.40, 0.63, 0.84, 1.00])
_L = np.array([0.150, 0.300, 0.490, 0.650, 0.745, 0.810])
_WARM = [(0.035, 35), (0.100, 32), (0.150, 42), (0.155, 58), (0.150, 74), (0.155, 86)]
_COOL = [(0.045, 266), (0.115, 260), (0.155, 248), (0.152, 232), (0.140, 212), (0.120, 200)]


def _ab(ch):
    o = np.zeros((len(ch), 2))
    for i, (C, h) in enumerate(ch):
        r = np.radians(h)
        o[i] = [C * np.cos(r), C * np.sin(r)]
    return o


_WA = _ab(_WARM)
_CA = _ab(_COOL)


def _render(Li, ai, bi):
    """Clamp each (L, a, b) into sRGB (preserving L and hue) -> (n, 3) sRGB array."""
    return np.array([_clamp(Li[k], ai[k], bi[k]) for k in range(len(Li))])


def _cmap(rgb, as_cmap, name, default):
    return ListedColormap(rgb, name=name or default) if as_cmap else rgb


def circadia(alpha, n=256, as_cmap=False, name=None):
    """Return (n,3) sRGB array (default) or a matplotlib ListedColormap for a given alpha."""
    ab = (1 - alpha) * _WA + alpha * _CA
    t = np.linspace(0, 1, n)
    Li = np.interp(t, _POS, _L)
    ai = np.interp(t, _POS, ab[:, 0])
    bi = np.interp(t, _POS, ab[:, 1])
    return _cmap(_render(Li, ai, bi), as_cmap, name, f"circadia_{alpha:.2f}")


circadian_cmap = circadia  # alias


def _sweep_ramp(pos):
    """Warm->cool sequential ramp at fractional positions `pos` in [0, 1] (shared monotone L)."""
    ai = (1 - pos) * np.interp(pos, _POS, _WA[:, 0]) + pos * np.interp(pos, _POS, _CA[:, 0])
    bi = (1 - pos) * np.interp(pos, _POS, _WA[:, 1]) + pos * np.interp(pos, _POS, _CA[:, 1])
    return _render(np.interp(pos, _POS, _L), ai, bi)


def circadia_sweep(n=256, as_cmap=False, name=None):
    """Full-axis sequential map sweeping protective (Sodium, warm) -> alerting (Xenon, cool), with
    the melanopic ratio rising ~linearly along the ramp -- the "data axis *is* the melanopic axis"
    teaching map. The shared monotone OKLab lightness keeps it ordered and CVD-recoverable; the
    positions are calibrated against the rater so M/P is linear in the data value. This is the one
    melanopic-aware generator (via a local import); `circadia` itself stays pure OKLab geometry.
    """
    from .rater import melanopic_ratio  # local import keeps the module pure OKLab geometry

    u = np.linspace(0, 1, 1024)
    m = np.maximum.accumulate(melanopic_ratio(_sweep_ramp(u)))  # force monotone for inversion
    pos = np.interp(np.linspace(m[0], m[-1], n), m, u)  # positions giving M/P linear in t
    return _cmap(_sweep_ramp(pos), as_cmap, name, "circadia_sweep")


# diverging map for signed data: warm Sodium arm <- light neutral centre -> cool Xenon arm
_DIV_LC, _DIV_LE, _DIV_C, _DIV_HW, _DIV_HX = 0.92, 0.42, 0.16, 50.0, 252.0


def circadia_diverging(n=256, as_cmap=False, name=None):
    """Diverging map for signed data: warm Sodium (protective, M/P<1) <- light neutral centre
    (M/P=1) -> cool Xenon (alerting, M/P>1). Each arm has monotone lightness, but -- like most
    diverging maps -- the arms are told apart across zero by *hue*, so it is NOT
    CVD-order-recoverable; use the sequential maps where CVD-safety matters.
    """
    t = np.linspace(-1, 1, n)
    s = np.abs(t)
    h = np.radians(np.where(t < 0, _DIV_HW, _DIV_HX))
    a = s * _DIV_C * np.cos(h)
    b = s * _DIV_C * np.sin(h)
    return _cmap(
        _render(_DIV_LC + s * (_DIV_LE - _DIV_LC), a, b), as_cmap, name, "circadia_diverging"
    )


SODIUM = circadia(0.0, as_cmap=True, name="sodium")  # protective endpoint
EQUILUX = circadia(0.55, as_cmap=True, name="equilux")  # M/P=1 crossover (alpha 0.55 -> M/P 0.999)
XENON = circadia(1.0, as_cmap=True, name="xenon")  # alerting endpoint

__all__ = [
    "circadia",
    "circadian_cmap",
    "circadia_sweep",
    "circadia_diverging",
    "SODIUM",
    "EQUILUX",
    "XENON",
]

"""The Diel family — circadian colormap generator.

diel(alpha): a perceptually-uniform, CVD-safe colormap whose colour temperature (and thus
melanopic ratio) is set by alpha in [0, 1]:
    0 = protective (Ember, warm, low melanopic)   1 = alerting (Glacier, cool, high melanopic)

One monotonic OKLab lightness profile is shared by every alpha, so perceptual uniformity
and colourblind-safety hold by construction; alpha morphs only the chroma vector (warm ->
near-neutral crossover ~0.52 -> cool). Melanopic ratio is the emergent, monotonic dial.

Named anchors: EMBER (0.0), EQUINOX (~neutral crossover, 0.52), GLACIER (1.0).
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


def diel(alpha, n=256, as_cmap=False, name=None):
    """Return (n,3) sRGB array (default) or a matplotlib ListedColormap for a given alpha."""
    ab = (1 - alpha) * _WA + alpha * _CA
    t = np.linspace(0, 1, n)
    Li = np.interp(t, _POS, _L)
    ai = np.interp(t, _POS, ab[:, 0])
    bi = np.interp(t, _POS, ab[:, 1])
    rgb = np.array([_clamp(Li[k], ai[k], bi[k]) for k in range(n)])
    return ListedColormap(rgb, name=name or f"diel_{alpha:.2f}") if as_cmap else rgb


circadian_cmap = diel  # alias

EMBER = diel(0.0, as_cmap=True, name="ember")  # protective endpoint
EQUINOX = diel(0.55, as_cmap=True, name="equinox")  # ~circadian-neutral crossover (M/P ~ 1)
GLACIER = diel(1.0, as_cmap=True, name="glacier")  # alerting endpoint

__all__ = ["diel", "circadian_cmap", "EMBER", "EQUINOX", "GLACIER"]

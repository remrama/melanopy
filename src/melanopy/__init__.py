"""Melanopy: A melanopic axis for colormaps.

Scientific colormaps carry a third, context-dependent design dimension alongside
perceptual uniformity and colour-vision-deficiency safety: how much short-wavelength
(melanopic / melatonin-suppressing) light they emit. Melanopy makes that axis
measurable, scores existing maps on it, and provides a one-parameter family that
walks the axis while holding uniformity and colourblind-safety fixed.
"""

from .accent import CIRCADIA_ACCENT, CIRCADIA_ACCENT_NAMES
from .adapters.mpl import register
from .generator import (
    EQUILUX,
    SODIUM,
    XENON,
    circadia,
    circadia_diverging,
    circadia_sweep,
    circadian_cmap,
)
from .rater import circadia_rating, melanopic_ratio, rate_colormap

__all__ = [
    "circadia",
    "circadian_cmap",
    "circadia_sweep",
    "circadia_diverging",
    "SODIUM",
    "XENON",
    "EQUILUX",
    "melanopic_ratio",
    "rate_colormap",
    "circadia_rating",
    "CIRCADIA_ACCENT",
    "CIRCADIA_ACCENT_NAMES",
    "register",
    "__version__",
]

__version__ = "0.0.2"

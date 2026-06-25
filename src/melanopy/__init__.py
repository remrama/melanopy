"""Melanopy — a melanopic axis for colormaps.

Scientific colormaps carry a third, context-dependent design dimension alongside
perceptual uniformity and colour-vision-deficiency safety: how much short-wavelength
(melanopic / melatonin-suppressing) light they emit. Melanopy makes that axis
measurable, scores existing maps on it, and provides a one-parameter family that
walks the axis while holding uniformity and colourblind-safety fixed.

Honest scope: this rates a colour's *chromaticity*, not light *dose*. Real circadian
load also depends on screen brightness, screen fill, viewing distance and ambient
light. See paper/manuscript.md.
"""

from .adapters.mpl import register
from .categorical import (
    CATEGORICAL,
    CATEGORICAL_DARK,
    CATEGORICAL_LIGHT,
    CATEGORICAL_NAMES,
)
from .generator import EMBER, EQUINOX, GLACIER, circadian_cmap, diel
from .rater import melanopic_ratio, rate_colormap

__all__ = [
    "diel",
    "circadian_cmap",
    "EMBER",
    "GLACIER",
    "EQUINOX",
    "melanopic_ratio",
    "rate_colormap",
    "CATEGORICAL_DARK",
    "CATEGORICAL_LIGHT",
    "CATEGORICAL_NAMES",
    "CATEGORICAL",
    "register",
    "__version__",
]

__version__ = "0.0.1"

"""Export Melanopy colormaps to pyqtgraph (for SMACC / Qt). Requires pyqtgraph."""

import numpy as np

from ..generator import circadia


def to_pyqtgraph(colors):
    import pyqtgraph as pg

    colors = np.asarray(colors, float)
    pos = np.linspace(0, 1, len(colors))
    rgba = np.clip(np.c_[colors, np.ones(len(colors))] * 255, 0, 255).astype(int)
    return pg.ColorMap(pos, rgba)


def circadia_pyqtgraph(alpha, n=256):
    """A pyqtgraph ColorMap for the given alpha — wire to an ImageItem LUT / a slider."""
    return to_pyqtgraph(circadia(alpha, n=n))

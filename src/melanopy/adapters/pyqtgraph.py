"""Export Melanopy colormaps to pyqtgraph (for SMACC / Qt). Requires pyqtgraph."""

import numpy as np

from ..generator import circadia, circadia_diverging, circadia_sweep


def to_pyqtgraph(colors):
    """Wrap any (N, 3) sRGB ramp as a pyqtgraph ColorMap — the general escape hatch.

    The named wrappers below cover the Circadia family; reach for this for anything else
    (a rated map, a qualitative palette, or any third-party colormap sampled to an array).
    """
    import pyqtgraph as pg

    colors = np.asarray(colors, float)
    pos = np.linspace(0, 1, len(colors))
    rgba = np.clip(np.c_[colors, np.ones(len(colors))] * 255, 0, 255).astype(int)
    return pg.ColorMap(pos, rgba)


def circadia_pyqtgraph(alpha, n=256):
    """A pyqtgraph ColorMap for the given alpha — wire to an ImageItem LUT / a slider."""
    return to_pyqtgraph(circadia(alpha, n=n))


def circadia_sweep_pyqtgraph(n=256):
    """A pyqtgraph ColorMap for the sequential sweep — wire to an ImageItem LUT."""
    return to_pyqtgraph(circadia_sweep(n=n))


def circadia_diverging_pyqtgraph(n=256):
    """A pyqtgraph ColorMap for the diverging family (neutral at the M/P crossing)."""
    return to_pyqtgraph(circadia_diverging(n=n))


__all__ = [
    "to_pyqtgraph",
    "circadia_pyqtgraph",
    "circadia_sweep_pyqtgraph",
    "circadia_diverging_pyqtgraph",
]

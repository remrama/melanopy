"""Register Melanopy colormaps with matplotlib."""

import matplotlib as mpl

from ..generator import EQUILUX, SODIUM, XENON, diel_diverging, diel_sweep


def register():
    """Register sodium/xenon/equilux + diel_sweep/diel_diverging as named matplotlib colormaps."""
    cmaps = (SODIUM, XENON, EQUILUX, diel_sweep(as_cmap=True), diel_diverging(as_cmap=True))
    for cm in cmaps:
        try:
            mpl.colormaps.register(cm)
        except (ValueError, AttributeError):
            pass  # already registered, or older matplotlib

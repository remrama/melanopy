"""Register Melanopy colormaps with matplotlib."""

import matplotlib as mpl

from ..generator import EQUILUX, SODIUM, XENON, circadia_diverging, circadia_sweep


def register():
    """Register sodium/xenon/equilux + circadia_sweep/circadia_diverging as matplotlib colormaps."""
    cmaps = (SODIUM, XENON, EQUILUX, circadia_sweep(as_cmap=True), circadia_diverging(as_cmap=True))
    for cm in cmaps:
        try:
            mpl.colormaps.register(cm)
        except (ValueError, AttributeError):
            pass  # already registered, or older matplotlib

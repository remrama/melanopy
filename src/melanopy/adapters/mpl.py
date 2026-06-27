"""Register Melanopy colormaps with matplotlib."""

import matplotlib as mpl

from ..generator import EQUILUX, SODIUM, XENON


def register():
    """Register 'sodium', 'xenon', 'equilux' as named matplotlib colormaps."""
    for cm in (SODIUM, XENON, EQUILUX):
        try:
            mpl.colormaps.register(cm)
        except (ValueError, AttributeError):
            pass  # already registered, or older matplotlib

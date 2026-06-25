"""Register Melanopy colormaps with matplotlib."""

import matplotlib as mpl

from ..generator import EMBER, EQUINOX, GLACIER


def register():
    """Register 'ember', 'glacier', 'equinox' as named matplotlib colormaps."""
    for cm in (EMBER, GLACIER, EQUINOX):
        try:
            mpl.colormaps.register(cm)
        except (ValueError, AttributeError):
            pass  # already registered, or older matplotlib

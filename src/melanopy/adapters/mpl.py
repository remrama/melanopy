"""Register Melanopy colormaps with matplotlib."""

import matplotlib as mpl

from ..generator import EQUILUX, SODIUM, XENON, circadia_diverging, circadia_sweep


def register():
    """Register sodium/xenon/equilux + circadia_sweep/circadia_diverging as matplotlib colormaps.

    After calling this, the maps are available by name to any matplotlib call. Safe to call
    more than once.

    Examples
    --------
    >>> import matplotlib.pyplot as plt, numpy as np, melanopy as mp
    >>> mp.register()
    >>> Z = np.add.outer(np.linspace(0, 1, 200), np.linspace(0, 1, 200))
    >>> plt.imshow(Z, cmap="sodium")  # doctest: +SKIP
    """
    cmaps = (SODIUM, XENON, EQUILUX, circadia_sweep(as_cmap=True), circadia_diverging(as_cmap=True))
    for cm in cmaps:
        try:
            mpl.colormaps.register(cm)
        except (ValueError, AttributeError):
            pass  # already registered, or older matplotlib

"""Smoke test for the optional pyqtgraph adapter (SMACC / Qt integration).

Gated on the ``qt`` extra: skipped unless pyqtgraph *and* a Qt binding import. Uses the
try/except idiom (like ``test_coeffs.py``) rather than ``importorskip`` because pyqtgraph raises a
plain ``ImportError`` deep in its Qt shim when no binding is present, which ``importorskip`` does
not treat as "module missing". Importing the adapter module itself never needs pyqtgraph (the
dependency is imported lazily inside the functions).
"""

import numpy as np
import pytest

from melanopy.adapters.pyqtgraph import (
    circadia_diverging_pyqtgraph,
    circadia_pyqtgraph,
    circadia_sweep_pyqtgraph,
    to_pyqtgraph,
)

try:
    import pyqtgraph as pg
except ImportError:  # pyqtgraph absent, or installed without a Qt binding
    pg = None

pytestmark = pytest.mark.skipif(
    pg is None, reason="pyqtgraph + Qt binding not installed (qt extra)"
)


def test_pyqtgraph_wrappers_return_colormaps():
    cmaps = [
        to_pyqtgraph(np.linspace(0, 1, 16)[:, None].repeat(3, 1)),  # general escape hatch
        circadia_pyqtgraph(0.3),
        circadia_sweep_pyqtgraph(),
        circadia_diverging_pyqtgraph(),
    ]
    assert all(isinstance(c, pg.ColorMap) for c in cmaps)
    assert circadia_sweep_pyqtgraph(n=64).getLookupTable(nPts=64).shape == (64, 3)

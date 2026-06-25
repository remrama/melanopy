"""Spectral basis: CIE S 026 melanopic action spectrum + CIE 1931 2° V(λ),
plus a helper to derive display coefficients from measured primary SPDs.

Data files in melanopy/data/ are vendored from the CIE Toolbox (via luxpy).
See melanopy/data/NOTICE.md for provenance and licensing (CONFIRM before public release).
"""

import io
import os

import numpy as np

_DATA = os.path.join(os.path.dirname(__file__), "data")
WL = np.arange(380, 781, 1.0)  # 1 nm grid


def _read(path):
    txt = open(path, encoding="utf-8").read().replace("\r", "")
    return np.genfromtxt(
        io.StringIO(txt), delimiter=",", skip_header=1 if path.endswith(".csv") else 0
    )


def melanopic_action_spectrum():
    a = _read(os.path.join(_DATA, "cie_s026_actionspectra.csv"))  # nm,sc,mc,lc,rh,mel
    nm, mel = a[:, 0], a[:, 5]
    fin = np.isfinite(mel)
    s = np.interp(WL, nm[fin], mel[fin], left=0.0, right=0.0)
    return s / s.max()


def vlambda():
    a = _read(os.path.join(_DATA, "ciexyz_1931_2.dat"))  # nm,xbar,ybar,zbar
    return np.interp(WL, a[:, 0], a[:, 2])


SMEL = melanopic_action_spectrum()
V = vlambda()


def representative_primaries():
    """Gaussian narrowband-RGB model (peaks R625/G530/B460 nm)."""

    def g(peak, fwhm):
        return np.exp(-0.5 * ((WL - peak) / (fwhm / 2.3548)) ** 2)

    return {"R": g(625, 28), "G": g(530, 35), "B": g(460, 22)}


def coefficients_from_primaries(primaries, smel=None, vlam=None):
    """primaries: dict {'R','G','B'} -> SPD array on WL. Returns per-primary M/P."""
    smel = SMEL if smel is None else smel
    vlam = V if vlam is None else vlam
    return {
        k: float(np.trapezoid(p * smel, WL) / np.trapezoid(p * vlam, WL))
        for k, p in primaries.items()
    }

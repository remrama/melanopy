"""Spectral basis: CIE S 026 melanopic action spectrum + CIE 1931 2° V(λ),
plus a helper to derive display coefficients from measured primary SPDs.

Data files in melanopy/data/ are verbatim CIE reference tables (CIE S 026:2018 Table 2;
CIE 1931 2° observer), © CIE and licensed CC BY-SA 4.0 — not under Melanopy's MIT license.
See melanopy/data/NOTICE.md for full provenance, DOIs, and licensing.
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


def _gauss(peak, fwhm):
    return np.exp(-0.5 * ((WL - peak) / (fwhm / 2.3548)) ** 2)


def representative_primaries():
    """Narrowband RGB-LED / quantum-dot model (peaks R625/G530/B460 nm) — the default panel."""
    return {"R": _gauss(625, 28), "G": _gauss(530, 35), "B": _gauss(460, 22)}


PANEL_KINDS = ("representative", "led_lcd", "oled", "wide_gamut")


def panel_primaries(kind="representative"):
    """Primary SPDs {R,G,B} on WL for a panel *archetype* (representative models, not measured).

    These span the spectral diversity the per-primary coefficients depend on; feed any of them
    to coefficients_from_primaries() to (re)derive the numbers baked in melanopy.coeffs. See
    data/NOTICE.md for the measured-SPD cross-check left as future work.

    representative  narrowband RGB-LED / quantum-dot (the default)
    led_lcd         blue-pump white-LED backlight (blue spike + broad phosphor) x LCD filters
    oled            broad self-emissive RGB
    wide_gamut      very narrow quantum-dot (DCI-P3 / Rec. 2020 class)
    """
    if kind == "representative":
        return representative_primaries()
    if kind == "led_lcd":
        bl = _gauss(451, 20) + 1.4 * _gauss(560, 95)  # blue-pump backlight, carved by filters
        return {"R": bl * _gauss(612, 90), "G": bl * _gauss(540, 70), "B": bl * _gauss(452, 46)}
    if kind == "oled":
        return {"R": _gauss(620, 40), "G": _gauss(530, 48), "B": _gauss(465, 32)}
    if kind == "wide_gamut":
        return {"R": _gauss(630, 24), "G": _gauss(525, 26), "B": _gauss(450, 20)}
    raise ValueError(f"unknown panel archetype: {kind!r}")


def coefficients_from_primaries(primaries, smel=None, vlam=None):
    """Derive the three per-primary M/P coefficients from measured primary SPDs.

    Parameters
    ----------
    primaries : dict
        ``{'R', 'G', 'B'}`` -> SPD array on :data:`WL` (the 380–780 nm, 1 nm grid).
    smel, vlam : array-like, optional
        Override the melanopic action spectrum / V(λ); default to the shipped CIE tables.

    Returns
    -------
    dict
        ``{'R', 'G', 'B'}`` -> the melanopic/photopic ratio of each primary.

    Examples
    --------
    >>> from melanopy.spectra import coefficients_from_primaries, panel_primaries
    >>> coefficients_from_primaries(panel_primaries("representative"))
    {'R': 0.003, 'G': 0.656, 'B': 10.968}
    """
    smel = SMEL if smel is None else smel
    vlam = V if vlam is None else vlam
    return {
        k: float(np.trapezoid(p * smel, WL) / np.trapezoid(p * vlam, WL))
        for k, p in primaries.items()
    }

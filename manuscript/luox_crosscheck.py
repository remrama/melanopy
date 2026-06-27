"""luox / CIE S 026 cross-check of melanopy's melanopic ratios.

melanopy reduces a colour to R(SPD) = int(SPD * s_mel) / int(SPD * V), using the vendored CIE
S 026 melanopic action spectrum (peak-normalized) and CIE 1931 2-deg V(lambda). luox reports a
melanopic Daylight (D65) Efficacy Ratio (mel-DER), normalized so D65 = 1.000. Because

    mel-DER(SPD) = R(SPD) / R(D65),

every unit constant (683 lm/W, the peak-normalizations) cancels in the ratio, so melanopy's
numbers are directly comparable to luox's melanopic DER with no fudge factor.

This script computes melanopy's mel-DER for the CIE standard illuminants (D65 == 1 by
definition, A, E) and for the representative display primaries + sRGB display white, and writes a
luox-uploadable CSV of every SPD. Run:

    uv run --with colour-science python luox_crosscheck.py
"""

import os

import numpy as np

from melanopy.coeffs import LUM_W
from melanopy.spectra import SMEL, WL, V, coefficients_from_primaries, panel_primaries

SCRATCH = os.path.dirname(os.path.abspath(__file__))


def R(spd):
    """melanopy's raw melanopic/photopic ratio for an SPD on the WL grid."""
    spd = np.asarray(spd, float)
    return float(np.trapezoid(spd * SMEL, WL) / np.trapezoid(spd * V, WL))


# --- standard illuminant SPDs on the 380..780 nm / 1 nm grid -----------------------------
E = np.ones_like(WL)  # Illuminant E: equal energy (flat)


def illuminant_A(wl):
    """Exact CIE analytic definition of Standard Illuminant A (Planckian, T=2848 K, c2=1.435e7)."""
    return (
        100.0
        * (560.0 / wl) ** 5
        * (np.exp(1.435e7 / (2848.0 * 560.0)) - 1.0)
        / (np.exp(1.435e7 / (2848.0 * wl)) - 1.0)
    )


A = illuminant_A(WL)

try:
    import colour

    _d65 = colour.SDS_ILLUMINANTS["D65"]
    D65 = np.interp(WL, _d65.wavelengths, _d65.values)
    have_colour = True
except Exception as exc:  # noqa: BLE001
    raise SystemExit(f"need colour-science for the D65 SPD: {exc}")

R_D65 = R(D65)


def der(spd):
    return R(spd) / R_D65


# --- representative display primaries + sRGB display white --------------------------------
prim = panel_primaries("representative")
coeffs = coefficients_from_primaries(prim)  # == melanopy.coeffs.PANELS["representative"]

# sRGB white SPD: scale each primary so its photopic weight matches the sRGB luminance weight,
# so R(white) reproduces the rater's white-normalization constant exactly.
white = sum((LUM_W[k] / np.trapezoid(prim[k] * V, WL)) * prim[k] for k in "RGB")

spectra = {
    "primary_R": prim["R"],
    "primary_G": prim["G"],
    "primary_B": prim["B"],
    "display_white": white,
    "illuminant_E": E,
    "illuminant_A": A,
    "D65": D65,
}

# --- report ------------------------------------------------------------------------------
print(f"melanopy R(D65) = {R_D65:.6f}   (colour-science D65 SPD)\n")
print(f"{'spectrum':<16}{'melanopy R':>12}{'mel-DER':>10}")
print("-" * 38)
for name, spd in spectra.items():
    print(f"{name:<16}{R(spd):>12.4f}{der(spd):>10.4f}")

print("\nrepresentative per-primary coefficients (melanopy.coeffs.PANELS):")
for k in "RGB":
    print(f"  {k}: coeff={coeffs[k]:.4f}  -> mel-DER={coeffs[k] / R_D65:.4f}")

print(f"\ndisplay-white mel-DER = {der(white):.4f}")
print("melanopic_ratio(colour) == mel-DER(colour) / mel-DER(white) by construction.")

# --- luox-uploadable CSV (col 1 = wavelength, then one column per spectrum) ---------------
out = os.path.join(SCRATCH, "melanopy_spectra_for_luox.csv")
header = "wavelength_nm," + ",".join(spectra)
cols = np.column_stack([WL] + [spectra[name] for name in spectra])
np.savetxt(out, cols, delimiter=",", header=header, comments="", fmt="%.6g")
print(f"\nwrote {out}")

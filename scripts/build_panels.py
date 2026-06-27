"""Derive the per-panel melanopic coefficients baked in ``melanopy.coeffs.PANELS``.

Turns each panel archetype in ``melanopy.spectra.panel_primaries`` into its three per-primary
melanopic/photopic coefficients (via the vendored CIE S 026 spectrum + V(lambda)), printed as
ready-to-paste ``PANELS`` rows. Offline / generation-time: needs the CIE ``data/`` tables.

    uv run scripts/build_panels.py
"""

from melanopy import spectra


def main():
    print("PANELS = {")
    for kind in spectra.PANEL_KINDS:
        c = spectra.coefficients_from_primaries(spectra.panel_primaries(kind))
        r, g, b = (round(c[k], 4) for k in ("R", "G", "B"))
        print(f'    "{kind}": {{"R": {r}, "G": {g}, "B": {b}}},')
    print("}")


if __name__ == "__main__":
    main()

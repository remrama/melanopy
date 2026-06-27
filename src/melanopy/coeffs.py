"""Display-primary melanopic coefficients (per-primary melanopic/photopic ratios).

The melanopic content of a *display* colour depends on the panel's primary spectral
power distributions, which sRGB does not fix. All of that dependence collapses into
three coefficients. PANELS holds several representative archetypes (narrowband RGB, blue-pump
LED-LCD, OLED, wide-gamut QD); the panel= argument threading through the API selects one. For
exact results on a specific monitor, measure its primary SPDs and regenerate (see
melanopy.spectra.coefficients_from_primaries).
"""

LUM_W = {"R": 0.2126, "G": 0.7152, "B": 0.0722}  # exact sRGB / Rec.709 luminance weights

# Per-primary melanopic/photopic coefficients for representative panel *archetypes* (models,
# not measured), each derived from melanopy.spectra.panel_primaries via the CIE S 026 spectrum.
# Regenerate with `uv run scripts/build_panels.py`; tests/test_coeffs.py locks them to the
# models. Absolute M/P shifts with the panel, but the colormap ranking is stable across these
# (Spearman rho >= 0.99 — see scripts/build_panel_robustness.py).
PANELS = {
    "representative": {"R": 0.0031, "G": 0.6555, "B": 10.9681},  # narrowband RGB-LED / QD
    "led_lcd": {"R": 0.0918, "G": 0.3814, "B": 10.9332},  # blue-pump white-LED + LCD filters
    "oled": {"R": 0.0065, "G": 0.6855, "B": 8.8207},  # broad self-emissive RGB
    "wide_gamut": {"R": 0.0022, "G": 0.798, "B": 13.6715},  # narrow quantum-dot (P3 / Rec.2020)
    # add a measured monitor: melanopy.spectra.coefficients_from_primaries(measured_spds)
}
DEFAULT_PANEL = "representative"


def get_coeffs(panel: str = DEFAULT_PANEL) -> dict:
    return PANELS[panel]

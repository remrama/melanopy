"""Display-primary melanopic coefficients (per-primary melanopic/photopic ratios).

The melanopic content of a *display* colour depends on the panel's primary spectral
power distributions, which sRGB does not fix. All of that dependence collapses into
three coefficients. Defaults are CIE S 026-validated for a representative narrowband-RGB
panel; for exact results on a specific monitor, measure its primary SPDs and regenerate
(see melanopy.spectra.coefficients_from_primaries).
"""

LUM_W = {"R": 0.2126, "G": 0.7152, "B": 0.0722}  # exact sRGB / Rec.709 luminance weights

PANELS = {
    # CIE S 026:2018 melanopic action spectrum x representative narrowband-RGB primaries
    "representative": {"R": 0.0031, "G": 0.6555, "B": 10.9681},
    # add measured panels here, e.g. "my_oled": {...}
}
DEFAULT_PANEL = "representative"


def get_coeffs(panel: str = DEFAULT_PANEL) -> dict:
    return PANELS[panel]

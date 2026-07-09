"""CVD-safe qualitative palettes.

The neutral set (:data:`QUALITATIVE`, with hex lists :data:`QUALITATIVE_DARK` /
:data:`QUALITATIVE_LIGHT` and :data:`QUALITATIVE_NAMES`) is a fixed colourblind-safe set for small
marks (lines, points, glyphs). It is deliberately **circadian-neutral**: by the area-weighted
budget --- small marks emit negligible light regardless of colour --- the melanopic axis does not
apply to them, so it is optimised for category separability under colour-vision deficiency, *not*
for melanopic content. Its swatches straddle the axis; the melanopic ratio is reported, never tuned.

Two **regime-themed** variants (:data:`QUALITATIVE_PROTECTIVE`, :data:`QUALITATIVE_ALERTING`) are
provided for when you *want* qualitative marks to harmonise with the display's circadian regime, or
for large qualitative fills where the axis does apply. They are *chromatically* aligned --- warm,
low-M/P for protective; cool, high-M/P for alerting --- an aesthetic alignment, not a light-dose
claim. Confining colour to one hue wedge costs count and contrast, so each is a smaller,
lower-contrast set (5 colours) than the neutral one; all stay CVD-distinct under simulation.

For marks (ticks, points, event lines) laid *over* a Circadia fill, :data:`CIRCADIA_ACCENT` gives a
few high-chroma colours chosen to sit outside the family's colour footprint (so they pop over warm
*and* cool fills) and to stay mutually distinct under CVD --- vivid by design, since their job is to
stand out. All three regime-aware sets are built by ``scripts/build_qualitative.py``.

Validated under deuteran / protan / tritan simulation (Machado et al. 2009).

Examples
--------
>>> import melanopy as mp
>>> mp.QUALITATIVE_NAMES[:3]
['amber', 'sky', 'teal']
>>> mp.QUALITATIVE_PROTECTIVE_NAMES
['amber', 'ember', 'wheat', 'orange', 'tan']
>>> len(mp.CIRCADIA_ACCENT)
4
>>> from matplotlib.colors import to_rgb
>>> prot = mp.melanopic_ratio([to_rgb(c) for c in mp.QUALITATIVE_PROTECTIVE])
>>> bool((prot < 1).all())  # every protective swatch sits below display white (M/P = 1)
True
"""

from matplotlib.colors import ListedColormap

QUALITATIVE_DARK = ["#F2A036", "#81CAF0", "#009C89", "#F1E48C", "#325CAF", "#D85039", "#CE79B3"]
QUALITATIVE_LIGHT = ["#CF8100", "#62AACF", "#007A6B", "#D0C36C", "#163F8E", "#B52E17", "#AD5B93"]
QUALITATIVE_NAMES = ["amber", "sky", "teal", "yellow", "blue", "vermillion", "rose"]
QUALITATIVE = ListedColormap(QUALITATIVE_DARK, name="melanopy_qualitative")

# Regime-themed variants (scripts/build_qualitative.py): chromatically aligned with the melanopic
# regimes --- warm/low-M/P (protective) and cool/high-M/P (alerting). A thematic (aesthetic)
# alignment, not a light-dose claim. Fewer, less-separable colours than the neutral set --- the cost
# of staying on one side of the axis --- but still CVD-distinct under simulation. Ordered so the
# first two swatches are maximally distinct.
QUALITATIVE_PROTECTIVE = ["#db9338", "#984839", "#dfc176", "#bd6533", "#b58763"]
QUALITATIVE_PROTECTIVE_NAMES = ["amber", "ember", "wheat", "orange", "tan"]
QUALITATIVE_ALERTING = ["#3c75bf", "#00999b", "#94dce4", "#283c72", "#55add8"]
QUALITATIVE_ALERTING_NAMES = ["blue", "teal", "ice", "indigo", "sky"]

# Accent palette (scripts/build_qualitative.py): vivid marks that pop over *any* Circadia fill —
# far from the family's colour footprint across all alpha, and mutually distinct under CVD. The
# far-from-family requirement confines them to the magenta/violet/green arc; curated there for a
# coordinated look, then validated against the distance + CVD floors.
CIRCADIA_ACCENT = ["#d84fb0", "#5e2b9e", "#12a074", "#a5d84f"]
CIRCADIA_ACCENT_NAMES = ["orchid", "grape", "emerald", "lime"]

__all__ = [
    "QUALITATIVE_DARK",
    "QUALITATIVE_LIGHT",
    "QUALITATIVE_NAMES",
    "QUALITATIVE",
    "QUALITATIVE_PROTECTIVE",
    "QUALITATIVE_PROTECTIVE_NAMES",
    "QUALITATIVE_ALERTING",
    "QUALITATIVE_ALERTING_NAMES",
    "CIRCADIA_ACCENT",
    "CIRCADIA_ACCENT_NAMES",
]

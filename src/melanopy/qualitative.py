"""CVD-safe qualitative palette.

A fixed colourblind-safe qualitative set for small marks (lines, points, glyphs).
It is deliberately **circadian-neutral**: by the area-weighted budget --- small marks emit
negligible light regardless of their colour --- the melanopic axis does not apply to them, so
this palette is optimised for category separability under colour-vision deficiency, *not* for
melanopic content. Its swatches straddle the axis (some warm, some cool); the melanopic ratio is
reported, never tuned. Validated under deuteran / protan / tritan simulation (Machado et al. 2009).

Examples
--------
>>> import melanopy as mp
>>> mp.QUALITATIVE_NAMES[:3]
['amber', 'sky', 'teal']
>>> len(mp.QUALITATIVE_DARK)
7
"""

from matplotlib.colors import ListedColormap

QUALITATIVE_DARK = ["#F2A036", "#81CAF0", "#009C89", "#F1E48C", "#325CAF", "#D85039", "#CE79B3"]
QUALITATIVE_LIGHT = ["#CF8100", "#62AACF", "#007A6B", "#D0C36C", "#163F8E", "#B52E17", "#AD5B93"]
QUALITATIVE_NAMES = ["amber", "sky", "teal", "yellow", "blue", "vermillion", "rose"]
QUALITATIVE = ListedColormap(QUALITATIVE_DARK, name="melanopy_qualitative")

__all__ = ["QUALITATIVE_DARK", "QUALITATIVE_LIGHT", "QUALITATIVE_NAMES", "QUALITATIVE"]

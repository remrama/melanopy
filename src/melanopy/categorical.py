"""CVD-safe categorical palette.

Area-weighted melanopic budget: small categorical marks (lines, points) emit negligible
light, so a single colourblind-safe set serves every circadian regime. Validated under
deuteran / protan / tritan simulation (Machado et al. 2009).
"""

from matplotlib.colors import ListedColormap

CATEGORICAL_DARK = ["#F2A036", "#81CAF0", "#009C89", "#F1E48C", "#325CAF", "#D85039", "#CE79B3"]
CATEGORICAL_LIGHT = ["#CF8100", "#62AACF", "#007A6B", "#D0C36C", "#163F8E", "#B52E17", "#AD5B93"]
CATEGORICAL_NAMES = ["amber", "sky", "teal", "yellow", "blue", "vermillion", "rose"]
CATEGORICAL = ListedColormap(CATEGORICAL_DARK, name="melanopy_categorical")

__all__ = ["CATEGORICAL_DARK", "CATEGORICAL_LIGHT", "CATEGORICAL_NAMES", "CATEGORICAL"]

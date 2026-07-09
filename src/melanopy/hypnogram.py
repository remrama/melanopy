"""Hypnogram sleep-stage qualitative palette.

A labelled stage -> colour mapping for hypnograms and hypnodensity plots. Unlike a generic
qualitative palette this one *uses* the melanopic axis: sleep stages are ordered by cortical
activation (Wake > REM > N1 > N2 > N3), so the palette walks a diagonal path through the same OKLab
geometry as the Circadia family --- co-varying colour temperature (alerting Wake -> protective N3,
an *emergent* monotone melanopic ratio) with lightness (light Wake -> dark N3, so deep sleep reads
dark and the order survives CVD).

REM does not lie on the depth axis --- its EEG is wake-like --- so on an *activation* axis it sits
between Wake and N1 (monotone in both lightness and melanopic ratio), but its hue is set off the
warm<->cool spine (a magenta-orchid) so it stays distinct from Wake and N1. Artifact and Unscored
are out-of-band neutral greys: they are not stages, so they sit off the axis entirely.

This is a bespoke path through the OKLab geometry, not a literal sample of a named Circadia map; the
melanopic ratio is measured back with the rater, not set here.

Examples
--------
>>> import melanopy as mp
>>> mp.HYPNOGRAM_STAGES
['Wake', 'REM', 'N1', 'N2', 'N3']
>>> sorted(mp.HYPNOGRAM)  # the five stages plus two out-of-band labels
['Artifact', 'N1', 'N2', 'N3', 'REM', 'Unscored', 'Wake']
>>> from matplotlib.colors import to_rgb
>>> stages = [to_rgb(mp.HYPNOGRAM[s]) for s in mp.HYPNOGRAM_STAGES]
>>> r = mp.melanopic_ratio(stages)
>>> bool((r[:-1] > r[1:]).all())  # M/P falls monotonically Wake -> REM -> N1 -> N2 -> N3
True
"""

import numpy as np
from matplotlib.colors import to_hex

from .generator import _CA, _L, _POS, _WA, _clamp

HYPNOGRAM_STAGES = ["Wake", "REM", "N1", "N2", "N3"]

_WAKE_LT = (0.80, 1.00)  # Wake: (lightness, temperature) at the family's light, cool, alerting end
_REM_L, _REM_C, _REM_HUE = 0.68, 0.13, 340.0  # off-spine orchid, between Wake and N1 in activation
# NREM: a clean warm ramp (amber -> sienna -> rust) as (L, C, hue), lightness falling with depth.
# Kept off the family's own warm chroma so the deep end reads as rich rust, not a muddy brown.
_NREM = {
    "N1": (0.63, 0.085, 66),
    "N2": (0.48, 0.105, 54),
    "N3": (0.34, 0.100, 46),
}
_ARTIFACT_L, _UNSCORED_L = 0.50, 0.85  # out-of-band neutral greys (not stages)


def _spine_color(lightness, temperature):
    """Colour at (lightness, temperature) on the Circadia geometry (temperature 0 warm, 1 cool)."""
    p = np.interp(lightness, _L, _POS)  # ramp position with this lightness (L monotone in POS)
    warm = np.array([np.interp(p, _POS, _WA[:, 0]), np.interp(p, _POS, _WA[:, 1])])
    cool = np.array([np.interp(p, _POS, _CA[:, 0]), np.interp(p, _POS, _CA[:, 1])])
    a, b = (1 - temperature) * warm + temperature * cool
    return _clamp(lightness, a, b)


def _hue_color(lightness, chroma, hue_deg):
    r = np.radians(hue_deg)
    return _clamp(lightness, chroma * np.cos(r), chroma * np.sin(r))


HYPNOGRAM = {
    "Wake": to_hex(_spine_color(*_WAKE_LT)),
    "REM": to_hex(_hue_color(_REM_L, _REM_C, _REM_HUE)),
    "N1": to_hex(_hue_color(*_NREM["N1"])),
    "N2": to_hex(_hue_color(*_NREM["N2"])),
    "N3": to_hex(_hue_color(*_NREM["N3"])),
    "Artifact": to_hex(_hue_color(_ARTIFACT_L, 0.0, 0.0)),
    "Unscored": to_hex(_hue_color(_UNSCORED_L, 0.0, 0.0)),
}

__all__ = ["HYPNOGRAM", "HYPNOGRAM_STAGES"]

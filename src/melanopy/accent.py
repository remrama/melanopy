"""Circadia accent palette --- high-chroma marks that pop over any Circadia fill.

For qualitative marks (ticks, points, event lines) drawn *over* a Circadia colormap fill, ordinary
qualitative colours can be lost against the fill or clash with it. :data:`CIRCADIA_ACCENT` is a
small set chosen to sit outside the family's colour footprint across the whole axis (so it contrasts
with warm *and* cool fills) and to stay mutually distinct under colour-vision deficiency --- which
confines it to the magenta/violet/green arc. Vivid by design; derived and validated by
``scripts/build_accent.py``.

For qualitative marks that are *not* over a fill, the melanopic axis does not apply (small marks
emit negligibly) --- any CVD-safe qualitative palette serves.

Examples
--------
>>> import melanopy as mp
>>> mp.CIRCADIA_ACCENT_NAMES
['orchid', 'grape', 'emerald', 'lime']
>>> len(mp.CIRCADIA_ACCENT)
4
"""

CIRCADIA_ACCENT = ["#d84fb0", "#5e2b9e", "#12a074", "#a5d84f"]
CIRCADIA_ACCENT_NAMES = ["orchid", "grape", "emerald", "lime"]

__all__ = ["CIRCADIA_ACCENT", "CIRCADIA_ACCENT_NAMES"]

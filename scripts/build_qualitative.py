"""Derive and validate the themed qualitative palettes (protective / alerting).

Generation-time tool (like ``build_panels.py``): builds palettes from OKLab ``(L, C, hue)``
anchors, clamps them into sRGB with the generator's gamut clamp, and validates them against the
rater (melanopic-ratio sign) and ``colorspacious`` (CVD separability). Prints the hex + names to
bake into ``melanopy.qualitative``.

    uv run --extra dev scripts/build_qualitative.py
"""

import colorspacious as cs
import numpy as np
from matplotlib.colors import to_hex

from melanopy import melanopic_ratio
from melanopy.generator import _clamp


def build(anchors):
    """List of OKLab ``(L, C, hue_deg)`` -> ``(N, 3)`` sRGB, each reduced into gamut."""
    out = []
    for lightness, chroma, hue in anchors:
        r = np.radians(hue)
        out.append(_clamp(lightness, chroma * np.cos(r), chroma * np.sin(r)))
    return np.array(out)


def _min_pairwise(lab):
    d = np.linalg.norm(lab[:, None, :] - lab[None, :, :], axis=-1)
    return d[d > 0].min()


def min_cvd_separation(rgb):
    """Worst-case min pairwise CAM02-UCS separation over normal + 3 dichromacies."""
    worst = _min_pairwise(cs.cspace_convert(np.clip(rgb, 0, 1), "sRGB1", "CAM02-UCS"))
    for cvd in ("deuteranomaly", "protanomaly", "tritanomaly"):
        space = {"name": "sRGB1+CVD", "cvd_type": cvd, "severity": 100}
        sim = np.clip(cs.cspace_convert(np.clip(rgb, 0, 1), space, "sRGB1"), 0, 1)
        worst = min(worst, _min_pairwise(cs.cspace_convert(sim, "sRGB1", "CAM02-UCS")))
    return worst


def report(label, anchors, names):
    rgb = build(anchors)
    m = melanopic_ratio(rgb)
    print(f"\n{label}: worst CVD min-dE = {min_cvd_separation(rgb):.2f}")
    for name, c, ratio in zip(names, rgb, m):
        print(f"  {name:9s} {to_hex(c)}  M/P={ratio:.3f}")
    print(f"  M/P range [{m.min():.3f}, {m.max():.3f}]")
    print(f"  hex = {[to_hex(c) for c in rgb]}")


# (L, C, hue_deg) OKLab anchors — warm wedge (protective) / cool wedge (alerting). Ordered so the
# first two swatches are maximally distinct (the common 2-3 category use); separability inside each
# wedge is bought mostly from lightness, which survives CVD.
PROTECTIVE = [
    (0.72, 0.135, 68),
    (0.50, 0.11, 32),
    (0.82, 0.10, 88),
    (0.60, 0.13, 48),
    (0.66, 0.075, 60),
]
PROTECTIVE_NAMES = ["amber", "ember", "wheat", "orange", "tan"]

ALERTING = [
    (0.56, 0.130, 256),
    (0.62, 0.118, 196),
    (0.85, 0.072, 205),
    (0.37, 0.095, 266),
    (0.71, 0.105, 232),
]
ALERTING_NAMES = ["blue", "teal", "ice", "indigo", "sky"]


if __name__ == "__main__":
    report("PROTECTIVE (warm, M/P<1)", PROTECTIVE, PROTECTIVE_NAMES)
    report("ALERTING  (cool, M/P>1)", ALERTING, ALERTING_NAMES)

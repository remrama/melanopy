"""Derive and validate the regime-aware qualitative palettes (protective / alerting / accent).

Generation-time tool (like ``build_panels.py``). The themed sets (protective / alerting) are built
from OKLab ``(L, C, hue)`` anchors and clamped into sRGB with the generator's gamut clamp; the
accent set is farthest-point-sampled away from the Circadia family's colour footprint. All are
validated against the rater (melanopic-ratio sign) and ``colorspacious`` (CVD separability). Prints
the hex + names to bake into ``melanopy.qualitative``.

    uv run --extra dev scripts/build_qualitative.py
"""

import colorspacious as cs
import numpy as np
from matplotlib.colors import to_hex

from melanopy import circadia, melanopic_ratio
from melanopy.generator import _clamp

CVDS = ("deuteranomaly", "protanomaly", "tritanomaly")


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


# --- accent palette: marks that pop over any Circadia fill --------------------------------------
# Marks (ticks, points, event lines) overlaid on a Circadia fill must (a) sit outside the region of
# colour space the family occupies across all alpha, so they contrast against warm *and* cool fills,
# and (b) stay mutually distinct under CVD. We build the family's CAM02-UCS footprint, then greedily
# farthest-point-sample high-chroma candidates that are far from it, scoring mutual distance by the
# worst case over normal + the three dichromacies.


def _cam(rgb):
    return cs.cspace_convert(np.clip(rgb, 0, 1), "sRGB1", "CAM02-UCS")


def _cvd_cam(rgb, cvd):
    space = {"name": "sRGB1+CVD", "cvd_type": cvd, "severity": 100}
    return _cam(np.clip(cs.cspace_convert(np.clip(rgb, 0, 1), space, "sRGB1"), 0, 1))


def family_footprint(n_alpha=11, n_ramp=48):
    """CAM02-UCS point cloud of the whole Circadia family (union over alpha)."""
    rgb = np.vstack([circadia(a, n=n_ramp) for a in np.linspace(0, 1, n_alpha)])
    return _cam(rgb)


def _min_to_cloud(lab, cloud):
    return np.linalg.norm(lab[:, None, :] - cloud[None, :, :], axis=-1).min(axis=1)


def build_accent(k=5, family_floor=18.0):
    """Greedy farthest-point accent set: far from the family footprint, mutually CVD-distinct."""
    cloud = family_footprint()
    cands = []
    for lightness in (0.45, 0.60, 0.72, 0.85):
        for hue in range(0, 360, 6):
            for chroma in (0.12, 0.16, 0.20, 0.26):
                r = np.radians(hue)
                cands.append(_clamp(lightness, chroma * np.cos(r), chroma * np.sin(r)))
    cands = np.array(cands)
    labs = {"normal": _cam(cands)}
    for cvd in CVDS:
        labs[cvd] = _cvd_cam(cands, cvd)
    fam_d = _min_to_cloud(labs["normal"], cloud)
    idx = [int(i) for i in np.where(fam_d > family_floor)[0]]

    def worst_pair(i, j):  # smallest separation over normal + the three dichromacies
        return min(float(np.linalg.norm(labs[key][i] - labs[key][j])) for key in labs)

    sel = [max(idx, key=lambda i: fam_d[i])]  # seed: farthest from the family
    while len(sel) < k:
        rest = (i for i in idx if i not in sel)
        sel.append(max(rest, key=lambda i: min(worst_pair(i, s) for s in sel)))
    return cands[sel], fam_d[sel]


def report_accent(k=5):
    rgb, fam_d = build_accent(k=k)
    mutual = min_cvd_separation(rgb)
    print(
        f"\nACCENT (k={k}): worst mutual CVD min-dE = {mutual:.2f}, "
        f"min dist to family = {fam_d.min():.2f}"
    )
    for c, d in zip(rgb, fam_d):
        print(f"  {to_hex(c)}  dist-to-family={d:.1f}  M/P={melanopic_ratio(c)[0]:.3f}")
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
    report_accent(k=5)

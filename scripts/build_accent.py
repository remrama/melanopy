"""Derive and validate the Circadia accent palette.

Generation-time tool (like ``build_panels.py``). Accent marks drawn over a Circadia fill must sit
outside the region of colour space the family occupies across all alpha (so they contrast with warm
*and* cool fills) and stay mutually distinct under CVD. ``build_accent`` farthest-point-samples that
region; the raw maximiser is garish, so the shipped set (``ACCENT``) is CURATED within the same arc
for a coordinated look, re-checked against the floors, and baked into ``melanopy.accent``.

    uv run --extra dev scripts/build_accent.py
"""

import colorspacious as cs
import numpy as np
from matplotlib.colors import to_hex, to_rgb

from melanopy import circadia, melanopic_ratio
from melanopy.generator import _clamp

CVDS = ("deuteranomaly", "protanomaly", "tritanomaly")


def _min_pairwise(lab):
    d = np.linalg.norm(lab[:, None, :] - lab[None, :, :], axis=-1)
    return d[d > 0].min()


def min_cvd_separation(rgb):
    """Worst-case min pairwise CAM02-UCS separation over normal + 3 dichromacies."""
    worst = _min_pairwise(cs.cspace_convert(np.clip(rgb, 0, 1), "sRGB1", "CAM02-UCS"))
    for cvd in CVDS:
        space = {"name": "sRGB1+CVD", "cvd_type": cvd, "severity": 100}
        sim = np.clip(cs.cspace_convert(np.clip(rgb, 0, 1), space, "sRGB1"), 0, 1)
        worst = min(worst, _min_pairwise(cs.cspace_convert(sim, "sRGB1", "CAM02-UCS")))
    return worst


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
        f"\nACCENT search (k={k}, raw): worst mutual CVD min-dE = {mutual:.2f}, "
        f"min dist to family = {fam_d.min():.2f}"
    )
    for c, d in zip(rgb, fam_d):
        print(f"  {to_hex(c)}  dist-to-family={d:.1f}  M/P={melanopic_ratio(c)[0]:.3f}")
    print(f"  hex = {[to_hex(c) for c in rgb]}")


# Shipped accent set: the raw farthest-point search maximises the two floors but looks garish, so we
# CURATE within the same far-from-family arc for a coordinated look, then check the floors still
# hold. Ordered orchid / grape / emerald / lime.
ACCENT = ["#d84fb0", "#5e2b9e", "#12a074", "#a5d84f"]
ACCENT_NAMES = ["orchid", "grape", "emerald", "lime"]


def report_curated_accent():
    rgb = np.array([to_rgb(c) for c in ACCENT])
    fam = _min_to_cloud(_cam(rgb), family_footprint()).min()
    print(
        f"\nACCENT (curated, k={len(ACCENT)}): min dist to family = {fam:.1f}, "
        f"worst mutual CVD min-dE = {min_cvd_separation(rgb):.1f}"
    )
    for hx, nm in zip(ACCENT, ACCENT_NAMES):
        print(f"  {nm:8s} {hx}")


if __name__ == "__main__":
    report_curated_accent()
    report_accent(k=5)  # raw farthest-point search, for reference (metric-max, garish)

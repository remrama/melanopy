"""Regenerate the scored index (``index/leaderboard.csv``) from the shipped package.

Scores a spread of common matplotlib colormaps plus the Melanopy endpoints on the
melanopic axis via :func:`melanopy.rate_colormap`, and writes them sorted protective ->
alerting. Repo-relative and dependency-light (only ``melanopy`` + matplotlib's builtin
colormaps).

    uv run scripts/build_leaderboard.py
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import melanopy as mp

# matplotlib builtins to score (the Melanopy endpoints are added below).
BUILTINS = [
    "hot", "copper", "inferno", "afmhot", "cividis", "magma", "plasma",
    "turbo", "viridis", "jet", "gray", "Blues", "winter", "cool",
]  # fmt: skip
N = 256
_T = np.linspace(0, 1, N)
FIELDS = ["colormap", "melanopic_ratio", "purity_sigma", "range_min", "range_max"]


def _samples():
    """label -> (N, 3) sRGB ramp, for the Melanopy endpoints and the builtins."""
    out = {
        f"{name} (melanopy)": cm(_T)[:, :3]
        for name, cm in [("sodium", mp.SODIUM), ("equilux", mp.EQUILUX), ("xenon", mp.XENON)]
    }
    out.update({name: plt.get_cmap(name)(_T)[:, :3] for name in BUILTINS})
    return out


def _row(name, colors):
    s = mp.rate_colormap(colors)
    return {
        "colormap": name,
        "melanopic_ratio": round(s["melanopic_ratio"], 4),
        "purity_sigma": round(s["purity_sigma"], 4),
        "range_min": round(s["range"][0], 4),
        "range_max": round(s["range"][1], 4),
    }


def main():
    rows = sorted(
        (_row(name, colors) for name, colors in _samples().items()),
        key=lambda r: r["melanopic_ratio"],
    )
    out = Path(__file__).resolve().parents[1] / "index" / "leaderboard.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out} ({len(rows)} maps)")


if __name__ == "__main__":
    main()

"""Multi-panel robustness of the melanopic leaderboard.

Scores the same colormaps as ``scripts/build_leaderboard.py`` under every panel archetype in
``melanopy.coeffs.PANELS``, then reports how stable the protective -> alerting *ranking* is
across panels (Spearman rho vs the representative panel) and a per-map M/P band (min..max).
Writes ``index/panel_robustness.csv`` and prints the rank-stability summary — answering the
panel-relativity question: absolute M/P is panel-dependent, the ranking is not.

    uv run scripts/build_panel_robustness.py
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import melanopy as mp
from melanopy.coeffs import PANELS

BUILTINS = [
    "hot", "copper", "inferno", "afmhot", "cividis", "magma", "plasma",
    "turbo", "viridis", "jet", "gray", "Blues", "winter", "cool",
]  # fmt: skip
N = 256
_T = np.linspace(0, 1, N)
PANEL_NAMES = list(PANELS)  # representative first (dict insertion order)


def _samples():
    out = {
        f"{name} (melanopy)": cm(_T)[:, :3]
        for name, cm in [("ember", mp.EMBER), ("equinox", mp.EQUINOX), ("glacier", mp.GLACIER)]
    }
    out.update({name: plt.get_cmap(name)(_T)[:, :3] for name in BUILTINS})
    return out


def _spearman(a, b):
    """Spearman rho between two equal-length score sequences (no ties expected in M/P)."""
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    samples = _samples()
    scores = {
        panel: {
            name: mp.rate_colormap(c, panel=panel)["melanopic_ratio"] for name, c in samples.items()
        }
        for panel in PANEL_NAMES
    }
    names = sorted(samples, key=lambda n: scores["representative"][n])

    rows = []
    for n in names:
        vals = [scores[p][n] for p in PANEL_NAMES]
        row = {"colormap": n, **{p: round(scores[p][n], 4) for p in PANEL_NAMES}}
        row["band"] = round(max(vals) - min(vals), 4)
        rows.append(row)

    out = Path(__file__).resolve().parents[1] / "index" / "panel_robustness.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["colormap", *PANEL_NAMES, "band"])
        w.writeheader()
        w.writerows(rows)

    ref = [scores["representative"][n] for n in names]
    print(f"wrote {out} ({len(rows)} maps x {len(PANEL_NAMES)} panels)")
    print("rank stability vs representative (Spearman rho):")
    for p in PANEL_NAMES:
        print(f"  {p:14s} {_spearman(ref, [scores[p][n] for n in names]):.4f}")
    worst = max(rows, key=lambda r: r["band"])
    print(f"widest M/P band: {worst['colormap']} ({worst['band']})")


if __name__ == "__main__":
    main()

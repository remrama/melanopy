"""Render colormap swatch images for the docs API reference into ``docs/assets/figures/``.

The docs site (``.github/workflows/docs.yml``) only runs ``zensical build``; it does not regenerate
figures, so these PNGs are committed. Re-run after changing the generator or the accent palette:

    uv run --extra dev scripts/build_docs_swatches.py
"""

from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import melanopy as mp

OUT = Path(__file__).resolve().parents[1] / "docs" / "assets" / "figures"
GRAD = np.linspace(0, 1, 256).reshape(1, -1)
INK, HAIR = "#444444", "#cccccc"


def _strip(ax, cmap, label):
    ax.imshow(GRAD, aspect="auto", cmap=cmap)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color(HAIR)
    ax.set_ylabel(label, rotation=0, ha="right", va="center", color=INK, fontsize=10, labelpad=10)


def circadia_family(path):
    rows = [
        ("circadia(0.0) · SODIUM", 0.0),
        ("circadia(0.25)", 0.25),
        ("circadia(0.55) · EQUILUX", 0.55),
        ("circadia(0.75)", 0.75),
        ("circadia(1.0) · XENON", 1.0),
    ]
    fig, axes = plt.subplots(len(rows), 1, figsize=(7, 3.0), facecolor="white")
    fig.subplots_adjust(left=0.32, right=0.98, top=0.98, bottom=0.02, hspace=0.55)
    for ax, (label, alpha) in zip(axes, rows):
        _strip(ax, mp.circadia(alpha, as_cmap=True), label)
    fig.savefig(path, dpi=140, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def circadia_special(path):
    rows = [
        ("circadia_sweep", mp.circadia_sweep(as_cmap=True)),
        ("circadia_diverging", mp.circadia_diverging(as_cmap=True)),
    ]
    fig, axes = plt.subplots(len(rows), 1, figsize=(7, 1.5), facecolor="white")
    fig.subplots_adjust(left=0.28, right=0.98, top=0.95, bottom=0.05, hspace=0.75)
    for ax, (label, cmap) in zip(axes, rows):
        _strip(ax, cmap, label)
    fig.savefig(path, dpi=140, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def accent_swatches(path):
    fig, ax = plt.subplots(figsize=(7, 1.5), facecolor="white")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    for i, (color, name) in enumerate(zip(mp.CIRCADIA_ACCENT, mp.CIRCADIA_ACCENT_NAMES)):
        ax.add_patch(plt.Rectangle((i + 0.06, 0.28), 0.88, 0.66, color=color, ec=HAIR, lw=0.5))
        ax.text(i + 0.5, 0.16, name, ha="center", va="top", color=INK, fontsize=10)
        ax.text(i + 0.5, 0.02, color, ha="center", va="top", color="#888", fontsize=8.5)
    ax.set_xlim(0, len(mp.CIRCADIA_ACCENT))
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    fig.savefig(path, dpi=140, facecolor="white", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    circadia_family(OUT / "circadia_family.png")
    circadia_special(OUT / "circadia_special.png")
    accent_swatches(OUT / "accent_swatches.png")
    print(f"wrote circadia_family.png, circadia_special.png, accent_swatches.png to {OUT}")

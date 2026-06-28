"""Cookbook figure: a circadian colormap on circadian data ("match the map to the data").

Two deterministic panels, built only from melanopy + matplotlib + numpy:

* a sleep-wake raster coloured by ``circadia_sweep`` -- awake reads as alerting (cool), asleep as
  protective (warm), so the sequential map's melanopic axis *is* the sleep-wake axis;
* a circadian alerting-drive curve coloured by ``circadia_diverging`` -- the biological day arm is
  alerting (cool), the night arm protective (warm), and the zero crossing is circadian-neutral.

    uv run scripts/build_sleep_wake_demo.py

Writes docs/assets/figures/sleep_wake_demo.png (the manuscript can adopt it later).
"""

from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize

import melanopy as mp

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "figures" / "sleep_wake_demo.png"

BG, PANEL, INK, INK2, HAIR = "#181410", "#221C16", "#ECE3D4", "#A99D89", "#3A332B"
AMBER, BLUE = "#F2A93E", "#4A9BE8"

# A noon-to-noon frame keeps the nocturnal sleep block contiguous and centred.
H0, H1, NBIN, NDAY = 12.0, 36.0, 144, 14
HOURS = np.linspace(H0, H1, NBIN, endpoint=False)


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def sleep_wake_raster():
    """Deterministic wakefulness in [0, 1] (1 = awake), NDAY x NBIN, with a mild phase delay."""
    rng = np.random.default_rng(0)
    rows = []
    for d in range(NDAY):
        onset = 23.2 + 0.11 * d  # bedtime creeps later across the fortnight
        offset = 31.4 + 0.04 * d  # wake time (07:24, +24 h) drifts a touch
        asleep = _sigmoid(2.6 * (HOURS - onset)) * _sigmoid(2.6 * (offset - HOURS))
        wake = 1.0 - asleep + rng.normal(0.0, 0.035, NBIN)
        rows.append(np.clip(wake, 0.0, 1.0))
    return np.vstack(rows)


def alerting_drive():
    """Signed circadian alerting drive over the frame: +1 alerting at 16:00, -1 at 04:00."""
    return np.cos(2 * np.pi * (HOURS - 16.0) / 24.0)


def _hour_axis(ax):
    ax.set_xlim(H0, H1)
    ax.set_xticks([12, 18, 24, 30, 36])
    ax.set_xticklabels(["12:00", "18:00", "00:00", "06:00", "12:00"])
    ax.tick_params(colors=INK2)
    for sp in ax.spines.values():
        sp.set_color(HAIR)


def _raster_panel(fig, ax):
    ax.set_facecolor(PANEL)
    im = ax.imshow(
        sleep_wake_raster(),
        aspect="auto",
        cmap=mp.circadia_sweep(as_cmap=True),
        vmin=0.0,
        vmax=1.0,
        extent=[H0, H1, NDAY + 0.5, 0.5],
        interpolation="nearest",
    )
    _hour_axis(ax)
    ax.set_yticks([1, 5, 10, 14])
    ax.set_ylabel("day", color=INK2)
    ax.set_title(
        "Sleep–wake raster — circadia_sweep maps asleep → protective (warm), "
        "awake → alerting (cool)",
        color=INK,
        loc="left",
        fontsize=11,
        pad=6,
    )
    cb = fig.colorbar(im, ax=ax, ticks=[0, 1], pad=0.02, fraction=0.045)
    cb.ax.set_yticklabels(["asleep\n(protective)", "awake\n(alerting)"], color=INK2, fontsize=8)
    cb.outline.set_edgecolor(HAIR)


def _drive_panel(ax):
    ax.set_facecolor(PANEL)
    drive = alerting_drive()
    pts = np.array([HOURS, drive]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, cmap=mp.circadia_diverging(as_cmap=True), norm=Normalize(-1, 1))
    lc.set_array(0.5 * (drive[:-1] + drive[1:]))
    lc.set_linewidth(3.2)
    ax.add_collection(lc)
    ax.axhline(0.0, color=INK2, lw=0.9, ls=":")
    ax.text(H0 + 0.2, 0.08, "circadian-neutral (M/P ≈ 1)", color=INK2, fontsize=8, va="bottom")
    ax.set_ylim(-1.18, 1.18)
    _hour_axis(ax)
    ax.set_yticks([-1, 0, 1])
    ax.set_ylabel("alerting drive", color=INK2)
    ax.text(H1 - 0.2, 0.92, "+ alerting (cool)", color=BLUE, fontsize=8.5, ha="right", va="top")
    ax.text(
        H1 - 0.2,
        -0.92,
        "− sleep-promoting (warm)",
        color=AMBER,
        fontsize=8.5,
        ha="right",
        va="bottom",
    )
    ax.set_title(
        "Circadian alerting drive — circadia_diverging splits the biological day from the night",
        color=INK,
        loc="left",
        fontsize=11,
        pad=6,
    )


def build(path):
    plt.rcParams.update({"font.size": 10, "text.color": INK, "axes.edgecolor": HAIR})
    fig = plt.figure(figsize=(11, 7.2), facecolor=BG)
    gs = fig.add_gridspec(
        2, 1, height_ratios=[2.3, 1.0], hspace=0.42, left=0.10, right=0.88, top=0.9, bottom=0.1
    )
    _raster_panel(fig, fig.add_subplot(gs[0]))
    _drive_panel(fig.add_subplot(gs[1]))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120, facecolor=BG)
    plt.close(fig)


def main():
    build(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

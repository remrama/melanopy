"""Regenerate the paper figures from the shipped package (repo-relative, reproducible).

Replaces the prototype builders in NOTES/scripts/ (which carried /home/claude paths, prototype
imports, and a duplicated analytic rater). Everything here reads from `melanopy` and the scored
index in `index/`; CVD simulation uses `colorspacious` (the dev-extra dependency the tests use).

    uv run --extra dev scripts/build_figures.py             # all figures
    uv run --extra dev scripts/build_figures.py generator   # just one

Figures are written to NOTES/paper/figures/ (alongside the manuscript draft).
"""

import csv
import sys
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import colorspacious as cs
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, to_rgb

import melanopy as mp
from melanopy.coeffs import LUM_W

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "NOTES" / "paper" / "figures"
T = np.linspace(0, 1, 256)
CVD = [
    ("normal", None),
    ("deuteran", "deuteranomaly"),
    ("protan", "protanomaly"),
    ("tritan", "tritanomaly"),
]

# dark-console theme (matches the prototype plates)
BG, PANEL, INK, INK2, HAIR = "#181410", "#221C16", "#ECE3D4", "#A99D89", "#3A332B"
AMBER, TEAL, BLUE, GREY = "#F2A93E", "#34C2A4", "#4A9BE8", "#A99D89"
RGB_COLS = ["#E0573B", "#79CC70", "#4987D9"]


def _theme():
    plt.rcParams.update({"font.size": 10, "text.color": INK, "axes.edgecolor": HAIR})


def _cvd(colors, kind):
    """Machado-2009 dichromacy simulation (severity 100) of an sRGB ramp, via colorspacious."""
    if kind is None:
        return np.clip(colors, 0, 1)
    space = {"name": "sRGB1+CVD", "cvd_type": kind, "severity": 100}
    return np.clip(cs.cspace_convert(np.clip(colors, 0, 1), space, "sRGB1"), 0, 1)


def _luminance(colors):
    c = np.asarray(colors, float)
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return lin @ np.array([LUM_W["R"], LUM_W["G"], LUM_W["B"]])


def _strip(ax, colors, label=None):
    ax.imshow(T.reshape(1, -1), aspect="auto", cmap=ListedColormap(np.clip(colors, 0, 1)))
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color(HAIR)
    if label:
        ax.set_ylabel(
            label, color=INK2, fontsize=9, rotation=0, ha="right", va="center", labelpad=18
        )


def _title(ax, text, size=11, pad=4):
    ax.set_title(text, color=INK, fontsize=size, loc="left", pad=pad)


def _colors_for(label):
    """sRGB ramp for a leaderboard label ('sodium (melanopy)' -> Diel endpoint, else builtin)."""
    named = {"sodium": mp.SODIUM, "equilux": mp.EQUILUX, "xenon": mp.XENON}
    key = label.replace(" (melanopy)", "")
    cm = named[key] if "(melanopy)" in label else plt.get_cmap(key)
    return cm(T)[:, :3]


def _read_csv(name):
    with (ROOT / "index" / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ----------------------------------------------------------------------------- generator
def fig_generator(path):
    alphas = np.linspace(0, 1, 21)
    axis = np.array([mp.rate_colormap(mp.diel(a))["melanopic_ratio"] for a in alphas])
    sigma = np.array([mp.rate_colormap(mp.diel(a))["purity_sigma"] for a in alphas])

    _theme()
    fig = plt.figure(figsize=(12, 14), facecolor=BG)
    gs = fig.add_gridspec(
        4,
        1,
        height_ratios=[1.9, 1.25, 1.2, 0.85],
        hspace=0.5,
        left=0.10,
        right=0.95,
        top=0.95,
        bottom=0.05,
    )

    # A: the family
    show = np.linspace(0, 1, 9)
    gsa = gs[0].subgridspec(len(show), 1, hspace=0.85)
    for i, a in enumerate(show):
        s = mp.rate_colormap(mp.diel(a))
        ax = fig.add_subplot(gsa[i])
        _strip(ax, mp.diel(a), f"α={a:.2f}")
        ax.text(
            1.012,
            0.5,
            f"M/P {s['melanopic_ratio']:.2f}  ·  σ {s['purity_sigma']:.2f}",
            transform=ax.transAxes,
            color=INK2,
            fontsize=8,
            va="center",
        )
        if i == 0:
            _title(
                ax,
                "The family — one lightness profile, chroma morphs warm → neutral → cool",
                size=12,
                pad=6,
            )

    # B: melanopic ratio + purity vs alpha
    axb = fig.add_subplot(gs[1])
    axb.set_facecolor(PANEL)
    axb.plot(alphas, axis, color=AMBER, lw=2.4, marker="o", ms=4, label="melanopic ratio")
    axb.axhline(1.0, color=INK2, lw=0.9, ls=":")
    axb.text(0.01, 1.04, "white = 1.0", color=INK2, fontsize=8)
    axb.set_xlabel("α  (protective → alerting)", color=INK2)
    axb.set_ylabel("melanopic ratio", color=AMBER)
    axb.set_xlim(0, 1)
    axb.tick_params(colors=INK2)
    axb.tick_params(axis="y", colors=AMBER)
    axc = axb.twinx()
    axc.plot(alphas, sigma, color=TEAL, lw=2.0, ls="--", marker="s", ms=3, label="purity σ")
    axc.set_ylabel("purity σ", color=TEAL)
    axc.tick_params(axis="y", colors=TEAL)
    axc.set_ylim(0, max(0.2, sigma.max() * 1.4))
    for sp in (*axb.spines.values(), *axc.spines.values()):
        sp.set_color(HAIR)
    h1, l1 = axb.get_legend_handles_labels()
    h2, l2 = axc.get_legend_handles_labels()
    axb.legend(h1 + h2, l1 + l2, facecolor=PANEL, edgecolor=HAIR, fontsize=8.5, labelcolor=INK2)
    _title(
        axb,
        "Proof — melanopic ratio rises monotonically with α; purity σ low on the warm "
        "side, bounded at the cool end",
        size=10.5,
    )

    # C: per-position melanopic profiles
    axp = fig.add_subplot(gs[2])
    axp.set_facecolor(PANEL)
    for a, col in [(0.0, AMBER), (0.5, GREY), (1.0, BLUE)]:
        colors = mp.diel(a)
        prof = mp.melanopic_ratio(colors)
        y = _luminance(colors)
        axp.plot(T, np.where(y > 0.01 * y.max(), prof, np.nan), color=col, lw=2, label=f"α={a:.1f}")
    axp.axhline(1.0, color=INK2, lw=0.9, ls=":")
    axp.set_xlim(0, 1)
    axp.set_ylim(0, 2.0)
    axp.set_xlabel("data value", color=INK2)
    axp.set_ylabel("melanopic ratio", color=INK2)
    axp.tick_params(colors=INK2)
    for sp in axp.spines.values():
        sp.set_color(HAIR)
    axp.legend(facecolor=PANEL, edgecolor=HAIR, fontsize=8.5, labelcolor=INK2, loc="upper right")
    _title(
        axp,
        "Per-α profiles — flat & pure on the warm side, sloped at the cool end "
        "(light blues must desaturate)",
        size=10.5,
    )

    # D: alerting endpoint under CVD
    gsd = gs[3].subgridspec(4, 1, hspace=0.45)
    xenon = mp.diel(1.0)
    for k, (lab, kind) in enumerate(CVD):
        ax = fig.add_subplot(gsd[k])
        _strip(ax, _cvd(xenon, kind), lab)
        if k == 0:
            _title(
                ax,
                "Alerting endpoint (α=1) under dichromacy — order preserved (shared monotonic L)",
            )

    fig.savefig(path, dpi=120, facecolor=BG)
    plt.close(fig)


# ----------------------------------------------------------------------------- leaderboard
def fig_leaderboard(path):
    lb = _read_csv("leaderboard.csv")
    bands = {r["colormap"]: r for r in _read_csv("panel_robustness.csv")}
    panels = ("representative", "led_lcd", "oled", "wide_gamut")
    names = [r["colormap"] for r in lb]  # already sorted protective -> alerting
    n = len(names)

    _theme()
    fig = plt.figure(figsize=(12, 9), facecolor=BG)
    gs = fig.add_gridspec(
        1, 2, width_ratios=[1.0, 1.9], wspace=0.02, left=0.13, right=0.90, top=0.90, bottom=0.07
    )
    axl, axr = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])

    ticks, labels = [], []
    for i, name in enumerate(names):
        y = n - 1 - i
        axl.imshow(
            _colors_for(name).reshape(1, -1, 3), extent=[0, 1, y + 0.14, y + 0.86], aspect="auto"
        )
        axl.add_patch(plt.Rectangle((0, y + 0.14), 1, 0.72, fill=False, edgecolor=HAIR, lw=0.6))
        ticks.append(y + 0.5)
        labels.append(name)
        mpr = float(lb[i]["melanopic_ratio"])
        vals = [float(bands[name][p]) for p in panels]
        axr.add_patch(
            plt.Rectangle((min(vals), y + 0.36), max(vals) - min(vals), 0.28, color=HAIR, alpha=0.9)
        )
        axr.errorbar(
            mpr,
            y + 0.5,
            xerr=[[mpr - min(vals)], [max(vals) - mpr]],
            fmt="o",
            ms=5,
            color=INK,
            ecolor=INK2,
            elinewidth=1.5,
            capsize=3,
        )
        axr.text(2.38, y + 0.5, f"{mpr:.2f}", color=INK2, fontsize=8, va="center", ha="right")

    axl.set_xlim(0, 1)
    axl.set_ylim(0, n)
    axl.set_facecolor(BG)
    axl.set_xticks([])
    axl.set_yticks(ticks)
    axl.set_yticklabels(labels, fontsize=9.5, color=INK)
    axl.tick_params(length=0)
    for sp in axl.spines.values():
        sp.set_visible(False)

    axr.axvline(1.0, color=INK2, lw=1.0, ls="--")
    axr.text(1.0, n + 0.12, "white = 1.0", color=INK2, fontsize=8, ha="center")
    axr.text(0.0, n + 0.12, "← protective (warm)", color=AMBER, fontsize=9, ha="left")
    axr.text(2.4, n + 0.12, "alerting (cool) →", color=BLUE, fontsize=9, ha="right")
    axr.set_xlim(0, 2.45)
    axr.set_ylim(0, n)
    axr.set_yticks([])
    axr.tick_params(colors=INK2)
    axr.set_facecolor(PANEL)
    for sp in axr.spines.values():
        sp.set_color(HAIR)
    axr.set_xlabel(
        "melanopic ratio (axis position)   ·   bar = spread across 4 panel archetypes", color=INK2
    )
    fig.suptitle(
        "Melanopic leaderboard — existing colormaps on the circadian axis "
        "(ranking stable across panels, Spearman ρ ≥ 0.99)",
        color=INK,
        fontsize=12.5,
        x=0.13,
        ha="left",
    )
    fig.savefig(path, dpi=120, facecolor=BG)
    plt.close(fig)


# ----------------------------------------------------------------------------- validation
def fig_validation(path):
    from melanopy import spectra  # needs the vendored CIE data/

    wl = spectra.WL
    smel, vlam = spectra.SMEL, spectra.V
    prim = spectra.representative_primaries()
    coeffs = mp.coeffs.PANELS["representative"]

    _theme()
    fig = plt.figure(figsize=(11, 8.5), facecolor=BG)
    gs = fig.add_gridspec(
        2, 1, height_ratios=[1.55, 1.0], hspace=0.32, left=0.09, right=0.96, top=0.92, bottom=0.09
    )

    # A: action spectrum vs V(lambda) vs display primaries
    ax = fig.add_subplot(gs[0])
    ax.set_facecolor(PANEL)
    peak = wl[smel.argmax()]
    ax.axvspan(460, 490, color=TEAL, alpha=0.08)
    ax.fill_between(wl, smel, color=TEAL, alpha=0.18)
    smel_lbl = f"melanopic action spectrum s(λ)  (peak {peak:.0f} nm)"
    ax.plot(wl, smel, color=TEAL, lw=2.3, label=smel_lbl)
    ax.plot(wl, vlam, color=INK, lw=1.4, ls=":", label="photopic V(λ)")
    for k, col in zip("RGB", RGB_COLS):
        p = prim[k]
        ax.plot(wl, p / p.max(), color=col, lw=1.5, alpha=0.9)
    ax.set_xlim(380, 720)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("wavelength (nm)", color=INK2)
    ax.tick_params(colors=INK2)
    for sp in ax.spines.values():
        sp.set_color(HAIR)
    ax.legend(facecolor=PANEL, edgecolor=HAIR, fontsize=8.5, labelcolor=INK2, loc="upper right")
    _title(
        ax, "CIE S 026 melanopic action spectrum vs the representative display primaries", size=11.5
    )

    # B: per-primary coefficients + the white normalizer
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor(PANEL)
    keys = ["R", "G", "B"]
    ax2.bar(keys, [coeffs[k] for k in keys], color=RGB_COLS, width=0.6)
    for i, k in enumerate(keys):
        ax2.text(
            i, coeffs[k], f"  {coeffs[k]:.4f}", color=INK, fontsize=10, va="bottom", ha="center"
        )
    ax2.set_yscale("log")
    ax2.set_ylabel("per-primary melanopic / photopic", color=INK2)
    ax2.tick_params(colors=INK2)
    for sp in ax2.spines.values():
        sp.set_color(HAIR)
    white = sum(LUM_W[k] * coeffs[k] for k in keys)
    _title(
        ax2,
        f"Three coefficients carry all display dependence — display white M/P = "
        f"{white:.3f} normalizes to 1.000 (grey = 1.000 by construction)",
        size=10.5,
    )

    fig.savefig(path, dpi=120, facecolor=BG)
    plt.close(fig)


# ----------------------------------------------------------------------------- nightwatch
def _pairwise_min(colors):
    lab = cs.cspace_convert(np.clip(colors, 0, 1), "sRGB1", "CAM02-UCS")
    d = np.linalg.norm(lab[:, None, :] - lab[None, :, :], axis=-1)
    return d[d > 0].min()


def fig_nightwatch(path):
    sodium = mp.diel(0.0)
    cat = np.array([to_rgb(c) for c in mp.CATEGORICAL_DARK])
    names = mp.CATEGORICAL_NAMES

    _theme()
    fig = plt.figure(figsize=(11, 10.5), facecolor=BG)
    gs = fig.add_gridspec(
        3,
        1,
        height_ratios=[1.5, 1.0, 1.5],
        hspace=0.45,
        left=0.10,
        right=0.95,
        top=0.93,
        bottom=0.05,
    )

    # A: Sodium sequential under normal + CVD
    gsa = gs[0].subgridspec(4, 1, hspace=0.45)
    for k, (lab, kind) in enumerate(CVD):
        ax = fig.add_subplot(gsa[k])
        _strip(ax, _cvd(sodium, kind), lab)
        if k == 0:
            _title(
                ax,
                "Sodium (protective sequential) — order preserved under dichromacy "
                "(lightness does the work)",
            )

    # B: categorical swatches
    axc = fig.add_subplot(gs[1])
    axc.set_facecolor(PANEL)
    axc.set_xlim(0, len(cat))
    axc.set_ylim(0, 1)
    axc.set_xticks([])
    axc.set_yticks([])
    for sp in axc.spines.values():
        sp.set_color(HAIR)
    for i, c in enumerate(cat):
        axc.add_patch(plt.Rectangle((i + 0.08, 0.30), 0.84, 0.62, color=c))
        axc.text(i + 0.5, 0.14, names[i], ha="center", va="center", color=INK2, fontsize=8.5)
    _title(
        axc,
        "CVD-safe categorical set — one palette serves every circadian regime "
        "(area-weighted budget)",
    )

    # C: categorical under CVD (separability)
    axt = fig.add_subplot(gs[2])
    axt.set_facecolor(PANEL)
    axt.set_xlim(0, len(cat))
    axt.set_ylim(0, len(CVD))
    axt.set_xticks([])
    axt.set_yticks([])
    for sp in axt.spines.values():
        sp.set_color(HAIR)
    for r, (lab, kind) in enumerate(CVD):
        sim = _cvd(cat, kind)
        y = len(CVD) - 1 - r
        for i, c in enumerate(sim):
            axt.add_patch(plt.Rectangle((i + 0.06, y + 0.12), 0.88, 0.76, color=c))
        axt.text(
            -0.1,
            y + 0.5,
            f"{lab}\nΔmin {_pairwise_min(sim):.2f}",
            ha="right",
            va="center",
            color=INK2,
            fontsize=8.5,
        )
    _title(
        axt,
        "Categorical under simulated dichromacy — min CAM02-UCS separation stays well "
        "above the confusion floor",
        size=10.5,
    )

    fig.savefig(path, dpi=120, facecolor=BG)
    plt.close(fig)


FIGURES = {
    "generator": (fig_generator, "circadian_generator.png"),
    "leaderboard": (fig_leaderboard, "melanopic_leaderboard.png"),
    "validation": (fig_validation, "s026_validation.png"),
    "nightwatch": (fig_nightwatch, "nightwatch_colormaps.png"),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for key in sys.argv[1:] or list(FIGURES):
        func, filename = FIGURES[key]
        func(OUT / filename)
        print(f"wrote {OUT / filename}")


if __name__ == "__main__":
    main()

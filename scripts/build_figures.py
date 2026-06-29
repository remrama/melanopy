"""Regenerate the paper figures from the shipped package (repo-relative, reproducible).

Everything here reads from `melanopy` and the scored index in `index/`; CVD simulation uses
`colorspacious` (the dev-extra dependency the tests use).

    uv run --extra dev scripts/build_figures.py                          # all → manuscript/figures
    uv run --extra dev scripts/build_figures.py generator               # just one
    uv run --extra dev scripts/build_figures.py --out docs/assets/figures   # refresh docs copies
    uv run --extra dev scripts/build_figures.py --theme dark            # dark-console variant

Light is the default (white-page look for the manuscript PDF and the light-mode docs site);
pass ``--theme dark`` for the dark-console plates. Palettes live in scripts/_figtheme.py.
"""

import argparse
import csv
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import colorspacious as cs
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, to_rgb

import melanopy as mp
from melanopy.coeffs import LUM_W

from _figtheme import LIGHT, THEMES, apply_theme
from _perceptual import is_cvd_recoverable, is_pu

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manuscript" / "figures"
T = np.linspace(0, 1, 256)
CVD = [
    ("normal", None),
    ("deuteran", "deuteranomaly"),
    ("protan", "protanomaly"),
    ("tritan", "tritanomaly"),
]

# Palette globals — default light; main() rebinds them per --theme via apply_theme(). The
# figure functions below read these names directly; see scripts/_figtheme.py for the roles.
BG, PANEL, INK, INK2, HAIR = LIGHT["BG"], LIGHT["PANEL"], LIGHT["INK"], LIGHT["INK2"], LIGHT["HAIR"]
AMBER, TEAL, BLUE, GREY = LIGHT["AMBER"], LIGHT["TEAL"], LIGHT["BLUE"], LIGHT["GREY"]
RGB_COLS = list(LIGHT["RGB"])


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
    """sRGB ramp for a leaderboard label ('sodium (melanopy)' -> Circadia anchor, else builtin)."""
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
    axis = np.array([mp.rate_colormap(mp.circadia(a))["melanopic_ratio"] for a in alphas])
    sigma = np.array([mp.rate_colormap(mp.circadia(a))["mp_spread"] for a in alphas])

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
        s = mp.rate_colormap(mp.circadia(a))
        ax = fig.add_subplot(gsa[i])
        _strip(ax, mp.circadia(a), f"α={a:.2f}")
        ax.text(
            1.012,
            0.5,
            f"M/P {s['melanopic_ratio']:.2f}  ·  σ {s['mp_spread']:.2f}",
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

    # B: melanopic ratio + spread vs alpha
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
    axc.plot(alphas, sigma, color=TEAL, lw=2.0, ls="--", marker="s", ms=3, label="spread σ")
    axc.set_ylabel("spread σ", color=TEAL)
    axc.tick_params(axis="y", colors=TEAL)
    axc.set_ylim(0, max(0.2, sigma.max() * 1.4))
    for sp in (*axb.spines.values(), *axc.spines.values()):
        sp.set_color(HAIR)
    h1, l1 = axb.get_legend_handles_labels()
    h2, l2 = axc.get_legend_handles_labels()
    axb.legend(h1 + h2, l1 + l2, facecolor=PANEL, edgecolor=HAIR, fontsize=8.5, labelcolor=INK2)
    _title(
        axb,
        "Proof — melanopic ratio rises monotonically with α; spread σ low on the warm "
        "side, bounded at the cool end",
        size=10.5,
    )

    # C: per-position melanopic profiles
    axp = fig.add_subplot(gs[2])
    axp.set_facecolor(PANEL)
    for a, col in [(0.0, AMBER), (0.5, GREY), (1.0, BLUE)]:
        colors = mp.circadia(a)
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
    xenon = mp.circadia(1.0)
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


# ----------------------------------------------------------------------------- leaderboard table
# The leaderboard is a generated LaTeX scorecard (Table 1), not a figure: the manuscript
# preamble defines \cmap/\mprow/\mpruler/\pass/\fail, and this emits the per-row data plus the
# 17 ramp strips. The x-domain of \mprow/\mpruler in main.tex is 0..AXIS_DOMAIN_MAX; we assert
# no per-panel band exceeds it so the table can never silently clip.
AXIS_DOMAIN_MAX = 2.3
PANEL_COLS = ("representative", "led_lcd", "oled", "wide_gamut")


def _strip_png(colors, path):
    """Render a colormap ramp as a tight standalone PNG (one leaderboard \\cmap cell)."""
    fig, ax = plt.subplots(figsize=(2.0, 0.20))
    ax.imshow(np.clip(colors, 0, 1)[None, :, :], aspect="auto")
    ax.set_axis_off()
    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def _glyph(ok, marginal):
    """Pass/fail glyph macro call: filled \\pass / open \\fail, with a \\textsuperscript{*} flag."""
    return (r"\pass" if ok else r"\fail") + (r"\textsuperscript{*}" if marginal else "")


def fig_leaderboard_table(path):
    """Emit the merged leaderboard scorecard — 17 ramp strips + the row data ``leaderboard.tex``.

    Folds the old leaderboard point-plot and the inline prose table into one generated table:
    ramp strip, dot-and-band M/P axis cell, M/P mean, spread sigma, and the two universal
    requirements (PU / CVD-recoverable) as filled/open glyphs. Mean/sigma come from
    ``index/leaderboard.csv`` and the per-panel band from ``index/panel_robustness.csv`` (the
    scored-index single source of truth); PU and CVD reuse the §3 test criteria via
    :mod:`_perceptual`. Also writes ``leaderboard_note.tex`` (a caption footnote naming any
    map within 10% of a threshold) next to ``path``.
    """
    figdir = path.parent
    (figdir / "strips").mkdir(parents=True, exist_ok=True)
    lb = _read_csv("leaderboard.csv")
    bands = {r["colormap"]: r for r in _read_csv("panel_robustness.csv")}

    rows, notes, worst_hi = [], [], 0.0
    for r in sorted(lb, key=lambda r: float(r["melanopic_ratio"])):  # protective -> alerting
        label = r["colormap"]
        name = label.replace(" (melanopy)", "")
        colors = _colors_for(label)
        _strip_png(colors, figdir / "strips" / f"{name}.png")

        mean, sigma = float(r["melanopic_ratio"]), float(r["mp_spread"])
        vals = [float(bands[label][p]) for p in PANEL_COLS]
        lo, hi = min(vals), max(vals)
        worst_hi = max(worst_hi, hi)

        pu_ok, cov = is_pu(colors)
        cvd_ok, min_step = is_cvd_recoverable(colors)
        pu_m = 0.27 <= cov <= 0.33  # within 10% of the 0.30 PU threshold
        cvd_m = cvd_ok and 0.0 < min_step < 0.01  # passes, but a near-flat (nearly non-mono) step

        m = round(mean, 2)
        color = "prot" if m < 1.0 else "alert" if m > 1.0 else "neutral"
        disp = rf"\textbf{{{name}}}" if "(melanopy)" in label else name
        rows.append(
            rf"{disp} & \cmap{{strips/{name}}} & "
            rf"\mprow{{{mean:.2f}}}{{{lo:.2f}}}{{{hi:.2f}}}{{{color}}} & "
            rf"{mean:.2f} & {sigma:.2f} & {_glyph(pu_ok, pu_m)} & {_glyph(cvd_ok, cvd_m)} \\"
        )
        if pu_m:
            notes.append(rf"\texttt{{{name}}} (CAM02-UCS step CoV {cov:.2f}, PU threshold 0.30)")
        if cvd_m:
            notes.append(rf"\texttt{{{name}}} (smallest simulated lightness step {min_step:.3f})")

    if worst_hi > AXIS_DOMAIN_MAX + 1e-9:
        raise SystemExit(
            f"per-panel band hi {worst_hi:.3f} exceeds the axis domain {AXIS_DOMAIN_MAX}; "
            "bump the domain in main.tex (\\mprow/\\mpruler) and AXIS_DOMAIN_MAX"
        )

    # Wrap the rows in a macro rather than emitting bare `row \\` lines: \input'ing bare rows
    # straight into the tabular throws "Misplaced \noalign" at the file/alignment seam, so the
    # manuscript \input's this in the preamble (defining \leaderboardrows) and expands the macro
    # in the table body, which is in-stream and robust. Same for the marginal-cases footnote
    # (\input inside a \caption{} argument breaks brace scanning). LF endings to match the repo.
    rowsrc = r"\newcommand{\leaderboardrows}{%" + "\n" + "\n".join(rows) + "}\n"
    path.write_text(rowsrc, encoding="utf-8", newline="\n")
    body = ("Marginal (${}^{*}$): " + "; ".join(notes) + ".") if notes else ""
    (figdir / "leaderboard_note.tex").write_text(
        r"\newcommand{\leaderboardnote}{" + body + "}\n", encoding="utf-8", newline="\n"
    )
    print(f"  ({len(rows)} rows, {len(rows)} strips, {len(notes)} marginal)")


# ------------------------------------------------------------------- leaderboard point-plot (docs)
# The manuscript folds the leaderboard into Table 1 (fig_leaderboard_table above); this point-plot
# is retained for the docs site (docs/leaderboard.md), which renders a figure rather than a table.
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


# ----------------------------------------------------------------------------- melanopic colormaps
def _pairwise_min(colors):
    lab = cs.cspace_convert(np.clip(colors, 0, 1), "sRGB1", "CAM02-UCS")
    d = np.linalg.norm(lab[:, None, :] - lab[None, :, :], axis=-1)
    return d[d > 0].min()


def fig_melanopic_colormaps(path):
    sodium = mp.circadia(0.0)
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


# --------------------------------------------------------- per-position profiles (appendix)
# The un-summarized profile behind Table 1: rate_colormap(profile=True) gives, per ramp position,
# the melanopic ratio (NaN where the colour emits ~nothing) and the photopic luminance (the weight).
# Table 1's M/P mean is the luminance-weighted height of this curve; sigma is its spread.
def _spans(mask):
    """Yield ``(start, end)`` (end-exclusive) index spans where boolean ``mask`` is True."""
    idx = np.flatnonzero(mask)
    if not len(idx):
        return
    brk = np.flatnonzero(np.diff(idx) > 1)
    for s, e in zip(np.r_[idx[0], idx[brk + 1]], np.r_[idx[brk], idx[-1]] + 1):
        yield int(s), int(e)


def _mp_gray(ratios):
    """Per-position M/P -> [0,1] gray on the fixed global log2 scale (0.25->0, 1->0.5, 4->1).

    Log2 because the axis is multiplicative around the white point. NaN (no emission) stays NaN so
    the strip can hatch it rather than paint an extreme (and meaningless) gray.
    """
    return np.clip((np.log2(ratios) + 2.0) / 4.0, 0.0, 1.0)


def _profile_strip(ax, img, cmap):
    """One thin (1 x N) image strip, no ticks, hairline frame."""
    ax.imshow(img.reshape(1, -1), aspect="auto", cmap=cmap, vmin=0, vmax=1, extent=[0, 1, 0, 1])
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color(HAIR)
        sp.set_linewidth(0.4)


def _overview(ax, group, gi):
    """One overview panel: each map's M/P curve coloured by its colormap, faded by luminance."""
    ax.set_facecolor(PANEL)
    ax.set_yscale("log", base=2)
    ax.axhspan(0.22, 1.0, color=AMBER, alpha=0.06)  # protective band
    ax.axhspan(1.0, 4.4, color=BLUE, alpha=0.06)  # alerting band
    ax.axhline(1.0, color=INK2, lw=0.8, ls="--")
    for m in group:
        pos, mp_, lum = m["pos"], m["mp"], m["lum"]
        ax.plot(pos, mp_, color=INK2, lw=0.5, alpha=0.45, zorder=1)  # faint full-opacity raw curve
        pts = np.column_stack([pos, mp_])
        segs = np.stack([pts[:-1], pts[1:]], axis=1)
        rgba = ListedColormap(np.clip(m["colors"], 0, 1))(0.5 * (pos[:-1] + pos[1:]))
        rgba[:, 3] = np.clip(0.5 * (lum[:-1] + lum[1:]) / lum.max(), 0.0, 1.0)  # luminance opacity
        ok = ~np.isnan(segs).any(axis=(1, 2))  # NaN positions are gaps, not interpolated
        ax.add_collection(LineCollection(segs[ok], colors=rgba[ok], linewidths=1.6, zorder=2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0.22, 4.4)
    ax.set_yticks([0.25, 0.5, 1, 2, 4])
    ax.set_yticklabels(["0.25", "0.5", "1", "2", "4"])
    ax.set_xticks([0, 1])
    ax.tick_params(colors=INK2, labelsize=8)
    for sp in ax.spines.values():
        sp.set_color(HAIR)
    ax.set_title(f"M/P rank {6 * gi + 1}–{6 * gi + len(group)}", color=INK2, fontsize=9, loc="left")
    if gi == 0:
        ax.set_ylabel("melanopic ratio  (log$_2$, white = 1)", color=INK2, fontsize=9)


def fig_profiles(path):
    lb = _read_csv("leaderboard.csv")  # ascending M/P (same order as Table 1)
    maps = []
    for r in lb:
        colors = _colors_for(r["colormap"])
        p = mp.rate_colormap(colors, profile=True)
        maps.append(
            {
                "name": r["colormap"].replace(" (melanopy)", ""),
                "colors": colors,
                "pos": p["positions"],
                "mp": p["ratios"],
                "lum": p["luminance"],
                "mean": float(r["melanopic_ratio"]),
                "sigma": float(r["mp_spread"]),
            }
        )

    gray = plt.cm.gray.copy()
    gray.set_bad("white")  # NaN cells render white, then get hatched
    _theme()
    fig = plt.figure(figsize=(11, 11), facecolor=BG)
    outer = fig.add_gridspec(
        2, 1, height_ratios=[1.0, 3.0], hspace=0.22, left=0.06, right=0.97, top=0.91, bottom=0.03
    )
    fig.text(
        0.06,
        0.965,
        "Per-position melanopic profiles — the curve Table 1 summarizes "
        "(M/P mean = luminance-weighted height, $\\sigma$ = spread)",
        color=INK,
        fontsize=12,
    )
    fig.text(
        0.06,
        0.945,
        "Overview lines coloured by their colormap, opacity $\\propto$ per-position luminance "
        "(faint = low emission; thin grey curve = true unweighted height)",
        color=INK2,
        fontsize=9,
    )

    # overview line panels (3 groups of ~6 maps by M/P rank, shared log2 y-axis)
    ov = outer[0].subgridspec(1, 3, wspace=0.16)
    for gi, group in enumerate((maps[0:6], maps[6:12], maps[12:17])):
        _overview(fig.add_subplot(ov[gi]), group, gi)

    # per-map triplets: 2 columns x 9 rows (slot 18 holds the M/P scale bar)
    grid = outer[1].subgridspec(9, 2, hspace=1.05, wspace=0.10)
    for i, m in enumerate(maps):
        cell = grid[i % 9, i // 9].subgridspec(3, 1, hspace=0.0)
        n = len(m["pos"])
        axc = fig.add_subplot(cell[0])
        _profile_strip(axc, np.linspace(0, 1, n), ListedColormap(np.clip(m["colors"], 0, 1)))
        axc.set_title(
            f"{m['name']}   M/P {m['mean']:.2f} · $\\sigma$ {m['sigma']:.2f}",
            color=INK,
            fontsize=8.5,
            loc="left",
            pad=2,
        )
        axm = fig.add_subplot(cell[1])
        g = _mp_gray(m["mp"])
        _profile_strip(axm, np.ma.masked_invalid(g), gray)
        for s, e in _spans(np.isnan(g)):  # near-black / NaN: hatch, never an extreme gray
            axm.add_patch(
                plt.Rectangle(
                    (s / n, 0),
                    (e - s) / n,
                    1,
                    facecolor="none",
                    hatch="////",
                    edgecolor="0.55",
                    lw=0,
                )
            )
        axe = fig.add_subplot(cell[2])
        _profile_strip(
            axe, m["lum"] / (m["lum"].max() or 1.0), gray
        )  # emission, per-map normalized
        if i // 9 == 0:
            for ax_, lab in ((axc, "colour"), (axm, "M/P"), (axe, "emit")):
                ax_.set_ylabel(
                    lab, color=INK2, fontsize=6.5, rotation=0, ha="right", va="center", labelpad=9
                )

    # shared M/P grayscale scale bar in the empty 18th slot
    sb = fig.add_subplot(grid[8, 1].subgridspec(3, 1, hspace=0.0)[1])
    sb.imshow(
        np.linspace(0, 1, 256).reshape(1, -1),
        aspect="auto",
        cmap=gray,
        vmin=0,
        vmax=1,
        extent=[0, 1, 0, 1],
    )
    sb.set_yticks([])
    sb.set_xticks([0, 0.5, 1])
    sb.set_xticklabels(["0.25", "1.0", "4.0"], fontsize=7, color=INK2)
    sb.tick_params(colors=INK2, length=2)
    for sp in sb.spines.values():
        sp.set_color(HAIR)
        sp.set_linewidth(0.4)
    sb.set_title("M/P gray scale (global log$_2$)", color=INK2, fontsize=7.5, loc="left", pad=2)
    sb.text(
        0.0,
        -1.6,
        "hatched = near-black (no emission); emit strip normalized per map",
        transform=sb.transAxes,
        color=INK2,
        fontsize=7,
    )

    fig.savefig(path, dpi=160, facecolor=BG)
    fig.savefig(path.with_suffix(".pdf"), facecolor=BG)
    plt.close(fig)


FIGURES = {
    "generator": (fig_generator, "circadian_generator.png"),
    "leaderboard_table": (fig_leaderboard_table, "leaderboard.tex"),  # manuscript Table 1
    "leaderboard": (fig_leaderboard, "melanopic_leaderboard.png"),  # docs point-plot
    "profiles": (fig_profiles, "fig_melanopic_profiles.png"),  # appendix A
    "validation": (fig_validation, "s026_validation.png"),
    "melanopic_colormaps": (fig_melanopic_colormaps, "melanopic_colormaps.png"),
}


def main():
    ap = argparse.ArgumentParser(description="Regenerate the paper/docs figures.")
    ap.add_argument(
        "names",
        nargs="*",
        metavar="FIGURE",
        help=f"subset to build (default: all) — any of: {', '.join(FIGURES)}",
    )
    ap.add_argument(
        "--theme",
        choices=list(THEMES),
        default=None,
        help="palette (default: light, or $MELANOPY_FIG_THEME)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=OUT,
        help="output directory (default: manuscript/figures)",
    )
    args = ap.parse_args()
    unknown = [n for n in args.names if n not in FIGURES]
    if unknown:
        ap.error(f"unknown figure(s) {', '.join(unknown)}; choose from {', '.join(FIGURES)}")
    theme = apply_theme(globals(), args.theme)
    args.out.mkdir(parents=True, exist_ok=True)
    for key in args.names or list(FIGURES):
        func, filename = FIGURES[key]
        func(args.out / filename)
        print(f"wrote {args.out / filename}  [{theme}]")


if __name__ == "__main__":
    main()

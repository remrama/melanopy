# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Melanopy adds a third evaluation axis to scientific colormaps alongside perceptual
uniformity and colour-vision-deficiency (CVD) safety: **melanopic (circadian) content** —
how much short-wavelength, melatonin-suppressing light a map emits. It *measures* the axis,
*scores* existing colormaps on it, and *generates* a one-parameter family that walks the
axis while holding uniformity and CVD-safety fixed. It rates a colour's chromaticity, not
light dose (see README for the honest-scope caveat).

## Commands

Use `uv` for everything (per global instruction; the repo is uv-locked). The runtime
package needs no extras; all tooling lives in the `dev` optional-dependency group, so
prefix tool commands with `--extra dev`.

```bash
uv run --extra dev pytest -q                                   # run tests
uv run --extra dev pytest tests/test_sanity.py::test_gray_is_neutral   # single test
uv run --extra dev ruff check        # lint  (add --fix to autofix)
uv run --extra dev ruff format       # format
uv run --extra dev mypy              # type-check (files = src/ only)
uv run --extra dev pre-commit run --all-files   # ruff-check, ruff-format, mypy
uv run examples/rate_a_map.py        # run an example (no dev extra needed)
```

`qt` is a separate extra (`uv run --extra qt ...`) needed only for the pyqtgraph adapter.

## Architecture

The package's organizing insight: **the melanopic content of a display colour collapses
into three per-primary coefficients** (the melanopic/photopic ratio of each RGB primary).
Everything else is built around producing, storing, and consuming those three numbers.

The dependency flow is a one-way pipeline — understand this before editing:

1. **`spectra.py` (offline, optional)** — reads the CIE S 026 melanopic action spectrum and
   CIE 1931 V(λ) from `src/melanopy/data/` and, via `coefficients_from_primaries()`, derives
   the three coefficients from measured primary SPDs. This is a *generation-time* tool, not a
   runtime path. **It is deliberately NOT imported by `__init__.py`, and `import
   melanopy.spectra` currently raises `FileNotFoundError`** because the vendored CIE `data/`
   files are not committed (provenance/licensing pending — see the module docstring's NOTICE.md
   reference). The rest of the package works fine without them.
2. **`coeffs.py` (runtime source of truth)** — holds the three coefficients hand-baked into
   `PANELS["representative"]`, plus sRGB luminance weights `LUM_W`. Add a measured monitor as a
   new `PANELS` entry; `panel=` threads through the public API to select it.
3. **`rater.py`** — consumes `coeffs.py`. `melanopic_ratio(rgb)` normalizes so display
   white = 1.0 (<1 protective/warm, >1 alerting/cool). `rate_colormap(colors)` returns two
   distinct metrics: `melanopic_ratio` (*where* the map sits on the axis, luminance-weighted
   mean) and `purity_sigma` (*how tightly* it sits — luminance-weighted spread; a map can be
   protective on average yet smeared). sRGB is linearized before weighting.
4. **`generator.py`** — the "Diel family". Independent of `coeffs.py`: it is pure OKLab
   geometry. One shared monotonic lightness profile (`_L` over `_POS`) is used for every
   `alpha`, so perceptual uniformity and CVD-safety hold *by construction*; `alpha` in [0, 1]
   morphs only the chroma vector (warm `_WARM` → cool `_COOL`). `_clamp()` reduces chroma to
   stay in sRGB gamut while preserving L and hue. The melanopic ratio is therefore an
   *emergent, monotonic* property of alpha, not something the generator computes — that
   monotonicity is asserted in the tests via the rater. Anchors: `EMBER` (0.0, protective),
   `EQUINOX` (0.55, ~neutral M/P≈1), `GLACIER` (1.0, alerting).

`categorical.py` is separate from the continuous axis: a fixed CVD-safe categorical palette
(dark/light variants), justified by an area-weighted argument that small marks emit
negligible light, so one palette serves every circadian regime.

**Adapters** (`src/melanopy/adapters/`) keep third-party integration out of core:
`mpl.register()` registers ember/glacier/equinox as named matplotlib colormaps;
`pyqtgraph.py` (optional, `qt` extra) exports to a pyqtgraph `ColorMap` for live LUT sliders
in the SMACC Qt reference app.

## Conventions

- Style is intentionally terse: short helpers, single-letter math locals, vectorized numpy.
  Match it. Ruff enforces line-length 100, numpy docstring convention, and McCabe
  complexity ≤ 10 (`select = E, F, I, W, C90, UP, NPY201`).
- Color math is explicit and dependency-light (sRGB↔linear and OKLab↔linear transforms are
  inlined, not pulled from a color library). Keep new color math in the same style rather
  than adding heavy dependencies — base runtime deps are only numpy + matplotlib.
- Public API is curated in `__init__.py`'s `__all__`; export new public symbols there.

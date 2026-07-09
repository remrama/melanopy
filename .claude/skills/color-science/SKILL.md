---
name: color-science
description: >-
  Reference for melanopy's colour- and vision-science internals — the inlined sRGB↔linear and
  OKLab↔linear transforms, the three per-primary melanopic coefficients and the white-normalised
  M/P pipeline, the Circadia family's invariants (display white = 1.0, one shared monotone OKLab
  lightness), and the CAM02-UCS + Machado-CVD recipes that verify perceptual uniformity and CVD
  order-recoverability. Use when editing rater.py, generator.py, coeffs.py, spectra.py or
  accent.py, adding a display panel or colormap, or auditing a PU / CVD / melanopic claim.
---

# Melanopy colour & vision science

Working notes for changing anything that touches colour. The package keeps its colour maths
**inlined, dependency-light, and vectorised** (numpy only at runtime; no `colour`/`colorspacious`
in the runtime path). Match that style — do not pull in a colour library for core code.

## Where the maths lives

| file           | responsibility                                                                  |
| -------------- | ------------------------------------------------------------------------------- |
| `rater.py`     | sRGB→linear, the three-coefficient melanopic pipeline, the two metrics          |
| `generator.py` | OKLab↔linear, gamut clamp, the shared lightness profile, the Circadia family    |
| `coeffs.py`    | `PANELS` (per-primary M/P coefficients), `LUM_W`, `get_coeffs(panel)`           |
| `spectra.py`   | **offline only** — derives coefficients from primary SPDs + CIE S 026 data      |
| `accent.py`    | `CIRCADIA_ACCENT` — vivid marks for drawing over a Circadia fill (CVD-distinct) |

`spectra.py` reads the vendored CIE tables (`src/melanopy/data/`, CC BY-SA 4.0) and is *not*
imported by `__init__.py`; it is a generation-time tool. The runtime never reads `data/`.

## The transforms (exact, as inlined)

**sRGB ↔ linear** (standard sRGB EOTF; note the two different thresholds):

```python
# sRGB → linear  (rater.py: _to_linear)
lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
# linear → sRGB  (generator.py: _lin2srgb)
srgb = np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
```

**OKLab ↔ linear sRGB** (Björn Ottosson; matrices `_M1`, `_M2` in `generator.py`). The cube /
cube-root sits *between* the two matrices:

```python
# linear → OKLab:  lab = (lin @ M1.T) ** (1/3) @ M2.T
# OKLab → linear:  lin = (lab @ M2i.T) ** 3   @ M1i.T   # _oklab2lin
```

The generator builds in OKLab (perceptual L, plus an (a, b) chroma vector), then `_clamp(L, a, b)`
**reduces chroma while preserving L and hue** until the colour is in sRGB gamut. Never clip RGB
directly — that shifts hue and breaks the uniformity/CVD guarantees.

## The melanopic pipeline (three numbers carry everything)

`melanopic_ratio(rgb, panel)` — normalised so **display white = 1.0**:

```python
W   = [LUM_W.R, LUM_W.G, LUM_W.B]            # sRGB luminance weights
c   = get_coeffs(panel)                       # per-primary melanopic/photopic, {R,G,B}
lin = srgb_to_linear(rgb)
Yc  = lin * W                                 # per-channel luminance contributions
Y   = Yc.sum(-1)                              # photopic luminance
M   = (Yc * [c.R, c.G, c.B]).sum(-1)          # melanopic
ratio = (M / Y) / (W @ [c.R, c.G, c.B])       # divide by white's M/P → white maps to 1.0
```

`rate_colormap` returns two **distinct** metrics — keep them distinct:

- `melanopic_ratio` — the **M/P mean**, *where* the map sits: luminance-weighted **mean** position
    (white = 1).
- `mp_spread` — the **M/P spread (σ)**, *how tightly* it sits: luminance-weighted **spread** of the
    per-pixel ratio (a tight spread reads as a "pure" ramp — keep that handle in prose only, never
    as a metric name).

Both are luminance-weighted and **ignore near-black pixels** (`Y > 0.01 * Y.max()`); a dark end
that dumps blue still shows up in `range`, not in the mean. sRGB must be linearised *before*
weighting. Pass `profile=True` to also get the per-position `positions`/`ratios`/`luminance` arrays
that back the per-data-position profile claim.

## Invariants — assert these after any change

- **Display white → 1.0** and **neutral grey → 1.0** (by construction; see `tests/test_sanity.py`).
- **One shared monotone OKLab lightness** `_L` over `_POS` for *every* `alpha` — this is what makes
    the maps perceptually uniform and CVD order-recoverable. `alpha` morphs only the chroma vector
    (`_WARM` → `_COOL`); it must **not** touch `_L`.
- **Melanopic ratio is emergent and monotonic in `alpha`** — the generator never computes it; the
    rater measures it. Assert monotonicity via the rater, don't hard-code numbers.
- **Coefficients are locked to the SPD models** by `tests/test_coeffs.py`; regenerate with
    `scripts/build_panels.py`, never hand-edit `PANELS` to "fix" a number.

## Verification recipes (the real checks)

These run in an **independent** perceptual space (CAM02-UCS via `colorspacious`, the `dev` extra),
so they are *not* circular with the OKLab construction. This is the whole point — verify in a
different space than you built in. Canonical source: `tests/test_perceptual.py`.

**Perceptual uniformity** — lightness monotone, steps near-uniform:

```python
import colorspacious as cs, numpy as np
ucs = cs.cspace_convert(np.clip(rgb, 0, 1), "sRGB1", "CAM02-UCS")  # (N,3): J', a', b'
steps = np.linalg.norm(np.diff(ucs, axis=0), axis=1)
assert np.all(np.diff(ucs[:, 0]) > 0)          # J' strictly increasing
assert steps.std() / steps.mean() < 0.30       # CoV (~0.16–0.26 in practice)
```

**CVD order-recoverability** — Machado (2009), full severity, ordering survives:

```python
for cvd in ("deuteranomaly", "protanomaly", "tritanomaly"):
    space = {"name": "sRGB1+CVD", "cvd_type": cvd, "severity": 100}
    sim = cs.cspace_convert(np.clip(rgb, 0, 1), space, "sRGB1")
    J = cs.cspace_convert(np.clip(sim, 0, 1), "sRGB1", "CAM02-UCS")[:, 0]
    assert np.all(np.diff(J) > 0)               # data order still readable
```

Say exactly what the tests show: the sequential maps are **CVD order-recoverable** (lightness
carries the order), not the stronger "CVD-safe". `circadia_diverging` distinguishes its arms by
**hue**, so it is **not** order-recoverable — use the sequential maps where CVD matters.

## Honest scope

Melanopy rates a colour's **chromaticity**, not light **dose**. Real circadian load also depends on
brightness, screen fill, viewing distance, and ambient light. Keep claims calibrated — the value is
measurability, a scored index, and a uniformity-preserving generator, not a physiological promise.

## Before committing a colour change

1. `uv run --extra dev pytest -q` — especially `test_perceptual`, `test_sanity`, `test_coeffs`.
2. If you touched coefficients/panels: `uv run scripts/build_panels.py` and check
    `build_panel_robustness.py` (ranking must stay stable, Spearman ρ ≥ 0.99).
3. If you touched the family or rater: regenerate `scripts/build_figures.py` +
    `scripts/build_leaderboard.py` so the docs/manuscript figures match the code.

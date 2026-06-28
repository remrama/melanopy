# API reference

The public API is curated in `melanopy.__all__`. Everything below is importable directly from
the top-level package, e.g. `import melanopy as mp; mp.rate_colormap(...)`.

## Rating

::: melanopy.rate_colormap

::: melanopy.melanopic_ratio

## Generator

::: melanopy.circadia

`circadian_cmap` is an alias of `circadia`.

::: melanopy.circadia_sweep

::: melanopy.circadia_diverging

The named anchors **`SODIUM`** (`alpha=0.0`), **`EQUILUX`** (`alpha=0.55`, the M/P = 1
crossover), and **`XENON`** (`alpha=1.0`) are exported as ready-made
`matplotlib.colors.ListedColormap` objects. See [The Circadia family](circadia.md).

`circadia` sets a geometric position on the axis; **`circadia_rating(alpha, panel=...)`** reports
the *physical* melanopic ratio that position yields on a given panel — the one call a labelled live
slider needs (see the [Cookbook](cookbook.md)).

::: melanopy.circadia_rating

## matplotlib integration

::: melanopy.register

## Categorical palette

The CVD-safe categorical palette is exposed as `CATEGORICAL` (with `CATEGORICAL_DARK`,
`CATEGORICAL_LIGHT`, and `CATEGORICAL_NAMES`). One palette serves every circadian regime — see
[the area-weighted argument](axis.md#the-area-weighted-melanopic-budget).

## Advanced — adding a measured panel

The built-in panels (`representative`, `led_lcd`, `oled`, `wide_gamut`) are spectral *archetypes*,
not measurements. For research-grade work where the *absolute* melanopic level matters — a sleep
lab, a chronobiology study — derive the coefficients from the deployment monitor's own measured
primary SPDs and register them as a new panel.

**Without a measured panel, a reported M/P is indicative, not metrological:** it reflects a
representative archetype, not your hardware. The protective ↔ alerting *ranking* is stable across
panels (Spearman ρ ≥ 0.99), so relative comparisons hold on any panel — only the *absolute* M/P
needs a measured one.

Measure the three primary SPDs (R, G, B at full drive) on the package's 1 nm grid
(`melanopy.spectra.WL`, 380–780 nm) with a spectroradiometer, then derive the three coefficients:

```python
from melanopy.spectra import coefficients_from_primaries

coeffs = coefficients_from_primaries({"R": spd_r, "G": spd_g, "B": spd_b})
# -> {"R": ..., "G": ..., "B": ...}
```

Add the result to `melanopy.coeffs.PANELS` as a new keyed row (e.g. `"lab_monitor": {...}`) and
select it everywhere via `panel="lab_monitor"` — the argument threads through `rate_colormap`,
`melanopic_ratio`, and `circadia_rating`.

For a panel you intend to keep, also wire the SPDs into the model layer so the test-suite locks the
baked numbers against drift:

1. Add a branch returning the SPDs to `melanopy.spectra.panel_primaries`, and its name to
    `melanopy.spectra.PANEL_KINDS`.
2. Regenerate with `uv run scripts/build_panels.py` and paste the printed rows into
    `melanopy.coeffs.PANELS`.
3. `tests/test_coeffs.py` then asserts every `PANELS` row still equals
    `coefficients_from_primaries(panel_primaries(kind))`, so a later edit can't silently diverge.

For the one-call derivation itself:

::: melanopy.spectra.coefficients_from_primaries

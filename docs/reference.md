# API reference

The public API is curated in `melanopy.__all__`. Everything below is importable directly from the
top-level package, e.g. `import melanopy as mp; mp.rate_colormap(...)`.

## Rating

::: melanopy.rate_colormap

::: melanopy.melanopic_ratio

::: melanopy.circadia_rating

## Generator — the Circadia family

::: melanopy.circadia

`circadian_cmap` is an alias of `circadia`.

::: melanopy.circadia_sweep

::: melanopy.circadia_diverging

The named anchors **`SODIUM`** (`alpha=0.0`), **`EQUILUX`** (`alpha=0.55`, the M/P = 1 crossover),
and **`XENON`** (`alpha=1.0`) are exported as ready-made `matplotlib.colors.ListedColormap` objects.

## matplotlib integration

::: melanopy.register

## Qualitative palettes

The CVD-safe qualitative palette is exposed as `QUALITATIVE` (a `ListedColormap`), with the raw hex
lists `QUALITATIVE_DARK` / `QUALITATIVE_LIGHT` and `QUALITATIVE_NAMES`. It is **circadian-neutral by
design**: small qualitative marks emit negligible light regardless of colour (the area-weighted
budget), so this palette is optimised for category separability under colour-vision deficiency, not
for melanopic content — its swatches straddle the axis, and the melanopic ratio is reported, never
tuned. One palette therefore serves every circadian regime.

```python
>>> import melanopy as mp
>>> mp.QUALITATIVE_NAMES
['amber', 'sky', 'teal', 'yellow', 'blue', 'vermillion', 'rose']
>>> mp.QUALITATIVE_DARK[:3]
['#F2A036', '#81CAF0', '#009C89']
```

## Adding a measured panel

The built-in panels (`representative`, `led_lcd`, `oled`, `wide_gamut`) are spectral *archetypes*,
not measurements — so a reported M/P is indicative, not metrological. The protective ↔ alerting
*ranking* is stable across panels (Spearman ρ ≥ 0.99), so relative comparisons hold on any panel;
only the *absolute* M/P needs a measured one.

For research-grade work, measure the three primary SPDs (R, G, B at full drive) on the package's
1 nm grid (`melanopy.spectra.WL`, 380–780 nm) and derive the coefficients:

```python
>>> from melanopy.spectra import coefficients_from_primaries
>>> coeffs = coefficients_from_primaries({"R": spd_r, "G": spd_g, "B": spd_b})  # doctest: +SKIP
```

Add the result to `melanopy.coeffs.PANELS` as a new keyed row (e.g. `"lab_monitor": {...}`); the
`panel="lab_monitor"` argument then threads through `rate_colormap`, `melanopic_ratio`, and
`circadia_rating`.

::: melanopy.spectra.coefficients_from_primaries

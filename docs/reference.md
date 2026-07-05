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

## Categorical palette

The CVD-safe categorical palette is exposed as `CATEGORICAL` (a `ListedColormap`), with the raw hex
lists `CATEGORICAL_DARK` / `CATEGORICAL_LIGHT` and `CATEGORICAL_NAMES`. One palette serves every
circadian regime: small categorical marks emit negligible light.

```python
>>> import melanopy as mp
>>> mp.CATEGORICAL_NAMES
['amber', 'sky', 'teal', 'yellow', 'blue', 'vermillion', 'rose']
>>> mp.CATEGORICAL_DARK[:3]
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

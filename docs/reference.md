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

## Accent palette

`CIRCADIA_ACCENT` (with `CIRCADIA_ACCENT_NAMES`) is a small set of vivid colours for qualitative
marks — ticks, points, event lines — drawn *over* a Circadia colormap fill, where ordinary
qualitative colours can be lost against the fill or clash with it. They are chosen to sit outside the
family's colour footprint across the whole axis (so they contrast with warm *and* cool fills) and to
stay mutually distinct under colour-vision deficiency — which confines them to the
magenta/violet/green arc. Vivid by design.

```python
>>> import melanopy as mp
>>> mp.CIRCADIA_ACCENT_NAMES
['orchid', 'grape', 'emerald', 'lime']
```

For qualitative marks that are *not* over a fill, the melanopic axis does not apply (small marks emit
negligibly) — any CVD-safe qualitative palette (e.g. ColorBrewer, Okabe–Ito) serves.

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

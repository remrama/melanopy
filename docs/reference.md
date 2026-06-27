# API reference

The public API is curated in `melanopy.__all__`. Everything below is importable directly from
the top-level package, e.g. `import melanopy as mp; mp.rate_colormap(...)`.

## Rating

::: melanopy.rate_colormap

::: melanopy.melanopic_ratio

## Generator

::: melanopy.diel

`circadian_cmap` is an alias of `diel`.

::: melanopy.diel_sweep

::: melanopy.diel_diverging

The named anchors **`SODIUM`** (`alpha=0.0`), **`EQUILUX`** (`alpha=0.55`, the M/P = 1
crossover), and **`XENON`** (`alpha=1.0`) are exported as ready-made
`matplotlib.colors.ListedColormap` objects. See [The Diel family](generator.md).

## matplotlib integration

::: melanopy.register

## Categorical palette

The CVD-safe categorical palette is exposed as `CATEGORICAL` (with `CATEGORICAL_DARK`,
`CATEGORICAL_LIGHT`, and `CATEGORICAL_NAMES`). One palette serves every circadian regime — see
[the area-weighted argument](axis.md#the-area-weighted-melanopic-budget).

## Advanced — deriving panel coefficients

For exact numbers on a specific monitor, derive the three per-primary coefficients from its
measured primary SPDs. This lives in `melanopy.spectra`, a generation-time tool that is *not*
imported by the runtime package:

::: melanopy.spectra.coefficients_from_primaries

# API reference

The public API is curated in `melanopy.__all__`. Everything below is importable directly from the
top-level package, e.g. `import melanopy as mp; mp.rate_colormap(...)`.

```python exec="true" session="mpl"
# Docs setup (hidden): render matplotlib figures inline by making plt.show() emit an SVG.
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _render_svg(*args, **kwargs):
    from io import StringIO

    for num in plt.get_fignums():
        buffer = StringIO()
        plt.figure(num).savefig(buffer, format="svg", bbox_inches="tight")
        print(buffer.getvalue())
    plt.close("all")


plt.show = _render_svg
```

## Rating

::: melanopy.rate_colormap

::: melanopy.melanopic_ratio

::: melanopy.circadia_rating

## Generator — the Circadia family

The `circadia(alpha)` family walks from protective (warm) to alerting (cool) while holding lightness
and CVD-recoverability fixed. Each member is a drop-in matplotlib colormap:

```python exec="true" source="above" html="true" session="mpl"
import matplotlib.pyplot as plt
import numpy as np

import melanopy as mp

grad = np.linspace(0, 1, 256).reshape(1, -1)
fig, axes = plt.subplots(5, 1, figsize=(7, 3))
for ax, alpha in zip(axes, [0.0, 0.25, 0.55, 0.75, 1.0]):
    ax.imshow(grad, aspect="auto", cmap=mp.circadia(alpha, as_cmap=True))
    ax.set_ylabel(f"α = {alpha}", rotation=0, ha="right", va="center")
    ax.set_xticks([])
    ax.set_yticks([])
plt.show()
```

::: melanopy.circadia

`circadian_cmap` is an alias of `circadia`.

::: melanopy.circadia_sweep

::: melanopy.circadia_diverging

`circadia_sweep` walks the whole axis along one ramp (a teaching map whose melanopic ratio rises
~linearly with the data value); `circadia_diverging` is a warm↔cool diverging map, neutral at the
zero crossing:

```python exec="true" source="above" html="true" session="mpl"
import matplotlib.pyplot as plt
import numpy as np

import melanopy as mp

grad = np.linspace(0, 1, 256).reshape(1, -1)
maps = [("circadia_sweep", mp.circadia_sweep(as_cmap=True)),
        ("circadia_diverging", mp.circadia_diverging(as_cmap=True))]
fig, axes = plt.subplots(2, 1, figsize=(7, 1.2))
for ax, (name, cmap) in zip(axes, maps):
    ax.imshow(grad, aspect="auto", cmap=cmap)
    ax.set_title(name, loc="left", fontsize=9)
    ax.set_axis_off()
plt.show()
```

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

```python exec="true" source="above" html="true" session="mpl"
import matplotlib.pyplot as plt

import melanopy as mp

fig, ax = plt.subplots(figsize=(7, 1.2))
for i, (color, name) in enumerate(zip(mp.CIRCADIA_ACCENT, mp.CIRCADIA_ACCENT_NAMES)):
    ax.add_patch(plt.Rectangle((i, 0), 0.9, 1, color=color))
    ax.text(i + 0.45, -0.12, name, ha="center", va="top")
ax.set(xlim=(0, 4), ylim=(0, 1))
ax.set_axis_off()
plt.show()
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

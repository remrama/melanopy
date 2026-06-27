# Rating colormaps

The rater turns a colormap into numbers on the melanopic axis. The whole pipeline collapses
display dependence into **three per-primary coefficients**, which is what makes it fast and
swappable across displays.

## The pipeline

For each colour in the map:

```text
sRGB → linearize → displayed SPD = r·P_R + g·P_G + b·P_B
                 → photopic luminance  Y   (exact sRGB weights)
                 → melanopic           M   (∫ SPD · s_mel,  CIE S 026)
                 → M/P, normalized so display white = 1
```

Because the primaries are fixed for a given display, the melanopic content of a colour is just
a weighted sum of three numbers — the **melanopic/photopic ratio of each RGB primary**. For
the representative panel those coefficients are:

| primary | coefficient (M/P) |
| ------- | ----------------- |
| R       | 0.0031            |
| G       | 0.6555            |
| B       | 10.9681           |

The blue primary does almost all of the melanopic work — which is exactly why the axis is
mostly a warm ↔ cool story.

## The two metrics

`rate_colormap` returns two *distinct* numbers (plus the raw per-position `range`):

```python
import matplotlib.pyplot as plt
import numpy as np
import melanopy as mp

c = plt.get_cmap("viridis")(np.linspace(0, 1, 256))[:, :3]
mp.rate_colormap(c)
# {'melanopic_ratio': 0.834, 'purity_sigma': 0.556, 'range': (0.395, 3.069)}
```

| metric                                    | meaning                                                                                                       |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **melanopic ratio (M/P)**                 | *where* the map sits — luminance-weighted mean position (white = 1). **< 1 protective**, **> 1 alerting**.    |
| **circadian purity (σ)** — `purity_sigma` | *how tightly* it sits — luminance-weighted spread of the per-position ratio. **Lower = more circadian-pure.** |

The two are independent. viridis sits mid-axis (0.83 — mildly protective on average) yet has a
**high σ (0.56)**: it dumps high-melanopic blue at its dark end, so it is *smeared*, not pure.
A single mean would hide that; σ surfaces it. Both metrics are luminance-weighted, so near-black
pixels that emit almost nothing don't dominate the score.

To score a single colour rather than a whole map, use `melanopic_ratio`:

```python
mp.melanopic_ratio([1.0, 1.0, 1.0])   # display white -> array([1.0])
mp.melanopic_ratio([1.0, 0.4, 0.0])   # a warm orange  -> < 1
```

## Display panels

Melanopic content depends on the display's primary spectra, which sRGB does **not** fix. So
both functions take a `panel=` argument selecting among representative archetypes:

| panel                        | display type             |
| ---------------------------- | ------------------------ |
| `representative` *(default)* | narrowband RGB           |
| `led_lcd`                    | blue-pump white-LED LCD  |
| `oled`                       | OLED                     |
| `wide_gamut`                 | quantum-dot / wide-gamut |

Absolute M/P shifts with the panel (the blue coefficient ranges ≈ 8.8 to ≈ 13.7), but the
**ranking is robust** — see [The scored index](leaderboard.md) for the rank-stability result.
For exact numbers on a specific monitor, plug its measured primary SPDs into
`melanopy.spectra.coefficients_from_primaries` (see the [API reference](reference.md)).

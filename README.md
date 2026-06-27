# Melanopy — a melanopic axis for colormaps

Scientific colormaps are usually judged on two axes: **perceptual uniformity** and
**colour-vision-deficiency (CVD) safety**. Melanopy adds a third: how much
short-wavelength, **melanopic** (melatonin-suppressing) light a map emits — makes it
*measurable*, scores existing colormaps on it, and provides a one-parameter family that
walks the axis while holding uniformity and CVD-safety fixed.

For people who read screens as their main light source at night (e.g., sleep labs,
observatories, NICU, night radiology, control rooms) large data-fills (e.g., spectrograms,
density maps) actually emit light, and their colour content can cooperate with, or fight,
a chosen circadian lighting strategy.

> This rates a colour's *chromaticity*, not light *dose*. Real circadian
> load also depends on screen brightness, screen fill, viewing distance, and ambient light.
> If you genuinely need to stay alert, the dominant lever is room lighting. The value
> here is measurability, a scored index, a uniformity-preserving generator, and surfacing
> the axis. The physiological effect of a colormap alone is second-order.

📖 **Documentation:** <https://remrama.github.io/melanopy/>

## Quickstart

```python
import matplotlib.pyplot as plt
import numpy as np

import melanopy as mp

# Score any colormap on the melanopic axis  (display white = 1.0)
c = plt.get_cmap("viridis")(np.linspace(0, 1, 256))[:, :3]
print(mp.rate_colormap(c))
# {'melanopic_ratio': ~0.83, 'purity_sigma': ..., 'range': (...)}

# Use the named endpoints (registered with matplotlib)
mp.register()
plt.imshow(Z, cmap="sodium")    # protective: warm, low-melanopic
plt.imshow(Z, cmap="xenon")     # alerting:   cool, high-melanopic
plt.imshow(Z, cmap="equilux")   # circadian-neutral (M/P ~ 1)

# Dial the whole axis: alpha 0 (protective) .. 1 (alerting)
cmap = mp.diel(0.3, as_cmap=True)

# Or walk the whole axis in one map, or diverge for signed data
seq = mp.diel_sweep()        # protective -> alerting; melanopic ratio ~linear in the data
div = mp.diel_diverging()    # signed: warm protective <- neutral -> cool alerting
```

`melanopic_ratio` < 1 → protective (warm); > 1 → alerting (cool/blue).

## The two metrics

- **melanopic ratio (M/P)** - *where* a map sits on the axis (white = 1).
- **circadian purity (σ)** - *how tightly* it sits (luminance-weighted spread; lower =
    more circadian-pure). A map can be mildly protective on average yet *smeared* (e.g.
    viridis dumps blue at its dark end); the two numbers tell that apart.

## Display panels

Melanopic content depends on the display's primary spectra, which sRGB doesn't fix — so the
rater takes a `panel=` argument selecting among representative archetypes (`representative`
narrowband, `led_lcd` blue-pump white-LED, `oled`, `wide_gamut` quantum-dot). Absolute M/P
shifts with the panel (the blue coefficient ranges ≈8.8 to ≈13.7), but the **ranking is
robust**: Spearman ρ ≥ 0.99 across panels, and display white stays exactly 1.0 (see
[`index/`](index/README.md)). For exact numbers on a specific monitor, plug its measured
primary SPDs into `melanopy.spectra.coefficients_from_primaries`.

## Licensing

Melanopy's code is MIT-licensed. The spectral reference tables bundled in
`src/melanopy/data/` are verbatim CIE data tables (CIE S 026:2018 and the CIE 1931 2°
observer), © CIE and licensed **CC BY-SA 4.0** — they are **not** covered by the MIT license.
See [`src/melanopy/data/NOTICE.md`](src/melanopy/data/NOTICE.md) for sources, DOIs, and terms.

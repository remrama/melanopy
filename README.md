[![CI](https://github.com/remrama/melanopy/actions/workflows/ci.yml/badge.svg)](https://github.com/remrama/melanopy/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/remrama/melanopy/graph/badge.svg)](https://codecov.io/gh/remrama/melanopy)

# Melanopy: A melanopic axis for colormaps

Scientific colormaps are usually judged on two axes: **perceptual uniformity** and
**colour-vision-deficiency (CVD) safety**. Melanopy adds a third: how much short-wavelength,
**melanopic** (melatonin-suppressing) light a map emits. Unlike the other two, this third axis is a
**design dimension you choose by context, not a pass/fail gate** — a sleep lab wants its protective
end, a daytime alerting display the other. Melanopy makes the axis *measurable*, scores existing
colormaps on it, and provides a one-parameter family that walks it while holding uniformity and
CVD-safety fixed.

For people who read screens as their main light source at night (e.g., sleep labs, observatories,
NICU, night radiology, control rooms) large data-fills (e.g., spectrograms, density maps) actually
emit light, and their colour content can cooperate with, or fight, a chosen circadian lighting
strategy.

> This rates a colour's *chromaticity*, not light *dose*. Real circadian
> load also depends on screen brightness, screen fill, viewing distance, and ambient light.
> If you genuinely need to stay alert, the dominant lever is room lighting. The value
> here is measurability, a scored index, a uniformity-preserving generator, and surfacing
> the axis. The physiological effect of a colormap alone is second-order.

📖 **Documentation:** <https://remrama.github.io/melanopy>

## Quickstart

```python
import matplotlib.pyplot as plt
import numpy as np

import melanopy as mp

# Score any colormap on the melanopic axis  (display white = 1.0)
c = plt.get_cmap("viridis")(np.linspace(0, 1, 256))[:, :3]
print(mp.rate_colormap(c))
# {'melanopic_ratio': ~0.83, 'mp_spread': ..., 'range': (...)}

# Use the named endpoints (registered with matplotlib) on any 2-D field Z
mp.register()
Z = np.add.outer(np.linspace(0, 1, 200), np.linspace(0, 1, 200))
plt.imshow(Z, cmap="sodium")    # protective: warm, low-melanopic
plt.imshow(Z, cmap="xenon")     # alerting:   cool, high-melanopic
plt.imshow(Z, cmap="equilux")   # circadian-neutral (M/P ~ 1)

# Dial the whole axis: alpha 0 (protective) .. 1 (alerting)
cmap = mp.circadia(0.3, as_cmap=True)

# Or walk the whole axis in one map, or diverge for signed data
seq = mp.circadia_sweep()        # protective -> alerting; melanopic ratio ~linear in the data
div = mp.circadia_diverging()    # signed: warm protective <- neutral -> cool alerting
```

`melanopic_ratio` < 1 → protective (warm); > 1 → alerting (cool/blue).

## The two metrics

- **M/P mean** (`melanopic_ratio`) — *where* a map sits on the axis (white = 1).
- **M/P spread (σ)** (`mp_spread`) — *how tightly* it sits. A map can be mildly protective on
    average yet *smeared* (e.g. viridis dumps blue at its dark end); a tight spread reads as a
    "pure" ramp. Both numbers are luminance-weighted, so near-black pixels that emit almost nothing
    don't dominate either one.

## What scoring the existing maps reveals

Applying the rater to the colormaps people already use settles how much new design is even needed —
three non-obvious facts fall out (full table in [`index/`](index/README.md)):

- **A protective, pure map already exists** — `copper` (M/P 0.49, σ 0.03) and `sodium` (0.29); the
    protective end just needed naming, not inventing.
- **The popular uniform maps are *smeared*** — viridis / magma / inferno / cividis / plasma sit
    mid-axis but dump high-melanopic blue at their dark, low-data end (σ ≈ 0.4–1.0).
- **The genuine gap is a uniform, CVD-safe *alerting* map** — the slot the Circadia family's
    `xenon` endpoint is built to fill.

## Scope & novelty

- **Borrowed** — the melanopic *metrology*: the CIE S 026 melanopic action spectrum + V(λ),
    validated against the [luox](https://luox.app) reference calculator (melanopy reproduces the
    CIE S 026 D65 constant to five significant figures — see
    [`manuscript/luox_crosscheck.md`](manuscript/luox_crosscheck.md)).
- **New** — the *port to colormaps*: the per-display **three-coefficient collapse** (any sRGB
    colour → a weighted sum of three per-primary M/P numbers, so no runtime spectral integration);
    the **mean + spread** decomposition that catches "smeared" maps; and the
    **constraint-preserving generator** in which melanopic content is *emergent*, never optimized.

## Display panels

Melanopic content depends on the display's primary spectra, which sRGB doesn't fix — so the
rater takes a `panel=` argument selecting among representative archetypes (`representative`
narrowband, `led_lcd` blue-pump white-LED, `oled`, `wide_gamut` quantum-dot). Absolute M/P
shifts with the panel (the blue coefficient ranges ≈8.8 to ≈13.7), but the **ranking is
robust**: Spearman ρ ≥ 0.99 across panels, and display white stays exactly 1.0 (see
[`index/`](index/README.md)). For exact numbers on a specific monitor, plug its measured
primary SPDs into `melanopy.spectra.coefficients_from_primaries`.

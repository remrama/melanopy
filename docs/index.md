# Melanopy

**A melanopic (circadian) axis for scientific colormaps.**

Scientific colormaps are usually judged on two axes: **perceptual uniformity** and
**colour-vision-deficiency (CVD) safety**. Melanopy adds a third — how much
short-wavelength, **melanopic** (melatonin-suppressing) light a map emits — and makes it:

- **measurable** — a [rater](rating.md) that scores any colormap on the axis (display white = 1.0);
- **surveyed** — a [scored index](leaderboard.md) of the colormaps people already use;
- **generatable** — the [Diel family](generator.md), a one-parameter ramp that walks the axis
    while holding uniformity and CVD-safety fixed.

For people who read screens as their main light source at night — sleep labs, observatories,
NICUs, night radiology, control rooms — large data-fills (spectrograms, density maps) actually
emit light, and their colour content can cooperate with, or fight, a chosen circadian lighting
strategy.

!!! warning "Honest scope — a colour property, not a dose"

    Melanopy rates a colour's **chromaticity**, not light **dose**. Real circadian load also
    depends on screen brightness, screen fill, viewing distance, and ambient light. If you
    genuinely need to stay alert, the dominant lever is room lighting. The value here is
    measurability, a scored index, a uniformity-preserving generator, and surfacing the axis —
    the physiological effect of a colormap alone is second-order. See [Limitations](limitations.md).

## Install

```bash
pip install melanopy      # or:  uv add melanopy
```

## Quickstart

```python
import matplotlib.pyplot as plt
import numpy as np

import melanopy as mp

# Score any colormap on the melanopic axis (display white = 1.0)
c = plt.get_cmap("viridis")(np.linspace(0, 1, 256))[:, :3]
print(mp.rate_colormap(c))
# {'melanopic_ratio': 0.834, 'purity_sigma': 0.556, 'range': (0.395, 3.069)}

# Use the named endpoints (registered with matplotlib)
mp.register()
plt.imshow(Z, cmap="sodium")     # protective: warm, low-melanopic
plt.imshow(Z, cmap="xenon")   # alerting:   cool, high-melanopic
plt.imshow(Z, cmap="equilux")   # circadian-neutral (M/P ~ 1)

# Dial the whole axis: alpha 0 (protective) .. 1 (alerting)
cmap = mp.diel(0.3, as_cmap=True)
```

`melanopic_ratio` **< 1 → protective** (warm); **> 1 → alerting** (cool/blue).

## The two metrics

| metric                    | what it tells you                                                              |
| ------------------------- | ------------------------------------------------------------------------------ |
| **melanopic ratio (M/P)** | *where* a map sits on the axis (display white = 1)                             |
| **circadian purity (σ)**  | *how tightly* it sits — luminance-weighted spread; lower = more circadian-pure |

A map can be mildly protective on average yet *smeared* (viridis dumps blue at its dark end);
the two numbers tell that apart. See [Rating colormaps](rating.md).

## Where next

<div class="grid cards" markdown>

- **[The melanopic axis](axis.md)**

    The concept — and why melanopic content is a *dimension*, not a pass/fail rule.

- **[Rating colormaps](rating.md)**

    The rater pipeline, the three per-primary coefficients, and the two metrics.

- **[The scored index](leaderboard.md)**

    How common maps rank — and the gap that Xenon fills.

- **[The Diel family](generator.md)**

    The one-parameter, uniformity-preserving generator.

- **[Validation](validation.md)**

    CIE S 026, perceptual uniformity, and CVD — verified numerically.

- **[API reference](reference.md)**

    The public functions and named colormaps.

</div>

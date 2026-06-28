# Melanopy

**A melanopic (circadian) axis for scientific colormaps.**

Scientific colormaps are usually judged on two axes: **perceptual uniformity** and
**colour-vision-deficiency (CVD) safety**. Melanopy adds a third — how much short-wavelength,
**melanopic** (melatonin-suppressing) light a map emits. Unlike the other two, this one is a
**design dimension you choose by context, not a pass/fail gate**: a sleep lab wants the protective
end of the axis, a daytime alerting display the other. Melanopy makes it:

- **measurable** — a [rater](rating.md) that scores any colormap on the axis (display white = 1.0);
- **surveyed** — a [scored index](leaderboard.md) that, applied to the maps people already use,
    reveals that a protective, pure map *already exists* (`copper`), the popular uniform maps are
    *smeared*, and the real gap is a uniform, CVD-safe *alerting* map;
- **generatable** — the [Circadia family](circadia.md), a one-parameter ramp that walks the axis
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
# {'melanopic_ratio': 0.834, 'mp_spread': 0.556, 'range': (0.395, 3.069)}

# Use the named endpoints (registered with matplotlib) on any 2-D field Z
mp.register()
Z = np.add.outer(np.linspace(0, 1, 200), np.linspace(0, 1, 200))
plt.imshow(Z, cmap="sodium")     # protective: warm, low-melanopic
plt.imshow(Z, cmap="xenon")   # alerting:   cool, high-melanopic
plt.imshow(Z, cmap="equilux")   # circadian-neutral (M/P ~ 1)

# Dial the whole axis: alpha 0 (protective) .. 1 (alerting)
cmap = mp.circadia(0.3, as_cmap=True)
```

`melanopic_ratio` **< 1 → protective** (warm); **> 1 → alerting** (cool/blue).

## Scope & novelty

**Borrowed** — the melanopic *metrology*: the CIE S 026 melanopic action spectrum and V(λ),
validated against the [luox](https://luox.app) reference calculator (melanopy's weighting
reproduces the CIE S 026 D65 constant to five significant figures — see [Validation](validation.md)).

**New** — the *port to colormaps*: the per-display **three-coefficient collapse** (any sRGB colour →
a weighted sum of three per-primary M/P numbers, so no runtime spectral integration); the **mean +
spread** decomposition that catches "smeared" maps; and the **constraint-preserving generator** in
which melanopic content is *emergent*, never optimized.

## The two metrics

| metric                           | what it tells you                                             |
| -------------------------------- | ------------------------------------------------------------- |
| **M/P mean** (`melanopic_ratio`) | *where* a map sits on the axis (display white = 1)            |
| **M/P spread (σ)** (`mp_spread`) | *how tightly* it sits — a tight spread reads as a "pure" ramp |

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

- **[The Circadia family](circadia.md)**

    The one-parameter, uniformity-preserving generator.

- **[Validation](validation.md)**

    CIE S 026, the luox cross-check, perceptual uniformity, and CVD — verified numerically.

- **[API reference](reference.md)**

    The public functions and named colormaps.

</div>

# Melanopy

**A melanopic (circadian) axis for scientific colormaps.**

Colormaps are usually judged on two axes — **perceptual uniformity** and **colour-vision-deficiency
(CVD) safety**. Melanopy adds a third: how much short-wavelength, **melanopic**
(melatonin-suppressing) light a map emits. Unlike the other two it is a *design dimension you choose
by context, not a pass/fail gate* — a sleep lab wants the protective end of the axis, a daytime
alerting display the other.

The package **measures** the axis (a rater that scores any colormap, display white = 1.0),
**generates** a one-parameter family that walks it while holding uniformity and CVD-safety fixed,
and ships CVD-safe named colormaps.

![The Circadia family: one dial from protective (warm) to alerting (cool), lightness held uniform](assets/figures/circadian_generator.png){ loading=lazy }

!!! note "Scope — a colour property, not a dose"

    Melanopy rates a colour's **chromaticity**, not light **dose**. Real circadian load also depends
    on brightness, screen fill, viewing distance, and ambient light; if you need to stay alert the
    dominant lever is room lighting. The concept, validation, and limitations are covered in full in
    the [manuscript](https://github.com/remrama/melanopy) — these docs stay focused on the API.

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
plt.imshow(Z, cmap="xenon")      # alerting:   cool, high-melanopic
plt.imshow(Z, cmap="equilux")    # circadian-neutral (M/P ≈ 1)

# Dial the whole axis: alpha 0 (protective) .. 1 (alerting)
cmap = mp.circadia(0.3, as_cmap=True)
```

`melanopic_ratio` **< 1 → protective** (warm); **> 1 → alerting** (cool/blue).

## The two metrics

`rate_colormap` returns two distinct numbers:

| metric                           | what it tells you                                             |
| -------------------------------- | ------------------------------------------------------------- |
| **M/P mean** (`melanopic_ratio`) | *where* a map sits on the axis (display white = 1)            |
| **M/P spread (σ)** (`mp_spread`) | *how tightly* it sits — a tight spread reads as a "pure" ramp |

A map can be mildly protective on average yet *smeared* (viridis dumps blue at its dark end); the
two numbers tell that apart.

## Where next

- **[API reference](reference.md)** — the public functions and named colormaps, with examples.
- **[Cookbook](cookbook.md)** — short, copy-pasteable recipes with output.

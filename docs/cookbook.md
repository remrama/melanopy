# Cookbook

Short, copy-pasteable recipes. Each is self-contained — `import melanopy as mp` and go.
For the functions they draw on, see the [API reference](reference.md).

## Score a handful of colormaps

Rank any set of Matplotlib colormaps on the melanopic axis. `melanopic_ratio` is *where* a
map sits (display white = 1.0; < 1 protective, > 1 alerting); `purity_sigma` is *how
tightly* it sits (luminance-weighted spread).

```python
import matplotlib.pyplot as plt
import numpy as np

import melanopy as mp

for name in ["magma", "viridis", "cividis", "cool", "gray"]:
    c = plt.get_cmap(name)(np.linspace(0, 1, 256))[:, :3]
    s = mp.rate_colormap(c)
    print(f"{name:9s} M/P={s['melanopic_ratio']:.2f}  purity σ={s['purity_sigma']:.2f}")
```

For the full pre-computed ranking of common maps, see [The scored index](leaderboard.md).

## Sweep the Diel family

`mp.diel(alpha)` walks the axis from protective (`alpha=0`) to alerting (`alpha=1`) while
holding lightness uniform. Sweeping `alpha` and rating each step shows the melanopic ratio
climb monotonically — the dial is an *emergent* property of the OKLab geometry, not a knob
the generator sets.

```python
import matplotlib.pyplot as plt
import numpy as np

import melanopy as mp

alphas = np.linspace(0, 1, 9)
fig, axes = plt.subplots(len(alphas), 1, figsize=(7, 5))
ramp = np.linspace(0, 1, 256).reshape(1, -1)
for ax, a in zip(axes, alphas):
    ax.imshow(ramp, aspect="auto", cmap=mp.diel(a, as_cmap=True))
    s = mp.rate_colormap(mp.diel(a))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylabel(
        f"α={a:.2f}  M/P {s['melanopic_ratio']:.2f}",
        rotation=0,
        ha="right",
        va="center",
        fontsize=8,
    )
fig.tight_layout()
fig.savefig("diel_family.png", dpi=120)
```

## A live α-slider

Recolour a large fill in real time without touching the data — drag the slider, call
`im.set_cmap`. The SMACC reference app does the same through the pyqtgraph adapter
(`melanopy.adapters.pyqtgraph`); the idea is identical: move α, recolour the fill, never
recompute the data.

```python
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

import melanopy as mp

z = np.add.outer(np.sin(np.linspace(0, 6, 200)), np.cos(np.linspace(0, 6, 300)))
z = (z - z.min()) / (z.max() - z.min())

fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)
im = ax.imshow(z, cmap=mp.diel(0.0, as_cmap=True), aspect="auto")

sax = fig.add_axes([0.2, 0.06, 0.6, 0.04])
slider = Slider(sax, "Circadian (α)", 0.0, 1.0, valinit=0.0)
slider.on_changed(lambda v: (im.set_cmap(mp.diel(v, as_cmap=True)), fig.canvas.draw_idle()))
plt.show()
```

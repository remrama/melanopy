"""Sweep the Diel family; show the melanopic dial as stacked bars."""

import matplotlib.pyplot as plt
import numpy as np

import melanopy as mp

alphas = np.linspace(0, 1, 9)
fig, axes = plt.subplots(len(alphas), 1, figsize=(7, 5))
g = np.linspace(0, 1, 256).reshape(1, -1)
for ax, a in zip(axes, alphas):
    ax.imshow(g, aspect="auto", cmap=mp.diel(a, as_cmap=True))
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
plt.tight_layout()
plt.savefig("diel_family.png", dpi=120)
print("wrote diel_family.png")

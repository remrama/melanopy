"""Score colormaps on the melanopic axis."""

import matplotlib.pyplot as plt
import numpy as np

import melanopy as mp

for name in ["magma", "viridis", "cividis", "cool", "gray"]:
    c = plt.get_cmap(name)(np.linspace(0, 1, 256))[:, :3]
    s = mp.rate_colormap(c)
    print(f"{name:9s} M/P={s['melanopic_ratio']:.2f}  purity σ={s['purity_sigma']:.2f}")

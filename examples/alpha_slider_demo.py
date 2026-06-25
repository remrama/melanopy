"""Minimal live α-slider demo (matplotlib). The SMACC reference app uses the pyqtgraph
adapter (melanopy.adapters.pyqtgraph), but the idea is identical: move α, recolour the
large fill, never recompute the data."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

import melanopy as mp

Z = np.add.outer(np.sin(np.linspace(0, 6, 200)), np.cos(np.linspace(0, 6, 300)))
Z = (Z - Z.min()) / (Z.max() - Z.min())
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
im = ax.imshow(Z, cmap=mp.diel(0.0, as_cmap=True), aspect="auto")
sax = plt.axes([0.2, 0.06, 0.6, 0.04])
s = Slider(sax, "Circadian (α)", 0.0, 1.0, valinit=0.0)
s.on_changed(lambda v: (im.set_cmap(mp.diel(s.val, as_cmap=True)), fig.canvas.draw_idle()))
plt.show()

"""Generate the Melanopy logo: an iris whose radial gradient runs protective -> alerting.

The gradient is sampled from melanopy's own circadian axis (``circadia_sweep``): warm, low-melanopic
"protective" at the inner iris -> cool, high-melanopic "alerting" at the outer rim -- so the mark
literally shows the axis the package measures.

    uv run scripts/build_logo.py                          # -> docs/assets/logo.png (512)
    uv run scripts/build_logo.py --out preview.png --size 256
"""

import argparse
from pathlib import Path

import matplotlib.image as mpimg
import numpy as np

import melanopy as mp

ROOT = Path(__file__).resolve().parents[1]


def _step(a, b, x):
    """Smoothstep: 0 at x<=a, 1 at x>=b, with a smooth ramp between (works for a>b too)."""
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _gradient(n=256, sat=1.35):
    """Warm (protective) -> cool (alerting) sampled from the Circadia axis at near-constant
    lightness, then chroma-boosted -- a clean amber->blue hue sweep that reads at a glance.

    Walks ``alpha`` 0..1 (the protective->alerting dial) and takes one high-lightness sample from
    each ramp, so it is literally melanopy's axis rather than a hand-picked palette.
    """
    a = np.linspace(0, 1, 40)
    samp = np.array([mp.circadia(v)[184] for v in a])  # ~L 0.72 slice of each alpha ramp
    g = np.column_stack([np.interp(np.linspace(0, 1, n), a, samp[:, c]) for c in range(3)])
    y = g @ np.array([0.2126, 0.7152, 0.0722])
    return np.clip(y[:, None] + sat * (g - y[:, None]), 0, 1)


def _iris(size, seed=7):
    rng = np.random.default_rng(seed)
    n = size
    y, x = np.mgrid[0:n, 0:n].astype(float)
    x = (x - (n - 1) / 2) / (n / 2)
    y = (y - (n - 1) / 2) / (n / 2)
    r = np.hypot(x, y)
    th = np.arctan2(y, x)

    pr, ir = 0.30, 0.94  # pupil radius, iris outer radius
    t = np.clip((r - pr) / (ir - pr), 0, 1)  # 0 inner iris -> 1 outer rim

    lut = _gradient(256)  # protective (warm) -> alerting (cool), vivid, near-constant lightness
    rgb = lut[np.clip((t * 255).astype(int), 0, 255)]

    # radial iris fibres: coherent along r, varying with theta -> spokes; faded at both ends
    fib = 0.55 * np.sin(th * 90 + 2.2 * np.sin(th * 13)) + 0.45 * np.sin(
        th * 210 + rng.uniform(0, 6)
    )
    fade = _step(pr, pr + 0.12, r) * _step(ir, ir - 0.25, r)
    bright = 1 + 0.16 * fib * fade

    # collarette (the thick inner ring) + fine furrows crossing it
    coll = np.exp(-((t - 0.18) ** 2) / (2 * 0.06**2))
    bright *= 1 - 0.20 * coll * (0.5 + 0.5 * np.sin(th * 160))
    rgb = np.clip(rgb * bright[..., None], 0, 1)
    rgb *= (1 - 0.26 * coll)[..., None]

    # dark limbal ring at the outer edge
    rgb *= (1 - 0.55 * _step(ir - 0.10, ir, r))[..., None]

    # pupil (near-black, soft edge)
    pup = _step(pr, pr - 0.03, r)
    rgb = rgb * (1 - pup)[..., None] + np.array([0.02, 0.02, 0.03]) * pup[..., None]

    # wet-eye specular highlight, upper-left (image y grows downward, so -0.42 is up)
    spec = np.exp(-(((x + 0.30) ** 2 + (y + 0.42) ** 2) / (2 * 0.085**2)))
    rgb = np.clip(rgb + 0.7 * spec[..., None], 0, 1)

    alpha = _step(ir + 0.02, ir - 0.02, r)  # circular disk, soft anti-aliased edge
    return np.dstack([rgb, alpha])


def build(size=512, ss=3, seed=7):
    """Render at ``ss``x resolution and box-downsample for crisp, anti-aliased fibres."""
    big = _iris(size * ss, seed)
    return big.reshape(size, ss, size, ss, 4).mean((1, 3))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=ROOT / "docs/assets/logo.png")
    p.add_argument("--size", type=int, default=512)
    p.add_argument("--seed", type=int, default=7)
    a = p.parse_args()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    mpimg.imsave(a.out, build(a.size, seed=a.seed))
    print(f"wrote {a.out}  ({a.size}x{a.size})")


if __name__ == "__main__":
    main()

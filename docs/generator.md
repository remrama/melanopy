# The Diel family

The leaderboard says a warm, circadian-pure map already exists, but a perceptually-uniform,
CVD-safe **alerting** map does not. The **Diel family** is a one-parameter generator built to
walk the whole axis without giving up uniformity.

![The Diel family swept across alpha](assets/figures/circadian_generator.png){ loading=lazy }

## One dial, `alpha`

```python
import melanopy as mp

cmap = mp.diel(0.3, as_cmap=True)   # a matplotlib ListedColormap
rgb  = mp.diel(0.3)                 # or the raw (256, 3) sRGB array
```

`alpha` runs from **0 (protective)** to **1 (alerting)**:

| anchor      | `alpha` | M/P    | character                             |
| ----------- | ------- | ------ | ------------------------------------- |
| **Sodium**  | 0.00    | 0.29   | warm, protective, circadian-pure      |
| **Equilux** | 0.55    | ≈ 1.00 | circadian-neutral (M/P = 1 crossover) |
| **Xenon**   | 1.00    | 1.73   | cool, alerting                        |

The three anchors are exported as ready-made colormaps (`mp.SODIUM`, `mp.EQUILUX`,
`mp.XENON`) and registered with matplotlib by name:

```python
mp.register()
plt.imshow(Z, cmap="sodium")     # protective
plt.imshow(Z, cmap="equilux")   # neutral
plt.imshow(Z, cmap="xenon")   # alerting
```

## Why uniformity comes for free

The generator is pure OKLab geometry — it never looks at the melanopic coefficients. The trick
is a **single monotonic lightness profile shared by every `alpha`**:

- Lightness (the `L` in OKLab) increases monotonically along the ramp, identically for all
    `alpha`. Monotone lightness is what keeps the map **ordered and recoverable under CVD** and
    close to **perceptually uniform**.
- `alpha` morphs **only the chroma vector** — the warm hue path at `alpha = 0` rotates to the
    cool hue path at `alpha = 1`. A gamut clamp reduces chroma (preserving `L` and hue) wherever a
    colour would fall outside sRGB.

Because lightness does all the structural work and `alpha` only steers chroma, **perceptual
uniformity and CVD-recoverability hold for every `alpha`**, and the **melanopic ratio is an
emergent, monotonic** function of `alpha` (0.29 → 1.73) — the generator never computes it. That
both properties actually hold is *verified numerically*, not asserted — see
[Validation](validation.md).

!!! note "A fundamental warm/cool asymmetry"

    Sodium is far more circadian-pure than Xenon (σ 0.07 vs 0.42). This is a property of the
    display gamut, not a tuning miss: short-wavelength primaries are intrinsically low-luminance,
    so *a light, saturated blue does not exist* — light cool colours must desaturate toward white
    (M/P → 1). A perfectly pure **protective** map is achievable; a perfectly pure **alerting**
    one is not, under a shared lightness profile.

## Beyond one dial — full-axis and diverging maps

`diel(alpha)` fixes the melanopic temperature and renders it as a sequential ramp. Two derived
maps cover the other common needs.

### `diel_sweep` — the whole axis in one map

Where `diel` holds the temperature fixed, **`diel_sweep`** lets it rise *along* the ramp: low data
is protective (warm, Sodium-like), high data is alerting (cool, Xenon-like), so the **melanopic
ratio increases ~linearly with the data value** (≈ 0.38 → 1.29). The data axis literally *is* the
melanopic axis, which makes it a natural teaching map; lightness still rises monotonically, so it
stays ordered and CVD-recoverable.

```python
rgb = mp.diel_sweep()              # (256, 3) sRGB
plt.imshow(Z, cmap="diel_sweep")  # after mp.register()
```

It is the one melanopic-aware generator: positions are calibrated against the rater to linearize
M/P, whereas the core `diel` stays pure OKLab geometry.

### `diel_diverging` — signed data

For signed data (z-scored EEG, ERP differences, anomalies) **`diel_diverging`** places a light,
**circadian-neutral centre** (M/P = 1) between a warm protective arm (Sodium, M/P < 1) and a cool
alerting arm (Xenon, M/P > 1):

```python
rgb = mp.diel_diverging()             # warm below the centre, cool above
plt.imshow(Z, cmap="diel_diverging")  # pair with a symmetric / centered norm
```

!!! warning "Diverging maps and CVD"

    Like most diverging maps, the two arms are told apart across zero by **hue**, which colour
    blindness compresses — so `diel_diverging` is **not** CVD-order-recoverable. When CVD-safety
    matters, reach for the sequential maps (`diel`, `diel_sweep`).

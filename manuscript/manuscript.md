# A melanopic axis for scientific colormaps: a rater, a scored index, and a uniformity-preserving generator

**Author.** Remington Mallett.

**Naming.** *Melanopy* is the collection and the Python package
(`import melanopy as mp`). The one-parameter family is **Circadia** (`mp.circadia(alpha)`); its
endpoints are **Sodium** (α = 0, warm/protective) and **Xenon** (α = 1, cool/alerting), with
**Equilux** (α ≈ 0.55, melanopic ratio ≈ 1) as the neutral crossover. The dial α is the *melanopic
temperature*. The two reported metrics are the **M/P mean** — where a map sits on the axis — and the
**M/P spread (σ)** — how tightly it sits. This split is deliberate: the *measured* quantities take
the precise optical term **melanopic** (M/P mean, M/P spread), while the colormap *family* takes the
evocative name **Circadia** — precision for what is measured, motivation for what is named.

---

## Abstract

Scientific colormaps are designed around two axes: **perceptual uniformity** (equal data steps
look equal) and **colour-vision-deficiency (CVD) safety** (the map survives colour blindness). We
introduce a third — **melanopic content**, the short-wavelength, melatonin-suppressing light a
colormap emits — which, unlike the other two, is a design *dimension* selected by context rather
than a pass/fail requirement, and which matters whenever a display is a viewer's dominant light
source at night:
sleep laboratories, observatories, neonatal intensive care, overnight radiology, and control
rooms. We make this axis *measurable* for colormaps. All of a display's dependence collapses into
**three per-primary melanopic/photopic coefficients** derived from the CIE S 026:2018 melanopic
action spectrum, reducing the melanopic content of any sRGB colour to a weighted sum of three
numbers. From this we report two luminance-weighted quantities per map: an **M/P mean** (axis
position, normalized so display white = 1) and an **M/P spread** (how tightly that ratio sits along
the ramp). Scoring the colormaps people already use yields three findings: a warm, pure sequential
map *already exists* (`copper`, and our `sodium`); the popular perceptually-uniform maps are
*smeared* (viridis and its siblings dump high-melanopic blue at their dark, low-data end); and the
genuine gap is a perceptually-uniform, CVD-safe **alerting** map. We fill that gap with the
**Circadia family**, a one-parameter generator that walks
the axis (melanopic ratio 0.29 → 1.73) while holding perceptual uniformity and CVD-recoverability
fixed — by sharing a single monotone-lightness profile across the parameter and letting it steer
only chroma. We are explicit about scope: we rate a colour's *chromaticity*, not a light *dose*,
and the physiological effect of a colormap alone is second-order. The contribution is the
measurement, the scored index *and the empirical findings it yields*, the constrained generator, and
surfacing an axis the field has not named. The rater, index, generator, and figures are reproducible
from the open-source package.

---

## 1. Introduction & statement of need

Most guidance on scientific colormaps optimizes how a map is *read*: whether equal differences in
the data produce equal perceived differences in colour (perceptual uniformity), and whether that
reading survives colour-vision deficiency (CVD-safety). Those are the right priorities for almost
every figure. But a colormap is also *light*. On a self-luminous display a large data-fill — a
spectrogram, a density map, a heat map — covers a substantial fraction of the screen and therefore
emits a substantial fraction of the screen's light. When the viewer is in a dark room and the
display is their dominant light source, the *spectrum* of that emitted light is not cosmetic: short
wavelengths drive the intrinsically photosensitive retinal ganglion cells that regulate the
circadian system and acutely suppress melatonin [@lucas2014melanopsin; @brown2020melanopic].

This situation is not exotic. Sleep laboratories, observatories, neonatal intensive-care units,
overnight radiology reading rooms, and 24-hour control centres all put practitioners in front of
data displays at night, deliberately in dim surroundings. Our own motivating deployment is SMACC,
a sleep/dream-research acquisition tool whose operators watch live EEG spectrograms through the
night (§8). In all of these settings the colour content of the large fills can *cooperate with* —
or *fight* — whatever circadian-lighting strategy the room is running.

Colormap craft offers no vocabulary for this. Collections are organized by structure, by domain,
or by data type, but none by circadian/melanopic content (§2). The metrology to quantify melanopic
light is standardized and mature [@cie_s026_2018; @lucas2014melanopsin], but it operates on
spectral power distributions, not on the sRGB arrays that are colormaps. This paper bridges the
two. We contribute: (i) a **rater** that scores any colormap on a melanopic axis; (ii) a **scored
index** of common colormaps, which empirically settles how much new map design is even needed;
(iii) a one-parameter **generator** that walks the axis while preserving uniformity and CVD-safety;
and (iv) a reference **application** that exposes the parameter as a live control. The concept and
the index are the headline; the generated maps are a worked example.

## 2. Background

**The two axes the field already uses.** Modern colormap design is organized around perceptual
uniformity, monotone ordering, and CVD-safety. The viridis family was built to be uniform and
CVD-robust [@smith2015viridis]; cividis optimizes explicitly for CVD [@nunez2018cividis]; Kovesi's
CET maps systematize uniformity [@kovesi2015colourmaps]; Moreland's diverging maps solved the
midpoint problem for signed data [@moreland2009diverging]; and Crameri's work documents how much
colour misuse still distorts science [@crameri2020colour]. Where collections add organizing
structure, they sort by *structure* itself (Crameri), by *domain* (cmocean [@thyng2016cmocean]), or
by *data type* (ColorBrewer [@harrower2003colorbrewer]). **None sorts by circadian or melanopic
content.** That empty slot is the opening this paper fills.

**The metrology we stand on.** Quantifying melanopic light is a solved, standardized problem. The
CIE S 026:2018 system defines the melanopic action spectrum and the α-opic quantities
[@cie_s026_2018], formalizing the framework of Lucas et al. [@lucas2014melanopsin]; melanopic
equivalent daylight illuminance predicts circadian responses across a wide range of conditions
[@brown2020melanopic]; and validated open implementations exist (luox [@spitschan2021luox], LuxPy,
and Colour). Crucially, these tools take **spectral power distributions** as input. They do not
answer "where does viridis sit?", because a colormap is a list of sRGB triples, not a spectrum. We
build directly on this metrology rather than reinventing it; our work is the missing adapter from
colormaps to the established melanopic measure.

## 3. The melanopic axis

The central conceptual move is to treat melanopic content as a **design dimension, not a pass/fail
rule**. Perceptual uniformity and CVD-safety are *universal requirements*: every map should clear
them, and a map that fails is simply worse. Melanopic content is different. Every map sits
*somewhere* on the axis, and "good/bad" does not apply — only *which regime suits which context*:

- **protective** — warm, low melanopic ratio (M/P < 1);
- **alerting** — cool / blue-rich, high melanopic ratio (M/P > 1),

with **display white as the unit** (M/P = 1). A daytime alertness display and an overnight sleep-lab
display want opposite ends of the same axis; neither end is "correct" in the abstract.

**The area-weighted melanopic budget.** Why does the axis matter for some marks and not others?
Because emitted light scales with screen area. Large fills — spectrograms, density maps, heat maps —
cover a big fraction of the display and dominate the light it emits, so the axis matters for them.
Small categorical marks — lines, points, glyphs — emit negligibly regardless of their colour, so
for them the axis is effectively *"ignore it"*: a single CVD-safe categorical palette serves every
circadian regime. This split is a design principle, not a limitation: it tells us to spend the
melanopic budget on *sequential fills* and to keep categorical colour a separate, fixed concern.
(Melanopy ships exactly one CVD-safe categorical palette, justified by this argument; it stays
well-separated under simulated colour blindness, Fig. 1.)

![**Figure 1.** The area-weighted budget in practice. *Top:* the protective endpoint Sodium under simulated dichromacy stays order-preserving — lightness does the ordering work. *Middle/bottom:* the single CVD-safe categorical palette stays well-separated under colour blindness, so one palette serves every circadian regime.](figures/melanopic_colormaps.png)

## 4. Rating colormaps

The rater turns a colormap into numbers on the melanopic axis. For each colour in the map:

```
sRGB → linearize → displayed SPD = r·P_R + g·P_G + b·P_B
                 → photopic luminance  Y   (exact sRGB weights)
                 → melanopic           M   (∫ SPD · s_mel,  CIE S 026)
                 → M/P, normalized so display white = 1
```

The pipeline's organizing insight is that, because a display's primaries `P_R, P_G, P_B` are
fixed, the melanopic content of any colour collapses to a weighted sum of **three per-primary
coefficients** — the melanopic/photopic ratio of each RGB primary. For the representative panel:

| primary | coefficient (M/P) |
|---|---|
| R | 0.0031 |
| G | 0.6555 |
| B | 10.9681 |

The blue primary does almost all of the melanopic work, which is precisely why the axis is mostly a
warm ↔ cool story, and why the warm/cool spread asymmetry of §6 is fundamental rather than
incidental. These three numbers are the entire display-dependent part of the model; swapping in a
different panel means swapping three coefficients (§4.2).

### 4.1 Two metrics

Both reported quantities are **luminance-weighted**, and near-black pixels (which emit almost
nothing) are dropped — a pipeline-level decision so that neither number is dominated by the dark end
of the ramp. A single mean still hides the structure that matters, so the rater reports **two
distinct quantities** (plus the raw per-position range):

- **M/P mean** — *where* the map sits: the mean of the per-position ratio (display white = 1;
  < 1 protective, > 1 alerting).
- **M/P spread (σ)** — *how tightly* it sits: the spread of the per-position ratio along the ramp.
  A tight spread reads as a "pure" ramp.

The two are independent, and the gap between them is the point. viridis sits mid-axis (M/P 0.83 —
mildly protective on *average*) yet has a high spread (σ 0.56): it dumps high-melanopic blue at its
dark, low-data end, so it is *smeared*, not tight. A protective mean and a pure ramp are different
properties, and a map can have one without the other. (Concretely, `rate_colormap(viridis)` returns
`melanopic_ratio = 0.834`, `mp_spread = 0.556`, `range = (0.395, 3.069)`.)

### 4.2 Display-panel dependence

Melanopic content depends on the display's primary spectra, which sRGB does **not** fix. The rater
therefore takes a `panel` argument selecting among representative archetypes — narrowband RGB
(default), blue-pump white-LED LCD, OLED, and quantum-dot wide-gamut. Absolute M/P shifts with the
panel (the blue coefficient ranges ≈ 8.8 for OLED to ≈ 13.7 for wide-gamut), but the **ranking is
robust** to it (§5.1). For exact numbers on a specific monitor, a user plugs that monitor's
measured primary SPDs into `melanopy.spectra.coefficients_from_primaries` and obtains its own three
coefficients.

## 5. A scored index of existing colormaps

A rater invites an obvious empirical question — *where do the colormaps people already use actually
land?* — and answering it decides how much new design is needed at all. We scored a representative
set on the default panel (display white = 1; regenerable from the package):

| colormap | M/P | σ (spread) | regime |
|---|---|---|---|
| **sodium** (Melanopy) | 0.29 | 0.07 | protective, pure |
| copper | 0.49 | 0.03 | protective, pure |
| inferno | 0.50 | 0.45 | mid, smeared |
| cividis | 0.72 | 0.44 | mid, smeared |
| viridis | 0.83 | 0.56 | mid, smeared |
| **equilux** (Melanopy) | 1.00 | 0.16 | neutral |
| gray | 1.00 | 0.00 | neutral |
| Blues | 1.33 | 0.40 | alerting |
| **xenon** (Melanopy) | 1.73 | 0.42 | alerting, ~PU/CVD |
| cool | 2.06 | 0.58 | alerting, not PU |

![**Figure 2.** The melanopic leaderboard: common colormaps placed on the axis (display white = 1), with per-map M/P mean and M/P spread; per-panel bands show robustness to the display archetype.](figures/melanopic_leaderboard.png)

Three findings fall out:

1. **A protective, pure map already exists.** `copper` (M/P 0.49, σ 0.03) and our `sodium`
   (0.29, σ 0.07) sit both low *and* flat — a warm, pure sequential map has been hiding
   in matplotlib all along. No new design is needed at the protective end; it needs only to be
   *named and surfaced*.
2. **The popular uniform maps are smeared.** viridis, magma, inferno, cividis, and plasma sit
   mid-axis but dump high-melanopic blue at their dark (low-data) end — none is tight
   (σ ≈ 0.4–0.6). Choosing one of these "for safety" at night does not buy a low melanopic load;
   it buys a *mixed* one.
3. **The genuine gap is a pure alerting map.** The maps that reach the alerting end — `cool`,
   `winter`, `Blues` — are either not perceptually uniform or single-hue. A perceptually-uniform,
   CVD-safe *alerting* map does not exist off the shelf. That is the one slot worth generating, and
   it motivates the Circadia family's Xenon endpoint (§6).

### 5.1 Robustness to the display panel

The single biggest threat to a rater like this is that its conclusions might be an artifact of one
assumed display. We therefore re-scored every map under all four panel archetypes. Absolute M/P
**is** panel-dependent (driven by the blue coefficient's ≈ 8.8–13.7 range), but the **ranking is
not**: Spearman ρ ≥ 0.99 against the representative panel, with display white pinned at exactly 1.0
on every panel and the widest single-map band being the saturated `cool` (≈ 0.32 across panels).
So *where a map sits on the axis* is a property one can trust without knowing the exact monitor —
which is what makes the index, not just a single measurement, worth publishing.

## 6. The Circadia family: a uniformity-preserving generator

The leaderboard says the protective end is already covered but the alerting end is not. The
**Circadia family** is a one-parameter generator built to walk the whole axis without surrendering
uniformity or CVD-safety at any point along it.

![**Figure 3.** The Circadia family swept across α from the protective endpoint Sodium (α = 0) through the neutral Equilux (α ≈ 0.55) to the alerting Xenon (α = 1). Lightness rises identically for every α; only the chroma path changes.](figures/circadian_generator.png)

The dial α runs from 0 (protective) to 1 (alerting):

| anchor | α | M/P | character |
|---|---|---|---|
| **Sodium** | 0.00 | 0.29 | warm, protective, pure |
| **Equilux** | 0.55 | ≈ 1.00 | neutral (M/P = 1 crossover, true α ≈ 0.5505) |
| **Xenon** | 1.00 | 1.73 | cool, alerting |

**Why uniformity comes for free.** The generator is pure OKLab geometry [@ottosson2020oklab]; it
never looks at the melanopic coefficients of §4. The trick is a **single monotone-lightness profile
shared by every α**. Lightness (the L of OKLab) increases identically along the ramp for all α,
and α morphs *only the chroma vector* — rotating the warm hue path at α = 0 to the cool hue path at
α = 1, with a gamut clamp that reduces chroma (preserving L and hue) wherever a colour would leave
sRGB. Because lightness does all of the structural work and α only steers chroma, perceptual
uniformity and CVD-recoverability hold for *every* α, and the **melanopic ratio is an emergent,
monotone function of α** (0.29 → 1.73) that the generator never computes. The axis falls out of the
geometry; it is not imposed on it. That both properties actually hold is *verified numerically*
(§7), not assumed.

**A fundamental warm/cool asymmetry.** Sodium sits far tighter on the axis than Xenon (M/P spread
σ 0.07 vs 0.42), and this is a property of the display gamut, not a tuning miss. Short-wavelength
primaries are intrinsically low-luminance, so *a light, saturated blue does not exist* — light cool
colours must desaturate toward white, where M/P → 1. A perfectly pure *protective* map is therefore
achievable under a shared lightness profile, but a perfectly pure *alerting* one is not.
This is a statement about the intersection of the melanopic axis with the sRGB gamut, and we report
it rather than hide it (§9).

## 7. Validation

Two separate claims need backing, and both are checked **numerically in the test suite** rather
than asserted.

**The spectral weighting (CIE S 026).** The melanopic weighting is the standardized one: the CIE
S 026:2018 melanopic action spectrum together with the CIE 1931 2° V(λ) photopic function, both
vendored from the source tables. Replacing an earlier analytic template with the validated S 026
spectrum, the melanopic response peaks at **490 nm** as expected; display gray stays **1.000**; the
leaderboard ranking is essentially unchanged (every map moved ≤ 0.035); and the generator span is
unchanged (0.29 → 1.73) and still monotone. The baked per-primary coefficients are regression-locked
to this spectrum, so the data and the numbers cannot silently drift apart.

![**Figure 4.** CIE S 026 validation: the melanopic action spectrum (peak 490 nm), display gray pinned at 1.000, and the leaderboard ranking unchanged (every map moved ≤ 0.035) when the analytic template is replaced by the validated spectrum.](figures/s026_validation.png)

**External cross-check (luox / CIE S 026).** As an independent check, melanopy's spectral engine
reproduces the CIE S 026 D65 melanopic ELR normalization constant — the quantity on which the
validated luox calculator [@spitschan2021luox] is built — to five significant figures (1.32621 vs
1.3262 mW/lm), and yields the expected melanopic daylight-efficacy ratios (mel-DER) for the standard
illuminants: D65 = 1.000 (by definition), equal-energy = 0.906, and Illuminant A = 0.496. The three
representative primaries reproduce melanopy's baked per-primary coefficients exactly. Method and a
luox-uploadable spectrum set are in the companion `luox_crosscheck.md`.

**Perceptual uniformity and CVD-recoverability.** The generator's structural claims are checked
with `colorspacious`. For perceptual uniformity, the CAM02-UCS lightness (J′) is strictly
increasing along each Circadia map and the CAM02-UCS step sizes are near-constant (coefficient of
variation < 0.30). For CVD, under simulated deuteranopia, protanopia, and tritanopia (Machado et
al. model [@machado2009cvd], severity 100) the perceived lightness stays strictly monotone, so the
data order remains recoverable. We deliberately say **CVD-recoverable**, not the stronger
"CVD-safe": a shared monotone-lightness profile guarantees recoverable *order*, which is exactly
what the tests show and exactly what we claim.

## 8. Reference application: an in-app circadian slider

The generator's α is most useful as a *live control*. SMACC (a PyQt6 + pyqtgraph sleep/dream
research tool) is our reference deployment: α is exposed as a toolbar slider so the screen's colour
temperature can be moved along the melanopic axis during an overnight session without leaving the
app.

**What α controls.** It drives the active scientific colormap for large-fill views — the EEG
spectrogram, hypnogram density, scalp/topographic maps — where the melanopic budget is non-trivial.
Optionally it also drives the UI accent tokens, so chrome and data move together. Categorical
line/scatter views need *not* react: the area-weighted budget (§3) says their emission is
negligible. Bindings can be manual (raw α, or labelled presets *Protective / Neutral / Alerting*),
scheduled by the clock (an automatic warm-down across the night), driven by an ambient-light sensor
or an "I'm fading" button, or coupled to the app's theme mode.

**Why in-app, not a global filter.** This is the core justification and a paper-worthy point. A
global gamma/LUT warp such as f.lux or OS Night Shift tints the entire framebuffer
*data-blind* and non-uniformly, which **breaks perceptual uniformity and CVD-safety** for every
figure on screen — and, empirically, a spectral shift without dimming does not reliably reduce
melatonin suppression anyway [@nagare2019nightshift]. Doing the adjustment at the *data → colour*
step instead preserves uniformity and CVD-safety by construction, touches only the analysis canvas
(never a participant-facing display), and lets one dial drive plots and chrome coherently.

**Honesty surfaced in the UI itself.** The slider changes *appearance* and how the screen
*participates in* the room's circadian strategy; it is **not** an alertness dial. The interface
pairs it with brightness and room-light guidance, restating the governing truth: if the goal is
genuinely to stay awake, light the room — the colormap is a second-order, mostly non-interference
lever.

**Implementation.** A small lookup table of α steps is precomputed at startup (or the 256×3 sRGB
array is regenerated on demand, a sub-millisecond cost), wrapped as a `pyqtgraph.ColorMap` and
applied to the relevant `ImageItem`/`PlotItem` LUTs; the slider is debounced to recolor only, never
to recompute the data. α persists in the session config, with an optional schedule table (α vs.
clock time).

## 9. Limitations & honest scope

Melanopy's credibility *is* its contribution, so the caveats are stated plainly rather than buried.

- **It rates chromaticity, not dose.** We report a colour property, never a light dose or an
  alertness effect. Actual circadian load is roughly screen luminance × fraction of screen filled ×
  viewing distance × ambient light — none of which a colormap fixes. If the goal is genuinely to
  stay alert, the dominant lever is room lighting.
- **Display-primary dependence.** The three coefficients assume a representative panel; real
  white-LED-LCD, OLED, and wide-gamut displays differ, especially in blue. We ship several panel
  archetypes and let users plug in measured SPDs. S 026 validates the *spectral weighting*; the
  *panel model* is orthogonal and still approximate. Reassuringly, the ranking is robust across
  panels (§5.1).
- **The warm/cool spread asymmetry is fundamental.** A perfectly pure protective map is achievable;
  a perfectly pure alerting one is not, because light saturated blues do not exist in the gamut
  (§6). This is a property of the axis ∩ the display gamut, not a defect to be tuned away.
- **"CVD-recoverable", not "CVD-safe".** A shared monotone-lightness profile makes *order*
  recoverable under CVD; we verify that and claim exactly that, no more.
- **The physiological effect is second-order.** The dominant levers are screen brightness, UI
  background, and room light. Melanopy's worth is (a) measurability, (b) the tool and index,
  (c) surfacing the axis, and (d) a modest *non-interference* claim — letting large fills cooperate
  with whatever circadian strategy the room already runs.
- **Prior-art scope.** The novelty claim rests on a structured related-work pass across three
  literatures (§10), documented separately, not a full PRISMA systematic review.

## 10. Related work & novelty

Three mature fields border this work, and the contribution sits in the gap between them.
(1) **Melanopic metrology:** CIE S 026 [@cie_s026_2018] and validated calculators
[@spitschan2021luox] on the α-opic framework of Lucas et al. [@lucas2014melanopsin], with melanopic
EDI predicting circadian responses [@brown2020melanopic] — all operating on SPDs, not colormaps.
(2) **Colormap craft:** perceptual uniformity, ordering, and CVD-safety [@smith2015viridis;
@nunez2018cividis; @kovesi2015colourmaps; @moreland2009diverging; @crameri2020colour], with
collections organized by structure, domain, or data type [@thyng2016cmocean; @harrower2003colorbrewer]
— none by melanopic content. (3) **Lighting-domain melanopic modulation**, where the axis idea
actually lives, but for lamps and display *hardware*: metameric display tuning that varies melanopic
output independent of visual appearance [@allen2018metamerism] (the closest prior art — a 5-primary
VDU for melatonin/alertness experiments, *not* a colormap tool), and OS night-shift filters
[@nagare2019nightshift].

The melanopic axis itself is therefore *not* novel — it is mature in lighting. **What is novel is
the port to scientific colormaps as four specific artifacts:** a melanopic *rater for colormaps*, a
*per-data-position* melanopic profile, a *scored index* of existing scientific maps, and a
*perceptual-uniformity- and CVD-constrained generator* parameterized by melanopic content. We
searched the three literatures above and found no precedent for any of the four — a defensible
related-work pass (English-only, without a patent-database sweep), not an exhaustive systematic
review.

## 11. Availability & reproducibility

Melanopy is an open-source Python package (`pip install melanopy`; numpy + matplotlib only at
runtime). The code is MIT-licensed; the vendored CIE reference tables (S 026:2018 and the CIE 1931
2° observer) are © CIE and redistributed under CC BY-SA 4.0, documented with sources and DOIs. The
scored index ships in the repository and regenerates from the package
(`scripts/build_leaderboard.py`); the panel-robustness analysis and all four figures regenerate the
same way (`scripts/build_panel_robustness.py`, `scripts/build_figures.py`). The validation claims of
§7 are the test suite (`pytest`), run in CI across a Python/OS matrix. Documentation, including an
API reference, is published at the project site. Every numeric claim in this paper is reproducible
from a clean checkout.

## References

Rendered from `references.bib` (Pandoc `[@key]` citations). Cited keys: `smith2015viridis`,
`nunez2018cividis`, `kovesi2015colourmaps`, `moreland2009diverging`, `crameri2020colour`,
`thyng2016cmocean`, `harrower2003colorbrewer`, `cie_s026_2018`, `lucas2014melanopsin`,
`spitschan2021luox`, `brown2020melanopic`, `allen2018metamerism`, `nagare2019nightshift`,
`machado2009cvd`, `ottosson2020oklab`. (`govardovskii2000template` and `wyman2013cmf` support the
offline spectral/CMF derivation in `spectra.py`.)

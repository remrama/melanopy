# Prior-art search & novelty statement

> Turns the §10 "scan, not a systematic review" caveat into a documented search. Scope: a
> defensible related-work pass for a viz short paper, not a PRISMA review. Conducted 2026-06
> via web search (Google Scholar / publisher sites / PubMed). Records the fields, queries, and
> what was — and was not — found. See `references.bib` for full citations.

## Claim under test

Melanopy's novelty is **not** the melanopic axis itself (well-established in lighting), but its
**port to scientific colormaps** as four specific artifacts:

1. a melanopic **rater** for a colormap (M/P normalized to display white);
2. a **per-data-position** melanopic profile (where on the ramp the blue sits);
3. a **scored leaderboard** of existing scientific colormaps;
4. a **PU + CVD-constrained generator** parameterized by melanopic content.

The search asks: does any of (1)–(4) already exist?

## Fields searched & findings

**A. Melanopic metrology (the measurement we stand on).** CIE S 026:2018 standardizes the
α-opic framework introduced by Lucas et al. 2014 [`lucas2014melanopsin`]; melanopic equivalent
daylight illuminance predicts circadian responses [`brown2020melanopic`]; validated calculators
exist (luox [`spitschan2021luox`], LuxPy, Colour). **All operate on spectral power
distributions, not sRGB colormaps.** We build on them; we do not reinvent them.

**B. Colormap craft (the universal bar).** The field is organized around perceptual uniformity,
ordering, and CVD-safety: viridis [`smith2015viridis`], cividis [`nunez2018cividis`], Kovesi/CET
[`kovesi2015colourmaps`], Moreland's diverging maps [`moreland2009diverging`], Crameri's
Scientific Colour Maps [`crameri2020colour`]; CVD via Machado et al. [`machado2009cvd`].
Collections are organized by *structure* (Crameri), *domain* (cmocean [`thyng2016cmocean`]), or
*data type* (ColorBrewer [`harrower2003colorbrewer`]) — **none by circadian / melanopic
content.** No colormap rater, per-position profile, scored index, or generator on a melanopic
axis was found.

**C. Lighting-domain melanopic modulation (where the axis idea actually lives).** This is the
existential-risk field, and the axis idea *is* present here — but for lamps and display
hardware, not data-viz:
- **Metameric display tuning.** Allen et al. 2018 [`allen2018metamerism`] built a 5-primary VDU
  presenting metameric movies (matched colour + luminance) that vary melanopic irradiance — the
  closest prior art. It modulates a *display's* melanopic output for melatonin/alertness
  experiments; it is **not** a colormap tool, has no PU/CVD-constrained data-mapping, and rates
  no existing maps.
- **OS night-shift / blue-light filters.** Nagare, Plitnick & Figueiro 2019
  [`nagare2019nightshift`] show iPad Night Shift (spectral shift without dimming) does **not**
  significantly reduce melatonin suppression — a global framebuffer tint, data-blind. This both
  anchors the f.lux/Night-Shift comparison and *supports* Melanopy's honest-scope caveat
  (brightness is the dominant lever; a colour change alone is second-order).
- Human-centric/circadian lighting and melanopic-spectrum luminaires (incl. patents) ramp
  melanopic content over the day — again hardware, not visualization.

## Novelty-specific queries (artifact check)

Searches combining {melanopic, circadian, "blue light", melatonin} × {colormap, colour map,
palette, "data visualization", "scientific visualization"} returned **only** lighting metrology,
human-centric-lighting, and light-emitting-device/patent results — **no colormap rater, scored
index, per-position melanopic profile, or PU/CVD melanopic generator.**

## Novelty statement (for §10)

> We searched the melanopic-metrology, scientific-colormap, and circadian-lighting literatures.
> The melanopic axis is mature in lighting — α-opic metrology [`lucas2014melanopsin`;
> CIE S 026], metameric display tuning that varies melanopic output independent of appearance
> [`allen2018metamerism`], and night-shift filters [`nagare2019nightshift`] — and the colormap
> field is mature on perceptual uniformity and CVD-safety [`smith2015viridis`;
> `kovesi2015colourmaps`; `crameri2020colour`], with collections organized by structure, domain,
> or data type [`thyng2016cmocean`; `harrower2003colorbrewer`; `moreland2009diverging`]. We found
> **no precedent** for the specific contribution here: a melanopic *rater for colormaps*, a
> per-data-position melanopic *profile*, a *scored index* of existing scientific colormaps, or a
> perceptual-uniformity- and CVD-constrained *generator* parameterized by melanopic content.

## Limitations

A structured search across the obvious venues, not an exhaustive systematic review: English-only,
no patent-database sweep, no hand-search of lighting-conference proceedings (CIE, Experiencing
Light, LightSym). Adequate to support a "no precedent found" claim for a viz short paper; a full
review would be warranted only if a reviewer surfaces a near-miss.

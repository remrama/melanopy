# Limitations & honest scope

Melanopy's credibility *is* the contribution, so the caveats are front and centre rather than
buried.

## It rates chromaticity, not dose

The headline caveat: Melanopy reports a **colour property**, not a light **dose**, and never an
alertness effect. Actual circadian load is roughly

> screen luminance × fraction of screen filled × viewing distance × ambient light,

none of which a colormap fixes. If the goal is genuinely to stay alert, the dominant lever is
**room lighting**. The value here is measurability, a scored index, a uniformity-preserving
generator, and surfacing the axis.

## Display-primary dependence

The three coefficients assume a *representative* panel. White-LED-LCD, OLED, and wide-gamut
displays differ — especially in the blue primary. Melanopy ships several panel archetypes and
lets you plug in measured SPDs (`melanopy.spectra.coefficients_from_primaries`). S 026 validates
the *spectral weighting*; the *panel model* is orthogonal and still approximate. Reassuringly,
the **ranking is robust** across panels (ρ ≥ 0.99; see [the scored index](leaderboard.md)).

## The warm/cool spread asymmetry is fundamental

A perfectly pure (tight-spread) **protective** map is achievable; a perfectly pure **alerting** one
is not. Short-wavelength primaries are intrinsically low-luminance, so a light, saturated blue
does not exist — light cool colours must desaturate toward white. This is a property of the
axis ∩ the display gamut, not a tuning miss (cool-end M/P spread σ ≈ 0.42 vs warm-end σ ≈ 0.07).

## "CVD-recoverable", not "CVD-safe"

A shared monotone-lightness profile makes order **recoverable** under CVD; we verify that
numerically and say exactly that, rather than the stronger "safe."

## Physiological effect is second-order

Honestly, the dominant levers are screen brightness, UI background, and room light. Melanopy's
worth is (a) measurability, (b) the tool + index, (c) surfacing the axis, and (d) a modest
**non-interference** claim: let large fills *cooperate* with whatever circadian strategy the room
is already running.

## Prior-art scope

The novelty claim — porting the melanopic axis from lighting hardware to data-viz colormaps —
rests on a **structured related-work pass across three literatures** (metrology, colormap craft,
lighting), not a full PRISMA systematic review. The closest prior art is metameric *display*
tuning (Allen et al., 2018[^allen]); no precedent was found for a melanopic colormap rater, a
scored index, or a PU/CVD-constrained melanopic generator.

\[^allen\]: Allen, A. E. et al. (2018). *Exploiting metamerism to regulate the impact of a visual display on alertness and melatonin suppression independent of visual appearance.*

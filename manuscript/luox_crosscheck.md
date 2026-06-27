# luox / CIE S 026 cross-check

> External validation of melanopy's melanopic numbers against the CIE S 026 standard that the
> validated **luox** reference calculator [`spitschan2021luox`] implements. Conducted 2026-06-27.
> Reproduce with `uv run --with colour-science python luox_crosscheck.py` (colour-science supplies
> only the D65 SPD; it is not a melanopy dependency). The script prints the table below and writes
> `melanopy_spectra_for_luox.csv`, ready to upload to <https://luox.app>.

## Why this is a valid comparison

melanopy reduces a colour to `R(SPD) = ∫ SPD·s_mel / ∫ SPD·V`, using the vendored CIE S 026
melanopic action spectrum (peak-normalized) and CIE 1931 2° V(λ) — the *same* functions luox uses.
luox reports a melanopic **Daylight (D65) Efficacy Ratio (mel-DER)**, normalized so D65 = 1.000.
Because

    mel-DER(SPD) = R(SPD) / R(D65),

the 683 lm/W luminous-efficacy constant and the peak-normalizations cancel in the ratio, so
melanopy's numbers are directly comparable to luox's melanopic DER with no fitting factor.

## Result 1 — the D65 normalization constant (the definitive anchor)

The entire CIE S 026 melanopic system — and therefore luox — is pinned to one constant: the
melanopic ELR of D65 = **1.3262 mW/lm** (equivalently, melanopic EDI = melanopic irradiance /
0.0013262 lx). melanopy reproduces it from its own vendored spectra:

    mel-ELR(D65) = R(D65) / 683 = 0.905804 / 683 = 1.32621 mW/lm

— matching the CIE S 026 / luox value of **1.3262 mW/lm to five significant figures** (≈ 0.001 %).
This validates melanopy's spectral integration and normalization against the exact quantity luox is
built on.

## Result 2 — standard illuminants and display primaries

| spectrum | melanopy `R` | mel-DER | expectation |
|---|---|---|---|
| D65 | 0.9058 | 1.0000 | 1.000 (definition) |
| Illuminant E (equal-energy) | 0.8205 | 0.9058 | < 1, flat spectrum |
| Illuminant A (2856 K) | 0.4490 | 0.4957 | low (warm / incandescent) |
| representative primary R | 0.0031 | 0.0034 | ≈ 0 (red ≈ no melanopic drive) |
| representative primary G | 0.6555 | 0.7237 | moderate |
| representative primary B | 10.9681 | 12.1086 | high (blue dominates) |
| sRGB display white | 1.2614 | 1.3925 | > 1 (narrowband archetype, not D65-balanced) |

The three primary `R` values are exactly melanopy's baked coefficients
(`coeffs.PANELS["representative"]` = R 0.0031, G 0.6555, B 10.9681), so the rater and this spectral
computation are mutually consistent. The ordering A 0.50 (warm) < E 0.91 (flat) < D65 1.00 is the
expected physical pattern. By construction, `melanopic_ratio(colour) = mel-DER(colour) /
mel-DER(white)`.

## Live luox confirmation (one upload)

`melanopy_spectra_for_luox.csv` (column 1 = wavelength, then one column per spectrum above) uploads
directly to <https://luox.app>; its melanopic DER column should reproduce the table. A *live* luox
run was **not** performed in this session (no browser was connected); the CSV + script make it a
one-step reproduction.

## Scope

The melanopic action spectrum is the single CIE S 026 standard table that both tools use, so this
checks melanopy's *integration and normalization*, not an independent action spectrum. Result 1
(the D65-constant match) is the load-bearing check; the standard-illuminant DERs corroborate it.

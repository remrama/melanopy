# Validation

Two different claims need backing, and Melanopy backs both **numerically** (in the test suite)
rather than by assertion.

## 1. The spectral weighting — CIE S 026

The melanopic weighting is the real, standardized one: the **CIE S 026:2018** melanopic action
spectrum together with the **CIE 1931 2° V(λ)** photopic function, both vendored in
`src/melanopy/data/` (© CIE, CC BY-SA 4.0).

![CIE S 026 validation](assets/figures/s026_validation.png){ loading=lazy }

Swapping the prototype's analytic template for the validated S 026 spectrum:

- the melanopic response peaks at **490 nm**, as expected;
- display gray stays **1.000**;
- the leaderboard ranking is **essentially identical** — every map moved ≤ 0.035;
- the generator span is unchanged (0.29 → 1.73) and still monotonic.

The baked per-primary coefficients are regression-locked to this spectrum
(`tests/test_coeffs.py`), so the data and the numbers can't silently drift apart.

**External cross-check against luox.** The melanopic weighting is *borrowed* — so it had better
reproduce the standard. melanopy's spectral engine recovers the CIE S 026 D65 melanopic ELR
normalization constant — the quantity the validated [luox](https://luox.app) calculator is built
on — to five significant figures (1.32621 vs 1.3262 mW/lm), and returns the expected melanopic
daylight-efficacy ratios for the standard illuminants (D65 = 1.000 by definition, equal-energy =
0.906, Illuminant A = 0.496). Method and a luox-uploadable spectrum set are in the companion
[`luox_crosscheck.md`](https://github.com/remrama/melanopy/blob/main/manuscript/luox_crosscheck.md).

## 2. Perceptual uniformity and CVD-safety

The generator's structural claims are checked with `colorspacious` in
`tests/test_perceptual.py`:

- **Perceptual uniformity** — the CAM02-UCS lightness (J′) is strictly increasing along each
    Circadia map, and the CAM02-UCS step sizes are near-constant (coefficient of variation < 0.30).
- **CVD order-recoverability** — under simulated deuteranopia, protanopia, and tritanopia
    (Machado 2009, severity 100), the perceived lightness stays strictly monotonic, so the data
    order is still recoverable.

!!! quote "Wording, calibrated"

    A shared monotone-lightness profile keeps order **CVD-recoverable** (not the stronger
    "CVD-safe"), and perceptual uniformity and CVD-recoverability are **verified numerically**.
    We say exactly what the tests show — see [Limitations](limitations.md).

## Reproducing

```bash
uv run --extra dev pytest -q                   # the full suite, including the checks above
uv run --extra dev scripts/build_figures.py    # regenerate the figures on this page
```

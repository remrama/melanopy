# Scored index

Popular colormaps scored on the melanopic axis (display white = 1.0).

## `leaderboard.csv`

| column            | meaning                                                                          |
| ----------------- | -------------------------------------------------------------------------------- |
| `melanopic_ratio` | axis position; **< 1 protective** (warm), **> 1 alerting** (cool)                |
| `purity_sigma`    | luminance-weighted spread of per-position ratio; **lower = more circadian-pure** |
| `range_min/max`   | min/max per-position ratio over the (emitting) ramp                              |

Regenerate from the shipped package with `uv run scripts/build_leaderboard.py` (which calls
`melanopy.rate_colormap`). Scores use the representative-panel coefficients.

Key reads: warm/single-hue maps (Sodium, copper) are protective **and** circadian-pure;
the viridis family sits mid-axis but *smeared* (high σ — blue concentrated at the dark
end); cool maps reach the alerting end but most aren't perceptually uniform. Xenon fills
the perceptually-uniform, CVD-safe, alerting slot.

## `panel_robustness.csv`

Each map's M/P under every panel archetype in `melanopy.coeffs.PANELS` (`representative`,
`led_lcd`, `oled`, `wide_gamut`), plus its `band` (max − min across panels). Regenerate with
`uv run scripts/build_panel_robustness.py`.

Absolute M/P is panel-dependent — the blue coefficient ranges ≈8.8 (OLED) to ≈13.7 (wide-gamut
QD) — but the **ranking is not**: Spearman ρ ≥ 0.99 vs the representative panel, display white
stays exactly 1.0 on every panel, and the widest band is the saturated `cool` (≈0.32). So
*where* a map sits on the axis is robust to the display.

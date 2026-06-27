# Scored index

`leaderboard.csv` — popular colormaps scored on the melanopic axis (display white = 1.0).

| column | meaning |
|---|---|
| `melanopic_ratio` | axis position; **< 1 protective** (warm), **> 1 alerting** (cool) |
| `purity_sigma`    | luminance-weighted spread of per-position ratio; **lower = more circadian-pure** |
| `range_min/max`   | min/max per-position ratio over the (emitting) ramp |

Regenerate from the shipped package with `uv run scripts/build_leaderboard.py` (which calls
`melanopy.rate_colormap`). Scores use the representative-panel coefficients; absolute values
shift with a monitor's measured primary SPDs, but the ranking is robust.

Key reads: warm/single-hue maps (Ember, copper) are protective **and** circadian-pure;
the viridis family sits mid-axis but *smeared* (high σ — blue concentrated at the dark
end); cool maps reach the alerting end but most aren't perceptually uniform. Glacier fills
the perceptually-uniform, CVD-safe, alerting slot.

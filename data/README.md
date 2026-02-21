# Data README

## Files
- `probability_sweep.csv`: Monte Carlo sweep output for tennis simulation metrics.

## Current sweep in this folder
- Point-win probability range: `0.4500` to `0.6000`
- Step size: `0.0020`
- Rows: one row per probability value

## Column definitions
- `point_win_probability`: Baseline probability that Player 1 wins any point.
- `expected_game_win_rate`: Estimated probability Player 1 wins a game.
- `expected_set_win_rate`: Estimated probability Player 1 wins a set.
- `expected_match_win_rate`: Estimated probability Player 1 wins a match.
- `expected_p1_break_points_earned_per_match`: Average break points earned by Player 1 per match.
- `expected_p1_break_points_converted_per_match`: Average break points converted by Player 1 per match.
- `expected_p1_break_points_faced_per_match`: Average break points faced by Player 1 per match.
- `expected_p1_break_points_saved_per_match`: Average break points saved by Player 1 per match.
- `p1_break_point_conversion_rate`: `converted / earned` across all simulated matches.
- `p1_break_point_save_rate`: `saved / faced` across all simulated matches.

## Regenerate
Run from repository root:

```powershell
python src/run_probability_sweep.py --start 0.45 --stop 0.60 --step 0.002 --output data/probability_sweep.csv
```

Optional quality/runtime controls:
- `--games`
- `--sets`
- `--matches`
- `--seed`


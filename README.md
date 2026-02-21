# tennis_simulation
Analysis of tennis point win percentages and their effect on match outcomes.

## Point-by-point tennis simulator

This project includes a Python simulation of tennis matches with:
- Point-level randomness using a configurable point win probability
- Full game logic (win by 2 after deuce)
- Full set logic (first to 6 by 2, with 6-6 tiebreak)
- Best-of-3 or best-of-5 match logic
- Monte Carlo mode to estimate match win rates

## Run

```powershell
python src/run_probability_sweep.py
```

## Configure

Core config now lives in `src/tennis_simulation/config.py`:
- `p1_point_win_probability`: probability that Player 1 wins any point (independent points)
- `best_of_sets`: `3` or `5`
- `games_to_win_set`: default `6`
- `set_win_margin`: default `2`
- `tiebreak_at`: default `6` (triggers tiebreak at 6-6)
- `tiebreak_points_to_win`: default `7`
- `tiebreak_win_margin`: default `2`
- `streak`: streakiness controls (`enabled`, `intensity`, `decay`, `momentum_step`)
- `clutch`: clutch controls (`enabled`, `primary_boost`, `secondary_boost`)

The engine and extension points are split into:
- `src/tennis_simulation/engine.py`: match/set/game simulation flow
- `src/tennis_simulation/state.py`: point context model
- `src/tennis_simulation/events.py`: pressure-point classification
- `src/tennis_simulation/policies/`: probability policy interface and implementations
- `src/simulation.py`: compatibility exports

The sweep script defaults to probabilities `0.25` to `0.75` in steps of `0.05`, and writes:
- `data/probability_sweep.csv`

The CSV contains:
- point win probability
- expected game win rate
- expected set win rate
- expected match win rate
- expected P1 break points earned per match
- expected P1 break points converted per match
- expected P1 break points faced per match
- expected P1 break points saved per match
- P1 break point conversion rate
- P1 break point save rate

Example with custom sensitivity:

```powershell
python src/run_probability_sweep.py --start 0.30 --stop 0.70 --step 0.02
```

Example enabling streakiness and clutch:

```powershell
python src/run_probability_sweep.py --enable-streak --streak-intensity 0.03 --enable-clutch --clutch-primary-boost 0.02 --clutch-secondary-boost 0.01
```

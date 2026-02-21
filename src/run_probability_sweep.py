import argparse
import csv
from pathlib import Path

from simulation import (
    ClutchConfig,
    MatchConfig,
    StreakConfig,
    estimate_game_win_rate,
    estimate_match_profile,
    estimate_set_win_rate,
)


def frange(start: float, stop: float, step: float) -> list[float]:
    values = []
    current = start
    while current <= stop + 1e-12:
        values.append(round(current, 4))
        current += step
    return values


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Sweep point-win probabilities and estimate game/set/match win rates."
        )
    )
    parser.add_argument("--start", type=float, default=0.25)
    parser.add_argument("--stop", type=float, default=0.75)
    parser.add_argument("--step", type=float, default=0.05)
    parser.add_argument("--games", type=int, default=50000)
    parser.add_argument("--sets", type=int, default=30000)
    parser.add_argument("--matches", type=int, default=20000)
    parser.add_argument("--best-of-sets", type=int, default=3, choices=[3, 5])
    parser.add_argument("--enable-streak", action="store_true")
    parser.add_argument("--streak-intensity", type=float, default=0.0)
    parser.add_argument("--streak-decay", type=float, default=0.9)
    parser.add_argument("--streak-momentum-step", type=float, default=0.25)
    parser.add_argument("--enable-clutch", action="store_true")
    parser.add_argument("--clutch-primary-boost", type=float, default=0.0)
    parser.add_argument("--clutch-secondary-boost", type=float, default=0.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data") / "probability_sweep.csv",
    )
    parser.add_argument("--seed", type=int, default=12345)
    args = parser.parse_args()

    probabilities = frange(args.start, args.stop, args.step)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "point_win_probability",
                "expected_game_win_rate",
                "expected_set_win_rate",
                "expected_match_win_rate",
                "expected_p1_break_points_earned_per_match",
                "expected_p1_break_points_converted_per_match",
                "expected_p1_break_points_faced_per_match",
                "expected_p1_break_points_saved_per_match",
                "p1_break_point_conversion_rate",
                "p1_break_point_save_rate",
            ]
        )

        for i, probability in enumerate(probabilities):
            streak = StreakConfig(
                enabled=args.enable_streak,
                intensity=args.streak_intensity,
                decay=args.streak_decay,
                momentum_step=args.streak_momentum_step,
            )
            clutch = ClutchConfig(
                enabled=args.enable_clutch,
                primary_boost=args.clutch_primary_boost,
                secondary_boost=args.clutch_secondary_boost,
            )
            config = MatchConfig(
                best_of_sets=args.best_of_sets,
                p1_point_win_probability=probability,
                streak=streak,
                clutch=clutch,
            )
            base_seed = args.seed + i * 1000
            game_win_rate = estimate_game_win_rate(
                p1_point_win_probability=probability,
                n_games=args.games,
                seed=base_seed,
                config=config,
            )
            set_win_rate = estimate_set_win_rate(
                config=config,
                n_sets=args.sets,
                seed=base_seed + 1,
            )
            match_win_rate, break_point_metrics = estimate_match_profile(
                config=config,
                n_matches=args.matches,
                seed=base_seed + 2,
            )

            writer.writerow(
                [
                    f"{probability:.4f}",
                    f"{game_win_rate:.6f}",
                    f"{set_win_rate:.6f}",
                    f"{match_win_rate:.6f}",
                    f"{break_point_metrics.p1_break_points_earned_per_match:.6f}",
                    f"{break_point_metrics.p1_break_points_converted_per_match:.6f}",
                    f"{break_point_metrics.p1_break_points_faced_per_match:.6f}",
                    f"{break_point_metrics.p1_break_points_saved_per_match:.6f}",
                    f"{break_point_metrics.p1_break_point_conversion_rate:.6f}",
                    f"{break_point_metrics.p1_break_point_save_rate:.6f}",
                ]
            )

    print(f"Wrote {len(probabilities)} rows to {args.output}")


if __name__ == "__main__":
    main()

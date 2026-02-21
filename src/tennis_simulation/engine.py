import random
from dataclasses import dataclass
from typing import Tuple

from .config import MatchConfig
from .events import build_point_context
from .policies import IndependentPolicy, ProbabilityPolicy, build_policy


@dataclass
class MatchResult:
    p1_sets: int
    p2_sets: int
    p1_games_current_set: int
    p2_games_current_set: int
    winner: str


@dataclass
class BreakPointStats:
    p1_break_points_earned: int = 0
    p1_break_points_converted: int = 0
    p1_break_points_faced: int = 0
    p1_break_points_saved: int = 0

    def conversion_rate(self) -> float:
        if self.p1_break_points_earned == 0:
            return 0.0
        return self.p1_break_points_converted / self.p1_break_points_earned

    def save_rate(self) -> float:
        if self.p1_break_points_faced == 0:
            return 0.0
        return self.p1_break_points_saved / self.p1_break_points_faced

    def add(self, other: "BreakPointStats") -> None:
        self.p1_break_points_earned += other.p1_break_points_earned
        self.p1_break_points_converted += other.p1_break_points_converted
        self.p1_break_points_faced += other.p1_break_points_faced
        self.p1_break_points_saved += other.p1_break_points_saved


@dataclass
class BreakPointMetrics:
    p1_break_points_earned_per_match: float
    p1_break_points_converted_per_match: float
    p1_break_points_faced_per_match: float
    p1_break_points_saved_per_match: float
    p1_break_point_conversion_rate: float
    p1_break_point_save_rate: float


def _validate_match_config(config: MatchConfig) -> None:
    if not 0.0 <= config.p1_point_win_probability <= 1.0:
        raise ValueError("p1_point_win_probability must be between 0 and 1.")
    if config.best_of_sets not in (3, 5):
        raise ValueError("best_of_sets must be 3 or 5.")


def _play_point(policy: ProbabilityPolicy, context, rng: random.Random) -> bool:
    p1_prob = policy.point_probability(context)
    p1_won = rng.random() < p1_prob
    policy.on_point_end(context, p1_won)
    return p1_won


def _simulate_standard_game(
    policy: ProbabilityPolicy,
    config: MatchConfig,
    rng: random.Random,
    p1_sets: int,
    p2_sets: int,
    p1_games: int,
    p2_games: int,
    p1_serving: bool,
    break_point_stats: BreakPointStats | None = None,
) -> int:
    p1_points = 0
    p2_points = 0
    while True:
        context = build_point_context(
            config=config,
            p1_sets=p1_sets,
            p2_sets=p2_sets,
            p1_games=p1_games,
            p2_games=p2_games,
            p1_points=p1_points,
            p2_points=p2_points,
            p1_serving=p1_serving,
            in_tiebreak=False,
        )
        p1_won_point = _play_point(policy, context, rng)

        if break_point_stats is not None and context.is_break_point:
            if p1_serving:
                break_point_stats.p1_break_points_faced += 1
                if p1_won_point:
                    break_point_stats.p1_break_points_saved += 1
            else:
                break_point_stats.p1_break_points_earned += 1
                if p1_won_point:
                    break_point_stats.p1_break_points_converted += 1

        if p1_won_point:
            p1_points += 1
        else:
            p2_points += 1

        if p1_points >= 4 and p1_points - p2_points >= 2:
            return 1
        if p2_points >= 4 and p2_points - p1_points >= 2:
            return 2


def _simulate_tiebreak(
    policy: ProbabilityPolicy,
    config: MatchConfig,
    rng: random.Random,
    p1_sets: int,
    p2_sets: int,
    p1_games: int,
    p2_games: int,
    p1_serving: bool,
) -> int:
    p1_points = 0
    p2_points = 0
    while True:
        context = build_point_context(
            config=config,
            p1_sets=p1_sets,
            p2_sets=p2_sets,
            p1_games=p1_games,
            p2_games=p2_games,
            p1_points=p1_points,
            p2_points=p2_points,
            p1_serving=p1_serving,
            in_tiebreak=True,
        )
        if _play_point(policy, context, rng):
            p1_points += 1
        else:
            p2_points += 1

        if (
            p1_points >= config.tiebreak_points_to_win
            and p1_points - p2_points >= config.tiebreak_win_margin
        ):
            return 1
        if (
            p2_points >= config.tiebreak_points_to_win
            and p2_points - p1_points >= config.tiebreak_win_margin
        ):
            return 2


def simulate_game(
    p1_point_win_probability: float,
    rng: random.Random,
) -> int:
    config = MatchConfig(p1_point_win_probability=p1_point_win_probability)
    policy = IndependentPolicy(p1_point_win_probability)
    return _simulate_standard_game(
        policy=policy,
        config=config,
        rng=rng,
        p1_sets=0,
        p2_sets=0,
        p1_games=0,
        p2_games=0,
        p1_serving=True,
    )


def simulate_set(
    config: MatchConfig,
    rng: random.Random,
    policy: ProbabilityPolicy | None = None,
    p1_sets: int = 0,
    p2_sets: int = 0,
    p1_serving_first_game: bool = True,
    break_point_stats: BreakPointStats | None = None,
) -> Tuple[int, int, int, bool]:
    _validate_match_config(config)
    active_policy = policy if policy is not None else build_policy(config)

    p1_games = 0
    p2_games = 0
    p1_serving = p1_serving_first_game

    while True:
        if p1_games == config.tiebreak_at and p2_games == config.tiebreak_at:
            tiebreak_winner = _simulate_tiebreak(
                policy=active_policy,
                config=config,
                rng=rng,
                p1_sets=p1_sets,
                p2_sets=p2_sets,
                p1_games=p1_games,
                p2_games=p2_games,
                p1_serving=p1_serving,
            )
            if tiebreak_winner == 1:
                p1_games += 1
            else:
                p2_games += 1
            p1_serving = not p1_serving
            break

        game_winner = _simulate_standard_game(
            policy=active_policy,
            config=config,
            rng=rng,
            p1_sets=p1_sets,
            p2_sets=p2_sets,
            p1_games=p1_games,
            p2_games=p2_games,
            p1_serving=p1_serving,
            break_point_stats=break_point_stats,
        )
        if game_winner == 1:
            p1_games += 1
        else:
            p2_games += 1

        p1_serving = not p1_serving

        if (
            p1_games >= config.games_to_win_set
            and p1_games - p2_games >= config.set_win_margin
        ):
            break
        if (
            p2_games >= config.games_to_win_set
            and p2_games - p1_games >= config.set_win_margin
        ):
            break

    set_winner = 1 if p1_games > p2_games else 2
    return set_winner, p1_games, p2_games, p1_serving


def simulate_match(
    config: MatchConfig,
    seed: int | None = None,
    policy: ProbabilityPolicy | None = None,
    break_point_stats: BreakPointStats | None = None,
) -> MatchResult:
    _validate_match_config(config)
    rng = random.Random(seed)
    active_policy = policy if policy is not None else build_policy(config)
    active_policy.reset_match()

    sets_needed = config.best_of_sets // 2 + 1
    p1_sets = 0
    p2_sets = 0
    p1_games = 0
    p2_games = 0
    p1_serving = rng.random() < 0.5

    while p1_sets < sets_needed and p2_sets < sets_needed:
        set_winner, p1_games, p2_games, p1_serving = simulate_set(
            config=config,
            rng=rng,
            policy=active_policy,
            p1_sets=p1_sets,
            p2_sets=p2_sets,
            p1_serving_first_game=p1_serving,
            break_point_stats=break_point_stats,
        )
        if set_winner == 1:
            p1_sets += 1
        else:
            p2_sets += 1

    winner = "Player 1" if p1_sets > p2_sets else "Player 2"
    return MatchResult(
        p1_sets=p1_sets,
        p2_sets=p2_sets,
        p1_games_current_set=p1_games,
        p2_games_current_set=p2_games,
        winner=winner,
    )


def run_monte_carlo(
    n_matches: int,
    config: MatchConfig,
    seed: int | None = None,
) -> tuple[int, int]:
    if n_matches <= 0:
        raise ValueError("n_matches must be greater than 0.")

    _validate_match_config(config)
    rng = random.Random(seed)
    p1_wins = 0
    p2_wins = 0

    for _ in range(n_matches):
        match_seed = rng.randint(0, 10**9)
        result = simulate_match(config=config, seed=match_seed)
        if result.winner == "Player 1":
            p1_wins += 1
        else:
            p2_wins += 1

    return p1_wins, p2_wins


def _run_monte_carlo_with_break_point_stats(
    n_matches: int,
    config: MatchConfig,
    seed: int | None = None,
) -> tuple[int, int, BreakPointStats]:
    if n_matches <= 0:
        raise ValueError("n_matches must be greater than 0.")

    _validate_match_config(config)
    rng = random.Random(seed)
    p1_wins = 0
    p2_wins = 0
    aggregate_stats = BreakPointStats()

    for _ in range(n_matches):
        match_seed = rng.randint(0, 10**9)
        match_break_point_stats = BreakPointStats()
        result = simulate_match(
            config=config,
            seed=match_seed,
            break_point_stats=match_break_point_stats,
        )
        aggregate_stats.add(match_break_point_stats)
        if result.winner == "Player 1":
            p1_wins += 1
        else:
            p2_wins += 1

    return p1_wins, p2_wins, aggregate_stats


def estimate_game_win_rate(
    p1_point_win_probability: float,
    n_games: int,
    seed: int | None = None,
    config: MatchConfig | None = None,
) -> float:
    if n_games <= 0:
        raise ValueError("n_games must be greater than 0.")
    if not 0.0 <= p1_point_win_probability <= 1.0:
        raise ValueError("p1_point_win_probability must be between 0 and 1.")

    active_config = (
        config
        if config is not None
        else MatchConfig(p1_point_win_probability=p1_point_win_probability)
    )
    _validate_match_config(active_config)
    rng = random.Random(seed)
    p1_wins = 0
    for _ in range(n_games):
        policy = build_policy(active_config)
        policy.reset_match()
        if (
            _simulate_standard_game(
                policy=policy,
                config=active_config,
                rng=rng,
                p1_sets=0,
                p2_sets=0,
                p1_games=0,
                p2_games=0,
                p1_serving=True,
            )
            == 1
        ):
            p1_wins += 1
    return p1_wins / n_games


def estimate_set_win_rate(
    config: MatchConfig, n_sets: int, seed: int | None = None
) -> float:
    if n_sets <= 0:
        raise ValueError("n_sets must be greater than 0.")

    _validate_match_config(config)
    rng = random.Random(seed)
    p1_wins = 0
    for _ in range(n_sets):
        policy = build_policy(config)
        policy.reset_match()
        p1_serving = rng.random() < 0.5
        set_winner, _, _, _ = simulate_set(
            config=config,
            rng=rng,
            policy=policy,
            p1_sets=0,
            p2_sets=0,
            p1_serving_first_game=p1_serving,
        )
        if set_winner == 1:
            p1_wins += 1
    return p1_wins / n_sets


def estimate_match_win_rate(
    config: MatchConfig, n_matches: int, seed: int | None = None
) -> float:
    p1_wins, _ = run_monte_carlo(n_matches=n_matches, config=config, seed=seed)
    return p1_wins / n_matches


def estimate_break_point_metrics(
    config: MatchConfig, n_matches: int, seed: int | None = None
) -> BreakPointMetrics:
    _, _, stats = _run_monte_carlo_with_break_point_stats(
        n_matches=n_matches,
        config=config,
        seed=seed,
    )
    return BreakPointMetrics(
        p1_break_points_earned_per_match=stats.p1_break_points_earned / n_matches,
        p1_break_points_converted_per_match=stats.p1_break_points_converted / n_matches,
        p1_break_points_faced_per_match=stats.p1_break_points_faced / n_matches,
        p1_break_points_saved_per_match=stats.p1_break_points_saved / n_matches,
        p1_break_point_conversion_rate=stats.conversion_rate(),
        p1_break_point_save_rate=stats.save_rate(),
    )


def estimate_match_profile(
    config: MatchConfig, n_matches: int, seed: int | None = None
) -> tuple[float, BreakPointMetrics]:
    p1_wins, _, stats = _run_monte_carlo_with_break_point_stats(
        n_matches=n_matches,
        config=config,
        seed=seed,
    )
    match_win_rate = p1_wins / n_matches
    metrics = BreakPointMetrics(
        p1_break_points_earned_per_match=stats.p1_break_points_earned / n_matches,
        p1_break_points_converted_per_match=stats.p1_break_points_converted / n_matches,
        p1_break_points_faced_per_match=stats.p1_break_points_faced / n_matches,
        p1_break_points_saved_per_match=stats.p1_break_points_saved / n_matches,
        p1_break_point_conversion_rate=stats.conversion_rate(),
        p1_break_point_save_rate=stats.save_rate(),
    )
    return match_win_rate, metrics

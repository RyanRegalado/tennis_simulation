from dataclasses import dataclass, field


@dataclass(frozen=True)
class StreakConfig:
    enabled: bool = False
    intensity: float = 0.0
    decay: float = 0.9
    momentum_step: float = 0.25


@dataclass(frozen=True)
class ClutchConfig:
    enabled: bool = False
    primary_boost: float = 0.0
    secondary_boost: float = 0.0


@dataclass(frozen=True)
class MatchConfig:
    best_of_sets: int = 3
    games_to_win_set: int = 6
    set_win_margin: int = 2
    tiebreak_at: int = 6
    tiebreak_points_to_win: int = 7
    tiebreak_win_margin: int = 2
    p1_point_win_probability: float = 0.55
    streak: StreakConfig = field(default_factory=StreakConfig)
    clutch: ClutchConfig = field(default_factory=ClutchConfig)

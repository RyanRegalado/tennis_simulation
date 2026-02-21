from dataclasses import dataclass


@dataclass
class MatchState:
    p1_sets: int = 0
    p2_sets: int = 0
    p1_games: int = 0
    p2_games: int = 0


@dataclass
class PointContext:
    p1_sets: int
    p2_sets: int
    p1_games: int
    p2_games: int
    p1_points: int
    p2_points: int
    p1_serving: bool
    in_tiebreak: bool
    is_primary_clutch: bool
    is_secondary_clutch: bool
    is_break_point: bool
    is_set_point: bool
    is_match_point: bool

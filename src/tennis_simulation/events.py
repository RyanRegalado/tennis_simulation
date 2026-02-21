from .config import MatchConfig
from .state import PointContext


def _would_win_standard_game(p1_points: int, p2_points: int, p1_wins_point: bool) -> bool:
    next_p1 = p1_points + (1 if p1_wins_point else 0)
    next_p2 = p2_points + (0 if p1_wins_point else 1)
    if p1_wins_point:
        return next_p1 >= 4 and next_p1 - next_p2 >= 2
    return next_p2 >= 4 and next_p2 - next_p1 >= 2


def _would_win_tiebreak(
    p1_points: int,
    p2_points: int,
    p1_wins_point: bool,
    points_to_win: int,
    win_margin: int,
) -> bool:
    next_p1 = p1_points + (1 if p1_wins_point else 0)
    next_p2 = p2_points + (0 if p1_wins_point else 1)
    if p1_wins_point:
        return next_p1 >= points_to_win and next_p1 - next_p2 >= win_margin
    return next_p2 >= points_to_win and next_p2 - next_p1 >= win_margin


def _would_win_set(
    config: MatchConfig,
    p1_games: int,
    p2_games: int,
    p1_wins_game: bool,
    in_tiebreak: bool,
) -> bool:
    next_p1 = p1_games + (1 if p1_wins_game else 0)
    next_p2 = p2_games + (0 if p1_wins_game else 1)
    if in_tiebreak:
        return p1_wins_game
    if p1_wins_game:
        return next_p1 >= config.games_to_win_set and next_p1 - next_p2 >= config.set_win_margin
    return next_p2 >= config.games_to_win_set and next_p2 - next_p1 >= config.set_win_margin


def build_point_context(
    config: MatchConfig,
    p1_sets: int,
    p2_sets: int,
    p1_games: int,
    p2_games: int,
    p1_points: int,
    p2_points: int,
    p1_serving: bool,
    in_tiebreak: bool,
) -> PointContext:
    sets_needed = config.best_of_sets // 2 + 1

    if in_tiebreak:
        p1_game_point = _would_win_tiebreak(
            p1_points,
            p2_points,
            True,
            config.tiebreak_points_to_win,
            config.tiebreak_win_margin,
        )
        p2_game_point = _would_win_tiebreak(
            p1_points,
            p2_points,
            False,
            config.tiebreak_points_to_win,
            config.tiebreak_win_margin,
        )
    else:
        p1_game_point = _would_win_standard_game(p1_points, p2_points, True)
        p2_game_point = _would_win_standard_game(p1_points, p2_points, False)

    p1_set_point = _would_win_set(config, p1_games, p2_games, True, in_tiebreak and p1_game_point)
    p2_set_point = _would_win_set(config, p1_games, p2_games, False, in_tiebreak and p2_game_point)

    p1_match_point = p1_set_point and (p1_sets + 1 == sets_needed)
    p2_match_point = p2_set_point and (p2_sets + 1 == sets_needed)

    is_break_point = (not in_tiebreak) and (
        (p1_game_point and not p1_serving) or (p2_game_point and p1_serving)
    )
    is_set_point = p1_set_point or p2_set_point
    is_match_point = p1_match_point or p2_match_point
    is_primary_clutch = is_break_point or is_set_point or is_match_point

    # Secondary clutch situations are common pressure states outside official break/set/match points.
    # This definition can be replaced with a custom classifier later.
    if p1_serving:
        server_points, returner_points = p1_points, p2_points
    else:
        server_points, returner_points = p2_points, p1_points
    is_secondary_clutch = (
        (server_points == 0 and returner_points == 2)  # love-30
        or (server_points >= 2 and returner_points >= 2 and server_points == returner_points)  # 30-30/deuce
    ) and not is_primary_clutch

    return PointContext(
        p1_sets=p1_sets,
        p2_sets=p2_sets,
        p1_games=p1_games,
        p2_games=p2_games,
        p1_points=p1_points,
        p2_points=p2_points,
        p1_serving=p1_serving,
        in_tiebreak=in_tiebreak,
        is_primary_clutch=is_primary_clutch,
        is_secondary_clutch=is_secondary_clutch,
        is_break_point=is_break_point,
        is_set_point=is_set_point,
        is_match_point=is_match_point,
    )

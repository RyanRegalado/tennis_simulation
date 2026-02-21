from ..config import MatchConfig
from .base import ProbabilityPolicy
from .clutch import ClutchPolicy
from .independent import IndependentPolicy
from .streakiness import StreakinessPolicy


def build_policy(config: MatchConfig) -> ProbabilityPolicy:
    policy: ProbabilityPolicy = IndependentPolicy(config.p1_point_win_probability)
    if config.streak.enabled:
        policy = StreakinessPolicy(policy, config.streak)
    if config.clutch.enabled:
        policy = ClutchPolicy(policy, config.clutch)
    return policy

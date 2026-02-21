from ..config import ClutchConfig
from ..state import PointContext
from .base import ProbabilityPolicy, clamp_probability


class ClutchPolicy(ProbabilityPolicy):
    def __init__(self, inner: ProbabilityPolicy, config: ClutchConfig) -> None:
        self.inner = inner
        self.config = config

    def reset_match(self) -> None:
        self.inner.reset_match()

    def point_probability(self, context: PointContext) -> float:
        probability = self.inner.point_probability(context)
        if context.is_primary_clutch:
            probability += self.config.primary_boost
        elif context.is_secondary_clutch:
            probability += self.config.secondary_boost
        return clamp_probability(probability)

    def on_point_end(self, context: PointContext, p1_won_point: bool) -> None:
        self.inner.on_point_end(context, p1_won_point)

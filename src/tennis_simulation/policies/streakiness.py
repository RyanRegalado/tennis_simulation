from ..config import StreakConfig
from ..state import PointContext
from .base import ProbabilityPolicy, clamp_probability


class StreakinessPolicy(ProbabilityPolicy):
    def __init__(self, inner: ProbabilityPolicy, config: StreakConfig) -> None:
        self.inner = inner
        self.config = config
        self.momentum = 0.0

    def reset_match(self) -> None:
        self.momentum = 0.0
        self.inner.reset_match()

    def point_probability(self, context: PointContext) -> float:
        base = self.inner.point_probability(context)
        adjustment = self.config.intensity * self.momentum
        return clamp_probability(base + adjustment)

    def on_point_end(self, context: PointContext, p1_won_point: bool) -> None:
        direction = 1.0 if p1_won_point else -1.0
        self.momentum = (self.momentum * self.config.decay) + (
            direction * self.config.momentum_step
        )
        self.momentum = max(-1.0, min(1.0, self.momentum))
        self.inner.on_point_end(context, p1_won_point)

from ..state import PointContext
from .base import ProbabilityPolicy, clamp_probability


class IndependentPolicy(ProbabilityPolicy):
    def __init__(self, base_probability: float) -> None:
        self.base_probability = clamp_probability(base_probability)

    def point_probability(self, context: PointContext) -> float:
        return self.base_probability

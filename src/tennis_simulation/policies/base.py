from abc import ABC, abstractmethod

from ..state import PointContext


def clamp_probability(value: float) -> float:
    return max(0.0, min(1.0, value))


class ProbabilityPolicy(ABC):
    @abstractmethod
    def point_probability(self, context: PointContext) -> float:
        """Return P(Player 1 wins next point) for this context."""

    def on_point_end(self, context: PointContext, p1_won_point: bool) -> None:
        """Optional hook for stateful policies (e.g., momentum)."""

    def reset_match(self) -> None:
        """Reset internal policy state before a new match."""

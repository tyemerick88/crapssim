from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from .dice import Dice
from .point import Point


class Rules(Protocol):
    """Protocol for game-rule variants used by the table engine."""

    def point_numbers(self) -> list[int]:
        ...

    def come_out_winners(self) -> list[int]:
        ...

    def come_out_losers(self) -> list[int]:
        ...

    def come_out_pushers(self) -> list[int]:
        ...

    def point_winners(self, point: int | None) -> list[int]:
        ...

    def point_losers(self, point: int | None) -> list[int]:
        ...

    def point_pushers(self, point: int | None) -> list[int]:
        ...

    def should_set_point(self, point: Point, dice: Dice) -> bool:
        ...

    def should_reset_shooter(self, point: Point, dice: Dice) -> bool:
        ...


class BaseRules(ABC):
    """Shared default behaviors for craps rule variants."""

    def point_numbers(self) -> list[int]:
        return []

    def come_out_pushers(self) -> list[int]:
        return []

    def point_winners(self, point: int | None) -> list[int]:
        if point is None:
            return []
        return [point]

    def point_losers(self, point: int | None) -> list[int]:
        return [7]

    def point_pushers(self, point: int | None) -> list[int]:
        return []

    def should_set_point(self, point: Point, dice: Dice) -> bool:
        return point.status == "Off" and dice.total in self.point_numbers()

    def should_reset_shooter(self, point: Point, dice: Dice) -> bool:
        return point.status == "On" and dice.total == 7


class ClassicRules(BaseRules):
    """Traditional craps rules."""

    def point_numbers(self) -> list[int]:
        return [4, 5, 6, 8, 9, 10]

    def come_out_winners(self) -> list[int]:
        return [7, 11]

    def come_out_losers(self) -> list[int]:
        return [2, 3, 12]


class CraplessRules(BaseRules):
    """Crapless craps rules.

    In this variant, 2, 3, 11 and 12 are treated as points rather than immediate losses
    for the pass line and come family bets.
    """

    def point_numbers(self) -> list[int]:
        return [2, 3, 4, 5, 6, 8, 9, 10, 11, 12]

    def come_out_winners(self) -> list[int]:
        return [7]

    def come_out_losers(self) -> list[int]:
        return []

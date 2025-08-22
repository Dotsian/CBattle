from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Type

from ballsdex.core.models import BallInstance, Player

from .customs.base import BaseEffect

if TYPE_CHECKING:
    from discord import Member, User

    from .components import BattleAcceptView


@dataclass
class BattleBall:
    """
    Stores a ball instance and keeps track of their health.
    """

    model: BallInstance
    health: int

    effects: list[BaseEffect] = field(default_factory=list)

    @classmethod
    def from_ballinstance(cls, ballinstance: BallInstance):
        return cls(model=ballinstance, health=ballinstance.health)

    @property
    def damage(self) -> int:
        return self.model.attack

    def apply_effect(self, effect: Type[BaseEffect], rounds: int):
        self.effects.append(effect(self, rounds))


@dataclass
class BattlePlayer:
    """
    Stores the deck of a player and their model.
    """

    model: Player
    user: User | Member
    balls: list[BattleBall] = field(default_factory=list)


@dataclass
class BattleState:
    """
    Stores both `BattlePlayer` instances and other additional information for a battle.
    """

    player1: BattlePlayer
    player2: BattlePlayer

    turn: int = 0
    started: bool = False
    accepted: bool = False
    accept_view: BattleAcceptView | None = None

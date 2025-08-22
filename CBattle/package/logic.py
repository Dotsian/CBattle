from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Type

from ballsdex.core.models import BallInstance, Player

from .base import BaseEffect

# from .config import max_deck_size

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

    # @property
    # def damage(self) -> int:
    #     base = model.attack * random.uniform(0.5, 1)
    #     is_super = random.random() < 0.25
    #     if is_super:
    #         return int(base * 1.5), True
    #     return int(base), False

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

    turns: int = 0
    started: bool = False
    accepted: bool = False
    winner: str = ""
    accept_view: BattleAcceptView | None = None
    # max_deck_size: int = max_deck_size

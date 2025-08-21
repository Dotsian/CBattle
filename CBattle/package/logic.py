from dataclasses import dataclass, field

from ballsdex.core.models import BallInstance, Player

from .customs.base import BaseEffect


@dataclass
class BattleBall:
    """
    Stores a ball instance and keeps track of their health.
    """

    model: BallInstance
    health: int

    effect: BaseEffect | None = None

    @property
    def damage(self) -> int:
        return self.model.attack

    def apply_effect(self, effect: BaseEffect, rounds: int):
        self.effect = effect(self, rounds)  # type: ignore


@dataclass
class BattlePlayer:
    """
    Stores the deck of a player and their model.
    """

    model: Player
    balls: list[BattleBall] = field(default_factory=list)


@dataclass
class Battle:
    """
    Stores both `BattlePlayer` instances and other additional information for a battle.
    """

    player1: BattlePlayer
    player2: BattlePlayer

    turn: int = 0

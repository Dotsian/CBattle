from dataclasses import dataclass, field

from ballsdex.core.models import BallInstance, Player


@dataclass
class BattleBall:
    """
    Stores a ball instance and keeps track of their health.
    """

    model: BallInstance
    health: int


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

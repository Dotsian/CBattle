from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Type

from ballsdex.core.models import BallInstance, Player

from .base import BaseEffect
from .config import config

if TYPE_CHECKING:
    from discord import Member, TextChannel, User

    from .components import BattleAcceptView, TurnView


def format_random(msg_list, **kwargs):
    return random.choice(msg_list).format(**kwargs)


@dataclass
class BattleBall:
    """
    Stores a ball instance and keeps track of their health.
    """

    model: BallInstance
    owner: BattlePlayer

    health: int
    attack: int

    evasion: float = 0.25
    crit_chance: float = 0.2
    dead: bool = False

    effects: set[BaseEffect] = field(default_factory=set)

    @classmethod
    def from_ballinstance(cls, ballinstance: BallInstance, owner: BattlePlayer):
        return cls(model=ballinstance, health=ballinstance.health, attack=ballinstance.attack, owner=owner)

    def damage(self, amount: int) -> bool:
        """Damage a BattleBall. If the damage kills the ball, returns true, otherwise returns false"""
        self.health -= amount
        if self.health <= 0:
            self.dead = True
            return True
        return False

    @property
    def name(self) -> str:
        return self.model.countryball.country

    def apply_effect(self, effect: Type[BaseEffect], rounds: int):
        self.effects.add(effect(self, rounds))

    def round_passed(self, round_number):
        for effect in self.effects:
            effect.round_passed(round_number)

    def attack_target(self, target: BattleBall) -> str:
        if random.random() < target.evasion:
            return random.choice(config.dodge_messages).format(
                a_owner=self.owner, a_name=self.name, d_owner=target.owner, d_name=target.name
            )

        damage = int(self.attack * random.uniform(0.6, 1.2))

        crit = False
        if random.random() < self.crit_chance:
            crit = True
            damage *= 2

        if target.damage(damage):
            response = random.choice(config.defeat_messages).format(
                a_owner=self.owner, a_name=self.name, d_owner=target.owner, d_name=target.name, dmg=damage
            )
        else:
            response = random.choice(config.attack_messages).format(
                a_owner=self.owner, a_name=self.name, d_owner=target.owner, d_name=target.name, dmg=damage
            )

        if crit:
            response += "\nIt's a critical hit!"

        return response


@dataclass
class BattlePlayer:
    """
    Stores the deck of a player and their model.
    """

    model: Player
    user: User | Member
    balls: list[BattleBall] = field(default_factory=list)
    locked: bool = False

    def __str__(self) -> str:
        return self.user.name


@dataclass
class BattleState:
    """
    Stores both `BattlePlayer` instances and other additional information for a battle.
    """

    player1: BattlePlayer
    player2: BattlePlayer

    active_player: BattlePlayer | None = None
    inactive_player: BattlePlayer | None = None
    round_number: int = 0

    started: bool = False
    accepted: bool = False

    accept_view: BattleAcceptView | None = None
    channel: TextChannel | None = None
    last_turn: TurnView | None = None

    def start(self):
        if self.started:
            return
        self.started = True
        self.active_player = self.player1
        self.inactive_player = self.player2

    def get_user(self, user: User | Member) -> BattlePlayer | None:
        if self.player1.user == user:
            return self.player1
        if self.player2.user == user:
            return self.player2

        return None

    def next_round(self) -> str | BattlePlayer:
        if all(ball.dead for ball in self.player2.balls):
            return self.player1
        if all(ball.dead for ball in self.player1.balls):
            return self.player2

        if not self.active_player or not self.inactive_player:
            raise Exception("Attempted to move on to next round without an active player!")

        self.round_number += 1

        # swap inactive and active
        self.active_player, self.inactive_player = self.inactive_player, self.active_player

        for ball in self.active_player.balls:
            ball.round_passed(self.round_number)

        return random.choice(self.active_player.balls).attack_target(random.choice(self.inactive_player.balls))


# max_deck_size: int = max_deck_size

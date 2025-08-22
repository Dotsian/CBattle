from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Type

from ballsdex.core.models import BallInstance, Player

from .base import BaseEffect

if TYPE_CHECKING:
    from discord import Member, TextChannel, User

    from .components import BattleAcceptView

ATTACK_MESSAGES = [
    "{a_owner}'s {a_name} attacks {d_owner}'s {d_name} for {dmg} DMG!",
    "{a_name} uppercuts {d_name}, dealing {dmg} DMG!",
    "{a_owner}'s {a_name} slices {d_name}! ({dmg} DMG)",
    "{a_name} lands a solid blow on {d_name} for {dmg} DMG",
]

DEFEAT_MESSAGES = [
    "{a_name} has easily crushed {d_name}!",
    "{d_owner}'s {d_name} has fallen to {a_owner}'s {a_name}.",
    "{a_name} knocks out {d_name}!",
    "{d_name} has been defeated!",
]

DODGE_MESSAGES = [
    "{a_name} tries to land a blow, but {d_name} dodges!",
    "{d_owner}'s {d_name} evades {a_owner}'s {a_name} attack!",
    "{d_name} sidesteps the attack!",
]


def format_random(msg_list, **kwargs):
    return random.choice(msg_list).format(**kwargs)


@dataclass
class BattleBall:
    """
    Stores a ball instance and keeps track of their health.
    """

    model: BallInstance
    health: int
    dead: bool = False

    effects: list[BaseEffect] = field(default_factory=list)

    @classmethod
    def from_ballinstance(cls, ballinstance: BallInstance):
        return cls(model=ballinstance, health=ballinstance.health)

    @property
    def damage(self):
        return int(self.model.attack * random.uniform(0.6, 1.2))

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
    locked: bool = False


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
    accept_view: BattleAcceptView | None = None
    channel: TextChannel | None = None
    winner: User | Member | None = None

    def get_user(self, user: User | Member) -> BattlePlayer | None:
        if self.player1.user == user:
            return self.player1
        if self.player2.user == user:
            return self.player2

        return None


# max_deck_size: int = max_deck_size


def attack(current_ball, opponent_balls):
    alive_balls = [ball for ball in opponent_balls if not ball.dead]
    opponent = random.choice(alive_balls)

    damage = current_ball.damage
    opponent.health -= damage
    if opponent.health <= 0:
        opponent.health = 0
        opponent.dead = True

    if opponent.dead:
        text = format_random(
            DEFEAT_MESSAGES,
            a_owner=current_ball.owner,
            a_name=current_ball.name,
            d_owner=opponent.owner,
            d_name=opponent.name,
            dmg=damage,
        )
    else:
        text = format_random(
            ATTACK_MESSAGES,
            a_owner=current_ball.owner,
            a_name=current_ball.name,
            d_owner=opponent.owner,
            d_name=opponent.name,
            dmg=damage,
        )

    return text


def random_events(p1_ball, p2_ball):
    if random.randint(1, 100) <= 25:
        msg = format_random(
            DODGE_MESSAGES, a_owner=p2_ball.owner, a_name=p2_ball.name, d_owner=p1_ball.owner, d_name=p1_ball.name
        )
        return True, msg
    return False, ""


def gen_battle(battle: BattleState):
    turn = 0

    while any(ball for ball in battle.player1.balls if not ball.dead) and any(
        ball for ball in battle.player2.balls if not ball.dead
    ):
        alive_p1 = [ball for ball in battle.player1.balls if not ball.dead]
        alive_p2 = [ball for ball in battle.player2.balls if not ball.dead]

        for p1_ball, p2_ball in zip(alive_p1, alive_p2):
            if not p1_ball.dead:
                turn += 1

                event = random_events(p1_ball, p2_ball)
                if event[0]:
                    yield f"Turn {turn}: {event[1]}"
                    continue

                yield f"Turn {turn}: {attack(p1_ball, battle.player2.balls)}"

                if all(ball.dead for ball in battle.player2.balls):
                    break

            if not p2_ball.dead:
                turn += 1

                event = random_events(p2_ball, p1_ball)
                if event[0]:
                    yield f"Turn {turn}: {event[1]}"
                    continue

                yield f"Turn {turn}: {attack(p2_ball, battle.player1.balls)}"

                if all(ball.dead for ball in battle.player1.balls):
                    break

    if all(ball.dead for ball in battle.player1.balls):
        battle.winner = battle.player2.user
    elif all(ball.dead for ball in battle.player2.balls):
        battle.winner = battle.player1.user

    battle.turns = turn

from __future__ import annotations
import random

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Type

from ballsdex.core.models import BallInstance, Player

from .base import BaseEffect
from .config import max_deck_size

if TYPE_CHECKING:
    from discord import Member, User

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
        base = model.attack * random.uniform(0.5, 1)
        is_super = random.random() < 0.25
        if is_super:
            return int(base * 1.5), True
        return int(base), False

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
    max_deck_size: int = max_deck_size

def attack(current_ball, opponent_balls):
    alive_balls = [ball for ball in opponent_balls if not ball.dead]
    opponent = random.choice(alive_balls)

    damage, is_super = get_damage(current_ball)
    opponent.health -= damage
    if opponent.health <= 0:
        opponent.health = 0
        opponent.dead = True

    if opponent.dead:
        text = format_random(
            DEFEAT_MESSAGES,
            a_owner=current_ball.owner,
            a_name=current_ball.name,
            d_owner=opponet.owner,
            d_name=opponent.name,
            dmg=damage,
        )
    else:
        text = format_random(
            ATTACK_MESSAGES,
            a_owner=current_ball.owner,
            a_name=current_ball.name,
            d_owner=opponet.owner,
            d_name=opponent.name,
            dmg=damage,
        )

    if is_super:
        text += " 💥**CRITICAL HIT!**"

    return text

def random_events(p1_ball, p2_ball):
    if random.randint(1, 100) <= 25:
        msg = format_random(
            DODGE_MESSAGES,
            a_owner=p2_ball.owner,
            a_name=p2_ball.name,
            d_owner=p1_ball.owner,
            d_name=p1_ball.name,
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

            if not player2.ball.dead:
                turn += 1

                event = random_events(p2_ball, p1_ball)
                if event[0]:
                    yield f"Turn {turn}: {event[1]}"
                    continue

                yield f"Turn {turn}: {attack(p2_ball, battle.player1.balls)}"

                if all(ball.dead for ball in battle.player1.balls):
                    break

    if all(ball.dead for ball in battle.player1.balls):
        battle.winner = battle.player2.balls[0].owner
    elif all(ball.dead for ball in battle.player2.balls):
        battle.winner = battle.player1.balls[0].owner

    battle.turns = turn

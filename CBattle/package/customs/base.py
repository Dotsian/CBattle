from dataclasses import dataclass
from typing import final

from ..logic import BattleBall


@dataclass
class BaseAbility:
    """
    Base ability class for all custom abilities.
    """

    ball: BattleBall

    passive: bool = False
    usable: int = 0
    used_since: int = 0

    active: bool = False

    @final
    def process_activation(self):
        if not self.passive and self.usable <= 0:
            return

        self.usable -= 1
        self.active = True
        self.used_since = 0

        self.on_activation()

    @final
    def process_round(self):
        if not self.active:
            return

        self.used_since += 1

    def on_activation(self):
        pass

    def round_passed(self, round_number: int):
        self.process_round()

    def choose_ball(self) -> bool:
        return True

    def fetch_damage(self, opponent_ball) -> int:
        return self.ball.damage


@dataclass
class BaseEffect:
    """
    Base effect class for handling custom effects.
    """

    ball: BattleBall
    rounds: int

    rounds_since: int = 0
    active: bool = True

    @final
    def process_round(self):
        if not self.active:
            return

        self.rounds_since += 1

        if self.rounds_since < self.rounds:
            self.active = False
            self.ball.effect = None

    def choose_ball(self) -> bool:
        return True

    def fetch_damage(self, opponent_ball: BattleBall) -> int:
        return self.ball.damage

    def round_passed(self, round_number: int):
        self.process_round()

from dataclasses import dataclass

from .base import BaseEffect


@dataclass
class Stun(BaseEffect):
    """
    Stun effect class.
    """

    def choose_ball(self) -> bool:
        return False  # Prevents this ball from getting chosen if it's stunned.

from typing import TYPE_CHECKING

from .cog import Battle
from .commands import CBattleText

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


async def setup(bot: "BallsDexBot"):
    await bot.add_cog(Battle(bot))
    await bot.add_cog(CBattleText(bot))

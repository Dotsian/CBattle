import asyncio
from typing import TYPE_CHECKING

import discord
from discord.ui import Button, View, button

from .logic import Battle

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


class TimeoutTimer:
    def __init__(self, interval, function, async_function=False):
        self.interval = interval
        self.function = function
        self.async_function = async_function
        self.task = None

    def start(self):
        self.cancel()

        loop = asyncio.get_running_loop()
        self.task = loop.call_later(self.interval, self._run)

    def cancel(self):
        if self.task:
            self.task.cancel()
            self.task = None

    def reset(self):
        self.start()

    def _run(self):
        if self.async_function:
            asyncio.create_task(self.function())
        else:
            self.function()

        self.task = None

class BattleStartView(View):
    """
    View that is displayed when starting a battle.
    """

    def __init__(self, interaction: discord.Interaction["BallsDexBot"], target_player: discord.User):
        super().__init__()

        self.interaction = interaction
        self.start_player = interaction.user
        self.target_player = target_player

        self.battle: Battle | None = None
        self.timeout = TimeoutTimer(10, self.timeout_request, True)

    async def timeout_request(self):
        for child in [x for x in self.children if isinstance(x, Button)]:
            child.disabled = True

        embed = self.interaction.message.embeds[0]
        embed.description = "Battle request timed out..."

        await self.interaction.response.edit_message(embed=embed, view=self)

    @button(style=discord.ButtonStyle.primary, label="Accept")
    async def accept_button(self, interaction: discord.Interaction["BallsDexBot"], button: Button):
        if interaction.user.id != self.target_player.id:
            await interaction.response.send_message("Only the target player can accept a battle!", ephemeral=True)
            return

        self.timeout.cancel()

        for child in [x for x in self.children if isinstance(x, Button)]:
            child.disabled = True

        embed = interaction.message.embeds[0]
        embed.description = "Battle accepted!"

        await interaction.response.edit_message(embed=embed, view=self)

        # battle = Battle(BattlePlayer(model=self.start_player), BattlePlayer(model=self.target_player))

    @button(style=discord.ButtonStyle.red, label="Decline")
    async def decline_button(self, interaction: discord.Interaction["BallsDexBot"], button: Button):
        if interaction.user.id != self.target_player.id:
            await interaction.response.send_message("Only the target player can accept a battle!", ephemeral=True)
            return

        self.timeout.cancel()

        for child in [x for x in self.children if isinstance(x, Button)]:
            child.disabled = True

        embed = interaction.message.embeds[0]
        embed.description = "Battle declined!"

        await interaction.response.edit_message(embed=embed, view=self)

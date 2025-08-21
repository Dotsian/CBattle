from typing import TYPE_CHECKING

import discord
from discord.embeds import Embed
from discord.ui import Button, View, button

from .logic import Battle

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


class BattleStartView(View):
    """
    View that is displayed when starting a battle.
    """

    def __init__(self, interaction: discord.Interaction["BallsDexBot"], target_player: discord.User):
        super().__init__(timeout=60)

        self.interaction = interaction
        self.start_player = interaction.user
        self.target_player = target_player

        self.battle: Battle | None = None

    async def on_timeout(self) -> None:
        for child in [x for x in self.children if isinstance(x, Button)]:
            child.disabled = True

        embed = Embed()
        embed.description = "Battle request timed out."

        await self.interaction.edit_original_response(embed=embed, view=self)
        return await super().on_timeout()

    @button(style=discord.ButtonStyle.primary, label="Accept")
    async def accept_button(self, interaction: discord.Interaction["BallsDexBot"], button: Button):
        if interaction.user.id != self.target_player.id:
            await interaction.response.send_message("Only the target player can accept a battle!", ephemeral=True)
            return

        for child in [x for x in self.children if isinstance(x, Button)]:
            child.disabled = True

        if interaction.message is None:
            return

        embed = interaction.message.embeds[0]
        embed.description = "Battle accepted!"

        await interaction.response.edit_message(embed=embed, view=self)

        # battle = Battle(BattlePlayer(model=self.start_player), BattlePlayer(model=self.target_player))

    @button(style=discord.ButtonStyle.red, label="Decline")
    async def decline_button(self, interaction: discord.Interaction["BallsDexBot"], button: Button):
        if interaction.user.id != self.target_player.id:
            await interaction.response.send_message("Only the target player can decline a battle!", ephemeral=True)
            return

        for child in [x for x in self.children if isinstance(x, Button)]:
            child.disabled = True

        if interaction.message is None:
            return

        embed = interaction.message.embeds[0]
        embed.description = "Battle declined!"

        await interaction.response.edit_message(embed=embed, view=self)

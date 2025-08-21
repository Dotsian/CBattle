from typing import TYPE_CHECKING

import discord
from discord.ui import Button, View, button

from .logic import Battle, BattlePlayer


if TYPE_CHECKING:
    from ballsdex.core.models import Player
    from ballsdex.core.bot import BallsDexBot


class BattleStartView(View):
    """
    Embed that is displayed when starting a battle.
    """

    def __init__(self, start_player, target_player):
        super().__init__()

        self.start_player: discord.User = start_player
        self.target_player: discord.User = target_player

        self.battle: None | Battle = None

    @button(style=discord.ButtonStyle.primary, label="Accept")
    async def accept_button(self, interaction: discord.Interaction["BallsDexBot"], button: Button):
        if interaction.user.id != self.target_player.id:
            await interaction.response.send_message("Only the target player can accept a battle!")
            return

        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True
        embed = interaction.message.embeds[0]
        embed.description = "Battle accepted!"
        await interaction.response.edit_message(embed=embed, view=self)

        battle = Battle(BattlePlayer(model=self.start_player), BattlePlayer(model=self.target_player))

    @button(style=discord.ButtonStyle.red, label="Decline")
    async def decline_button(self, interaction: discord.Interaction["BallsDexBot"], button: Button):
        if interaction.user.id != self.target_player.id:
            await interaction.response.send_message("Only the target player can accept a battle!")
            return

        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True

        embed = interaction.message.embeds[0]
        embed.description = "Battle declined!"
        await interaction.response.edit_message(embed=embed, view=self)

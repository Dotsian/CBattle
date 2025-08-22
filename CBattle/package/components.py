from typing import TYPE_CHECKING

import discord
from discord.embeds import Embed
from discord.ui import Button, View, button

from ballsdex.core.models import Player

from .logic import BattleState

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


class BattleStartView(View):
    """
    View that is displayed when starting a battle.
    """

    def __init__(self, interaction: discord.Interaction["BallsDexBot"], target_player: discord.User, battle, battles):
        super().__init__(timeout=60)

        self.interaction = interaction
        self.start_player = interaction.user
        self.target_player = target_player

        self.battle: BattleState = battle
        self.battles: dict[Player, BattleState] = battles

    async def on_timeout(self) -> None:
        for child in [x for x in self.children if isinstance(x, Button)]:
            child.disabled = True

        start_player, _ = await Player.get_or_create(discord_id=self.start_player.id)
        del self.battles[start_player]

        embed = Embed()
        embed.description = "Battle request timed out."
        embed.set_footer(text="")

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
        embed.set_footer(text="")

        if True:  # TODO: replace with classic / cbattle add menu
            embed.description = (
                "Battle accepted! You can now add balls with `/battle add` and remove them with `/battle remove`"
            )

        await interaction.response.edit_message(embed=embed, view=self)
        target_player, _ = await Player.get_or_create(discord_id=interaction.user.id)

        self.battle.accepted = True
        self.battles[target_player] = self.battle

        view = BattleAcceptView(self.battle)
        self.battle.accept_view = view

        message = await interaction.channel.send(view=view, embed=view.get_embed())
        view.message = message

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
        embed.set_footer(text="")

        start_player, _ = await Player.get_or_create(discord_id=self.start_player.id)
        del self.battles[start_player]

        await interaction.response.edit_message(embed=embed, view=self)


class BattleAcceptView(View):
    def __init__(self, battle: BattleState):
        self.battle: BattleState = battle
        self.message: discord.Message
        super().__init__()

    def get_embed(self) -> Embed:
        embed = Embed()
        embed.description = "<Placeholder>"
        for ball in self.battle.player1.balls:
            embed.description += ball.model.countryball.country
        for ball in self.battle.player2.balls:
            embed.description += ball.model.countryball.country

        return embed

    async def update(self):
        await self.message.edit(view=self, embed=self.get_embed())

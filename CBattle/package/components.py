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

        if not self.battle.accepted:
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

        message = await self.battle.channel.send(view=view, embed=view.get_embed())
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
        embed = (
            Embed(
                color=10181046,
                title="Battle planning",
                description="Add or remove battle balls with /battle add and /battle remove commands.",
            )
            .add_field(
                name=self.battle.player1.user.name + ("🔒" if self.battle.player1.locked else ""),
                value="\n".join(" - " + ball.model.to_string() for ball in self.battle.player1.balls),
                inline=True,
            )
            .add_field(
                name=self.battle.player2.user.name + ("🔒" if self.battle.player2.locked else ""),
                value="\n".join(" - " + ball.model.to_string() for ball in self.battle.player2.balls),
                inline=True,
            )
        )

        return embed

    @button(style=discord.ButtonStyle.red, label="Lock")
    async def lock_button(self, interaction: discord.Interaction["BallsDexBot"], button: Button):
        battle_player = self.battle.get_user(interaction.user)
        if battle_player is None:
            await interaction.response.send_message("You are not in this battle!")
            return

        if battle_player.locked:
            await interaction.response.send_message(
                f"{interaction.user.mention} You've already locked.", ephemeral=True
            )
            return

        battle_player.locked = True
        await interaction.response.send_message(f"{interaction.user.mention} locked!")
        await self.update()

        if not (self.battle.player1.locked and self.battle.player2.locked):
            return

        self.battle.started = True

        button.disabled = True

        view = TurnView(self.battle)
        message = await self.battle.channel.send("<Placeholder>", view=view)
        self.battle.last_turn = TurnView
        view.message = message

    async def update(self):
        await self.message.edit(view=self, embed=self.get_embed())


class TurnView(View):
    def __init__(self, battle: BattleState):
        self.battle: BattleState = battle
        self.message: discord.Message
        super().__init__()

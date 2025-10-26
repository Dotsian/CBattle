from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from ballsdex.core.models import Player
from ballsdex.core.utils.transformers import BallInstanceTransform

from .components import BattleStartView
from .logic import BattleBall, BattlePlayer, BattleState
from .pagination import TutorialPages

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

class Battle(commands.GroupCog):
    """
    Battle commands.
    """

    def __init__(self, bot):
        self.bot = bot
        self.battles: dict[Player, BattleState] = {}

    @app_commands.command()
    async def tutorial(self, interaction: discord.Interaction):
        """View the tutorial for CBattling!"""

        pages = [lambda i=i: None for i in range(5)]
        view = TutorialPages(pages, interaction.user.id)

        await interaction.response.send_message(view=view)

    @app_commands.command()
    async def add(self, interaction: discord.Interaction["BallsDexBot"], countryball: BallInstanceTransform):
        """
        Adds a countryball to the battle.

        Parameters
        ----------
        countryball: BallInstance
            The countryball you want to add.
        """
        interaction_player, _ = await Player.get_or_create(discord_id=interaction.user.id)

        if interaction_player not in self.battles:
            await interaction.response.send_message("You don't have an active battle!", ephemeral=True)
            return

        battle = self.battles[interaction_player]

        if battle.started:
            await interaction.response.send_message(
                "You can't change your deck after the battle has started!", ephemeral=True
            )
            return

        if not battle.accepted:
            await interaction.response.send_message(
                "You can't add a ball until the battle is accepted!", ephemeral=True
            )
            return

        battle_player = battle.player1 if battle.player1.model == interaction_player else battle.player2

        if battle_player.locked:
            await interaction.response.send_message("You can't change your deck after you've locked!", ephemeral=True)
            return

        battleball = BattleBall.from_ballinstance(countryball, battle_player)

        if battleball in battle_player.balls:
            await interaction.response.send_message("You've already added this ball to your deck!", ephemeral=True)
            return

        battle_player.balls.append(BattleBall.from_ballinstance(countryball, battle_player))
        emoji = self.bot.get_emoji(countryball.countryball.emoji_id)

        await interaction.response.send_message(
            f"`#{countryball.id}` {emoji} {countryball.countryball.country} added!", ephemeral=True
        )

        await battle.accept_view.update()

    @app_commands.command()
    async def remove(self, interaction: discord.Interaction["BallsDexBot"], countryball: BallInstanceTransform):
        """
        Removes a countryball from the battle.

        Parameters
        ----------
        countryball: BallInstance
            The countryball you want to remove.
        """
        interaction_player, _ = await Player.get_or_create(discord_id=interaction.user.id)

        if interaction_player not in self.battles:
            await interaction.response.send_message("You don't have an active battle!", ephemeral=True)
            return

        battle = self.battles[interaction_player]

        if battle.started:
            await interaction.response.send_message(
                "You can't change your deck after the battle has started!", ephemeral=True
            )
            return
        if not battle.accepted:
            await interaction.response.send_message(
                "You can't remove a ball until the battle is accepted!", ephemeral=True
            )
            return

        battle_player = battle.player1 if battle.player1.model == interaction_player else battle.player2

        if battle_player.locked:
            await interaction.response.send_message("You can't change your deck after you've locked!", ephemeral=True)
            return

        removing_ball = BattleBall.from_ballinstance(countryball)

        emoji = self.bot.get_emoji(countryball.countryball.emoji_id)

        if removing_ball not in battle_player.balls:
            await interaction.response.send_message("This ball is not in your deck!", ephemeral=True)
            return

        battle_player.balls.remove(removing_ball)

        await interaction.response.send_message(
            f"`#{countryball.id}` {emoji} {countryball.countryball.country} removed!", ephemeral=True
        )

        await battle.accept_view.update()

    @app_commands.command()
    async def cancel(self, interaction: discord.Interaction):
        interaction_player, _ = await Player.get_or_create(discord_id=interaction.user.id)

        if interaction_player not in self.battles:
            await interaction.response.send_message("You don't have an active battle!", ephemeral=True)
            return

        battle = self.battles[interaction_player]
        if battle.accept_view:
            await battle.accept_view.message.edit(content="This battle was cancelled.")

        players = [battle.player1.model, battle.player2.model]
        for player in players:
            del self.battles[player]

        if battle.last_turn:
            await battle.last_turn.cancel()

        await interaction.response.send_message("Cancelled battle!")

    @app_commands.command()
    async def start(self, interaction: discord.Interaction, user: discord.User):
        """
        Starts a battle with a user.

        Parameters
        ----------
        user: discord.User
            The user you want to battle against.
        """

        if not interaction.channel:
            await interaction.response.send_message("This command must be run in a channel")

        if user.bot:
            await interaction.response.send_message("You cannot battle against bots.", ephemeral=True)
            return

        if user.id == interaction.user.id:
            await interaction.response.send_message("You cannot battle against yourself.", ephemeral=True)
            return

        if user.id in self.bot.blacklist:
            await interaction.response.send_message("You cannot battle against a blacklisted player.", ephemeral=True)
            return

        player1, _ = await Player.get_or_create(discord_id=interaction.user.id)
        player2, _ = await Player.get_or_create(discord_id=user.id)

        blocked1 = await player1.is_blocked(player2)
        blocked2 = await player2.is_blocked(player1)

        if blocked1:
            await interaction.response.send_message(
                "You cannot battle against a player you have blocked.", ephemeral=True
            )
            return

        if blocked2:
            await interaction.response.send_message(
                "You cannot battle against a player that has blocked you.", ephemeral=True
            )
            return

        if player1 in self.battles:
            await interaction.response.send_message(
                "You cannot start a battle while you have an active battle or battle request", ephemeral=True
            )
            return
        if player2 in self.battles:
            await interaction.response.send_message(
                "You cannot start a battle with a player already in a battle", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="Battle Request!",
            description=f"{user.mention}, {interaction.user.mention} has invited you to a battle!",
        )

        embed.set_footer(text="Battle request will expire in 1 minute.")

        battle = BattleState(
            player1=BattlePlayer(model=player1, user=interaction.user),
            player2=BattlePlayer(model=player2, user=user),
            channel=interaction.channel,
        )
        self.battles[player1] = battle

        view = BattleStartView(interaction, user, battle, self.battles)

        await interaction.response.send_message(view=view, embed=embed)

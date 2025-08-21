import discord
from discord import app_commands
from discord.ext import commands

from ballsdex.core.models import Player

from .components import StartEmbed
from .logic import Battle as BattleClass
from .logic import BattlePlayer


class Battle(commands.GroupCog):
    """
    Battle commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def start(self, interaction: discord.Interaction, user: discord.User):
        """
        Starts a battle with a user.

        Parameters
        ----------
        user: discord.User
            The user you want to battle against.
        """
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

        battle_player1 = BattlePlayer(player1)
        battle_player2 = BattlePlayer(player2)

        battle = BattleClass(battle_player1, battle_player2)

        await interaction.response.send_message(embed=StartEmbed(battle))

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from ballsdex.core.models import Player
from ballsdex.core.utils.transformers import BallInstanceTransform
from ballsdex.settings import settings

from .components import BattleStartView
from .logic import BattleBall, BattlePlayer, BattleState
from .pagination import TutorialPages

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

TUTORIAL = {
    "Welcome to CBattle!": (
        "Welcome, soldier, and thank you for installing CBattle! In this package, battling is greatly improved by "
        f"giving {settings.plural_collectible_name} abilities, attack & health stats and even spells! This helpful "
        "tutorial will help you master CBattling, so you wont get left for dead in the arena. You'll learn how to "
        "start a battle, get taught abilities, how to win, making decks and even studying the basics of a fight, so get"
        " ready to brawl in this amazing extension of battling, CBattle!!!"
    ),
    "Starting a Battle": (
        "To initiate a battle, you can type `/battle start`. Click on it, then you will see a parameter asking for what"
        " user you'd like to challenge. Click it, and if you already see them on the list, perfect! Click on them and "
        "send the message. If you dont, search for their user by typing their name in the message bar and clicking "
        "their name. Then, the opponent will get mentioned and once they've arrived, the battle will commence."
    ),
    "All About Decks": (
        f"Decks are the #1 most important thing in CBattling. You know how in {settings.bot_name}, you can catch "
        f"{settings.plural_collectible_name}? Well with decks, you can finally put them to the test! By using "
        f"`/battle add`, you can search and select from your inventory of {settings.plural_collectible_name}. "
        f"Once you've selected them, send the command and you'll see the {settings.plural_collectible_name} pop up in "
        "the embed message! Remember, theres a certain limit of how much there can be in a deck. You can also remove "
        f"{settings.plural_collectible_name}, too, with the `/battle remove` command! Make sure to select the exact "
        f"{settings.collectible_name} you want to remove, though."
    ),
    "Abilities and Such": (
        f"If you've ever seen a {settings.plural_collectible_name} card before, you'd know they have special abilities,"
        " like poison, burst damage, healing and shielding! And yes, in CBattling, this all works! When it is your turn"
        " to fight the opponent's card, you'll have an option to use your ability "
        "(at least if it applies to the abilities logic). Once you've used it, you'll see the card spin, and a message"
        " will pop up over the image, saying: `Example has used Ability: Example Ability!` Most abilites do damage, "
        "so they'd just say it did damage, but it could also say it healed something or gave paralyzation or even one "
        "shot something! I think you get it now!"
    ),
    "Winning and Losing": (
        "Winning and losing. It happens to all of us! But you are a WINNER. If you have all your cards gray, "
        f"unfortunately, you have been defeated, but that doesnt mean give up! Your {settings.plural_collectible_name} "
        "are still alive, so you can fight all you want and train to become the CBattle champion. If all the opponents "
        "cards are gray, however, then congrats, soldier, then you have done it! You are the ultimate warrior! Maybe "
        "you'll earn a cookie. Keep battling other worthy opponents in search of mastering... CBattle!!!"
    ),
}

THUMBNAILS = [
    # page 1: cbattle logo
    "https://images-ext-1.discordapp.net/external/yM5ZPPxC1zPzGYhq8HnzXjT0Q0T8uWlOXHbWyay3Nnw/https/raw.githubusercontent.com/Dotsian/CBattle/refs/heads/main/assets/Logo.png",
    # page 2: fists
    "https://www.pngmart.com/files/23/Fist-PNG.png",
    # page 3: cards
    "https://cdn-icons-png.flaticon.com/512/5030/5030368.png",
    # page 4: shield
    "https://th.bing.com/th/id/R.cc541053f483f433d81d867221f29135?rik=QzKgpGUoVAyNmA&riu=http%3a%2f%2fwww.clker.com%2fcliparts%2fl%2fE%2f3%2fC%2fe%2fT%2fred-shield-hi.png&ehk=YNsIL2zoKv%2b54fxAa3tiPatJI6%2ffLPrU%2f3lgEb2wKLc%3d&risl=&pid=ImgRaw&r=0",
    # page 5: potion
    "https://gamepedia.cursecdn.com/zelda_gamepedia_en/thumb/6/68/PH_Red_Potion_Model.png/225px-PH_Red_Potion_Model.png?version=59fdeb61e177cc36789fd835546017e4",
    # page 6: trophy
    "https://th.bing.com/th/id/R.a5b17534342efbc6b3d1c9689255c7b7?rik=9u%2fKoEzC1XQ1jw&pid=ImgRaw&r=0",
]


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

        pages = [lambda i=i: None for i in range(6)]
        view = TutorialPages(pages, interaction.user.id)

        await interaction.response.send_message(view=view, flags=discord.MessageFlags.components_v2())

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

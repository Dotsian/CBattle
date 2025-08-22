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


class Battle(commands.GroupCog):
    """
    Battle commands.
    """

    def __init__(self, bot):
        self.bot = bot
        self.battles: dict[Player, BattleState] = {}

    @app_commands.command()
    async def tutorial(self, interaction: discord.Interaction):
        """
        View the tutorial for CBattling!
        """

        def make_pages(page_num: int):
            async def page():
                titles = [
                    "Welcome to CBattle!",
                    "Starting a Battle",
                    "All About Decks",
                    "During a Battle",
                    "Abilities and Such",
                    "Losing and Winning",
                ]

                descriptions = [
                    f"Welcome, soldier, and thank you for installing CBattle! In this package, battling is greatly improved by giving {settings.plural_collectible_name} abilities, attack & health stats and even spells! This helpful tutorial will help you master CBattling, so you wont get left for dead in the arena. You'll learn how to start  a battle, get taught abilities, how to win, making decks and even studying the basics of a fight, so  get ready to brawl in this amazing extension of battling, CBattle!!!",  # noqa: E501
                    "To initiate a battle, you can type the / key in the message bar and then look for `battle start`. Click on it, then you will see a parameter asking for what user you'd like to challenge. Click it, and if you already see them on the list, perfect! Click on them and send the message. If you dont, search for their user by typing their name in the message bar and clicking their name. Then, the opponent will get mentioned and once they've arrived, the battle will commence.",  # noqa: E501
                    f"Decks are the #1 most important thing in CBattling. You know how in {settings.bot_name}, you can catch {settings.plural_collectible_name}? Well with decks, you can finally put them to the test! By using `/battle add`, you can search and select from your inventory of {settings.plural_collectible_name}. Once you've selected them, send the command and you'll see the {settings.plural_collectible_name} pop up in the embed message! Remember, theres a certain limit of how much there can be in a deck. You can also remove {settings.plural_collectible_name}, too, with the `/battle remove` command! Make sure to select the exact {settings.collectible_name} you want to remove, though.",  # noqa: E501
                    "Once both players decks have been created, both players must click the green `Ready!` button. You'll know if the other opponent is ready if there's a check next to their name. Once the battle is started, you'll start to see your cards IN ACTION! When it is your turn, you can either attack, dodge # unfinished # When your card takes damage, above it, the **health bar** goes down. You'll also know when your card has died when it turns gray, and move to the back of the deck. Once all your cards have died, the other person has won. But if the opponents cards are all gray! You are the champion!",  # noqa: E501
                    f"If you've ever seen a {settings.plural_collectible_name} card before, you'd know they have special abilities, like poison, burst damage, healing and shielding! And yes, in CBattling, this all works! When it is your turn to fight the opponent's card, you'll have an option to use your ability (at least if it applies to the abilities logic). Once you've used it, you'll see the card spin, and a message will pop up over the image, saying: `Example has used Ability: Example Ability!` Most abilites do damage, so they'd just say it did damage, but it could also say it healed something or gave paralyzation or even one shot something! I think you get it now!",  # noqa: E501
                    f"Losing and winning. It happens to all of us! But you are a WINNER. If you have all your cards gray, unfortunately, you have been defeated, but that doesnt mean give up! Your {settings.plural_collectible_name} are still alive, so you can fight all you want and train to become the CBattle champion. If all the opponents cards are gray, however, then congrats, soldier, then you have done it! You are the ultimate warrior! Maybe you'll earn a cookie. Keep battling other worthy opponents in search of mastering... CBattle!!!",  # noqa: E501
                ]

                thumbnails = [
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

                embed = discord.Embed(
                    title=f"Tutorial Page {page_num + 1}: {titles[page_num]}",
                    description=descriptions[page_num],
                    color=discord.Color.red(),
                )

                embed.set_thumbnail(url=thumbnails[page_num])

                return embed, None

            return page

        pages = [make_pages(i) for i in range(6)]
        view = TutorialPages(pages, interaction.user.id)
        embed, attachment = await pages[0]()

        if attachment:
            await interaction.response.send_message(embed=embed, file=attachment, view=view)
            return

        await interaction.response.send_message(embed=embed, view=view)

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

        if not battle.accepted:
            await interaction.response.send_message(
                "You can't add a ball until the battle is accepted!", ephemeral=True
            )
            return

        if battle.player1.model == interaction_player:
            battle_player = battle.player1
        else:
            battle_player = battle.player2

        battleball = BattleBall.from_ballinstance(countryball)
        if battleball in battle_player.balls:
            await interaction.response.send_message("You've already added this ball to the battle!", ephemeral=True)
            return

        battle_player.balls.append(BattleBall.from_ballinstance(countryball))
        emj = self.bot.get_emoji(countryball.countryball.emoji_id)
        await interaction.response.send_message(f"`#{countryball.id}` {emj} {countryball.countryball.country} removed!"
                                                , ephemeral=True)
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

        if not battle.accepted:
            await interaction.response.send_message(
                "You can't remove a ball until the battle is accepted!", ephemeral=True
            )
            return

        if battle.player1.model == interaction_player:
            battle_player = battle.player1
        else:
            battle_player = battle.player2

        inst_to_remove = BattleBall.from_ballinstance(countryball)

        emj = self.bot.get_emoji(countryball.countryball.emoji_id)

        if inst_to_remove in battle_player.balls:
            battle_player.balls.remove(inst_to_remove)
            await interaction.response.send_message(f"`#{countryball.id}` {emj} {countryball.countryball.country} removed!", ephemeral=True)
            await battle.accept_view.update()

        else:
            await interaction.response.send_message("This ball is not in your deck already!", ephemeral=True)
            return

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

        battle = BattleState(BattlePlayer(model=player1, user=interaction.user), BattlePlayer(model=player2, user=user))
        self.battles[player1] = battle

        view = BattleStartView(interaction, user, battle, self.battles)

        await interaction.response.send_message(view=view, embed=embed)

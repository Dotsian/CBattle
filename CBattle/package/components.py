import discord

from .logic import Battle


class StartEmbed(discord.Embed):
    """
    Embed that is displayed when starting a battle.
    """

    def __init__(self, battle: Battle):
        super().__init__()

        self.battle = battle

        self.title = "Battle"
        self.description = "<PLACEHOLDER>"

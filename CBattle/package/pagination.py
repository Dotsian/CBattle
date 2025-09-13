import discord

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

class TutorialPages(discord.ui.LayoutView):
    def __init__(self, pages, author_id: int):
        super().__init__(timeout=None)
        self.pages = pages
        self.author_id = author_id
        self.current = 0
        self.build_page()

    def build_page(self):
        self.clear_items()

        title = list(TUTORIAL.keys())[self.current]
        description = TUTORIAL[title]
        thumbnail_url = THUMBNAILS[self.current]

        section = discord.ui.Section(
            discord.ui.TextDisplay(content=f"**Tutorial Page {self.current + 1}: {title}**"),
            discord.ui.TextDisplay(content=description),
            accessory=discord.ui.Thumbnail(media=thumbnail_url),
        )

        action_row = discord.ui.ActionRow(
            discord.ui.Button(style=discord.ButtonStyle.secondary, emoji="⏮️", custom_id="first"),
            discord.ui.Button(style=discord.ButtonStyle.secondary, emoji="◀️", custom_id="prev"),
            discord.ui.Button(style=discord.ButtonStyle.secondary, emoji="▶️", custom_id="next"),
            discord.ui.Button(style=discord.ButtonStyle.secondary, emoji="⏭️", custom_id="last"),
        )

        container = discord.ui.Container(section, action_row, accent_colour=discord.Colour.red(), spoiler=True)

        self.add_item(container)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You are not allowed to interact with this menu.", ephemeral=True)
            return False
        return True

    async def on_button_click(self, interaction: discord.Interaction):
        match interaction.data["custom_id"]:
            case "first":
                self.current = 0
            case "prev":
                self.current = (self.current - 1) % len(self.pages)
            case "next":
                self.current = (self.current + 1) % len(self.pages)
            case "last":
                self.current = len(self.pages) - 1

        self.build_page()
        await interaction.response.edit_message(view=self)

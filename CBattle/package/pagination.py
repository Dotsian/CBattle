import discord

from discord.ui import LayoutView, Container, TextDisplay, Button, Thumbnail
from discord import Interaction, ButtonStyle, Colour, MessageFlags

from .cog import TUTORIAL, THUMBNAILS

class TutorialPages(LayoutView):
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

        container = Container(accent_color=Colour.red())

        container.add_item(TextDisplay(
            text=f"**Tutorial Page {self.current + 1}: {title}**\n{description}"
        ))

        container.add_item(Thumbnail(url=thumbnail_url))

        container.add_item(Button(label="⇐", style=ButtonStyle.secondary, custom_id="first"))
        container.add_item(Button(label="◁", style=ButtonStyle.primary, custom_id="prev"))
        container.add_item(Button(label="▷", style=ButtonStyle.primary, custom_id="next"))
        container.add_item(Button(label="⇒", style=ButtonStyle.secondary, custom_id="last"))

        self.add_item(container)

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You are not allowed to interact with this menu.", ephemeral=True)
            return False
        return True

    async def on_button_click(self, interaction: Interaction):
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

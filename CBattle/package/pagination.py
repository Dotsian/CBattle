from discord import Interaction, ButtonStyle, Colour
from discord.ui import LayoutView, Container, Section, TextDisplay, Thumbnail, ActionRow, Button

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

        section = Section(
            TextDisplay(content=f"**Tutorial Page {self.current + 1}: {title}**"),
            TextDisplay(content=description),
            accessory=Thumbnail(media=thumbnail_url)
        )

        action_row = ActionRow(
            Button(style=ButtonStyle.secondary, emoji="⏮️", custom_id="first"),
            Button(style=ButtonStyle.secondary, emoji="◀️", custom_id="prev"),
            Button(style=ButtonStyle.secondary, emoji="▶️", custom_id="next"),
            Button(style=ButtonStyle.secondary, emoji="⏭️", custom_id="last"),
        )

        container = Container(
            section,
            action_row,
            accent_colour=Colour(14169654),
            spoiler=True
        )

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

import discord


class TutorialPages(discord.ui.View):
    def __init__(self, pages, author_id: int):
        super().__init__(timeout=None)

        self.pages = pages
        self.author_id = author_id

        self.current = 0

    async def update_page(self, interaction: discord.Interaction):
        embed, attachment = await self.pages[self.current]()

        if attachment:
            await interaction.response.edit_message(embed=embed, attachments=[attachment], view=self)
            return

        await interaction.response.edit_message(embed=embed, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You are not allowed to interact with this menu.", ephemeral=True)
            return False

        return True

    @discord.ui.button(style=discord.ButtonStyle.secondary, label="⇐")
    async def go_first(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = 0
        await self.update_page(interaction)

    @discord.ui.button(style=discord.ButtonStyle.primary, label="◁")
    async def go_previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = (self.current - 1) % len(self.pages)
        await self.update_page(interaction)

    @discord.ui.button(style=discord.ButtonStyle.primary, label="▷")
    async def go_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = (self.current + 1) % len(self.pages)
        await self.update_page(interaction)

    @discord.ui.button(style=discord.ButtonStyle.secondary, label="⇒")
    async def go_last(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = len(self.pages) - 1
        await self.update_page(interaction)

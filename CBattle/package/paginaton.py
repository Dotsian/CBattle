import discord

class TutorialPages(discord.ui.View):
    def __init__(self, pages, author_id: int):
        super().__init__(timeout=None)
        self.pages = pages
        self.current = 0
        self.message = None
        self.author_id = author_id

        self.first_button = discord.ui.Button(label="⇐⇐", style=discord.ButtonStyle.secondary)
        self.prev_button = discord.ui.Button(label="◁", style=discord.ButtonStyle.primary)
        self.next_button = discord.ui.Button(label="▷", style=discord.ButtonStyle.primary)
        self.last_button = discord.ui.Button(label="⇒⇒", style=discord.ButtonStyle.secondary)

        self.first_button.callback = self.go_first
        self.prev_button.callback = self.go_previous
        self.next_button.callback = self.go_next
        self.last_button.callback = self.go_last

        self.add_item(self.first_button)
        self.add_item(self.prev_button)
        self.add_item(self.next_button)
        self.add_item(self.last_button)

    async def update_page(self, interaction: discord.Interaction):
        embed, file = await self.pages[self.current]()
        await interaction.response.edit_message(embed=embed, attachments=[file], view=self)

    async def go_first(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)
            return
        self.current = 0
        await self.update_page(interaction)

    async def go_last(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)
            return
        self.current = len(self.pages) - 1
        await self.update_page(interaction)

    async def go_previous(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)
            return
        self.current = (self.current - 1) % len(self.pages)
        await self.update_page(interaction)

    async def go_next(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)
            return
        self.current = (self.current + 1) % len(self.pages)
        await self.update_page(interaction)

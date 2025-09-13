import base64

import requests
from discord.ext import commands

__version__ = "0.0.1a"


class CBattleText(commands.Cog):
    """
    Battle text commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def cbattle(self, ctx: commands.Context, reference: str = "main", remote: str = "Dotsian/CBattle"):
        """
        Displays the CBattle installer.

        Parameters
        ----------
        reference: str
            The CBattle branch you want to run the installer on.
        """
        link = f"https://api.github.com/repos/{remote}/contents/CBattle/github/installer.py"

        request = requests.get(link, {"ref": reference})

        match request.status_code:
            case requests.codes.not_found:
                await ctx.send(f"Could not find installer for the {reference} branch on {remote}.")

            case requests.codes.ok:
                content = requests.get(link, {"ref": reference}).json()["content"]

                await ctx.invoke(self.bot.get_command("eval"), body=base64.b64decode(content).decode())

            case _:
                await ctx.send(f"Request raised error code `{request.status_code}`.")

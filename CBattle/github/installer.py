import requests

def format(code: str) -> str:
    return (
        code.replace("<NAME>", "CBattle")
        .replace("<REPOSITORY>", "Dotsian/CBattle")
        .replace("<BRANCH>", "main")
        .replace("<PATH>", "ballsdex/packages/cbattle")
        .replace("<FOLDER>", "CBattle")
        .replace("<COLOR>", "#FF466A")
    )

content = requests.get("https://raw.githubusercontent.com/Dotsian/BDInstaller/main/main.py").text

await ctx.invoke(bot.get_command("eval"), body=format(content))

# CBattle - Interactive Battle Package

[![Ruff](https://github.com/Dotsian/CBattle/actions/workflows/ruff.yml/badge.svg)](https://github.com/Dotsian/CBattle/actions/workflows/ruff.yml)
[![Issues](https://img.shields.io/github/issues/Dotsian/CBattle)](https://github.com/Dotsian/CBattle/issues)
[![discord.py](https://img.shields.io/badge/discord-py-blue.svg)](https://github.com/Rapptz/discord.py)

## What is CBattle?

CBattle is the first public interactive battle package developed by CrashTextAlex and DotZZ designed for the Ballsdex Discord bot that provides extensive customizability. It supports features such as abilities, turn-based actions, critical attacks, and more!

## CBattle Requirements

To install CBattle, you must have the following:

* Ballsdex
* Eval access

## CBattle Setup

The CBattle installer is an intuitive menu from DexScript that allows you to easily update, install, configure, and uninstall the package. To bring up the CBattle installer, all you have to do is run one eval command!

To install CBattle, run the following eval command:

> ```py
> import base64, requests; await ctx.invoke(bot.get_command("eval"), body=base64.b64decode(requests.get("https://api.github.com/repos/Dotsian/CBattle/contents/CBattle/github/installer.py").json()["content"]).decode())
> ```

import discord
import tomllib
from pathlib import Path

maxballamount=5
debug=False
attributes={}

def read_settings(path: "Path"):
    with open(Path, "r") as f:
        dic = tomllib.load(f)

    maxballamount=dic["max-ball-amount = 5"]
    debug=dic["debug"]
    attributes=dic["attributes"]
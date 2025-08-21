import tomllib
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Config():
    max_ball_amount=5
    debug=False
    attributes={}
    def read_settings(path: "Path"):
        with open(Path, "r") as f:
            dic = tomllib.load(f)

        max_ball_amount=dic.get("max-ball-amount", 5)
        debug=dic.get("debug", False)
        attributes=dic.get("attributes", {})
import tomllib
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config():
    max_ball_amount:int=5
    debug:bool=False
    attributes:list={}
    def read_settings(self, path: "Path"):
        with open(Path, "r") as f:
            dic = tomllib.load(f)

        self.max_ball_amount=dic.get("max-ball-amount", 5)
        self.debug=dic.get("debug", False)
        self.attributes=dic.get("attributes", {})

import os
import tomllib
from pathlib import Path


class Config:
    """
    Configuration class for holding all config values loaded from the `config.toml` file.
    """

    def __init__(self, path: Path):
        with path.open("rb") as config_file:
            data = tomllib.load(config_file)

        self.max_ball_amount = data["settings"].get("max-ball-amount", 5)
        self.debug = data["settings"].get("debug", False)
        self.attributes = data.get("attributes", {})
        self.attack_messages = data["messages"].get("attack", [])
        self.defeat_messages = data["messages"].get("defeat", [])
        self.dodge_messages = data["messages"].get("dodge", [])


CONFIG_PATH = Path(os.path.dirname(os.path.abspath(__file__)), "./config.toml")
config = Config(CONFIG_PATH)

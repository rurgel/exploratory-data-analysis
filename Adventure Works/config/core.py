from pathlib import Path
from tkinter.ttk import Separator
from pydantic import BaseModel
from strictyaml import YAML, load  # type: ignore
from typing import List, Dict, Optional

BASE_PATH = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_PATH / "config.yml"
INPUT_PATH = BASE_PATH / "input"

class Config(BaseModel):
    datafolder: Path
    datatypes: Dict[str, str]


def find_config_file() -> Path:
    """Locate the configuration file."""
    if CONFIG_FILE.is_file():
        return CONFIG_FILE
    raise Exception(f"Config not found at {CONFIG_FILE!r}")


def fetch_config_from_yaml(cfg_path: Optional[Path] = None) -> YAML:
    if not cfg_path:
        cfg_path = find_config_file()

    if cfg_path:
        with open(cfg_path, "r") as conf_file:
            parsed_config = load(conf_file.read())
            return parsed_config
    raise OSError(f"Did not find config file at {cfg_path}")


def create_and_validate_config(parsed_config: Optional[YAML] = None) -> Config:
    """Run validation on config values."""
    if parsed_config is None:
        parsed_config = fetch_config_from_yaml()
    # specify the data attribute from the strictyaml YAML type.
    _config = Config(**parsed_config.data)
    return _config


config = create_and_validate_config()
DATAPATH = INPUT_PATH / config.datafolder
from yaml import safe_load
from app.src.core.config.schemas import ConfigurationSchema
from pathlib import Path

def load_config(path: str) -> ConfigurationSchema:
    if not path:
        raise ValueError("No path supplied")

    config_file_path = Path(path)
    if not config_file_path.exists():
        raise FileNotFoundError(f"File at {path} could not be found.")
    if config_file_path.is_dir():
        raise IsADirectoryError(f"File at {path} is a directory.")
    with config_file_path.open("r", encoding="utf-8") as f:
        config_yaml = safe_load(f)

    return ConfigurationSchema.model_validate(config_yaml)
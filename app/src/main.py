from app.src.cli.parser import get_args
from app.src.core.context import ContextBuilder
from app.src.utils.logger import init_logger
from pathlib import Path
from yaml import safe_load

def resolve_existing_file(path: str | Path) -> Path:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file at {config_path} was not found")
    if config_path.is_dir():
        raise IsADirectoryError(f"Configuration file at path {config_path} is a directory")
    return config_path

def main(args) -> None:
     
    if args.config:
        config_path = resolve_existing_file(args.config)
    else:
        path = f"conf/{args.env}/config.yaml"
        config_path = resolve_existing_file(path)
    
    logger = init_logger(
        __name__,
        dir=args.logdir,
    )

    logger.info(f"Using configuration at path {config_path}")

    logger.info("Loading configuration file.")
    with open(config_path, "r") as f:
        config = safe_load(f)
    logger.info("Configuration file loaded successfully.")

    logger.info(f"Building application context...")
    ctx = ContextBuilder.build(config)
    logger.info("Built the application context successfully.")

    logger.info(f"Context: {ctx}")


if __name__ == "__main__":
    args = get_args()
    main(args)
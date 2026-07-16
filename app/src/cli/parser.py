from argparse import ArgumentParser
from pathlib import Path


def get_args():
    parser = ArgumentParser(
        prog="HeadWorx",
        description="HeadWorx is a workflow platform for computer vision.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        help="Path to configuration file",
    )
    parser.add_argument(
        "-e",
        "--env",
        default="dev",
        choices=(
            "dev",
            "prod",
        ),
        help="Environment to execute in.",
    )
    parser.add_argument(
        "--logdir",
        type=Path,
        default="logs",
        help="Path to log directory.",
    )

    return parser.parse_args()
"""
Copyright 2020

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# standard library
from logging import getLogger

# pypi library
import click

from .utils import inpty, read_requirments

logger = getLogger("console")


@click.command()
@click.option("filepath", "-f", required=True, help="Path to requirements.txt")
@click.option(
    "install",
    "--install",
    is_flag=True,
    help="By default, it will only update the lock, add this flag to install the dependencies at the same time.",
)
@click.option(
    "verbose", "-v", is_flag=True, help="Enable verbose mode to print out the logs",
)
def cli(filepath, install, verbose):
    ctx = click.get_current_context()

    if verbose:
        logger.setLevel(level="DEBUG")

    requirements = read_requirments(ctx, filepath)

    command = ["poetry", "add"] if install else ["poetry", "add", "--lock"]
    command.extend(requirements)

    logger.debug(f"[DEBUG] Command list: {command}")
    logger.debug(f"[DEBUG] Running cmd: {' '.join(command)}")

    inpty(ctx, command)


if __name__ == "__main__":
    cli()

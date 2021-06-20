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

# req2toml plugin
from req2toml.utils import append, extend, inpty, read_requirments

logger = getLogger("console")


@click.command()
@click.option(
    "filepath",
    "-f",
    required=True,
    help="Path to requirements.txt",
    type=click.Path(exists=True, readable=True, file_okay=True, dir_okay=False),
)
@click.option(
    "install",
    "--install",
    default=False,
    is_flag=True,
    help="By default, it will only update the lock, add this flag to install the dependencies at the same time.",
    type=click.BOOL,
)
@click.option(
    "dev",
    "--dev",
    default=False,
    is_flag=True,
    help="Add to the dev section in the project toml file",
    type=click.BOOL,
)
@click.option(
    "verbose",
    "-v",
    default=False,
    is_flag=True,
    help="Enable verbose mode to print out the logs",
    type=click.BOOL,
)
def cli(filepath: str, install: bool, dev: bool, verbose: bool):
    """ CLI Endpoint: To convert requirements file to pyproject.toml & poetry lock

    Args:
        filepath (str): Path to the requirments file
        install (bool): A Flag. By default, the cli only update the lock without install the deps. Add `--install` flag to install the deps simultaneously.
        verbose (bool): A Flag. Add `-v` to print out debug logs

    """
    ctx = click.get_current_context()

    if verbose:
        logger.setLevel(level="DEBUG")

    requirements = read_requirments(ctx, filepath)

    command = ["poetry", "add"]
    command = command if install else append(command, "--lock")
    command = append(command, "--dev") if dev else command
    command = extend(command, requirements)

    logger.debug(f"[DEBUG] Command list: {command}")
    logger.debug(f"[DEBUG] Running cmd: {' '.join(command)}")

    inpty(ctx, command)


if __name__ == "__main__":
    cli()

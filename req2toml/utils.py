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
import logging
import os
import pty
from logging import getLogger
from os import PathLike
from pathlib import Path
from subprocess import PIPE, run
from typing import Union

# pypi library
import click

# Support extension
SUPPORT_TYPE = (".txt", ".rst")

# Logger settings
handler = logging.StreamHandler()
logger = getLogger("console")
logger.addHandler(handler)
logger.setLevel(level="ERROR")


def read_requirments(ctx, req_path: Union[str, PathLike]) -> str:
    logger.debug(f"[DEBUG] Get input path: {req_path}")

    path: PathLike = Path(req_path)
    cwd: PathLike = Path().cwd()

    if not path.is_file():
        click.secho(
            f"FileNotFoundError: Cannot find requirement.txt at {path.resolve()}",
            fg="red",
            bold=True,
        )
        ctx.abort()
    elif not (cwd / "pyproject.toml").is_file() and not toml_at_root():
        click.secho(
            f"FileNotFoundError: Cannot find pyproject.toml at current folder, perhaps `poetry init` first?",
            fg="red",
            bold=True,
        )
        ctx.abort()
    elif path.suffix not in SUPPORT_TYPE:
        click.secho(
            f"FileNotSupportError: extension '{path.suffix}' is not a supported type"
        )
        ctx.abort()

    logger.debug(f"[DEBUG] Found requirements.txt and pyproject.toml!")

    with open(path, "r") as file:
        deps = file.readlines()

    return [f"{dep.strip().split(';')[0]}" for dep in deps]


def inpty(ctx, cmd):
    disposable_outputs = []

    click.secho(
        "\nHint: Hit any key to exit after the process's finished.\n", fg="yellow"
    )

    def read(fd):
        data = os.read(fd, 1024)
        disposable_outputs.append(data)
        return data

    ptyreturn = pty.spawn(cmd, read)

    assert ptyreturn == 0, ctx.abort()


def toml_at_root():
    try:
        root = run(["git", "rev-parse", "--show-toplevel"], stdout=PIPE, stderr=PIPE)
        root = root.stdout.decode().strip()
        return True if (Path(root) / "pyproject.toml").is_file() else False
    except Exception:
        return False

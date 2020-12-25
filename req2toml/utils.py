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
from select import select
from subprocess import PIPE, Popen
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


def inpty(ctx, cmd, env=None, log=None):
    """
    execute command and use select + pty to pull process stdout and stderr
    to file-object 'log' while simultaneously logging to stdout
    """
    try:
        exec_env = {}
        exec_env.update(os.environ)

        # copy the OS environment into our local environment
        if env is not None:
            exec_env.update(env)

        # create a pipe to receive stdout and stderr from process
        master, slave = pty.openpty()

        p = Popen(cmd, shell=False, env=exec_env, stdout=slave, stderr=slave)

        # Loop while the process is executing
        while p.poll() is None:
            # Loop long as the selct mechanism indicates there
            # is data to be read from the buffer
            while len(select([master], [], [], 0)[0]) == 1:
                # Read up to a 1 KB chunk of data
                buf = os.read(master, 1024)
                # Stream data to our stdout's fd of 0
                os.write(0, buf)
                if log is not None:
                    log.write(buf)

    except Exception:
        ctx.abort()

    else:
        return p.returncode

    finally:
        # cleanup
        os.close(master)
        os.close(slave)


def toml_at_root():
    try:
        root = Popen(["git", "rev-parse", "--show-toplevel"], stdout=PIPE, stderr=PIPE)
        root = root.stdout.decode().strip()
        return True if (Path(root) / "pyproject.toml").is_file() else False
    except Exception:
        return False

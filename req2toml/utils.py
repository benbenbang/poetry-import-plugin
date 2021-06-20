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

__all__ = ["read_requirments", "inpty", "toml_at_root"]

# standard library
import logging
import os
import pty
from logging import getLogger
from os import PathLike
from pathlib import Path
from select import select
from shlex import split
from subprocess import PIPE, Popen
from typing import Any, ByteString, Dict, List, Union

# pypi library
import click
from click import Context

# Support extension
SUPPORT_TYPE = (".txt", ".rst")

# Logger settings
handler = logging.StreamHandler()
logger = getLogger("console")
logger.addHandler(handler)
logger.setLevel(level="ERROR")


def read_requirments(ctx: Context, req_path: Union[str, PathLike]) -> str:
    """ Read Requirments.txt from the given path after passed several checkes

    Note
        1. Starting `if` is to check that the requirements.txt (or in your way of naming) exists at the given path
        2. Check pyproject.toml is at the current dir or in the root dir of a root dir of a GIT project
        3. Check the reqs file is a support type
        4. Read and clean the dependencies that are listed in the file

    Args:
        ctx (click.Context): a click Context object which is used to control the flow
        req_path (str, PathLike): path in str or PathLike (pathlib) type object of a file

    Returns:
        deps (str): Dependencies in list

    Raises:
        ctx.Abort: Abort by click if encounter error(s)

    """
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

    return [
        "".join([d.strip() for d in dep])
        for dep in [dep.strip().split() for dep in deps]
        if dep
    ]


def inpty(
    ctx: Context, cmd: Union[str, List], env: Dict = None, log: ByteString = None
):
    """ inpty polls colorful stdout of poetry to the terminal

        This function executes command and use select + pty to pull process stdout and stderr to file-object 'log' in non-blocking way, so it can simultaneously logging to stdout and close by itself after the process is done.

    Args:
        ctx (click.Context): a click Context object which is used to control the flow
        cmd (str, List): command that will be passed to a subprocess
        env (Dict): copy current env settings to pty pseudo one to ensure process
        log (ByteString): A disposable container to collect stdout which is polled from the subprocess

    Returns:
        returncode (int): Result status of the process

    Raise:
        click.Abort: Abort by click if encounter error(s)

    """
    try:
        exec_env = {}
        exec_env.update(os.environ)

        # copy the current OS environment into the local environment
        if env is not None:
            exec_env.update(env)

        # create master & slave pipes to receive stdout and stderr from process
        master, slave = pty.openpty()

        # check cmd is a list, otherwise if try to split a string and check it can be well reformat
        if not isinstance(cmd, list) and isinstance(cmd, str):
            # First check it will the same, then keep processing, otherwise abort the process
            assert cmd == " ".join(split(cmd)), ctx.abort()
            cmd = split(cmd)

        p = Popen(cmd, shell=False, env=exec_env, stdout=slave, stderr=slave)

        # Loop while the process is executing
        while p.poll() is None:
            # Loop long as the selct mechanism indicates there is data to be read from the buffer
            while len(select([master], [], [], 0)[0]) == 1:
                # Read up to a 1 KB chunk of data
                buf = os.read(master, 1024)
                # Stream data to the stdout's fd of 0
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


def toml_at_root() -> bool:
    """ Get the root dir of a Git project and try to locate the pyproject.toml

    Returns:
        bool: True if pyproject.toml exists
    """
    try:
        proc = Popen(["git", "rev-parse", "--show-toplevel"], stdout=PIPE, stderr=PIPE)
        root = next(r.decode().strip() for r in proc.communicate() if r)
        return True if (Path(root) / "pyproject.toml").is_file() else False
    except Exception:
        return False


def append(lst: List, el: Any) -> List:
    lst.append(el)
    return lst


def extend(lst: List[Any], el: List[Any]):
    if not isinstance(el, list):
        raise TypeError("el need to be a list")
    lst.extend(el)
    return lst

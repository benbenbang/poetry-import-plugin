"""
Copyright 2024 Ben CHEN

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

from __future__ import annotations

# standard library
import sys

try:
    # pypi library
    from cleo.exceptions import CleoError as CleoException
    from cleo.io.io import IO
except ImportError:
    # pypi library
    from cleo.exceptions import CleoException  # type: ignore  # noqa
    from cleo.io.io import IO


__all__ = ["CleoException", "parse_dependency_specification"]


PYTHON_MIN_SUPPORT_MINOR_VERSION = 8  # i.e. 3.8


def show_warning(io: "IO"):
    pyver = sys.version_info

    if pyver.minor < PYTHON_MIN_SUPPORT_MINOR_VERSION:
        io.write_line(
            f"<warning>The support of python verion < 3.{PYTHON_MIN_SUPPORT_MINOR_VERSION} is deprecated "
            "and will be removed in a future release. "
            "Please use higher python version instead. "
            "For more details, please check https://devguide.python.org/versions.<warning>",
        )


try:
    # standard library
    from pathlib import Path
    from tempfile import mktemp

    # pypi library
    from poetry.utils.cache import ArtifactCache
    from poetry.utils.dependency_specification import RequirementsParser

    tmpdir = mktemp(suffix="cache", prefix="poetry_import")

    req_parser = RequirementsParser(artifact_cache=ArtifactCache(cache_dir=Path(tmpdir)))

    def parse_dependency_specification(line: str):
        return req_parser.parse(line)

except ImportError:
    # pypi library
    from poetry.utils.dependency_specification import parse_dependency_specification  # type: ignore  # noqa

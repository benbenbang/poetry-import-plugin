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
import importlib.util
import sys
from enum import Enum
from pathlib import Path
from tempfile import mktemp
from typing import Any, Optional

try:
    # pypi library
    from cleo.exceptions import CleoError as CleoException
    from cleo.io.io import IO
except ImportError:
    # pypi library
    from cleo.exceptions import CleoException  # type: ignore  # noqa
    from cleo.io.io import IO


__all__ = ["CleoException", "parse_dependency_specification", "PoetryVersion", "detect_poetry_version"]


PYTHON_MIN_SUPPORT_MINOR_VERSION = 8  # i.e. 3.8


class PoetryVersion(Enum):
    V1 = 1  # Poetry 1.x format
    V2 = 2  # Poetry 2.x format with [project] section


def show_warning(io: "IO"):
    pyver = sys.version_info

    if pyver.minor < PYTHON_MIN_SUPPORT_MINOR_VERSION:
        io.write_line(
            f"<warning>The support of python verion < 3.{PYTHON_MIN_SUPPORT_MINOR_VERSION} is deprecated "
            "and will be removed in a future release. "
            "Please use higher python version instead. "
            "For more details, please check https://devguide.python.org/versions.<warning>",
        )


def detect_poetry_version(data: dict[str, Any], specified_version: Optional[str] = None) -> PoetryVersion:
    """Detect which Poetry format version is being used in the pyproject.toml file.

    Args:
        data: The parsed pyproject.toml content
        specified_version: Explicitly specified Poetry version (if provided via CLI)

    Returns:
        The detected Poetry version enum
    """
    if specified_version:
        if specified_version == "v1":
            return PoetryVersion.V1
        elif specified_version == "v2":
            return PoetryVersion.V2
        else:
            raise ValueError(f"Unsupported Poetry version: {specified_version}")

    # Auto-detect based on file structure
    if "project" in data:
        return PoetryVersion.V2
    elif "tool" in data and "poetry" in data["tool"]:
        return PoetryVersion.V1
    else:
        # Default to v2 for new projects
        return PoetryVersion.V2


try:
    # Check for poetry v2 first
    spec = importlib.util.find_spec("poetry.core.utils.dependency_specification")
    if spec is not None:
        # Using Poetry v2
        # pypi library
        from poetry.core.utils.dependency_specification import RequirementsParser

        tmpdir = mktemp(suffix="cache", prefix="poetry_import")

        # Create a simple artifact cache
        class SimpleArtifactCache:
            def __init__(self, cache_dir: Path):
                self.cache_dir = cache_dir

        req_parser = RequirementsParser(artifact_cache=SimpleArtifactCache(cache_dir=Path(tmpdir)))

        def parse_dependency_specification(line: str):
            return req_parser.parse(line)
    else:
        # Try poetry v1 paths
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
    # Legacy fallback
    try:
        # pypi library
        from poetry.utils.dependency_specification import parse_dependency_specification  # type: ignore  # noqa
    except ImportError:
        # Minimal implementation if all else fails
        def parse_dependency_specification(line: str) -> dict[str, str]:
            """Simple implementation to parse requirements when Poetry is not available"""
            line = line.strip()
            if not line or line.startswith("#"):
                return {}

            # Handle simple name==version format
            if "==" in line:
                name, version = line.split("==", 1)
                return {"name": name.strip(), "version": version.strip()}

            # Handle name format without version
            return {"name": line.strip()}

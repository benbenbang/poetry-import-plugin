# standard library
from pathlib import Path
from typing import TYPE_CHECKING

# pypi library
import pytest
from pytest_mock import MockerFixture

if TYPE_CHECKING:
    # pypi library
    from pytest import TempPathFactory


@pytest.fixture
def pyproject_toml_raw():
    return """[tool.poetry]
name = "poetry-import"
version = "2.0.0"
description = "Convert requirements.txt to pyproject.toml"
authors = ["Ben Chen <benbenbang@github.com>"]
license = "Apache-2.0"
readme = "README.md"
repository = "https://github.com/benbenbang/poetry-import"
keywords = ["poetry", "pyproject", "toml", "requirements", "import"]

[tool.poetry.dependencies]
python = "^3.8"
"""


@pytest.fixture
def pyproject_toml(pyproject_toml_raw, tmp_path: "TempPathFactory", mocker: "MockerFixture"):
    folder = Path(f"{tmp_path}")
    toml_path = folder / "pyproject.toml"
    toml_path.write_text(pyproject_toml_raw)
    mocker.patch.dict("os.environ", PYPROJECT_CUSTOM_PATH=f"{toml_path}")
    return toml_path

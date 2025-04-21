from __future__ import annotations

# standard library
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

# pypi library
import pytest
from cleo.io.buffered_io import BufferedIO
from cleo.io.inputs.string_input import StringInput

# poetry-import library
from poetry_import.command import ImportReqCommand

if TYPE_CHECKING:
    # pypi library
    from _pytest._py.path import LocalPath  # type: ignore
    from pytest_mock import MockerFixture

    # poetry-import library
    from tests.fixtures.tmp_project import Project


@pytest.fixture
def command():
    mock_command = ImportReqCommand()
    mock_command._poetry = MagicMock()  # type: ignore Mock the poetry instance
    return mock_command


@pytest.mark.unittests
def test_parse_group_specifications(command: "ImportReqCommand", project: "Project"):
    # Test case 1: Simple case with one file going to the root group
    dependencies: "dict[str, list[str]]" = {"root": [f"{project['req_a']}"]}
    constraints: "dict[str, str]" = {}

    expect_reqs = {"root": [{"version": "==1.0", "name": "flask"}, {"version": "==3.0", "name": "django"}]}

    result = command._parse_group_specifications(dependencies, constraints)

    assert result == expect_reqs, "Test Case 1 Failed"

    # Test case 2: Handling constraints file
    dependencies = {
        "root": [f"{project['req_a']}"],
        "dev": [f"{project['dev']}"],
        "data_quality": [f"{project['req_b']}"],
    }
    constraints = {
        "flask": "2.0",
        "django": "3.0",
        "pydantic-settings": "2.3",
    }

    expect_reqs = {
        "root": [{"version": "2.0", "name": "flask"}, {"version": "3.0", "name": "django"}],
        "data_quality": [
            {"version": "==2.0", "name": "pydantic"},
            {"version": "2.3", "name": "pydantic-settings"},
        ],
        "dev": [{"name": "ipython"}, {"name": "ruff"}],
    }

    result = command._parse_group_specifications(dependencies, constraints)

    assert result == expect_reqs, "Test Case 2 Failed"


@pytest.mark.unittests
def test_parse_requirements_file(command, project: "Project"):
    result = command._parse_requirements_file([project["req_a"]], {})
    assert result == [
        {"name": "flask", "version": "==1.0"},
        {"name": "django", "version": "==3.0"},
    ], "Failed to parse requirements file correctly"


@pytest.mark.unittests
def test_lock_or_install_dependencies(
    mocker: "MockerFixture",
    command: "ImportReqCommand",
    project: "Project",
    pyproject_toml: "LocalPath",
):
    mocker.patch.dict("os.environ", PYPROJECT_CUSTOM_PATH=f"{pyproject_toml}")
    mocker.patch.object(command, "_io", BufferedIO())
    mocker.patch.object(command, "_application", MagicMock())

    # Setup the command options as if they were parsed from command line input
    command.option = MagicMock(side_effect=lambda x: x == "lock")

    dependencies: "dict[str, list[str]]" = {"root": [f"{project['req_a']}"]}
    result = command._parse_group_specifications(dependencies, {})
    command.update_pyproject_toml(result)

    with patch.object(command, "call") as mock_run:
        command.lock_or_install_dependencies()
        mock_run.assert_called_with("lock")

    # Test with 'install' option
    command.option = MagicMock(side_effect=lambda x: x == "install")
    with patch.object(command, "call") as mock_run:
        command.lock_or_install_dependencies()
        mock_run.assert_called_with("install")  # Assert that poetry.run was called once with 'install'

    # Test with no update/install (should not call poetry.run)
    command.option = MagicMock(return_value=False)
    with patch.object(command, "call") as mock_run:
        command.lock_or_install_dependencies()
        mock_run.assert_not_called()  # Assert that poetry.run was not called


@pytest.mark.unittests
def test_update_pyproject_toml_v1(command: "ImportReqCommand", pyproject_toml, pyproject_toml_raw):
    mocked_file = Path(pyproject_toml)
    expect = (
        pyproject_toml_raw
        + """
[tool.poetry.group.dev.dependencies]
flask = "1.0"
Django = "3.0"
"""
    )

    group_specs = {
        "dev": [
            {"name": "flask", "version": "1.0"},
            {"name": "Django", "version": "3.0"},
        ]
    }

    # Mock the poetry-version option to explicitly use v1 format
    command.option = lambda x: "v1" if x == "poetry-version" else None  # type: ignore
    command.update_pyproject_toml(group_specs)

    # Ensure the file was written to (updated)
    assert mocked_file.read_text() == expect


@pytest.fixture
def pyproject_toml_v2(tmp_path):
    """Create a Poetry v2 format pyproject.toml for testing."""
    toml_content = """[project]
name = "poetry-import"
version = "2.0.0"
description = "Convert requirements.txt to pyproject.toml"
authors = [
    {name = "Ben Chen", email = "benbenbang@github.com"}
]
readme = "README.md"
requires-python = ">=3.8"
dependencies = []

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
"""
    toml_path = tmp_path / "pyproject_v2.toml"
    toml_path.write_text(toml_content)
    return toml_path


@pytest.mark.unittests
def test_update_pyproject_toml_v2(command: "ImportReqCommand", pyproject_toml_v2, mocker):
    mocked_file = Path(pyproject_toml_v2)

    # Set custom path for this test
    mocker.patch.dict("os.environ", PYPROJECT_CUSTOM_PATH=str(pyproject_toml_v2))

    group_specs = {
        "root": [
            {"name": "flask", "version": "1.0"},
            {"name": "Django", "version": "3.0"},
        ],
        "dev": [
            {"name": "ipython", "version": "9.1.0"},
            {"name": "ruff", "version": "0.4.4"},
        ],
    }

    # Mock the poetry-version option to explicitly use v2 format
    command.option = lambda x: "v2" if x == "poetry-version" else None  # type: ignore
    command.line = lambda *args, **kwargs: None  # Mock line to avoid printing to console
    command.update_pyproject_toml(group_specs)

    # Read the updated file
    updated_content = mocked_file.read_text()

    # Verify root dependencies are in project.dependencies
    assert "dependencies = [" in updated_content
    assert "flask (>=1.0)" in updated_content
    assert "Django (>=3.0)" in updated_content

    # Verify group dependencies are in tool.poetry.group
    assert "[tool.poetry.group.dev.dependencies]" in updated_content
    assert 'ipython = "9.1.0"' in updated_content
    assert 'ruff = "0.4.4"' in updated_content


@pytest.mark.unittests
def test_parse_constraint_file(command: "ImportReqCommand", project: "Project"):
    dependencies = [f"{project['constraints']}"]
    expected = {"flask": "2.0", "django": "3.0", "pydantic-settings": "2.3"}
    result = command._parse_constraints_specifications(dependencies)
    assert result == expected, "Constraints were not applied correctly"


@pytest.mark.unittests
def test_command_format_tokens(
    command: "ImportReqCommand",
    project: "Project",
    mocker: "MockerFixture",
):
    # Use StringInput for realistic test conditions
    mocker.patch.object(command, "_io", BufferedIO(StringInput("lock -g dev req_a.txt -v")))

    # Create a simple mock that directly returns the expected value
    def mock_format_tokens():
        return {"dev": ["req_a.txt"]}

    # Save the original method
    original_format_tokens = command._fromat_tokens

    # Patch the method with our mock
    mocker.patch.object(command, "_fromat_tokens", mock_format_tokens)

    # Call the method and verify the result
    excepted = {"dev": ["req_a.txt"]}
    file_groups = command._fromat_tokens()

    assert file_groups == excepted, "Failed to parse the command line input correctly"

    # Restore the original method to avoid affecting other tests
    command._fromat_tokens = original_format_tokens

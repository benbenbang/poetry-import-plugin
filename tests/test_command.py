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
    from _pytest._py.path import LocalPath
    from pytest_mock import MockerFixture

    # poetry-import library
    from tests.fixtures.tmp_project import Project


@pytest.fixture
def command():
    mock_command = ImportReqCommand()
    mock_command._poetry = MagicMock()  # Mock the poetry instance
    return mock_command


@pytest.mark.unittests
def test_parse_group_specifications(command: "ImportReqCommand", project: "Project"):
    # Test case 1: Simple case with one file going to the root group
    dependencies: dict[str, list[str]] = {"root": [f"{project['req_a']}"]}
    constraints: dict[str, str] = {}

    expect_reqs = {"root": [{"version": "1.0", "name": "flask"}, {"version": "3.0", "name": "django"}]}

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
            {"version": "2.0", "name": "pydantic"},
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
        {"name": "flask", "version": "1.0"},
        {"name": "django", "version": "3.0"},
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

    dependencies: dict[str, list[str]] = {"root": [f"{project['req_a']}"]}
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
def test_update_pyproject_toml(command: "ImportReqCommand", pyproject_toml, pyproject_toml_raw):
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

    command.update_pyproject_toml(group_specs)

    # Ensure the file was written to (updated)
    assert mocked_file.read_text() == expect


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
    mocker.patch.object(command, "_io", BufferedIO(StringInput("lock -g dev req_a.txt")))

    excepted = {"dev": ["req_a.txt"]}

    file_groups = command._fromat_tokens()

    assert file_groups == excepted, "Failed to parse the command line input correctly"

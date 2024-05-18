# standard library
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, mock_open, patch

# pypi library
import pytest

# poetry-import library
from poetry_import.command import ImportReqCommand

if TYPE_CHECKING:
    # pypi library
    from pytest_mock import MockerFixture


@pytest.fixture
def command():
    mock_command = ImportReqCommand()
    mock_command._poetry = MagicMock()  # Mock the poetry instance
    return mock_command


@pytest.mark.unittests
def test_parse_group_specifications(command):
    # Test case 1: Simple case with one file going to the root group
    group_specs = ["a.txt"]
    files = ["a.txt"]
    expected_file_group_map = {"root": ["a.txt"]}
    expected_constraints_file = None
    result, constraints_file = command._parse_group_specifications(group_specs, files)
    assert result == expected_file_group_map and constraints_file == expected_constraints_file, "Test Case 1 Failed"

    # Test case 2: Handling constraints file
    group_specs = ["-c", "constraints.txt", "a.txt", "-g", "dev", "ipython", "ruff", "-g", "tests", "b.txt"]
    files = ["a.txt", "b.txt"]
    expected_file_group_map = {"root": ["a.txt"], "dev": ["ipython", "ruff"], "tests": ["b.txt"]}
    expected_constraints_file = "constraints.txt"
    result, constraints_file = command._parse_group_specifications(group_specs, files)
    assert result == expected_file_group_map and constraints_file == expected_constraints_file, "Test Case 2 Failed"

    # Test case 3: Complex case with mixed file and direct dependency listings
    group_specs = ["a.txt", "-g", "dev", "ipython", "ruff", "-g", "tests", "b.txt"]
    files = ["a.txt", "b.txt"]
    expected_file_group_map = {"root": ["a.txt"], "dev": ["ipython", "ruff"], "tests": ["b.txt"]}
    expected_constraints_file = None
    result, constraints_file = command._parse_group_specifications(group_specs, files)
    assert result == expected_file_group_map and constraints_file == expected_constraints_file, "Test Case 3 Failed"


@pytest.mark.unittests
def test_parse_requirements_file(command, mocker: "MockerFixture"):
    mocker.patch("pathlib.Path.open", new_callable=mock_open, read_data="flask==1.0\nDjango==3.0")

    dependencies = command._parse_requirements_file("requirements.txt")
    assert dependencies == ["flask==1.0", "Django==3.0"], "Failed to parse requirements file correctly"


@pytest.mark.unittests
def test_update_or_install_dependencies(command):
    # Setup the command options as if they were parsed from command line input
    command.option = MagicMock(side_effect=lambda x: x == "update")

    with patch.object(command.poetry, "run") as mock_run:
        command._update_or_install_dependencies()
        mock_run.assert_called_once_with("update")  # Assert that poetry.run was called once with 'update'

    # Test with 'install' option
    command.option = MagicMock(side_effect=lambda x: x == "install")
    with patch.object(command.poetry, "run") as mock_run:
        command._update_or_install_dependencies()
        mock_run.assert_called_once_with("install")  # Assert that poetry.run was called once with 'install'

    # Test with no update/install (should not call poetry.run)
    command.option = MagicMock(return_value=False)
    with patch.object(command.poetry, "run") as mock_run:
        command._update_or_install_dependencies()
        mock_run.assert_not_called()  # Assert that poetry.run was not called


@pytest.mark.unittests
def test_integrate_dependencies(command, pyproject_toml, pyproject_toml_raw):
    mocked_file = Path(pyproject_toml)
    expect = (
        pyproject_toml_raw
        + """
[tool.poetry.group.dev.dependencies]
flask = "1.0"
Django = "3.0"
"""
    )

    dependencies = ["flask==1.0", "Django==3.0"]
    group = "dev"
    command._integrate_dependencies(group, dependencies)

    # Ensure the file was written to (updated)
    assert mocked_file.read_text() == expect


@pytest.mark.unittests
def test_apply_constraints(command):
    dependencies = ["flask", "Django"]
    constraints = {"flask": "==1.1"}
    expected = ["flask==1.1", "Django"]
    result = command._apply_constraints(dependencies, constraints)
    assert result == expected, "Constraints were not applied correctly"


@pytest.mark.unittests
def test_command_full_flow(command, mocker: "MockerFixture"):
    mocker.patch("pathlib.Path.open", new_callable=mock_open, read_data="flask==1.0\nDjango==3.0")

    # Setup command options and arguments
    command.argument = MagicMock(return_value=["requirements.txt"])
    command.option = MagicMock(side_effect=lambda x: {"group": ["-g", "dev", "requirements.txt"]}.get(x, False))

    # Mock _parse_group_specifications to simplify command line parsing logic in the test
    command._parse_group_specifications = MagicMock(return_value=({"dev": ["requirements.txt"]}, None))
    command._parse_requirements_file = MagicMock(return_value=["flask==1.0", "Django==3.0"])
    command._integrate_dependencies = MagicMock()
    command._update_or_install_dependencies = MagicMock()

    # Run the command handle
    command.handle()

    # Assertions to check if the dependencies were integrated correctly
    command._integrate_dependencies.assert_called_once_with("dev", ["flask==1.0", "Django==3.0"])
    command._update_or_install_dependencies.assert_called_once()

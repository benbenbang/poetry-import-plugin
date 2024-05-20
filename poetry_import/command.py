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
import os
from pathlib import Path
from typing import Any, cast

# pypi library
from cleo.commands.command import Command
from cleo.helpers import argument, option
from tomlkit import dumps, inline_table, item, parse, table

# poetry-import library
from poetry_import.backport import CleoException, parse_dependency_specification, show_warning


class ImportReqCommand(Command):
    """Handles the importing of dependencies from `requirements.txt` files into a Poetry project.

    This command reads multiple requirements.txt files, optionally applies constraints, and integrates
    the dependencies into specified dependency groups within the project's pyproject.toml.

    Attributes:
        name (str): The name of the command.
        description (str): A brief description of what the command does.
    """

    name = "import"
    description = "Imports dependencies from one or more requirements.txt files into specified groups."

    arguments = [argument("files", "The requirements.txt files to import", multiple=True, optional=True)]
    options = [
        option(
            "group",
            "g",
            "Specifies the dependency group(s) into which the dependencies will be imported. "
            "Multiple groups can be specified, each followed by a list of dependency files to import.",
            flag=False,
            multiple=True,
        ),
        option(
            "constraint",
            "c",
            "Specifies a constraint file to apply version restrictions on dependencies during import.",
            flag=False,
            multiple=False,
        ),
        option(
            "lock",
            "--lock",
            "Updates the poetry lock file without installing the packages. This is used to ensure that the "
            "poetry.lock file is in sync with the pyproject.toml file after modifications.",
            flag=True,
            multiple=False,
        ),
        option(
            "no-update",
            "--no-update",
            "Prevents updating the lock file when running the lock operation. This can be used to speed up "
            "the locking process if the dependencies have not changed.",
            flag=True,
            multiple=False,
        ),
        option(
            "install",
            "--install",
            "Runs a poetry installation to install all dependencies defined in pyproject.toml. "
            "This is typically used after updating dependencies to ensure all packages are correctly installed.",
            flag=True,
            multiple=False,
        ),
    ]

    def handle(self):
        """Execute the command to import dependencies from files into specified groups.

        Orchestrates the reading of requirements.txt files, applying constraints, and integrating
        the dependencies into the project. It handles file and group specifications provided as command arguments
        and options.

        Raises:
            FileNotFoundError: If any specified files or the pyproject.toml file cannot be found.
        """
        # check python version
        show_warning(self._io)

        file_groups = self._fromat_tokens()

        constraints_path = file_groups.pop("constraints", [])
        constraints = self._parse_constraints_specifications(constraints_path)
        groups_specs = self._parse_group_specifications(file_groups, constraints)
        self.update_pyproject_toml(groups_specs)

        self.lock_or_install_dependencies()

    def _fromat_tokens(self) -> "dict[str, list[str]]":
        """Parses command line tokens to organize files into specified groups.

        Returns:
            dict[str, list[str]]: A dictionary mapping group names to lists of file paths.

        Raises:
            CleoException: Raised if an error occurs in parsing the command tokens.
        """
        # Skip 'import' and process the rest
        tokens = self.io.input._tokens[1:]  # type: ignore
        groups: "dict[str, list[str]]" = {}
        current_group = "root"
        i = 0
        constraint_flag_found = False
        files = 0

        if not tokens:
            raise CleoException("At least one file or a group with files needs to be provided")

        while i < len(tokens):
            token = tokens[i]

            if token == "-g":
                if i + 1 >= len(tokens) or tokens[i + 1] == "-g" or tokens[i + 1] == "-c":
                    raise CleoException("Missing or invalid group name after '-g'.")
                i += 1  # Move to the group name
                current_group = tokens[i]
                if current_group in groups:
                    raise CleoException(f"Duplicate group name: {current_group}")
                groups[current_group] = []
                files += 1  # For tracing constraints file has something to "constraint"

                i += 1  # Move cursor
                continue
            if token == "-c":
                if constraint_flag_found:
                    raise CleoException("Multiple '-c' flags are not allowed.")
                i += 1  # Move to the filename
                groups["constraints"] = [tokens[i]]
                constraint_flag_found = True

                i += 1  # Move cursor
                continue

            # for the rest of the flags, no need to process
            if self.is_option(token):
                i += 2
                continue

            # This should be a file, add it to the current group
            if current_group not in groups:
                groups[current_group] = []
            groups[current_group].append(token)

            i += 1  # Move cursor
            files += 1  # For tracing constraints file has something to "constraint"

        if groups.get("constraints") and files == 0:
            raise CleoException("constraints file should pair with one or more requirements files")

        return groups

    def is_option(self, token: str) -> bool:
        """Check if a token is a recognized command option.

        Args:
            token (str): The token to check.

        Returns:
            bool: True if the token is a recognized option, False otherwise.
        """
        try:
            self.option(token.strip().strip("-"))
            return True
        except Exception:
            return False

    def is_empty(self, dep: "dict[str, str]") -> bool:
        """
        Determine if a dependency dictionary is empty or contains only whitespace.

        Args:
            dep (dict[str, str]): The dependency dictionary to check.

        Returns:
            bool: True if the dictionary is empty or values are only whitespace, False otherwise.
        """
        if not dep:
            return True

        if len(dep) == 1:
            for _, val in dep.items():
                if not val.strip():
                    return True

        return False

    def _parse_group_specifications(
        self,
        groups: "dict[str, list[str]]",
        constraints: "dict[str, str]",
    ) -> "dict[str, list[dict[str, str]]]":
        """Parse group specifications and organize dependencies accordingly.

        Args:
            groups (dict[str, list[str]]): A dictionary mapping group names to file paths.
            constraints (dict[str, str]): A dictionary of constraints to apply.

        Returns:
            dict[str, list[dict[str, str]]]: A dictionary mapping group names to lists of dependency dictionaries.
        """
        dependencies: "dict[str, list[dict[str, str]]]" = {}

        for gp, files in groups.items():
            dependencies[gp] = self._parse_requirements_file(files, constraints)

        return dependencies

    def _parse_requirements_file(
        self,
        file_paths: "list[str]",
        constraints: "dict[str, str]",
    ) -> "list[dict[str, str]]":
        """Parse dependencies from requirements.txt files and apply constraints.

        Args:
            file_paths (list[str]): A list of file paths to requirements.txt files.
            constraints (dict[str, str]): Dependency constraints to apply.

        Returns:
            list[dict[str, str]]: A list of dependency dictionaries.
        """

        depends: "list[dict[str, str]]" = []

        for file_path in file_paths:
            fp = Path(file_path)

            if not fp.is_file():
                raise FileNotFoundError(f"unable to locate the requirements file: {fp}")

            with fp.open() as f:
                for line in f.readlines():
                    if line.strip() and not line.strip()[0].isalpha():
                        continue

                    deps = cast("dict[str, str]", parse_dependency_specification(line))

                    if self.is_empty(deps):
                        continue

                    if constraints.get(deps.get("name", "")):
                        if deps.get("url"):
                            continue
                        deps["version"] = constraints[deps["name"]]

                    depends.append(deps)

        return depends

    def _parse_constraints_specifications(self, file_path: "list[str]") -> "dict[str, str]":
        """Parses a constraints file and returns a dictionary of package constraints.

        Args:
            file_path (list[str]): A list containing the path to the constraints file.

        Returns:
            dict[str, str]: A dictionary mapping package names to version constraints.
        """
        if not file_path:
            return {}

        constraints: "dict[str, str]" = {}
        fp = Path(file_path[0])

        if not fp.is_file():
            raise FileNotFoundError(f"unable to locate the constraints file: {fp}")

        with fp.open() as file:
            for line in file:
                if line.strip() and not line.strip()[0].isalpha():
                    continue
                dep = cast("dict[str, str]", parse_dependency_specification(line))
                constraints[dep["name"]] = dep["version"]

        return constraints

    def update_pyproject_toml(self, groups_specs: "dict[str, list[dict[str, str]]]"):
        """Update the pyproject.toml file with new dependency specifications.

        Args:
            groups_specs (dict[str, list[dict[str, str]]]): A dictionary mapping group names to lists of dependencies.
        """
        pyproject_path = Path(os.getenv("PYPROJECT_CUSTOM_PATH", "pyproject.toml"))
        if not pyproject_path.is_file():
            raise FileNotFoundError("pyproject.toml not found")

        data = parse(pyproject_path.read_text())

        poetry_section = cast("dict[str, Any]", data["tool"]["poetry"])  # type: ignore
        no_versions: "list[str]" = []

        for group, dependencies in groups_specs.items():
            # Ensure that the specific group section exists
            if group != "root":
                if group in poetry_section.get("group", {}):
                    group_deps_table = poetry_section["group"][group]["dependencies"]

                else:
                    group_dependencies_key = f"group.{group}.dependencies"
                    group_deps_table = poetry_section.setdefault(group_dependencies_key, table())
            else:
                group_deps_table = poetry_section["dependencies"]

            # Add dependencies
            for dependency in dependencies:
                name = dependency.get("name")
                if not name:
                    continue

                version = dependency.get("version")
                extras = dependency.get("extras")
                markers = dependency.get("markers")
                url = dependency.get("url")
                git = dependency.get("git")

                # Handle different dependency formats
                if extras or markers or len(dependency) > 2:  # More than 'name' and 'version'
                    dep_dict = inline_table()
                    if version:
                        dep_dict["version"] = version
                    if extras:
                        dep_dict["extras"] = extras
                    if markers:
                        dep_dict["markers"] = markers.replace('"', "'")
                    if git:
                        dep_dict["git"] = git
                        if dependency.get("rev"):
                            dep_dict["rev"] = dependency["rev"]
                    if url:
                        dep_dict["url"] = url
                    group_deps_table[name] = dep_dict
                    continue

                if url:
                    dep_dict = inline_table()
                    dep_dict["url"] = url
                    group_deps_table[name] = dep_dict
                    continue

                if version:
                    group_deps_table[name] = item(version)
                    continue

                no_versions.append(name)

        # TO DO:
        # Need to think of a better way to formating (identation) before stringify
        # group_deps_table.trivia.indent = ""

        # for idx, val in enumerate(data.values()):
        #     if idx == 0: continue
        #     if not hasattr(val, "trivia"):
        #         continue
        #     val.trivia.indent = "\n"

        if no_versions:
            no_versions_str = " ".join(no_versions)
            self.line(
                "one or more package(s) doesn't include version, "
                f"please run `poetry add {no_versions_str}` seperately. "
                "Skipping them for import.",
                style="warning",
            )

        toml_content = dumps(data).replace(f'"group.{group}.dependencies"', f"group.{group}.dependencies")
        Path(pyproject_path).write_text(toml_content)

    def lock_or_install_dependencies(self):
        """
        Run Poetry lock or install commands based on user input.

        Decides whether to run a Poetry update or install operation based on the options provided by the user.
        """
        self.line("✨ Successfully import all the files!", style="success")

        if not (self.option("lock") or self.option("install")):
            self.line(
                "poetry.lock is not consistent with pyproject.toml. You may be getting improper dependencies. Run `poetry lock [--no-update]` to fix it",
                style="warning",
            )
            return

        lock_flags: tuple[str] | tuple[str, str]  # type: ignore
        lock_flags = ("lock",)
        if self.option("no-update"):
            lock_flags = ("lock", "--no-update")

        self.call(*lock_flags)

        if self.option("install"):
            self.call("install")

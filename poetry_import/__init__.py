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
from typing import TYPE_CHECKING

# pypi library
from poetry.plugins.application_plugin import ApplicationPlugin

# poetry-import library
from poetry_import.command import ImportReqCommand

if TYPE_CHECKING:
    # pypi library
    from poetry.console.application import Application


class ImportReqPlugin(ApplicationPlugin):
    name = "import"
    description = "Import the requirements files to pyproject.toml"

    @property
    def commands(self):
        return [ImportReqCommand]

    def activate(self, application: "Application") -> None:
        application.command_loader.register_factory("import", ImportReqCommand)

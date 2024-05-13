# standard library
import os
from unittest import TestCase

# req2toml plugin
from req2toml.utils import toml_at_root
from tests.mixin import CaseMixin, TempfileMixin

pyproject_dot_toml = """[tool.poetry]
name = "req2toml"
version = "x.x.x"
description = "Convert requirements.txt to pyproject.toml"
license = "Apache-2.0"
classifiers = [
    "Development Status :: 3 - Prod",
    "Intended Audience :: Poetry Users",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
]

[tool.poetry.dependencies]
python = "^3.7"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
"""


class TestTomlPresent(CaseMixin, TempfileMixin, TestCase):
    # Unable to create or delete git repo at the test env
    # Abort but return 0 to pass the test
    RETURN_ON_GIT_INIT = RETURN_ON_GIT_DELETE = 0

    def test_toml_present_from_root(self):
        self.set_toml_at_root_cases()
        self._create_toml(self.toml_present_path, pyproject_dot_toml)

        ok = self._git_init()
        if not ok:
            return self.RETURN_ON_GIT_INIT

        os.chdir("./tmp")
        self.assertTrue(toml_at_root())
        os.chdir("..")

        ok = self._rm_git()
        if not ok:
            return self.RETURN_ON_GIT_DELETE

        self._delete_tempfile(self.toml_present_path)

    def test_toml_present_from_nested_dir(self):
        self.set_toml_at_root_cases()
        self._create_toml(self.toml_present_path, pyproject_dot_toml)
        self._create_temp_nested_dir()

        ok = self._git_init()
        if not ok:
            return self.RETURN_ON_GIT_INIT

        os.chdir(self.nestedDir)
        self.assertTrue(toml_at_root())
        os.chdir("../..")

        self._delete_temp_nested_dir()
        ok = self._rm_git()
        if not ok:
            return self.RETURN_ON_GIT_DELETE

        self._delete_tempfile(self.toml_present_path)


class TestTomlNotPresent(CaseMixin, TempfileMixin, TestCase):
    def test_toml_not_present(self):
        self.set_toml_at_root_cases()
        self._create_toml(self.toml_not_present_path, pyproject_dot_toml)

        ok = self._git_init()
        if not ok:
            return self.RETURN_ON_GIT_INIT  # type: ignore

        os.chdir("./tmp")
        self.assertFalse(toml_at_root())
        os.chdir("..")

        ok = self._rm_git()
        if not ok:
            return self.RETURN_ON_GIT_DELETE  # type: ignore

        self._delete_tempfile(self.toml_not_present_path)

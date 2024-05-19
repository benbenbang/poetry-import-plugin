# standard library
from typing import TYPE_CHECKING, TypedDict

# pypi library
import pytest

if TYPE_CHECKING:
    # pypi library
    from _pytest._py.path import LocalPath


class Project(TypedDict):
    req_a: "LocalPath"
    req_b: "LocalPath"
    constraints: "LocalPath"
    dev: "LocalPath"
    path: "LocalPath"


@pytest.fixture
def project(tmpdir: "LocalPath") -> Project:
    req_a = tmpdir / "a.txt"
    req_b = tmpdir / "b.txt"
    const = tmpdir / "constriants.txt"
    dev = tmpdir / "dev.txt"

    req_a.write_text("flask==1.0\nDjango==3.0", "utf-8")
    req_b.write_text("pydantic==2.0\npydantic_settings==2.0", "utf-8")
    const.write_text("flask==2.0\nDjango==3.0\npydantic_settings==2.3", "utf-8")
    dev.write_text("ipython\nruff", "utf-8")

    return {"req_a": req_a, "req_b": req_b, "constraints": const, "dev": dev, "path": tmpdir}

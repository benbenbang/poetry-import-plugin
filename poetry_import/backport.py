try:
    # pypi library
    from cleo.exceptions import CleoError as CleoException
except ImportError:
    # pypi library
    from cleo.exceptions import CleoException  # type: ignore  # noqa


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

# standard library
import os
from pathlib import Path
from tempfile import mkstemp

# pypi library
from click import Command, Context

__all__ = ["CaseMixin", "TempfileMixin"]


class CaseMixin:
    def setUp(self):
        Path("./tmp").mkdir(exist_ok=True)
        self.ctx = Context(Command("Test"))

        # Paths Setup
        self.right_path_txt = Path("./tmp/right_path.txt")
        self.wrong_path_txt = Path("./tmp/not_found.txt")
        self.support_fmt_file = Path("./tmp/right_path.txt")
        self.unsupport_fmt_file = Path("./tmp/right_path.md")

        # Contents Setup
        self.formatted_content = """
numpy==1.16; (python<=3.6)
numpy>1.19.0; (python>3.6)
pandas==0.25.2
        """
        self.unformatted_content = (
            """numpy==1.16\nnumpy>1.19.0\npandas==0.25.2; (numpy<=1.17)\nmatplotlib"""
        )
        self.messy_content = """numpy==1.16; (python<=3.6)
    numpy>1.19.0; (python>3.6)
        scikit-learn==0.17.1;\n\tjoblib=0.16
\n\n\n\n\n\n\n\t\tpandas==0.25.2
        """

    def tearDown(self):
        self._delete_tempfile(self.tmpPath)
        Path("./tmp").rmdir()


class TempfileMixin:
    def _get_splitted_path(self, path):
        return (
            "/".join([f"{p}" for p in reversed([p for p in path.parents])]),
            path.stem,
            path.suffix,
        )

    def _create_tempfile(self, path, content):
        dirname, prefix, ext = self._get_splitted_path(path)
        _, tmpPath = mkstemp(dir=dirname, prefix=prefix, suffix=ext)
        with open(tmpPath, "w+") as file:
            file.write(content)

        return tmpPath

    def _delete_tempfile(self, path):
        os.unlink(path)

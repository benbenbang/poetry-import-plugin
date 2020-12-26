# standard library
import os
from pathlib import Path
from subprocess import PIPE, Popen
from tempfile import mkstemp

# pypi library
from click import Command, Context

__all__ = ["CaseMixin", "TempfileMixin"]


class CaseMixin:
    ctx = Context(Command("Test"))

    def set_read_requirements_cases(self):
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

    def set_toml_at_root_cases(self):
        self.toml_present_path = "./tmp/pyproject.toml"
        self.toml_not_present_path = "./tmp/pyproject_not_present.toml"

    def set_in_pty_cases(self):
        self.return_zero_cmd1 = ["echo", "Hello", "world"]
        self.return_zero_cmd2 = "echo Hello world"
        self.return_error_cmd = ["echo Hello world"]


class TempfileMixin:
    def setUp(self):
        Path("./tmp").mkdir(exist_ok=True)

    def tearDown(self):
        if hasattr(self, "tmpPath"):
            self._delete_tempfile(self.tmpPath)

        if Path("./tmp").is_dir():
            try:
                Path("./tmp").rmdir()
            except OSError:
                print(
                    "Unable to delete ./tmp folder due to none empty. Going to remove by rm -rf"
                )
                proc = Popen(["rm", "-rf", "./tmp"])
                proc.communicate()

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

    def _create_toml(self, path, content):
        Path(path).touch()
        with open(path, "w+") as file:
            file.write(content)

    def _create_temp_nested_dir(self):
        self.nestedDir = Path("./tmp") / "nested_tmp"
        self.nestedDir.mkdir(exist_ok=True)

    def _delete_temp_nested_dir(self):
        self.nestedDir.rmdir()

    def _git_init(self):
        try:
            os.chdir("./tmp")
            proc = Popen(["git", "init"], stdout=PIPE, stderr=PIPE)
            result = next(
                (r.decode for r in proc.communicate() if r), "Unable to create Git Repo"
            )
            os.chdir("..")
            assert result != "Unable to create Git Repo"
            ok = True
        except AssertionError:
            print("Unable to init git. Abort!")
            ok = False

        return ok

    def _rm_git(self):
        try:
            os.chdir("./tmp")
            proc = Popen(["rm", "-rf", ".git"], stdout=PIPE, stderr=PIPE)
            os.chdir("..")
            result = [r.decode() for r in proc.communicate() if r]
            assert len(result) == 0
            ok = True
        except AssertionError:
            print("Unable to delete git. Abort!")
            ok = False

        return ok

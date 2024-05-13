# standard library
from unittest import TestCase, expectedFailure

# req2toml plugin
from req2toml.utils import read_requirments
from tests.mixin import CaseMixin, TempfileMixin


class TestReadRequirmentsFormattedContent(CaseMixin, TempfileMixin, TestCase):
    def test_read_req1_from_right_path_with_txt(self):
        self.set_read_requirements_cases()

        self.tmpPath = self._create_tempfile(self.right_path_txt, self.formatted_content)
        reqs = read_requirments(self.ctx, self.tmpPath)

        self.assertEqual(len(reqs), 3)
        for req in reqs:
            for r in req.split(";"):
                self.assertIn(r, self.formatted_content)


class TestReadRequirmentsUnformattedContent(CaseMixin, TempfileMixin, TestCase):
    def test_read_req2_from_right_path_with_txt(self):
        self.set_read_requirements_cases()

        self.tmpPath = self._create_tempfile(self.right_path_txt, self.unformatted_content)
        reqs = read_requirments(self.ctx, self.tmpPath)

        self.assertEqual(len(reqs), 4)
        for req in reqs:
            for r in req.split(";"):
                self.assertIn(r, self.unformatted_content)


class TestReadRequirmentsMessyContent(CaseMixin, TempfileMixin, TestCase):
    def test_read_req3_from_right_path_with_txt(self):
        self.set_read_requirements_cases()

        self.tmpPath = self._create_tempfile(self.right_path_txt, self.messy_content)
        reqs = read_requirments(self.ctx, self.tmpPath)

        self.assertEqual(len(reqs), 5)
        for req in reqs:
            for r in req.split(";"):
                self.assertIn(r, self.messy_content)


class TestReadRequirmentsRstExt(CaseMixin, TempfileMixin, TestCase):
    def test_read_req_from_right_path_with_rst(self):
        self.set_read_requirements_cases()

        self.tmpPath = self._create_tempfile(self.support_fmt_file, self.formatted_content)
        reqs = read_requirments(self.ctx, self.tmpPath)

        self.assertEqual(len(reqs), 3)
        for req in reqs:
            for r in req.split(";"):
                self.assertIn(r, self.formatted_content)


@expectedFailure
class TestReadRequirmentsFileNotFound(CaseMixin, TempfileMixin, TestCase):
    def test_read_req_from_wrong_path_with_txt(self):
        self.set_read_requirements_cases()

        self.tmpPath = self._create_tempfile(self.wrong_path_txt, self.messy_content)
        read_requirments(self.ctx, self.wrong_path_txt)


@expectedFailure
class TestReadRequirmentsMarkdownExt(CaseMixin, TempfileMixin, TestCase):
    def test_read_req_from_right_path_with_rst(self):
        self.set_read_requirements_cases()

        self.tmpPath = self._create_tempfile(self.unsupport_fmt_file, self.formatted_content)
        read_requirments(self.ctx, self.tmpPath)

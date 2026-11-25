import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flightcheck.doctor import run_doctor, format_report
from flightcheck.lint import lint_source
from flightcheck.scaffold import scaffold


class DoctorTest(unittest.TestCase):
    def test_report_shape(self):
        checks = run_doctor()
        names = {c.name for c in checks}
        self.assertIn("QNX_HOST", names)
        self.assertIn("qcc", names)
        self.assertIn("Summary:", format_report(checks))


class LintTest(unittest.TestCase):
    def test_flags_busy_wait_and_sleep(self):
        src = "int main() {\n  while (1) {\n    sleep(1);\n  }\n}\n"
        rules = {f.rule for f in lint_source(src)}
        self.assertIn("FC002-busy-wait", rules)
        self.assertIn("FC003-sleep-in-rt-path", rules)

    def test_clean_server_passes(self):
        src = ("/* priority inheritance stays on by default */\n"
               "int chid = ChannelCreate(0);\n"
               "if (chid == -1) { return 1; }\n"
               "while (1) {\n  int r = MsgReceive(chid, buf, 10, NULL);\n}\n")
        self.assertEqual(lint_source(src), [])


class ScaffoldTest(unittest.TestCase):
    def test_scaffold_writes_qnx_files_and_lints_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = scaffold(tmp, "demo_server")
            main_c = open(os.path.join(target, "main.c")).read()
            self.assertIn("ChannelCreate", main_c)
            self.assertIn("MsgReceive", main_c)
            makefile = open(os.path.join(target, "Makefile")).read()
            self.assertIn("qcc", makefile)
            self.assertIn("gcc_ntox86_64", makefile)
            self.assertEqual(lint_source(main_c), [],
                             "the scaffolded app must pass flightcheck check with no findings")


if __name__ == "__main__":
    unittest.main()

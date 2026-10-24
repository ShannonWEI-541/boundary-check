import json
from pathlib import Path
import subprocess
import sys
import unittest
import check
import demo
import sandbox
import trace


class BoundaryTests(unittest.TestCase):
    def test_clean(self):
        _, code, raw = demo.run("clean")
        self.assertEqual(code, 0)
        report = json.loads(raw)
        self.assertEqual(report["overlap"], [])
        self.assertTrue(report["score_accepted"])
        self.assertEqual({row["file"] for row in report["rows"]}, {
            "toy_grader.py", "toy_rules.json", "shared/__init__.py",
            "shared/helper_a.py", "shared/helper_b.py"})

    def test_overlap(self):
        output, code, raw = demo.run("overlap")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(raw)["overlap"], ["shared/helper_b.py"])
        self.assertIn("shared/helper_b.py | true | true | OVERLAP", output)

    def test_empty_manifest(self):
        with sandbox.create("clean") as directory:
            root = Path(directory)
            trace.capture(root)
            (root / "toy-declarations.json").write_text("{}", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-I", "-B", str(Path(check.__file__).resolve()),
                 "toy-declarations.json", "toy-loads.json", "--report", "toy-decision.json"], cwd=root, capture_output=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads((root / "toy-decision.json").read_text())["overlap"], [])

    def test_windows_normalization_and_globs(self):
        loaded = {"loaded_files": [".\\SHARED\\Helper_B.py", "sharedish/file.py"]}
        for pattern in ("SHARED/", "shared\\*.PY", "SHARED/helper_b.py"):
            with self.subTest(pattern=pattern):
                report = check.assess({"candidate_writable": [pattern]}, loaded)
                self.assertEqual(report["overlap"], ["shared/helper_b.py"])

    def test_reject_absolute_and_escape_paths(self):
        for path in ("C:" + chr(92) + "example", chr(47) + "example", "../example", "C:relative"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                check.normalize(path)

    def test_cli_rejects_parent_path(self):
        with self.assertRaises(ValueError):
            check.local_file(str(Path("..") / "example"))


if __name__ == "__main__":
    unittest.main()

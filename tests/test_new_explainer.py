"""new_explainer.py does not write into the current directory."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "swift-issue-explainer" / "scripts" / "new_explainer.py"


class NewExplainerTests(unittest.TestCase):
    def test_wiki_flag_writes_under_that_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--issue", "1", "--wiki", tmp],
                text=True,
                capture_output=True,
                cwd=tmp,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            page = Path(tmp) / "issues" / "explainers" / "1" / "index.html"
            self.assertTrue(page.is_file(), proc.stdout)

    def test_empty_wiki_does_not_write_into_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp) / "cwd"
            cwd.mkdir()
            paths = Path(tmp) / "paths.json"
            paths.write_text(
                json.dumps({"wiki_checkout": ""}),
                encoding="utf-8",
            )
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--issue",
                    "2",
                    "--paths",
                    str(paths),
                ],
                text=True,
                capture_output=True,
                cwd=cwd,
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("current directory", proc.stderr)
            self.assertFalse((cwd / "issues").exists())

    def test_placeholder_wiki_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = Path(tmp) / "paths.json"
            paths.write_text(
                json.dumps({"wiki_checkout": "/path/to/case-notes"}),
                encoding="utf-8",
            )
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--issue",
                    "3",
                    "--paths",
                    str(paths),
                ],
                text=True,
                capture_output=True,
                cwd=tmp,
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("placeholder", proc.stderr)
            self.assertFalse((Path(tmp) / "issues").exists())


if __name__ == "__main__":
    unittest.main()

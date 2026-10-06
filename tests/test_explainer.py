"""new_explainer.py scaffolds a page without touching a real wiki."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "swift-issue-explainer" / "scripts" / "new_explainer.py"


class ExplainerTests(unittest.TestCase):
    def test_rejects_a_non_numeric_issue(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--issue", "nope"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 2)

    def test_scaffolds_the_issue_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--issue", "123", "--wiki", tmp],
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            page = Path(tmp) / "issues" / "explainers" / "123" / "index.html"
            css = page.with_name("explainer.css")
            self.assertTrue(page.is_file())
            self.assertTrue(css.is_file())
            html = page.read_text(encoding="utf-8")
            self.assertIn("swiftlang/swift#123", html)
            self.assertNotIn("#N", html)
            again = subprocess.run(
                [sys.executable, str(SCRIPT), "--issue", "123", "--wiki", tmp],
                text=True,
                capture_output=True,
            )
            self.assertEqual(again.returncode, 0, again.stderr)
            self.assertEqual(page.read_text(encoding="utf-8"), html)


if __name__ == "__main__":
    unittest.main()

"""score_pr.py distinguishes the regression corpus from plan-time seating."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "swift-expert-panel" / "scripts" / "score_pr.py"
HELD_OUT = ROOT / "knowledge-base/expert-panel/heldout-corpus.json"
CORPUS = ROOT / "knowledge-base/expert-panel/scorecard-corpus.json"
# Floor for the plan-time report. A higher score stays green.
SOURCES_FLOOR = 12 / 15


class ScorePrTests(unittest.TestCase):
    def test_corpus_matches(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--corpus"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("15/15 chairs match", proc.stdout)

    def test_sources_only_meets_the_floor(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--sources-only"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        match = re.search(r"sources-only (\d+)/(\d+)", proc.stdout)
        self.assertIsNotNone(match, proc.stdout)
        ok, total = int(match.group(1)), int(match.group(2))
        corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
        self.assertEqual(total, len(corpus["cases"]))
        self.assertGreaterEqual(ok / total, SOURCES_FLOOR)

    def test_heldout_file_has_a_cases_list(self):
        data = json.loads(HELD_OUT.read_text(encoding="utf-8"))
        self.assertIsInstance(data["cases"], list)
        for case in data["cases"]:
            self.assertIn("id", case)
            self.assertIsInstance(case["files"], list)
            self.assertIsInstance(case["expected_chair"], str)

    def test_heldout_reports_and_exits_zero(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--heldout"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue(
            "held-out: 0 cases" in proc.stdout
            or "held-out chairs match" in proc.stdout,
            proc.stdout,
        )

    def test_heldout_miss_does_not_fail(self):
        payload = {
            "cases": [
                {
                    "id": "1",
                    "files": ["lib/Sema/CSSimplify.cpp"],
                    "expected_chair": "silgen",
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "heldout.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--heldout-file", str(path)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("FAIL 1", proc.stdout)
        self.assertIn("report only", proc.stdout)


if __name__ == "__main__":
    unittest.main()

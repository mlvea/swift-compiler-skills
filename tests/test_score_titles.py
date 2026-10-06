"""Title-tag mapping, without a Swift checkout."""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_mod():
    path = ROOT / "swift-expert-panel" / "scripts" / "score_titles.py"
    spec = importlib.util.spec_from_file_location("score_titles", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TitleMapTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_mod()

    def test_bracket_and_colon_tags(self):
        cases = {
            "[Embedded] Project fixed tuples": "embedded",
            "SILGen: emit a cleanup": "silgen",
            "[cxx-interop] Keep the spelling": "clang-importer",
            "[DiagnosticVerifier] bind markers": "parser-diagnostics",
            "SIL,SILGen,IRGen: support type(of:)": "silgen",
            "[NFC] tidy a comment": None,
            "Fix a bug": None,
        }
        for title, domain in cases.items():
            self.assertEqual(self.mod.domain_for_title(title), domain, title)

    def test_merge_commit_uses_the_body_title(self):
        parsed = self.mod.pr_from_commit(
            "Merge pull request #92847 from user/branch",
            "\n[DiagnosticVerifier] bind expansion markers\n",
        )
        self.assertEqual(parsed, ("92847", "[DiagnosticVerifier] bind expansion markers"))

    def test_non_merge_is_ignored(self):
        self.assertIsNone(
            self.mod.pr_from_commit("[Embedded] not a merge", "")
        )

    def test_source_paths_drop_tests(self):
        self.assertEqual(
            self.mod.source_paths(
                ["lib/Sema/CSSimplify.cpp", "test/Constraints/calls.swift"]
            ),
            ["lib/Sema/CSSimplify.cpp"],
        )

    def test_score_rows_counts_three_cuts(self):
        seat = importlib.util.spec_from_file_location(
            "seat_for_titles",
            ROOT / "swift-expert-panel" / "scripts" / "seat.py",
        )
        mod = importlib.util.module_from_spec(seat)
        seat.loader.exec_module(mod)
        table = json.loads(
            (ROOT / "knowledge-base/expert-panel/seats.json").read_text(
                encoding="utf-8"
            )
        )
        rows = [
            {
                "number": "1",
                "title": "[Embedded] Embedded Swift witness tables",
                "domain": "embedded",
                "files": [
                    "lib/SILOptimizer/Utils/Generics.cpp",
                    "test/embedded/existential-generic-error.swift",
                ],
            }
        ]
        counts = self.mod.score_rows(mod, table, rows)
        self.assertEqual(counts["all changed files"], (1, 1))
        # The test file is what chairs embedded. Source files keep the
        # optimizer as chair. The title still seats the embedded brief.
        self.assertEqual(counts["source files only"], (0, 1))
        self.assertEqual(counts["source files plus title"], (0, 1))
        seated = mod.seat(
            ["lib/SILOptimizer/Utils/Generics.cpp"],
            rows[0]["title"],
            None,
            table,
        )
        self.assertIn("embedded", seated["seated"])
        self.assertNotEqual(seated["chair"], "unseated")


if __name__ == "__main__":
    unittest.main()

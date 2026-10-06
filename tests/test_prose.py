"""Prose rules used by the write hook and scripts/check_repo.py."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    path = ROOT / "scripts" / "check-doc-prose.py"
    spec = importlib.util.spec_from_file_location("check_doc_prose", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ProseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prose = load()

    def denies(self, path, text):
        self.assertTrue(self.prose.check(path, text), text)

    def allows(self, path, text):
        self.assertEqual(self.prose.check(path, text), [], text)

    def test_banned_filler_and_dashes(self):
        self.denies("README.md", "one small, gated edit")
        self.denies("README.md", "The gates are conservative")
        self.denies("README.md", "word \u2014 more")
        self.denies("README.md", "A1\u2013A10")
        self.denies("README.md", "delve into the solver")
        self.allows("README.md", "plain sentence.")

    def test_allowed_compiler_terms_and_journal_field(self):
        self.allows("README.md", "see evolution-gate.md")
        self.allows("README.md", "Confirm the repro is target-gated.")
        self.allows("README.md", "flag-gated behavior may change")
        self.allows("optimization/edit-log.md", "Gate: execution (ok)")
        self.allows("optimization/edit-log.md", "Fix-loop gates: panel on the plan")

    def test_home_paths_only_in_paths_json(self):
        sample = "see " + "/Users" + "/example/src"
        self.denies("swift-local-build-test/SKILL.md", sample)
        self.denies("knowledge-base/pipeline-map.md", sample)
        self.allows("swift-local-build-test/references/paths.json", sample)
        # paths.json is not a document suffix, so check() ignores it.
        # The allow above is because .json is not scanned as prose.
        self.allows("README.md", "Name the checkout, not a home directory.")


if __name__ == "__main__":
    unittest.main()

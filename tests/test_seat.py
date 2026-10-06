"""Deterministic seating, without a Swift checkout."""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_seat():
    path = ROOT / "swift-expert-panel" / "scripts" / "seat.py"
    spec = importlib.util.spec_from_file_location("seat", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class SeatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seat = load_seat()
        cls.table = json.loads(
            (ROOT / "knowledge-base/expert-panel/seats.json").read_text(encoding="utf-8")
        )

    def test_constraint_solver_chairs_type_system(self):
        got = self.seat.seat(
            ["lib/Sema/CSSimplify.cpp"], "", "sema", self.table
        )
        self.assertEqual(got["chair"], "type-system")
        self.assertIn("type-system", got["seated"])
        self.assertLessEqual(len(got["seated"]), 4)

    def test_macro_file_chairs_macros(self):
        got = self.seat.seat(
            ["lib/Sema/TypeCheckMacros.cpp"], "", "sema", self.table
        )
        self.assertEqual(got["chair"], "macros")

    def test_keyword_alone_does_not_sit_a_conditional_domain(self):
        got = self.seat.seat([], "macro expansion", None, self.table)
        self.assertNotIn("macros", got["seated"])
        self.assertEqual(got["chair"], "unseated")
        self.assertEqual(got["seated"], [])

    def test_no_file_match_is_unseated(self):
        got = self.seat.seat(
            ["lib/LLVMPasses/LLVMARCContract.cpp"], "", None, self.table
        )
        self.assertEqual(got["chair"], "unseated")
        self.assertEqual(got["seated"], [])
        self.assertNotIn("type-system", got["seated"])

    def test_diagnostic_verifier_is_not_library_evolution(self):
        got = self.seat.seat(
            ["lib/Frontend/DiagnosticVerifier.cpp"], "", None, self.table
        )
        self.assertEqual(got["chair"], "unseated")
        self.assertNotIn("library-evolution", got["seated"])

    def test_embedded_text_seats_embedded_without_a_primary_file(self):
        got = self.seat.seat(
            ["lib/SILOptimizer/Utils/Generics.cpp"],
            "Embedded Swift witness_method specialization",
            "sil-opts",
            self.table,
        )
        self.assertIn("embedded", got["seated"])

    def test_embedded_text_alone_seats_embedded(self):
        got = self.seat.seat([], "Embedded Swift", None, self.table)
        self.assertEqual(got["chair"], "embedded")
        self.assertIn("embedded", got["seated"])

    def test_stdlib_primary_sits_stdlib(self):
        got = self.seat.seat(
            ["stdlib/public/core/Array.swift"], "", None, self.table
        )
        self.assertEqual(got["chair"], "stdlib")


if __name__ == "__main__":
    unittest.main()

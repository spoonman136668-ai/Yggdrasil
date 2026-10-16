#!/usr/bin/env python3
"""Pure unit tests for F84 D4 legal-action witness (no cohorts accessed)."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import unittest

DIR = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "f84_native_actions_no_experiment",
    DIR / "native_legal_action_witness.py",
)
D4 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = D4
SPEC.loader.exec_module(D4)


def fixture():
    links = [
        (100, 0, 101), (102, 1, 101), (102, 2, 103),
        (104, 3, 103), (104, 0, 105), (106, 1, 105),
    ]
    irrelevant = [(1000 + 2*i, i % 4, 1001 + 2*i) for i in range(66)]
    return tuple(links + irrelevant), dict(
        start=100, answer=106,
        ops=((0, 1), (1, -1), (2, 1), (3, -1), (0, 1), (1, -1))
    )


class LegalReachabilityUnitTests(unittest.TestCase):
    def test_only_public_edges_from_actual_path(self):
        public, question = fixture()
        edges = D4.query_path_in_original_public(public, question)
        self.assertEqual(len(edges), 6)
        self.assertEqual(edges, public[:6])
        self.assertEqual(len(set(edges)), 6)

    def test_wrong_direction_denies_full_history_witness(self):
        public, question = fixture()
        question["ops"] = ((0, -1),) + question["ops"][1:]
        with self.assertRaises(AssertionError):
            D4.query_path_in_original_public(public, question)

    def test_wrong_answer_denies_full_history_witness(self):
        public, question = fixture()
        question["answer"] = 999999
        with self.assertRaises(AssertionError):
            D4.query_path_in_original_public(public, question)

    def test_no_synthesized_edge_is_injected(self):
        public, question = fixture()
        witness = D4.query_path_in_original_public(public, question)
        self.assertTrue(all(edge in public for edge in witness))


if __name__ == "__main__":
    unittest.main()

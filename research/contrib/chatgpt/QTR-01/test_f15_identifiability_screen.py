"""F15 fixed, source-free development falsification checks; no protected worlds."""
import unittest
from itertools import combinations
from f15_identifiability_screen import EVENTS, hypotheses, run


class F15Identifiability(unittest.TestCase):
    def test_ten_distinct_causal_hypotheses(self):
        h = hypotheses()
        self.assertEqual(len(h), 10)
        tables = [tuple(fn(e) for e in EVENTS) for fn in h.values()]
        self.assertEqual(len(set(tables)), 10)

    def test_three_or_fewer_probes_cannot_identify_all(self):
        tables = [tuple(fn(e) for e in EVENTS) for fn in hypotheses().values()]
        for n in range(1, 4):
            for probes in combinations(range(len(EVENTS)), n):
                signatures = {tuple(table[i] for i in probes) for table in tables}
                self.assertLess(len(signatures), 10)

    def test_four_fixed_probes_make_unique_signatures(self):
        results = run()
        self.assertEqual(results["min_fixed_probe_budget"], 4)
        probes = [EVENTS.index(tuple(e)) for e in results["probe_cases"]]
        tables = [tuple(fn(e) for e in EVENTS) for fn in hypotheses().values()]
        self.assertEqual(len({tuple(table[i] for i in probes) for table in tables}), 10)

    def test_symbolic_ceiling_and_exact_retrieval_abstention(self):
        results = run()
        self.assertEqual(results["fully_informed_symbolic_correct"], 80)
        self.assertEqual(results["exact_event_retrieval_covered"], 40)
        self.assertEqual(results["exact_event_retrieval_abstains"], 40)
        self.assertFalse(results["scientific_pass"])
        self.assertFalse(results["native_transfer_tested"])
        self.assertFalse(results["source_benchmark_executed"])

    def test_deterministic_repetition(self):
        self.assertEqual(run(), run())


if __name__ == "__main__":
    unittest.main()

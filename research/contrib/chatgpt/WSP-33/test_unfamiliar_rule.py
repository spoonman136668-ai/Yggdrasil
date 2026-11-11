import unittest
from pathlib import Path
import json
from run_dev import RULES, TARGETS, target_rule, expressible_in_old_language, symbolic
from cumulative_model import CumulativeModel, PlasticNand, context, SOURCE_KNOWN, PUBLIC, MODES, BUDGETS

S0 = (0, 1, 0, 1, 0, 1, 0, 1)
S1 = (1, 1, 0, 0, 1, 1, 0, 0)

def make(rule="xor", mode="source_two"):
    a, b = PlasticNand(), PlasticNand()
    observed_sources = tuple(tuple((context(i), row[i]) for i in SOURCE_KNOWN)
                             for row in (S0, S1))
    target = target_rule((S0, S1), rule)
    observed_target = tuple((context(i), target[i]) for i in PUBLIC)
    return CumulativeModel((a.snapshot(), b.snapshot()), observed_sources, observed_target, mode), target

class UnfamiliarRuleTests(unittest.TestCase):
    def test_truth_is_evaluator_only_and_deterministic(self):
        self.assertEqual(target_rule((S0, S1), "xor"), tuple(a ^ b for a, b in zip(S0, S1)))
        self.assertEqual(target_rule((S0, S1), "switch"), tuple((S0, S1)[i & 1][i] for i in range(8)))
        self.assertEqual(len(TARGETS), 3)
        with self.assertRaises(ValueError):
            target_rule((S0, S1), "oracle")
        with self.assertRaises(ValueError):
            target_rule((S0, (0,) * 7), "xor")

    def test_no_new_rule_or_hidden_target_in_model_state(self):
        m, target = make("xor")
        raw = m.snapshot()
        data = json.loads(raw[9:-32])
        self.assertEqual(data["schema"], "wsp32.cumulative-facts.v1")
        self.assertNotIn("xor", raw.decode("latin1"))
        self.assertNotIn("switch", raw.decode("latin1"))
        for i in TARGETS:
            self.assertEqual(m.target_known[i], 0)
        self.assertEqual(m.snapshot(), raw)

    def test_two_writes_retain_originals_after_cold_restore(self):
        for rule in RULES:
            m, _ = make(rule)
            initial_banks = m.payloads()
            acquired = []
            for _ in range(2):
                q = m.query()
                self.assertIsNotNone(q)
                y = (S0, S1)[q[1]][q[2]]
                m.answer(q, y)
                acquired.append((q, y))
                state = m.snapshot()
                m = CumulativeModel.restore(state)
                self.assertEqual(m.snapshot(), state)
                self.assertEqual(m.payloads(), initial_banks)
                for bank, row in enumerate((S0, S1)):
                    for i in SOURCE_KNOWN:
                        self.assertEqual(m._source(bank, context(i)), row[i])
                target = target_rule((S0, S1), rule)
                for i in PUBLIC:
                    self.assertEqual(m.predict(context(i)), target[i])
                for q0, y0 in acquired:
                    self.assertEqual(m._source(q0[1], context(q0[2])), y0)
                for i in range(8):
                    self.assertEqual(symbolic(m, i), m.predict(context(i)))
            self.assertIsNone(m.query())

    def test_actual_answer_address_and_budget_fences(self):
        for rule in RULES:
            for mode in MODES:
                m, _ = make(rule, mode)
                initial = m.snapshot()
                if BUDGETS[mode] == 0:
                    self.assertIsNone(m.query())
                    with self.assertRaises(ValueError):
                        m.answer(("s", 0, 5), 0)
                    self.assertEqual(m.snapshot(), initial)
                else:
                    q = m.query()
                    with self.assertRaises(ValueError):
                        m.answer(("t", 0, 5), 0)
                    self.assertEqual(m.snapshot(), initial)
                    y = (S0, S1)[q[1]][q[2]]
                    m.answer(q, y)
                    after = m.snapshot()
                    m.answer(q, y)
                    self.assertEqual(after, m.snapshot())
                    with self.assertRaises(ValueError):
                        m.answer(q, 1-y)
                    self.assertEqual(after, m.snapshot())

    def test_identical_evidence_independent_of_hidden_rule_identity(self):
        a, _ = make()
        b, _ = make()
        self.assertEqual(a.snapshot(), b.snapshot())
        for _ in range(2):
            self.assertEqual(a.query(), b.query())
            q = a.query()
            y = (S0, S1)[q[1]][q[2]]
            a.answer(q, y)
            b.answer(q, y)
            self.assertEqual(a.snapshot(), b.snapshot())

    def test_expressibility_diagnostic_never_changes_scoring_cohort(self):
        zeros = (0,) * 8
        ones = (1,) * 8
        self.assertTrue(expressible_in_old_language((zeros, zeros), zeros))
        self.assertFalse(expressible_in_old_language((zeros, zeros), ones))
        self.assertEqual(len(RULES) * 60 * 16, 1920)

if __name__ == "__main__":
    unittest.main()

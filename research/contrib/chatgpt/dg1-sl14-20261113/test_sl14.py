"""DG1-SL14 freeze, paid physical interventions, independent controls and custody."""
import copy
import json
import unittest
from pathlib import Path

from sl14 import (
    ARMS, AUDITS, COLD, COHORTS, FREEZE, PAIRED, SCHEMA,
    Fingerprint, IndependentBayes, RollingRule, FlatLookup, World,
    audit, gate, pair, one_world, learner, trial, genuine_return_flags,
)


class SL14Tests(unittest.TestCase):
    def test_registration_and_distinct_six_bit_causal_substrate(self):
        p = json.loads((Path(__file__).parent / "prereg.json").read_text())
        self.assertEqual(FREEZE, "272cbb87542d87c779161780602cfddfb7439e8a")
        self.assertEqual(p["status"],
                         "FROZEN_BEFORE_IMPLEMENTATION_AND_SCIENTIFIC_OUTCOME")
        self.assertEqual(p["budget"]["worlds"], 32)
        self.assertEqual(p["budget"]["total_paid_steps"], 18432)
        self.assertEqual(p["budget"]["total_paid_causal_observations"], 14784)
        self.assertEqual(p["budget"]["total_paid_input_perturbations"], 3648)
        self.assertEqual(len(ARMS), 6)
        self.assertEqual(sum(map(len, COHORTS.values())), 32)
        self.assertEqual(AUDITS, (24, 48, 54, 72, 78, 96))
        self.assertEqual(COLD, (43, 67, 89))
        self.assertTrue(all(c not in (24, 48, 72) for c in COLD))

    def test_physical_gate_truth_is_local_and_not_four_bit_repetition(self):
        self.assertEqual(
            [[gate(g, x) for x in range(4)] for g in range(6)],
            [[0, 0, 0, 1], [0, 1, 1, 1], [0, 1, 1, 0],
             [1, 1, 1, 0], [1, 0, 0, 0], [1, 0, 0, 1]])
        for x in range(8):
            for a in range(3):
                self.assertIn(pair(x, a), range(4))
        with self.assertRaises(ValueError):
            gate(6, 0)
        with self.assertRaises(ValueError):
            gate(0, 4)
        with self.assertRaises(ValueError):
            pair(8, 0)

    def test_every_world_charges_all_real_physical_actions(self):
        for cohort, seeds in COHORTS.items():
            w = World(seeds[0], cohort)
            state = seeds[0] % 64
            stats = {"perturb": 0, "causal": 0}
            for t in range(96):
                chosen = t % 3 if t >= 48 and t % 5 != 4 else None
                before = state
                kind, action, after = w.step(before, t, chosen)
                stats[kind] += 1
                if kind == "causal":
                    self.assertIn(after, (before, before ^ (1 << (3+action))))
                else:
                    self.assertEqual(after, before ^ (1 << action))
                state = after
            self.assertEqual(stats, {"perturb": 19, "causal": 77})
            self.assertEqual(w.paid, 96)
            with self.assertRaises(ValueError):
                w.step(state, 95, 0)
            with self.assertRaises(ValueError):
                w.audit_truth(0, 0, 95)
        with self.assertRaises(ValueError):
            World(106001, "ABAB")
        w = World(107001, "ABAB")
        with self.assertRaises(ValueError):
            w.step(0, 0, 1)
        with self.assertRaises(ValueError):
            w.step(0, 48)
        with self.assertRaises(ValueError):
            w.step(0, 4, 0)

    def test_fingerprint_requires_diverse_genuine_physical_witnesses(self):
        m = Fingerprint()
        for _ in range(15):
            m.observe(0, 0, 0)
        self.assertEqual(len(m.banks), 1)
        self.assertFalse(m.transitions)
        self.assertIn(m.choose(3, 48), range(3))
        self.assertEqual(m.choose(3, 48), m.choose(3, 48))
        with self.assertRaises(ValueError):
            m.choose(3, 49)  # scheduled paid input perturbation
        with self.assertRaises(TypeError):
            m.observe(0, 0, 0, hidden_context="B")
        with self.assertRaises(ValueError):
            m.observe(0, 0, 2)
        with self.assertRaises(ValueError):
            m.observe(8, 0, 0)

    def test_checkpoint_tamper_and_full_prediction_parity(self):
        for m in (Fingerprint(), Fingerprint(False), IndependentBayes(),
                  RollingRule(), FlatLookup()):
            for i in range(16):
                m.observe((i*3) % 8, i % 3, i % 2)
            raw = m.snapshot()
            r = type(m).restore(raw)
            self.assertEqual(r.snapshot(), raw)
            self.assertLessEqual(len(raw), 8192)
            self.assertEqual(
                [m.predict(x, a) for x in range(8) for a in range(3)],
                [r.predict(x, a) for x in range(8) for a in range(3)],
            )
            for bad in (raw[:-1], raw+b" ",
                        bytes([raw[0]^1])+raw[1:]):
                with self.assertRaises(ValueError):
                    type(m).restore(bad)

    def test_paid_replay_arms_have_identical_full_physical_traces(self):
        world = one_world(107001, "ABAB")
        self.assertEqual(set(world["arms"]), set(ARMS))
        rows = world["arms"]
        self.assertEqual(len({v["trace_sha256"] for k, v
                              in rows.items() if k in PAIRED}), 1)
        self.assertEqual(len({v["trace_first48_sha256"]
                              for v in rows.values()}), 1)
        for name, record in rows.items():
            self.assertEqual(record["charged_steps"], 96, name)
            self.assertEqual(record["causal_observations"], 77, name)
            self.assertEqual(record["charged_input_perturbations"], 19, name)
            self.assertEqual(len(record["snapshot_bytes"]), 3, name)
            self.assertLessEqual(
                max(record["snapshot_bytes"] +
                    [record["final_snapshot_bytes"]]), 8192, name)
            self.assertEqual(len(record["physical_ledger"]), 96, name)
            for t in AUDITS:
                metrics = record["audits"][str(t)]
                self.assertEqual(metrics["correct"] +
                                 metrics["wrong_confident"], 24, name)
        for arm in PAIRED[1:]:
            self.assertEqual(rows[arm]["physical_ledger"],
                             rows["fingerprint_active"]["physical_ledger"])
        flags = genuine_return_flags(world)
        self.assertEqual(set(flags), {"A2", "B2", "A4", "falseC"})
        self.assertFalse(any(t["archived_reuse"] for t in
                            rows["no_retrieval_on_active"]["transitions"]))

    def test_free_replay_or_oracle_cannot_pollute_physical_learning(self):
        with self.assertRaises(ValueError):
            trial(107001, "ABAB", "fingerprint_active", "replay", [None])
        invalid = [None] * 96
        invalid[48] = 1
        invalid[49] = 2
        with self.assertRaises(ValueError):
            trial(107001, "ABAB", "no_retrieval_on_active", "replay", invalid)
        with self.assertRaises(ValueError):
            learner("outside_scope")
        with self.assertRaises(ValueError):
            IndependentBayes().observe(0, 0, 2)
        with self.assertRaises(TypeError):
            Fingerprint().observe(0, 0, 1, evaluator_answer=1)

    def test_science_outputs_deterministic_except_wall_clock_timing(self):
        a = one_world(107009, "ABAC")
        b = one_world(107009, "ABAC")
        for obj in (a, b):
            for result in obj["arms"].values():
                result.pop("cpu_ns")
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()

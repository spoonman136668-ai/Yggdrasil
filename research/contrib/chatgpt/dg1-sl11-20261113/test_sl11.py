"""SL11 freeze custody, physical-only context evidence and replay negatives."""
import json
import unittest
from pathlib import Path

from sl11 import (
    ARMS, AUDITS, COHORTS, FLIPS, FREEZE, GROUPS,
    EvidenceGated, World, choose, learner, one_world, sl09, trial,
)


class SL11Tests(unittest.TestCase):
    def test_registration_and_protocol_first(self):
        p = json.loads((Path(__file__).parent / "prereg.json").read_text())
        self.assertEqual(FREEZE, "2717821accf3c22140b58859d7c8bc8c9fd5a2de")
        self.assertEqual(p["status"], "FROZEN_BEFORE_ANY_SOURCE_OR_OUTCOME")
        self.assertEqual(len(ARMS), 8)
        self.assertEqual(sum(map(len, COHORTS.values())), 32)
        self.assertEqual(len(FLIPS), 10)
        self.assertEqual(AUDITS, (60, 64, 72, 80))
        self.assertEqual(p["budgets"]["paid_steps"], 20480)
        self.assertEqual(p["budgets"]["paid_causal_observations"], 17920)
        self.assertEqual(p["budgets"]["paid_flips"], 2560)

    def test_paid_physics_and_no_labels(self):
        for cohort, seeds in COHORTS.items():
            world = World(seeds[0], cohort)
            state = seeds[0] % 16
            n = {"flip": 0, "causal": 0}
            for step in range(80):
                selected = (step % 4) if step >= 60 and step not in FLIPS else None
                kind, action, nxt = world.step(state, step, selected)
                self.assertIn(nxt, (state, state ^ (1 << action)))
                n[kind] += 1
                state = nxt
            self.assertEqual(n, {"flip": 10, "causal": 70})
            self.assertEqual(world.paid, 80)
            with self.assertRaises(ValueError):
                world.step(state, 80)
            with self.assertRaises(ValueError):
                world.audit_truth(0, 0, 79)
        with self.assertRaises(ValueError):
            World(103001, "RETURN_A")
        world = World(104001, "RETURN_A")
        with self.assertRaises(ValueError):
            world.step(0, 0, 2)
        with self.assertRaises(ValueError):
            world.step(0, 60)
        with self.assertRaises(TypeError):
            EvidenceGated().observe(0, 0, 0, phase_label="A")

    def test_gated_rejects_oracle_and_unpaid_or_nonlocal_events(self):
        model = EvidenceGated()
        with self.assertRaises(ValueError):
            model.observe(0, 0, 2)
        with self.assertRaises(ValueError):
            model.observe(16, 0, 0)
        self.assertEqual(model.causal_events, 0)
        with self.assertRaises(TypeError):
            model.observe(0, 0, 1, hidden_rule=(1, 2, 3))
        for i in range(70):
            model.observe(i % 16, i % 4, i % 16)
        with self.assertRaises(ValueError):
            model.observe(0, 0, 0)

    def test_evidence_must_be_distinct_and_physical(self):
        model = EvidenceGated()
        for _ in range(30):
            model.observe(0, 0, 0)
        self.assertEqual(model.switches, 0)
        self.assertEqual(len(model.model.banks), 1)
        self.assertLessEqual(len(model.witness), 6)
        with self.assertRaises(ValueError):
            choose(model, 0, 62, "gated")
        with self.assertRaises(ValueError):
            choose(model, 0, 60, "not-a-policy")
        with self.assertRaises(ValueError):
            choose(learner("original_active"), 0, 60, "gated")

    def test_cold_and_final_snapshot_custody(self):
        model = EvidenceGated()
        for i in range(16):
            before, action = i % 16, i % 4
            model.observe(before, action, before)
        model.rest()
        snap = model.snapshot()
        restored = EvidenceGated.restore(snap)
        self.assertEqual(restored.snapshot(), snap)
        self.assertLessEqual(len(snap), 8192)
        self.assertEqual(
            [model.predict(s, a) for s in range(16) for a in range(4)],
            [restored.predict(s, a) for s in range(16) for a in range(4)]
        )
        for bad in (snap[:-1], snap + b" ",
                    bytes([snap[0] ^ 1]) + snap[1:]):
            with self.assertRaises(ValueError):
                EvidenceGated.restore(bad)

    def test_all_arms_paired_physical_action_state_outcomes(self):
        result = one_world(104001, "RETURN_A")
        arms = result["arms"]
        self.assertEqual(set(arms), set(ARMS))
        self.assertEqual(len({v["pre_cold_trace_sha256"]
                              for v in arms.values()}), 1)
        for group in GROUPS:
            self.assertEqual(
                len({arms[k]["complete_trace_sha256"] for k in group}), 1)
            for other in group[1:]:
                self.assertEqual(arms[group[0]]["paid_ledger"],
                                 arms[other]["paid_ledger"])
        for arm, z in arms.items():
            self.assertEqual(z["charged_steps"], 80, arm)
            self.assertEqual(z["flips"], 10, arm)
            self.assertEqual(z["paid_causal_observations"], 70, arm)
            self.assertLessEqual(z["cold_checkpoint_bytes"], 8192, arm)
            self.assertLessEqual(z["final_checkpoint_bytes"], 8192, arm)
            self.assertEqual(sum(z["prequential"].values()), 70, arm)
            for checkpoint in AUDITS:
                counts = z["stage_audits"][str(checkpoint)]
                self.assertEqual(sum(counts[k] for k in (
                    "correct", "wrong_confident", "abstained")), 64, arm)

    def test_replay_cannot_inject_free_actions(self):
        with self.assertRaises(ValueError):
            trial(104001, "RETURN_A", "gated_active", "replay",
                  replay_plan=[0])
        forged = [None] * 80
        forged[60] = 0
        forged[62] = 1
        with self.assertRaises(ValueError):
            trial(104001, "RETURN_A", "original_on_gated", "replay",
                  replay_plan=forged)
        with self.assertRaises(ValueError):
            learner("unknown")
        with self.assertRaises(ValueError):
            sl09.audit(EvidenceGated(),
                       World(104001, "RETURN_A"), set(), 79)


if __name__ == "__main__":
    unittest.main()

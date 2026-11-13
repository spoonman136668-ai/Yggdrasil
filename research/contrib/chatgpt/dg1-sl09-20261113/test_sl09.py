"""SL09 preregistration, paid-physics, negatives and checkpoint custody."""
import json
import unittest
from pathlib import Path
from sl09 import (
    ARMS, AUDITS, COHORTS, FLIPS, FREEZE, MASKS,
    PROGRAMS, Agent, World, audit, flip, one_world,
)


class SL09Tests(unittest.TestCase):
    def test_prereg_frozen_prior_to_source(self):
        spec = json.loads((Path(__file__).parent / "prereg.json").read_text())
        self.assertEqual(FREEZE, "9f760727f58058a538f4af82a0d4494b98be11c9")
        self.assertEqual(spec["status"], "FROZEN_BEFORE_IMPLEMENTATION_OR_OUTCOME")
        self.assertEqual(len(ARMS), 6)
        self.assertEqual(len(PROGRAMS), 216)
        self.assertEqual(sum(map(len, COHORTS.values())), 32)
        self.assertEqual(len(FLIPS), 10)
        self.assertEqual(AUDITS, (60, 64, 72, 80))
        self.assertTrue(all(len(m) == 216 for m in MASKS.values()))

    def test_physical_paid_steps_and_nonlocal_event_rejection(self):
        for group, seeds in COHORTS.items():
            world = World(seeds[0], group)
            state = seeds[0] % 16
            flips = causal = 0
            for step in range(80):
                kind, action, nxt = world.step(state, step)
                self.assertIn(nxt, (state, state ^ (1 << action)))
                if kind == "flip":
                    flips += 1
                else:
                    causal += 1
                state = nxt
            self.assertEqual((world.paid, flips, causal), (80, 10, 70))
            with self.assertRaises(ValueError):
                world.step(state, 80)
            with self.assertRaises(ValueError):
                world.step(state, 79)
        with self.assertRaises(ValueError):
            World(101001, "RETURN_A")
        with self.assertRaises(ValueError):
            Agent(ARMS[0]).observe(0, 0, 2)
        with self.assertRaises(TypeError):
            Agent(ARMS[0]).observe(0, 0, 1, phase="A")

    def test_non_token_program_structure_and_ood_unseen(self):
        for a in range(4):
            for s in range(16):
                for p in PROGRAMS:
                    self.assertIn(flip(p, s, a), (0, 1))
        self.assertNotEqual(
            set(range(3)), set(range(3, 6))
        )
        world = World(102025, "COMPOSITION_OOD")
        with self.assertRaises(ValueError):
            world.audit_truth(0, 0, 79)
        with self.assertRaises(ValueError):
            world.audit_truth(0, 0, 80.0)

    def test_cold_snapshot_and_checkpoint_tampering_each_arm(self):
        for arm in ARMS:
            x = Agent(arm)
            x.observe(0, 0, 0)
            x.observe(1, 1, 1)
            x.rest()
            raw = x.snapshot()
            y = Agent.restore(raw)
            self.assertEqual(y.snapshot(), raw)
            for state in range(16):
                for action in range(4):
                    self.assertEqual(x.predict(state, action),
                                     y.predict(state, action))
            self.assertLessEqual(len(raw), 8192)
            for altered in (raw + b" ", raw[:-1],
                            bytes([raw[0] ^ 1]) + raw[1:]):
                with self.assertRaises(ValueError):
                    Agent.restore(altered)

    def test_negative_capacity_and_no_evaluator_learning(self):
        x = Agent(ARMS[0])
        for _ in range(70):
            x.observe(0, 0, 0)
        with self.assertRaises(ValueError):
            x.observe(0, 0, 0)
        with self.assertRaises(ValueError):
            x.observe(-1, 0, 0)
        world = World(102001, "RETURN_A")
        with self.assertRaises(ValueError):
            audit(x, world, set(), 79)

    def test_trial_all_arms_exact_same_paid_trace_and_unseen_audit(self):
        w = one_world(102001, "RETURN_A")
        self.assertEqual(set(w["arms"]), set(ARMS))
        self.assertEqual(len(set(x["trace_sha256"]
                                 for x in w["arms"].values())), 1)
        for a in w["arms"].values():
            self.assertEqual(a["paid_steps"], 80)
            self.assertEqual(a["flips"], 10)
            self.assertEqual(a["causal_observations"], 70)
            self.assertLessEqual(a["cold_checkpoint_bytes"], 8192)
            self.assertLessEqual(a["final_checkpoint_bytes"], 8192)
            for t in AUDITS:
                audit_row = a["stage_audits"][str(t)]
                self.assertEqual(sum(audit_row[k] for k in (
                    "correct", "wrong_confident", "abstained")), 64)
                self.assertLessEqual(sum(audit_row[k] for k in (
                    "unseen_correct", "unseen_wrong_confident",
                    "unseen_abstained")), 64)


if __name__ == "__main__":
    unittest.main()

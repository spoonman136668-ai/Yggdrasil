"""Pure mechanical AAI-10A tests, with NO reserved science cohort IDs."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent / "AAI-10P"
sys.path.insert(0, str(BENCH))
sys.path.insert(0, str(HERE))

import benchmark as b
import models as m


def row(law, x, goal=(1, 0), action=None):
    s = b.public_initial(law, x, goal)
    return b.public_step(law, s, action) if action else s


class FrozenOperatorAssociationContracts(unittest.TestCase):
    def test_source_and_preprimary_freeze(self):
        p = json.loads((HERE / "prereg.json").read_text("utf8"))
        self.assertEqual(p["id"], "AAI-10A")
        self.assertEqual(p["base_sha"], "1deeb328abc478949b6d528e5cd2775c72021150")
        self.assertFalse(p["future_science"]["first_use_authorized"])
        self.assertFalse(p["future_science"]["frozen_first_use"])
        self.assertTrue(p["future_science"]["no_post_result_tuning"])
        self.assertEqual(p["candidate"]["slots"], 3)
        self.assertEqual(p["matched_conventional_controls"]["logistic_interactions"][:12],
                         "Conventional")
        self.assertEqual(p["common_protocol"]["worlds"]["transfer"], {"start": 992000, "count": 64})
        self.assertEqual(m.GRAMMAR.__len__(), 9)

    def test_all_predicate_hypotheses_are_public_and_finite(self):
        for x in b.INPUTS:
            for rule in m.GRAMMAR:
                self.assertIn(m.pattern(rule, x), (0, 1))
        self.assertEqual(set(op for op, _, _ in m.GRAMMAR), {"xor", "and", "or"})
        self.assertEqual(len({tuple(h) for h in m.GRAMMAR}), 9)

    def test_all_controls_receive_identical_public_evidence(self):
        learners = {name: m.create(name) for name in m.NAMES}
        evidence = [
            row("A", x, (i % 2, (i+1) % 2), b.ACTIONS[i % 6])
            for i, x in enumerate(b.INPUTS)
        ]
        for event in evidence:
            for learner in learners.values():
                learner.learn(event)
        for name, learner in learners.items():
            p = learner.predict((1, 0, 1))
            self.assertEqual(len(p), 2, name)
            self.assertTrue(all(0 <= q <= 1 for q in p), (name, p))
            self.assertTrue(learner.choose(row("A", (0, 1, 0))) in (None, *b.ACTIONS), name)
        for name, learner in learners.items():
            cp = m.checkpoint({name: learner})
            recovered = m.cold_restore(cp)
            self.assertEqual(m.checkpoint(recovered), cp, name)

    def test_hidden_identity_rejected_by_all_models(self):
        invalid = {**row("A", (1, 1, 0)), "law": "A"}
        before = {name: m.canonical(m.create(name).state()) for name in m.NAMES}
        for name in m.NAMES:
            model = m.create(name)
            with self.assertRaises(ValueError):
                model.learn(invalid)
            self.assertEqual(m.canonical(model.state()), before[name])

    def test_contradiction_and_protected_slot_shape_without_law_labels(self):
        learner = m.ProtectedOperatorBank()
        # Structural fixtures only: no reserved world seeds, no transfer split.
        for law in ("A", "B"):
            for _ in range(4):
                for x in b.INPUTS:
                    learner.learn(row(law, x))
        self.assertLessEqual(len(learner.slots), 3)
        self.assertEqual(len({s["id"] for s in learner.slots}), len(learner.slots))
        self.assertIn(learner.active_id, {s["id"] for s in learner.slots})
        self.assertEqual(learner.scratch, [])
        self.assertEqual(learner.max_slots, 3)
        cp = m.checkpoint({"candidate": learner})
        clone = m.cold_restore(cp)["candidate"]
        self.assertEqual(m.checkpoint({"candidate": clone}), cp)
        for x in b.INPUTS:
            clone.learn(row("A", x))
        self.assertEqual(m.checkpoint({"candidate": learner}), cp)

    def test_one_slot_ablation_cannot_allocate_memory(self):
        learner = m.create("one_slot")
        for law in ("A", "B", "C", "D"):
            for x in b.INPUTS:
                learner.learn(row(law, x))
        self.assertEqual(len(learner.slots), 1)
        self.assertFalse(learner.reuse)

    def test_fully_trained_logistic_is_not_privileged(self):
        learner = m.LogisticInteractions()
        for x in b.INPUTS:
            learner.learn(row("A", x))
        state = learner.state()
        self.assertEqual(state["epochs"], 1200)
        self.assertEqual(len(state["samples"]), 8)
        self.assertEqual(len(state["weights"]), 2)
        self.assertEqual(len(state["weights"][0]), 8)
        self.assertEqual(m.cold_restore({"logistic_interactions": m.canonical(state)})[
            "logistic_interactions"].state(), state)

    def test_common_planner_respects_persistent_interventions_and_cost(self):
        for name in m.NAMES:
            model = m.create(name)
            start = row("B", (0, 1, 1), (0, 1))
            action1 = model.choose(start)
            if action1 is None:
                continue
            after1 = b.public_step("B", start, action1)
            model.learn(after1)
            action2 = model.choose(after1)
            if action2 is not None:
                after2 = b.public_step("B", after1, action2)
                self.assertEqual(after2["actions_taken"], 2)
                self.assertEqual(after2["mediators"], list(b.mediators("B", after2["x"])))
                self.assertEqual(after2["reward"],
                                 b.reward(after2["mediators"], (0, 1), 2))

    def test_no_primary_command(self):
        cmd = [sys.executable, "-B", str(HERE / "source_only.py"), "--primary"]
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("DISARMED", done.stderr)

    def test_invalid_checkpoint_rejected(self):
        model = m.create("candidate")
        cp = m.checkpoint({"candidate": model})
        with self.assertRaises(ValueError):
            m.cold_restore({"candidate": cp["candidate"] + " "})
        model.learn(row("A", (0, 0, 0)))
        cp = m.checkpoint({"candidate": model})
        other = m.cold_restore(cp)["candidate"]
        self.assertEqual(m.checkpoint({"candidate": other}), cp)


if __name__ == "__main__":
    unittest.main()

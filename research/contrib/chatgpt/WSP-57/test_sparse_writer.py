"""WSP57 prospective SELFTEST: charged active vs random interventions.

All source dynamics remain evaluator-only. Learners see identical initial 12
unary probes and separately selected 24 charged pair actions, never oracle
tables or heldout outcomes until scoring. No DEV/PRIMARY exposure.
"""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from random import Random
import inspect
import json
import time
import unittest

import sparse_writer
from sparse_writer import SparsePermutationWriter, ALL_QUERIES
from source import SEEDS, build_world


def score(model, world, heldout):
    correct = wrong = abstain = 0
    for query in heldout:
        guess = model.predict(*query)
        true = world.query(*query).after
        if guess is None:
            abstain += 1
        elif guess == true:
            correct += 1
        else:
            wrong += 1
    return {"correct": correct, "wrong_confident": wrong,
            "abstain": abstain, "total": len(heldout)}


class SparseActiveResearch(unittest.TestCase):
    def test_learner_source_isolation_costs(self):
        code = Path(sparse_writer.__file__).read_text("utf-8")
        self.assertNotIn("from source import", code)
        self.assertNotIn("import source", code)
        self.assertEqual(SparsePermutationWriter.gradient_steps, 0)
        self.assertEqual(list(inspect.signature(SparsePermutationWriter.predict).parameters),
                         ["self", "first", "second", "before"])
        with self.assertRaises(PermissionError):
            build_world(2301, cohort="PRIMARY")
        with self.assertRaises(PermissionError):
            build_world(2301, cohort="DEV")
        world = build_world(2301)
        first = world.unary()[0]
        model = SparsePermutationWriter()
        for invalid in (replace(first, action_cost=0), replace(first, first=4),
                        replace(first, before=7), replace(first, after=7),
                        replace(first, second=1)):
            with self.assertRaises(ValueError):
                model.observe(invalid)
        self.assertEqual(len(model.rows), 0)
        self.assertIsNone(model.predict(0, 1, 0))

    def test_six_frozen_worlds_matched_action_budget(self):
        results = []
        a_correct = r_correct = a_wrong = r_wrong = 0
        total_unseen = 0
        unary_correct = 0
        for seed in SEEDS:
            with self.subTest(seed=seed):
                world = build_world(seed)
                self.assertEqual(world.receipt(), build_world(seed).receipt())
                active = SparsePermutationWriter()
                random_control = SparsePermutationWriter()
                unary_control = SparsePermutationWriter()
                started = time.perf_counter()
                cpu_started = time.process_time()
                for row in world.unary():
                    for arm in (active, random_control, unary_control):
                        arm.observe(row)
                self.assertEqual(active.hypothesis_counts(), (24, 24, 24, 24))
                self.assertEqual(random_control.hypothesis_counts(), (24, 24, 24, 24))
                salt = int.from_bytes(sha256(
                    f"WSP57|random-policy|{seed}".encode("ascii")).digest(), "big")
                rng = Random(salt)
                for _ in range(24):
                    aq = active.select_active()
                    rq = rng.choice(random_control.available_actions())
                    self.assertNotEqual(active.predict(*aq), -1)
                    active.observe(world.query(*aq))
                    random_control.observe(world.query(*rq))
                self.assertEqual(len(active.rows), len(random_control.rows))
                self.assertEqual(len(active.rows), 36)
                self.assertEqual(len(active.pairs), len(random_control.pairs))
                self.assertEqual(len(active.pairs), 24)
                observed = {(i, j, x) for i, j, x, y in
                            active.pairs + random_control.pairs}
                shared = tuple(q for q in ALL_QUERIES if q not in observed)
                self.assertGreaterEqual(len(shared), 36)
                a = score(active, world, shared)
                r = score(random_control, world, shared)
                u = score(unary_control, world, shared)
                a_correct += a["correct"]
                r_correct += r["correct"]
                unary_correct += u["correct"]
                a_wrong += a["wrong_confident"]
                r_wrong += r["wrong_confident"]
                total_unseen += len(shared)
                self.assertEqual(a["total"], r["total"])
                self.assertEqual(a["total"], u["total"])
                self.assertEqual(active.gradient_steps, 0)
                self.assertEqual(random_control.gradient_steps, 0)
                for arm in (active, random_control):
                    snap = arm.snapshot()
                    cold = SparsePermutationWriter.restore(snap)
                    self.assertEqual(cold.snapshot(), snap)
                    self.assertEqual(score(cold, world, shared),
                                     score(arm, world, shared))
                    with self.assertRaises(ValueError):
                        SparsePermutationWriter.restore(snap.replace(
                            "wsp57.sparse-writer.v1", "wsp57.sparse-writer.v2"))
                    self.assertLessEqual(arm.capacity_bits(), 1000000 * 8)
                wall = time.perf_counter() - started
                cpu = time.process_time() - cpu_started
                def trace_digest(arm):
                    return sha256(json.dumps(arm.rows, sort_keys=True,
                                    separators=(",", ":")).encode("ascii")).hexdigest()
                results.append({
                    "seed": seed, "source": world.receipt(),
                    "shared_heldout": len(shared),
                    "active": a, "random": r, "unary_only_unmatched": u,
                    "active_candidates": active.hypothesis_counts(),
                    "random_candidates": random_control.hypothesis_counts(),
                    "initial_candidates": [24, 24, 24, 24],
                    "active_trajectory_sha256": trace_digest(active),
                    "random_trajectory_sha256": trace_digest(random_control),
                    "active_search_checks": active.total_checks,
                    "random_search_checks": random_control.total_checks,
                    "active_persistent_bits": active.capacity_bits(),
                    "random_persistent_bits": random_control.capacity_bits(),
                    "wall_seconds": round(wall, 6),
                    "cpu_seconds": round(cpu, 6)
                })
        active_rate = a_correct / total_unseen
        random_rate = r_correct / total_unseen
        classification = (
            "SELFTEST_SIGNAL" if
            active_rate - random_rate >= 0.10 and active_rate >= 0.40
            and a_wrong == 0 and r_wrong == 0
            else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE"
        )
        print("WSP57_SELFTEST_DIAGNOSTIC " + json.dumps({
            "classification": classification,
            "total_common_heldout": total_unseen,
            "active_correct": a_correct, "random_correct": r_correct,
            "unary_only_correct": unary_correct,
            "active_wrong_confident": a_wrong,
            "random_wrong_confident": r_wrong,
            "active_accuracy": round(active_rate, 8),
            "random_accuracy": round(random_rate, 8),
            "active_minus_random": round(active_rate - random_rate, 8),
            "fixtures": results
        }, sort_keys=True, separators=(",", ":")))
        self.assertEqual(len(results), 6)
        # Negative outcomes are preserved as valid exploratory observations.


if __name__ == "__main__":
    unittest.main()

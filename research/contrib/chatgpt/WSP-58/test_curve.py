"""WSP58 frozen early-budget policy comparison, SELFTEST only.

Evaluator-only WSP58 source independently samples fresh worlds. Reuses the exact
WSP57 constraint learner without changing its hypothesis family, action policy
or prior. Outcomes of uncharged actions are never passed to the learner.
"""
from __future__ import annotations
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from random import Random
import inspect
import json
import sys
import time
import unittest

from source import build_world, SEEDS
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "WSP-57"))
import sparse_writer
from sparse_writer import SparsePermutationWriter, ALL_QUERIES

CHECKPOINTS = (0, 4, 8, 12, 16, 24)
PRIMARY = 8


def score(writer, world, questions):
    c = {"correct": 0, "wrong_confident": 0,
         "abstain": 0, "total": len(questions)}
    for q in questions:
        p = writer.predict(*q)
        if p is None:
            c["abstain"] += 1
        elif p == world.query(*q).after:
            c["correct"] += 1
        else:
            c["wrong_confident"] += 1
    return c


def digest_ledger(writer):
    msg = json.dumps(writer.rows, sort_keys=True, separators=(",", ":")).encode("ascii")
    return sha256(msg).hexdigest()


class EarlyBudgetCausalResearch(unittest.TestCase):
    def test_guardrails_and_source_isolation(self):
        learner_src = Path(sparse_writer.__file__).read_text("utf-8")
        self.assertNotIn("from source import", learner_src)
        self.assertNotIn("import source", learner_src)
        self.assertEqual(SparsePermutationWriter.gradient_steps, 0)
        self.assertEqual(
            list(inspect.signature(SparsePermutationWriter.predict).parameters),
            ["self", "first", "second", "before"])
        for cohort in ("DEV", "PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(2401, cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(2301)
        world = build_world(2401)
        learner = SparsePermutationWriter()
        invalid = replace(world.unary()[0], action_cost=0)
        with self.assertRaises(ValueError):
            learner.observe(invalid)
        self.assertEqual(len(learner.rows), 0)

    def test_prospective_curve_twelve_fresh_worlds(self):
        records = []
        aggregate = {
            b: {"heldout": 0, "active_correct": 0, "random_correct": 0,
                "unary_correct": 0, "active_wrong": 0, "random_wrong": 0}
            for b in CHECKPOINTS
        }
        for seed in SEEDS:
            with self.subTest(seed=seed):
                world = build_world(seed)
                self.assertEqual(world.receipt(), build_world(seed).receipt())
                active = SparsePermutationWriter()
                random_arm = SparsePermutationWriter()
                unary_only = SparsePermutationWriter()
                start_time, start_cpu = time.perf_counter(), time.process_time()
                for row in world.unary():
                    for arm in (active, random_arm, unary_only):
                        arm.observe(row)
                self.assertEqual(active.hypothesis_counts(), (24, 24, 24, 24))
                self.assertEqual(random_arm.hypothesis_counts(), (24, 24, 24, 24))
                salt = int.from_bytes(sha256(
                    f"WSP58|SELFTEST|random-policy|{seed}".encode("ascii")
                ).digest(), "big")
                rng = Random(salt)
                select_time = update_time = 0.
                checkpoints = {}

                for b in range(25):
                    if b in CHECKPOINTS:
                        asked = {
                            (i, j, x)
                            for arm in (active, random_arm)
                            for i, j, x, _ in arm.pairs
                        }
                        heldout = tuple(q for q in ALL_QUERIES if q not in asked)
                        self.assertGreaterEqual(len(heldout), 36)
                        self.assertEqual(len(active.rows), 12+b)
                        self.assertEqual(len(random_arm.rows), 12+b)
                        a = score(active, world, heldout)
                        r = score(random_arm, world, heldout)
                        u = score(unary_only, world, heldout)
                        aggregate[b]["heldout"] += len(heldout)
                        aggregate[b]["active_correct"] += a["correct"]
                        aggregate[b]["random_correct"] += r["correct"]
                        aggregate[b]["unary_correct"] += u["correct"]
                        aggregate[b]["active_wrong"] += a["wrong_confident"]
                        aggregate[b]["random_wrong"] += r["wrong_confident"]
                        checkpoints[b] = {
                            "heldout": len(heldout),
                            "active": a, "random": r, "unary_only": u,
                            "active_hypotheses": active.hypothesis_counts(),
                            "random_hypotheses": random_arm.hypothesis_counts(),
                            "active_action_sha256": digest_ledger(active),
                            "random_action_sha256": digest_ledger(random_arm),
                            "active_candidate_checks": active.total_checks,
                            "random_candidate_checks": random_arm.total_checks
                        }
                        if b in (PRIMARY, 24):
                            for arm, expected in ((active, a), (random_arm, r)):
                                snapshot = arm.snapshot()
                                cold = SparsePermutationWriter.restore(snapshot)
                                self.assertEqual(cold.snapshot(), snapshot)
                                self.assertEqual(score(cold, world, heldout), expected)
                                with self.assertRaises(ValueError):
                                    SparsePermutationWriter.restore(
                                        snapshot.replace("wsp57.sparse-writer.v1",
                                                         "wsp57.sparse-writer.v2"))
                                self.assertLessEqual(arm.capacity_bits(), 8000000)
                    if b == 24:
                        break
                    tick = time.perf_counter()
                    q_a = active.select_active()
                    q_r = rng.choice(random_arm.available_actions())
                    select_time += time.perf_counter() - tick
                    tick = time.perf_counter()
                    active.observe(world.query(*q_a))
                    random_arm.observe(world.query(*q_r))
                    update_time += time.perf_counter() - tick

                self.assertEqual(len(active.rows), 36)
                self.assertEqual(len(random_arm.rows), 36)
                self.assertEqual(active.gradient_steps, 0)
                self.assertEqual(random_arm.gradient_steps, 0)
                records.append({
                    "seed": seed, "source": world.receipt(),
                    "checkpoints": {str(k): v for k, v in checkpoints.items()},
                    "active_select_wall_seconds": round(select_time, 6),
                    "joint_update_wall_seconds": round(update_time, 6),
                    "whole_experiment_wall_seconds": round(time.perf_counter()-start_time, 6),
                    "whole_experiment_cpu_seconds": round(time.process_time()-start_cpu, 6),
                    "active_bits_final": active.capacity_bits(),
                    "random_bits_final": random_arm.capacity_bits()
                })

        results = {}
        for b in CHECKPOINTS:
            s = aggregate[b]
            n = s["heldout"]
            active_rate = s["active_correct"] / n
            random_rate = s["random_correct"] / n
            results[str(b)] = {
                **s,
                "active_rate": round(active_rate, 8),
                "random_rate": round(random_rate, 8),
                "absolute_gain": round(active_rate-random_rate, 8),
                "unary_rate": round(s["unary_correct"]/n, 8),
                "actions_per_arm": 12+b
            }

        primary = results[str(PRIMARY)]
        classification = ("SELFTEST_SIGNAL" if
                          primary["absolute_gain"] >= 0.10 and
                          primary["active_rate"] >= 0.35 and
                          primary["active_wrong"] == 0 and
                          primary["random_wrong"] == 0
                          else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP58_SELFTEST_DIAGNOSTIC " + json.dumps({
            "classification": classification,
            "frozen_primary_pair_budget": PRIMARY,
            "primary": primary,
            "curve": results,
            "worlds": records
        }, sort_keys=True, separators=(",", ":")))
        self.assertEqual(len(records), 12)
        self.assertEqual(len(results), len(CHECKPOINTS))
        self.assertGreater(primary["heldout"], 600)
        # A frozen negative is valid exploratory evidence, not workflow failure.


if __name__ == "__main__":
    unittest.main()

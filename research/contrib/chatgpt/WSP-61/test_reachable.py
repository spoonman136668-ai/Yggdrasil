"""WSP61 prospective SELFTEST of no-reset online causal learning.

Two arms physically traverse each hidden source world for exactly 80 steps.
No training arbitrary-state queries; the learner sees only the current
charged state-action-consequence from a session. Evaluator-only state/audit/
task labels are withheld from both agents until final scoring.
"""
from __future__ import annotations
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from random import Random
import inspect
import json
import time
import unittest

from source import SEEDS, STATES, CHANNELS, INITIAL, TRAIN_ACTIONS, build_world
from learner import ReachableCausalLearner


def digest(learner):
    b = json.dumps(learner.ledger, sort_keys=True,
                   separators=(",", ":")).encode("ascii")
    return sha256(b).hexdigest()


def audit(learner, world):
    counts = {"correct": 0, "wrong_confident": 0, "abstain": 0}
    for state in STATES:
        for action in CHANNELS:
            prediction = learner.predict(state, action)
            truth = world._step_oracle(state, action)  # evaluator-only audit
            if prediction is None:
                counts["abstain"] += 1
            elif prediction == truth:
                counts["correct"] += 1
            else:
                counts["wrong_confident"] += 1
    assert sum(counts.values()) == 64
    return counts


def goals(learner, world, tasks, memory_only=False):
    successes = 0
    abstain = 0
    for task in tasks:
        plan = learner.plan(task.start, task.target, memory_only=memory_only)
        if plan is None:
            abstain += 1
            continue
        if world.evaluate(task, plan):
            successes += 1
    return {"success": successes, "abstain": abstain, "total": len(tasks)}


class NoResetResearch(unittest.TestCase):
    def test_source_separation_and_sequential_custody(self):
        src = (Path(__file__).parent/"learner.py").read_text("utf-8")
        self.assertNotIn("from source import", src)
        self.assertNotIn("import source", src)
        self.assertEqual(ReachableCausalLearner.gradient_updates, 0)
        self.assertEqual(
            list(inspect.signature(ReachableCausalLearner.plan).parameters),
            ["self", "start", "target", "horizon", "memory_only"])
        for cohort in ("DEV", "PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(2701, cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(2501)
        world = build_world(2701)
        self.assertEqual(world.receipt(), build_world(2701).receipt())
        self.assertEqual(len(world.tasks()), 32)
        a = ReachableCausalLearner()
        session = world.training_session()
        first = session.step(0)
        with self.assertRaises(ValueError):
            a.observe(replace(first, before=(1, 1, 1, 1)))
        with self.assertRaises(ValueError):
            a.observe(replace(first, action_cost=0))
        with self.assertRaises(ValueError):
            a.observe(replace(first, after=(2, 0, 0, 0)))
        self.assertEqual(len(a.ledger), 0)
        a.observe(first)
        self.assertEqual(a.state, session.state)
        with self.assertRaises(ValueError):
            a.observe(first)
        with self.assertRaises(ValueError):
            a.predict((0, 0, 0, 0), 4)

    def test_twelve_frozen_reachable_worlds(self):
        rows = []
        total = {"tasks": 0, "active_success": 0, "random_success": 0,
                 "lookup_success": 0, "active_wrong": 0,
                 "active_abstain": 0, "active_visited_states": 0,
                 "random_visited_states": 0}
        for seed in SEEDS:
            with self.subTest(seed=seed):
                world = build_world(seed)
                receipt = world.receipt()
                self.assertEqual(receipt, build_world(seed).receipt())
                active = ReachableCausalLearner()
                random_arm = ReachableCausalLearner()
                live_a = world.training_session()
                live_r = world.training_session()
                rng = Random(int.from_bytes(sha256(
                    f"WSP61|random-channels|{seed}".encode("ascii")
                ).digest(), "big"))
                started = time.perf_counter()
                cpu_started = time.process_time()
                active_decision_seconds = 0.0
                for _ in range(TRAIN_ACTIONS):
                    tick = time.perf_counter()
                    a_action = active.select_action()
                    active_decision_seconds += time.perf_counter()-tick
                    r_action = rng.choice(CHANNELS)
                    # The only charged training interface is Session.step().
                    row_a = live_a.step(a_action)
                    row_r = live_r.step(r_action)
                    active.observe(row_a)
                    random_arm.observe(row_r)
                    self.assertEqual(active.state, live_a.state)
                    self.assertEqual(random_arm.state, live_r.state)
                self.assertEqual(len(active.ledger), 80)
                self.assertEqual(len(random_arm.ledger), 80)
                self.assertEqual(len(live_a.ledger), 80)
                self.assertEqual(len(live_r.ledger), 80)
                self.assertEqual(active.gradient_updates, 0)
                self.assertEqual(random_arm.gradient_updates, 0)
                self.assertEqual(active.ledger[0][0], INITIAL)
                self.assertEqual(random_arm.ledger[0][0], INITIAL)
                self.assertTrue(all(active.ledger[i][2] == active.ledger[i+1][0]
                                    for i in range(79)))
                self.assertTrue(all(random_arm.ledger[i][2] == random_arm.ledger[i+1][0]
                                    for i in range(79)))
                before_restore = active.snapshot()
                cold = ReachableCausalLearner.restore(before_restore)
                self.assertEqual(cold.snapshot(), before_restore)
                with self.assertRaises(ValueError):
                    ReachableCausalLearner.restore(
                        before_restore.replace(
                            "wsp61.no-reset-learner.v1",
                            "wsp61.no-reset-learner.v2"))
                truth_a = audit(active, world)
                truth_r = audit(random_arm, world)
                self.assertEqual(audit(cold, world), truth_a)
                tasks = world.tasks()
                score_a = goals(active, world, tasks)
                score_r = goals(random_arm, world, tasks)
                score_lookup = goals(active, world, tasks, memory_only=True)
                self.assertEqual(goals(cold, world, tasks), score_a)
                self.assertEqual(len(tasks), 32)
                self.assertEqual(truth_a["correct"]+
                                 truth_a["wrong_confident"]+
                                 truth_a["abstain"], 64)
                total["tasks"] += len(tasks)
                total["active_success"] += score_a["success"]
                total["random_success"] += score_r["success"]
                total["lookup_success"] += score_lookup["success"]
                total["active_wrong"] += truth_a["wrong_confident"]
                total["active_abstain"] += truth_a["abstain"]
                total["active_visited_states"] += len(active.state_visits)
                total["random_visited_states"] += len(random_arm.state_visits)
                rows.append({
                    "seed": seed, "family": world.family,
                    "source": receipt,
                    "train_actions_active": len(active.ledger),
                    "train_actions_random": len(random_arm.ledger),
                    "active_state_count": len(active.state_visits),
                    "random_state_count": len(random_arm.state_visits),
                    "active_pair_count": len({(b,a) for b,a,y in active.ledger}),
                    "random_pair_count": len({(b,a) for b,a,y in random_arm.ledger}),
                    "active_ledger_sha256": digest(active),
                    "random_ledger_sha256": digest(random_arm),
                    "active_audit": truth_a,
                    "random_audit": truth_r,
                    "active_goal": score_a,
                    "random_goal": score_r,
                    "lookup_goal": score_lookup,
                    "active_candidate_counts": active.hypothesis_counts(),
                    "random_candidate_counts": random_arm.hypothesis_counts(),
                    "active_numeric_entries": active.numeric_entry_count(),
                    "random_numeric_entries": random_arm.numeric_entry_count(),
                    "active_snapshot_bits": active.capacity_bits(),
                    "random_snapshot_bits": random_arm.capacity_bits(),
                    "active_decision_seconds": round(active_decision_seconds, 6),
                    "whole_world_wall_seconds": round(time.perf_counter()-started, 6),
                    "whole_world_cpu_seconds": round(time.process_time()-cpu_started, 6)
                })
        self.assertEqual(len(rows), 12)
        self.assertEqual(total["tasks"], 384)
        active_rate = total["active_success"] / 384
        random_rate = total["random_success"] / 384
        status = ("SELFTEST_SIGNAL" if
                  active_rate >= .55 and
                  active_rate-random_rate >= .10 and
                  total["active_wrong"] == 0
                  else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP61_SELFTEST_DIAGNOSTIC " + json.dumps({
            "classification": status, "total": total,
            "active_rate": round(active_rate, 8),
            "random_rate": round(random_rate, 8),
            "gain": round(active_rate-random_rate, 8),
            "worlds": rows
        }, sort_keys=True, separators=(",", ":")))
        # Frozen negative outcomes remain valid scientific development evidence.


if __name__ == "__main__":
    unittest.main()

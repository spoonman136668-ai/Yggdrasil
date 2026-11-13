"""WSP60 frozen SELFTEST: causal counterexamples and grounded multistep plans.

The evaluator imports the hidden simulator; the learner does not. Disjoint
fresh seeds, matched 40/44/48 charged interactions and nine taught byte goals
for every arm. Frozen PRIMARY is the 44-action checkpoint, not 48.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from random import Random
import json
import time
import unittest

from source import build_world, SEEDS, STATES, CHANNELS
from identifying_agent import IdentifyingAgent, BaseAgent
from agent import pairwise_coverage_probes

PRIMARY = 44
SECONDARY = 48


def digest(rows):
    return sha256(json.dumps(rows, sort_keys=True,
                             separators=(",", ":")).encode("ascii")).hexdigest()


def evaluate_agent(agent, world, tasks, *, memory_only=False):
    success = 0
    plans = []
    grounded = 0
    for task in tasks:
        if agent.decode(task.raw_instruction) == task._goal:
            grounded += 1
        plan = agent.plan(task.before, task.raw_instruction,
                          memory_only=memory_only)
        plans.append(plan)
        if plan is not None and world.evaluate(task, plan):
            success += 1
            if agent.decode(task.raw_instruction) == task._goal:
                assert len(plan) == task._shortest
    return success, grounded, plans


def source_prediction_audit(agent, world):
    correct = wrong = abstain = 0
    for state in STATES:
        for action in CHANNELS:
            prediction = agent.predict(state, action)
            if prediction is None:
                abstain += 1
            elif prediction == world.step(state, action):
                correct += 1
            else:
                wrong += 1
    assert correct + wrong + abstain == 80
    return {"correct": correct, "wrong_confident": wrong, "abstain": abstain}


class CounterexampleResearch(unittest.TestCase):
    def test_source_isolation_and_custody(self):
        learner_text = (Path(__file__).parent / "identifying_agent.py").read_text("utf-8")
        self.assertNotIn("from source import", learner_text)
        self.assertNotIn("import source", learner_text)
        self.assertEqual(IdentifyingAgent.gradient_updates, 0)
        for blocked in ("DEV", "PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(2601, cohort=blocked)
        with self.assertRaises(PermissionError):
            build_world(2501)
        world = build_world(2601)
        self.assertEqual(len(world.demonstrations()), 9)
        self.assertEqual(len(world.tasks()), 32)
        self.assertEqual(world.receipt(), build_world(2601).receipt())
        samples = pairwise_coverage_probes()
        self.assertEqual(len(samples), 10)
        agent = IdentifyingAgent()
        self.assertEqual(agent.gradient_updates, 0)
        with self.assertRaises(ValueError):
            agent.select_disambiguating(0)
        with self.assertRaises(ValueError):
            agent.observe((6, 0, 0), 0, (0, 0, 0))

    def test_twelve_world_frozen_primary_and_secondary(self):
        coverage = pairwise_coverage_probes()
        results = []
        aggregate = {
            40: {"active": 0, "random": 0, "old_minimal": 0, "lookup": 0,
                 "shuffled": 0, "grounded": 0, "wrong": 0, "abstain": 0},
            44: {"active": 0, "random": 0, "old_minimal": 0, "lookup": 0,
                 "shuffled": 0, "grounded": 0, "wrong": 0, "abstain": 0},
            48: {"active": 0, "random": 0, "old_minimal": 0, "lookup": 0,
                 "shuffled": 0, "grounded": 0, "wrong": 0, "abstain": 0}
        }
        for seed in SEEDS:
            with self.subTest(seed=seed):
                world = build_world(seed)
                active, random_arm = IdentifyingAgent(), IdentifyingAgent()
                old, shuffled = BaseAgent(), IdentifyingAgent()
                demos = world.demonstrations()
                for idx, demo in enumerate(demos):
                    for agent in (active, random_arm, old):
                        agent.teach(demo.raw_instruction, demo.grounded_predicate)
                    shuffled.teach(demo.raw_instruction,
                                   demos[(idx+1) % 9].grounded_predicate)
                begin, cpu_begin = time.perf_counter(), time.process_time()
                for action in CHANNELS:
                    for state in coverage:
                        after = world.step(state, action)
                        for agent in (active, random_arm, old, shuffled):
                            agent.observe(state, action, after)
                self.assertEqual(len(active.rows), 40)
                self.assertEqual(len(random_arm.rows), 40)
                self.assertEqual(len(old.rows), 40)
                self.assertEqual(len(shuffled.rows), 40)
                rng = Random(int.from_bytes(sha256(
                    f"WSP60|random-extra-counterexample|{seed}".encode("ascii")
                ).digest(), "big"))
                tasks = world.tasks()
                checkpoints = {}
                for extra_round in (0, 1, 2):
                    budget = 40 + 4*extra_round
                    if extra_round:
                        for action in CHANNELS:
                            state_a = active.select_disambiguating(action)
                            observed_random = {b for b, a, y in random_arm.rows
                                               if a == action}
                            options = [s for s in STATES if s not in observed_random]
                            state_r = rng.choice(options)
                            value_a = world.step(state_a, action)
                            value_r = world.step(state_r, action)
                            active.observe(state_a, action, value_a)
                            random_arm.observe(state_r, action, value_r)
                            old.observe(state_a, action, value_a)
                            shuffled.observe(state_a, action, value_a)
                    for arm in (active, random_arm, old, shuffled):
                        self.assertEqual(len(arm.rows), budget)
                        self.assertEqual(len(arm.demos), 9)
                    active_n, grounded_n, plans = evaluate_agent(active, world, tasks)
                    random_n, _, _ = evaluate_agent(random_arm, world, tasks)
                    old_n, _, _ = evaluate_agent(old, world, tasks)
                    lookup_n, _, _ = evaluate_agent(old, world, tasks, memory_only=True)
                    shuffled_n, _, _ = evaluate_agent(shuffled, world, tasks)
                    audit = source_prediction_audit(active, world)
                    aggregate[budget]["active"] += active_n
                    aggregate[budget]["random"] += random_n
                    aggregate[budget]["old_minimal"] += old_n
                    aggregate[budget]["lookup"] += lookup_n
                    aggregate[budget]["shuffled"] += shuffled_n
                    aggregate[budget]["grounded"] += grounded_n
                    aggregate[budget]["wrong"] += audit["wrong_confident"]
                    aggregate[budget]["abstain"] += audit["abstain"]
                    checkpoints[str(budget)] = {
                        "active_solved": active_n, "random_solved": random_n,
                        "old_minimal_solved": old_n, "lookup_solved": lookup_n,
                        "shuffled_solved": shuffled_n, "grounded": grounded_n,
                        "transition_audit": audit,
                        "active_hypotheses": active.candidate_counts(),
                        "random_hypotheses": random_arm.candidate_counts(),
                        "active_numeric_entries": active.numeric_table_entries(),
                        "active_action_sha256": digest(active.rows),
                        "random_action_sha256": digest(random_arm.rows),
                        "active_snapshot_bits": active.capacity_bits(),
                        "random_snapshot_bits": random_arm.capacity_bits()
                    }
                    if budget in (PRIMARY, SECONDARY):
                        for agent in (active, random_arm):
                            snap = agent.snapshot()
                            cold = IdentifyingAgent.restore(snap)
                            self.assertEqual(cold.snapshot(), snap)
                            for state in STATES:
                                for action in CHANNELS:
                                    self.assertEqual(cold.predict(state, action),
                                                     agent.predict(state, action))
                            self.assertEqual(
                                evaluate_agent(cold, world, tasks)[0],
                                evaluate_agent(agent, world, tasks)[0])
                            with self.assertRaises(ValueError):
                                IdentifyingAgent.restore(snap.replace(
                                    "wsp59.grounded-causal-agent.v1",
                                    "wsp59.grounded-causal-agent.v2"))
                results.append({
                    "seed": seed, "source_receipt": world.receipt(),
                    "heldout_tasks": 32,
                    "checkpoints": checkpoints,
                    "total_wall_seconds": round(time.perf_counter()-begin, 6),
                    "total_cpu_seconds": round(time.process_time()-cpu_begin, 6)
                })
        primary = aggregate[PRIMARY]
        n = len(SEEDS)*32
        primary_rate = primary["active"]/n
        random_rate = primary["random"]/n
        gain = primary_rate-random_rate
        classification = (
            "SELFTEST_SIGNAL" if
            primary["active"] >= 250 and
            primary["active"] - primary["random"] >= 47 and
            primary["wrong"] == 0 and primary["grounded"] == n
            else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE"
        )
        print("WSP60_SELFTEST_DIAGNOSTIC " + json.dumps({
            "classification": classification,
            "heldout_tasks": n,
            "frozen_primary_budget": PRIMARY,
            "active_rate_primary": round(primary_rate, 8),
            "random_rate_primary": round(random_rate, 8),
            "gain_primary": round(gain, 8),
            "checkpoints": aggregate,
            "worlds": results
        }, sort_keys=True, separators=(",", ":")))
        self.assertEqual(len(results), 12)
        self.assertEqual(n, 384)
        self.assertEqual(len(aggregate), 3)
        # A criterion miss is recorded as negative; never silently retuned.


if __name__ == "__main__":
    unittest.main()

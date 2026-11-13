"""Prospective WSP59 SELFTEST: grounded unfamiliar-world causal planning.

No protected data or model initialization from source.py. Only the evaluator
imports the hidden world generator; causal agent imports no simulator/module.
All controls receive precisely 40 charged observations and nine demonstrations.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from random import Random
import json
import time
import unittest

from agent import GroundedCausalAgent, STATES, CHANNELS, pairwise_coverage_probes
from source import SEEDS, build_world, PREDICATES


def hash_public(rows):
    return sha256(json.dumps(rows, sort_keys=True,
                             separators=(",", ":")).encode("ascii")).hexdigest()


class GeneralizationWorldResearch(unittest.TestCase):
    def test_guardrails_and_source_independence(self):
        agent_source = (Path(__file__).parent / "agent.py").read_text("utf-8")
        self.assertNotIn("from source import", agent_source)
        self.assertNotIn("import source", agent_source)
        self.assertEqual(GroundedCausalAgent.gradient_updates, 0)
        for cohort in ("DEV", "PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(2501, cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(2401)
        world = build_world(2501)
        self.assertEqual(len(world.demonstrations()), 9)
        self.assertEqual(len(world.tasks()), 32)
        self.assertEqual(world.receipt(), build_world(2501).receipt())
        self.assertEqual(len(pairwise_coverage_probes()), 10)
        agent = GroundedCausalAgent()
        with self.assertRaises(ValueError):
            agent.observe((9, 1, 0), 0, (0, 0, 0))
        with self.assertRaises(ValueError):
            agent.observe((1, 0, 0), 4, (1, 0, 0))
        with self.assertRaises(ValueError):
            agent.teach(b"a & b", (0, 1))
        self.assertEqual(agent.rows, [])

    def test_eight_unfamiliar_worlds_grounding_and_planning(self):
        records = []
        active_success = random_success = lookup_success = shuffled_success = 0
        correct_grounded = transition_wrong = transition_abstain = 0
        active_plan_len_sum = 0
        total_tasks = 0
        for seed in SEEDS:
            with self.subTest(seed=seed):
                world = build_world(seed)
                active = GroundedCausalAgent()
                random_arm = GroundedCausalAgent()
                shuffled = GroundedCausalAgent()
                demos = world.demonstrations()
                self.assertEqual(len(demos), 9)
                for idx, demo in enumerate(demos):
                    active.teach(demo.raw_instruction, demo.grounded_predicate)
                    random_arm.teach(demo.raw_instruction, demo.grounded_predicate)
                    shuffled.teach(
                        demo.raw_instruction,
                        demos[(idx+1) % len(demos)].grounded_predicate
                    )
                known = pairwise_coverage_probes()
                rng = Random(int.from_bytes(sha256(
                    f"WSP59|SELFTEST|control-random-policy|{seed}".encode("ascii")
                ).digest(), "big"))
                start = time.perf_counter()
                cpu_start = time.process_time()
                for action in CHANNELS:
                    unknown = rng.sample(list(STATES), 10)
                    for state in known:
                        after = world.step(state, action)
                        active.observe(state, action, after)
                        shuffled.observe(state, action, after)
                    for state in unknown:
                        random_arm.observe(state, action, world.step(state, action))
                self.assertEqual(len(active.rows), 40)
                self.assertEqual(len(random_arm.rows), 40)
                self.assertEqual(len(shuffled.rows), 40)
                self.assertEqual(len(active.demos), 9)
                self.assertEqual(len(random_arm.demos), 9)
                self.assertEqual(len(shuffled.demos), 9)
                self.assertTrue(any(row[0] not in known for row in random_arm.rows))
                snapshot = active.snapshot()
                cold = GroundedCausalAgent.restore(snapshot)
                self.assertEqual(cold.snapshot(), snapshot)
                with self.assertRaises(ValueError):
                    GroundedCausalAgent.restore(snapshot.replace(
                        "wsp59.grounded-causal-agent.v1",
                        "wsp59.grounded-causal-agent.v2"))
                with self.assertRaises(ValueError):
                    cold.observe(known[0], 0, world.step(known[0], 0))
                self.assertEqual(active.gradient_updates, 0)
                self.assertEqual(active.capacity_bits(), cold.capacity_bits())

                transitions = {"correct": 0, "wrong_confident": 0, "abstain": 0}
                for before in STATES:
                    for action in CHANNELS:
                        guess = active.predict(before, action)
                        true = world.step(before, action)
                        if guess is None:
                            transitions["abstain"] += 1
                        elif guess == true:
                            transitions["correct"] += 1
                        else:
                            transitions["wrong_confident"] += 1
                        self.assertEqual(cold.predict(before, action), guess)
                transition_wrong += transitions["wrong_confident"]
                transition_abstain += transitions["abstain"]
                tasks = world.tasks()
                wins = {"active": 0, "random": 0,
                        "lookup_only": 0, "shuffled_demos": 0}
                grounded = 0
                plan_lengths = []
                for task in tasks:
                    self.assertGreaterEqual(task._shortest, 2)
                    self.assertLessEqual(task._shortest, 4)
                    decoded = active.decode(task.raw_instruction)
                    if decoded == task._goal:
                        grounded += 1
                    self.assertEqual(cold.decode(task.raw_instruction), decoded)
                    trials = {
                        "active": active.plan(task.before, task.raw_instruction),
                        "random": random_arm.plan(task.before, task.raw_instruction),
                        "lookup_only": active.plan(
                            task.before, task.raw_instruction, memory_only=True),
                        "shuffled_demos": shuffled.plan(
                            task.before, task.raw_instruction)
                    }
                    self.assertEqual(
                        cold.plan(task.before, task.raw_instruction),
                        trials["active"])
                    for name, path in trials.items():
                        if path is not None:
                            self.assertLessEqual(len(path), 4)
                            if world.evaluate(task, path):
                                wins[name] += 1
                                if name == "active":
                                    plan_lengths.append(len(path))
                                    self.assertEqual(len(path), task._shortest)
                correct_grounded += grounded
                active_success += wins["active"]
                random_success += wins["random"]
                lookup_success += wins["lookup_only"]
                shuffled_success += wins["shuffled_demos"]
                active_plan_len_sum += sum(plan_lengths)
                total_tasks += len(tasks)
                records.append({
                    "seed": seed,
                    "source": world.receipt(),
                    "charged_actions_each_policy": 40,
                    "grounding_demonstrations_each": 9,
                    "grounded_conjunctions_exact": grounded,
                    "heldout_tasks": len(tasks),
                    "transition": transitions,
                    "solved": wins,
                    "active_numeric_entries": active.numeric_table_entries(),
                    "random_numeric_entries": random_arm.numeric_table_entries(),
                    "active_snapshot_bits": active.capacity_bits(),
                    "random_snapshot_bits": random_arm.capacity_bits(),
                    "active_action_ledger_sha256": hash_public(active.rows),
                    "random_action_ledger_sha256": hash_public(random_arm.rows),
                    "wall_seconds": round(time.perf_counter() - start, 6),
                    "cpu_seconds": round(time.process_time() - cpu_start, 6)
                })
        self.assertEqual(total_tasks, 256)
        rate_a = active_success / total_tasks
        rate_r = random_success / total_tasks
        status = ("SELFTEST_SIGNAL" if
                  rate_a >= .65 and rate_a - rate_r >= .15 and
                  transition_wrong == 0 and correct_grounded == total_tasks
                  else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        result = {
            "classification": status,
            "worlds": len(SEEDS), "heldout_tasks": total_tasks,
            "active_success": active_success,
            "random_success": random_success,
            "exact_observation_success": lookup_success,
            "shuffled_grounding_success": shuffled_success,
            "active_rate": round(rate_a, 8),
            "random_rate": round(rate_r, 8),
            "active_minus_random": round(rate_a-rate_r, 8),
            "correct_grounded_conjunctions": correct_grounded,
            "active_wrong_confident_transitions": transition_wrong,
            "active_abstained_transitions": transition_abstain,
            "active_success_plan_len_sum": active_plan_len_sum,
            "source_fixtures": records
        }
        print("WSP59_SELFTEST_DIAGNOSTIC " + json.dumps(
            result, sort_keys=True, separators=(",", ":")))
        self.assertEqual(len(records), 8)
        self.assertEqual(sum(r["charged_actions_each_policy"]
                             for r in records), 320)
        self.assertEqual(sum(r["grounding_demonstrations_each"]
                             for r in records), 72)
        # Failure of frozen scientific development criterion is an observation.


if __name__ == "__main__":
    unittest.main()

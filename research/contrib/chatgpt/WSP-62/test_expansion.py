"""Frozen WSP62 source-only SELFTEST: exact-ledger expandable representation.

Evaluator alone imports source.py; all candidate learners see only live charged
action-consequence observations. Frozen original WSP61 policy supplies the
same active sequential ledger to its own fixed model and the WSP62 model,
ensuring improvements are due to representation and not altered exploration.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from random import Random
import inspect
import json
import time
import unittest

from source import SEEDS, STATES, ACTIONS, INITIAL, build_world
from expanded_learner import ExpandedCausalLearner, LinearOnlyLearner
from learner import ReachableCausalLearner


def digest(rows):
    data = json.dumps(rows, separators=(",", ":"), sort_keys=True).encode("ascii")
    return sha256(data).hexdigest()


def audit(agent, world):
    v = {"correct":0,"wrong_confident":0,"abstain":0,
         "unobserved_correct":0,"unobserved_wrong":0,
         "unobserved_abstain":0}
    seen = {(before, action) for before, action, after in agent.ledger}
    for before in STATES:
        for action in ACTIONS:
            value = agent.predict(before, action)
            outcome = world._step_oracle(before, action)  # evaluator only!
            suffix = "unobserved_" if (before, action) not in seen else ""
            if value is None:
                v["abstain"] += 1
                if suffix: v["unobserved_abstain"] += 1
            elif value == outcome:
                v["correct"] += 1
                if suffix: v["unobserved_correct"] += 1
            else:
                v["wrong_confident"] += 1
                if suffix: v["unobserved_wrong"] += 1
    if v["correct"]+v["wrong_confident"]+v["abstain"] != 64:
        raise AssertionError("audit not exhaustive")
    return v


def score(agent, world, tasks, memory_only=False):
    result = {"success":0,"abstain":0,"total":len(tasks)}
    for task in tasks:
        plan = agent.plan(task.start, task.target, memory_only=memory_only)
        if plan is None:
            result["abstain"] += 1
        elif world.evaluate(task, plan):
            result["success"] += 1
    return result


class AdaptiveRepresentationQualification(unittest.TestCase):
    def test_source_boundaries_and_linear_algebra_guard(self):
        source_text = (Path(__file__).parent / "expanded_learner.py").read_text("utf-8")
        self.assertNotIn("import source", source_text)
        self.assertNotIn("from source import", source_text)
        self.assertEqual(ExpandedCausalLearner.gradient_updates, 0)
        self.assertEqual(list(inspect.signature(ExpandedCausalLearner.plan).parameters),
                         ["self","start","target","horizon","memory_only"])
        for cohort in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(2801, cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(2701)
        from expanded_learner import _linear_basis, _certain_value, _features
        self.assertIsNone(_linear_basis([(1,0),(1,1)], 11))
        basis = _linear_basis([(_features((0,0,0,0)), 1)],11)
        self.assertEqual(_certain_value(basis, _features((0,0,0,0))),1)
        self.assertIsNone(_certain_value(basis, _features((1,0,0,0))))
        world=build_world(2801)
        self.assertEqual(world.receipt(),build_world(2801).receipt())
        self.assertEqual(len(world.tasks()),32)
        agent=ExpandedCausalLearner()
        step=world.training_session().step(0)
        with self.assertRaises(ValueError):
            from source import Experience
            agent.observe(Experience((1,1,1,1),0,step.after))
        self.assertEqual(len(agent.ledger),0)

    def test_frozen_twelve_families_and_controls(self):
        results=[]
        overall={"tasks":0,"active":0,"random":0,"fixed_parent":0,
                 "lookup":0,"linear_only":0,"active_wrong":0,
                 "active_unobserved_correct":0,"active_unobserved_wrong":0,
                 "active_unobserved_abstain":0,"expansions":0}
        by_family={}
        for seed in SEEDS:
            with self.subTest(seed=seed):
                world=build_world(seed)
                self.assertEqual(world.receipt(),build_world(seed).receipt())
                base=ReachableCausalLearner()
                adaptive=ExpandedCausalLearner()
                linear=LinearOnlyLearner()
                random_arm=ExpandedCausalLearner()
                active_session=world.training_session()
                random_session=world.training_session()
                rng=Random(int.from_bytes(sha256(
                    f"WSP62|random-trajectory|{seed}".encode("ascii")
                ).digest(),"big"))
                wall_begin=time.perf_counter()
                cpu_begin=time.process_time()
                active_select_time=0.0
                for _ in range(80):
                    before_time=time.perf_counter()
                    action=base.select_action()
                    active_select_time +=time.perf_counter()-before_time
                    chosen_random=rng.choice(ACTIONS)
                    physical=active_session.step(action)
                    random_physical=random_session.step(chosen_random)
                    base.observe(physical)
                    adaptive.observe(physical)
                    linear.observe(physical)
                    random_arm.observe(random_physical)
                    self.assertEqual(base.state,adaptive.state)
                    self.assertEqual(base.state,linear.state)
                    self.assertEqual(base.state,active_session.state)
                    self.assertEqual(random_arm.state,random_session.state)
                self.assertEqual(len(base.ledger),80)
                self.assertEqual(base.ledger,adaptive.ledger)
                self.assertEqual(base.ledger,linear.ledger)
                self.assertEqual(len(random_arm.ledger),80)
                self.assertTrue(all(base.ledger[i][2] == base.ledger[i+1][0]
                                    for i in range(79)))
                self.assertTrue(all(random_arm.ledger[i][2]==random_arm.ledger[i+1][0]
                                    for i in range(79)))
                self.assertEqual(base.ledger[0][0],INITIAL)
                self.assertEqual(random_arm.ledger[0][0],INITIAL)
                snap=adaptive.snapshot()
                restored=ExpandedCausalLearner.restore(snap)
                self.assertEqual(restored.snapshot(),snap)
                with self.assertRaises(ValueError):
                    ExpandedCausalLearner.restore(snap.replace(
                        "wsp62.expanded-anf.v1","wsp62.expanded-anf.v2"))
                for before in STATES:
                    for action in ACTIONS:
                        self.assertEqual(restored.predict(before,action),
                                         adaptive.predict(before,action))
                tasks=world.tasks()
                active_score=score(adaptive,world,tasks)
                random_score=score(random_arm,world,tasks)
                baseline_score=score(base,world,tasks)
                lookup_score=score(base,world,tasks,memory_only=True)
                linear_score=score(linear,world,tasks)
                self.assertEqual(score(restored,world,tasks),active_score)
                audit_active=audit(adaptive,world)
                audit_random=audit(random_arm,world)
                audit_fixed=audit(base,world)
                audit_linear=audit(linear,world)
                expansions=adaptive.expansions()
                known_pairs=len({(b,a) for b,a,y in adaptive.ledger})
                self.assertEqual(known_pairs+audit_active["unobserved_correct"]
                                 +audit_active["unobserved_wrong"]
                                 +audit_active["unobserved_abstain"],64)
                self.assertEqual(adaptive.gradient_updates,0)
                self.assertLessEqual(adaptive.capacity_bits(),300000*8)
                overall["tasks"] += 32
                overall["active"] += active_score["success"]
                overall["random"] += random_score["success"]
                overall["fixed_parent"] += baseline_score["success"]
                overall["lookup"] += lookup_score["success"]
                overall["linear_only"] += linear_score["success"]
                overall["active_wrong"] += audit_active["wrong_confident"]
                overall["active_unobserved_correct"] += audit_active["unobserved_correct"]
                overall["active_unobserved_wrong"] += audit_active["unobserved_wrong"]
                overall["active_unobserved_abstain"] += audit_active["unobserved_abstain"]
                if world.family == "xor_conjunction":
                    overall["expansions"] += len(expansions)
                family_row=by_family.setdefault(world.family,{
                    "worlds":0,"active":0,"random":0,"fixed_parent":0,"lookup":0,
                    "linear":0,"promotions":0
                })
                family_row["worlds"]+=1
                family_row["active"]+=active_score["success"]
                family_row["random"]+=random_score["success"]
                family_row["fixed_parent"]+=baseline_score["success"]
                family_row["lookup"]+=lookup_score["success"]
                family_row["linear"]+=linear_score["success"]
                family_row["promotions"]+=len(expansions)
                results.append({
                    "seed":seed,"family":world.family,"source":world.receipt(),
                    "training_action_ledger_sha256":digest(base.ledger),
                    "random_action_ledger_sha256":digest(random_arm.ledger),
                    "active_action_count":80,"random_action_count":80,
                    "active_visited":len(base.state_visits),
                    "random_visited":len(random_arm.state_visits),
                    "active_observed_pairs":known_pairs,
                    "active":active_score,"random":random_score,
                    "fixed_parent":baseline_score,"lookup":lookup_score,
                    "linear_only":linear_score,
                    "audit_adaptive":audit_active,
                    "audit_fixed_parent":audit_fixed,
                    "audit_random":audit_random,
                    "audit_linear_only":audit_linear,
                    "expansions":[list(x) for x in expansions],
                    "rank_receipts":adaptive.rank_receipts(),
                    "identified_coefficient_dimensions":adaptive.committed_numeric_weights(),
                    "snapshot_bits":adaptive.capacity_bits(),
                    "active_selection_wall_seconds":round(active_select_time,6),
                    "experiment_wall_seconds":round(time.perf_counter()-wall_begin,6),
                    "experiment_cpu_seconds":round(time.process_time()-cpu_begin,6)
                })
        self.assertEqual(overall["tasks"],384)
        classification=(
            "SELFTEST_SIGNAL" if
            overall["active"]>=300 and
            overall["active"]-overall["fixed_parent"]>=50 and
            overall["active_unobserved_correct"]>=25 and
            overall["active_wrong"]==0 and
            overall["expansions"]>=4
            else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE"
        )
        print("WSP62_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":classification,
            "overall":overall,
            "by_family":by_family,
            "fixtures":results
        },sort_keys=True,separators=(",",":")))
        self.assertEqual(len(results),12)
        self.assertEqual(sum(v["worlds"] for v in by_family.values()),12)
        self.assertEqual(sum(x["active_action_count"] for x in results),960)
        # The selftest outcome is scientific DEVELOPMENT evidence, not a
        # Python test assertion; frozen negative results are not hidden.


if __name__ == "__main__":
    unittest.main()

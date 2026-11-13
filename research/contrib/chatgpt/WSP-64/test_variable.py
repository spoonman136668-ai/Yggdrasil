"""Frozen WSP64 SELFTEST: variable sensors, coupled effects, hidden-mode negative.

The evaluator alone imports source.py. The learners receive only charged
physical transitions from stateful no-reset sessions. The 3-bit and 5-bit
worlds use independent heldout source-reachable start/goal tasks; the four
hidden-mode worlds are audited under both unobserved hidden modes.
"""
from __future__ import annotations
from collections import deque
from hashlib import sha256
from pathlib import Path
from random import Random
import json
import time
import unittest

from source import SEEDS,ACTIONS,Experience,build_world
from learner import SparseWorldLearner,_terms,_sparse_candidates
from independent_tree import IndependentTreeControl


def _hash(x):
    return sha256(json.dumps(x,sort_keys=True,
                 separators=(",",":")).encode("ascii")).hexdigest()


def audit_markov(learner,world,tree=None):
    known={(b,a) for b,a,after in learner.ledger}
    stats={"correct":0,"wrong_confident":0,"abstain":0,
           "unseen_correct":0,"unseen_wrong":0,"unseen_abstain":0,
           "unseen_total":0,"tree_correct":0,"tree_wrong":0}
    for state in world.states:
        for action in ACTIONS:
            truth,_=world._step_oracle(state,action)
            pred=learner.predict(state,action)
            unseen=(state,action) not in known
            if unseen: stats["unseen_total"]+=1
            if pred is None:
                stats["abstain"]+=1
                if unseen: stats["unseen_abstain"]+=1
            elif pred==truth:
                stats["correct"]+=1
                if unseen: stats["unseen_correct"]+=1
            else:
                stats["wrong_confident"]+=1
                if unseen: stats["unseen_wrong"]+=1
            if tree is not None:
                t=tree.predict(state,action)
                if t is not None:
                    stats["tree_correct" if t==truth else "tree_wrong"]+=1
    assert stats["correct"]+stats["wrong_confident"]+stats["abstain"]==(
        len(world.states)*len(ACTIONS))
    assert stats["unseen_correct"]+stats["unseen_wrong"]+stats["unseen_abstain"]==stats["unseen_total"]
    return stats


def audit_latent(learner,world):
    stats={"correct":0,"wrong_confident":0,"abstain":0,"truth_conflicts":0}
    for state in world.states:
        for action in ACTIONS:
            outputs={world._step_oracle(state,action,mode=mode)[0]
                     for mode in (0,1)}
            if len(outputs)>1: stats["truth_conflicts"]+=1
            for mode in (0,1):
                truth,_=world._step_oracle(state,action,mode)
                pred=learner.predict(state,action)
                if pred is None: stats["abstain"]+=1
                elif pred==truth: stats["correct"]+=1
                else: stats["wrong_confident"]+=1
    assert sum(stats[k] for k in ("correct","wrong_confident","abstain"))==128
    assert stats["truth_conflicts"]>0
    return stats


def plan_via(predict,start,target,limit=6):
    if start==target: return ()
    queue=deque([(start,())])
    seen={start}
    while queue:
        state,trace=queue.popleft()
        if len(trace)>=limit: continue
        for action in ACTIONS:
            nxt=predict(state,action)
            if nxt is None: continue
            path=trace+(action,)
            if nxt==target: return path
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt,path))
    return None


def task_success(predict,world,tasks):
    win=abstain=0
    for task in tasks:
        proposed=plan_via(predict,task.start,task.target)
        if proposed is None:
            abstain+=1
        elif world.evaluate(task,proposed):
            win+=1
    return {"success":win,"abstain":abstain,"total":len(tasks)}


class FrozenVariableDimensionResearch(unittest.TestCase):
    def test_scope_source_safety_and_custody(self):
        src=(Path(__file__).parent/"learner.py").read_text("utf-8")
        self.assertNotIn("from source import",src)
        self.assertNotIn("import source",src)
        self.assertEqual(SparseWorldLearner.gradient_updates,0)
        self.assertEqual(len(_terms(3)),7)
        self.assertEqual(len(_terms(5)),16)
        self.assertEqual(len(_sparse_candidates(5)),697)
        for cohort in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(3001,cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(2901)
        for seed in SEEDS:
            w=build_world(seed)
            self.assertEqual(w.receipt(),build_world(seed).receipt())
            self.assertEqual(w.budget,64 if seed>=3009 else 48)
            if seed<=3008:
                self.assertEqual(len(w.tasks()),32)
        w=build_world(3001)
        learner=SparseWorldLearner()
        action=w.training_session().step(0)
        with self.assertRaises(ValueError):
            learner.observe(Experience((1,1,1),action.action,action.after))
        self.assertEqual(len(learner.ledger),0)
        learner.observe(action)
        with self.assertRaises(ValueError):
            learner.observe(Experience((1,1,1),action.action,action.after))
        with self.assertRaises(ValueError):
            learner.observe(Experience(learner.state,4,learner.state))

    def test_twelve_fresh_variable_and_hidden_worlds(self):
        records=[]
        overall={"markov_tasks":0,"markov_active":0,
                 "markov_memory":0,"markov_tree":0,"markov_random":0,
                 "markov_unseen_correct":0,"markov_unseen_wrong":0,
                 "markov_wrong":0,"markov_unseen_total":0,
                 "latent_worlds_with_observed_conflict":0,
                 "latent_wrong":0,"latent_conflicts":0,
                 "latent_correct":0,"latent_abstain":0}
        family={}
        for seed in SEEDS:
            with self.subTest(seed=seed):
                world=build_world(seed)
                active=SparseWorldLearner()
                random_arm=SparseWorldLearner()
                live=world.training_session()
                random_live=world.training_session()
                rng=Random(int.from_bytes(sha256(
                    f"WSP64|independent-random-actions|{seed}".encode("ascii")
                ).digest(),"big"))
                started=time.perf_counter()
                cpu_started=time.process_time()
                policy_time=0.0
                for _ in range(world.budget):
                    tick=time.perf_counter()
                    chosen=active.select_action()
                    policy_time+=time.perf_counter()-tick
                    other=rng.choice(ACTIONS)
                    active.observe(live.step(chosen))
                    random_arm.observe(random_live.step(other))
                    self.assertEqual(active.state,live.state)
                    self.assertEqual(random_arm.state,random_live.state)
                self.assertEqual(len(active.ledger),world.budget)
                self.assertEqual(len(random_arm.ledger),world.budget)
                self.assertEqual(active.dimension,world.bits)
                self.assertEqual(random_arm.dimension,world.bits)
                self.assertTrue(all(active.ledger[i][2]==active.ledger[i+1][0]
                                    for i in range(world.budget-1)))
                self.assertTrue(all(random_arm.ledger[i][2]==random_arm.ledger[i+1][0]
                                    for i in range(world.budget-1)))
                self.assertEqual(active.gradient_updates,0)
                frozen=active.snapshot()
                cold=SparseWorldLearner.restore(frozen)
                self.assertEqual(cold.snapshot(),frozen)
                with self.assertRaises(ValueError):
                    SparseWorldLearner.restore(frozen.replace(
                        "wsp64.sparse-variable-state.v1",
                        "wsp64.sparse-variable-state.v2"))
                for state in world.states:
                    for action in ACTIONS:
                        self.assertEqual(active.predict(state,action),
                                         cold.predict(state,action))
                contradictions=active.contradictory_pairs()
                trees=IndependentTreeControl(active.ledger,world.bits)
                fixture={"seed":seed,"family":world.family,"bits":world.bits,
                    "source":world.receipt(),"active_charges":len(active.ledger),
                    "random_charges":len(random_arm.ledger),
                    "active_ledger_sha256":_hash(active.ledger),
                    "random_ledger_sha256":_hash(random_arm.ledger),
                    "active_visited_states":len(active.state_visits),
                    "random_visited_states":len(random_arm.state_visits),
                    "active_observed_pairs":len({(b,a) for b,a,y in active.ledger}),
                    "contradictory_observed_pairs":len(contradictions),
                    "contradictory_action_channels":active.inconsistent_channels(),
                    "hypothesis_multiplicity":active.hypothesis_counts(),
                    "sparse_candidate_count":len(_sparse_candidates(world.bits)),
                    "snapshot_bits":active.capacity_bits(),
                    "policy_wall_seconds":round(policy_time,6)}
                if world.family=="latent":
                    safety=audit_latent(active,world)
                    self.assertEqual(audit_latent(cold,world),safety)
                    overall["latent_worlds_with_observed_conflict"]+=int(bool(contradictions))
                    overall["latent_wrong"]+=safety["wrong_confident"]
                    overall["latent_correct"]+=safety["correct"]
                    overall["latent_abstain"]+=safety["abstain"]
                    overall["latent_conflicts"]+=safety["truth_conflicts"]
                    fixture["latent_two_mode_audit"]=safety
                else:
                    tasks=world.tasks()
                    original=task_success(active.predict,world,tasks)
                    same_memory=task_success(
                        lambda b,a:active.predict(b,a,memory_only=True),world,tasks)
                    control=task_success(random_arm.predict,world,tasks)
                    tree=task_success(trees.predict,world,tasks)
                    self.assertEqual(task_success(cold.predict,world,tasks),original)
                    safety=audit_markov(active,world,tree=trees)
                    overall["markov_tasks"]+=len(tasks)
                    overall["markov_active"]+=original["success"]
                    overall["markov_memory"]+=same_memory["success"]
                    overall["markov_tree"]+=tree["success"]
                    overall["markov_random"]+=control["success"]
                    overall["markov_unseen_correct"]+=safety["unseen_correct"]
                    overall["markov_unseen_wrong"]+=safety["unseen_wrong"]
                    overall["markov_unseen_total"]+=safety["unseen_total"]
                    overall["markov_wrong"]+=safety["wrong_confident"]
                    fixture["active_goals"]=original
                    fixture["exact_memory_goals"]=same_memory
                    fixture["tree_goals"]=tree
                    fixture["random_goals"]=control
                    fixture["physical_audit"]=safety
                    fixture["random_physical_audit"]=audit_markov(random_arm,world)
                    counts=family.setdefault(world.family,{
                        "worlds":0,"active":0,"lookup":0,"tree":0,"random":0,
                        "unseen_correct":0,"wrong":0})
                    counts["worlds"]+=1
                    counts["active"]+=original["success"]
                    counts["lookup"]+=same_memory["success"]
                    counts["tree"]+=tree["success"]
                    counts["random"]+=control["success"]
                    counts["unseen_correct"]+=safety["unseen_correct"]
                    counts["wrong"]+=safety["wrong_confident"]
                fixture["world_wall_seconds"]=round(time.perf_counter()-started,6)
                fixture["world_cpu_seconds"]=round(time.process_time()-cpu_started,6)
                records.append(fixture)
        self.assertEqual(len(records),12)
        self.assertEqual(overall["markov_tasks"],256)
        self.assertEqual(sum(f["active_charges"] for f in records),8*48+4*64)
        gates={
            ">=160_markov_tasks":overall["markov_active"]>=160,
            ">=20_more_goals_than_memory":
                overall["markov_active"]-overall["markov_memory"]>=20,
            ">=70_unobserved_predictions":overall["markov_unseen_correct"]>=70,
            "zero_markov_wrong":overall["markov_wrong"]==0,
            ">=3_latent_worlds_with_observed_conflicts":
                overall["latent_worlds_with_observed_conflict"]>=3,
            "zero_wrong_across_both_hidden_modes":overall["latent_wrong"]==0
        }
        classification=("SELFTEST_SIGNAL" if all(gates.values())
                        else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP64_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":classification,"criteria":gates,
            "overall":overall,"by_markov_family":family,"fixtures":records
        },sort_keys=True,separators=(",",":")))
        # Negative experiments are preserved, not assertions to be repaired.


if __name__=="__main__":
    unittest.main()

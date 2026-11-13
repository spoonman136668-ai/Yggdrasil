"""WSP63 frozen experimental qualification, source-only SELFTEST.

A copied frozen WSP61 action-policy learner supplies the *same* 48
chronological no-reset experiences to the WSP61, WSP62, WSP63 and exact
lookup controls; a separate 48-action random history tests action policy.
Only the evaluator module imports hidden physics and computes heldout truth.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from random import Random
import inspect
import json
import time
import unittest

from source import SEEDS,STATES,CHANNELS,TRAIN_ACTIONS,build_world
# Import compressed learner first; it exposes the pinned unchanged WSP61/WSP62
# modules for the exact-ledger controls (no evaluator imports in model).
from compressed_effect import CompressedEffectLearner,trigger_features,TERMS
from learner import ReachableCausalLearner
from expanded_learner import ExpandedCausalLearner


def digest(ledger):
    return sha256(json.dumps(ledger,sort_keys=True,
                 separators=(",",":")).encode("ascii")).hexdigest()


def audit(model,world,seen):
    x={"correct":0,"wrong_confident":0,"abstain":0,
       "unseen_correct":0,"unseen_wrong":0,"unseen_abstain":0,
       "unseen_total":0}
    for state in STATES:
        for action in CHANNELS:
            prediction=model.predict(state,action)
            truth=world._step_oracle(state,action)  # evaluator-only truth
            unseen=(state,action) not in seen
            if unseen: x["unseen_total"]+=1
            if prediction is None:
                x["abstain"]+=1
                if unseen: x["unseen_abstain"]+=1
            elif prediction==truth:
                x["correct"]+=1
                if unseen: x["unseen_correct"]+=1
            else:
                x["wrong_confident"]+=1
                if unseen: x["unseen_wrong"]+=1
    assert x["correct"]+x["wrong_confident"]+x["abstain"]==64
    assert x["unseen_correct"]+x["unseen_wrong"]+x["unseen_abstain"]==x["unseen_total"]
    return x


def goals(model,world,tasks,memory_only=False):
    results={"success":0,"abstain":0,"total":len(tasks)}
    for task in tasks:
        plan=model.plan(task.start,task.target,memory_only=memory_only)
        if plan is None:
            results["abstain"]+=1
        elif world.evaluate(task,plan):
            results["success"]+=1
    return results


class FrozenSparseExtrapolation(unittest.TestCase):
    def test_source_isolation_and_guardrails(self):
        code=(Path(__file__).parent/"compressed_effect.py").read_text("utf-8")
        self.assertNotIn("import source",code)
        self.assertNotIn("from source import",code)
        self.assertEqual(CompressedEffectLearner.gradient_updates,0)
        self.assertEqual(list(inspect.signature(CompressedEffectLearner.predict).parameters),
                         ["self","before","action","memory_only"])
        self.assertEqual(len(TERMS),7)
        self.assertEqual(trigger_features((0,0,0,0),(0,1,2)),1)
        for cohort in ("PRIMARY","DEV"):
            with self.assertRaises(PermissionError):
                build_world(2901,cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(2801)
        source=build_world(2901)
        self.assertEqual(source.receipt(),build_world(2901).receipt())
        self.assertEqual(len(source.tasks()),32)
        learner=CompressedEffectLearner()
        session=source.training_session()
        step=session.step(0)
        with self.assertRaises(ValueError):
            from source import Experience
            learner.observe(Experience((1,1,1,1),0,step.after))
        self.assertEqual(learner.ledger,[])

    def test_frozen_twelve_worlds_and_controls(self):
        by_family={}
        rows=[]
        totals={
            "infamily_tasks":0, "infamily_compressed":0,
            "infamily_lookup":0, "infamily_wsp62":0,
            "infamily_wsp61":0, "infamily_random":0,
            "infamily_unseen_correct":0, "infamily_wrong":0,
            "cubic_tasks":0, "cubic_compressed":0,
            "cubic_lookup":0, "cubic_wsp62":0, "cubic_wrong":0,
            "all_wrong":0, "all_unseen_correct":0,
            "all_unseen_audit_total":0
        }
        for seed in SEEDS:
            with self.subTest(seed=seed):
                world=build_world(seed)
                self.assertEqual(world.receipt(),build_world(seed).receipt())
                policy=ReachableCausalLearner()
                compressed=CompressedEffectLearner()
                old=ExpandedCausalLearner()
                random_arm=CompressedEffectLearner()
                oldparent=ReachableCausalLearner()
                live=world.training_session()
                live_random=world.training_session()
                rng=Random(int.from_bytes(sha256(
                    f"WSP63|random-policy|{seed}".encode("ascii")
                ).digest(),"big"))
                wall=time.perf_counter()
                cpu=time.process_time()
                selection=0.0
                for _ in range(TRAIN_ACTIONS):
                    t=time.perf_counter()
                    action=policy.select_action()
                    selection+=time.perf_counter()-t
                    other=rng.choice(CHANNELS)
                    charged=live.step(action)
                    charged_r=live_random.step(other)
                    for learner in (policy,compressed,old,oldparent):
                        learner.observe(charged)
                    random_arm.observe(charged_r)
                    self.assertEqual(compressed.state,live.state)
                    self.assertEqual(random_arm.state,live_random.state)
                self.assertEqual(len(compressed.ledger),TRAIN_ACTIONS)
                self.assertEqual(len(random_arm.ledger),TRAIN_ACTIONS)
                self.assertEqual(compressed.ledger,old.ledger)
                self.assertEqual(compressed.ledger,oldparent.ledger)
                self.assertEqual(compressed.ledger,policy.ledger)
                self.assertEqual(compressed.ledger[0][0],(0,0,0,0))
                self.assertTrue(all(compressed.ledger[j][2]==compressed.ledger[j+1][0]
                                    for j in range(TRAIN_ACTIONS-1)))
                self.assertTrue(all(random_arm.ledger[j][2]==random_arm.ledger[j+1][0]
                                    for j in range(TRAIN_ACTIONS-1)))
                self.assertEqual(compressed.gradient_updates,0)
                public_seen={(b,a) for b,a,y in compressed.ledger}
                snapshot=compressed.snapshot()
                cold=CompressedEffectLearner.restore(snapshot)
                self.assertEqual(cold.snapshot(),snapshot)
                for state in STATES:
                    for action in CHANNELS:
                        self.assertEqual(cold.predict(state,action),
                                         compressed.predict(state,action))
                with self.assertRaises(ValueError):
                    CompressedEffectLearner.restore(snapshot.replace(
                        "wsp63.compressed-effect.v1",
                        "wsp63.compressed-effect.v2"))
                tasks=world.tasks()
                outcome=goals(compressed,world,tasks)
                memory=goals(compressed,world,tasks,memory_only=True)
                oldout=goals(old,world,tasks)
                parentout=goals(oldparent,world,tasks)
                randout=goals(random_arm,world,tasks)
                self.assertEqual(goals(cold,world,tasks),outcome)
                a=audit(compressed,world,public_seen)
                oa=audit(old,world,public_seen)
                pa=audit(oldparent,world,public_seen)
                ra=audit(random_arm,world,
                         {(b,x) for b,x,y in random_arm.ledger})
                self.assertEqual(a["wrong_confident"],a["unseen_wrong"]+
                                 # Trained observations must always be reconstructed correctly.
                                 0)
                self.assertLessEqual(compressed.capacity_bits(),300000*8)
                target="cubic" if world.family=="cubic_negative" else "infamily"
                totals[target+"_tasks"]+=32
                totals[target+"_compressed"]+=outcome["success"]
                totals[target+"_lookup"]+=memory["success"]
                totals[target+"_wsp62"]+=oldout["success"]
                totals[target+"_wrong"]+=a["wrong_confident"]
                if target=="infamily":
                    totals["infamily_wsp61"]+=parentout["success"]
                    totals["infamily_random"]+=randout["success"]
                    totals["infamily_unseen_correct"]+=a["unseen_correct"]
                totals["all_wrong"]+=a["wrong_confident"]
                totals["all_unseen_correct"]+=a["unseen_correct"]
                totals["all_unseen_audit_total"]+=a["unseen_total"]
                bucket=by_family.setdefault(world.family,{
                    "worlds":0,"compressed":0,"lookup":0,"wsp62":0,
                    "wsp61":0,"random":0,"unseen_correct":0,
                    "unseen_wrong":0,"wrong_confident":0
                })
                bucket["worlds"]+=1
                bucket["compressed"]+=outcome["success"]
                bucket["lookup"]+=memory["success"]
                bucket["wsp62"]+=oldout["success"]
                bucket["wsp61"]+=parentout["success"]
                bucket["random"]+=randout["success"]
                bucket["unseen_correct"]+=a["unseen_correct"]
                bucket["unseen_wrong"]+=a["unseen_wrong"]
                bucket["wrong_confident"]+=a["wrong_confident"]
                rows.append({
                    "seed":seed,"family":world.family,"source":world.receipt(),
                    "charged_actions":len(compressed.ledger),
                    "charged_random_actions":len(random_arm.ledger),
                    "seen_state_action_pairs":len(public_seen),
                    "seen_random_pairs":len({(b,x) for b,x,y in random_arm.ledger}),
                    "active_sha256":digest(compressed.ledger),
                    "random_sha256":digest(random_arm.ledger),
                    "compressed":outcome,"lookup":memory,
                    "wsp62":oldout,"wsp61":parentout,"random":randout,
                    "source_audit":a,"wsp62_audit":oa,
                    "wsp61_audit":pa,"random_audit":ra,
                    "learned_action_ranks":compressed.rank_receipts(),
                    "identified_coefficients":compressed.identified_numeric_dimensions(),
                    "snapshot_bits":compressed.capacity_bits(),
                    "active_selection_wall":round(selection,6),
                    "whole_world_wall":round(time.perf_counter()-wall,6),
                    "whole_world_cpu":round(time.process_time()-cpu,6)
                })
        self.assertEqual(len(rows),12)
        self.assertEqual(totals["infamily_tasks"],256)
        self.assertEqual(totals["cubic_tasks"],128)
        self.assertEqual(sum(x["charged_actions"] for x in rows),576)
        criterion={
            "in_family_goal_min_180":totals["infamily_compressed"]>=180,
            "in_family_lookup_advantage_min_20":
                totals["infamily_compressed"]-totals["infamily_lookup"]>=20,
            "unobserved_correct_min_35":totals["infamily_unseen_correct"]>=35,
            "in_family_zero_wrong":totals["infamily_wrong"]==0,
            "cubic_negative_zero_wrong":totals["cubic_wrong"]==0
        }
        classification=("SELFTEST_SIGNAL" if all(criterion.values())
                        else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP63_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":classification,"criterion":criterion,
            "totals":totals,"by_family":by_family,"fixtures":rows
        },sort_keys=True,separators=(",",":")))
        # The frozen criterion is not used as a Python assertion. A negative
        # outcome remains recorded and cannot justify post-hoc tuning.


if __name__=="__main__":
    unittest.main()

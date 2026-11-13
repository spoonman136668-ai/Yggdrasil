"""WSP69 prospective SELFTEST: experience-selected neural hidden weights.

Frozen before source/model/tests in prereg. All arms see the same 96
physically charged no-reset public source experiences; exemplar selection
depends only on trained prediction residuals on those rows. New hidden
neurons and readout matrices are executable neural weights, not compiled
physics rules. Independent end-to-end neural controls use backpropagation.
All withheld outcomes are scored only by evaluator AFTER learning.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from random import Random
import sys
import time
import json
import unittest

from source import SEEDS,STATES,ACTIONS,STAGE_A,TRAIN_ACTIONS,build_world
from growing_neural import (
    FeatureGrowthNeural,prototype_neuron,inputs,
    BASE_NEURONS,NEW_PER_PHASE,FIXED_SEED,MARGIN,MAX_LEVERAGE
)
from end_to_end_control import EndToEndAdamControl

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"WSP-67"))
from independent_symbolic import ExactMemory
sys.path.insert(0,str(ROOT/"WSP-64"))
from independent_tree import IndependentTreeControl


def hash_json(v):
    return sha256(json.dumps(v,sort_keys=True,
                  separators=(",",":")).encode("ascii")).hexdigest()


def scoring(predict,world,seen,compositions=None):
    tally={"correct":0,"wrong_confident":0,"abstain":0}
    unseen={"correct":0,"wrong_confident":0,"abstain":0,"total":0}
    for s in STATES:
        for action in ACTIONS:
            guess=predict(s,action)
            truth=world._step_oracle(s,action)
            group=("abstain" if guess is None else
                   "correct" if guess==truth else "wrong_confident")
            tally[group]+=1
            if (s,action) not in seen:
                unseen[group]+=1
                unseen["total"]+=1
    assert sum(tally.values())==64
    assert sum(v for k,v in unseen.items() if k!="total")==unseen["total"]
    result={"physical":tally,"unseen":unseen}
    if compositions is not None:
        composite={"correct":0,"wrong_confident":0,"abstain":0}
        for case in compositions:
            x,y=case.actions
            first=predict(case.start,x)
            second=predict(first,y) if first is not None else None
            group=("abstain" if second is None else
                   "correct" if second==case._finish else "wrong_confident")
            composite[group]+=1
        assert sum(composite.values())==len(compositions)
        result["compositions"]=composite
    return result


def score_with_cpu(model,world,seen,compositions):
    start=time.process_time_ns()
    result=scoring(model.predict,world,seen,compositions)
    elapsed=time.process_time_ns()-start
    return result,elapsed


class FrozenSourceBlindHiddenFeatureGrowth(unittest.TestCase):
    def test_source_separation_and_neural_prototypes(self):
        for filename in ("growing_neural.py","end_to_end_control.py"):
            content=(Path(__file__).parent/filename).read_text("utf-8")
            for forbidden in ("from source import","import source",
                              "from weight_programmer import",
                              "from independent_symbolic import"):
                self.assertNotIn(forbidden,content)
        self.assertEqual(FIXED_SEED,68182026)
        self.assertEqual(MARGIN,0.27)
        self.assertEqual(MAX_LEVERAGE,2.0)
        self.assertEqual(BASE_NEURONS,32)
        self.assertEqual(NEW_PER_PHASE,12)
        self.assertEqual(FeatureGrowthNeural.gradient_steps,0)
        center=(1,0,1,0)
        a=2
        w,b=prototype_neuron(center,a)
        def hidden(s,action):
            v=inputs(s,action)
            return max(0.,sum(i*j for i,j in zip(w,v))+b)
        self.assertEqual(hidden(center,a),1.0)
        self.assertEqual(hidden((0,0,1,0),a),0.5)
        self.assertEqual(hidden(center,3),0.0)
        self.assertEqual(hidden((1,1,1,1),a),0.0)
        for cohort in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(4301,cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(4201)
        for seed in SEEDS:
            world=build_world(seed)
            self.assertEqual(world.receipt(),build_world(seed).receipt())
            self.assertEqual(len(world.composition_tests()),32)
        model=FeatureGrowthNeural()
        row=build_world(4301).training_session().step(0)
        with self.assertRaises(ValueError):
            from source import Experience
            model.charge(Experience((1,1,1,1),0,row.after))
        with self.assertRaises(ValueError):
            model.charge(Experience((0,0,0,0),0,row.after,0))
        self.assertEqual(len(model.ledger),0)
        model.charge(row)
        with self.assertRaises(ValueError):
            model.grow()
        self.assertEqual(model.charged_actions,1)

    def test_frozen_12_world_neural_growth_and_qualified_controls(self):
        overall={"worlds":0,"training_actions":0,
                 "physical_tests":0,"composite_tests":0,
                 "adaptive_confident_correct":0,"adaptive_confident_wrong":0,
                 "adaptive_abstained":0,"adaptive_unseen_correct":0,
                 "adaptive_unseen_wrong":0,"adaptive_unseen_total":0,
                 "adaptive_composites_correct":0,"adaptive_composites_wrong":0,
                 "random_confident_correct":0,"random_confident_wrong":0,
                 "random_unseen_correct":0,"random_unseen_wrong":0,
                 "random_composites_correct":0,
                 "fixed_confident_correct":0,"fixed_unseen_correct":0,
                 "memory_correct":0,"memory_composites_correct":0,
                 "tree_correct":0,"tree_wrong":0,
                 "tree_composites_correct":0,
                 "gradient_forced_correct":0,"gradient_forced_wrong":0,
                 "gradient_confident_correct":0,"gradient_confident_wrong":0,
                 "gradient_composites_correct":0,
                 "gradient_baseline_converged_worlds":0,
                 "gradient_updates":0,
                 "stageA_eligible_correct":0,"stageB_retained_correct":0,
                 "hidden_features_added_worlds":0,"readout_edited_worlds":0,
                 "cold_restored_worlds":0,"adaptive_cpu_ns":0,
                 "random_cpu_ns":0,"gradient_training_cpu_ns":0}
        family={}
        worlds=[]
        for seed in SEEDS:
            with self.subTest(seed=seed):
                world=build_world(seed)
                session=world.training_session()
                policy_rng=Random(int.from_bytes(sha256(
                    f"WSP69|charged-random-action|{seed}".encode("ascii")
                ).digest(),"big"))
                adaptive=FeatureGrowthNeural(policy="residual",seed=seed)
                random_bank=FeatureGrowthNeural(policy="random",seed=seed)
                # Original fixed-neuron WSP68 still uses identical 32 ReLUs,
                # skip and λ=0.5, no adaptive prototypes.
                fixed=FeatureGrowthNeural(policy="random",seed=seed)
                charged=[]
                a_cpu=r_cpu=0
                for i in range(TRAIN_ACTIONS):
                    physical=session.step(policy_rng.choice(ACTIONS))
                    charged.append((physical.before,physical.action,physical.after))
                    start=time.process_time_ns()
                    adaptive.charge(physical)
                    a_cpu+=time.process_time_ns()-start
                    start=time.process_time_ns()
                    random_bank.charge(physical)
                    r_cpu+=time.process_time_ns()-start
                    fixed.charge(physical)
                    if i+1 in (STAGE_A,TRAIN_ACTIONS):
                        start=time.process_time_ns()
                        adaptive.grow()
                        a_cpu+=time.process_time_ns()-start
                        start=time.process_time_ns()
                        random_bank.grow()
                        r_cpu+=time.process_time_ns()-start
                        if i+1==STAGE_A:
                            stage_a=FeatureGrowthNeural.restore(adaptive.snapshot())
                            stage_a_snapshot=adaptive.snapshot()
                            random_stage_a=FeatureGrowthNeural.restore(
                                random_bank.snapshot())
                        else:
                            stage_b=FeatureGrowthNeural.restore(adaptive.snapshot())
                            random_stage_b=FeatureGrowthNeural.restore(
                                random_bank.snapshot())
                self.assertEqual(len(charged),TRAIN_ACTIONS)
                self.assertEqual(session.ledger[0].before,(0,0,0,0))
                self.assertTrue(all(charged[i][2]==charged[i+1][0]
                                    for i in range(TRAIN_ACTIONS-1)))
                self.assertEqual(adaptive.charged_actions,96)
                self.assertEqual(random_bank.charged_actions,96)
                self.assertEqual(fixed.charged_actions,96)
                self.assertEqual(len(adaptive.centers),len(random_bank.centers))
                self.assertEqual(len(adaptive.hidden_weights),
                                 len(random_bank.hidden_weights))
                self.assertTrue(len(adaptive.centers)>0)
                self.assertEqual(adaptive.growth_rounds,2)
                self.assertEqual(random_bank.growth_rounds,2)
                self.assertEqual(fixed.growth_rounds,0)
                self.assertEqual(fixed.hidden_weights[:32],
                                 adaptive.hidden_weights[:32])
                for raw,snapshot in ((stage_a_snapshot,stage_a),
                                     (adaptive.snapshot(),stage_b),
                                     (random_bank.snapshot(),random_stage_b)):
                    self.assertEqual(FeatureGrowthNeural.restore(raw).snapshot(),
                                     raw)
                    self.assertNotIn('"ledger"',raw)
                    self.assertNotIn('"centers"',raw)
                    with self.assertRaises(ValueError):
                        FeatureGrowthNeural.restore(raw.replace(
                            "wsp69.neural-feature-growth.v1",
                            "wsp69.neural-feature-growth.v2"))
                for s in STATES:
                    for action in ACTIONS:
                        self.assertEqual(stage_b.raw(s,action),
                                         adaptive.raw(s,action))
                        self.assertEqual(stage_b.predict(s,action),
                                         adaptive.predict(s,action))
                        self.assertEqual(random_stage_b.predict(s,action),
                                         random_bank.predict(s,action))
                erased=FeatureGrowthNeural.restore(adaptive.snapshot())
                erased.w_readout=[[0.0]*len(row)
                                  for row in erased.w_readout]
                self.assertTrue(any(
                    erased.raw(s,a)!=stage_b.raw(s,a)
                    for s in STATES for a in ACTIONS))
                seen={(b,a) for b,a,y in charged}
                seenA={(b,a) for b,a,y in charged[:STAGE_A]}
                heldout=world.composition_tests()
                stage_a_test=scoring(stage_a.predict,world,seenA)
                adapt_test,dt=score_with_cpu(stage_b,world,seen,heldout)
                a_cpu+=dt
                random_test,dt=score_with_cpu(random_stage_b,world,seen,heldout)
                r_cpu+=dt
                fixed_test=scoring(fixed.predict,world,seen)
                memory=ExactMemory(charged)
                memory_test=scoring(memory.predict,world,seen,heldout)
                tree=IndependentTreeControl(charged,4)
                tree_test=scoring(tree.predict,world,seen,heldout)
                grad=EndToEndAdamControl(seed)
                start_grad=time.process_time_ns()
                training=grad.fit(charged)
                grad_cpu=time.process_time_ns()-start_grad
                gradient_forced=scoring(grad.predict,world,seen,heldout)
                gradient_confident=scoring(
                    lambda s,a:grad.predict(s,a,confidence=True),world,seen)
                retained=eligible=0
                for s in STATES:
                    for action in ACTIONS:
                        old=stage_a.predict(s,action)
                        truth=world._step_oracle(s,action)
                        if old is not None and old==truth:
                            eligible+=1
                            retained+=int(stage_b.predict(s,action)==truth)
                overall["worlds"]+=1
                overall["training_actions"]+=96
                overall["physical_tests"]+=64
                overall["composite_tests"]+=32
                for prefix,diagnostic in [
                    ("adaptive",adapt_test),("random",random_test)]:
                    overall[f"{prefix}_confident_correct"]+=(
                        diagnostic["physical"]["correct"])
                    overall[f"{prefix}_confident_wrong"]+=(
                        diagnostic["physical"]["wrong_confident"])
                    overall[f"{prefix}_unseen_correct"]+=(
                        diagnostic["unseen"]["correct"])
                    overall[f"{prefix}_unseen_wrong"]+=(
                        diagnostic["unseen"]["wrong_confident"])
                overall["adaptive_abstained"]+=adapt_test["physical"]["abstain"]
                overall["adaptive_unseen_total"]+=adapt_test["unseen"]["total"]
                overall["adaptive_composites_correct"]+=adapt_test["compositions"]["correct"]
                overall["adaptive_composites_wrong"]+=adapt_test["compositions"]["wrong_confident"]
                overall["random_composites_correct"]+=random_test["compositions"]["correct"]
                overall["fixed_confident_correct"]+=fixed_test["physical"]["correct"]
                overall["fixed_unseen_correct"]+=fixed_test["unseen"]["correct"]
                overall["memory_correct"]+=memory_test["physical"]["correct"]
                overall["memory_composites_correct"]+=memory_test["compositions"]["correct"]
                overall["tree_correct"]+=tree_test["physical"]["correct"]
                overall["tree_wrong"]+=tree_test["physical"]["wrong_confident"]
                overall["tree_composites_correct"]+=tree_test["compositions"]["correct"]
                overall["gradient_forced_correct"]+=gradient_forced["physical"]["correct"]
                overall["gradient_forced_wrong"]+=gradient_forced["physical"]["wrong_confident"]
                overall["gradient_confident_correct"]+=gradient_confident["physical"]["correct"]
                overall["gradient_confident_wrong"]+=gradient_confident["physical"]["wrong_confident"]
                overall["gradient_composites_correct"]+=gradient_forced["compositions"]["correct"]
                overall["gradient_baseline_converged_worlds"]+=int(
                    training["fully_trained"])
                overall["gradient_updates"]+=training["gradient_updates_total"]
                overall["stageA_eligible_correct"]+=eligible
                overall["stageB_retained_correct"]+=retained
                overall["hidden_features_added_worlds"]+=int(
                    len(adaptive.hidden_weights)>len(stage_a.hidden_weights))
                overall["readout_edited_worlds"]+=adaptive.changed_readout(stage_a)
                overall["cold_restored_worlds"]+=1
                overall["adaptive_cpu_ns"]+=a_cpu
                overall["random_cpu_ns"]+=r_cpu
                overall["gradient_training_cpu_ns"]+=grad_cpu
                bucket=family.setdefault(world.family,{
                    "worlds":0,"adaptive_correct":0,"random_correct":0,
                    "adaptive_unseen_correct":0,"random_unseen_correct":0,
                    "adaptive_wrong":0,"random_wrong":0,
                    "gradient_converged":0})
                bucket["worlds"]+=1
                bucket["adaptive_correct"]+=adapt_test["physical"]["correct"]
                bucket["random_correct"]+=random_test["physical"]["correct"]
                bucket["adaptive_unseen_correct"]+=adapt_test["unseen"]["correct"]
                bucket["random_unseen_correct"]+=random_test["unseen"]["correct"]
                bucket["adaptive_wrong"]+=adapt_test["physical"]["wrong_confident"]
                bucket["random_wrong"]+=random_test["physical"]["wrong_confident"]
                bucket["gradient_converged"]+=int(training["fully_trained"])
                worlds.append({
                    "seed":seed,"family":world.family,
                    "source":world.receipt(),
                    "charged_action_ledger_sha256":hash_json(charged),
                    "charged_actions":len(charged),
                    "stageA_neural_sha256":sha256(stage_a_snapshot.encode("ascii")).hexdigest(),
                    "stageB_neural_sha256":sha256(adaptive.snapshot().encode("ascii")).hexdigest(),
                    "random_stageB_neural_sha256":sha256(random_bank.snapshot().encode("ascii")).hexdigest(),
                    "grown_neurons_stageA":len(stage_a.hidden_weights)-BASE_NEURONS,
                    "grown_neurons_stageB":len(stage_b.hidden_weights)-BASE_NEURONS,
                    "adaptive_neural_params":stage_b.readout_parameter_count(),
                    "adaptive_snapshot_bytes":stage_b.snapshot_bytes(),
                    "adaptive_vs_random_matched_hidden_width":
                        len(adaptive.hidden_weights)==len(random_bank.hidden_weights),
                    "stageA":stage_a_test,
                    "stageB_adaptive":adapt_test,
                    "stageB_random":random_test,
                    "stageB_fixed":fixed_test,
                    "memory":memory_test,
                    "tree":tree_test,
                    "end_to_end_forced":gradient_forced,
                    "end_to_end_confident":gradient_confident,
                    "end_to_end_train":training,
                    "retention_correct":retained,
                    "retention_eligible":eligible,
                    "adaptive_cpu_ns":a_cpu,
                    "random_cpu_ns":r_cpu,
                    "gradient_train_cpu_ns":grad_cpu
                })
        self.assertEqual(overall["worlds"],12)
        self.assertEqual(overall["training_actions"],12*96)
        self.assertEqual(overall["physical_tests"],768)
        self.assertEqual(overall["composite_tests"],384)
        self.assertEqual(overall["cold_restored_worlds"],12)
        assert all(x["adaptive_vs_random_matched_hidden_width"] for x in worlds)
        retention=(overall["stageB_retained_correct"]/
                   overall["stageA_eligible_correct"]
                   if overall["stageA_eligible_correct"] else 0.0)
        cpu_ratio=overall["adaptive_cpu_ns"]/max(1,overall["random_cpu_ns"])
        gates={
            "unseen_correct_ge_35":overall["adaptive_unseen_correct"]>=35,
            "all_confident_correct_ge_210":
                overall["adaptive_confident_correct"]>=210,
            "beat_exact_memory_by_30":
                overall["adaptive_confident_correct"]-overall["memory_correct"]>=30,
            "beat_width_matched_random_unseen_by_15":
                overall["adaptive_unseen_correct"]-
                overall["random_unseen_correct"]>=15,
            "beat_width_matched_random_all_by_25":
                overall["adaptive_confident_correct"]-
                overall["random_confident_correct"]>=25,
            "no_more_than_5_extra_wrong_vs_random":
                overall["adaptive_confident_wrong"]-
                overall["random_confident_wrong"]<=5,
            "confident_wrong_le_20":
                overall["adaptive_confident_wrong"]<=20,
            "confident_compositions_ge_80":
                overall["adaptive_composites_correct"]>=80,
            "retention_ge_85pct":retention>=0.85,
            "feature_growth_and_readout_edits_10_worlds":
                overall["hidden_features_added_worlds"]>=10 and
                overall["readout_edited_worlds"]>=10,
            "all_12_cold_matrix_restore_and_tamper":
                overall["cold_restored_worlds"]==12,
            "direct_cpu_no_more_3x_random":cpu_ratio<=3.0
        }
        classification=("SELFTEST_SIGNAL" if all(gates.values())
                        else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP69_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":classification,"criteria":gates,
            "retention_rate":round(retention,8),
            "direct_over_random_cpu_ratio":round(cpu_ratio,6),
            "qualified_end_to_end_neural_baseline":
                overall["gradient_baseline_converged_worlds"]==12,
            "totals":overall,"by_family":family,"worlds":worlds
        },sort_keys=True,separators=(",",":")))
        # Scientific threshold failures are recorded, not unit-test asserts.


if __name__=="__main__":
    unittest.main()

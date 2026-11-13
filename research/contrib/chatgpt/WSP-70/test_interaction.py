"""WSP70 preregistered gradient-free reusable interaction feature SELFTEST.

Training uses a single common 96-action charged no-reset source experience
stream per world, stage A 48 and stage B 96. Direct neural candidate and
equal-width random-dictionary control use identical evidence and ridge
editing/confidence; source dynamics and heldout labels stay evaluator-only.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from random import Random
import sys
import time
import json
import unittest

from source import SEEDS, STATES, ACTIONS, STAGE_A, TRAIN_ACTIONS, build_world
from interaction_writer import (
    ReusableInteractionNeural, DICTIONARY, neural_conjunction_weights,
    activation
)
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"WSP-69"))
from growing_neural import FeatureGrowthNeural, BASE_NEURONS, NEW_PER_PHASE
from end_to_end_control import EndToEndAdamControl
sys.path.insert(0,str(ROOT/"WSP-67"))
from independent_symbolic import ExactMemory
sys.path.insert(0,str(ROOT/"WSP-64"))
from independent_tree import IndependentTreeControl


def digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,
                  separators=(",",":")).encode("ascii")).hexdigest()


def evaluate(predict,world,seen,compositions=None):
    physical={"correct":0,"wrong_confident":0,"abstain":0}
    unseen={"correct":0,"wrong_confident":0,"abstain":0,"total":0}
    for state in STATES:
        for action in ACTIONS:
            result=predict(state,action)
            truth=world._step_oracle(state,action)  # evaluator-only scoring
            label=("abstain" if result is None else
                   "correct" if result==truth else "wrong_confident")
            physical[label]+=1
            if (state,action) not in seen:
                unseen[label]+=1
                unseen["total"]+=1
    assert sum(physical.values())==64
    assert unseen["correct"]+unseen["wrong_confident"]+unseen["abstain"]==unseen["total"]
    out={"physical":physical,"unseen":unseen}
    if compositions is not None:
        comp={"correct":0,"wrong_confident":0,"abstain":0}
        for item in compositions:
            first,second=item.actions
            mid=predict(item.start,first)
            end=predict(mid,second) if mid is not None else None
            label=("abstain" if end is None else
                   "correct" if end==item._finish else "wrong_confident")
            comp[label]+=1
        assert sum(comp.values())==len(compositions)
        out["compositions"]=comp
    return out


class FrozenReusableInteractionNeurons(unittest.TestCase):
    def test_source_blindness_and_action_gated_weight_construction(self):
        writer_source=(Path(__file__).parent/"interaction_writer.py").read_text("utf-8")
        for forbidden in ("from source import","import source",
                          "from weight_programmer import","_step_oracle"):
            self.assertNotIn(forbidden,writer_source)
        self.assertEqual(len(DICTIONARY),224)
        self.assertEqual(len(set(DICTIONARY)),224)
        self.assertEqual(ReusableInteractionNeural.gradient_steps,0)
        self.assertEqual(NEW_PER_PHASE,12)
        key=(2,((0,1),(3,0)))
        w,b=neural_conjunction_weights(key)
        self.assertEqual(len(w),8)
        self.assertEqual(activation(key,(1,0,0,0),2),1.0)
        self.assertEqual(activation(key,(1,0,0,1),2),0.0)
        self.assertEqual(activation(key,(0,0,0,0),2),0.0)
        self.assertEqual(activation(key,(1,0,0,0),3),0.0)
        for cohort in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(4401,cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(4301)
        self.assertEqual(len(SEEDS),14)
        for seed in SEEDS:
            world=build_world(seed)
            self.assertEqual(world.receipt(),build_world(seed).receipt())
            self.assertEqual(len(world.composition_tests()),32)
        world=build_world(4401)
        model=ReusableInteractionNeural("residual",4401)
        first=world.training_session().step(0)
        from source import Experience
        with self.assertRaises(ValueError):
            model.charge(Experience((1,1,1,1),0,first.after))
        with self.assertRaises(ValueError):
            model.charge(Experience((0,0,0,0),0,first.after,0))
        self.assertEqual(model.charged_actions,0)
        model.charge(first)
        with self.assertRaises(ValueError):
            model.grow()

    def test_frozen_fourteen_worlds_controls_and_retention(self):
        total={
            "primary_worlds":0, "negative_worlds":0,
            "primary_actions":0,"primary_physical":0,"primary_compositions":0,
            "candidate_correct":0,"candidate_wrong":0,"candidate_abstain":0,
            "candidate_unseen_correct":0,"candidate_unseen_wrong":0,
            "candidate_unseen_total":0,
            "random_correct":0,"random_wrong":0,"random_abstain":0,
            "random_unseen_correct":0,"random_unseen_wrong":0,
            "candidate_compositions":0,"candidate_compositions_wrong":0,
            "random_compositions":0,
            "fixed_correct":0,"fixed_unseen_correct":0,
            "memory_correct":0,"memory_compositions":0,
            "tree_correct":0,"tree_wrong":0,"tree_compositions":0,
            "mlp_forced_correct":0,"mlp_forced_wrong":0,
            "mlp_confident_correct":0,"mlp_confident_wrong":0,
            "mlp_converged":0,"mlp_gradient_steps":0,
            "stageA_correct_eligible":0,"stageB_retained_correct":0,
            "hidden_growth_worlds":0,"readout_changed_worlds":0,
            "matrix_cold_restore_worlds":0,
            "candidate_cpu_ns":0,"random_cpu_ns":0,
            "mlp_train_cpu_ns":0,
            "quartic_wrong_confident":0,"quartic_correct":0,
            "quartic_unseen_correct":0
        }
        world_records=[]
        by_family={}
        for seed in SEEDS:
            with self.subTest(seed=seed):
                negative=seed>=4413
                world=build_world(seed)
                initial=time.perf_counter()
                candidate=ReusableInteractionNeural("residual",seed=seed)
                random_arm=ReusableInteractionNeural("random",seed=seed)
                fixed=FeatureGrowthNeural("random",seed=seed)
                source=world.training_session()
                rng=Random(int.from_bytes(sha256(
                    f"WSP70|charged-action-policy|{seed}".encode("ascii")
                ).digest(),"big"))
                charge_rows=[]
                candidate_cpu=random_cpu=0
                for i in range(TRAIN_ACTIONS):
                    row=source.step(rng.choice(ACTIONS))
                    charge_rows.append((row.before,row.action,row.after))
                    t=time.process_time_ns()
                    candidate.charge(row)
                    candidate_cpu+=time.process_time_ns()-t
                    t=time.process_time_ns()
                    random_arm.charge(row)
                    random_cpu+=time.process_time_ns()-t
                    fixed.charge(row)
                    if i+1 in (STAGE_A,TRAIN_ACTIONS):
                        t=time.process_time_ns()
                        self.assertGreater(candidate.grow(),0)
                        candidate_cpu+=time.process_time_ns()-t
                        t=time.process_time_ns()
                        self.assertGreater(random_arm.grow(),0)
                        random_cpu+=time.process_time_ns()-t
                        if i+1==STAGE_A:
                            frozen_a=candidate.snapshot()
                            cold_a=ReusableInteractionNeural.restore(frozen_a)
                        else:
                            frozen_b=candidate.snapshot()
                            cold_b=ReusableInteractionNeural.restore(frozen_b)
                            random_cold=ReusableInteractionNeural.restore(
                                random_arm.snapshot())
                self.assertEqual(len(charge_rows),96)
                self.assertEqual(source.ledger[0].before,(0,0,0,0))
                self.assertTrue(all(charge_rows[i][2]==charge_rows[i+1][0]
                                    for i in range(95)))
                self.assertEqual(candidate.charged_actions,96)
                self.assertEqual(random_arm.charged_actions,96)
                self.assertEqual(fixed.charged_actions,96)
                self.assertEqual(len(candidate.hidden_weights),
                                 len(random_arm.hidden_weights))
                self.assertEqual(candidate.hidden_weights[:BASE_NEURONS],
                                 random_arm.hidden_weights[:BASE_NEURONS])
                self.assertEqual(candidate.growth_rounds,2)
                self.assertEqual(random_arm.growth_rounds,2)
                self.assertGreater(len(candidate.hidden_weights),BASE_NEURONS)
                self.assertEqual(candidate.snapshot(),cold_b.snapshot())
                self.assertEqual(frozen_a,cold_a.snapshot())
                self.assertNotIn('"ledger"',frozen_b)
                self.assertNotIn('"centers"',frozen_b)
                self.assertNotIn('"source"',frozen_b)
                with self.assertRaises(ValueError):
                    ReusableInteractionNeural.restore(frozen_b.replace(
                        "wsp69.neural-feature-growth.v1",
                        "wsp69.neural-feature-growth.v2"))
                for state in STATES:
                    for action in ACTIONS:
                        self.assertEqual(cold_b.raw(state,action),
                                         candidate.raw(state,action))
                        self.assertEqual(cold_b.predict(state,action),
                                         candidate.predict(state,action))
                        self.assertEqual(random_cold.predict(state,action),
                                         random_arm.predict(state,action))
                seen={(b,a) for b,a,y in charge_rows}
                previous_seen={(b,a) for b,a,y in charge_rows[:STAGE_A]}
                tasks=world.composition_tests()
                stage_a=evaluate(cold_a.predict,world,previous_seen)
                t=time.process_time_ns()
                cand=evaluate(cold_b.predict,world,seen,tasks)
                candidate_cpu+=time.process_time_ns()-t
                t=time.process_time_ns()
                rand=evaluate(random_cold.predict,world,seen,tasks)
                random_cpu+=time.process_time_ns()-t
                baseline=evaluate(fixed.predict,world,seen)
                memory=ExactMemory(charge_rows)
                mem=evaluate(memory.predict,world,seen,tasks)
                tree=IndependentTreeControl(charge_rows,4)
                fitted_tree=evaluate(tree.predict,world,seen,tasks)
                erased=ReusableInteractionNeural.restore(frozen_b)
                erased.w_readout=[[0.0]*len(x) for x in erased.w_readout]
                self.assertTrue(any(
                    erased.raw(state,action)!=cold_b.raw(state,action)
                    for state in STATES for action in ACTIONS))
                retained=eligible=0
                for state in STATES:
                    for action in ACTIONS:
                        earlier=cold_a.predict(state,action)
                        truth=world._step_oracle(state,action)
                        if earlier is not None and earlier==truth:
                            eligible+=1
                            retained+=int(cold_b.predict(state,action)==truth)
                item={
                    "seed":seed,"family":world.family,"source":world.receipt(),
                    "charged_actions":96,
                    "charged_ledger_sha256":digest(charge_rows),
                    "hidden_neurons_stageA":
                        len(cold_a.hidden_weights)-BASE_NEURONS,
                    "hidden_neurons_stageB":
                        len(cold_b.hidden_weights)-BASE_NEURONS,
                    "source_blind_selected_feature_ids":
                        candidate.selected_feature_ids(),
                    "stageA_numeric_snapshot_sha256":
                        sha256(frozen_a.encode("ascii")).hexdigest(),
                    "stageB_numeric_snapshot_sha256":
                        sha256(frozen_b.encode("ascii")).hexdigest(),
                    "stageA_evaluation":stage_a,
                    "stageB_candidate":cand,"stageB_random":rand,
                    "stageB_fixed":baseline,
                    "exact_history_memory":mem,
                    "independent_decision_tree":fitted_tree,
                    "retained_correct":retained,"retention_eligible":eligible,
                    "candidate_cpu_ns":candidate_cpu,
                    "random_cpu_ns":random_cpu,
                    "candidate_matrix_bytes":candidate.snapshot_bytes(),
                    "random_matrix_bytes":random_arm.snapshot_bytes(),
                    "whole_world_wall_seconds":round(time.perf_counter()-initial,6),
                    "new_hidden_weight_parameters":(
                        len(candidate.hidden_weights)-BASE_NEURONS)*9,
                    "readout_parameter_count":candidate.readout_parameter_count()
                }
                if negative:
                    total["negative_worlds"]+=1
                    total["quartic_correct"]+=cand["physical"]["correct"]
                    total["quartic_wrong_confident"]+=cand["physical"]["wrong_confident"]
                    total["quartic_unseen_correct"]+=cand["unseen"]["correct"]
                else:
                    mlp=EndToEndAdamControl(seed)
                    started=time.process_time_ns()
                    train=mlp.fit(charge_rows)
                    grad_ns=time.process_time_ns()-started
                    mlp_forced=evaluate(mlp.predict,world,seen,tasks)
                    mlp_safe=evaluate(
                        lambda s,a:mlp.predict(s,a,confidence=True),world,seen)
                    item["mlp_train"]=train
                    item["mlp_forced"]=mlp_forced
                    item["mlp_confident"]=mlp_safe
                    item["mlp_training_cpu_ns"]=grad_ns
                    total["primary_worlds"]+=1
                    total["primary_actions"]+=96
                    total["primary_physical"]+=64
                    total["primary_compositions"]+=32
                    total["candidate_correct"]+=cand["physical"]["correct"]
                    total["candidate_wrong"]+=cand["physical"]["wrong_confident"]
                    total["candidate_abstain"]+=cand["physical"]["abstain"]
                    total["candidate_unseen_correct"]+=cand["unseen"]["correct"]
                    total["candidate_unseen_wrong"]+=cand["unseen"]["wrong_confident"]
                    total["candidate_unseen_total"]+=cand["unseen"]["total"]
                    total["random_correct"]+=rand["physical"]["correct"]
                    total["random_wrong"]+=rand["physical"]["wrong_confident"]
                    total["random_abstain"]+=rand["physical"]["abstain"]
                    total["random_unseen_correct"]+=rand["unseen"]["correct"]
                    total["random_unseen_wrong"]+=rand["unseen"]["wrong_confident"]
                    total["candidate_compositions"]+=cand["compositions"]["correct"]
                    total["candidate_compositions_wrong"]+=cand["compositions"]["wrong_confident"]
                    total["random_compositions"]+=rand["compositions"]["correct"]
                    total["fixed_correct"]+=baseline["physical"]["correct"]
                    total["fixed_unseen_correct"]+=baseline["unseen"]["correct"]
                    total["memory_correct"]+=mem["physical"]["correct"]
                    total["memory_compositions"]+=mem["compositions"]["correct"]
                    total["tree_correct"]+=fitted_tree["physical"]["correct"]
                    total["tree_wrong"]+=fitted_tree["physical"]["wrong_confident"]
                    total["tree_compositions"]+=fitted_tree["compositions"]["correct"]
                    total["mlp_forced_correct"]+=mlp_forced["physical"]["correct"]
                    total["mlp_forced_wrong"]+=mlp_forced["physical"]["wrong_confident"]
                    total["mlp_confident_correct"]+=mlp_safe["physical"]["correct"]
                    total["mlp_confident_wrong"]+=mlp_safe["physical"]["wrong_confident"]
                    total["mlp_converged"]+=int(train["fully_trained"])
                    total["mlp_gradient_steps"]+=train["gradient_updates_total"]
                    total["stageA_correct_eligible"]+=eligible
                    total["stageB_retained_correct"]+=retained
                    total["hidden_growth_worlds"]+=int(
                        len(cold_b.hidden_weights)>len(cold_a.hidden_weights))
                    total["readout_changed_worlds"]+=int(
                        candidate.changed_readout(cold_a))
                    total["matrix_cold_restore_worlds"]+=1
                    total["candidate_cpu_ns"]+=candidate_cpu
                    total["random_cpu_ns"]+=random_cpu
                    total["mlp_train_cpu_ns"]+=grad_ns
                    group=by_family.setdefault(world.family,{
                        "worlds":0,"candidate_correct":0,"random_correct":0,
                        "candidate_unseen":0,"random_unseen":0,
                        "candidate_wrong":0,"random_wrong":0,
                        "mlp_converged":0})
                    group["worlds"]+=1
                    group["candidate_correct"]+=cand["physical"]["correct"]
                    group["random_correct"]+=rand["physical"]["correct"]
                    group["candidate_unseen"]+=cand["unseen"]["correct"]
                    group["random_unseen"]+=rand["unseen"]["correct"]
                    group["candidate_wrong"]+=cand["physical"]["wrong_confident"]
                    group["random_wrong"]+=rand["physical"]["wrong_confident"]
                    group["mlp_converged"]+=int(train["fully_trained"])
                world_records.append(item)
        self.assertEqual(total["primary_worlds"],12)
        self.assertEqual(total["negative_worlds"],2)
        self.assertEqual(total["primary_actions"],1152)
        self.assertEqual(total["primary_physical"],768)
        self.assertEqual(total["primary_compositions"],384)
        self.assertEqual(total["matrix_cold_restore_worlds"],12)
        self.assertEqual(len(world_records),14)
        retention=(total["stageB_retained_correct"]/
                   total["stageA_correct_eligible"]
                   if total["stageA_correct_eligible"] else 0.0)
        cpu_ratio=total["candidate_cpu_ns"]/max(1,total["random_cpu_ns"])
        gates={
            "unseen_correct_ge_25":total["candidate_unseen_correct"]>=25,
            "unseen_gain_random_ge_12":
                total["candidate_unseen_correct"]-total["random_unseen_correct"]>=12,
            "all_confident_correct_ge_300":total["candidate_correct"]>=300,
            "all_gain_random_ge_25":
                total["candidate_correct"]-total["random_correct"]>=25,
            "confident_wrong_le_20":total["candidate_wrong"]<=20,
            "compositions_ge_100":total["candidate_compositions"]>=100,
            "stageA_retention_ge_85pct":retention>=0.85,
            "hidden_growth_readout_edit_ge_10_worlds":
                total["hidden_growth_worlds"]>=10 and
                total["readout_changed_worlds"]>=10,
            "cold_tamper_parity_12_worlds":
                total["matrix_cold_restore_worlds"]==12,
            "cpu_vs_random_le_3":cpu_ratio<=3.0,
            "quartic_negative_wrong_le_6":
                total["quartic_wrong_confident"]<=6
        }
        status=("SELFTEST_SIGNAL" if all(gates.values())
                else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP70_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":status,"criteria":gates,
            "retention_rate":round(retention,8),
            "candidate_over_random_cpu_ratio":round(cpu_ratio,6),
            "fully_converged_end_to_end_worlds":total["mlp_converged"],
            "totals":total,"by_family":by_family,"worlds":world_records
        },sort_keys=True,separators=(",",":")))
        # A negative result is recorded as scientific evidence, not a unit
        # test failure to be hidden by tuning metrics after the experiment.


if __name__=="__main__":
    unittest.main()

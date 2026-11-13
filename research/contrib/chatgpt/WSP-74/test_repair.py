"""WSP74 frozen active causal interventions + direct hidden-neuron weight repair.

Source world roles and all heldout physics live exclusively in evaluator.
EACH seed runs two distinct paid 144-action no-reset physical sessions,
sharing an independently charged initial 96-action prefix; active vs
uniform random intervenes for 48 real actions and then directly learns
numerical ReLU weights from only that physical experience. All same-ledger
ablation controls pay ZERO extra physical source calls.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from random import Random
import sys
import time
import json
import unittest

from source import SEEDS,STATES,ACTIONS,TRAIN_ACTIONS,build_world
from repair import (
    repair,fitted_readout,policy_action,random_policy,
    A_CHARGES,B_CHARGES,MAX_EDITS,TOP_UNITS,DELTA
)
from independent_end_to_end import EndToEndAdamControl
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"WSP-70"))
from interaction_writer import ReusableInteractionNeural
sys.path.insert(0,str(ROOT/"WSP-69"))
from growing_neural import FeatureGrowthNeural
sys.path.insert(0,str(ROOT/"WSP-67"))
from independent_symbolic import ExactMemory
sys.path.insert(0,str(ROOT/"WSP-64"))
from independent_tree import IndependentTreeControl


def digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),
        default=list).encode("ascii")).hexdigest()


def evaluate(predict,world,paid,compositions=None):
    physical={"correct":0,"wrong_confident":0,"abstain":0}
    unseen={"correct":0,"wrong_confident":0,"abstain":0,"total":0}
    for s in STATES:
        for a in ACTIONS:
            candidate=predict(s,a)
            truth=world._step_oracle(s,a)
            key=("abstain" if candidate is None else
                 "correct" if candidate==truth else "wrong_confident")
            physical[key]+=1
            if (s,a) not in paid:
                unseen[key]+=1
                unseen["total"]+=1
    assert sum(physical.values())==64
    assert sum(v for k,v in unseen.items() if k!="total")==unseen["total"]
    result={"physical":physical,"unseen":unseen}
    if compositions is not None:
        comp={"correct":0,"wrong_confident":0,"abstain":0}
        for task in compositions:
            a,b=task.actions
            mid=predict(task.start,a)
            finish=predict(mid,b) if mid is not None else None
            key=("abstain" if finish is None else
                 "correct" if finish==task._finish else "wrong_confident")
            comp[key]+=1
        assert sum(comp.values())==len(compositions)
        result["two_action"]=comp
    return result


def retention(predict,frozen,world):
    before=kept=0
    for s in STATES:
        for a in ACTIONS:
            past=frozen.predict(s,a)
            if past is not None and past==world._step_oracle(s,a):
                before+=1
                kept+=int(predict(s,a)==past)
    return {"eligible":before,"retained":kept}


class FrozenCausalActionDirectedNumericalRepair(unittest.TestCase):
    def test_frozen_source_bounds_and_source_blind_numerical_writer(self):
        source_code=(Path(__file__).parent/"repair.py").read_text("utf-8")
        for forbidden in ("from source import","import source",
                          "_step_oracle","from weight_programmer import",
                          "torch","backward(","from independent_symbolic import"):
            self.assertNotIn(forbidden,source_code)
        self.assertEqual(len(SEEDS),16)
        self.assertEqual(TRAIN_ACTIONS,144)
        self.assertEqual(A_CHARGES,96)
        self.assertEqual(B_CHARGES,48)
        self.assertEqual(MAX_EDITS,4)
        self.assertEqual(TOP_UNITS,8)
        self.assertEqual(DELTA,0.5)
        for seed in SEEDS:
            self.assertEqual(build_world(seed).receipt(),build_world(seed).receipt())
            self.assertEqual(len(build_world(seed).composition_tests()),32)
        for protected in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(SEEDS[0],cohort=protected)
        with self.assertRaises(PermissionError):
            build_world(4701)
        world=build_world(4801)
        session=world.training_session()
        for step in range(144):
            session.step(step%4)
        self.assertEqual(len(session.ledger),144)
        with self.assertRaises(ValueError):
            session.step(0)
        with self.assertRaises(ValueError):
            repair("not-a-model",[],[],"counterexample",4801)

    def test_frozen_new_physics_interventions_numerical_repairs_and_baselines(self):
        fields=(
            "primary_worlds","negative_worlds","worlds","real_charged_actions",
            "primary_physical_cases","primary_two_action_cases",
            "active_repair_correct","active_repair_wrong","active_repair_abstain",
            "active_repair_unseen_correct","active_repair_unseen_wrong",
            "active_repair_unseen_total","active_two_action_correct",
            "active_two_action_wrong","readout_refit_correct",
            "readout_refit_wrong","random_hidden_edit_correct",
            "random_hidden_edit_wrong","random_policy_repair_correct",
            "random_policy_repair_wrong","random_policy_unseen_correct",
            "exact_memory_correct","exact_memory_wrong",
            "decision_tree_correct","decision_tree_wrong",
            "mlp_confident_correct","mlp_confident_wrong",
            "mlp_forced_correct","mlp_forced_wrong","mlp_converged_worlds",
            "mlp_gradient_steps","mlp_training_cpu_ns",
            "stageA_eligible","stageA_retained",
            "worlds_with_changed_hidden_coefficients",
            "worlds_with_reprogrammed_readout","cold_restored_worlds",
            "active_unique_contexts","random_unique_contexts",
            "active_repair_cpu_ns","refit_cpu_ns","active_policy_cpu_ns",
            "random_policy_cpu_ns","active_repair_eval_cpu_ns",
            "refit_eval_cpu_ns",
            "quartic_active_wrong","quartic_active_correct",
            "quartic_random_policy_wrong"
        )
        total={key:0 for key in fields}
        receipts=[]
        by_family={}
        for seed in SEEDS:
            with self.subTest(seed=seed):
                negative=seed>=4813
                world=build_world(seed)
                active_world=world.training_session()
                random_world=build_world(seed).training_session()
                initial_action_rng=Random(int.from_bytes(sha256(
                    f"WSP74|identical-A-actions|{seed}".encode("ascii")
                ).digest(),"big"))
                first_teacher=ReusableInteractionNeural("residual",seed=seed)
                second_teacher=ReusableInteractionNeural("random",seed=seed)
                A_active=[]
                A_random=[]
                for i in range(A_CHARGES):
                    a=initial_action_rng.choice(ACTIONS)
                    o1=active_world.step(a)
                    o2=random_world.step(a)
                    d1=(o1.before,o1.action,o1.after)
                    d2=(o2.before,o2.action,o2.after)
                    self.assertEqual(d1,d2)
                    A_active.append(d1)
                    A_random.append(d2)
                    first_teacher.charge(o1)
                    second_teacher.charge(o1)
                    if i+1 in (48,96):
                        first_teacher.grow()
                        second_teacher.grow()
                self.assertEqual(A_active,A_random)
                self.assertEqual(first_teacher.charged_actions,96)
                self.assertEqual(second_teacher.charged_actions,96)
                teacher_snapshot=first_teacher.snapshot()
                teacher_cold=FeatureGrowthNeural.restore(teacher_snapshot)
                self.assertEqual(teacher_cold.snapshot(),teacher_snapshot)
                # Frozen teachers may only predict B actions, never train
                # on B or read source roles/heldout source consequences.
                active_B=[]
                random_B=[]
                rr=random_policy(seed)
                active_policy_cpu=random_policy_cpu=0
                for i in range(B_CHARGES):
                    t=time.process_time_ns()
                    active_a=policy_action(
                        first_teacher,second_teacher,active_world.state,seed,i)
                    active_policy_cpu+=time.process_time_ns()-t
                    t=time.process_time_ns()
                    random_a=rr.choice(ACTIONS)
                    random_policy_cpu+=time.process_time_ns()-t
                    o1=active_world.step(active_a)
                    o2=random_world.step(random_a)
                    active_B.append((o1.before,o1.action,o1.after))
                    random_B.append((o2.before,o2.action,o2.after))
                self.assertEqual(len(active_world.ledger),144)
                self.assertEqual(len(random_world.ledger),144)
                self.assertEqual(A_active[-1][2],active_B[0][0])
                self.assertEqual(A_random[-1][2],random_B[0][0])
                for rows in (A_active+active_B,A_random+random_B):
                    self.assertEqual(rows[0][0],(0,0,0,0))
                    self.assertTrue(all(rows[j][2]==rows[j+1][0]
                                     for j in range(143)))
                t=time.process_time_ns()
                candidate,edit_receipt=repair(
                    teacher_snapshot,A_active,active_B,"counterexample",seed)
                candidate_cpu=time.process_time_ns()-t
                t=time.process_time_ns()
                refit=fitted_readout(teacher_snapshot,A_active,active_B)
                refit_cpu=time.process_time_ns()-t
                random_edit,random_edit_receipt=repair(
                    teacher_snapshot,A_active,active_B,"random",seed)
                random_active,random_active_receipt=repair(
                    teacher_snapshot,A_random,random_B,"counterexample",seed)
                for network in (candidate,refit,random_edit,random_active):
                    self.assertEqual(len(network.hidden_weights),
                                     len(teacher_cold.hidden_weights))
                    self.assertEqual(network.charged_actions,96)
                    self.assertEqual(network.growth_rounds,2)
                self.assertEqual(len(edit_receipt["hidden_edits"])<=4,True)
                self.assertEqual(len(random_edit_receipt["hidden_edits"]),4)
                for index,coord,delta,gain in edit_receipt["hidden_edits"]:
                    self.assertTrue(32<=index<len(candidate.hidden_weights))
                    self.assertIn(coord,(0,1,2,3))
                    self.assertIn(delta,(-0.5,0.5))
                    self.assertIsNotNone(gain)
                    self.assertGreater(gain,1e-9)
                self.assertEqual(edit_receipt["direct_gradient_steps"],0)
                self.assertEqual(
                    edit_receipt["changed_hidden_coefficients"],
                    sum(candidate.hidden_weights[j][k]!=teacher_cold.hidden_weights[j][k]
                        for j in range(len(candidate.hidden_weights))
                        for k in range(8)))
                # Snapshots contain ONLY neural numeric matrices/covariance.
                # Exact restoration must not require training ledgers.
                for network in (candidate,refit,random_edit,random_active):
                    snap=network.snapshot()
                    self.assertNotIn('"ledger"',snap)
                    self.assertNotIn('"source"',snap)
                    restored=FeatureGrowthNeural.restore(snap)
                    self.assertEqual(restored.snapshot(),snap)
                    with self.assertRaises(ValueError):
                        FeatureGrowthNeural.restore(snap.replace(
                            "wsp69.neural-feature-growth.v1",
                            "wsp69.neural-feature-growth.v2"))
                    for s in STATES:
                        for a in ACTIONS:
                            self.assertEqual(restored.predict(s,a),
                                             network.predict(s,a))
                seen_active={(s,a) for s,a,y in A_active+active_B}
                seen_random={(s,a) for s,a,y in A_random+random_B}
                tasks=world.composition_tests()
                t=time.process_time_ns()
                tested_candidate=evaluate(candidate.predict,world,seen_active,tasks)
                candidate_eval_cpu=time.process_time_ns()-t
                t=time.process_time_ns()
                tested_refit=evaluate(refit.predict,world,seen_active,tasks)
                refit_eval_cpu=time.process_time_ns()-t
                tested_random_edit=evaluate(random_edit.predict,world,seen_active,tasks)
                tested_random_policy=evaluate(random_active.predict,world,seen_random,tasks)
                mem=ExactMemory(A_active+active_B)
                mem_score=evaluate(mem.predict,world,seen_active)
                tree=IndependentTreeControl(A_active+active_B,4)
                tree_score=evaluate(tree.predict,world,seen_active)
                before=evaluate(teacher_cold.predict,world,seen_active)
                old_retention=retention(candidate.predict,teacher_cold,world)
                mlp_fit=mlp_confident=mlp_forced=None
                mlp_cpu=0
                if not negative:
                    mlp=EndToEndAdamControl(seed)
                    t=time.process_time_ns()
                    mlp_fit=mlp.fit(A_active+active_B)
                    mlp_cpu=time.process_time_ns()-t
                    mlp_confident=evaluate(
                        lambda s,a:mlp.predict(s,a,confidence=True),
                        world,seen_active)
                    mlp_forced=evaluate(mlp.predict,world,seen_active)
                record={
                    "seed":seed,"family":world.family,
                    "source":world.receipt(),
                    "active_A_physical_sha256":digest(A_active),
                    "random_A_physical_sha256":digest(A_random),
                    "active_B_physical_sha256":digest(active_B),
                    "random_B_physical_sha256":digest(random_B),
                    "physically_paid_action_count_per_policy":144,
                    "A_prefix_same_action_consequence":A_active==A_random,
                    "unique_active_physical_contexts":len(seen_active),
                    "unique_random_physical_contexts":len(seen_random),
                    "frozen_StageA_numeric_snapshot_sha256":sha256(
                        teacher_snapshot.encode("ascii")).hexdigest(),
                    "candidate_numeric_snapshot_sha256":sha256(
                        candidate.snapshot().encode("ascii")).hexdigest(),
                    "random_mutation_numeric_snapshot_sha256":sha256(
                        random_edit.snapshot().encode("ascii")).hexdigest(),
                    "policy_random_numeric_snapshot_sha256":sha256(
                        random_active.snapshot().encode("ascii")).hexdigest(),
                    "coordinate_edit_receipt":edit_receipt,
                    "random_edit_receipt":random_edit_receipt,
                    "random_action_edit_receipt":random_active_receipt,
                    "active_repair":tested_candidate,
                    "same_ledger_readout_refit":tested_refit,
                    "same_ledger_random_hidden_edit":tested_random_edit,
                    "random_policy_same_repair":tested_random_policy,
                    "same_ledger_exact_memory":mem_score,
                    "same_ledger_decision_tree":tree_score,
                    "frozen_teacher_A":before,
                    "old_cold_retention":old_retention,
                    "fully_trained_end_to_end_MLP":mlp_fit,
                    "MLP_confident_eval":mlp_confident,
                    "MLP_forced_eval":mlp_forced,
                    "active_policy_cpu_ns":active_policy_cpu,
                    "uniform_random_policy_cpu_ns":random_policy_cpu,
                    "coordinate_repair_cpu_ns":candidate_cpu,
                    "same_ledger_refit_cpu_ns":refit_cpu,
                    "candidate_evaluator_cpu_ns":candidate_eval_cpu,
                    "refit_evaluator_cpu_ns":refit_eval_cpu,
                    "MLP_train_cpu_ns":mlp_cpu
                }
                receipts.append(record)
                total["worlds"]+=1
                total["real_charged_actions"]+=288
                total["cold_restored_worlds"]+=1
                if negative:
                    total["negative_worlds"]+=1
                    total["quartic_active_wrong"]+=tested_candidate[
                        "physical"]["wrong_confident"]
                    total["quartic_active_correct"]+=tested_candidate[
                        "physical"]["correct"]
                    total["quartic_random_policy_wrong"]+=tested_random_policy[
                        "physical"]["wrong_confident"]
                else:
                    total["primary_worlds"]+=1
                    total["primary_physical_cases"]+=64
                    total["primary_two_action_cases"]+=32
                    for name,test_result in (
                        ("active_repair",tested_candidate),
                        ("readout_refit",tested_refit),
                        ("random_hidden_edit",tested_random_edit),
                        ("random_policy_repair",tested_random_policy),
                        ("exact_memory",mem_score),
                        ("decision_tree",tree_score),
                        ("mlp_confident",mlp_confident),
                        ("mlp_forced",mlp_forced)
                    ):
                        total[f"{name}_correct"]+=test_result["physical"]["correct"]
                        total[f"{name}_wrong"]+=test_result["physical"]["wrong_confident"]
                    total["active_repair_abstain"]+=tested_candidate["physical"]["abstain"]
                    total["active_repair_unseen_correct"]+=tested_candidate["unseen"]["correct"]
                    total["active_repair_unseen_wrong"]+=tested_candidate["unseen"]["wrong_confident"]
                    total["active_repair_unseen_total"]+=tested_candidate["unseen"]["total"]
                    total["active_two_action_correct"]+=tested_candidate["two_action"]["correct"]
                    total["active_two_action_wrong"]+=tested_candidate["two_action"]["wrong_confident"]
                    total["random_policy_unseen_correct"]+=tested_random_policy["unseen"]["correct"]
                    total["stageA_eligible"]+=old_retention["eligible"]
                    total["stageA_retained"]+=old_retention["retained"]
                    total["active_unique_contexts"]+=len(seen_active)
                    total["random_unique_contexts"]+=len(seen_random)
                    total["worlds_with_changed_hidden_coefficients"]+=int(
                        edit_receipt["changed_hidden_coefficients"]>0)
                    total["worlds_with_reprogrammed_readout"]+=int(
                        edit_receipt["readout_reprogrammed"])
                    total["active_repair_cpu_ns"]+=candidate_cpu
                    total["refit_cpu_ns"]+=refit_cpu
                    total["active_policy_cpu_ns"]+=active_policy_cpu
                    total["random_policy_cpu_ns"]+=random_policy_cpu
                    total["active_repair_eval_cpu_ns"]+=candidate_eval_cpu
                    total["refit_eval_cpu_ns"]+=refit_eval_cpu
                    total["mlp_converged_worlds"]+=int(mlp_fit["fully_trained"])
                    total["mlp_gradient_steps"]+=mlp_fit["gradient_updates_total"]
                    total["mlp_training_cpu_ns"]+=mlp_cpu
                    bucket=by_family.setdefault(world.family,{
                        "worlds":0,"active_correct":0,"readout_correct":0,
                        "random_edit_correct":0,"random_policy_correct":0,
                        "active_unseen":0,"active_wrong":0,"mlp_converged":0})
                    bucket["worlds"]+=1
                    bucket["active_correct"]+=tested_candidate["physical"]["correct"]
                    bucket["readout_correct"]+=tested_refit["physical"]["correct"]
                    bucket["random_edit_correct"]+=tested_random_edit["physical"]["correct"]
                    bucket["random_policy_correct"]+=tested_random_policy["physical"]["correct"]
                    bucket["active_unseen"]+=tested_candidate["unseen"]["correct"]
                    bucket["active_wrong"]+=tested_candidate["physical"]["wrong_confident"]
                    bucket["mlp_converged"]+=int(mlp_fit["fully_trained"])
        self.assertEqual(total["worlds"],16)
        self.assertEqual(total["primary_worlds"],12)
        self.assertEqual(total["negative_worlds"],4)
        self.assertEqual(total["real_charged_actions"],4608)
        self.assertEqual(total["primary_physical_cases"],768)
        self.assertEqual(total["primary_two_action_cases"],384)
        self.assertEqual(total["cold_restored_worlds"],16)
        retain=total["stageA_retained"]/max(1,total["stageA_eligible"])
        cpu_ratio=(total["active_repair_cpu_ns"]+
                   total["active_policy_cpu_ns"]+
                   total["active_repair_eval_cpu_ns"])/max(1,
                   total["refit_cpu_ns"]+total["refit_eval_cpu_ns"])
        criterion={
            "primary_correct_ge_320":total["active_repair_correct"]>=320,
            "beat_readout_only_25":
                total["active_repair_correct"]-total["readout_refit_correct"]>=25,
            "beat_same_ledger_random_hidden_edits_20":
                total["active_repair_correct"]-total["random_hidden_edit_correct"]>=20,
            "beat_equal_paid_random_B_policy_20":
                total["active_repair_correct"]-total["random_policy_repair_correct"]>=20,
            "never_paid_contexts_correct_ge_30":
                total["active_repair_unseen_correct"]>=30,
            "confident_wrong_le_24":total["active_repair_wrong"]<=24,
            "StageA_true_confident_retention_ge_80pct":retain>=0.80,
            "two_action_compositions_ge_110":total["active_two_action_correct"]>=110,
            "negative_nested_confident_wrong_le_16":
                total["quartic_active_wrong"]<=16,
            "actual_hidden_coordinate_edits_in_10_worlds":
                total["worlds_with_changed_hidden_coefficients"]>=10,
            "all_16_cold_snapshot_tamper_parity":total["cold_restored_worlds"]==16,
            "whole_candidate_CPU_over_refit_le_8":cpu_ratio<=8.0
        }
        classification=("SELFTEST_SIGNAL" if all(criterion.values()) else
                        "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP74_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":classification,"criteria":criterion,
            "stageA_retention_rate":round(retain,8),
            "measured_full_candidate_to_refit_cpu":round(cpu_ratio,6),
            "end_to_end_MLP_converged_worlds":total["mlp_converged_worlds"],
            "totals":total,"by_family":by_family,"worlds":receipts
        },sort_keys=True,separators=(",",":")))
        # Science FAIL is preserved as diagnostic and is NOT a unittest FAIL.


if __name__=="__main__":
    unittest.main()

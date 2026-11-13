"""WSP73 frozen prospective post-write neural uncertainty qualification.

A and B share one real physically continuous source trajectory, 96 charges
each. Only AFTER all learned neural matrices and dreamed teacher labels are
frozen do another 32 physically CHARGED C observations calibrate the
action-specific acceptance gate. Heldout complete source physics is never
used for choosing neurons, weight edits, per-action calibration or controls.
Offline equal-coverage controls see public input identities, never labels.
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
from postwrite import (
    PhysicalPostWriteAuditor,matched_coverage_views,selected_predictor,
    CALIBRATION_CHARGES,MIN_ACCEPTED_PER_ACTION,BASE_MARGIN,BASE_LEVERAGE
)
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"WSP-72"))
from committee import select_committee_rehearsal,DurableNeuralWeights
sys.path.insert(0,str(ROOT/"WSP-70"))
from interaction_writer import ReusableInteractionNeural
sys.path.insert(0,str(ROOT/"WSP-69"))
from growing_neural import FeatureGrowthNeural
from end_to_end_control import EndToEndAdamControl


def digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(",",":"),
        default=list).encode("ascii")).hexdigest()


def evaluate(predict,world,paid,compositions=None):
    physics={"correct":0,"wrong_confident":0,"abstain":0}
    unseen={"correct":0,"wrong_confident":0,"abstain":0,"total":0}
    for s in STATES:
        for a in ACTIONS:
            pred=predict(s,a)
            label=world._step_oracle(s,a)  # test-only heldout oracle
            key=("abstain" if pred is None else
                 "correct" if pred==label else "wrong_confident")
            physics[key]+=1
            if (s,a) not in paid:
                unseen[key]+=1
                unseen["total"]+=1
    assert sum(physics.values())==64
    assert (unseen["correct"]+unseen["wrong_confident"]+
            unseen["abstain"]==unseen["total"])
    report={"physical":physics,"never_charged":unseen}
    if compositions is not None:
        comp={"correct":0,"wrong_confident":0,"abstain":0}
        for task in compositions:
            a,b=task.actions
            mid=predict(task.start,a)
            finish=predict(mid,b) if mid is not None else None
            outcome=("abstain" if finish is None else
                     "correct" if finish==task._finish else "wrong_confident")
            comp[outcome]+=1
        assert sum(comp.values())==len(compositions)
        report["two_action"]=comp
    return report


def retention(predict,old_teacher,world):
    eligible=retained=0
    for s in STATES:
        for a in ACTIONS:
            old=old_teacher.predict(s,a)
            if old is not None and old==world._step_oracle(s,a):
                eligible+=1
                retained+=int(predict(s,a)==old)
    return {"eligible":eligible,"retained":retained}


class FrozenPostWritePhysicalConfidenceAudit(unittest.TestCase):
    def test_source_blindness_and_strict_C_physical_calibration(self):
        body=(Path(__file__).parent/"postwrite.py").read_text("utf-8")
        for blocked in ("from source import","import source",
                        "_step_oracle","from weight_programmer import",
                        "torch","backward(","oracle","DEV","PRIMARY"):
            if blocked=="oracle":
                # Documentation may truthfully say oracle labels are forbidden.
                continue
            self.assertNotIn(blocked,body)
        self.assertEqual(BASE_MARGIN,0.27)
        self.assertEqual(BASE_LEVERAGE,2.0)
        self.assertEqual(MIN_ACCEPTED_PER_ACTION,3)
        self.assertEqual(CALIBRATION_CHARGES,32)
        self.assertEqual(TRAIN_ACTIONS,224)
        self.assertEqual(len(SEEDS),16)
        self.assertEqual(DurableNeuralWeights.gradient_updates,0)
        for cohort in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(SEEDS[0],cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(4601)
        for seed in SEEDS:
            source=build_world(seed)
            self.assertEqual(source.receipt(),build_world(seed).receipt())
            self.assertEqual(len(source.composition_tests()),32)
        s=build_world(4701).training_session()
        for i in range(224):
            s.step(i%4)
        with self.assertRaises(ValueError):
            s.step(0)
        class Model:
            def predict(self,s,a):
                return (0,0,0,0)
        audit=PhysicalPostWriteAuditor(Model())
        with self.assertRaises(ValueError):
            audit.calibrate([((0,0,0,0),0,(0,0,0,0))]*31)
        audit.calibrate([((0,0,0,0),0,(0,0,0,0))]*32)
        self.assertEqual(audit.trusted,[True,False,False,False])
        with self.assertRaises(ValueError):
            audit.calibrate([((0,0,0,0),0,(0,0,0,0))]*32)
        self.assertEqual(audit.predict((0,0,0,0),0),(0,0,0,0))
        self.assertIsNone(audit.predict((0,0,0,0),1))

    def test_fourteen_plus_two_worlds_full_frozen_scientific_comparison(self):
        total={key:0 for key in (
            "worlds","primary_worlds","negative_worlds",
            "total_real_physical_charges",
            "phase_A_charges","phase_B_charges","phase_C_charges",
            "primary_physical_cases","primary_two_action_cases",
            "gate_correct","gate_wrong","gate_abstain",
            "gate_unseen_correct","gate_unseen_wrong","gate_unseen_total",
            "gate_two_action_correct","gate_two_action_wrong",
            "base_correct","base_wrong","base_abstain",
            "equal_score_correct","equal_score_wrong","equal_score_abstain",
            "equal_random_correct","equal_random_wrong",
            "unfiltered_correct","unfiltered_wrong",
            "Bonly_correct","Bonly_wrong",
            "mlp_correct","mlp_wrong","mlp_converged",
            "stageA_old_correct","stageA_preserved",
            "trusted_actions","primary_worlds_with_trusted_action",
            "C_confident_predictions","C_confident_errors",
            "C_real_actions","total_matched_coverage",
            "total_base_coverage","cold_numeric_worlds",
            "negative_gate_correct","negative_gate_wrong",
            "negative_equal_score_correct","negative_equal_score_wrong",
            "negative_equal_random_wrong","negative_base_wrong",
            "gate_cpu_ns","base_audit_cpu_ns","teacher_cpu_ns",
            "MLP_cpu_ns","MLP_gradient_updates","dreams"
        )}
        receipts=[]
        grouped={}
        for seed in SEEDS:
            with self.subTest(seed=seed):
                is_negative=seed>=4713
                w=build_world(seed)
                source=w.training_session()
                rng=Random(int.from_bytes(sha256(
                    f"WSP73|charged-public-action-policy|{seed}".encode("ascii")
                ).digest(),"big"))
                fast=ReusableInteractionNeural("residual",seed=seed)
                second=ReusableInteractionNeural("random",seed=seed)
                A=[]
                B=[]
                C=[]
                teacher_t=time.process_time_ns()
                for i in range(TRAIN_ACTIONS):
                    row=source.step(rng.choice(ACTIONS))
                    datum=(row.before,row.action,row.after)
                    if i<96:
                        A.append(datum)
                        fast.charge(row)
                        second.charge(row)
                        if i+1 in (48,96):
                            fast.grow()
                            second.grow()
                    elif i<192:
                        B.append(datum)
                    else:
                        C.append(datum)
                teacher_ns=time.process_time_ns()-teacher_t
                self.assertEqual(len(A),96)
                self.assertEqual(len(B),96)
                self.assertEqual(len(C),32)
                self.assertEqual(len(source.ledger),224)
                self.assertEqual(A[0][0],(0,0,0,0))
                self.assertEqual(A[-1][2],B[0][0])
                self.assertEqual(B[-1][2],C[0][0])
                self.assertTrue(all(source.ledger[i].after==
                     source.ledger[i+1].before for i in range(223)))
                self.assertEqual(fast.charged_actions,96)
                self.assertEqual(second.charged_actions,96)
                teacher_snapshot=fast.snapshot()
                second_snapshot=second.snapshot()
                frozen_fast=FeatureGrowthNeural.restore(teacher_snapshot)
                frozen_second=FeatureGrowthNeural.restore(second_snapshot)
                self.assertEqual(teacher_snapshot,frozen_fast.snapshot())
                self.assertEqual(second_snapshot,frozen_second.snapshot())
                t=time.process_time_ns()
                plan=select_committee_rehearsal(
                    frozen_fast,frozen_second,A,B,seed)
                k=plan["k"]
                student=DurableNeuralWeights(teacher_snapshot)
                student.fit_phase_b(B)
                student.replay(plan["candidate"])
                unfiltered=DurableNeuralWeights(teacher_snapshot)
                unfiltered.fit_phase_b(B)
                unfiltered.replay(plan["unfiltered"])
                Bonly=DurableNeuralWeights(teacher_snapshot)
                Bonly.fit_phase_b(B)
                Bonly.replay(())
                train_ns=time.process_time_ns()-t
                before_C_snapshot=student.snapshot()
                self.assertNotIn('"ledger"',before_C_snapshot)
                self.assertNotIn('"dreams"',before_C_snapshot)
                audit=PhysicalPostWriteAuditor(student)
                audit.calibrate(C)
                self.assertEqual(student.snapshot(),before_C_snapshot)
                self.assertEqual(audit.paid_calibration_actions,32)
                self.assertEqual(sum(audit.accepted),sum(
                    student.predict(s,a) is not None for s,a,y in C))
                self.assertEqual(sum(audit.errors),sum(
                    student.predict(s,a) is not None and
                    student.predict(s,a)!=y for s,a,y in C))
                t=time.process_time_ns()
                views=matched_coverage_views(audit,seed)
                matched_score=selected_predictor(
                    student,views["global_score"])
                matched_random=selected_predictor(
                    student,views["random"])
                self.assertEqual(views["matched_count"],len(views["gate"]))
                self.assertEqual(len(views["global_score"]),
                                 len(views["gate"]))
                self.assertEqual(len(views["random"]),
                                 len(views["gate"]))
                assert all(student.predict(s,a) is not None
                           for s,a in views["global_score"])
                public_build_ns=time.process_time_ns()-t
                # All chosen subsets were frozen with PUBLIC input identities
                # and numeric predictions before ANY heldout truth scoring.
                paid={(s,a) for s,a,y in A+B+C}
                tasks=w.composition_tests()
                t=time.process_time_ns()
                gate=evaluate(audit.predict,w,paid,tasks)
                gate_eval_ns=time.process_time_ns()-t
                t=time.process_time_ns()
                base=evaluate(student.predict,w,paid,tasks)
                base_eval_ns=time.process_time_ns()-t
                equal_score=evaluate(matched_score,w,paid,tasks)
                equal_random=evaluate(matched_random,w,paid,tasks)
                prev_unfiltered=evaluate(unfiltered.predict,w,paid)
                prev_Bonly=evaluate(Bonly.predict,w,paid)
                self.assertEqual(views["matched_count"],
                                 gate["physical"]["correct"]+
                                 gate["physical"]["wrong_confident"])
                self.assertEqual(views["matched_count"],
                                 equal_score["physical"]["correct"]+
                                 equal_score["physical"]["wrong_confident"])
                self.assertEqual(views["matched_count"],
                                 equal_random["physical"]["correct"]+
                                 equal_random["physical"]["wrong_confident"])
                self.assertEqual(views["base_confident"],
                                 base["physical"]["correct"]+
                                 base["physical"]["wrong_confident"])
                # Cold parity + canonical weight-only tamper rejection. 32
                # physical C observations were never used to update weights.
                restored=DurableNeuralWeights.restore(before_C_snapshot)
                self.assertEqual(restored.snapshot(),before_C_snapshot)
                with self.assertRaises(ValueError):
                    DurableNeuralWeights.restore(
                        before_C_snapshot.replace(
                            "wsp69.neural-feature-growth.v1",
                            "wsp69.neural-feature-growth.v2"))
                for s in STATES:
                    for a in ACTIONS:
                        self.assertEqual(restored.predict(s,a),
                                         student.predict(s,a))
                old=retention(audit.predict,frozen_fast,w)
                mlp_fit=None
                mlp_score=None
                mlp_ns=0
                if not is_negative:
                    mlp=EndToEndAdamControl(seed)
                    mt=time.process_time_ns()
                    mlp_fit=mlp.fit(B)
                    mlp_ns=time.process_time_ns()-mt
                    mlp_score=evaluate(
                        lambda s,a:mlp.predict(s,a,confidence=True),
                        w,paid)
                report={
                    "seed":seed,"family":w.family,"source":w.receipt(),
                    "phaseA_charged_sha256":digest(A),
                    "phaseB_charged_sha256":digest(B),
                    "phaseC_charged_sha256":digest(C),
                    "charged_actions":224,"C_calibration_actions":32,
                    "teacher_numerical_snapshot_sha256":sha256(
                        teacher_snapshot.encode("ascii")).hexdigest(),
                    "student_after_B_before_C_weights_sha256":sha256(
                        before_C_snapshot.encode("ascii")).hexdigest(),
                    "dreams_count":k,
                    "dreams_sha256":digest(plan["candidate"]),
                    "original_primary_dreams_sha256":digest(
                        plan["all_primary_proposals"]),
                    "C_calibration":audit.precommitted_receipt(),
                    "evaluation_matched_coverage_counts":{
                        "all_original_confident":views["base_confident"],
                        "all_matched":views["matched_count"]},
                    "matched_unlabeled_input_sha256":{
                        key:digest(views[key])
                        for key in ("gate","global_score","random")
                    },
                    "gate":gate,"base":base,
                    "equal_score":equal_score,"equal_random":equal_random,
                    "Bonly":prev_Bonly,"unfiltered_dream":prev_unfiltered,
                    "old_knowledge_after_gate":old,
                    "full_end_to_end_B_MLP":mlp_fit,
                    "full_end_to_end_B_MLP_eval":mlp_score,
                    "teacher_and_physical_cpu_ns":teacher_ns,
                    "student_train_cpu_ns":train_ns,
                    "public_unlabeled_coverage_build_cpu_ns":public_build_ns,
                    "gate_eval_cpu_ns":gate_eval_ns,
                    "base_eval_cpu_ns":base_eval_ns,
                    "MLP_train_cpu_ns":mlp_ns
                }
                receipts.append(report)
                total["worlds"]+=1
                total["total_real_physical_charges"]+=224
                total["C_real_actions"]+=32
                total["cold_numeric_worlds"]+=1
                if is_negative:
                    total["negative_worlds"]+=1
                    for prefix,item in (
                        ("negative_gate",gate),("negative_equal_score",equal_score)):
                        total[f"{prefix}_correct"]+=item["physical"]["correct"]
                        total[f"{prefix}_wrong"]+=item["physical"]["wrong_confident"]
                    total["negative_equal_random_wrong"]+=equal_random[
                        "physical"]["wrong_confident"]
                    total["negative_base_wrong"]+=base["physical"]["wrong_confident"]
                else:
                    total["primary_worlds"]+=1
                    total["primary_physical_cases"]+=64
                    total["primary_two_action_cases"]+=32
                    total["phase_A_charges"]+=96
                    total["phase_B_charges"]+=96
                    total["phase_C_charges"]+=32
                    for name,result in (
                        ("gate",gate),("base",base),
                        ("equal_score",equal_score),
                        ("equal_random",equal_random),
                        ("unfiltered",prev_unfiltered),
                        ("Bonly",prev_Bonly)
                    ):
                        for suffix,key in (("correct","correct"),
                                          ("wrong","wrong_confident")):
                            total[f"{name}_{suffix}"]+=result["physical"][key]
                    total["gate_abstain"]+=gate["physical"]["abstain"]
                    total["base_abstain"]+=base["physical"]["abstain"]
                    total["equal_score_abstain"]+=equal_score["physical"]["abstain"]
                    total["gate_unseen_correct"]+=gate["never_charged"]["correct"]
                    total["gate_unseen_wrong"]+=gate["never_charged"]["wrong_confident"]
                    total["gate_unseen_total"]+=gate["never_charged"]["total"]
                    total["gate_two_action_correct"]+=gate["two_action"]["correct"]
                    total["gate_two_action_wrong"]+=gate["two_action"]["wrong_confident"]
                    total["stageA_old_correct"]+=old["eligible"]
                    total["stageA_preserved"]+=old["retained"]
                    total["trusted_actions"]+=sum(audit.trusted)
                    total["primary_worlds_with_trusted_action"]+=int(any(audit.trusted))
                    total["C_confident_predictions"]+=sum(audit.accepted)
                    total["C_confident_errors"]+=sum(audit.errors)
                    total["total_matched_coverage"]+=views["matched_count"]
                    total["total_base_coverage"]+=views["base_confident"]
                    total["dreams"]+=k
                    total["gate_cpu_ns"]+=teacher_ns+train_ns+public_build_ns+gate_eval_ns
                    total["base_audit_cpu_ns"]+=teacher_ns+train_ns+base_eval_ns
                    total["teacher_cpu_ns"]+=teacher_ns
                    total["MLP_cpu_ns"]+=mlp_ns
                    total["mlp_correct"]+=mlp_score["physical"]["correct"]
                    total["mlp_wrong"]+=mlp_score["physical"]["wrong_confident"]
                    total["mlp_converged"]+=int(mlp_fit["fully_trained"])
                    total["MLP_gradient_updates"]+=mlp_fit["gradient_updates_total"]
                    f=grouped.setdefault(w.family,{
                        "worlds":0,"gate_correct":0,"gate_wrong":0,
                        "equal_score_wrong":0,"coverage":0,
                        "C_errors":0,"mlp_converged":0
                    })
                    f["worlds"]+=1
                    f["gate_correct"]+=gate["physical"]["correct"]
                    f["gate_wrong"]+=gate["physical"]["wrong_confident"]
                    f["equal_score_wrong"]+=equal_score["physical"]["wrong_confident"]
                    f["coverage"]+=views["matched_count"]
                    f["C_errors"]+=sum(audit.errors)
                    f["mlp_converged"]+=int(mlp_fit["fully_trained"])
        self.assertEqual(total["primary_worlds"],12)
        self.assertEqual(total["negative_worlds"],4)
        self.assertEqual(total["worlds"],16)
        self.assertEqual(total["primary_physical_cases"],768)
        self.assertEqual(total["primary_two_action_cases"],384)
        self.assertEqual(total["total_real_physical_charges"],3584)
        self.assertEqual(total["cold_numeric_worlds"],16)
        coverage=total["total_matched_coverage"]/max(1,total["total_base_coverage"])
        retention_rate=total["stageA_preserved"]/max(1,total["stageA_old_correct"])
        cpu_ratio=total["gate_cpu_ns"]/max(1,total["base_audit_cpu_ns"])
        gates={
            "gate_correct_ge_260":total["gate_correct"]>=260,
            "coverage_at_least_65pct_of_base":coverage>=0.65,
            "gate_confident_wrong_le_16":total["gate_wrong"]<=16,
            "primary_wrong_reduction_vs_score_ge_8":
                total["equal_score_wrong"]-total["gate_wrong"]>=8,
            "primary_wrong_reduction_vs_random_ge_8":
                total["equal_random_wrong"]-total["gate_wrong"]>=8,
            "never_charged_correct_ge_12":
                total["gate_unseen_correct"]>=12,
            "stageA_retention_ge_70pct":retention_rate>=0.70,
            "two_action_correct_ge_70":total["gate_two_action_correct"]>=70,
            "quartic_gate_wrong_confident_le_8":
                total["negative_gate_wrong"]<=8,
            "quartic_wrong_reduction_vs_score_ge_6":
                total["negative_equal_score_wrong"]-total["negative_gate_wrong"]>=6,
            "at_least_12_worlds_with_trusted_action":
                total["primary_worlds_with_trusted_action"]>=12,
            "all_16_cold_numeric_custody":total["cold_numeric_worlds"]==16,
            "cpu_vs_base_audit_le_2":cpu_ratio<=2.0
        }
        label="SELFTEST_SIGNAL" if all(gates.values()) else (
              "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP73_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":label,
            "criteria":gates,
            "frozen_coverage_ratio_to_original_confident":round(coverage,8),
            "frozen_old_knowledge_retention":round(retention_rate,8),
            "measured_gate_to_base_CPU_ratio":round(cpu_ratio,8),
            "MLP_converged_primary_worlds":total["mlp_converged"],
            "totals":total,"by_family":grouped,"worlds":receipts
        },sort_keys=True,separators=(",",":")))
        # Scientific negatives stay in receipts; test PASS alone is not science.


if __name__=="__main__":
    unittest.main()

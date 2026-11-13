"""WSP71 frozen no-gradient sleep-style teacher->durable neural consolidation.

Physical training: ONE uninterrupted 192-action source session per world.
Phase A 96 actions trains the unchanged source-blind WSP70 neural teacher,
with its original real neuron-growth milestones at 48 and 96. Phase B 96
actions is identical public evidence to all durable readout controls.
Offline dreamed labels are produced only by the cold teacher, never by
evaluator truths. The physical evaluator is used *solely after training* to
score 64 physical transitions and 32 fresh two-action compositions/world.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from pathlib import Path
from random import Random
import sys
import time
import json
import unittest

from source import SEEDS, STATES, ACTIONS, STAGE_A, TRAIN_ACTIONS, build_world
from consolidate import (
    DREAM_MAX, DurableNeuralWeights, select_rehearsal, visible_dreams
)
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"WSP-70"))
from interaction_writer import ReusableInteractionNeural
sys.path.insert(0,str(ROOT/"WSP-69"))
from growing_neural import FeatureGrowthNeural
from end_to_end_control import EndToEndAdamControl
sys.path.insert(0,str(ROOT/"WSP-67"))
from independent_symbolic import ExactMemory


def digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,
                  separators=(",",":"),default=list).encode("ascii")).hexdigest()


def evaluate(predict,world,seen_all,compositions=None):
    count={"correct":0,"wrong_confident":0,"abstain":0}
    unseen={"correct":0,"wrong_confident":0,"abstain":0,"total":0}
    for state in STATES:
        for action in ACTIONS:
            pred=predict(state,action)
            truth=world._step_oracle(state,action)
            key="abstain" if pred is None else (
                "correct" if pred==truth else "wrong_confident"
            )
            count[key]+=1
            if (state,action) not in seen_all:
                unseen[key]+=1
                unseen["total"]+=1
    assert sum(count.values())==64
    assert unseen["correct"]+unseen["wrong_confident"]+unseen["abstain"]==unseen["total"]
    out={"physical":count,"never_charged":unseen}
    if compositions is not None:
        comp={"correct":0,"wrong_confident":0,"abstain":0}
        for case in compositions:
            a,b=case.actions
            mid=predict(case.start,a)
            final=predict(mid,b) if mid is not None else None
            k="abstain" if final is None else (
                "correct" if final==case._finish else "wrong_confident")
            comp[k]+=1
        assert sum(comp.values())==len(compositions)
        out["two_action"]=comp
    return out


def retention(predict,old_teacher,world):
    eligible=retained=0
    for state in STATES:
        for action in ACTIONS:
            old=old_teacher.predict(state,action)
            if old is not None and old==world._step_oracle(state,action):
                eligible+=1
                retained+=int(predict(state,action)==old)
    return {"stageA_eligible":eligible,"retained":retained}


class FrozenSleepConsolidation(unittest.TestCase):
    def test_no_source_in_neural_module_and_no_protected_first_use(self):
        text=(Path(__file__).parent/"consolidate.py").read_text("utf-8")
        for forbidden in ("from source import","import source",
                          "_step_oracle","from weight_programmer import",
                          "torch","backward(","gradient_step"):
            self.assertNotIn(forbidden,text)
        self.assertEqual(DREAM_MAX,32)
        self.assertEqual(StageA:=STAGE_A,96)
        self.assertEqual(TRAIN_ACTIONS,192)
        self.assertEqual(len(SEEDS),14)
        self.assertEqual(DurableNeuralWeights.gradient_updates,0)
        for cohort in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(SEEDS[0],cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(4401)
        for seed in SEEDS:
            w=build_world(seed)
            self.assertEqual(w.receipt(),build_world(seed).receipt())
            self.assertEqual(len(w.composition_tests()),32)
        w=build_world(SEEDS[0])
        session=w.training_session()
        self.assertEqual(session.state,(0,0,0,0))
        for i in range(TRAIN_ACTIONS):
            session.step(i%4)
        with self.assertRaises(ValueError):
            session.step(0)
        self.assertEqual(len(session.ledger),TRAIN_ACTIONS)

    def test_frozen_weight_only_teacher_to_student_results(self):
        total={
            "primary_worlds":0,"negative_worlds":0,
            "total_physical_actions":0,"phaseA_charged":0,
            "phaseB_charged":0,"physical_eval":0,
            "two_action_eval":0,
            "dream_correct":0,"dream_wrong":0,"dream_attempted":0,
            "dream_count":0,"worlds_with_dreams":0,
            "candidate_correct":0,"candidate_wrong":0,
            "candidate_abstain":0,"candidate_never_charged_correct":0,
            "candidate_never_charged_wrong":0,
            "candidate_never_charged_total":0,
            "candidate_two_action_correct":0,
            "candidate_two_action_wrong":0,
            "repeat_correct":0,"repeat_wrong":0,
            "repeat_never_charged_correct":0,
            "repeat_two_action_correct":0,
            "trueA_correct":0,"trueA_wrong":0,
            "B_only_correct":0,"B_only_wrong":0,
            "corrupted_dream_correct":0,"corrupted_dream_wrong":0,
            "teacher_correct":0,"teacher_wrong":0,
            "mlp_correct":0,"mlp_wrong":0,
            "mlp_converged_worlds":0,"mlp_gradient_updates":0,
            "stageA_eligible":0,"candidate_retained":0,
            "repeat_retained":0,"trueA_retained":0,
            "B_only_retained":0,
            "cold_neural_snapshots":0,
            "candidate_cpu_ns":0,"repeat_cpu_ns":0,
            "teacher_cpu_ns":0,"mlp_cpu_ns":0,
            "quartic_candidate_wrong":0,
            "quartic_candidate_correct":0
        }
        records=[]
        by_family={}
        for seed in SEEDS:
            with self.subTest(seed=seed):
                negative=seed>=4513
                w=build_world(seed)
                source=w.training_session()
                rng=Random(int.from_bytes(sha256(
                    f"WSP71|continuous-public-physical-actions|{seed}".encode("ascii")
                ).digest(),"big"))
                teacher=ReusableInteractionNeural(policy="residual",seed=seed)
                raw_a=[]
                raw_b=[]
                teacher_start=time.process_time_ns()
                for i in range(TRAIN_ACTIONS):
                    row=source.step(rng.choice(ACTIONS))
                    datum=(row.before,row.action,row.after)
                    if i<STAGE_A:
                        teacher.charge(row)
                        raw_a.append(datum)
                        if i+1 in (48,96):
                            teacher.grow()
                        if i+1==STAGE_A:
                            teacher_snapshot=teacher.snapshot()
                    else:
                        raw_b.append(datum)
                teacher_cpu=time.process_time_ns()-teacher_start
                self.assertEqual(len(raw_a),96)
                self.assertEqual(len(raw_b),96)
                self.assertEqual(len(source.ledger),192)
                self.assertEqual(raw_a[0][0],(0,0,0,0))
                self.assertEqual(raw_a[-1][2],raw_b[0][0])
                self.assertTrue(all(source.ledger[i].after==source.ledger[i+1].before
                                    for i in range(TRAIN_ACTIONS-1)))
                self.assertEqual(teacher.charged_actions,96)
                self.assertEqual(len(teacher.centers),24)
                cold_teacher=FeatureGrowthNeural.restore(teacher_snapshot)
                self.assertEqual(teacher_snapshot,cold_teacher.snapshot())
                self.assertNotIn('"ledger"',teacher_snapshot)
                # No evaluator labels or hidden roles accessed by neural models.
                t=time.process_time_ns()
                replay=select_rehearsal(cold_teacher,raw_a,raw_b,seed)
                dream_selection_cpu=time.process_time_ns()-t
                k=replay["k"]
                self.assertLessEqual(k,DREAM_MAX)
                self.assertEqual(len(replay["dreams"]),k)
                self.assertEqual(len(replay["B_repeats"]),k)
                self.assertEqual(len(replay["stored_A"]),k)
                self.assertEqual(len(replay["scrambled_dreams"]),k)
                students={}
                student_cpu={}
                for mode,extra in (
                    ("candidate",replay["dreams"]),
                    ("repeat",replay["B_repeats"]),
                    ("trueA",replay["stored_A"]),
                    ("B_only",()),
                    ("corrupted_dream",replay["scrambled_dreams"])
                ):
                    t=time.process_time_ns()
                    student=DurableNeuralWeights(teacher_snapshot)
                    student.fit_phase_b(raw_b)
                    student.replay(extra)
                    student_cpu[mode]=time.process_time_ns()-t
                    self.assertEqual(student.physical_rows,96)
                    self.assertEqual(student.rehearsal_rows,len(extra))
                    self.assertEqual(student.weight_edit_count,96+len(extra))
                    students[mode]=student
                # Attribution: all arms pay the SAME Stage-A teacher construction,
                # and candidate additionally pays source-free dreamed-query CPU.
                candidate_cpu=teacher_cpu+dream_selection_cpu+student_cpu["candidate"]
                repeat_cpu=teacher_cpu+student_cpu["repeat"]
                model_bytes={}
                for mode,student in students.items():
                    snapshot=student.snapshot()
                    cold=DurableNeuralWeights.restore(snapshot)
                    self.assertEqual(cold.snapshot(),snapshot)
                    self.assertNotIn('"ledger"',snapshot)
                    self.assertNotIn('"dreams"',snapshot)
                    with self.assertRaises(ValueError):
                        DurableNeuralWeights.restore(snapshot.replace(
                            "wsp69.neural-feature-growth.v1",
                            "wsp69.neural-feature-growth.v2"))
                    self.assertEqual(student.model.hidden_weights,
                                     cold.hidden_weights)
                    for s in STATES:
                        for a in ACTIONS:
                            self.assertEqual(cold.predict(s,a),
                                             student.predict(s,a))
                    model_bytes[mode]=len(snapshot.encode("ascii"))
                if not negative:
                    total["cold_neural_snapshots"]+=1
                seen_all={(s,a) for s,a,y in raw_a+raw_b}
                tasks=w.composition_tests()
                diagnostics={}
                stability={}
                for mode,student in students.items():
                    t=time.process_time_ns()
                    diagnostics[mode]=evaluate(student.predict,w,seen_all,tasks)
                    if mode=="candidate":
                        candidate_cpu+=time.process_time_ns()-t
                    if mode=="repeat":
                        repeat_cpu+=time.process_time_ns()-t
                    stability[mode]=retention(student.predict,cold_teacher,w)
                teacher_diag=evaluate(cold_teacher.predict,w,seen_all,tasks)
                teacher_retain=stability["candidate"]["stageA_eligible"]
                self.assertEqual(teacher_retain,
                                 stability["repeat"]["stageA_eligible"])
                pseudo_truth={
                    "correct":sum(int(y==w._step_oracle(s,a))
                                  for s,a,y in replay["dreams"]),
                    "total":k
                }
                pseudo_truth["wrong"]=k-pseudo_truth["correct"]
                # Labels checked evaluator-only AFTER all students are trained.
                mlp_results=None
                mlp_fit=None
                mlp_cpu=0
                if not negative:
                    from end_to_end_control import EndToEndAdamControl
                    mlp=EndToEndAdamControl(seed)
                    t=time.process_time_ns()
                    mlp_fit=mlp.fit(raw_b)
                    mlp_cpu=time.process_time_ns()-t
                    mlp_results=evaluate(
                        lambda s,a:mlp.predict(s,a,confidence=True),
                        w,seen_all)
                self.assertEqual(sum(diagnostics["candidate"]["physical"].values()),64)
                if not negative:
                    total["primary_worlds"]+=1
                    total["total_physical_actions"]+=192
                    total["phaseA_charged"]+=96
                    total["phaseB_charged"]+=96
                    total["physical_eval"]+=64
                    total["two_action_eval"]+=32
                    total["dream_correct"]+=pseudo_truth["correct"]
                    total["dream_wrong"]+=pseudo_truth["wrong"]
                    total["dream_attempted"]+=replay["teacher_query_count"]
                    total["dream_count"]+=k
                    total["worlds_with_dreams"]+=int(k>0)
                    total["teacher_correct"]+=teacher_diag["physical"]["correct"]
                    total["teacher_wrong"]+=teacher_diag["physical"]["wrong_confident"]
                    for mode,key in (("candidate","candidate"),("repeat","repeat"),
                                     ("trueA","trueA"),("B_only","B_only"),
                                     ("corrupted_dream","corrupted_dream")):
                        total[f"{key}_correct"]+=diagnostics[mode]["physical"]["correct"]
                        total[f"{key}_wrong"]+=diagnostics[mode]["physical"]["wrong_confident"]
                    total["candidate_abstain"]+=diagnostics["candidate"]["physical"]["abstain"]
                    total["candidate_never_charged_correct"]+=diagnostics["candidate"]["never_charged"]["correct"]
                    total["candidate_never_charged_wrong"]+=diagnostics["candidate"]["never_charged"]["wrong_confident"]
                    total["candidate_never_charged_total"]+=diagnostics["candidate"]["never_charged"]["total"]
                    total["candidate_two_action_correct"]+=diagnostics["candidate"]["two_action"]["correct"]
                    total["candidate_two_action_wrong"]+=diagnostics["candidate"]["two_action"]["wrong_confident"]
                    total["repeat_never_charged_correct"]+=diagnostics["repeat"]["never_charged"]["correct"]
                    total["repeat_two_action_correct"]+=diagnostics["repeat"]["two_action"]["correct"]
                    total["stageA_eligible"]+=teacher_retain
                    for mode,key in (("candidate","candidate"),("repeat","repeat"),
                                     ("trueA","trueA"),("B_only","B_only")):
                        total[f"{key}_retained"]+=stability[mode]["retained"]
                    total["mlp_correct"]+=mlp_results["physical"]["correct"]
                    total["mlp_wrong"]+=mlp_results["physical"]["wrong_confident"]
                    total["mlp_converged_worlds"]+=int(mlp_fit["fully_trained"])
                    total["mlp_gradient_updates"]+=mlp_fit["gradient_updates_total"]
                    total["candidate_cpu_ns"]+=candidate_cpu
                    total["repeat_cpu_ns"]+=repeat_cpu
                    total["teacher_cpu_ns"]+=teacher_cpu
                    total["mlp_cpu_ns"]+=mlp_cpu
                    group=by_family.setdefault(w.family,{
                        "worlds":0,"candidate_correct":0,"repeat_correct":0,
                        "candidate_unseen":0,"repeat_unseen":0,
                        "candidate_wrong":0,"repeat_wrong":0,
                        "teacher_dream_correct":0,"teacher_dream_count":0,
                        "mlp_converged":0
                    })
                    group["worlds"]+=1
                    group["candidate_correct"]+=diagnostics["candidate"]["physical"]["correct"]
                    group["repeat_correct"]+=diagnostics["repeat"]["physical"]["correct"]
                    group["candidate_unseen"]+=diagnostics["candidate"]["never_charged"]["correct"]
                    group["repeat_unseen"]+=diagnostics["repeat"]["never_charged"]["correct"]
                    group["candidate_wrong"]+=diagnostics["candidate"]["physical"]["wrong_confident"]
                    group["repeat_wrong"]+=diagnostics["repeat"]["physical"]["wrong_confident"]
                    group["teacher_dream_correct"]+=pseudo_truth["correct"]
                    group["teacher_dream_count"]+=k
                    group["mlp_converged"]+=int(mlp_fit["fully_trained"])
                else:
                    total["negative_worlds"]+=1
                    total["quartic_candidate_correct"]+=diagnostics["candidate"]["physical"]["correct"]
                    total["quartic_candidate_wrong"]+=diagnostics["candidate"]["physical"]["wrong_confident"]
                records.append({
                    "seed":seed,"family":w.family,
                    "source":w.receipt(),
                    "phaseA_charged_sha256":digest(raw_a),
                    "phaseB_charged_sha256":digest(raw_b),
                    "all_physical_actions":192,
                    "teacher_neural_snapshot_sha256":sha256(
                        teacher_snapshot.encode("ascii")).hexdigest(),
                    "dream_receipts_sha256":digest(replay["dreams"]),
                    "rehearsal_budget_k":k,
                    "dream_teacher_attempts":replay["teacher_query_count"],
                    "teacher_confident_candidates":replay["teacher_confident_candidate_count"],
                    "charged_A_unique_contexts":replay["actual_A_distinct"],
                    "dream_labels_private_audit":pseudo_truth,
                    "teacher_audit":teacher_diag,
                    "student_audits":diagnostics,
                    "stageA_knowledge_retention":stability,
                    "numerical_snapshot_bytes":model_bytes,
                    "student_weight_edit_steps":{
                        key:value.weight_edit_count for key,value in students.items()},
                    "student_stageB_physical_action_count":96,
                    "teacher_cpu_ns":teacher_cpu,
                    "dream_selection_cpu_ns":dream_selection_cpu,
                    "candidate_cpu_ns":candidate_cpu,
                    "repeat_cpu_ns":repeat_cpu,
                    "mlp_cpu_ns":mlp_cpu,
                    "fully_trained_B_neural_baseline":mlp_fit,
                    "mlp_physical_audit":mlp_results
                })
        self.assertEqual(total["primary_worlds"],12)
        self.assertEqual(total["negative_worlds"],2)
        self.assertEqual(total["physical_eval"],768)
        self.assertEqual(total["two_action_eval"],384)
        self.assertEqual(total["total_physical_actions"],2304)
        self.assertEqual(total["cold_neural_snapshots"],12)
        retain=total["candidate_retained"]/max(1,total["stageA_eligible"])
        dream_accuracy=total["dream_correct"]/max(1,total["dream_count"])
        cpu_ratio=total["candidate_cpu_ns"]/max(1,total["repeat_cpu_ns"])
        gates={
            "candidate_correct_ge_260":total["candidate_correct"]>=260,
            "gain_vs_B_repeats_ge_20":
                total["candidate_correct"]-total["repeat_correct"]>=20,
            "stageA_retention_ge_82pct":retain>=0.82,
            "stageA_retained_gain_vs_repeat_ge_15":
                total["candidate_retained"]-total["repeat_retained"]>=15,
            "never_physically_charged_correct_ge_18":
                total["candidate_never_charged_correct"]>=18,
            "confident_wrong_le_24":total["candidate_wrong"]<=24,
            "two_action_correct_ge_100":
                total["candidate_two_action_correct"]>=100,
            "teacher_dream_truth_ge_85pct":dream_accuracy>=0.85,
            "nonzero_dream_worlds_ge_10":
                total["worlds_with_dreams"]>=10,
            "cold_matrix_parity_tamper_worlds_12":
                total["cold_neural_snapshots"]==12,
            "measured_cpu_ratio_le_2":cpu_ratio<=2.0,
            "quartic_confident_wrong_le_6":
                total["quartic_candidate_wrong"]<=6
        }
        result="SELFTEST_SIGNAL" if all(gates.values()) else (
            "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP71_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":result,"criteria":gates,
            "retention_rate":round(retain,8),
            "dream_truth_rate":round(dream_accuracy,8),
            "candidate_over_repeat_cpu_ratio":round(cpu_ratio,7),
            "qualified_end_to_end_MLP_worlds":total["mlp_converged_worlds"],
            "totals":total,"by_family":by_family,"worlds":records
        },sort_keys=True,separators=(",",":")))
        # Frozen failures are data, not assertions or invitations to retune.


if __name__=="__main__":
    unittest.main()

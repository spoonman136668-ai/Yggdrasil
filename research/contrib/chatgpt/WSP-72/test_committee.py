"""WSP72 prospectively frozen neural-pseudolabel trust and weight consolidation.

Two differently grown DIRECT NUMERICAL Stage A neural teachers, trained
only on the same 96 charged public actions, make teacher labels. A second
teacher's confident agreement plus a no-contradiction check against only
96 separately charged B actions selects k pseudo labels. Same-k ungated
teacher predictions are drawn from the identical primary proposals.

All learned models share the identical teacher hidden weights and Phase B
charged labels; output edits are rank-one ridge, no gradients. Source
oracle truth is used in THIS evaluator test only after all models trained.
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
from committee import select_committee_rehearsal,DurableNeuralWeights,DREAM_MAX

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"WSP-70"))
from interaction_writer import ReusableInteractionNeural
sys.path.insert(0,str(ROOT/"WSP-69"))
from growing_neural import FeatureGrowthNeural
from end_to_end_control import EndToEndAdamControl


def digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,
        separators=(",",":"),default=list).encode("ascii")).hexdigest()


def evaluate(predict,world,seen,compositions=None):
    count={"correct":0,"wrong_confident":0,"abstain":0}
    unseen={"correct":0,"wrong_confident":0,"abstain":0,"total":0}
    for state in STATES:
        for action in ACTIONS:
            out=predict(state,action)
            actual=world._step_oracle(state,action)
            key=("abstain" if out is None else
                 "correct" if out==actual else "wrong_confident")
            count[key]+=1
            if (state,action) not in seen:
                unseen[key]+=1
                unseen["total"]+=1
    assert sum(count.values())==64
    assert sum(v for k,v in unseen.items() if k!="total")==unseen["total"]
    result={"physical":count,"never_charged":unseen}
    if compositions is not None:
        composed={"correct":0,"wrong_confident":0,"abstain":0}
        for c in compositions:
            a,b=c.actions
            mid=predict(c.start,a)
            out=predict(mid,b) if mid is not None else None
            key=("abstain" if out is None else
                 "correct" if out==c._finish else "wrong_confident")
            composed[key]+=1
        assert sum(composed.values())==len(compositions)
        result["two_action"]=composed
    return result


def retained(predict,old,world):
    count=kept=0
    for s in STATES:
        for a in ACTIONS:
            earlier=old.predict(s,a)
            if earlier is not None and earlier==world._step_oracle(s,a):
                count+=1
                kept+=int(predict(s,a)==earlier)
    return {"stageA_eligible":count,"retained":kept}


class FrozenTeacherTrustVsEqualDreamCount(unittest.TestCase):
    def test_source_blindness_and_negative_trust_checks(self):
        code=(Path(__file__).parent/"committee.py").read_text("utf-8")
        for forbidden in ("from source import","import source",
                          "_step_oracle","from weight_programmer import",
                          "torch","backward("):
            self.assertNotIn(forbidden,code)
        self.assertEqual(len(SEEDS),16)
        self.assertEqual(STAGE_A,96)
        self.assertEqual(TRAIN_ACTIONS,192)
        self.assertEqual(DREAM_MAX,32)
        self.assertEqual(DurableNeuralWeights.gradient_updates,0)
        for seed in SEEDS:
            w=build_world(seed)
            self.assertEqual(w.receipt(),build_world(seed).receipt())
            self.assertEqual(len(w.composition_tests()),32)
        for bad in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(4601,cohort=bad)
        with self.assertRaises(PermissionError):
            build_world(4501)
        # Mock teachers demonstrate that a disagreeing second model cannot
        # force an unsupported hypothesis into the durable weight model.
        class ConstantTeacher:
            def __init__(self,y):
                self.y=y
            def predict(self,s,a):
                return self.y
        A=[((0,0,0,0),0,(0,0,0,0))]*96
        B=[((0,0,0,0),0,(0,0,0,0))]*96
        x=select_committee_rehearsal(
            ConstantTeacher((0,0,0,0)),
            ConstantTeacher((1,1,1,1)),A,B,4601)
        self.assertEqual(x["k"],0)
        self.assertEqual(len(x["candidate"]),0)
        self.assertEqual(len(x["unfiltered"]),0)
        self.assertGreater(x["secondary_disagreement_count"],0)
        for i in range(TRAIN_ACTIONS):
            if i==0:
                session=build_world(4601).training_session()
            session.step(i%4)
        self.assertEqual(len(session.ledger),192)
        with self.assertRaises(ValueError):
            session.step(0)

    def test_fresh_worlds_weight_rehearsal_and_frozen_risk_criterion(self):
        total={name:0 for name in (
            "primary_worlds","negative_worlds","charged_actions",
            "primary_physical","primary_compositions",
            "candidate_correct","candidate_wrong","candidate_abstain",
            "candidate_unseen_correct","candidate_unseen_wrong",
            "candidate_unseen_total","candidate_two_action_correct",
            "candidate_two_action_wrong",
            "unfiltered_correct","unfiltered_wrong","unfiltered_abstain",
            "unfiltered_unseen_correct","unfiltered_two_action_correct",
            "B_repeat_correct","B_repeat_wrong","true_A_correct",
            "true_A_wrong","B_only_correct","B_only_wrong",
            "scrambled_correct","scrambled_wrong","teacher_correct",
            "teacher_wrong","independent_correct","independent_wrong",
            "stageA_eligible","candidate_retained","unfiltered_retained",
            "B_repeat_retained","true_A_retained",
            "selected_pseudo_correct","selected_pseudo_wrong",
            "unfiltered_pseudo_correct","unfiltered_pseudo_wrong",
            "original_primary_proposal_count",
            "committee_disagreements","B_contradictions","dream_attempts",
            "dream_count","worlds_k_ge_8",
            "cold_restore_tamper_worlds",
            "candidate_cpu_ns","unfiltered_cpu_ns",
            "mlp_correct","mlp_wrong","mlp_converged",
            "mlp_gradient_updates","mlp_cpu_ns",
            "negative_candidate_wrong","negative_unfiltered_wrong",
            "negative_candidate_correct","negative_unfiltered_correct"
        )}
        reports=[]
        family={}
        for seed in SEEDS:
            with self.subTest(seed=seed):
                is_negative=seed>=4613
                world=build_world(seed)
                physical=world.training_session()
                rng=Random(int.from_bytes(sha256(
                    f"WSP72|no-reset-sequential-action|{seed}".encode("ascii")
                ).digest(),"big"))
                fast=ReusableInteractionNeural("residual",seed=seed)
                other=ReusableInteractionNeural("random",seed=seed)
                A=[]
                B=[]
                start_cpu=time.process_time_ns()
                for idx in range(TRAIN_ACTIONS):
                    row=physical.step(rng.choice(ACTIONS))
                    data=(row.before,row.action,row.after)
                    if idx<STAGE_A:
                        fast.charge(row)
                        other.charge(row)
                        A.append(data)
                        if idx+1 in (48,96):
                            fast.grow()
                            other.grow()
                    else:
                        B.append(data)
                teacher_cpu=time.process_time_ns()-start_cpu
                self.assertEqual(len(A),96)
                self.assertEqual(len(B),96)
                self.assertEqual(len(physical.ledger),192)
                self.assertEqual(A[0][0],(0,0,0,0))
                self.assertEqual(A[-1][2],B[0][0])
                self.assertTrue(all(physical.ledger[i].after==
                                    physical.ledger[i+1].before
                                    for i in range(TRAIN_ACTIONS-1)))
                self.assertEqual(fast.charged_actions,96)
                self.assertEqual(other.charged_actions,96)
                self.assertEqual(len(fast.hidden_weights),
                                 len(other.hidden_weights))
                # Independent selection policies need not always select
                # different features. Record observed disagreement as data.
                fast_snapshot=fast.snapshot()
                other_snapshot=other.snapshot()
                frozen_fast=FeatureGrowthNeural.restore(fast_snapshot)
                frozen_other=FeatureGrowthNeural.restore(other_snapshot)
                self.assertEqual(frozen_fast.snapshot(),fast_snapshot)
                self.assertEqual(frozen_other.snapshot(),other_snapshot)
                t=time.process_time_ns()
                plan=select_committee_rehearsal(
                    frozen_fast,frozen_other,A,B,seed)
                selection_ns=time.process_time_ns()-t
                k=plan["k"]
                self.assertEqual(
                    set(plan),{"k","candidate","unfiltered","true_A",
                        "B_repeat","scrambled","all_primary_proposals",
                        "candidate_proposals_agreed",
                        "secondary_disagreement_count",
                        "charged_B_contradiction_count",
                        "primary_queries","secondary_queries",
                        "distinct_charged_A","distinct_charged_B"})
                self.assertEqual(len(plan["candidate"]),k)
                self.assertEqual(len(plan["unfiltered"]),k)
                self.assertEqual(len(plan["true_A"]),k)
                self.assertEqual(len(plan["B_repeat"]),k)
                self.assertEqual(len(plan["scrambled"]),k)
                self.assertLessEqual(k,32)
                for s,a,y in plan["candidate"]:
                    self.assertEqual(frozen_fast.predict(s,a),y)
                    self.assertEqual(frozen_other.predict(s,a),y)
                existing_B={(s,a):y for s,a,y in B}
                self.assertTrue(all((s,a) not in existing_B or
                                    existing_B[(s,a)]==y
                                    for s,a,y in plan["candidate"]))
                students={}
                cpu={}
                for name,replays in (
                    ("candidate",plan["candidate"]),
                    ("unfiltered",plan["unfiltered"]),
                    ("B_repeat",plan["B_repeat"]),
                    ("true_A",plan["true_A"]),
                    ("B_only",tuple()),
                    ("scrambled",plan["scrambled"])
                ):
                    t=time.process_time_ns()
                    m=DurableNeuralWeights(fast_snapshot)
                    m.fit_phase_b(B)
                    m.replay(replays)
                    cpu[name]=time.process_time_ns()-t
                    self.assertEqual(m.physical_rows,96)
                    self.assertEqual(m.rehearsal_rows,len(replays))
                    self.assertEqual(m.weight_edit_count,96+len(replays))
                    students[name]=m
                seen={(s,a) for s,a,y in A+B}
                composed=world.composition_tests()
                scores={}
                retentions={}
                for name,m in students.items():
                    scores[name]=evaluate(m.predict,world,seen,composed)
                    retentions[name]=retained(m.predict,frozen_fast,world)
                fast_scores=evaluate(frozen_fast.predict,world,seen,composed)
                other_scores=evaluate(frozen_other.predict,world,seen,composed)
                self.assertEqual(retentions["candidate"]["stageA_eligible"],
                                 retentions["unfiltered"]["stageA_eligible"])
                self.assertEqual(retentions["candidate"]["stageA_eligible"],
                                 retentions["B_repeat"]["stageA_eligible"])
                for name in ("candidate","unfiltered","B_repeat",
                             "true_A","B_only","scrambled"):
                    snap=students[name].snapshot()
                    self.assertNotIn('"ledger"',snap)
                    self.assertNotIn('"dreams"',snap)
                    clone=DurableNeuralWeights.restore(snap)
                    self.assertEqual(clone.snapshot(),snap)
                    for s in STATES:
                        for a in ACTIONS:
                            self.assertEqual(clone.predict(s,a),
                                             students[name].predict(s,a))
                    with self.assertRaises(ValueError):
                        DurableNeuralWeights.restore(snap.replace(
                            "wsp69.neural-feature-growth.v1",
                            "wsp69.neural-feature-growth.v2"))
                primary_truth=sum(int(y==world._step_oracle(s,a))
                    for s,a,y in plan["candidate"])
                baseline_truth=sum(int(y==world._step_oracle(s,a))
                    for s,a,y in plan["unfiltered"])
                # Crucial: evaluator truth and dream-label accuracy are
                # accessed ONLY here, after all student weights are frozen.
                shared_teacher_and_selection=teacher_cpu+selection_ns
                candidate_cpu=shared_teacher_and_selection+cpu["candidate"]
                baseline_cpu=shared_teacher_and_selection+cpu["unfiltered"]
                # Cost all model evaluation uniformly; measure the different
                # inference time separately from student updates.
                t=time.process_time_ns()
                evaluate(students["candidate"].predict,world,seen,composed)
                candidate_cpu+=time.process_time_ns()-t
                t=time.process_time_ns()
                evaluate(students["unfiltered"].predict,world,seen,composed)
                baseline_cpu+=time.process_time_ns()-t
                mlp_fit=mlp_scores=None
                mlp_ns=0
                if not is_negative:
                    mlp=EndToEndAdamControl(seed)
                    t=time.process_time_ns()
                    mlp_fit=mlp.fit(B)
                    mlp_ns=time.process_time_ns()-t
                    mlp_scores=evaluate(
                        lambda s,a:mlp.predict(s,a,confidence=True),
                        world,seen)
                record={
                    "seed":seed,"family":world.family,
                    "source":world.receipt(),
                    "phaseA_charged_sha256":digest(A),
                    "phaseB_charged_sha256":digest(B),
                    "physical_actions":192,"replay_k":k,
                    "fast_numeric_snapshot_sha256":sha256(
                        fast_snapshot.encode("ascii")).hexdigest(),
                    "other_numeric_snapshot_sha256":sha256(
                        other_snapshot.encode("ascii")).hexdigest(),
                    "selected_pseudolabel_sha256":digest(plan["candidate"]),
                    "unfiltered_pseudolabel_sha256":digest(plan["unfiltered"]),
                    "original_proposals_sha256":digest(
                        plan["all_primary_proposals"]),
                    "dream_query_counts":[
                        plan["primary_queries"],plan["secondary_queries"]],
                    "committee_agreed_count":plan["candidate_proposals_agreed"],
                    "committee_disagreement_count":plan[
                        "secondary_disagreement_count"],
                    "charged_B_contradiction_count":plan[
                        "charged_B_contradiction_count"],
                    "dream_truth_private":{
                        "accepted_correct":primary_truth,
                        "accepted_wrong":k-primary_truth,
                        "unfiltered_correct":baseline_truth,
                        "unfiltered_wrong":k-baseline_truth
                    },
                    "scores":scores,"retention":retentions,
                    "teacher":fast_scores,"second_teacher":other_scores,
                    "durable_snapshot_bytes":{
                        key:students[key].snapshot_bytes()
                        for key in students},
                    "candidate_cpu_ns":candidate_cpu,
                    "baseline_cpu_ns":baseline_cpu,
                    "student_update_cpu_ns":cpu,
                    "teacher_cpu_ns":teacher_cpu,
                    "selector_cpu_ns":selection_ns,
                    "mlp_train":mlp_fit,"mlp_scoring":mlp_scores,
                    "mlp_cpu_ns":mlp_ns
                }
                reports.append(record)
                if is_negative:
                    total["negative_worlds"]+=1
                    total["negative_candidate_wrong"]+=scores[
                        "candidate"]["physical"]["wrong_confident"]
                    total["negative_unfiltered_wrong"]+=scores[
                        "unfiltered"]["physical"]["wrong_confident"]
                    total["negative_candidate_correct"]+=scores[
                        "candidate"]["physical"]["correct"]
                    total["negative_unfiltered_correct"]+=scores[
                        "unfiltered"]["physical"]["correct"]
                else:
                    total["primary_worlds"]+=1
                    total["primary_physical"]+=64
                    total["primary_compositions"]+=32
                    total["mlp_correct"]+=mlp_scores["physical"]["correct"]
                    total["mlp_wrong"]+=mlp_scores["physical"]["wrong_confident"]
                    total["mlp_converged"]+=int(mlp_fit["fully_trained"])
                    total["mlp_gradient_updates"]+=mlp_fit["gradient_updates_total"]
                    total["mlp_cpu_ns"]+=mlp_ns
                    for key,metric in (
                        ("candidate","candidate"),
                        ("unfiltered","unfiltered"),
                        ("B_repeat","B_repeat"),
                        ("true_A","true_A"),
                        ("B_only","B_only"),
                        ("scrambled","scrambled")
                    ):
                        total[f"{metric}_correct"]+=scores[key]["physical"]["correct"]
                        total[f"{metric}_wrong"]+=scores[key]["physical"]["wrong_confident"]
                    total["candidate_abstain"]+=scores["candidate"]["physical"]["abstain"]
                    total["unfiltered_abstain"]+=scores["unfiltered"]["physical"]["abstain"]
                    total["candidate_unseen_correct"]+=scores["candidate"]["never_charged"]["correct"]
                    total["candidate_unseen_wrong"]+=scores["candidate"]["never_charged"]["wrong_confident"]
                    total["candidate_unseen_total"]+=scores["candidate"]["never_charged"]["total"]
                    total["unfiltered_unseen_correct"]+=scores["unfiltered"]["never_charged"]["correct"]
                    total["candidate_two_action_correct"]+=scores["candidate"]["two_action"]["correct"]
                    total["candidate_two_action_wrong"]+=scores["candidate"]["two_action"]["wrong_confident"]
                    total["unfiltered_two_action_correct"]+=scores["unfiltered"]["two_action"]["correct"]
                    total["stageA_eligible"]+=retentions["candidate"]["stageA_eligible"]
                    total["candidate_retained"]+=retentions["candidate"]["retained"]
                    total["unfiltered_retained"]+=retentions["unfiltered"]["retained"]
                    total["B_repeat_retained"]+=retentions["B_repeat"]["retained"]
                    total["true_A_retained"]+=retentions["true_A"]["retained"]
                    total["selected_pseudo_correct"]+=primary_truth
                    total["selected_pseudo_wrong"]+=k-primary_truth
                    total["unfiltered_pseudo_correct"]+=baseline_truth
                    total["unfiltered_pseudo_wrong"]+=k-baseline_truth
                    total["original_primary_proposal_count"]+=len(
                        plan["all_primary_proposals"])
                    total["committee_disagreements"]+=plan[
                        "secondary_disagreement_count"]
                    total["B_contradictions"]+=plan["charged_B_contradiction_count"]
                    total["dream_attempts"]+=plan["primary_queries"]+plan["secondary_queries"]
                    total["dream_count"]+=k
                    total["worlds_k_ge_8"]+=int(k>=8)
                    total["cold_restore_tamper_worlds"]+=1
                    total["candidate_cpu_ns"]+=candidate_cpu
                    total["unfiltered_cpu_ns"]+=baseline_cpu
                    bucket=family.setdefault(world.family,{
                        "worlds":0,"candidate_correct":0,"unfiltered_correct":0,
                        "candidate_wrong":0,"unfiltered_wrong":0,
                        "dreams":0,"pseudo_correct":0,"teacher_mlp_converged":0
                    })
                    bucket["worlds"]+=1
                    bucket["candidate_correct"]+=scores["candidate"]["physical"]["correct"]
                    bucket["unfiltered_correct"]+=scores["unfiltered"]["physical"]["correct"]
                    bucket["candidate_wrong"]+=scores["candidate"]["physical"]["wrong_confident"]
                    bucket["unfiltered_wrong"]+=scores["unfiltered"]["physical"]["wrong_confident"]
                    bucket["dreams"]+=k
                    bucket["pseudo_correct"]+=primary_truth
                    bucket["teacher_mlp_converged"]+=int(mlp_fit["fully_trained"])
                total["charged_actions"]+=192
        self.assertEqual(total["primary_worlds"],12)
        self.assertEqual(total["negative_worlds"],4)
        self.assertEqual(total["primary_physical"],768)
        self.assertEqual(total["primary_compositions"],384)
        self.assertEqual(total["charged_actions"],16*192)
        self.assertEqual(total["cold_restore_tamper_worlds"],12)
        retention_rate=total["candidate_retained"]/max(1,total["stageA_eligible"])
        dream_precision=total["selected_pseudo_correct"]/max(1,total["dream_count"])
        cpu_ratio=total["candidate_cpu_ns"]/max(1,total["unfiltered_cpu_ns"])
        criteria={
            "primary_correct_ge_430":total["candidate_correct"]>=430,
            "primary_gain_vs_equal_k_unfiltered_ge_18":
                total["candidate_correct"]-total["unfiltered_correct"]>=18,
            "stageA_retention_ge_82pct":retention_rate>=0.82,
            "stageA_retention_gain_ge_15":
                total["candidate_retained"]-total["unfiltered_retained"]>=15,
            "never_charged_correct_ge_18":total["candidate_unseen_correct"]>=18,
            "primary_confident_wrong_le_24":total["candidate_wrong"]<=24,
            "two_action_correct_ge_140":total["candidate_two_action_correct"]>=140,
            "pseudo_precision_ge_965":dream_precision>=0.965,
            "nine_worlds_k_ge_8":total["worlds_k_ge_8"]>=9,
            "pseudo_correct_count_ge_90":total["selected_pseudo_correct"]>=90,
            "cold_snapshots_12":total["cold_restore_tamper_worlds"]==12,
            "compute_ratio_le_2":cpu_ratio<=2.0,
            "quartic_wrong_confident_le_12":
                total["negative_candidate_wrong"]<=12,
            "quartic_confident_wrong_gain_ge_4":
                total["negative_unfiltered_wrong"]-
                total["negative_candidate_wrong"]>=4
        }
        status="SELFTEST_SIGNAL" if all(criteria.values()) else (
            "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP72_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":status,"criteria":criteria,
            "retention_rate":round(retention_rate,8),
            "selected_pseudo_precision":round(dream_precision,8),
            "candidate_over_matched_cpu_ratio":round(cpu_ratio,7),
            "trained_neural_baseline_worlds":total["mlp_converged"],
            "totals":total,"by_family":family,"worlds":reports
        },sort_keys=True,separators=(",",":")))
        # Science criterion failures are data; do not convert to unittest FAIL.


if __name__=="__main__":
    unittest.main()

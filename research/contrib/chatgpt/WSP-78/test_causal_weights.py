"""WSP78 frozen paid-causal-effect discovery -> executable numerical ReLU weights.

Two INDEPENDENT, source-identical 144-action no-reset physical trajectories
per world: actual-consequence contrast and SHA-uniform random. No learner
uses private source truth. Full evaluator only AFTER charge, compile, and
numeric cold weights freeze. Preserve all positive and negative criteria.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from random import Random
import sys,time,json,unittest

from source import SEEDS,STATES,ACTIONS,build_world,TRAIN_ACTIONS
from causal_weights import (
    CausalWeightProgrammer,MONOMIALS,INPUTS,OUTPUTS
)
from independent_symbolic import IndependentSymbolicCausal

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"WSP-77"))
from physical_contrasts6 import choose_observed_contrast,uniform_random
from neural6 import FeatureGrowthNeural
from repair6 import fitted_readout
from fully_trained_mlp6 import EndToEndAdamControl

PUBLIC=((s,a) for s in STATES for a in ACTIONS)
ALL_PUBLIC=tuple(PUBLIC)


def digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),
            ensure_ascii=True,default=list).encode("ascii")).hexdigest()


def score(predictions,truth,paid,tasks=None):
    totals={"correct":0,"wrong_confident":0,"abstain":0}
    unseen={"correct":0,"wrong_confident":0,"abstain":0,"total":0}
    for key,target in truth.items():
        predicted=predictions[key]
        label="abstain" if predicted is None else (
            "correct" if predicted==target else "wrong_confident")
        totals[label]+=1
        if key not in paid:
            unseen[label]+=1
            unseen["total"]+=1
    assert sum(totals.values())==384
    assert sum(unseen[k] for k in totals)==unseen["total"]
    report={"physical":totals,"truly_unpaid":unseen}
    if tasks is not None:
        comp={"correct":0,"wrong_confident":0,"abstain":0}
        for task in tasks:
            first,second=task.actions
            middle=predictions[(task.start,first)]
            last=predictions[(middle,second)] if middle is not None else None
            label=("abstain" if last is None else "correct" if last==task._finish
                   else "wrong_confident")
            comp[label]+=1
        assert sum(comp.values())==len(tasks)
        report["two_action"]=comp
    return report


def predict_all(predict):
    return {key:predict(*key) for key in ALL_PUBLIC}


def reachability(world):
    seen={(0,)*6}
    todo=[(0,)*6]
    while todo:
        s=todo.pop()
        for a in ACTIONS:
            nxt=world._step_oracle(s,a)
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return len(seen)


def coverage(rows):
    observed={(s,a) for s,a,y in rows}
    return {"unique_paid_contexts":len(observed),
            "unpaid_possible_contexts":384-len(observed),
            "distinct_public_states":len({rows[0][0]}|{y for s,a,y in rows}),
            "per_action_real_B_counts":[sum(int(action==a)
                for s,action,y in rows[96:]) for a in ACTIONS]}


def matched_neural_probabilities(baseline,numerical_predictions):
    """Equal-coverage selection from public UNLABELED six-bit inputs only."""
    m=sum(x is not None for x in numerical_predictions.values())
    ranks=[]
    for key in ALL_PUBLIC:
        state,action=key
        p=baseline.winner.probability(state,action)
        margin=min(abs(q-0.5) for q in p)
        ranks.append((-margin,key))
    chosen={key for margin,key in sorted(ranks)[:m]}
    return {key:baseline.predict(*key,confidence=False) if key in chosen
            else None for key in ALL_PUBLIC}


class FrozenReLUCausalEffectCompilation(unittest.TestCase):
    def test_source_blindness_numeric_and_physically_paid_custody(self):
        folder=Path(__file__).parent
        for name in ("causal_weights.py","independent_symbolic.py"):
            src=(folder/name).read_text("utf-8")
            for prohibited in ("from source import","import source","_step_oracle",
                               "torch","backward(", "from weight_programmer import"):
                self.assertNotIn(prohibited,src)
        self.assertEqual(len(SEEDS),16)
        self.assertEqual(TRAIN_ACTIONS,144)
        self.assertEqual(len(STATES),64)
        self.assertEqual(len(ACTIONS),6)
        self.assertEqual(INPUTS,12)
        self.assertEqual(OUTPUTS,6)
        self.assertEqual(len(MONOMIALS),22)
        self.assertEqual(384-144,240)
        for seed in SEEDS:
            w=build_world(seed)
            self.assertEqual(w.receipt(),build_world(seed).receipt())
            self.assertEqual(len(w.composition_tests()),32)
        with self.assertRaises(PermissionError):
            build_world(5101)
        for forbidden in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(5201,cohort=forbidden)
        w=build_world(5201)
        physical=w.training_session()
        m=CausalWeightProgrammer()
        for i in range(96):
            physical_row=physical.step(i%6)
            m.charge(physical_row)
        m.compile()
        self.assertEqual(m.charged_actions,96)
        cold=CausalWeightProgrammer.restore(m.snapshot())
        for s,a in ALL_PUBLIC:
            self.assertEqual(cold.predict(s,a),m.predict(s,a))
        with self.assertRaises(ValueError):
            CausalWeightProgrammer.restore(
                m.snapshot().replace("wsp78.learned-neural-parity.v1",
                                     "wsp78.learned-neural-parity.v2"))
        for i in range(48):
            m.charge(physical.step(i%6))
        m.compile()
        self.assertEqual(m.charged_actions,144)
        with self.assertRaises(ValueError):
            m.charge(physical.step(0))

    def test_frozen_16_paid_worlds_numerical_vs_symbolic_and_converged_MLP(self):
        keys=(
            "worlds","primary_worlds","negative_worlds","paid_actions",
            "evaluator_reachable_64","cold_numeric_tamper_worlds",
            "primary_cases","primary_compositions",
            "candidate_correct","candidate_wrong","candidate_abstain",
            "candidate_unpaid_correct","candidate_unpaid_wrong",
            "candidate_unpaid_count","candidate_two_action_correct",
            "candidate_two_action_wrong",
            "random_correct","random_wrong","random_unpaid_correct",
            "degree1_correct","degree1_wrong",
            "readout_correct","readout_wrong",
            "MLP_correct","MLP_wrong","MLP_forced_correct","MLP_forced_wrong",
            "MLP_matched_correct","MLP_matched_wrong",
            "memory_correct","memory_wrong",
            "stageA_true_confident","stageA_retained",
            "negative_correct","negative_wrong",
            "inconsistent_negative_actions","inconsistent_primary_actions",
            "symbolic_parity_worlds","primary_cold_numeric_worlds",
            "MLP_converged","MLP_gradient_updates",
            "candidate_train_cpu_ns","candidate_eval_cpu_ns",
            "MLP_train_cpu_ns","MLP_eval_cpu_ns",
            "candidate_numeric_confident_detectors","candidate_numeric_effect_weights",
            "observed_paid_unique","random_paid_unique"
        )
        totals={k:0 for k in keys}
        worlds=[]
        families={}
        for seed in SEEDS:
            with self.subTest(seed=seed):
                negative=seed>=5213
                physics=build_world(seed)
                active=build_world(seed).training_session()
                random=build_world(seed).training_session()
                action_A=Random(int.from_bytes(sha256(
                    f"WSP78|physically-paid-common-A|{seed}".encode("ascii")
                ).digest(),"big"))
                candidate=CausalWeightProgrammer(degree=2)
                random_program=CausalWeightProgrammer(degree=2)
                degree1=CausalWeightProgrammer(degree=1)
                legacy=FeatureGrowthNeural("residual",seed=seed)
                active_ledger=[]
                random_ledger=[]
                source_rowsA=[]
                train_t=time.process_time_ns()
                for i in range(96):
                    a=action_A.choice(ACTIONS)
                    x=active.step(a)
                    y=random.step(a)
                    self.assertEqual((x.before,x.action,x.after),
                                     (y.before,y.action,y.after))
                    record=(x.before,x.action,x.after)
                    active_ledger.append(record)
                    random_ledger.append(record)
                    source_rowsA.append(record)
                    candidate.charge(x)
                    random_program.charge(y)
                    degree1.charge(x)
                    legacy.charge(x)
                    if i+1 in (48,96):
                        legacy.grow()
                self.assertEqual(legacy.growth_rounds,2)
                self.assertEqual(legacy.charged_actions,96)
                stageA_numeric=legacy.snapshot()
                stageA_info=candidate.compile()
                stageA_weight_only=CausalWeightProgrammer.restore(candidate.snapshot())
                old_predictions=predict_all(stageA_weight_only.predict)
                direct_A_B=[]
                uniform_A_B=[]
                rng=random_policy=uniform_random(seed)
                policy_cpu_ns=0
                for step in range(48):
                    t=time.process_time_ns()
                    selected=choose_observed_contrast(
                        active.state,active_ledger,seed,step)
                    policy_cpu_ns+=time.process_time_ns()-t
                    x=active.step(selected)
                    y=random.step(random_policy.choice(ACTIONS))
                    candidate.charge(x)
                    random_program.charge(y)
                    degree1.charge(x)
                    rec1=(x.before,x.action,x.after)
                    rec2=(y.before,y.action,y.after)
                    direct_A_B.append(rec1)
                    uniform_A_B.append(rec2)
                    active_ledger.append(rec1)
                    random_ledger.append(rec2)
                self.assertEqual(len(active.ledger),144)
                self.assertEqual(len(random.ledger),144)
                self.assertEqual(active_ledger[:96],random_ledger[:96])
                for rows in (active_ledger,random_ledger):
                    self.assertTrue(all(rows[i][2]==rows[i+1][0]
                                    for i in range(143)))
                candidate_info=candidate.compile()
                random_info=random_program.compile()
                degree1_info=degree1.compile()
                candidate_train_ns=time.process_time_ns()-train_t
                self.assertEqual(candidate.gradient_steps,0)
                self.assertEqual(candidate_info["paid_actions"],144)
                self.assertEqual(random_info["paid_actions"],144)
                self.assertEqual(degree1_info["degree"],1)
                # Cold weight-only inference and tamper: the paid ledger and
                # row echelon are NEVER needed to answer heldout queries.
                cold=CausalWeightProgrammer.restore(candidate.snapshot())
                self.assertNotIn('"ledger"',candidate.snapshot())
                self.assertNotIn('"basis"',candidate.snapshot())
                with self.assertRaises(ValueError):
                    CausalWeightProgrammer.restore(
                        candidate.snapshot().replace(
                            "wsp78.learned-neural-parity.v1",
                            "wsp78.learned-neural-parity.v2"))
                self.assertEqual(candidate.snapshot(),cold.snapshot())
                for s,a in ALL_PUBLIC:
                    self.assertEqual(cold.predict(s,a),candidate.predict(s,a))
                # Same-ledger conventional source-blind numerical readout.
                readout=fitted_readout(stageA_numeric,source_rowsA,direct_A_B)
                same_paid_mem={(s,a):y for s,a,y in active_ledger}
                # Symbolic strong same-prior control independently fits ALL
                # paid rows; its predictions must match the learned NEURAL
                # numeric ReLU outputs for all public state/action identities.
                symbolic=IndependentSymbolicCausal(active_ledger,degree=2)
                t=time.process_time_ns()
                neural_predictions=predict_all(cold.predict)
                neural_eval_ns=time.process_time_ns()-t
                symbolic_predictions=predict_all(symbolic.predict)
                self.assertEqual(neural_predictions,symbolic_predictions)
                random_predictions=predict_all(random_program.predict)
                ablation_predictions=predict_all(degree1.predict)
                readout_predictions=predict_all(readout.predict)
                memory_predictions={key:same_paid_mem.get(key)
                                    for key in ALL_PUBLIC}
                self.assertTrue(any(
                    ablation_predictions[k]!=neural_predictions[k]
                    for k in ALL_PUBLIC))
                # Freeze all predictions before source evaluator truth.
                mlp=None
                mlp_info=None
                mlp_score_predictions=None
                mlp_forced_predictions=None
                mlp_matched_predictions=None
                mlp_cpu=mlp_eval_ns=0
                if not negative:
                    mlp=EndToEndAdamControl(seed)
                    t=time.process_time_ns()
                    mlp_info=mlp.fit(active_ledger)
                    mlp_cpu=time.process_time_ns()-t
                    t=time.process_time_ns()
                    mlp_score_predictions=predict_all(
                        lambda s,a:mlp.predict(s,a,confidence=True))
                    mlp_forced_predictions=predict_all(mlp.predict)
                    mlp_matched_predictions=matched_neural_probabilities(
                        mlp,neural_predictions)
                    mlp_eval_ns=time.process_time_ns()-t
                    self.assertEqual(
                        sum(x is not None for x in mlp_matched_predictions.values()),
                        sum(x is not None for x in neural_predictions.values()))
                # Evaluator-only; no physics truth used to write any weights
                # or pick any prediction/MLP equal-coverage inputs.
                truth={(s,a):physics._step_oracle(s,a) for s,a in ALL_PUBLIC}
                tasks=physics.composition_tests()
                reachable=reachability(physics)
                seen_active=set(same_paid_mem)
                seen_random={(s,a) for s,a,y in random_ledger}
                candidate_scores=score(neural_predictions,truth,seen_active,tasks)
                random_scores=score(random_predictions,truth,seen_random)
                degree1_scores=score(ablation_predictions,truth,seen_active)
                readout_scores=score(readout_predictions,truth,seen_active)
                memory_scores=score(memory_predictions,truth,seen_active)
                known_old={k:pred for k,pred in old_predictions.items()
                           if pred is not None and pred==truth[k]}
                retained=sum(int(neural_predictions[k]==old)
                             for k,old in known_old.items())
                if not negative:
                    mlp_scores=score(mlp_score_predictions,truth,seen_active)
                    mlp_forced_scores=score(mlp_forced_predictions,truth,seen_active)
                    mlp_matched_scores=score(mlp_matched_predictions,truth,seen_active)
                report={
                    "seed":seed,"family":physics.family,"source":physics.receipt(),
                    "evaluator_only_full_reachability":reachable,
                    "physically_paid_actions_per_policy":144,
                    "physical_paid_A_sha256":digest(source_rowsA),
                    "observed_paid_B_sha256":digest(direct_A_B),
                    "random_paid_B_sha256":digest(uniform_A_B),
                    "source_private_heldout_oracle_sha256":digest(
                        [[s,a,y] for (s,a),y in truth.items()]),
                    "StageA_numeric_causal_snapshot_sha256":sha256(
                        stageA_weight_only.snapshot().encode("ascii")).hexdigest(),
                    "final_numeric_causal_snapshot_sha256":sha256(
                        cold.snapshot().encode("ascii")).hexdigest(),
                    "numeric_compilation":candidate_info,
                    "StageA_causal_compilation":stageA_info,
                    "random_ledger_compilation":random_info,
                    "degree1_ablation_compilation":degree1_info,
                    "observed_coverage":coverage(active_ledger),
                    "random_coverage":coverage(random_ledger),
                    "cold_numeric":candidate_scores,
                    "independent_symbolic":score(symbolic_predictions,truth,seen_active),
                    "random_physically_paid_policy":random_scores,
                    "degree1_causal_grammar_ablation":degree1_scores,
                    "same_ledger_numerical_readout":readout_scores,
                    "exact_paid_memory":memory_scores,
                    "StageA_old_truth_confident":len(known_old),
                    "StageA_retained":retained,
                    "fully_trained_conventional_MLP":mlp_info,
                    "MLP_original_confidence":mlp_scores if not negative else None,
                    "MLP_forced":mlp_forced_scores if not negative else None,
                    "MLP_public_unlabeled_equal_coverage":mlp_matched_scores if not negative else None,
                    "direct_programming_total_train_cpu_ns":candidate_train_ns,
                    "physical_action_selection_cpu_ns":policy_cpu_ns,
                    "cold_numeric_evaluation_cpu_ns":neural_eval_ns,
                    "MLP_train_cpu_ns":mlp_cpu,
                    "MLP_eval_cpu_ns":mlp_eval_ns
                }
                worlds.append(report)
                totals["worlds"]+=1
                totals["paid_actions"]+=288
                totals["evaluator_reachable_64"]+=int(reachable==64)
                totals["cold_numeric_tamper_worlds"]+=1
                totals["symbolic_parity_worlds"]+=1
                if negative:
                    totals["negative_worlds"]+=1
                    totals["negative_correct"]+=candidate_scores["physical"]["correct"]
                    totals["negative_wrong"]+=candidate_scores["physical"]["wrong_confident"]
                    totals["inconsistent_negative_actions"]+=len(
                        candidate_info["inconsistent_actions"])
                else:
                    totals["primary_worlds"]+=1
                    totals["primary_cases"]+=384
                    totals["primary_compositions"]+=32
                    for name,item in (
                        ("candidate",candidate_scores),
                        ("random",random_scores),
                        ("degree1",degree1_scores),
                        ("readout",readout_scores),
                        ("memory",memory_scores),
                        ("MLP",mlp_scores),
                        ("MLP_forced",mlp_forced_scores),
                        ("MLP_matched",mlp_matched_scores)):
                        totals[f"{name}_correct"]+=item["physical"]["correct"]
                        totals[f"{name}_wrong"]+=item["physical"]["wrong_confident"]
                    totals["candidate_abstain"]+=candidate_scores["physical"]["abstain"]
                    totals["candidate_unpaid_correct"]+=candidate_scores["truly_unpaid"]["correct"]
                    totals["candidate_unpaid_wrong"]+=candidate_scores["truly_unpaid"]["wrong_confident"]
                    totals["candidate_unpaid_count"]+=candidate_scores["truly_unpaid"]["total"]
                    totals["random_unpaid_correct"]+=random_scores["truly_unpaid"]["correct"]
                    totals["candidate_two_action_correct"]+=candidate_scores["two_action"]["correct"]
                    totals["candidate_two_action_wrong"]+=candidate_scores["two_action"]["wrong_confident"]
                    totals["stageA_true_confident"]+=len(known_old)
                    totals["stageA_retained"]+=retained
                    totals["inconsistent_primary_actions"]+=len(
                        candidate_info["inconsistent_actions"])
                    totals["primary_cold_numeric_worlds"]+=1
                    totals["candidate_numeric_confident_detectors"]+=candidate_info[
                        "numeric_confidence_detector_units"]
                    totals["candidate_numeric_effect_weights"]+=candidate_info[
                        "causal_weight_nonzero"]
                    totals["observed_paid_unique"]+=coverage(active_ledger)[
                        "unique_paid_contexts"]
                    totals["random_paid_unique"]+=coverage(random_ledger)[
                        "unique_paid_contexts"]
                    totals["MLP_converged"]+=int(mlp_info["fully_trained"])
                    totals["MLP_gradient_updates"]+=mlp_info["gradient_updates_total"]
                    totals["candidate_train_cpu_ns"]+=candidate_train_ns
                    totals["candidate_eval_cpu_ns"]+=neural_eval_ns
                    totals["MLP_train_cpu_ns"]+=mlp_cpu
                    totals["MLP_eval_cpu_ns"]+=mlp_eval_ns
                    f=families.setdefault(physics.family,{
                        "worlds":0,"candidate_correct":0,"candidate_wrong":0,
                        "candidate_unpaid_correct":0,"unpaid_total":0,
                        "same_symbolic_tied":0,"MLP_matched_correct":0})
                    f["worlds"]+=1
                    f["candidate_correct"]+=candidate_scores["physical"]["correct"]
                    f["candidate_wrong"]+=candidate_scores["physical"]["wrong_confident"]
                    f["candidate_unpaid_correct"]+=candidate_scores["truly_unpaid"]["correct"]
                    f["unpaid_total"]+=candidate_scores["truly_unpaid"]["total"]
                    f["same_symbolic_tied"]+=1
                    f["MLP_matched_correct"]+=mlp_matched_scores["physical"]["correct"]
        self.assertEqual(totals["worlds"],16)
        self.assertEqual(totals["paid_actions"],4608)
        self.assertEqual(totals["primary_worlds"],12)
        self.assertEqual(totals["negative_worlds"],4)
        self.assertEqual(totals["primary_cases"],4608)
        self.assertEqual(totals["primary_compositions"],384)
        self.assertEqual(totals["symbolic_parity_worlds"],16)
        self.assertGreaterEqual(totals["candidate_unpaid_count"],2880)
        keep=totals["stageA_retained"]/max(1,totals["stageA_true_confident"])
        cost=(totals["candidate_train_cpu_ns"]+totals["candidate_eval_cpu_ns"])/max(
            1,totals["MLP_train_cpu_ns"]+totals["MLP_eval_cpu_ns"])
        gates={
            "all_16_reachable_64":totals["evaluator_reachable_64"]==16,
            "primary_correct_ge_1100":totals["candidate_correct"]>=1100,
            "primary_truly_unpaid_correct_ge_750":totals["candidate_unpaid_correct"]>=750,
            "primary_truly_unpaid_count_ge_2880":totals["candidate_unpaid_count"]>=2880,
            "primary_confident_wrong_le_12":totals["candidate_wrong"]<=12,
            "two_step_correct_ge_100":totals["candidate_two_action_correct"]>=100,
            "StageA_correct_confident_retention_ge_95pct":keep>=0.95,
            "beat_same_paid_readout_ge_300":
                totals["candidate_correct"]-totals["readout_correct"]>=300,
            "beat_MLP_equal_coverage_correct_ge_40":
                totals["candidate_correct"]-totals["MLP_matched_correct"]>=40,
            "no_more_wrong_than_equal_coverage_MLP":
                totals["candidate_wrong"]<=totals["MLP_matched_wrong"],
            "beat_degree1_same_paid_ablation_ge_150":
                totals["candidate_correct"]-totals["degree1_correct"]>=150,
            "not_worse_than_equal_paid_random_by_over_30":
                totals["candidate_correct"]+30>=totals["random_correct"],
            "primary_12_cold_numeric":totals["primary_cold_numeric_worlds"]==12,
            "cubic_negatives_wrong_le_60":totals["negative_wrong"]<=60,
            "all_16_cold_tamper":totals["cold_numeric_tamper_worlds"]==16,
            "independent_symbolic_same_prior_prediction_parity_16":
                totals["symbolic_parity_worlds"]==16,
            "fully_converged_MLP_worlds_ge_10":totals["MLP_converged"]>=10,
            "candidate_train_eval_CPU_to_MLP_le_075":cost<=0.75
        }
        verdict=("SELFTEST_SIGNAL" if all(gates.values()) else
                 "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP78_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":verdict,"frozen_criteria":gates,"totals":totals,
            "old_true_confident_retention":round(keep,8),
            "numeric_training_plus_inference_to_MLP_cpu":round(cost,8),
            "by_family":families,"worlds":worlds
        },sort_keys=True,separators=(",",":")))
        # Engineering unittest execution PASS is NOT scientific success.


if __name__=="__main__":
    unittest.main()

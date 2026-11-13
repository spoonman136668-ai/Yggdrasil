"""WSP79 frozen, independently physically charged six-bit causal order test.

The only private physical source import is HERE in the evaluator unit test.
Every learner operates on actual paid before/action/after rows only. Exact
evaluator-private physical transition truths are revealed ONLY after model
weights, cold restore, action selection, matched MLP coverage and symbolic
predictions are frozen. Negative science remains a PASS engineering test.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from random import Random
import json,sys,time,unittest

from source import SEEDS,STATES,ACTIONS,TRAIN_ACTIONS,build_world
from sparse_weights import SparseCausalNumeric,MONOMIALS,MONOMIAL_SETS,INPUTS,OUTPUTS
from independent_sparse_symbolic import IndependentSparseSymbolic

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"WSP-78"))
from causal_weights import CausalWeightProgrammer
sys.path.insert(0,str(ROOT/"WSP-77"))
from physical_contrasts6 import choose_observed_contrast,uniform_random
from neural6 import FeatureGrowthNeural
from repair6 import fitted_readout
from fully_trained_mlp6 import EndToEndAdamControl

PUBLIC=tuple((s,a) for s in STATES for a in ACTIONS)


def digest(data):
    return sha256(json.dumps(data,sort_keys=True,separators=(",",":"),
         ensure_ascii=True,default=list).encode("ascii")).hexdigest()


def all_predictions(predict):
    return {(s,a):predict(s,a) for s,a in PUBLIC}


def coverage(rows):
    paid={(s,a) for s,a,y in rows}
    return {"unique_paid_public_inputs":len(paid),
            "truly_unpaid_public_inputs":384-len(paid),
            "visited_public_states":len({rows[0][0]}|{y for s,a,y in rows}),
            "B_action_counts":[sum(int(a==x) for s,a,y in rows[96:])
                               for x in ACTIONS]}


def eval_model(predictions,truth,paid,compositions=None):
    got={"correct":0,"wrong_confident":0,"abstain":0}
    never={"correct":0,"wrong_confident":0,"abstain":0,"total":0}
    for key,y in truth.items():
        p=predictions[key]
        verdict=("abstain" if p is None else
                 "correct" if p==y else "wrong_confident")
        got[verdict]+=1
        if key not in paid:
            never[verdict]+=1
            never["total"]+=1
    assert sum(got.values())==384
    assert never["total"]==sum(never[k] for k in got)
    out={"physical":got,"genuinely_never_charged":never}
    if compositions is not None:
        pairs={"correct":0,"wrong_confident":0,"abstain":0}
        for task in compositions:
            a,b=task.actions
            middle=predictions[(task.start,a)]
            end=predictions[(middle,b)] if middle is not None else None
            v="abstain" if end is None else (
                "correct" if end==task._finish else "wrong_confident")
            pairs[v]+=1
        assert sum(pairs.values())==len(compositions)
        out["two_action"]=pairs
    return out


def reachability(world):
    found={(0,)*6}
    stack=[(0,)*6]
    while stack:
        state=stack.pop()
        for action in ACTIONS:
            future=world._step_oracle(state,action)
            if future not in found:
                found.add(future)
                stack.append(future)
    return len(found)


def matched_MLP(baseline,confidence_mask):
    # Match prediction COVERAGE using PUBLIC query identities and baseline
    # confidence alone; no private source outcome or frozen test error.
    number=sum(p is not None for p in confidence_mask.values())
    ranks=[]
    for s,a in PUBLIC:
        prob=baseline.winner.probability(s,a)
        margin=min(abs(q-0.5) for q in prob)
        ranks.append((-margin,(s,a)))
    keep={pair for margin,pair in sorted(ranks)[:number]}
    return {pair:(baseline.predict(*pair,confidence=False)
                  if pair in keep else None) for pair in PUBLIC}


class FrozenSparseDegreeDiscovery(unittest.TestCase):
    def test_source_blindness_model_and_physical_boundaries(self):
        folder=Path(__file__).parent
        for name in ("sparse_weights.py","independent_sparse_symbolic.py"):
            code=(folder/name).read_text("utf8")
            for forbidden in ("from source import","import source",
                              "_step_oracle","torch","backward(",
                              "from weight_programmer import"):
                self.assertNotIn(forbidden,code)
        self.assertEqual(len(SEEDS),16)
        self.assertEqual(TRAIN_ACTIONS,144)
        self.assertEqual(len(STATES),64)
        self.assertEqual(len(ACTIONS),6)
        self.assertEqual(INPUTS,12)
        self.assertEqual(OUTPUTS,6)
        self.assertEqual(len(MONOMIALS),42)
        self.assertEqual(len(MONOMIAL_SETS),12384)
        for seed in SEEDS:
            world=build_world(seed)
            self.assertEqual(world.receipt(),build_world(seed).receipt())
            self.assertEqual(len(world.composition_tests()),32)
        with self.assertRaises(PermissionError):
            build_world(5201)
        for cohort in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(5301,cohort=cohort)
        world=build_world(5301)
        session=world.training_session()
        learner=SparseCausalNumeric()
        for i in range(96):
            learner.charge(session.step(i%6))
        a=learner.compile()
        self.assertEqual(a["paid_physical_actions"],96)
        cold=SparseCausalNumeric.restore(learner.snapshot())
        for state,action in PUBLIC:
            self.assertEqual(cold.predict(state,action),learner.predict(state,action))
        with self.assertRaises(ValueError):
            SparseCausalNumeric.restore(learner.snapshot().replace(
                "wsp79.sparse-causal-numeric-weights.v1",
                "wsp79.sparse-causal-numeric-weights.v2"))
        for i in range(48):
            learner.charge(session.step(i%6))
        self.assertEqual(learner.compile()["paid_physical_actions"],144)
        with self.assertRaises(ValueError):
            learner.charge(session.step(0))

    def test_frozen_converged_neural_symbolic_and_negative_grammar(self):
        fields=(
            "worlds","primary_worlds","negative_worlds","paid_actions",
            "reachable_full_64_worlds","cold_numeric_worlds",
            "symbolic_exact_parity_worlds","primary_physical_cases",
            "primary_two_action_tasks",
            "candidate_correct","candidate_wrong","candidate_abstain",
            "candidate_never_paid_correct","candidate_never_paid_wrong",
            "candidate_never_paid_count","candidate_two_action_correct",
            "candidate_two_action_wrong",
            "degree3_correct","degree3_degree2_correct",
            "degree2_correct","degree2_wrong",
            "random_correct","random_wrong",
            "readout_correct","readout_wrong",
            "memory_correct","memory_wrong",
            "MLP_confident_correct","MLP_confident_wrong",
            "MLP_forced_correct","MLP_forced_wrong",
            "MLP_matched_correct","MLP_matched_wrong",
            "MLP_converged","MLP_gradient_updates",
            "stageA_true_confident","stageA_retained",
            "negative_correct","negative_wrong",
            "negative_inconsistent_actions","primary_inconsistent_actions",
            "numeric_neural_parameters","numeric_confidence_detectors",
            "surviving_sparse_hypotheses",
            "candidate_train_cpu_ns","candidate_eval_cpu_ns",
            "MLP_train_cpu_ns","MLP_eval_cpu_ns",
            "candidate_paid_unique","random_paid_unique"
        )
        totals={k:0 for k in fields}
        worlds=[]
        by_family={}
        for seed in SEEDS:
            with self.subTest(seed=seed):
                negative=seed>=5313
                physics=build_world(seed)
                copies={n:build_world(seed).training_session()
                        for n in ("candidate","random")}
                rngA=Random(int.from_bytes(sha256(
                    f"WSP79|paid-common-A|{seed}".encode("ascii")
                ).digest(),"big"))
                learn=SparseCausalNumeric()
                learn_random=SparseCausalNumeric()
                degree2=CausalWeightProgrammer(degree=2)
                legacy=FeatureGrowthNeural("residual",seed=seed)
                ledgers={n:[] for n in copies}
                t=time.process_time_ns()
                for i in range(96):
                    act=rngA.choice(ACTIONS)
                    outcomes={n:s.step(act) for n,s in copies.items()}
                    x=outcomes["candidate"]
                    self.assertEqual((x.before,x.action,x.after),
                                     (outcomes["random"].before,
                                      outcomes["random"].action,
                                      outcomes["random"].after))
                    row=(x.before,x.action,x.after)
                    for n in copies:
                        ledgers[n].append(row)
                    learn.charge(x)
                    learn_random.charge(outcomes["random"])
                    degree2.charge(x)
                    legacy.charge(x)
                    if i+1 in (48,96):
                        legacy.grow()
                self.assertEqual(legacy.charged_actions,96)
                legacy_stageA=legacy.snapshot()
                StageA=learn.compile()
                initial=SparseCausalNumeric.restore(learn.snapshot())
                initial_predictions=all_predictions(initial.predict)
                uniform=uniform_random(seed)
                t_policy=0
                for i in range(48):
                    p=time.process_time_ns()
                    selected=choose_observed_contrast(
                        copies["candidate"].state,ledgers["candidate"],seed,i)
                    t_policy+=time.process_time_ns()-p
                    x=copies["candidate"].step(selected)
                    y=copies["random"].step(uniform.choice(ACTIONS))
                    learn.charge(x)
                    learn_random.charge(y)
                    degree2.charge(x)
                    ledgers["candidate"].append((x.before,x.action,x.after))
                    ledgers["random"].append((y.before,y.action,y.after))
                compiled=learn.compile()
                random_compiled=learn_random.compile()
                degree2_compiled=degree2.compile()
                candidate_train=time.process_time_ns()-t
                self.assertEqual(learn.gradient_steps,0)
                self.assertEqual(compiled["paid_physical_actions"],144)
                self.assertEqual(random_compiled["paid_physical_actions"],144)
                self.assertEqual(degree2_compiled["paid_actions"],144)
                for n in copies:
                    self.assertEqual(len(copies[n].ledger),144)
                    self.assertEqual(len(ledgers[n]),144)
                    self.assertEqual(ledgers[n][0][0],(0,)*6)
                    self.assertTrue(all(ledgers[n][j][2]==ledgers[n][j+1][0]
                                        for j in range(143)))
                self.assertEqual(ledgers["candidate"][:96],
                                 ledgers["random"][:96])
                cold=SparseCausalNumeric.restore(learn.snapshot())
                self.assertEqual(cold.snapshot(),learn.snapshot())
                self.assertNotIn('"ledger"',cold.snapshot())
                self.assertNotIn('"survivors"',cold.snapshot())
                with self.assertRaises(ValueError):
                    SparseCausalNumeric.restore(cold.snapshot().replace(
                        "wsp79.sparse-causal-numeric-weights.v1",
                        "wsp79.sparse-causal-numeric-weights.v2"))
                start=time.process_time_ns()
                learned_predictions=all_predictions(cold.predict)
                neural_eval=time.process_time_ns()-start
                self.assertEqual(learned_predictions,all_predictions(learn.predict))
                # Independently implemented same-prior symbolic learner:
                # exact parity across ALL public inputs, all source worlds.
                symbolic=IndependentSparseSymbolic(ledgers["candidate"])
                symbolic_preds=all_predictions(symbolic.predict)
                self.assertEqual(learned_predictions,symbolic_preds)
                random_preds=all_predictions(learn_random.predict)
                degree2_preds=all_predictions(degree2.predict)
                readout=fitted_readout(
                    legacy_stageA,ledgers["candidate"][:96],
                    ledgers["candidate"][96:])
                readout_preds=all_predictions(readout.predict)
                lookup={(s,a):y for s,a,y in ledgers["candidate"]}
                memory_preds={key:lookup.get(key) for key in PUBLIC}
                # Erasure is a real numeric zero-effect negative control.
                erased=SparseCausalNumeric.restore(cold.snapshot())
                erased.effect_w=[[0.0]*len(row) for row in erased.effect_w]
                self.assertTrue(any(
                    erased.predict(s,a,force=True)!=cold.predict(s,a,force=True)
                    for s,a in PUBLIC))
                mlp_train_ns=mlp_eval_ns=0
                mlp_info=mlp_confident=mlp_forced=mlp_matched=None
                if not negative:
                    baseline=EndToEndAdamControl(seed)
                    k=time.process_time_ns()
                    mlp_info=baseline.fit(ledgers["candidate"])
                    mlp_train_ns=time.process_time_ns()-k
                    k=time.process_time_ns()
                    mlp_confident=all_predictions(
                        lambda s,a:baseline.predict(s,a,confidence=True))
                    mlp_forced=all_predictions(baseline.predict)
                    mlp_matched=matched_MLP(baseline,learned_predictions)
                    mlp_eval_ns=time.process_time_ns()-k
                    self.assertEqual(
                        sum(v is not None for v in mlp_matched.values()),
                        sum(v is not None for v in learned_predictions.values()))
                # Only now after ALL paid sessions and cold-only predictions
                # are frozen may evaluator inspect private physical labels.
                truth={(s,a):physics._step_oracle(s,a) for s,a in PUBLIC}
                tasks=physics.composition_tests()
                reached=reachability(physics)
                paid_active=set(lookup)
                paid_random={(s,a) for s,a,y in ledgers["random"]}
                scores={
                    "candidate":eval_model(learned_predictions,truth,paid_active,tasks),
                    "random":eval_model(random_preds,truth,paid_random),
                    "degree2":eval_model(degree2_preds,truth,paid_active),
                    "readout":eval_model(readout_preds,truth,paid_active),
                    "memory":eval_model(memory_preds,truth,paid_active),
                    "symbolic":eval_model(symbolic_preds,truth,paid_active)
                }
                initial_true={key:v for key,v in initial_predictions.items()
                              if v is not None and v==truth[key]}
                old_retained=sum(int(learned_predictions[k]==v)
                                 for k,v in initial_true.items())
                if not negative:
                    scores["MLP_confident"]=eval_model(mlp_confident,truth,paid_active)
                    scores["MLP_forced"]=eval_model(mlp_forced,truth,paid_active)
                    scores["MLP_matched"]=eval_model(mlp_matched,truth,paid_active)
                receipt={
                    "seed":seed,"family":physics.family,"source":physics.receipt(),
                    "eval_reachable_public_states":reached,
                    "paid_physical_charges_candidate":144,
                    "paid_physical_charges_random":144,
                    "paid_A_public_SHA256":digest(ledgers["candidate"][:96]),
                    "paid_B_candidate_SHA256":digest(ledgers["candidate"][96:]),
                    "paid_B_random_SHA256":digest(ledgers["random"][96:]),
                    "private_evaluator_heldout_SHA256":digest(
                        [[s,a,z] for (s,a),z in truth.items()]),
                    "stageA_cold_numeric_SHA256":sha256(initial.snapshot().encode("ascii")).hexdigest(),
                    "stageB_cold_numeric_SHA256":sha256(cold.snapshot().encode("ascii")).hexdigest(),
                    "stageA_compiler":StageA,
                    "stageB_compiler":compiled,
                    "random_compiler":random_compiled,
                    "degree2_fixed_grammar_compiler":degree2_compiled,
                    "physically_paid_coverage_candidate":coverage(ledgers["candidate"]),
                    "physically_paid_coverage_random":coverage(ledgers["random"]),
                    "same_prereg_hypothesis_symbolic_parity":True,
                    "scores":scores,
                    "old_true_confident_stageA_count":len(initial_true),
                    "old_retained":old_retained,
                    "fully_trained_MLP":mlp_info,
                    "active_policy_CPU_ns":t_policy,
                    "total_candidate_training_CPU_ns":candidate_train,
                    "cold_numeric_eval_CPU_ns":neural_eval,
                    "MLP_training_CPU_ns":mlp_train_ns,
                    "MLP_evaluation_CPU_ns":mlp_eval_ns
                }
                worlds.append(receipt)
                totals["worlds"]+=1
                totals["paid_actions"]+=288
                totals["reachable_full_64_worlds"]+=int(reached==64)
                totals["cold_numeric_worlds"]+=1
                totals["symbolic_exact_parity_worlds"]+=1
                if negative:
                    totals["negative_worlds"]+=1
                    totals["negative_correct"]+=scores["candidate"]["physical"]["correct"]
                    totals["negative_wrong"]+=scores["candidate"]["physical"]["wrong_confident"]
                    totals["negative_inconsistent_actions"]+=len(
                        compiled["inconsistent_public_actions"])
                else:
                    totals["primary_worlds"]+=1
                    totals["primary_physical_cases"]+=384
                    totals["primary_two_action_tasks"]+=32
                    for name,alias in (("candidate","candidate"),
                                       ("random","random"),
                                       ("degree2","degree2"),
                                       ("readout","readout"),
                                       ("memory","memory"),
                                       ("MLP_confident","MLP_confident"),
                                       ("MLP_forced","MLP_forced"),
                                       ("MLP_matched","MLP_matched")):
                        for stat,target in (("correct","correct"),
                                             ("wrong","wrong_confident")):
                            totals[f"{alias}_{stat}"]+=scores[name]["physical"][target]
                    totals["candidate_abstain"]+=scores["candidate"]["physical"]["abstain"]
                    totals["candidate_never_paid_correct"]+=scores["candidate"][
                        "genuinely_never_charged"]["correct"]
                    totals["candidate_never_paid_wrong"]+=scores["candidate"][
                        "genuinely_never_charged"]["wrong_confident"]
                    totals["candidate_never_paid_count"]+=scores["candidate"][
                        "genuinely_never_charged"]["total"]
                    totals["candidate_two_action_correct"]+=scores["candidate"][
                        "two_action"]["correct"]
                    totals["candidate_two_action_wrong"]+=scores["candidate"][
                        "two_action"]["wrong_confident"]
                    totals["stageA_true_confident"]+=len(initial_true)
                    totals["stageA_retained"]+=old_retained
                    totals["primary_inconsistent_actions"]+=len(
                        compiled["inconsistent_public_actions"])
                    totals["numeric_neural_parameters"]+=compiled["numeric_weight_parameter_count"]
                    totals["numeric_confidence_detectors"]+=compiled[
                        "numeric_confident_public_inputs"]
                    totals["surviving_sparse_hypotheses"]+=compiled[
                        "sum_surviving_sparse_hypotheses"]
                    totals["candidate_train_cpu_ns"]+=candidate_train
                    totals["candidate_eval_cpu_ns"]+=neural_eval
                    totals["MLP_train_cpu_ns"]+=mlp_train_ns
                    totals["MLP_eval_cpu_ns"]+=mlp_eval_ns
                    totals["MLP_converged"]+=int(mlp_info["fully_trained"])
                    totals["MLP_gradient_updates"]+=mlp_info["gradient_updates_total"]
                    totals["candidate_paid_unique"]+=coverage(
                        ledgers["candidate"])["unique_paid_public_inputs"]
                    totals["random_paid_unique"]+=coverage(
                        ledgers["random"])["unique_paid_public_inputs"]
                    if physics.family=="cubic_degree3":
                        totals["degree3_correct"]+=scores["candidate"]["physical"]["correct"]
                        totals["degree3_degree2_correct"]+=scores["degree2"]["physical"]["correct"]
                    bucket=by_family.setdefault(physics.family,{
                        "worlds":0,"candidate_correct":0,"candidate_wrong":0,
                        "degree2_correct":0,"random_correct":0,
                        "never_paid_correct":0,"never_paid_total":0,
                        "MLP_matched_correct":0})
                    bucket["worlds"]+=1
                    bucket["candidate_correct"]+=scores["candidate"]["physical"]["correct"]
                    bucket["candidate_wrong"]+=scores["candidate"]["physical"]["wrong_confident"]
                    bucket["degree2_correct"]+=scores["degree2"]["physical"]["correct"]
                    bucket["random_correct"]+=scores["random"]["physical"]["correct"]
                    bucket["never_paid_correct"]+=scores["candidate"][
                        "genuinely_never_charged"]["correct"]
                    bucket["never_paid_total"]+=scores["candidate"][
                        "genuinely_never_charged"]["total"]
                    bucket["MLP_matched_correct"]+=scores["MLP_matched"]["physical"]["correct"]
        self.assertEqual(totals["worlds"],16)
        self.assertEqual(totals["primary_worlds"],12)
        self.assertEqual(totals["negative_worlds"],4)
        self.assertEqual(totals["paid_actions"],4608)
        self.assertEqual(totals["primary_physical_cases"],4608)
        self.assertEqual(totals["primary_two_action_tasks"],384)
        self.assertEqual(totals["symbolic_exact_parity_worlds"],16)
        self.assertGreaterEqual(totals["candidate_never_paid_count"],2880)
        old_fraction=totals["stageA_retained"]/max(1,totals["stageA_true_confident"])
        cpu=(totals["candidate_train_cpu_ns"]+totals["candidate_eval_cpu_ns"])/max(
            1,totals["MLP_train_cpu_ns"]+totals["MLP_eval_cpu_ns"])
        criteria={
            "16_worlds_64_states_reachable":totals["reachable_full_64_worlds"]==16,
            "primary_correct_ge_1450":totals["candidate_correct"]>=1450,
            "unpaid_correct_ge_680":totals["candidate_never_paid_correct"]>=680,
            "unpaid_contexts_ge_2880":totals["candidate_never_paid_count"]>=2880,
            "confident_wrong_primary_le_8":totals["candidate_wrong"]<=8,
            "degree3_worlds_correct_ge_400":totals["degree3_correct"]>=400,
            "degree3_gain_vs_degree2_ge_100":
                totals["degree3_correct"]-totals["degree3_degree2_correct"]>=100,
            "same_ledger_readout_gain_ge_300":
                totals["candidate_correct"]-totals["readout_correct"]>=300,
            "beat_converged_MLP_matched_coverage_ge_20":
                totals["candidate_correct"]-totals["MLP_matched_correct"]>=20,
            "candidate_no_more_wrong_than_MLP_matched":
                totals["candidate_wrong"]<=totals["MLP_matched_wrong"],
            "old_true_confident_retention_ge_95pct":old_fraction>=0.95,
            "two_action_correct_ge_100":totals["candidate_two_action_correct"]>=100,
            "degree4_negative_wrong_le_20":totals["negative_wrong"]<=20,
            "degree4_negative_inconsistent_actions_ge_4":
                totals["negative_inconsistent_actions"]>=4,
            "random_policy_not_ahead_by_more_than_50":
                totals["candidate_correct"]+50>=totals["random_correct"],
            "symbolic_independent_exact_parity_16":
                totals["symbolic_exact_parity_worlds"]==16,
            "cold_numeric_tamper_16":totals["cold_numeric_worlds"]==16,
            "conventional_MLP_converged_worlds_ge_10":totals["MLP_converged"]>=10,
            "whole_train_infer_CPU_over_MLP_le_15":cpu<=1.5
        }
        verdict=("SELFTEST_SIGNAL" if all(criteria.values()) else
                 "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP79_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":verdict,"frozen_criteria":criteria,
            "totals":totals,"old_true_confident_retention":round(old_fraction,8),
            "candidate_vs_MLP_whole_training_inference_CPU_ratio":round(cpu,8),
            "by_family":by_family,"worlds":worlds
        },sort_keys=True,separators=(",",":")))
        # Exact source negative science must not masquerade as test failure.


if __name__=="__main__":
    unittest.main()

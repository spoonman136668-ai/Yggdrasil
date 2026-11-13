"""WSP77 prospectively frozen SIX-bit paid action learning, numerical weight editing.

The model/policy imports only numeric source-blind modules; PRIVATE physics
is imported by this evaluator-only unittest. All three 144-action training
trajectories are independently PHYSICALLY PAID, continuous and no-reset.
Every 384 state/action heldout source label is only read AFTER all neural
weights and source-blind action policies have finished training. Scientific
failures are recorded, not hidden as failing engineering unit tests.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
from random import Random
import sys,time,json,unittest

from source import SEEDS,STATES,ACTIONS,TRAIN_ACTIONS,build_world
from neural6 import FeatureGrowthNeural
from physical_contrasts6 import (
    choose_observed_contrast,uniform_random,balanced_cycle,
    paid_action_contrasts,repair,fitted_readout
)
from fully_trained_mlp6 import EndToEndAdamControl


def sha(data):
    return sha256(json.dumps(data,sort_keys=True,separators=(",",":"),
        default=list,ensure_ascii=True).encode("ascii")).hexdigest()


class ExactPaidMemory:
    def __init__(self,rows):
        self.paid={}
        for state,action,out in rows:
            if (state,action) in self.paid and self.paid[(state,action)]!=out:
                raise ValueError("hidden-state collision in deterministic control")
            self.paid[(state,action)]=out
    def predict(self,state,action):
        return self.paid.get((state,action))


class PhysicalDecisionTree:
    """Independent conventional fitted depth-4 bitwise classification trees.

    Uses ONLY 144 charged public state/action/consequence samples; no private
    evaluator labels or numeric WSP77 feature grammar. Each action and output
    bit gets its own greedy deterministic feature-split tree, depth <=4.
    Predicts all six outputs by six ordinary trees and never abstains.
    """
    def __init__(self,rows):
        self.trees={}
        for action in ACTIONS:
            charged=[(s,y) for s,a,y in rows if a==action]
            for bit in range(6):
                self.trees[(action,bit)]=self._fit(charged,bit,4,())

    def _fit(self,rows,bit,depth,used):
        labels=[y[bit] for s,y in rows]
        ones=sum(labels)
        answer=int(ones*2>=len(labels)) if labels else 0
        if depth==0 or len(rows)<3 or ones==0 or ones==len(labels):
            return ("leaf",answer)
        best=None
        for feature in range(6):
            if feature in used:
                continue
            groups=(
                [(s,y) for s,y in rows if s[feature]==0],
                [(s,y) for s,y in rows if s[feature]==1]
            )
            if not groups[0] or not groups[1]:
                continue
            # weighted Gini leaf impurity; deterministic feature tie.
            impurity=sum(2*sum(y[bit] for s,y in g)*
                          (len(g)-sum(y[bit] for s,y in g))/len(g)
                          for g in groups)
            key=(impurity,feature)
            if best is None or key<best[0]:
                best=(key,feature,groups)
        if best is None:
            return ("leaf",answer)
        _,feature,groups=best
        return ("node",feature,
                self._fit(groups[0],bit,depth-1,used+(feature,)),
                self._fit(groups[1],bit,depth-1,used+(feature,)))

    @staticmethod
    def _predict_node(tree,s):
        while tree[0]=="node":
            tree=tree[2+s[tree[1]]]
        return tree[1]

    def predict(self,state,action):
        return tuple(self._predict_node(self.trees[(action,bit)],state)
                     for bit in range(6))


def evaluate_predictions(predictions,truth,paid,tasks=None):
    output={"correct":0,"wrong_confident":0,"abstain":0}
    unseen={"correct":0,"wrong_confident":0,"abstain":0,"total":0}
    for key,actual in truth.items():
        predicted=predictions.get(key)
        label=("abstain" if predicted is None else
               "correct" if predicted==actual else "wrong_confident")
        output[label]+=1
        if key not in paid:
            unseen[label]+=1
            unseen["total"]+=1
    assert sum(output.values())==384
    assert sum(unseen[x] for x in output)==unseen["total"]
    record={"physical":output,"never_paid":unseen}
    if tasks is not None:
        composed={"correct":0,"wrong_confident":0,"abstain":0}
        for task in tasks:
            a,b=task.actions
            mid=predictions.get((task.start,a))
            finish=predictions.get((mid,b)) if mid is not None else None
            name=("abstain" if finish is None else
                  "correct" if finish==task._finish else "wrong_confident")
            composed[name]+=1
        assert sum(composed.values())==len(tasks)
        record["two_action"]=composed
    return record


def cached_predictions(model):
    return {(s,a):model.predict(s,a) for s in STATES for a in ACTIONS}


def physical_reachability(world):
    visited={(0,)*6}
    queue=[(0,)*6]
    while queue:
        state=queue.pop()
        for action in ACTIONS:
            after=world._step_oracle(state,action)
            if after not in visited:
                visited.add(after)
                queue.append(after)
    return len(visited)


def old_retention(stageA,candidate,truth):
    baseline=candidate_keep=0
    for k,actual in truth.items():
        if stageA[k] is not None and stageA[k]==actual:
            baseline+=1
            candidate_keep+=int(candidate[k]==actual)
    return {"eligible":baseline,"retained":candidate_keep}


def charged_coverage(rows):
    pairs={(s,a) for s,a,y in rows}
    states={rows[0][0]} | {y for s,a,y in rows}
    return {
        "distinct_paid_pairs":len(pairs),
        "distinct_visited_states":len(states),
        "A_paired_contrasts":len(paid_action_contrasts(rows[:96])),
        "AB_paired_contrasts":len(paid_action_contrasts(rows)),
        "new_B_contrasts":len(
            set(paid_action_contrasts(rows))-
            set(paid_action_contrasts(rows[:96]))),
        "B_public_action_counts":[sum(int(a==channel)
            for s,a,y in rows[96:]) for channel in ACTIONS]
    }


class FrozenSixBitIndependentHoldout(unittest.TestCase):
    def test_source_blindness_and_algebraic_unseen_bound(self):
        root=Path(__file__).parent
        for path in ("neural6.py","repair6.py","physical_contrasts6.py",
                     "fully_trained_mlp6.py"):
            code=(root/path).read_text("utf-8")
            for illegal in ("from source import","import source",
                            "_step_oracle","from weight_programmer import"):
                self.assertNotIn(illegal,code)
        self.assertEqual(len(STATES),64)
        self.assertEqual(len(ACTIONS),6)
        self.assertEqual(len(SEEDS),16)
        self.assertEqual(TRAIN_ACTIONS,144)
        self.assertEqual(len(balanced_cycle(5101)),48)
        self.assertEqual([balanced_cycle(5101).count(a) for a in ACTIONS],
                         [8]*6)
        self.assertEqual(len(STATES)*len(ACTIONS)-TRAIN_ACTIONS,240)
        for seed in SEEDS:
            world=build_world(seed)
            self.assertEqual(world.receipt(),build_world(seed).receipt())
            self.assertEqual(len(world.composition_tests()),32)
        for cohort in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(5101,cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(5001)
        world=build_world(5101)
        session=world.training_session()
        for i in range(144):
            session.step(i%6)
        with self.assertRaises(ValueError):
            session.step(0)
        zero=(0,)*6
        sample=[(zero,0,zero)]*96
        with self.assertRaises(ValueError):
            choose_observed_contrast((1,0,0,0,0,0),sample,5101,0)
        with self.assertRaises(ValueError):
            choose_observed_contrast(zero,sample[:95],5101,0)
        self.assertIn(choose_observed_contrast(zero,sample,5101,0),ACTIONS)
        self.assertEqual(len(paid_action_contrasts(
            [(zero,0,zero),(zero,1,(1,0,0,0,0,0))])),1)

    def test_frozen_six_bit_physical_generalization_and_neural_baselines(self):
        keys=(
            "worlds","primary_worlds","negative_worlds","paid_real_actions",
            "reachability_full_worlds","all_16_cold_snapshots",
            "primary_physical_cases","primary_compositions",
            "observed_correct","observed_wrong","observed_abstain",
            "random_correct","random_wrong","balanced_correct","balanced_wrong",
            "readout_correct","readout_wrong","random_edit_correct",
            "random_edit_wrong","exact_correct","exact_wrong",
            "tree_correct","tree_wrong","MLP_correct","MLP_wrong",
            "MLP_forced_correct","MLP_forced_wrong","MLP_converged",
            "MLP_gradient_steps","MLP_training_ns",
            "observed_never_paid_count","observed_never_paid_correct",
            "observed_never_paid_wrong","random_never_paid_correct",
            "observed_two_step_correct","observed_two_step_wrong",
            "StageA_eligible","StageA_retained",
            "actual_hidden_edits_worlds","observed_paid_contexts",
            "random_paid_contexts","balanced_paid_contexts",
            "observed_B_new_contrasts","random_B_new_contrasts",
            "balanced_B_new_contrasts","observed_policy_ns",
            "random_policy_ns","balanced_policy_ns",
            "observed_repair_ns","random_repair_ns",
            "observed_eval_ns","random_eval_ns",
            "negative_observed_correct","negative_observed_wrong"
        )
        total={k:0 for k in keys}
        records=[]
        families={}
        for seed in SEEDS:
            with self.subTest(seed=seed):
                negative=seed>=5113
                physical=build_world(seed)
                copies={name:build_world(seed).training_session()
                        for name in ("observed","random","balanced")}
                rng=Random(int.from_bytes(sha256(
                    f"WSP77|identically-paid-A|{seed}".encode("ascii")
                ).digest(),"big"))
                learner=FeatureGrowthNeural("residual",seed=seed)
                paid={name:[] for name in copies}
                for i in range(96):
                    action=rng.choice(ACTIONS)
                    transitions={n:s.step(action) for n,s in copies.items()}
                    row=transitions["observed"]
                    record=(row.before,row.action,row.after)
                    for n,o in transitions.items():
                        tup=(o.before,o.action,o.after)
                        self.assertEqual(tup,record)
                        paid[n].append(tup)
                    learner.charge(row)
                    if i+1 in (48,96):
                        learner.grow()
                self.assertEqual(learner.charged_actions,96)
                self.assertEqual(learner.growth_rounds,2)
                stageA=learner.snapshot()
                self.assertEqual(FeatureGrowthNeural.restore(stageA).snapshot(),stageA)
                Bpolicy_ns={n:0 for n in copies}
                rand=uniform_random(seed)
                cyclic=balanced_cycle(seed)
                for step in range(48):
                    tick=time.process_time_ns()
                    selected=choose_observed_contrast(
                        copies["observed"].state,paid["observed"],seed,step)
                    Bpolicy_ns["observed"]+=time.process_time_ns()-tick
                    tick=time.process_time_ns()
                    action_random=rand.choice(ACTIONS)
                    Bpolicy_ns["random"]+=time.process_time_ns()-tick
                    tick=time.process_time_ns()
                    action_balanced=cyclic[step]
                    Bpolicy_ns["balanced"]+=time.process_time_ns()-tick
                    for name,action in (("observed",selected),
                                         ("random",action_random),
                                         ("balanced",action_balanced)):
                        row=copies[name].step(action)
                        paid[name].append((row.before,row.action,row.after))
                for name,source in copies.items():
                    self.assertEqual(len(source.ledger),144)
                    self.assertEqual(len(paid[name]),144)
                    self.assertEqual(paid[name][0][0],(0,)*6)
                    self.assertTrue(all(paid[name][i][2]==paid[name][i+1][0]
                        for i in range(143)))
                self.assertEqual(paid["observed"][:96],paid["random"][:96])
                self.assertEqual(paid["observed"][:96],paid["balanced"][:96])
                networks={}
                edit_receipts={}
                repair_ns={}
                for name in copies:
                    tick=time.process_time_ns()
                    networks[name],edit_receipts[name]=repair(
                        stageA,paid[name][:96],paid[name][96:],
                        "counterexample",seed)
                    repair_ns[name]=time.process_time_ns()-tick
                refit=fitted_readout(stageA,paid["observed"][:96],
                                     paid["observed"][96:])
                noisy,noisy_receipt=repair(
                    stageA,paid["observed"][:96],paid["observed"][96:],
                    "random",seed)
                self.assertEqual(noisy_receipt["direct_gradient_steps"],0)
                self.assertEqual(edit_receipts["observed"]["direct_gradient_steps"],0)
                self.assertLessEqual(
                    edit_receipts["observed"]["changed_hidden_coefficients"],4)
                for model in list(networks.values())+[refit,noisy]:
                    self.assertEqual(len(model.hidden_weights),
                                     len(learner.hidden_weights))
                    self.assertEqual(model.growth_rounds,2)
                    snap=model.snapshot()
                    self.assertNotIn('"ledger"',snap)
                    self.assertNotIn('"source"',snap)
                    restored=FeatureGrowthNeural.restore(snap)
                    self.assertEqual(restored.snapshot(),snap)
                    with self.assertRaises(ValueError):
                        FeatureGrowthNeural.restore(snap.replace(
                            "wsp77.neural-feature-growth.v1",
                            "wsp77.neural-feature-growth.v2"))
                    for s in STATES[::4]:
                        for a in ACTIONS:
                            self.assertEqual(restored.predict(s,a),model.predict(s,a))
                # ALL evaluation labels are read ONLY from this point onward,
                # after real training, policy, and cold weight snapshots froze.
                truth={(s,a):physical._step_oracle(s,a)
                       for s in STATES for a in ACTIONS}
                tasks=physical.composition_tests()
                reach=physical_reachability(physical)
                cache={}
                evalCPU={}
                for name,m in networks.items():
                    tick=time.process_time_ns()
                    cache[name]=cached_predictions(m)
                    evalCPU[name]=time.process_time_ns()-tick
                cache["readout"]=cached_predictions(refit)
                cache["random_edit"]=cached_predictions(noisy)
                exact=ExactPaidMemory(paid["observed"])
                tree=PhysicalDecisionTree(paid["observed"])
                cache["exact"]=cached_predictions(exact)
                cache["tree"]=cached_predictions(tree)
                cache["stageA"]=cached_predictions(learner)
                scores={}
                for name,pred in cache.items():
                    pairs={(s,a) for s,a,y in paid[
                        name if name in copies else "observed"]}
                    scores[name]=evaluate_predictions(
                        pred,truth,pairs,tasks if name=="observed" else None)
                old=old_retention(cache["stageA"],cache["observed"],truth)
                mlp_fit=None
                mlp_ns=0
                if not negative:
                    baseline=EndToEndAdamControl(seed)
                    tick=time.process_time_ns()
                    mlp_fit=baseline.fit(paid["observed"])
                    mlp_ns=time.process_time_ns()-tick
                    mlp_conf=cached_predictions(type("Adapter",(),{
                        "predict":lambda self,s,a:baseline.predict(
                            s,a,confidence=True)})())
                    mlp_forced=cached_predictions(baseline)
                    scores["MLP"]=evaluate_predictions(
                        mlp_conf,truth,{(s,a) for s,a,y in paid["observed"]})
                    scores["MLP_forced"]=evaluate_predictions(
                        mlp_forced,truth,{(s,a) for s,a,y in paid["observed"]})
                coverage={n:charged_coverage(rows) for n,rows in paid.items()}
                report={
                    "seed":seed,"family":physical.family,
                    "source":physical.receipt(),
                    "evaluator_only_reachable_states":reach,
                    "paid_A_sha256":{n:sha(rows[:96]) for n,rows in paid.items()},
                    "paid_B_sha256":{n:sha(rows[96:]) for n,rows in paid.items()},
                    "physical_charges_per_policy":144,
                    "real_paid_charges_across_three_world_copies":432,
                    "StageA_numeric_sha256":sha256(stageA.encode("ascii")).hexdigest(),
                    "trained_cold_numeric_sha256":{n:sha256(
                        m.snapshot().encode("ascii")).hexdigest()
                        for n,m in networks.items()},
                    "same_ledger_readout_numeric_sha256":sha256(
                        refit.snapshot().encode("ascii")).hexdigest(),
                    "same_ledger_random_hidden_numeric_sha256":sha256(
                        noisy.snapshot().encode("ascii")).hexdigest(),
                    "hidden_coordinate_edits":edit_receipts,
                    "random_hidden_edit":noisy_receipt,
                    "real_paid_coverage_and_contrasts":coverage,
                    "scores":scores,
                    "StageA_old_truth_retention":old,
                    "MLP_training":mlp_fit,
                    "policy_CPU_ns":Bpolicy_ns,
                    "direct_repair_CPU_ns":repair_ns,
                    "numerical_audit_CPU_ns":evalCPU,
                    "MLP_train_CPU_ns":mlp_ns,
                    "heldout_source_truth_sha256":sha(sorted(
                        ((s,a,out) for (s,a),out in truth.items())))
                }
                records.append(report)
                total["worlds"]+=1
                total["paid_real_actions"]+=432
                total["reachability_full_worlds"]+=int(reach==64)
                total["all_16_cold_snapshots"]+=1
                if negative:
                    total["negative_worlds"]+=1
                    total["negative_observed_correct"]+=scores["observed"][
                        "physical"]["correct"]
                    total["negative_observed_wrong"]+=scores["observed"][
                        "physical"]["wrong_confident"]
                else:
                    total["primary_worlds"]+=1
                    total["primary_physical_cases"]+=384
                    total["primary_compositions"]+=32
                    for n,field in (("observed","observed"),
                                    ("random","random"),
                                    ("balanced","balanced"),
                                    ("readout","readout"),
                                    ("random_edit","random_edit"),
                                    ("exact","exact"),
                                    ("tree","tree"),
                                    ("MLP","MLP"),
                                    ("MLP_forced","MLP_forced")):
                        for suffix,metric in (("correct","correct"),
                                              ("wrong","wrong_confident")):
                            total[f"{field}_{suffix}"]+=scores[n]["physical"][metric]
                    total["observed_abstain"]+=scores["observed"]["physical"]["abstain"]
                    total["observed_never_paid_count"]+=scores["observed"]["never_paid"]["total"]
                    total["observed_never_paid_correct"]+=scores["observed"]["never_paid"]["correct"]
                    total["observed_never_paid_wrong"]+=scores["observed"]["never_paid"]["wrong_confident"]
                    total["random_never_paid_correct"]+=scores["random"]["never_paid"]["correct"]
                    total["observed_two_step_correct"]+=scores["observed"]["two_action"]["correct"]
                    total["observed_two_step_wrong"]+=scores["observed"]["two_action"]["wrong_confident"]
                    total["StageA_eligible"]+=old["eligible"]
                    total["StageA_retained"]+=old["retained"]
                    for n in copies:
                        total[f"{n}_paid_contexts"]+=coverage[n]["distinct_paid_pairs"]
                        total[f"{n}_B_new_contrasts"]+=coverage[n]["new_B_contrasts"]
                        total[f"{n}_policy_ns"]+=Bpolicy_ns[n]
                    total["actual_hidden_edits_worlds"]+=int(
                        edit_receipts["observed"]["changed_hidden_coefficients"]>0)
                    total["observed_repair_ns"]+=repair_ns["observed"]
                    total["random_repair_ns"]+=repair_ns["random"]
                    total["observed_eval_ns"]+=evalCPU["observed"]
                    total["random_eval_ns"]+=evalCPU["random"]
                    total["MLP_converged"]+=int(mlp_fit["fully_trained"])
                    total["MLP_gradient_steps"]+=mlp_fit["gradient_updates_total"]
                    total["MLP_training_ns"]+=mlp_ns
                    f=families.setdefault(physical.family,{
                        "worlds":0,"observed_correct":0,"random_correct":0,
                        "balanced_correct":0,"readout_correct":0,
                        "MLP_correct":0,"unseen_correct":0,"unseen_total":0})
                    f["worlds"]+=1
                    f["observed_correct"]+=scores["observed"]["physical"]["correct"]
                    f["random_correct"]+=scores["random"]["physical"]["correct"]
                    f["balanced_correct"]+=scores["balanced"]["physical"]["correct"]
                    f["readout_correct"]+=scores["readout"]["physical"]["correct"]
                    f["MLP_correct"]+=scores["MLP"]["physical"]["correct"]
                    f["unseen_correct"]+=scores["observed"]["never_paid"]["correct"]
                    f["unseen_total"]+=scores["observed"]["never_paid"]["total"]
        self.assertEqual(total["worlds"],16)
        self.assertEqual(total["primary_worlds"],12)
        self.assertEqual(total["negative_worlds"],4)
        self.assertEqual(total["paid_real_actions"],6912)
        self.assertEqual(total["primary_physical_cases"],4608)
        self.assertEqual(total["primary_compositions"],384)
        self.assertGreaterEqual(total["observed_never_paid_count"],2880)
        self.assertEqual(total["all_16_cold_snapshots"],16)
        retention=(total["StageA_retained"]/max(1,total["StageA_eligible"]))
        cpu_ratio=(total["observed_policy_ns"]+total["observed_repair_ns"]+
                   total["observed_eval_ns"])/max(1,
                   total["random_policy_ns"]+total["random_repair_ns"]+
                   total["random_eval_ns"])
        frozen={
            "all_16_source_states_reachable_64":total["reachability_full_worlds"]==16,
            "primary_confident_correct_ge_600":total["observed_correct"]>=600,
            "gain_over_equal_paid_random_ge_40":
                total["observed_correct"]-total["random_correct"]>=40,
            "gain_over_equal_paid_balanced_ge_40":
                total["observed_correct"]-total["balanced_correct"]>=40,
            "gain_vs_same_ledger_readout_ge_35":
                total["observed_correct"]-total["readout_correct"]>=35,
            "gain_vs_same_ledger_random_hidden_ge_35":
                total["observed_correct"]-total["random_edit_correct"]>=35,
            "at_least_2880_unpaid_primary_contexts":
                total["observed_never_paid_count"]>=2880,
            "true_never_paid_correct_ge_250":
                total["observed_never_paid_correct"]>=250,
            "true_never_paid_gain_vs_random_ge_40":
                total["observed_never_paid_correct"]-
                total["random_never_paid_correct"]>=40,
            "primary_wrong_confident_le_60":total["observed_wrong"]<=60,
            "StageA_true_confident_retention_ge_80pct":retention>=0.8,
            "two_action_compositions_ge_90":total["observed_two_step_correct"]>=90,
            "negative_confident_wrong_le_30":total["negative_observed_wrong"]<=30,
            "hidden_coefficients_changed_in_10_worlds":
                total["actual_hidden_edits_worlds"]>=10,
            "all_16_numeric_cold_restore_tamper":
                total["all_16_cold_snapshots"]==16,
            "conventional_neural_fully_trained_in_10_worlds":
                total["MLP_converged"]>=10,
            "policy_repair_audit_CPU_over_random_le_8":cpu_ratio<=8.0
        }
        verdict=("SELFTEST_SIGNAL" if all(frozen.values()) else
                 "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP77_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":verdict,"criteria":frozen,"totals":total,
            "retention_fraction":round(retention,8),
            "candidate_over_random_CPU_ratio":round(cpu_ratio,6),
            "families":families,"worlds":records
        },sort_keys=True,separators=(",",":")))
        # Frozen scientific misses are data, not green scientific acceptance.


if __name__=="__main__":
    unittest.main()

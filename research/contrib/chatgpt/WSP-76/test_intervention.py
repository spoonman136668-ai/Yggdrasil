"""WSP76 frozen reachable-contrast intervention vs equal-paid balanced and random.

Each world has three SEPARATELY PHYSICALLY CHARGED 144-action no-reset
streams. The first 96 paid actions/observations are identical but charged
THREE times. Each B policy chooses 48 real future actions independently.
No source-private roles, outcomes or evaluator truth enter action policy,
numerical weight programmer, MLP baseline or B training.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from random import Random
import sys,time,json,unittest

from source import SEEDS,STATES,ACTIONS,TRAIN_ACTIONS,build_world
from empirical_policy import (
    choose_observed_contrast,uniform_random,balanced_cycle,
    paid_action_contrasts,repair,fitted_readout
)

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"WSP-70"))
from interaction_writer import ReusableInteractionNeural
sys.path.insert(0,str(ROOT/"WSP-69"))
from growing_neural import FeatureGrowthNeural
sys.path.insert(0,str(ROOT/"WSP-74"))
from independent_end_to_end import EndToEndAdamControl
sys.path.insert(0,str(ROOT/"WSP-67"))
from independent_symbolic import ExactMemory
sys.path.insert(0,str(ROOT/"WSP-64"))
from independent_tree import IndependentTreeControl


def digest(data):
    return sha256(json.dumps(data,sort_keys=True,
        separators=(",",":"),default=list).encode("ascii")).hexdigest()


def evaluate(predict,world,charged_pairs,compositions=None):
    physical={"correct":0,"wrong_confident":0,"abstain":0}
    unseen={"correct":0,"wrong_confident":0,"abstain":0,"total":0}
    for state in STATES:
        for action in ACTIONS:
            pred=predict(state,action)
            true=world._step_oracle(state,action)
            verdict=("abstain" if pred is None else
                     "correct" if pred==true else "wrong_confident")
            physical[verdict]+=1
            if (state,action) not in charged_pairs:
                unseen[verdict]+=1
                unseen["total"]+=1
    assert sum(physical.values())==64
    assert sum(v for k,v in unseen.items() if k!="total")==unseen["total"]
    out={"physical":physical,"never_paid":unseen}
    if compositions is not None:
        comp={"correct":0,"wrong_confident":0,"abstain":0}
        for task in compositions:
            first,second=task.actions
            mid=predict(task.start,first)
            result=predict(mid,second) if mid is not None else None
            verdict=("abstain" if result is None else
                     "correct" if result==task._finish else "wrong_confident")
            comp[verdict]+=1
        assert sum(comp.values())==len(compositions)
        out["two_action"]=comp
    return out


def retention(predict,original,world):
    eligible=retained=0
    for s in STATES:
        for a in ACTIONS:
            pred=original.predict(s,a)
            if pred is not None and pred==world._step_oracle(s,a):
                eligible+=1
                retained+=int(predict(s,a)==pred)
    return {"stageA_true_confident":eligible,"retained":retained}


class FrozenReachableNoveltyIntervention(unittest.TestCase):
    def test_source_blind_contrast_policy_and_physically_paid_boundaries(self):
        body=(Path(__file__).parent/"empirical_policy.py").read_text("utf-8")
        for forbidden in ("from source import","import source",
                          "_step_oracle","from weight_programmer import",
                          "torch","backward("):
            self.assertNotIn(forbidden,body)
        self.assertEqual(len(SEEDS),16)
        self.assertEqual(TRAIN_ACTIONS,144)
        self.assertEqual(len(balanced_cycle(5001)),48)
        self.assertEqual([balanced_cycle(5001).count(a) for a in ACTIONS],
                         [12,12,12,12])
        for seed in SEEDS:
            w=build_world(seed)
            self.assertEqual(w.receipt(),build_world(seed).receipt())
            self.assertEqual(len(w.composition_tests()),32)
        for cohort in ("DEV","PRIMARY"):
            with self.assertRaises(PermissionError):
                build_world(5001,cohort=cohort)
        with self.assertRaises(PermissionError):
            build_world(4901)
        world=build_world(5001)
        session=world.training_session()
        for i in range(144):
            session.step(i%4)
        with self.assertRaises(ValueError):
            session.step(0)
        zero=(0,0,0,0)
        sample=[(zero,0,zero)]*96
        with self.assertRaises(ValueError):
            choose_observed_contrast((0,0,0,1),sample,5001,0)
        with self.assertRaises(ValueError):
            choose_observed_contrast(zero,sample[:95],5001,0)
        self.assertIn(choose_observed_contrast(zero,sample,5001,0),ACTIONS)
        contrast_paid=[
            (zero,0,zero),
            (zero,1,(1,0,0,0))
        ]
        self.assertEqual(len(paid_action_contrasts(contrast_paid)),1)
        with self.assertRaises(ValueError):
            paid_action_contrasts([(zero,0,zero),((1,0,0,0),1,zero)])

    def test_frozen_three_paid_streams_same_weights_and_independent_controls(self):
        names=(
            "worlds","primary_worlds","negative_worlds",
            "reachable_worlds_ge12","total_real_paid_actions","primary_physical_cases",
            "primary_composition_cases","contrast_correct","contrast_wrong",
            "contrast_abstain","contrast_unseen_correct","contrast_unseen_wrong",
            "contrast_unseen_total","contrast_two_action_correct",
            "contrast_two_action_wrong",
            "balanced_correct","balanced_wrong",
            "balanced_unseen_correct",
            "random_correct","random_wrong","random_unseen_correct",
            "readout_correct","readout_wrong",
            "random_hidden_correct","random_hidden_wrong",
            "exact_memory_correct","exact_memory_wrong",
            "decision_tree_correct","decision_tree_wrong",
            "MLP_confident_correct","MLP_confident_wrong",
            "MLP_forced_correct","MLP_forced_wrong",
            "MLP_converged","MLP_gradient_updates","MLP_training_cpu_ns",
            "old_stageA_eligible","old_stageA_retained",
            "contrast_unique_paid_contexts","balanced_unique_paid_contexts",
            "random_unique_paid_contexts","contrast_unique_visited_states",
            "balanced_unique_visited_states","random_unique_visited_states",
            "contrast_new_B_contexts","balanced_new_B_contexts",
            "random_new_B_contexts",
            "contrast_incremental_action_contrasts",
            "balanced_incremental_action_contrasts",
            "random_incremental_action_contrasts","contrast_actually_new_B_states",
            "balanced_actually_new_B_states","random_actually_new_B_states",
            "primary_worlds_with_actual_hidden_edits",
            "cold_snapshot_tamper_worlds","contrast_cpu_ns",
            "random_cpu_ns","contrast_policy_cpu_ns",
            "balanced_policy_cpu_ns","random_policy_cpu_ns",
            "contrast_repair_cpu_ns","balanced_repair_cpu_ns",
            "random_repair_cpu_ns",
            "nested_negative_correct","nested_negative_wrong"
        )
        total={k:0 for k in names}
        receipts=[]
        family={}
        for seed in SEEDS:
            with self.subTest(seed=seed):
                negative=seed>=4913
                physics=build_world(seed)
                copies={name:build_world(seed).training_session()
                        for name in ("contrast","balanced","random")}
                rng_A=Random(int.from_bytes(sha256(
                    f"WSP76|common-paid-A-prefix|{seed}".encode("ascii")
                ).digest(),"big"))
                residual=ReusableInteractionNeural("residual",seed=seed)
                alternative=ReusableInteractionNeural("random",seed=seed)
                charged={name:[] for name in copies}
                for step in range(96):
                    action=rng_A.choice(ACTIONS)
                    observations={name:world.step(action) for name,world in copies.items()}
                    canonical=observations["contrast"]
                    for name in copies:
                        row=observations[name]
                        record=(row.before,row.action,row.after)
                        charged[name].append(record)
                        self.assertEqual(record,
                                         (canonical.before,canonical.action,canonical.after))
                    residual.charge(canonical)
                    alternative.charge(canonical)
                    if step+1 in (48,96):
                        residual.grow()
                        alternative.grow()
                self.assertEqual(residual.charged_actions,96)
                self.assertEqual(alternative.charged_actions,96)
                stageA=residual.snapshot()
                alt_snapshot=alternative.snapshot()
                cold_teacher=FeatureGrowthNeural.restore(stageA)
                cold_alternative=FeatureGrowthNeural.restore(alt_snapshot)
                self.assertEqual(stageA,cold_teacher.snapshot())
                self.assertEqual(alt_snapshot,cold_alternative.snapshot())
                B_policy_ns={name:0 for name in copies}
                policy_random=uniform_random(seed)
                cyc=balanced_cycle(seed)
                for Bstep in range(48):
                    start=time.process_time_ns()
                    action_n=choose_observed_contrast(
                        copies["contrast"].state,charged["contrast"],seed,Bstep)
                    B_policy_ns["contrast"]+=time.process_time_ns()-start
                    start=time.process_time_ns()
                    action_d=cyc[Bstep]
                    B_policy_ns["balanced"]+=time.process_time_ns()-start
                    start=time.process_time_ns()
                    action_r=policy_random.choice(ACTIONS)
                    B_policy_ns["random"]+=time.process_time_ns()-start
                    chosen={"contrast":action_n,"balanced":action_d,"random":action_r}
                    for name,source in copies.items():
                        row=source.step(chosen[name])
                        charged[name].append((row.before,row.action,row.after))
                for name,source in copies.items():
                    self.assertEqual(len(source.ledger),144)
                    self.assertEqual(len(charged[name]),144)
                    self.assertEqual(charged[name][0][0],(0,0,0,0))
                    self.assertTrue(all(charged[name][i][2]==charged[name][i+1][0]
                                        for i in range(143)))
                self.assertEqual(charged["contrast"][:96],
                                 charged["balanced"][:96])
                self.assertEqual(charged["contrast"][:96],
                                 charged["random"][:96])
                models={}
                edits={}
                trainCPU={}
                for name in copies:
                    start=time.process_time_ns()
                    model,receipt=repair(
                        stageA,charged[name][:96],charged[name][96:],
                        "counterexample",seed)
                    trainCPU[name]=time.process_time_ns()-start
                    models[name]=model
                    edits[name]=receipt
                start=time.process_time_ns()
                refit=fitted_readout(stageA,charged["contrast"][:96],
                                     charged["contrast"][96:])
                refit_ns=time.process_time_ns()-start
                random_edits,random_edit_receipt=repair(
                    stageA,charged["contrast"][:96],charged["contrast"][96:],
                    "random",seed)
                self.assertEqual(random_edit_receipt["direct_gradient_steps"],0)
                self.assertEqual(edits["contrast"]["direct_gradient_steps"],0)
                self.assertEqual(models["contrast"].growth_rounds,2)
                self.assertEqual(len(models["contrast"].hidden_weights),
                                 len(cold_teacher.hidden_weights))
                self.assertLessEqual(edits["contrast"]["changed_hidden_coefficients"],4)
                # An untrained source cannot be read from numerical snapshots.
                for model in list(models.values())+[refit,random_edits]:
                    snap=model.snapshot()
                    self.assertNotIn('"ledger"',snap)
                    self.assertNotIn('"source"',snap)
                    clone=FeatureGrowthNeural.restore(snap)
                    self.assertEqual(clone.snapshot(),snap)
                    with self.assertRaises(ValueError):
                        FeatureGrowthNeural.restore(snap.replace(
                            "wsp69.neural-feature-growth.v1",
                            "wsp69.neural-feature-growth.v2"))
                    for s in STATES:
                        for a in ACTIONS:
                            self.assertEqual(clone.predict(s,a),model.predict(s,a))
                paid={name:{(s,a) for s,a,y in rows}
                      for name,rows in charged.items()}
                tasks=physics.composition_tests()
                scores={}
                eval_ns={}
                for name in copies:
                    start=time.process_time_ns()
                    scores[name]=evaluate(models[name].predict,physics,paid[name],tasks)
                    eval_ns[name]=time.process_time_ns()-start
                refit_eval=evaluate(refit.predict,physics,paid["contrast"])
                random_edit_eval=evaluate(random_edits.predict,physics,paid["contrast"])
                exact=ExactMemory(charged["contrast"])
                exact_eval=evaluate(exact.predict,physics,paid["contrast"])
                tree=IndependentTreeControl(charged["contrast"],4)
                tree_eval=evaluate(tree.predict,physics,paid["contrast"])
                old=retention(models["contrast"].predict,cold_teacher,physics)
                mlp_fit=None
                mlp_confident=None
                mlp_forced=None
                mlp_ns=0
                if not negative:
                    mlp=EndToEndAdamControl(seed)
                    start=time.process_time_ns()
                    mlp_fit=mlp.fit(charged["contrast"])
                    mlp_ns=time.process_time_ns()-start
                    mlp_confident=evaluate(
                        lambda s,a:mlp.predict(s,a,confidence=True),
                        physics,paid["contrast"])
                    mlp_forced=evaluate(mlp.predict,physics,paid["contrast"])
                physical_contrast={}
                for name,rows in charged.items():
                    prior_states={rows[0][0]}
                    prior_pairs=set()
                    added_states=added_pairs=0
                    for i,(before,action,after) in enumerate(rows):
                        if i>=96:
                            added_pairs+=int((before,action) not in prior_pairs)
                            added_states+=int(after not in prior_states)
                        prior_pairs.add((before,action))
                        prior_states.add(before)
                        prior_states.add(after)
                    physical_contrast[name]={
                        "unique_paid_contexts":len(prior_pairs),
                        "unique_visited_states":len(prior_states),
                        "B_new_context_events":added_pairs,
                        "B_new_state_events":added_states,
                        "B_action_counts":[
                            sum(int(r[1]==a) for r in rows[96:])
                            for a in ACTIONS],
                        "paid_paired_contrasts_A":len(
                            paid_action_contrasts(rows[:96])),
                        "paid_paired_contrasts_after_B":len(
                            paid_action_contrasts(rows)),
                        "incremental_actual_action_contrasts":len(
                            set(paid_action_contrasts(rows))-
                            set(paid_action_contrasts(rows[:96])))
                    }
                # Evaluator-only exhaustive reachability, AFTER model and
                # intervention policy training; never available to learners.
                reachable={(0,0,0,0)}
                frontier=[(0,0,0,0)]
                while frontier:
                    state=frontier.pop()
                    for action in ACTIONS:
                        next_state=physics._step_oracle(state,action)
                        if next_state not in reachable:
                            reachable.add(next_state)
                            frontier.append(next_state)
                total["reachable_worlds_ge12"]+=int(len(reachable)>=12)
                receipt={
                    "evaluator_only_reachable_public_states":len(reachable),
                    "seed":seed,"family":physics.family,"source":physics.receipt(),
                    "paid_physical_A_sha256":{
                        name:digest(charged[name][:96]) for name in copies},
                    "paid_physical_B_sha256":{
                        name:digest(charged[name][96:]) for name in copies},
                    "paid_physical_A_actions_per_policy":96,
                    "paid_physical_B_actions_per_policy":48,
                    "real_physics_charges_across_three_copies":432,
                    "frozen_A_primary_weights_sha256":sha256(
                        stageA.encode("ascii")).hexdigest(),
                    "frozen_A_secondary_weights_sha256":sha256(
                        alt_snapshot.encode("ascii")).hexdigest(),
                    "numeric_final_neural_snapshot_sha256":{
                        name:sha256(models[name].snapshot().encode("ascii")).hexdigest()
                        for name in copies},
                    "contrast_readout_only_numeric_snapshot_sha256":sha256(
                        refit.snapshot().encode("ascii")).hexdigest(),
                    "contrast_random_edits_snapshot_sha256":sha256(
                        random_edits.snapshot().encode("ascii")).hexdigest(),
                    "selected_hidden_weight_edits":edits,
                    "random_hidden_edit_receipt":random_edit_receipt,
                    "physical_reachability":physical_contrast,
                    "policy_inference_CPU_ns":B_policy_ns,
                    "direct_repair_CPU_ns":trainCPU,
                    "full_eval_CPU_ns":eval_ns,
                    "refit_only_CPU_ns":refit_ns,
                    "contrast_arm":scores["contrast"],
                    "balanced_arm":scores["balanced"],
                    "random_arm":scores["random"],
                    "contrast_same_ledger_readout":refit_eval,
                    "contrast_same_ledger_random_hidden":random_edit_eval,
                    "contrast_same_ledger_exact_memory":exact_eval,
                    "contrast_same_ledger_decision_tree":tree_eval,
                    "frozen_A_knowledge_retention":old,
                    "fully_trained_standard_neural_control":mlp_fit,
                    "MLP_confident_heldout":mlp_confident,
                    "MLP_forced_heldout":mlp_forced,
                    "MLP_training_CPU_ns":mlp_ns
                }
                receipts.append(receipt)
                total["worlds"]+=1
                total["total_real_paid_actions"]+=432
                total["cold_snapshot_tamper_worlds"]+=1
                if negative:
                    total["negative_worlds"]+=1
                    total["nested_negative_correct"]+=scores["contrast"]["physical"]["correct"]
                    total["nested_negative_wrong"]+=scores["contrast"]["physical"]["wrong_confident"]
                else:
                    total["primary_worlds"]+=1
                    total["primary_physical_cases"]+=64
                    total["primary_composition_cases"]+=32
                    for name,label in (
                        ("contrast","contrast"),
                        ("balanced","balanced"),
                        ("random","random")
                    ):
                        total[f"{label}_correct"]+=scores[name]["physical"]["correct"]
                        total[f"{label}_wrong"]+=scores[name]["physical"]["wrong_confident"]
                    for key,result in (
                        ("readout",refit_eval),
                        ("random_hidden",random_edit_eval),
                        ("exact_memory",exact_eval),
                        ("decision_tree",tree_eval),
                        ("MLP_confident",mlp_confident),
                        ("MLP_forced",mlp_forced)
                    ):
                        total[f"{key}_correct"]+=result["physical"]["correct"]
                        total[f"{key}_wrong"]+=result["physical"]["wrong_confident"]
                    total["contrast_abstain"]+=scores["contrast"]["physical"]["abstain"]
                    total["contrast_unseen_correct"]+=scores["contrast"]["never_paid"]["correct"]
                    total["contrast_unseen_wrong"]+=scores["contrast"]["never_paid"]["wrong_confident"]
                    total["contrast_unseen_total"]+=scores["contrast"]["never_paid"]["total"]
                    total["contrast_two_action_correct"]+=scores["contrast"]["two_action"]["correct"]
                    total["contrast_two_action_wrong"]+=scores["contrast"]["two_action"]["wrong_confident"]
                    total["balanced_unseen_correct"]+=scores["balanced"]["never_paid"]["correct"]
                    total["random_unseen_correct"]+=scores["random"]["never_paid"]["correct"]
                    total["old_stageA_eligible"]+=old["stageA_true_confident"]
                    total["old_stageA_retained"]+=old["retained"]
                    for name in copies:
                        for suffix,key in (
                            ("unique_paid_contexts","unique_paid_contexts"),
                            ("unique_visited_states","unique_visited_states"),
                            ("new_B_contexts","B_new_context_events"),
                            ("actually_new_B_states","B_new_state_events")
                        ):
                            total[f"{name}_{suffix}"]+=physical_contrast[name][key]
                        total[f"{name}_policy_cpu_ns"]+=B_policy_ns[name]
                        total[f"{name}_incremental_action_contrasts"]+=(
                            physical_contrast[name][
                                "incremental_actual_action_contrasts"])
                        if name=="contrast":
                            total["contrast_repair_cpu_ns"]+=trainCPU[name]
                        if name=="balanced":
                            total["balanced_repair_cpu_ns"]+=trainCPU[name]
                        if name=="random":
                            total["random_repair_cpu_ns"]+=trainCPU[name]
                    total["contrast_cpu_ns"]+=(
                        B_policy_ns["contrast"]+trainCPU["contrast"]+eval_ns["contrast"])
                    total["random_cpu_ns"]+=(
                        B_policy_ns["random"]+trainCPU["random"]+eval_ns["random"])
                    total["primary_worlds_with_actual_hidden_edits"]+=int(
                        edits["contrast"]["changed_hidden_coefficients"]>0)
                    total["MLP_converged"]+=int(mlp_fit["fully_trained"])
                    total["MLP_gradient_updates"]+=mlp_fit["gradient_updates_total"]
                    total["MLP_training_cpu_ns"]+=mlp_ns
                    bucket=family.setdefault(physics.family,{
                        "worlds":0,"contrast_correct":0,"random_correct":0,
                        "balanced_correct":0,"contrast_unseen":0,
                        "contrast_wrong":0,"contrast_contexts":0,
                        "random_contexts":0,"balanced_contexts":0})
                    bucket["worlds"]+=1
                    bucket["contrast_correct"]+=scores["contrast"]["physical"]["correct"]
                    bucket["random_correct"]+=scores["random"]["physical"]["correct"]
                    bucket["balanced_correct"]+=scores["balanced"]["physical"]["correct"]
                    bucket["contrast_unseen"]+=scores["contrast"]["never_paid"]["correct"]
                    bucket["contrast_wrong"]+=scores["contrast"]["physical"]["wrong_confident"]
                    bucket["contrast_contexts"]+=len(paid["contrast"])
                    bucket["random_contexts"]+=len(paid["random"])
                    bucket["balanced_contexts"]+=len(paid["balanced"])
        self.assertEqual(total["worlds"],16)
        self.assertEqual(total["primary_worlds"],12)
        self.assertEqual(total["negative_worlds"],4)
        self.assertEqual(total["total_real_paid_actions"],6912)
        self.assertEqual(total["primary_physical_cases"],768)
        self.assertEqual(total["primary_composition_cases"],384)
        self.assertEqual(total["cold_snapshot_tamper_worlds"],16)
        retention_fraction=(total["old_stageA_retained"]/
                            max(1,total["old_stageA_eligible"]))
        candidate_cpu_ratio=total["contrast_cpu_ns"]/max(1,total["random_cpu_ns"])
        criteria={
            "reachable_states_ge_12_all_16":
                total["reachable_worlds_ge12"]==16,
            "observed_contrast_correct_ge_360":
                total["contrast_correct"]>=360,
            "observed_gain_over_equal_paid_random_ge_18":
                total["contrast_correct"]-total["random_correct"]>=18,
            "observed_gain_over_equal_paid_balanced_ge_18":
                total["contrast_correct"]-total["balanced_correct"]>=18,
            "observed_gain_over_same_ledger_readout_ge_15":
                total["contrast_correct"]-total["readout_correct"]>=15,
            "observed_gain_over_same_ledger_random_edits_ge_15":
                total["contrast_correct"]-total["random_hidden_correct"]>=15,
            "incremental_actual_action_contrasts_vs_random_ge_15":
                total["contrast_incremental_action_contrasts"]-
                total["random_incremental_action_contrasts"]>=15,
            "incremental_actual_action_contrasts_vs_balanced_ge_15":
                total["contrast_incremental_action_contrasts"]-
                total["balanced_incremental_action_contrasts"]>=15,
            "truly_never_paid_correct_ge_24":
                total["contrast_unseen_correct"]>=24,
            "truly_never_paid_gain_over_random_ge_8":
                total["contrast_unseen_correct"]-total["random_unseen_correct"]>=8,
            "primary_confident_wrong_le_24":
                total["contrast_wrong"]<=24,
            "retention_ge_80pct":retention_fraction>=0.8,
            "two_action_correct_ge_115":
                total["contrast_two_action_correct"]>=115,
            "adversarial_confident_wrong_le_16":
                total["nested_negative_wrong"]<=16,
            "hidden_coefficients_changed_in_10_worlds":
                total["primary_worlds_with_actual_hidden_edits"]>=10,
            "all_16_numeric_cold_restore_tamper":
                total["cold_snapshot_tamper_worlds"]==16,
            "policy_and_repair_CPU_ratio_to_random_le_6":
                candidate_cpu_ratio<=6.0
        }
        verdict=("SELFTEST_SIGNAL" if all(criteria.values()) else
                 "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP76_SELFTEST_DIAGNOSTIC "+json.dumps({
            "classification":verdict,"criteria":criteria,
            "stageA_confident_true_retention":round(retention_fraction,8),
            "measured_candidate_over_random_policy_plus_repair_cpu":
                round(candidate_cpu_ratio,6),
            "qualified_independent_fully_trained_neural_worlds":
                total["MLP_converged"],
            "totals":total,"by_family":family,"worlds":receipts
        },sort_keys=True,separators=(",",":")))
        # Synthetic research misses preserve NEGATIVE receipts without
        # failing engineering unit tests or adjusting the frozen rubric.


if __name__=="__main__":
    unittest.main()

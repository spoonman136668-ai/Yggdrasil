"""CKAD25-X: frozen active discrimination after unlabeled causal world switches.

Primary intervention outcomes are revealed ONLY after the read-only selector
commits to a public context/action. The same source-conditioned native learner
provides persisted A/B causal memories through unrelated P/Q pressure.
This is a bounded synthetic developer test of causal probe selection, with
fully matched conventional exact Bayesian, fitted ML, fixed and random arms.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import importlib.util
import itertools
import json
import math
import random
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

HERE = Path(__file__).resolve().parent
HELP = HERE.parent / "CKAD25-S" / "run.py"
ORIGINAL = "c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f"
SEEDS = (65021, 65027, 65033, 65039)
PHASES = ("A", "B", "A", "C", "D")
POLICIES = ("native_active", "fixed", "random", "conventional_eig")
READOUTS = ("native_recall", "exact_continuous", "exact_hard", "logistic", "forest",
            "no_memory", "fixed_A", "recent_B", "privileged_oracle")


def require(ok, message):
    if not ok:
        raise ValueError("CKAD25X_" + message)


def conventional_helpers():
    spec=importlib.util.spec_from_file_location("ckad25s_unchanged_independent_control",HELP)
    require(spec is not None and spec.loader is not None,"MISSING_CONTROL_HELPER")
    h=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    require(h.ORIGINAL_CHECKPOINT==ORIGINAL and h.SEEDS==(1103,2207,3301),
            "CONTROL_SOURCE_DRIFT")
    return h


def source_roster(seed):
    masks=list(range(16))
    key=digest(canonical(["CKAD25-X-HIDDEN-SOURCE-ROSTER",seed]))
    random.Random(int(key[:16],16)).shuffle(masks)
    train,held=masks[:12],masks[12:]
    require(len(train)==12 and len(held)==4 and len(set(train+held))==16,
            "HELD_SOURCE_LEAK")
    return train,held


def coefficients(seed,source_pool):
    """Procedural rules are generator-only, never exposed to any selector."""
    rng=random.Random(int(digest(canonical(["CKAD25-X-HIDDEN-RULES",seed]))[:16],16))
    selected={}
    used=set()
    for name,count in (("A",3),("B",3),("C",4),("D",5),("P",2),("Q",2)):
        for _ in range(1000):
            terms=tuple(sorted(rng.sample(range(16),count)))
            # Both familiar worlds must be responsive to actual do-action.
            if name in ("A","B") and not any(t&8 for t in terms):
                continue
            bitmap=sum(1<<i for i in terms)
            if bitmap in used:
                continue
            if name=="B" and sum(
                evaluate(bitmap,x)!=evaluate(selected["A"],x) for x in source_pool)<4:
                continue
            selected[name]=bitmap
            used.add(bitmap)
            break
        else:
            raise ValueError("CKAD25X_GENERATOR_BUDGET")
    # Degree-4/5 ANF functions cannot be represented by a unique <=3-term ANF
    # grammar, even though finite observations may temporarily mimic one.
    require(all(selected[a].bit_count()==n for a,n in
                (("A",3),("B",3),("C",4),("D",5),("P",2),("Q",2))),
            "GENERATED_STRUCTURAL_CLASS")
    return selected


def evaluate(coefficients,mask):
    row=sum(1<<i for i in range(16) if (mask&i)==i)
    return (coefficients&row).bit_count()&1


def observed(weight,masks):
    return [[x&7,x>>3,evaluate(weight,x)] for x in masks]


def train(cold,slot,weight,masks,seed):
    rows=observed(weight,masks)
    ref=digest(canonical(["CKAD25-X-PUBLIC",seed,slot]))
    for packet in (rows[:8],rows[8:]):
        if packet:
            cold=cold.observe(slot,packet,digest(canonical(packet)),source_ref=ref)
    return cold


def exact_models(h,source_rows):
    feats=[(h.terms(c,a),y) for c,a,y in source_rows]
    models=[]
    for size in range(4):
        for active in itertools.combinations(range(16),size):
            if all((sum(f[j] for j in active)&1)==y for f,y in feats):
                models.append(active)
    return tuple(models)


def posterior_fraction(h,models,mask):
    if not models:
        return Fraction(1,2)
    feats=h.terms(mask&7,mask>>3)
    ones=sum((sum(feats[i] for i in active)&1) for active in models)
    return Fraction(ones,len(models))


def regime_posterior(h,models,diagnostics):
    counts={}
    for slot in (1,2):
        likelihood=Fraction(1,1)
        for c,a,y in diagnostics:
            p=posterior_fraction(h,models[slot],c|(a<<3))
            likelihood*=p if y else 1-p
        counts[slot]=likelihood
    counts["unknown"]=Fraction(1,2)**len(diagnostics)
    normalizer=sum(counts.values(),Fraction(0,1))
    require(normalizer>0,"ZERO_CONVENTIONAL_POSTERIOR")
    return {key:weight/normalizer for key,weight in counts.items()}


def independent_gini_choice(h,models,diagnostics,available):
    """Not the native implementation; re-fit independent exact source models."""
    w=regime_posterior(h,models,diagnostics)
    best=None
    for mask in sorted(available):
        p={slot:posterior_fraction(h,models[slot],mask) for slot in (1,2)}
        mean=w[1]*p[1]+w[2]*p[2]+w["unknown"]*Fraction(1,2)
        gain=(w[1]*(p[1]-mean)**2+w[2]*(p[2]-mean)**2
              +w["unknown"]*(Fraction(1,2)-mean)**2)
        if best is None or gain>best[0]:
            best=(gain,mask)
    return best[1]


def entropy(value):
    value=float(value)
    if value<=0 or value>=1:return 0.
    return -value*math.log2(value)-(1-value)*math.log2(1-value)


def conventional_eig_choice(h,models,diagnostics,available):
    """Independent full-source class Bayesian expected Shannon information gain."""
    w=regime_posterior(h,models,diagnostics)
    best_mask=None
    best_gain=-1.
    for mask in sorted(available):
        pp={slot:posterior_fraction(h,models[slot],mask) for slot in (1,2)}
        mean=w[1]*pp[1]+w[2]*pp[2]+w["unknown"]*Fraction(1,2)
        gain=(entropy(mean)-float(w[1])*entropy(pp[1])
              -float(w[2])*entropy(pp[2])-float(w["unknown"])*1.)
        if gain>best_gain+1e-13:
            best_gain=gain
            best_mask=mask
    require(best_mask in available,"EIG_ACTION_OUTSIDE_POOL")
    return best_mask


def exact_readouts(h,models,diagnostics,mask):
    w=regime_posterior(h,models,diagnostics)
    slot=max((1,2),key=lambda k:(w[k],-k))
    chosen=slot if w[slot]>=Fraction(9,10) else None
    probs={j:posterior_fraction(h,models[j],mask) for j in (1,2)}
    hard=probs[chosen] if chosen is not None else Fraction(1,2)
    continuous=(w[1]*probs[1]+w[2]*probs[2]+w["unknown"]*Fraction(1,2))
    return hard,chosen,continuous


def fitted_models(h,rows,seed):
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    ys=[y for _,_,y in rows]
    out={}
    for name in ("logistic","forest"):
        xs=[h.terms(c,a) if name=="logistic" else h.vector(c,a) for c,a,_ in rows]
        if len(set(ys))<2:
            prior=float(ys[0])
            out[name]=lambda mask,prior=prior:prior
            continue
        if name=="logistic":
            model=LogisticRegression(C=1,max_iter=1000,solver="lbfgs",
                                     random_state=seed).fit(xs,ys)
        else:
            model=RandomForestClassifier(n_estimators=64,max_depth=4,n_jobs=1,
                                         random_state=seed).fit(xs,ys)
        cls=list(model.classes_).index(1)
        def predict(mask,model=model,name=name,cls=cls):
            c,a=mask&7,mask>>3
            x=h.terms(c,a) if name=="logistic" else h.vector(c,a)
            return float(model.predict_proba([x])[0][cls])
        out[name]=predict
    return out


def fitted_gate(fitted,diagnostics,mask):
    score={}
    for slot in (1,2):
        likelihood=1.
        for c,a,y in diagnostics:
            p=fitted[slot](c|(a<<3))
            likelihood*=p if y else 1-p
        score[slot]=likelihood
    denominator=score[1]+score[2]+.5**len(diagnostics)
    chosen=max((1,2),key=lambda i:(score[i],-i))
    return fitted[chosen](mask) if score[chosen]/denominator>=.90 else .5


def choose_probe(policy,seed,phase,cold,h,models,diagnostics,available,rng):
    if policy=="native_active":
        given=[[x&7,x>>3] for x in sorted(available)]
        action=cold.propose_causal_discriminator((1,2),diagnostics,given)
        mask=action[0]|(action[1]<<3)
        require(mask==independent_gini_choice(h,models,diagnostics,available),
                "NATIVE_INDEPENDENT_CONVENTIONAL_GINI_PARITY")
    elif policy=="conventional_eig":
        mask=conventional_eig_choice(h,models,diagnostics,available)
    elif policy=="fixed":
        mask=min(available)
    elif policy=="random":
        mask=rng.choice(sorted(available))
    else:
        raise ValueError("CKAD25X_POLICY_UNKNOWN")
    require(mask in available and mask not in {c|(a<<3) for c,a,_ in diagnostics},
            "HIDDEN_ACTION_OR_DUPLICATION")
    return mask


def brier(values,truth):
    require(len(values)==len(truth)==4,"Brier_COUNT")
    return sum((float(p)-y)**2 for p,y in zip(values,truth))/4


def run_score(seed_roster=SEEDS):
    h=conventional_helpers()
    original=h.snapshot()
    before=original.checkpoint()
    require(digest(before)==ORIGINAL,"SOURCE_CHECKPOINT_DRIFT")
    old_predictions=[original.predict(0,c,a) for a in (0,1) for c in range(8)]
    cases=[]
    seed_custody={}
    for seed in seed_roster:
        pool,held=source_roster(seed)
        worlds=coefficients(seed,pool)
        native=NativeCumulativeLearner.restore(before,ORIGINAL)
        fitted={}
        independent={}
        source_training={}
        for slot,kind in ((1,"A"),(2,"B")):
            native=train(native,slot,worlds[kind],pool,seed)
            native=native.compile_causal_relations(slot)
            rows=observed(worlds[kind],pool)
            source_training[slot]=rows
            independent[slot]=exact_models(h,rows)
            fitted[slot]=fitted_models(h,rows,seed)
            require(native._compiled[slot].model_count==len(independent[slot]),
                    "NATIVE_BAYES_SOURCE_MODEL_COUNT")
        remembered=[native._compiled[i].checkpoint() for i in (1,2)]
        for slot,kind in ((3,"P"),(4,"Q")):
            native=train(native,slot,worlds[kind],pool[:8],seed)
        raw=native.checkpoint()
        native=NativeCumulativeLearner.restore(raw,digest(raw))
        retained=(raw==native.checkpoint()
                  and original.checkpoint()==before
                  and native._properties.checkpoint()==original._properties.checkpoint()
                  and native._source._seen[0]==original._source._seen[0]
                  and native._hypotheses[0].checkpoint()==original._hypotheses[0].checkpoint()
                  and native._events[:len(original._events)]==original._events
                  and [native.predict(0,c,a) for a in (0,1) for c in range(8)]==old_predictions
                  and [native._compiled[i].checkpoint() for i in (1,2)]==remembered
                  and [native.info()["observed_inputs"][i] for i in (1,2,3,4)]==[12,12,8,8]
                  and not any(native.info()["quarantined"][:5]))
        require(retained,"NATIVE_PERSISTENCE_OR_INTERFERENCE")
        seed_custody[str(seed)]={
            "native_cold_sha256":digest(raw),
            "A_compiled_sha256":digest(remembered[0]),
            "B_compiled_sha256":digest(remembered[1]),
            "source_train_sha256":digest(canonical(pool)),
            "held_mask_sha256":digest(canonical(held)),
            "native_old_and_compiled_retained":retained,
            "A_native_compiled_count":native._compiled[1].model_count,
            "B_native_compiled_count":native._compiled[2].model_count,
            "source_family_coefficients_evaluator_only":[worlds[x] for x in ("A","B","C","D")]
        }
        for phase,kind in enumerate(PHASES):
            expected_held=observed(worlds[kind],held)
            for policy in POLICIES:
                diag=[]
                available=set(pool)
                deterministic_key=digest(canonical(["CKAD25-X-RANDOM-ARM",seed,phase,policy]))
                rng=random.Random(int(deterministic_key[:16],16))
                chosen_masks=[]
                for _ in range(4):
                    choice=choose_probe(policy,seed,phase,native,h,independent,
                                        diag,available,rng)
                    chosen_masks.append(choice)
                    # THE ONLY target outcome revelation: AFTER committing action
                    diag.append([choice&7,choice>>3,evaluate(worlds[kind],choice)])
                    available.remove(choice)
                require(len(diag)==4 and len(set(chosen_masks))==4
                        and not set(chosen_masks)&set(held),
                        "SOURCE_PROBE_ACCOUNTING")
                output={k:[] for k in READOUTS}
                selected=[]
                exact_selected=[]
                for mask in held:
                    c,a=mask&7,mask>>3
                    ones,total,slot=native.recall_causal_regime([1,2],diag,c,a)
                    hard,known,continuous=exact_readouts(h,independent,diag,mask)
                    require(Fraction(ones,total)==hard and slot==known,
                            "INDEPENDENT_FULL_BAYES_SOURCE_EQUIVALENCE")
                    selected.append(slot)
                    exact_selected.append(known)
                    output["native_recall"].append(Fraction(ones,total))
                    output["exact_hard"].append(hard)
                    output["exact_continuous"].append(continuous)
                    for name in ("logistic","forest"):
                        preds={i:fitted[i][name] for i in (1,2)}
                        output[name].append(fitted_gate(preds,diag,mask))
                    output["no_memory"].append(.5)
                    for name,slot_const in (("fixed_A",1),("recent_B",2)):
                        p=native.causal_relation_probability(slot_const,c,a)
                        output[name].append(Fraction(p[0],p[1]))
                    if kind in ("A","B"):
                        truth_slot=1 if kind=="A" else 2
                        p=native.causal_relation_probability(truth_slot,c,a)
                        output["privileged_oracle"].append(Fraction(p[0],p[1]))
                    else:
                        output["privileged_oracle"].append(.5)
                require(len(set(selected))==1,"HELD_ADDRESS_DEPENDENT_SELECTION")
                y=[row[2] for row in expected_held]
                metrics={}
                for name,probs in output.items():
                    values=[float(p) for p in probs]
                    metrics[name]={
                        "brier":round(brier(probs,y),9),
                        "answered":sum(v in (0.,1.) for v in values),
                        "correct_answered":sum(v in (0.,1.) and int(v)==a
                                               for v,a in zip(values,y)),
                        "incorrect_answered":sum(v in (0.,1.) and int(v)!=a
                                                 for v,a in zip(values,y)),
                        "held_predictions":[
                            [p.numerator,p.denominator] if isinstance(p,Fraction)
                            else [round(p,12),1.] for p in probs]
                    }
                cases.append({
                    "seed":seed,"phase":phase,"policy":policy,
                    "evaluator_only_hidden_world":kind,
                    "selected_native_slot":selected[0],
                    "target_source_probe_masks":chosen_masks,
                    "target_revealed_probes_sha256":digest(canonical(diag)),
                    "source_fit_A_sha256":digest(canonical(source_training[1])),
                    "source_fit_B_sha256":digest(canonical(source_training[2])),
                    "common_held_mask_sha256":digest(canonical(held)),
                    "held_truth_sha256":digest(canonical(y)),
                    "A_return_is_duplicate_held_not_new_sample":phase==2,
                    "native_source_retention":retained,
                    "metrics":metrics
                })
    require(len(cases)==len(seed_roster)*len(PHASES)*len(POLICIES),
            "COHORT_SIZE")
    means={policy:{
        method:round(sum(x["metrics"][method]["brier"] for x in cases
                         if x["policy"]==policy)/(len(seed_roster)*len(PHASES)),9)
        for method in READOUTS} for policy in POLICIES}
    candidate=[x for x in cases if x["policy"]=="native_active"]
    familiar=[x for x in candidate if x["evaluator_only_hidden_world"] in ("A","B")]
    novel=[x for x in candidate if x["evaluator_only_hidden_world"] in ("C","D")]
    returners=[x for x in candidate if x["phase"]==2]
    return_correct=sum(x["selected_native_slot"]==1 for x in returners)
    phase_known_correct=sum(x["selected_native_slot"]==
                            (1 if x["evaluator_only_hidden_world"]=="A" else 2)
                            for x in familiar)
    fam_answered=sum(x["metrics"]["native_recall"]["answered"] for x in familiar)
    fam_wrong=sum(x["metrics"]["native_recall"]["incorrect_answered"] for x in familiar)
    novel_brier=round(sum(x["metrics"]["native_recall"]["brier"] for x in novel)/len(novel),9)
    novel_wrong=sum(x["metrics"]["native_recall"]["incorrect_answered"] for x in novel)
    best_fitted=min(means["native_active"][z] for z in ("logistic","forest"))
    gates={
        "original_memory_and_compiled_committees_retained":
            all(x["native_old_and_compiled_retained"] for x in seed_custody.values()),
        "equal_source_action_budgets_and_disjoint_held":
            all(len(x["target_source_probe_masks"])==4
                and len(set(x["target_source_probe_masks"]))==4 for x in cases),
        "native_beats_fixed_by_0_04":
            means["native_active"]["native_recall"]<=
            means["fixed"]["native_recall"]-.04+1e-12,
        "native_beats_random_by_0_04":
            means["native_active"]["native_recall"]<=
            means["random"]["native_recall"]-.04+1e-12,
        "returned_A_recognized_at_least_3_of_4":return_correct>=3,
        "familiar_phase_accuracy_at_least_9_of_12":phase_known_correct>=9,
        "familiar_confident_coverage_at_least_20_of_48":fam_answered>=20,
        "familiar_confident_wrong_at_most_3":fam_wrong<=3,
        "novel_Brier_at_most_0_27":novel_brier<=.27+1e-12,
        "novel_confident_wrong_at_most_1":novel_wrong<=1,
        "candidate_within_0_03_of_conventional_Bayes_EIG":
            means["native_active"]["native_recall"]<=
            means["conventional_eig"]["native_recall"]+.03+1e-12,
        "candidate_within_0_03_of_best_fitted_baseline":
            means["native_active"]["native_recall"]<=best_fitted+.03+1e-12,
        "candidate_within_0_04_of_exact_continuous_source_Bayes":
            means["native_active"]["native_recall"]<=
            means["native_active"]["exact_continuous"]+.04+1e-12,
        "native_exact_conventional_source_readout_parity":
            all(x["metrics"]["native_recall"]["held_predictions"]==
                x["metrics"]["exact_hard"]["held_predictions"] for x in cases),
    }
    per_seed={}
    for seed in seed_roster:
        per_seed[str(seed)]={
            "candidate_brier":round(sum(x["metrics"]["native_recall"]["brier"]
                                          for x in candidate if x["seed"]==seed)/5,9),
            "fixed_brier":round(sum(x["metrics"]["native_recall"]["brier"]
                                      for x in cases if x["seed"]==seed and x["policy"]=="fixed")/5,9),
            "random_brier":round(sum(x["metrics"]["native_recall"]["brier"]
                                       for x in cases if x["seed"]==seed and x["policy"]=="random")/5,9),
            "conventional_EIG_brier":round(sum(x["metrics"]["native_recall"]["brier"]
                                       for x in cases if x["seed"]==seed and x["policy"]=="conventional_eig")/5,9),
            "A_return_slot":next(x["selected_native_slot"] for x in candidate
                                 if x["seed"]==seed and x["phase"]==2)
        }
    return {
        "schema":"yggdrasil.ckad25x.active-native-causal-discrimination.v1",
        "source_sha256":digest(Path(__file__).read_bytes()),
        "control_helper_sha256":digest(HELP.read_bytes()),
        "original_native_source_sha256":ORIGINAL,
        "science_seeds":list(seed_roster),
        "first_use_scored":tuple(seed_roster)==SEEDS,
        "native_source_free_training_observations":len(seed_roster)*40,
        "phase_policy_revealed_target_observations":len(cases)*4,
        "held_phase_cases_per_policy":len(seed_roster)*5*4,
        "distinct_held_world_outcomes_per_policy":len(seed_roster)*4*4,
        "A_repeat_is_not_fresh_held_evidence":True,
        "original_protected_world_calls":0,
        "native_owner_first_use":False,
        "accepted_main_mutated":False,"one_native_learner_per_seed":True,
        "source_retention_by_seed":seed_custody,
        "per_seed":per_seed,
        "per_phase_policy":cases,
        "held_brier_by_policy_method":means,
        "candidate_known_confident_answered":fam_answered,
        "candidate_known_confident_wrong":fam_wrong,
        "candidate_familiar_regimes_correct":phase_known_correct,
        "candidate_return_A_seeds_correct":return_correct,
        "candidate_novel_brier":novel_brier,"candidate_novel_confident_wrong":novel_wrong,
        "frozen_gates":gates,
        "development_disposition":"DEVELOPMENT_SIGNAL" if all(gates.values()) else "DEVELOPMENT_NO_GO",
        "scientific_pass":False,"conventional_superiority":False,
        "forge_dispatch":False,"accepted_native":False,"native_promotion":False,
        "deployment":False
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--preflight",action="store_true")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    if args.preflight:
        require(args.output is None,"PREFLIGHT_NO_PRIMARY_RESULT")
        result=run_score((99981,))
        require(result["first_use_scored"] is False,"PREFLIGHT_LABEL")
        require(len(result["per_phase_policy"])==20,"PREFLIGHT_BUDGET")
        print("CKAD25X_DISJOINT_DEV_WIRING_PREFLIGHT_PASS")
        return
    require(args.output is not None,"PRIMARY_OUTPUT_REQUIRED")
    t=time.monotonic()
    result=run_score()
    raw=canonical(result)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(raw)
    print("CKAD25X_FROZEN_DEVELOPMENT="+result["development_disposition"])
    print("CKAD25X_POLICY_BRIER="+json.dumps(
          {k:v["native_recall"] for k,v in result["held_brier_by_policy_method"].items()},
          sort_keys=True))
    print("CKAD25X_RETURN_RECOGNITION="+str(result["candidate_return_A_seeds_correct"]))
    print("CKAD25X_NOVEL_BRIER="+str(result["candidate_novel_brier"]))
    print("CKAD25X_GATES="+json.dumps(result["frozen_gates"],sort_keys=True))
    print("CKAD25X_RESULT_SHA256="+digest(raw))
    print("CKAD25X_WALL_SECONDS="+str(round(time.monotonic()-t,3)))


if __name__=="__main__":
    main()

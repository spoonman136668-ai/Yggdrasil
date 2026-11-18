"""CKAD25-W frozen source-free unlabeled A/B/A causal recall, novel C/D control.

One original source-owned NativeCumulativeLearner learns A and B in persisted
numeric causal committees, then gets unrelated pressure P/Q. The candidate
sees only four target-world do/outcome triples, never a regime label.
The source-only conventional Bayesian controls are fully equal-informed.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
import math
import random
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

HERE=Path(__file__).resolve().parent
HELP=HERE.parent/"CKAD25-S"/"run.py"
CHECKPOINT="c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f"
SEEDS=(51041,51047)
PHASES=("A","B","A","C","D")
METHODS=("native_recall","full_exact_bayes","exact_gate","logistic_gate",
         "forest_gate","recency_B","fixed_A","no_memory","oracle_label")


def require(ok,name):
    if not ok:raise ValueError("CKAD25W_"+name)


def helpers():
    spec=importlib.util.spec_from_file_location("ckad25s_pure_helpers",HELP)
    require(spec is not None and spec.loader is not None,"CONTROL_HELPER_UNAVAILABLE")
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    require(h.ORIGINAL_CHECKPOINT==CHECKPOINT and h.SEEDS==(1103,2207,3301),
            "PREVIOUS_SOURCE_IDENTITY_DRIFT")
    return h


def law(kind,mask):
    c0,c1,c2,a=((mask>>i)&1 for i in range(4))
    if kind=="A":return 1^(c0&a)^(c1&c2)
    if kind=="B":return c2^(c0&c1)^(c1&a)
    if kind=="C":return (c0^c1)&(c2^a)
    if kind=="D":return int(c0+c1+c2+a>=2)
    if kind=="P":return c0^c2^a
    if kind=="Q":return 1^(c0&c2)
    raise ValueError("CKAD25W_UNKNOWN_CAUSAL_FAMILY")


def roster(seed):
    order=list(range(16))
    sha=digest(canonical(["CKAD25-W-FIRST-SOURCE",seed]))
    random.Random(int(sha[:16],16)).shuffle(order)
    return order[:12],order[:4],order[12:]


def witnessed(kind,masks):
    return [[mask&7,mask>>3,law(kind,mask)] for mask in masks]


def train(m,slot,kind,masks,seed):
    rows=witnessed(kind,masks)
    ref=digest(canonical(["CKAD25-W-PUBLIC-NATIVE",seed,slot]))
    for batch in (rows[:8],rows[8:]):
        if batch:m=m.observe(slot,batch,digest(canonical(batch)),source_ref=ref)
    return m


def exact_survivors(h,records):
    # Independent full 697-member uniform conventional class, NEVER labels.
    observations=[(h.terms(c,a),y) for c,a,y in records]
    models=[]
    for num in range(4):
        for subset in itertools.combinations(range(16),num):
            if all((sum(features[j] for j in subset)&1)==y for features,y in observations):
                models.append(subset)
    return tuple(models)


def conventional_fraction(h,models,mask):
    if not models:return Fraction(1,2)
    feats=h.terms(mask&7,mask>>3)
    return Fraction(sum(sum(feats[j] for j in subset)&1 for subset in models),
                    len(models))


def exact_selector(h,models,diagnostics,mask):
    counts={}
    for slot in (1,2):
        weight=Fraction(1,1)
        for c,a,y in diagnostics:
            p=conventional_fraction(h,models[slot],c|(a<<3))
            weight*=p if y else (1-p)
        counts[slot]=weight
    total=counts[1]+counts[2]+Fraction(1,16)
    slot=max((1,2),key=lambda t:(counts[t],-t))
    chosen=(slot if counts[slot]/total>=Fraction(9,10) else None)
    pred=(conventional_fraction(h,models[chosen],mask) if chosen is not None
          else Fraction(1,2))
    p1=conventional_fraction(h,models[1],mask)
    p2=conventional_fraction(h,models[2],mask)
    continuous=(counts[1]*p1+counts[2]*p2+Fraction(1,32))/total
    return pred,chosen,continuous


def fitted_model_predictor(h,records,seed,method):
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    ys=[y for _,_,y in records]
    if method=="logistic":
        xs=[h.terms(c,a) for c,a,_ in records]
    else:
        xs=[h.vector(c,a) for c,a,_ in records]
    if len(set(ys))==1:
        return lambda mask:float(ys[0])
    if method=="logistic":
        fitted=LogisticRegression(C=1,max_iter=1000,solver="lbfgs",random_state=seed).fit(xs,ys)
    else:
        fitted=RandomForestClassifier(n_estimators=64,max_depth=4,n_jobs=1,
                                      random_state=seed).fit(xs,ys)
    cls=list(fitted.classes_).index(1)
    def value(mask):
        c,a=mask&7,mask>>3
        x=h.terms(c,a) if method=="logistic" else h.vector(c,a)
        return float(fitted.predict_proba([x])[0][cls])
    return value


def fitted_gate(functions,diagnostics,mask):
    scores={}
    for slot in (1,2):
        like=1.
        for c,a,y in diagnostics:
            p=functions[slot](c|(a<<3))
            like*=p if y else 1.-p
        scores[slot]=like
    denom=scores[1]+scores[2]+1/16
    chosen=max((1,2),key=lambda x:(scores[x],-x))
    return functions[chosen](mask) if scores[chosen]/denom>=.9 else .5


def brier(probs,held):
    return sum((float(p)-row[2])**2 for p,row in zip(probs,held))/4


def score():
    h=helpers()
    parent=h.snapshot()
    initial=parent.checkpoint()
    require(digest(initial)==CHECKPOINT,"OLD_NATIVE_CHECKPOINT")
    old_predictions=[parent.predict(0,c,a) for a in (0,1) for c in range(8)]
    phase_results=[]
    per_seed={}
    for seed in SEEDS:
        training_masks,probe_masks,held_masks=roster(seed)
        require(len(set(training_masks+held_masks))==16
                and not set(held_masks)&set(probe_masks)
                and set(probe_masks).issubset(training_masks),
                "SPLIT_OR_HELD_LEAK")
        current=NativeCumulativeLearner.restore(initial,CHECKPOINT)
        known={}
        models={}
        for slot,kind in ((1,"A"),(2,"B")):
            current=train(current,slot,kind,training_masks,seed)
            current=current.compile_causal_relations(slot)
            known[slot]=witnessed(kind,training_masks)
            models[slot]=exact_survivors(h,known[slot])
            require(len(models[slot])==current._compiled[slot].model_count,
                    "EXACT_COMMITTEE_COUNT_DISAGREEMENT")
        parent_bank=(current._compiled[1].checkpoint(),current._compiled[2].checkpoint())
        cold=NativeCumulativeLearner.restore(current.checkpoint(),digest(current.checkpoint()))
        for slot,kind in ((3,"P"),(4,"Q")):
            cold=train(cold,slot,kind,training_masks[:8],seed)
        source_raw=cold.checkpoint()
        cold=NativeCumulativeLearner.restore(source_raw,digest(source_raw))
        retained=(cold.checkpoint()==source_raw
                  and parent.checkpoint()==initial
                  and cold._properties.checkpoint()==parent._properties.checkpoint()
                  and cold._source._seen[0]==parent._source._seen[0]
                  and cold._hypotheses[0].checkpoint()==parent._hypotheses[0].checkpoint()
                  and cold._events[:len(parent._events)]==parent._events
                  and [cold.predict(0,c,a) for a in (0,1) for c in range(8)]==old_predictions
                  and (cold._compiled[1].checkpoint(),cold._compiled[2].checkpoint())==parent_bank
                  and [cold.info()["observed_inputs"][j] for j in (1,2,3,4)]==[12,12,8,8]
                  and not any(cold.info()["quarantined"][:5]))
        require(retained,"NATIVE_MEMORY_INTERFERENCE_RETENTION")
        logistic={i:fitted_model_predictor(h,known[i],seed,"logistic") for i in (1,2)}
        forest={i:fitted_model_predictor(h,known[i],seed,"forest") for i in (1,2)}
        per_seed[str(seed)]={"post_pressure_native_sha256":digest(source_raw),
                             "first_A_native_committee_sha256":digest(parent_bank[0]),
                             "first_B_native_committee_sha256":digest(parent_bank[1]),
                             "train_input_sha256":digest(canonical(training_masks)),
                             "diagnostic_input_sha256":digest(canonical(probe_masks)),
                             "held_input_sha256":digest(canonical(held_masks)),
                             "native_retention_pass":retained}
        for phase,kind in enumerate(PHASES):
            diagnostics=witnessed(kind,probe_masks)
            held=witnessed(kind,held_masks)
            candidates={m:[] for m in METHODS}
            selections=[]
            for mask in held_masks:
                c,a=mask&7,mask>>3
                num,den,slot=cold.recall_causal_regime([1,2],diagnostics,c,a)
                native=Fraction(num,den)
                exact,chosen,mix=exact_selector(h,models,diagnostics,mask)
                require(slot==chosen and native==exact,
                        "INDEPENDENT_CONVENTIONAL_HARD_GATE_PARITY")
                selections.append(slot)
                candidates["native_recall"].append(native)
                candidates["exact_gate"].append(exact)
                candidates["full_exact_bayes"].append(mix)
                candidates["logistic_gate"].append(fitted_gate(logistic,diagnostics,mask))
                candidates["forest_gate"].append(fitted_gate(forest,diagnostics,mask))
                for name,source_slot in (("fixed_A",1),("recency_B",2)):
                    p=cold.causal_relation_probability(source_slot,c,a)
                    candidates[name].append(Fraction(p[0],p[1]))
                candidates["no_memory"].append(.5)
                if kind in ("A","B"):
                    p=cold.causal_relation_probability(1 if kind=="A" else 2,c,a)
                    candidates["oracle_label"].append(Fraction(p[0],p[1]))
                else:candidates["oracle_label"].append(.5)
            require(len(set(selections))==1,"SELECTED_WORLD_DEPENDS_ON_HELD_QUERY")
            selected=selections[0]
            truth=[row[2] for row in held]
            all_metrics={}
            for name,vals in candidates.items():
                all_metrics[name]={
                    "brier":round(brier(vals,held),9),
                    "confident_answered":sum(float(v) in (0.,1.) for v in vals),
                    "confident_wrong":sum(float(v) in (0.,1.) and int(float(v))!=y
                                          for v,y in zip(vals,truth)),
                    "prediction_fractions":[[v.numerator,v.denominator]
                                             if isinstance(v,Fraction) else [round(v,12),1.]
                                             for v in vals]
                }
            phase_results.append({
                "seed":seed,"phase":phase,"hidden_world_evaluator_only":kind,
                "selected_native_source_slot":selected,
                "train_A_source_sha256":digest(canonical(known[1])),
                "train_B_source_sha256":digest(canonical(known[2])),
                "target_diagnostic_sha256":digest(canonical(diagnostics)),
                "held_input_sha256":digest(canonical([[m&7,m>>3] for m in held_masks])),
                "held_truth_sha256":digest(canonical(truth)),
                "diagnostics_count":4,"held_count":4,
                "first_A_repeat_is_not_independent":phase==2,
                "metrics":all_metrics
            })
    require(len(phase_results)==10,"CASE_COUNT")
    means={m:round(sum(r["metrics"][m]["brier"] for r in phase_results)/10,9)
           for m in METHODS}
    known=[r for r in phase_results if r["hidden_world_evaluator_only"] in ("A","B")]
    novel=[r for r in phase_results if r["hidden_world_evaluator_only"] in ("C","D")]
    ret=[r for r in phase_results if r["phase"]==2]
    known_answered=sum(r["metrics"]["native_recall"]["confident_answered"] for r in known)
    known_wrong=sum(r["metrics"]["native_recall"]["confident_wrong"] for r in known)
    known_correct_worlds=sum(r["selected_native_source_slot"]==
                              (1 if r["hidden_world_evaluator_only"]=="A" else 2) for r in known)
    novel_brier=sum(r["metrics"]["native_recall"]["brier"] for r in novel)/len(novel)
    novel_wrong=sum(r["metrics"]["native_recall"]["confident_wrong"] for r in novel)
    return_gain=(sum(r["metrics"]["recency_B"]["brier"]-
                     r["metrics"]["native_recall"]["brier"] for r in ret)/len(ret))
    checks={
        "native_original_and_compiled_retain_after_pressure":all(x["native_retention_pass"] for x in per_seed.values()),
        "return_A_gain_at_least_0_08":return_gain>=.08-1e-12,
        "at_least_12_confident_known_answers":known_answered>=12,
        "known_confident_wrong_at_most_2":known_wrong<=2,
        "recognize_at_least_3_of_6_known_phases":known_correct_worlds>=3,
        "novel_brier_not_above_0_27":novel_brier<=.27+1e-12,
        "novel_confident_wrong_at_most_1":novel_wrong<=1,
        "within_0_03_of_best_fitted_logistic_or_forest":
            means["native_recall"]<=min(means["logistic_gate"],means["forest_gate"])+.03+1e-12,
        "within_0_04_of_full_exact_Bayes_mixture":
            means["native_recall"]<=means["full_exact_bayes"]+.04+1e-12,
        "native_matches_independent_conventional_exact_gate":
            all(r["metrics"]["native_recall"]["prediction_fractions"]==
                r["metrics"]["exact_gate"]["prediction_fractions"] for r in phase_results)
    }
    return {
        "schema":"yggdrasil.ckad25w.unlabeled-regime-recall-dev.v1",
        "source_sha256":digest(Path(__file__).read_bytes()),
        "independent_helper_sha256":digest(HELP.read_bytes()),
        "original_native_checkpoint_sha256":CHECKPOINT,
        "seeds":list(SEEDS),"worlds":"A-B-A-C-D","source_free_native_training_rows":80,
        "source_free_target_diagnostic_rows":40,"phase_scored_outputs":40,
        "unique_independent_world_held_labels":32,"A_return_repeated_not_independent":True,
        "original_protected_world_actions":0,"source_owner_first_use":False,
        "one_native_cumulative_learner_per_seed":True,
        "native_causal_memory_uses_existing_checkpoint":True,
        "no_language_tokens":True,"accepted_main_changed":False,
        "per_seed":per_seed,"per_seed_phase":phase_results,"overall_mean_brier":means,
        "known_confident_answered":known_answered,"known_confident_wrong":known_wrong,
        "known_regimes_selected_correctly":known_correct_worlds,
        "return_A_brier_gain_vs_recency_B":round(return_gain,9),
        "novel_brier":round(novel_brier,9),"novel_confident_wrong":novel_wrong,
        "frozen_gates":checks,
        "disposition":"DEVELOPMENT_SIGNAL" if all(checks.values()) else "DEVELOPMENT_NO_GO",
        "scientific_pass":False,"accepted_model":False,"forge_dispatch":False,
        "native_promotion":False,"deployment":False
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    started=time.monotonic()
    data=score()
    raw=canonical(data)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(raw)
    print("CKAD25W_DISPOSITION="+data["disposition"])
    print("CKAD25W_BRIER="+json.dumps(data["overall_mean_brier"],sort_keys=True))
    print("CKAD25W_RETURN_GAIN="+str(data["return_A_brier_gain_vs_recency_B"]))
    print("CKAD25W_KNOWN_CONFIDENT="+str(data["known_confident_answered"]))
    print("CKAD25W_NOVEL_BRIER="+str(data["novel_brier"]))
    print("CKAD25W_GATES="+json.dumps(data["frozen_gates"],sort_keys=True))
    print("CKAD25W_RESULT_SHA256="+digest(raw))
    print("CKAD25W_DEV_SOURCE_SECONDS="+str(round(time.monotonic()-started,3)))


if __name__=="__main__":
    main()

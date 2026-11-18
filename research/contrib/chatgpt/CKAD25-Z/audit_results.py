"""Independent read-only reconstruction of CKAD25-Z genuine witness evidence.

Runs with only stdlib, DOES NOT import Yggdrasil native learner, scorer, any
science module or fit new training model. Original evaluator-only world laws
and source/held action IDs are supplied in the sealed result, not to a model.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import random
from pathlib import Path

SEEDS=(72011,72029,72047,72061)
WORLDS=("C","D1","D2")
METHODS={"guarded_native","exact_equivalent_697","source_unvalidated",
         "exact_broader_6885","fitted_logistic","fitted_forest",
         "unrestricted_world","privileged_oracle"}


def need(ok,kind):
    if not ok:raise ValueError("CKAD25Z_ORIGINAL_AUDIT_"+kind)


def encode(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def split(seed):
    x=list(range(16))
    h=sha(encode(["CKAD25-Z-SOURCE_SPLIT",seed]))
    random.Random(int(h[:16],16)).shuffle(x)
    return x[:12],x[12:14],x[14:]


def feature(x):
    return sum(1<<k for k in range(16) if x&k==k)


def predict(weight,x):
    return (weight&feature(x)).bit_count()&1


def all_source_models(records,size):
    evidence=[(feature(c|(a<<3)),y) for c,a,y in records]
    return tuple(w for n in range(size+1)
                 for ix in itertools.combinations(range(16),n)
                 for w in [sum(1<<k for k in ix)]
                 if all(((w&f).bit_count()&1)==y for f,y in evidence))


def probability(models,x):
    return Fraction(sum(predict(w,x) for w in models),len(models)) if models else Fraction(1,2)


def target(world,base,x,validation,held):
    y=predict(base,x)
    if world=="D1" and x in (validation[0],held[0]):return y^1
    if world=="D2" and x==held[0]:return y^1
    return y


def metric(pred,labels):
    x=[float(f) for f in pred]
    return {"brier":round(sum((p-y)**2 for p,y in zip(x,labels))/2,9),
            "confident":sum(p in (0,1) for p in x),
            "confident_wrong":sum(p in (0,1) and int(p)!=y for p,y in zip(x,labels))}


def check(raw):
    data=json.loads(raw)
    need(encode(data)==raw,"CANONICAL_BYTES")
    need(data["schema"]=="yggdrasil.ckad25z.native-falsifying-witness.v1","SCHEMA")
    need(data["science_seeds"]==list(SEEDS) and data["scored_original_primary"] is True,
         "PROSPECTIVE_SCIENCE_ROSTER")
    need(data["genuine_source_free_action_consequences"]==312 and
         data["held_phase_predictions"]==24,"ACTION_BUDGET")
    need(data["alias_worlds_not_independent_families"] is True
         and data["one_native_tokenless_learner_per_seed"] is True
         and data["native_source_weights_learned_from_real_actions"] is True
         and data["source_family_labels_not_passed_to_native"] is True,
         "NO_FALSE_SCIENTIFIC_NOVELTY")
    need(data["scientific_pass"] is False and
         data["universal_OOD_safety"] is False and
         data["information_theoretic_alias_D2_unresolved"] is True
         and data["conventional_superiority"] is False and
         data["original_owner_science_first_use"] is False
         and data["accepted_main_changed"] is False
         and data["forge_dispatch"] is False and data["native_promotion"] is False
         and data["merge"] is False and data["deployment"] is False,
         "AUTHORITY_OR_CLAIM")
    rows=data["per_seed_world"]
    need(len(rows)==12 and len(data["frozen_seeds_source_history"])==4,"CASE_ROSTER")
    actual={}
    for seed in SEEDS:
        source,validation,held=split(seed)
        state=data["frozen_seeds_source_history"][str(seed)]
        laws=state["source_weights_evaluator_only"]
        need(set(laws)=={"A","B","C"} and all(x.bit_count()==3 for x in laws.values()),
             "FROZEN_C_SOURCE_LAW_"+str(seed))
        need(len(set(laws.values()))==3 and
             all(sum(predict(laws[k],i)!=predict(laws[j],i) for i in source)>=4
                 for k,j in (("A","B"),("A","C"),("B","C")),"NEW_SOURCE_WORLD_DISCRIMINABLE")
        need(state["source_split_sha256"]==sha(encode(source))
             and state["validation_split_sha256"]==sha(encode(validation))
             and state["held_split_sha256"]==sha(encode(held))
             and state["source_preserved_after_three_new_worlds"] is True
             and state["original_old_source_unchanged"] is True
             and len(state["A_B_C_compiled_sha256"])==3,"FROZEN_SOURCE_RETENTION")
        source_records=[[m&7,m>>3,predict(laws["C"],m)] for m in source]
        base_models=all_source_models(source_records,3)
        need(len(base_models)==1,"UNIQUE_PRETRAINED_C_SOURCE")
        observed_case=[x for x in rows if x["seed"]==seed]
        need(len(observed_case)==3,"PER_SEED_WORLD_COUNT")
        for i,world in enumerate(WORLDS):
            row=next(x for x in observed_case if x["evaluator_only_world"]==world)
            key=(seed,world)
            need(key not in actual,"DUPLICATE_WORLD")
            actual[key]=True
            twelve=[[m&7,m>>3,target(world,laws["C"],m,validation,held)]
                    for m in source]
            two=[[m&7,m>>3,target(world,laws["C"],m,validation,held)]
                 for m in validation]
            y=[target(world,laws["C"],m,validation,held) for m in held]
            need(twelve==source_records and
                 row["episode"]==i and row["actual_source_actions"]==12
                 and row["actual_new_validation_actions"]==2
                 and row["native_learned_source_slot"]==3
                 and row["native_source_selection"]=="RECALLED"
                 and row["evidence_native_slot"]==12+i,"REAL_INTERVENTION_ACCOUNT")
            need(row["original_12_witness_sha256"]==sha(encode(twelve))
                 and row["new_2_witness_sha256"]==sha(encode(two))
                 and row["source_mask_sha256"]==sha(encode(source))
                 and row["validation_mask_sha256"]==sha(encode(validation))
                 and row["held_mask_sha256"]==sha(encode(held))
                 and row["held_truth_sha256"]==sha(encode(y))
                 and row["old_causal_memories_and_source_retained"] is True,
                 "SOURCE_VS_HELD_CUSTODY_"+str(seed)+world)
            condition=tuple(w for w in base_models
                            if all(predict(w,c|(a<<3))==v for c,a,v in two))
            expanded=all_source_models(twelve+two,5)
            need(row["conventional_697_source_survivors_before"]==1
                 and row["conventional_697_source_survivors_after"]==len(condition)
                 and row["strong_conventional_6885_survivors_after"]==len(expanded),
                 "INDEPENDENT_CLASS_SURVIVOR_COUNTS")
            expected_status="CONSISTENT" if condition else "FALSIFIED"
            need(row["native_validation_status"]==expected_status,
                 "NATIVE_FALSIFIER_PARITY_"+world)
            need(set(row["prediction_metrics"])==METHODS,"CONTROL_ROSTER")
            for name,value in row["prediction_metrics"].items():
                pieces=value["held_fraction"]
                need(len(pieces)==2,"HELD_CASE_COUNT")
                pred=[]
                for item in pieces:
                    need(type(item) is list and len(item)==2 and
                         type(item[0]) in (int,float) and type(item[1]) in (int,float)
                         and item[1]>0 and 0<=item[0]<=item[1],"PREDICTION_FRACTION")
                    pred.append(Fraction(item[0],item[1]) if
                                isinstance(item[0],int) and isinstance(item[1],int)
                                else item[0]/item[1])
                rebuilt=metric(pred,y)
                need(all(rebuilt[k]==value[k] for k in rebuilt),
                     "ORIGINAL_METRIC_RECONSTRUCTION_"+name+world)
            native=[Fraction(*x) for x in row["prediction_metrics"]["guarded_native"]["held_fraction"]]
            expected=[probability(condition,x) for x in held]
            need(native==expected
                 and row["prediction_metrics"]["guarded_native"]["held_fraction"]==
                     row["prediction_metrics"]["exact_equivalent_697"]["held_fraction"],
                 "FULL_INDEPENDENT_697_NATIVE_PARITY")
            for method,models in (("source_unvalidated",base_models),
                                  ("exact_broader_6885",expanded)):
                predicted=[probability(models,x) for x in held]
                stored=[Fraction(*part) for part in row["prediction_metrics"][method]["held_fraction"]]
                need(predicted==stored,"STRONG_CLASS_REBUILD_"+method)
            need([Fraction(*v) for v in row["prediction_metrics"]["unrestricted_world"]["held_fraction"]]
                  ==[Fraction(1,2)]*2,"UNRESTRICTED_WORLD_EPISTEMIC_PRIOR")
            need([Fraction(*v) for v in row["prediction_metrics"]["privileged_oracle"]["held_fraction"]]
                  ==list(map(Fraction,y)),"PRIVILEGED_EVALUATOR_CEILING")
    need(len(actual)==12,"ALL_SOURCE_EPISODES_PRESENT")
    byworld={}
    means={}
    for world in WORLDS:
        byworld[world]={}
        for method in METHODS:
            value=round(sum(x["prediction_metrics"][method]["brier"]
                            for x in rows if x["evaluator_only_world"]==world)/4,9)
            need(abs(value-data["by_world_brier"][world][method])<=1e-8,
                 "ORIGINAL_WORLD_BRIER_"+world+method)
            byworld[world][method]=value
    for method in METHODS:
        value=round(sum(x["prediction_metrics"][method]["brier"] for x in rows)/12,9)
        need(abs(value-data["mean_brier"][method])<=1e-8,"ORIGINAL_MEAN_"+method)
        means[method]=value
    need(all(data["gates"].values()) and
         data["development_disposition"]=="BOUNDED_DETECTION_SIGNAL",
         "PRESERVE_FROZEN_BOUNDARY")
    need(byworld["C"]["guarded_native"]==0.
         and byworld["D1"]["guarded_native"]==.25
         and byworld["D2"]["guarded_native"]==.5,
         "NONCONVENTIONAL_RESULT_SWAP")
    return {"original_sha256":sha(raw),"episodes_verified":len(actual),
            "genuine_source_actions":312,"bounded_held":24,
            "mean_brier":means,"by_world_brier":byworld,
            "disposition":data["development_disposition"],
            "universal_safety":False,"owner_first_use":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("original_result",type=Path)
    args=p.parse_args()
    proof=check(args.original_result.read_bytes())
    print("CKAD25Z_INDEPENDENT_SOURCE_ACTUAL_697_AND_6885_AUDIT_PASS")
    print(json.dumps(proof,sort_keys=True))


if __name__=="__main__":
    main()

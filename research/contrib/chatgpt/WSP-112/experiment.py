"""First-use-only WSP112 unfamiliar causal law experiment.

DO NOT execute until immutable candidate tree passes full inherited Linux+Windows
regression and independent G29 atlas acceptance. No fixture imports this file.
The evaluator reveals each law's consequence only for a model-chosen action
until ALL unqueried predictions are sealed. Primary seed v1 only.
"""
from __future__ import annotations
import argparse
import copy
from hashlib import sha256
import json
import time
import numpy as np
from core import DirectWriter,SymbolicGF2,ConventionalGP,prior_from_full_training
from bayes import ActiveBayes
from oracle import training_tables,transfer_degree,label

SEED="v1"
N_WORLDS=256
N_QUERIES=8

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

def fresh_direct(prototype):
    obj=copy.copy(prototype)
    obj.hyp=prototype.hyp.copy()
    obj.observations=[]
    obj.synapses=prototype.synapses.copy()
    obj.numeric_effect_weights=prototype.numeric_effect_weights.copy()
    return obj

def fresh_bayesian(prototype):
    obj=copy.copy(prototype)
    obj.mass=[w.copy() for w in prototype.mass]
    obj.obs=[]
    obj.pred=prototype.pred.copy()
    return obj

def fresh_conventional(prototype):
    obj=copy.copy(prototype)
    obj.obs=[]
    obj.predictive=prototype.predictive.copy()
    obj.variances=prototype.variances.copy()
    return obj

def train_and_seal():
    start=time.monotonic()
    cpu=time.process_time()
    train=np.asarray(training_tables(SEED),dtype=np.uint8)
    if train.shape!=(512,16,2):
        raise AssertionError("training table shape")
    train_receipt=sha256(train.tobytes()).hexdigest()
    original_prior=prior_from_full_training(train)
    direct_factory=DirectWriter(original_prior)
    bayes_factory=ActiveBayes(train)
    gp_factory=ConventionalGP(train)
    records=[]
    first_retention=None
    total_interventions={}
    for world in range(N_WORLDS):
        degree=transfer_degree(world)
        models={
            "direct":fresh_direct(direct_factory),
            "independent_bayes":fresh_bayesian(bayes_factory),
            "independent_symbolic":SymbolicGF2(),
            "fully_fitted_conventional":fresh_conventional(gp_factory),
            "random_interventions":fresh_direct(direct_factory),
            "passive_lexicographic":fresh_direct(direct_factory),
        }
        sequences={k:[] for k in models}
        fixed_rng=np.random.default_rng(int.from_bytes(sha256(
            f"WSP112|RANDOM|v1|{world}".encode("ascii")).digest()[:8],"big"))
        random_order=[int(x) for x in fixed_rng.permutation(16)[:N_QUERIES]]
        for step in range(N_QUERIES):
            for name,model in models.items():
                if name=="random_interventions":
                    x=random_order[step]
                elif name=="passive_lexicographic":
                    x=step
                else:
                    x=model.choose()
                if x in [a for a,_ in sequences[name]]:
                    raise AssertionError("repeated information access")
                y=label("transfer",world,degree,x,SEED)
                model.observe(x,y)
                if model.predict(x)!=y:
                    raise AssertionError("observed causal response not retained")
                sequences[name].append((x,y))
        predictions={}
        for name,model in models.items():
            if len(sequences[name])!=N_QUERIES or len(set(x for x,_ in sequences[name]))!=N_QUERIES:
                raise AssertionError("unequal intervention budgets")
            used={x for x,_ in sequences[name]}
            predictions[name]=[(x,model.predict(x)) for x in range(16) if x not in used]
            if len(predictions[name])!=8:raise AssertionError("heldout support size")
            total_interventions[name]=total_interventions.get(name,0)+len(sequences[name])
        # Same-observation controls remove adaptive action-selection information differences.
        same={
            "matched_symbolic":SymbolicGF2(),
            "matched_bayes":fresh_bayesian(bayes_factory),
            "matched_conventional":fresh_conventional(gp_factory),
        }
        for x,y in sequences["direct"]:
            for model in same.values():model.observe(x,y)
        direct_unqueried=[x for x,_ in predictions["direct"]]
        for name,model in same.items():
            predictions[name]=[(x,model.predict(x)) for x in direct_unqueried]
        negative=fresh_direct(direct_factory)
        for x,y in sequences["direct"]:
            negative.observe((x+1)%16,y)
        predictions["wrong_action_binding"]=[(x,negative.predict(x)) for x in direct_unqueried]
        predictions["no_interventions"]=[(x,direct_factory.predict(x)) for x in direct_unqueried]
        snap=models["direct"].checkpoint()
        restored=DirectWriter.restore(snap)
        if [(x,restored.predict(x)) for x in range(16)] != [(x,models["direct"].predict(x)) for x in range(16)]:
            raise AssertionError("cold transfer memory prediction drift")
        if first_retention is None:
            first_retention=sha256(canonical(snap).encode()).hexdigest()
            corrupt={"schema":snap["schema"],"sha256":snap["sha256"],
                     "blocks":dict(snap["blocks"])}
            val=corrupt["blocks"]["synapses"]
            corrupt["blocks"]["synapses"]=("ff" if val[:2]!="ff" else "00")+val[2:]
            try:DirectWriter.restore(corrupt)
            except ValueError:pass
            else:raise AssertionError("tampered transfer weights accepted")
        records.append({"world":world,"degree":degree,
                        "interventions":sequences,"unqueried_predictions":predictions,
                        "cold_sha256":sha256(canonical(snap).encode()).hexdigest()})
    prescore=sha256(canonical(records).encode()).hexdigest()
    # Evaluation label oracle access below this line ONLY (except selected action effects).
    # The entire 256-world prediction and intervention transcript is sealed first.
    metrics={}
    arms=tuple(records[0]["unqueried_predictions"])
    for arm in arms:
        by_family={}
        world_accuracy=[]
        total_correct=0
        total_count=0
        for family in (3,4):
            scores=[]
            for row in records:
                if row["degree"]!=family:continue
                outcomes=row["unqueried_predictions"][arm]
                correct=sum(int(value==label("transfer",row["world"],family,x,SEED))
                            for x,value in outcomes)
                scores.append(correct/len(outcomes))
                world_accuracy.append((row["world"],correct/len(outcomes)))
                total_correct+=correct
                total_count+=len(outcomes)
            by_family[str(family)]={"correct":int(round(sum(scores)*8)),
                                    "total":len(scores)*8,
                                    "accuracy":float(np.mean(scores))}
        metrics[arm]={"correct":total_correct,"total":total_count,
                      "accuracy":total_correct/total_count,
                      "family":by_family,
                      "per_world_accuracy":sorted(world_accuracy)}
    # Strongest independent comparator; paired bootstrap over WORLD, not transitions.
    best=max(("independent_bayes","independent_symbolic","fully_fitted_conventional"),
             key=lambda name:metrics[name]["accuracy"])
    direct_world=dict(metrics["direct"]["per_world_accuracy"])
    baseline_world=dict(metrics[best]["per_world_accuracy"])
    delta=np.array([direct_world[g]-baseline_world[g] for g in range(N_WORLDS)])
    rng=np.random.default_rng(112)
    bootstrap=np.asarray([np.mean(delta[rng.integers(0,N_WORLDS,N_WORLDS)])
                          for _ in range(1000)])
    lower=float(np.quantile(bootstrap,0.025))
    overall_gain=float(delta.mean())
    primary_gain=overall_gain>=0.02 and lower>0 and all(
       metrics["direct"]["family"][str(f)]["accuracy"] >=
       metrics[best]["family"][str(f)]["accuracy"] for f in (3,4))
    return {
        "experiment":"WSP112",
        "status":"PRIMARY_SYNTHETIC_DEV_ONLY_NOT_INDEPENDENT_SCIENTIFIC_PASS",
        "preimplementation_prereg_sha":"36e4f1141aaf0fe0b2841a6ffb081301a05393aa",
        "train_worlds":len(train),
        "train_table_sha256":train_receipt,
        "unfamiliar_worlds":N_WORLDS,
        "allowed_interventions_per_world":N_QUERIES,
        "intervention_counts":total_interventions,
        "prescore_predictions_and_interventions_sha256":prescore,
        "first_cold_memory_sha256":first_retention,
        "cold_restored_worlds":N_WORLDS,
        "tamper_negative":"REJECTED",
        "heldout":{name:{key:value for key,value in v.items()
                         if key!="per_world_accuracy"} for name,v in metrics.items()},
        "best_independent_comparator":best,
        "direct_minus_best_two_bit_accuracy":overall_gain,
        "paired_world_bootstrap_95_lower":lower,
        "primary_preliminary_gain":bool(primary_gain),
        "scientific_pass":False,
        "independent_validation_cohorts_consumed":0,
        "wall_seconds":time.monotonic()-start,
        "cpu_seconds":time.process_time()-cpu,
        "limitations":"A 4-bit observable Boolean state-action world with full published algebraic feature basis and reset privilege; no unknown sensor primitives or real-world open-ended laws. Bayes is an independent strong comparator. Exact causal effects seen only on selected interventions. This does not establish AGI, efficient training, autonomous scientific acceptance or deployment."
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--frozen-unfamiliar-law-primary-dev",action="store_true",required=True)
    parser.parse_args()
    result=train_and_seal()
    print("WSP112_PRIMARY_DEV="+canonical(result),flush=True)

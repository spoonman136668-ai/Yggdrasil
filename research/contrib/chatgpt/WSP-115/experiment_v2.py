"""WSP115 v2 NEW first-use-only world-sharded nonlinear causal evaluation.

Never import into fixture tests without injecting a completely fabricated
oracle module first. The 1024-intervention, 64-node primary is run BEFORE
any lower-capacity fallback. Heldout labels are unopened until every model's
all-budget predictions, evidence, and checkpoint hashes have been sealed.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"WSP-114"))
from collections import defaultdict
from hashlib import sha256
import json
from math import isfinite
import time
import tracemalloc
import numpy as np

from native import (NativeWriter, effect_from_parameters, grammar,
                    LADDER,FULL_BUDGET)
from controls import IndependentSymbolic,ConvergedRidge
from oracle_v2 import common_training,transfer_effect,heldout_inputs

PREREG="3ab8b239d0e92646e4eb895cc8828f06bdec1a3a"
PRIMARY_NODES=64
PRIMARY_WORLDS=16
PRIMARY_HELDOUT=512
PRIMARY_BUDGET=1024
PRIMARY_LADDER=(1024,512,256,128,64,32,16,8)
ARMS=("direct","independent_symbolic","conventional_ridge","random","passive")

def encode(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

def query_for(name,nodes,world,step,model):
    if name=="direct":
        return model.choose(world)
    if name=="independent_symbolic":
        return model.choose(world)
    if name=="passive":
        return NativeWriter.candidate(0,step,0,nodes,
            namespace="WSP114|PASSIVE|v1")
    if name=="random":
        return NativeWriter.candidate(world,step,0,nodes,
            namespace="WSP114|RANDOM|v1")
    if name=="conventional_ridge":
        return NativeWriter.candidate(world,step,0,nodes,
            namespace="WSP114|RIDGE|v1")
    raise ValueError("unknown arm")

def new_model(name,nodes,world):
    if name in ("direct","random","passive"):
        return NativeWriter(nodes,f"WSP114|{name}|{world}")
    if name=="independent_symbolic":
        return IndependentSymbolic(nodes)
    if name=="conventional_ridge":
        return ConvergedRidge(nodes,l2=1.0)
    raise ValueError("unknown method")

def model_rank(model,nodes):
    if isinstance(model,NativeWriter):
        return list(model.ranks)
    if isinstance(model,IndependentSymbolic):
        model.fit()
        return list(model.ranks)
    return [None]*nodes

def predict_all(model,queries):
    return [int(model.predict(s,a)) for s,a in queries]

def ablations(full_direct,queries,nodes):
    zero=NativeWriter(nodes,"zero")
    absent=predict_all(zero,queries)
    masked=[]
    for j,coef in enumerate(full_direct.active_weights):
        m=sum(1<<k for k,term in enumerate(grammar(min(12,j))) if len(term)==1)
        masked.append(coef&m)
    no_pairs=[int(effect_from_parameters(s,a,masked,nodes)) for s,a in queries]
    return {"zero_memory":absent,"remove_quadratic_synapses":no_pairs}

def evaluation_capacity(nodes,worlds=16,budget=1024,ladder=PRIMARY_LADDER,heldout=512,world_ids=None):
    if type(nodes)!=int or nodes not in (64,48,32,16):
        raise ValueError("unsupported test capacity")
    if type(budget)!=int or not 1<=budget<=FULL_BUDGET or not ladder or ladder[0]!=budget:
        raise ValueError("invalid high-first budget")
    if any(not 1<=b<=budget for b in ladder) or tuple(sorted(ladder,reverse=True))!=tuple(ladder):
        raise ValueError("budget order changed")
    if type(worlds)!=int or not 1<=worlds<=16 or type(heldout)!=int or not 1<=heldout<=512:
        raise ValueError("evaluation bound")
    if world_ids is None:world_ids=tuple(range(worlds))
    if len(world_ids)!=worlds or len(set(world_ids))!=worlds or any(type(w)!=int or not 0<=w<16 for w in world_ids):
        raise ValueError("world shard membership must be unique and bounded")
    start=time.perf_counter()
    cpu=time.process_time()
    train_start=time.process_time()
    train=common_training(nodes)
    if len(train)!=32 or any(len(x)!=256 for x in train):
        raise AssertionError("unequal common training source")
    train_sha=sha256(encode(train).encode()).hexdigest()
    train_cpu=time.process_time()-train_start

    # We deliberately do not fit hidden test-world coefficients from the
    # public linear-only source. Its grammar and examples are equally
    # available to every arm, including the strong exact symbolic control.
    results=[]
    accounting=defaultdict(lambda:{"cpu":0.0,"wall":0.0,"peak_bytes":0,
                                    "observations":0,"cold_restores":0})
    checkpoints=set(ladder)
    tracemalloc.start()
    try:
        for world in world_ids:
            inputs=heldout_inputs(nodes,world,heldout)
            if len(inputs)!=heldout or len(set(inputs))!=heldout:
                raise AssertionError("heldout query collision")
            heldout_set=set(inputs)
            record={"world":world,"heldout_queries":[list(q) for q in inputs],
                    "arms":{},"matched_independent_symbolic":{},
                    "ablations":{}}
            for name in ARMS:
                model=new_model(name,nodes,world)
                tracer_cpu=time.process_time()
                tracer_wall=time.perf_counter()
                tracemalloc.reset_peak()
                observations=[]
                snapshots={}
                high_checkpoint=None
                for step in range(budget):
                    s,a=query_for(name,nodes,world,step,model)
                    if (s,a) in heldout_set:
                        raise AssertionError("selected intervention leaks heldout query")
                    if (s,a) in {(x,y) for x,y,_ in observations}:
                        raise AssertionError("duplicate intervention")
                    observed=transfer_effect(nodes,world,s,a)
                    model.observe(s,a,observed)
                    observations.append((s,a,observed))
                    b=step+1
                    if b in checkpoints:
                        if hasattr(model,"fit"):model.fit()
                        snapshots[str(b)]={
                            "predictions":predict_all(model,inputs),
                            "ranks":model_rank(model,nodes),
                            "observation_sha256":sha256(encode(observations).encode()).hexdigest()
                        }
                        if b==budget and isinstance(model,NativeWriter):
                            high_checkpoint=model.checkpoint()
                if len(observations)!=budget:
                    raise AssertionError("not all original interventions consumed")
                cold_sha=None
                if name=="direct":
                    if high_checkpoint is None:raise AssertionError("native snapshot missing")
                    cold=NativeWriter.restore(high_checkpoint)
                    if (cold.active_weights!=model.active_weights or cold.ranks!=model.ranks
                        or predict_all(cold,inputs)!=snapshots[str(budget)]["predictions"]):
                        raise AssertionError("cold restored native predictions drift")
                    corrupted={"schema":high_checkpoint["schema"],
                               "sha256":high_checkpoint["sha256"],
                               "data":dict(high_checkpoint["data"])}
                    corrupted["data"]["ranks"]=[r+1 for r in corrupted["data"]["ranks"]]
                    try:NativeWriter.restore(corrupted)
                    except ValueError:pass
                    else:raise AssertionError("tamper rejection failed")
                    cold_sha=sha256(encode(high_checkpoint).encode()).hexdigest()
                    accounting[name]["cold_restores"]+=1
                    record["ablations"]=ablations(model,inputs,nodes)
                    record["native_rank_full"]=list(model.ranks)
                    record["native_synaptic_float32_bytes"]=sum(
                        len(r)*4 for r in model.synapses)
                accounting[name]["cpu"]+=time.process_time()-tracer_cpu
                accounting[name]["wall"]+=time.perf_counter()-tracer_wall
                accounting[name]["peak_bytes"]=max(accounting[name]["peak_bytes"],
                    tracemalloc.get_traced_memory()[1])
                accounting[name]["observations"]+=len(observations)
                record["arms"][name]={"interventions":[list(q) for q in observations],
                                     "snapshots":snapshots,
                                     "cold_sha256":cold_sha}

            # Matched-information independent exact symbolic learner: it uses
            # only the observations the direct arm itself actually requested.
            matched=IndependentSymbolic(nodes)
            direct_transcript=record["arms"]["direct"]["interventions"]
            snap={}
            for i,(s,a,o) in enumerate(direct_transcript):
                matched.observe(s,a,o)
                if i+1 in checkpoints:
                    matched.fit()
                    snap[str(i+1)]={"predictions":predict_all(matched,inputs),
                                   "ranks":list(matched.ranks)}
            record["matched_independent_symbolic"]=snap
            results.append(record)

        sealed=sha256(encode(results).encode()).hexdigest()
        # === SCIENTIFIC CUSTODY BOUNDARY ===
        # No hidden heldout law/effect is read until the complete all-world,
        # all-arm and all-budget transcript and prediction digest exists.
        scores={}
        categories=ARMS+("matched_independent_symbolic","zero_memory",
                        "remove_quadratic_synapses")
        for category in categories:
            budgets=(budget,) if category in ("zero_memory","remove_quadratic_synapses") else ladder
            by_budget={}
            for b in budgets:
                total=0;full_match=0;bit_total=0;bit_match=0
                by_world=[]
                for record in results:
                    world=record["world"]
                    correct=0
                    if category in record["arms"]:
                        predictions=record["arms"][category]["snapshots"][str(b)]["predictions"]
                    elif category=="matched_independent_symbolic":
                        predictions=record["matched_independent_symbolic"][str(b)]["predictions"]
                    else:
                        predictions=record["ablations"][category]
                    for (s,a),candidate in zip(record["heldout_queries"],predictions):
                        label=transfer_effect(nodes,world,s,a)
                        correct+=int(candidate==label)
                        bit_match+=nodes-((candidate^label).bit_count())
                        bit_total+=nodes
                    total+=len(predictions)
                    full_match+=correct
                    by_world.append(correct/len(predictions))
                by_budget[str(b)]={"full_correct":full_match,"full_total":total,
                                   "full_exact_accuracy":full_match/total,
                                   "bit_accuracy":bit_match/bit_total,
                                   "per_world_full_accuracy":by_world}
            scores[category]=by_budget
        high={k:v[str(budget)]["full_exact_accuracy"] for k,v in scores.items()
              if str(budget) in v}
        strongest_control=max(("independent_symbolic","matched_independent_symbolic",
                               "conventional_ridge"),key=lambda k:high[k])
        gain=high["direct"]-high[strongest_control]
        accurate=high["direct"]>=0.95
        earliest=None
        for b in reversed(ladder):
            p=scores["direct"][str(b)]["full_exact_accuracy"]
            c=max(scores["independent_symbolic"][str(b)]["full_exact_accuracy"],
                  scores["matched_independent_symbolic"][str(b)]["full_exact_accuracy"],
                  scores["conventional_ridge"][str(b)]["full_exact_accuracy"])
            if p>=0.95 and p>=c-0.01:
                earliest=b
                break

        outcome={
            "experiment":"WSP115_V2_FRESH_SHARDED", 
            "world_ids":list(world_ids),
            "classification":"HIGH_FIRST_1024_V2_SHARD_DEV_NOT_SCIENTIFIC_PASS",
            "primary_nodes":nodes,
            "worlds":worlds,
            "max_interventions_per_arm_per_world":budget,
            "budget_ladder":list(ladder),
            "prereg_sha":PREREG,
            "shared_public_linear_train_sha256":train_sha,
            "shared_public_train_cpu_seconds":train_cpu,
            "original_before_score_all_arm_transcript_and_prediction_sha256":sealed,
            "heldout_full_state_per_arm_per_budget":worlds*heldout,
            "native_cold_restore_worlds":accounting["direct"]["cold_restores"],
            "tampered_checkpoint_rejected":True,
            "direct_high_accuracy":high["direct"],
            "strongest_control":strongest_control,
            "strongest_control_high_accuracy":high[strongest_control],
            "direct_minus_best_control_accuracy":gain,
            "first_qualifying_budget_from_high_first_ladder":earliest,
            "max_budget_capacity_dev_pass":accurate,
            "per_arm_all_inclusive_observed_cpu_wall_peak":dict(accounting),
            "scores":scores,
            "whole_process_cpu_seconds":time.process_time()-cpu,
            "whole_process_wall_seconds":time.perf_counter()-start,
            "scientific_pass":False,
            "no_promotions":True,
            "limitations":"Known 64-node causal order, XOR plus pair feature grammar, perfect state resets, artificial effects and preregistered generators. Model writes float32 numerical coefficients through generic GF2 fitting, and an independent exact symbolic solver is a strong baseline. Any accuracy tie is a null for native superiority. Measurements include tracemalloc, whose overhead means no like-for-like native runtime speed claim."
        }
        for name in ARMS:
            if accounting[name]["observations"]!=worlds*budget:
                raise AssertionError("unequal arm information budget")
        if not all(isfinite(x) for x in (gain,outcome["whole_process_wall_seconds"],
                                     high["direct"])):
            raise AssertionError("nonsensical metric")
        return outcome
    finally:
        tracemalloc.stop()

def run(shard):
    """One first-use world pair, all methods, all budgets, same exact-source."""
    if type(shard) is not int or not 0<=shard<8:
        raise ValueError("v2 shard must be 0..7")
    world_ids=(2*shard,2*shard+1)
    result=evaluation_capacity(PRIMARY_NODES,2,PRIMARY_BUDGET,
        PRIMARY_LADDER,PRIMARY_HELDOUT,world_ids=world_ids)
    if result["world_ids"]!=list(world_ids):
        raise AssertionError("mismatched v2 shard membership")
    return {
        "program":"WSP115_V2_INDEPENDENT_1024_HIGH_FIRST",
        "prereg":PREREG,
        "v2_shard":shard,
        "tested_capacity":64,
        "v2_world_ids":list(world_ids),
        "result":result,
        "original_v2_shard_consumed":True,
        "scientific_pass":False,
        "accepted_model_mutation":False,
        "global_accuracy_qualification":"PENDING_ALL_EIGHT_SHARDS",
        "v1_reuse":False
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--frozen-v2-shard",type=int,required=True,
                        choices=range(8))
    args=parser.parse_args()
    print("WSP115_V2_SHARD_RESULT="+encode(run(args.frozen_v2_shard)),flush=True)

"""WSP113 one-shot original unfamiliar dense causal graph DEV evaluator.

DO NOT run before exact-tree complete Linux+Windows regression and independent
G29 source-atlas acceptance. Only oracle-labelled selected interventions may
reach model code. All transfer heldout predictions and action transcripts are
sealed in SHA256 before opening the protected heldout graph masks/effects.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from math import isfinite
from random import Random
import time
from native import DirectCausalWriter,EDGES,SUPPORT
from controls import ExactBayesianGraph,IndependentSymbolicGraph,FittedKernelGraph
from oracle import training_observations,transfer_effect,graph_mask

PRIMARY_SEED="v1"
WORLDS=128
QUERY_BUDGET=8
HELDOUT=tuple((s,a) for s in range(8,16) for a in range(8))

def pack(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

def planned_trajectories(world):
    """Nonlearner evaluator instruction sequence, fixed before heldout scoring."""
    walks=[]
    for start in range(8,16):
        acts=[]
        for k in range(3):
            digest=sha256(f"WSP113|TRAJ|{PRIMARY_SEED}|{world}|{start}|{k}".encode()).digest()
            acts.append(digest[0]%8)
        walks.append((start,tuple(acts)))
    return tuple(walks)

def independent_training():
    start=time.process_time()
    raw=training_observations(PRIMARY_SEED)
    if len(raw)!=128 or any(len(t)!=128 for t in raw):
        raise AssertionError("incorrect common training exposure")
    seal=sha256(pack(raw).encode()).hexdigest()
    return raw,seal,time.process_time()-start

def predict_walk(model,start,actions):
    if hasattr(model,"triple"):
        return model.triple(start,actions)
    states=[]
    for a in actions:
        start=model.predict(start,a)
        states.append(start)
    return tuple(states)

def score_one_world(world, model_name, model, query_log):
    observations={tuple(q[:2]) for q in query_log}
    if len(query_log)!=8 or len(observations)!=8 or not observations.issubset(SUPPORT):
        raise AssertionError("over-budget or out-of-support observation")
    heldout=[(s,a,model.predict(s,a)) for s,a in HELDOUT]
    trajectories=[(s,list(acts),list(predict_walk(model,s,acts)))
                  for s,acts in planned_trajectories(world)]
    return {"heldout":heldout,"trajectory":trajectories}

def run():
    total_wall=time.perf_counter()
    train,train_sha,train_cpu=independent_training()
    model_families=("direct","symbolic","bayesian","conventional","random","passive")
    ledger={name:{"cpu":0.0,"wall":0.0,"worlds":[]} for name in model_families}
    records=[]
    for w in range(WORLDS):
        world_record={"world":w,"arms":{}}
        for name in model_families:
            t0=time.perf_counter()
            c0=time.process_time()
            if name=="direct" or name in ("random","passive"):
                model=DirectCausalWriter()
            elif name=="symbolic":model=IndependentSymbolicGraph()
            elif name=="bayesian":model=ExactBayesianGraph()
            else:model=FittedKernelGraph(train)
            if name=="random":
                rng=Random(int.from_bytes(sha256(
                    f"WSP113|RANDOM|v1|{w}".encode()).digest()[:8],"big"))
                chosen=rng.sample(SUPPORT,QUERY_BUDGET)
            elif name=="passive":
                chosen=SUPPORT[:QUERY_BUDGET]
            else:chosen=None
            observations=[]
            for k in range(QUERY_BUDGET):
                s,a=chosen[k] if chosen is not None else model.choose()
                if (s,a) not in SUPPORT or (s,a) in {(x,y) for x,y,_ in observations}:
                    raise AssertionError("invalid adaptive intervention")
                response=transfer_effect(w,s,a,PRIMARY_SEED)
                model.observe(s,a,response)
                if model.predict(s,a)!=response:
                    raise AssertionError("learner failed known observed action")
                observations.append((s,a,response))
            predicted=score_one_world(w,name,model,observations)
            native_snap=None
            if name=="direct":
                native_snap=model.checkpoint()
                cold=DirectCausalWriter.restore(native_snap)
                if (predicted!=score_one_world(w,name,cold,observations)):
                    raise AssertionError("cold predictions do not match")
                tamper={"schema":native_snap["schema"],"sha256":native_snap["sha256"],
                        "fields":dict(native_snap["fields"])}
                original=tamper["fields"]["weights_le_f32"]
                tamper["fields"]["weights_le_f32"]=("ff" if original[:2]!="ff" else "00")+original[2:]
                try:DirectCausalWriter.restore(tamper)
                except ValueError:pass
                else:raise AssertionError("tampered memory was accepted")
            guessed_mask=None
            if isinstance(model,DirectCausalWriter):
                guessed_mask=sum(int(bool(v))<<i for i,v in enumerate(model.synapses))
            elif isinstance(model,IndependentSymbolicGraph):
                guessed_mask=model.graph_mask()
            elif isinstance(model,ExactBayesianGraph):
                guessed_mask=min(model.hypotheses)
            # No graph oracle read here; only predicted effects and model's guessed edges.
            world_record["arms"][name]={
                "observations":observations,
                "predict":predicted,
                "guessed_mask":guessed_mask,
                "native_snapshot_sha256":(sha256(pack(native_snap).encode()).hexdigest()
                                          if native_snap is not None else None)}
            elapsed_cpu=time.process_time()-c0
            elapsed_wall=time.perf_counter()-t0
            ledger[name]["cpu"]+=elapsed_cpu
            ledger[name]["wall"]+=elapsed_wall
            ledger[name]["worlds"].append({"cpu":elapsed_cpu,"wall":elapsed_wall})
        # Same-feedback baselines, no new hidden feedback requests.
        direct_obs=world_record["arms"]["direct"]["observations"]
        matched={
          "same_action_symbolic":IndependentSymbolicGraph(),
          "same_action_bayesian":ExactBayesianGraph(),
          "same_action_conventional":FittedKernelGraph(train)
        }
        world_record["matched"]={}
        for name,model in matched.items():
            for s,a,y in direct_obs:model.observe(s,a,y)
            world_record["matched"][name]=score_one_world(w,name,model,direct_obs)
        zero=DirectCausalWriter()
        world_record["no_feedback"]=score_one_world(w,"zero",zero,direct_obs)
        wrong=DirectCausalWriter()
        for s,a,y in direct_obs:
            wrong.observe(s,a,y)
        # Negative: deliberately rotate all six stored edges, without any new effects.
        wrong.synapses=wrong.synapses[1:]+wrong.synapses[:1]
        world_record["wrong_binding"]=score_one_world(w,"rotated",wrong,direct_obs)
        records.append(world_record)
    prescore=sha256(pack(records).encode()).hexdigest()
    # *** CUSTODY BOUNDARY: only after this complete seal may we inspect
    # all original hidden graph masks or unqueried intervention/rollout answers.
    classified={}
    categories=list(model_families)+list(records[0]["matched"])+["no_feedback","wrong_binding"]
    for category in categories:
        correct=0
        total=0
        steps_correct=0
        steps_total=0
        trajectories_correct=0
        density=Counter()
        edge_correct=0
        edge_total=0
        edge_confusion=Counter()
        node_confusion=[Counter() for _ in range(4)]
        per_world=[]
        for row in records:
            w=row["world"]
            actual_mask=graph_mask("transfer",w,PRIMARY_SEED)
            ecount=actual_mask.bit_count()
            if category in row["arms"]:
                bundle=row["arms"][category]["predict"]
                guessed=row["arms"][category]["guessed_mask"]
            elif category in row["matched"]:
                bundle=row["matched"][category]
                guessed=None
            else:
                bundle=row[category]
                guessed=None
            one_correct=0
            for s,a,y in bundle["heldout"]:
                answer=transfer_effect(w,s,a,PRIMARY_SEED)
                one_correct+=int(y==answer)
                for bit in range(4):
                    truth=(answer>>bit)&1
                    predicted=(y>>bit)&1
                    key="tp" if truth and predicted else ("fp" if predicted else ("fn" if truth else "tn"))
                    node_confusion[bit][key]+=1
            correct+=one_correct
            total+=len(bundle["heldout"])
            density[ecount]=(density.get(ecount,(0,0))[0]+one_correct,
                             density.get(ecount,(0,0))[1]+len(bundle["heldout"]))
            per_world.append(one_correct/len(bundle["heldout"]))
            if guessed is not None:
                for i in range(6):
                    truth=(actual_mask>>i)&1
                    predicted=(guessed>>i)&1
                    edge_correct+=int(predicted==truth)
                    key="tp" if truth and predicted else ("fp" if predicted else ("fn" if truth else "tn"))
                    edge_confusion[key]+=1
                edge_total+=6
            for start,actions,guess_sequence in bundle["trajectory"]:
                state=start
                truth=[]
                for a in actions:
                    state=transfer_effect(w,state,a,PRIMARY_SEED)
                    truth.append(state)
                steps_correct+=sum(int(x==y) for x,y in zip(guess_sequence,truth))
                steps_total+=len(actions)
                trajectories_correct+=int(guess_sequence==truth)
        classified[category]={
          "correct":correct,"total":total,"accuracy":correct/total,
          "trajectory_exact":trajectories_correct,"trajectory_total":WORLDS*8,
          "trajectory_accuracy":trajectories_correct/(WORLDS*8),
          "step_accuracy":steps_correct/steps_total,
          "graph_bit_accuracy":edge_correct/edge_total if edge_total else None,
          "graph_edge_precision":edge_confusion["tp"]/max(1,edge_confusion["tp"]+edge_confusion["fp"]) if edge_total else None,
          "graph_edge_recall":edge_confusion["tp"]/max(1,edge_confusion["tp"]+edge_confusion["fn"]) if edge_total else None,
          "per_node_bit":{str(i):{"tp":n["tp"],"fp":n["fp"],"fn":n["fn"],"tn":n["tn"],
            "precision":n["tp"]/max(1,n["tp"]+n["fp"]),
            "recall":n["tp"]/max(1,n["tp"]+n["fn"])}
            for i,n in enumerate(node_confusion)},
          "per_density":{str(k):{"correct":v[0],"total":v[1],
                                 "accuracy":v[0]/v[1]} for k,v in sorted(density.items())},
          "_world_accuracy":per_world
        }
    best=max(("symbolic","bayesian","conventional"),key=lambda k:classified[k]["accuracy"])
    differences=[a-b for a,b in zip(classified["direct"]["_world_accuracy"],
                                   classified[best]["_world_accuracy"])]
    rng=Random(113)
    means=[]
    for _ in range(1000):
        means.append(sum(differences[rng.randrange(WORLDS)]
                         for __ in range(WORLDS))/WORLDS)
    means.sort()
    ci_lower=means[24]
    gain=sum(differences)/WORLDS
    output={
       "experiment":"WSP113",
       "status":"ORIGINAL_SYNTHETIC_DEV_NOT_INDEPENDENT_SCIENTIFIC_PASS",
       "prereg_commit":"57c2cd7778d3a70d149350865f170dee73a9bc81",
       "train_sha256":train_sha,
       "shared_training_cpu_seconds":train_cpu,
       "transfer_worlds":WORLDS,
       "adaptive_interventions_per_arm_per_world":QUERY_BUDGET,
       "all_heldout_predictions_transcripts_sha256_before_oracle_scoring":prescore,
       "cold_restored_worlds":WORLDS,
       "tampered_native_memory_rejected":True,
       "scores":{k:{x:y for x,y in v.items() if x!="_world_accuracy"}
                 for k,v in classified.items()},
       "strongest_control":best,
       "native_accuracy_minus_best":gain,
       "paired_95_bootstrap_lower":ci_lower,
       "per_arm_cpu_seconds":{k:v["cpu"] for k,v in ledger.items()},
       "per_arm_wall_seconds":{k:v["wall"] for k,v in ledger.items()},
       "whole_evaluation_wall_seconds":time.perf_counter()-total_wall,
       "new_independent_validation_cohorts_consumed":0,
       "scientific_pass":False,
       "limitations":"Supplied 4-node ordering, XOR causal mechanism and perfect reset; only dense-edge composition is unfamiliar. Causal equations solved in software as GF2, then six numbers written into explicit synaptic slots. Strong exact graph Bayesian/symbolic controls, fully fitted kernel and matching eight active outcomes. No general intelligence or autonomous architecture integration."
    }
    if not all(isfinite(x) for x in (*output["per_arm_cpu_seconds"].values(),output["native_accuracy_minus_best"],ci_lower)):
        raise AssertionError("nonfinite evaluation value")
    return output

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--frozen-dense-causal-graph-primary-dev",action="store_true",required=True)
    parser.parse_args()
    print("WSP113_ORIGINAL_DEV="+pack(run()),flush=True)

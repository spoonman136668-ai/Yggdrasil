"""WSP-157: historical ORIGINAL public DTR source, native 164-byte training.

Historical development only: previous DTR02 source actions were consumed in 2026-10.
Never imports original source, replays any reset/do, or opens protected VALID/DEV.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import time

from yggdrasil.public_causal_cells import PublicCausalCells

HERE=Path(__file__).resolve().parent
DATA=HERE/"consumed-original-public-fit.json"
SCHEMA="wsp157.consumed-original-dtr02-public-fit-packed.v1"
ORIGINAL_JSON_SHA="6527cb222b79c72b8d11224f63420cd8f0ddd31e152d46711a2b49b3ce7be47e"
ORIGINAL_CANON_SHA="016bf254ade33b936386abf7829ff90d765da71105e2beebcb130c95febe7d1d"
ORIGINAL_REP_SHA=(
 "978eb1fd88c5f5d477235f163566de84f24d69fa9bd862daf2e85cb4fae9876c",
 "71c85934cef85ead0d62eefc0a99aa41db2f85c42ff33bc056c973edbcbe32e2",
 "a96e9d02dba315a16b063dad4a259b2d2276adf5f471daa3103358fbfa4cdde7",
)
ORIGINAL_SOURCE="CausalAILab/Causal-Gymnasium@c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
ORIGINAL_SOURCE_BLOB="6af2371dce21804140ea141ccb7be14e003ba275"
ORIGINAL_ARCHIVE_SHA="ada547777ba2ba49070fe2606ac99c8d9248532f1cb16c8a0f8eab0f4001508c"
PACKED_SHA="cc4234fc00f50f2a5ae8841783320241864ff3c6bef9360e0399c66c10bb4820"
TRAIN_SIZES=(32,64,128,192)
HELD_START=192
HELD_N=64
LOGISTIC_ITERS=3000
LOGISTIC_L2=0.001
LOGISTIC_CONVERGE=1e-8

def require(flag,reason):
    if not flag:
        raise ValueError("WSP157_"+reason)

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_original_fit(data_path=DATA):
    """Verify historical original-source receipt *before* constructing learners."""
    raw=Path(data_path).read_bytes()
    require(0<len(raw)<8192,"PACKED_FILE_SIZE")
    def unique(pairs):
        d={}
        for k,v in pairs:
            require(k not in d,"REPEATED_SOURCE_KEY")
            d[k]=v
        return d
    d=json.loads(raw.decode("ascii"),object_pairs_hook=unique)
    require(raw==json.dumps(d,indent=2,sort_keys=False).encode("ascii")+b"\n",
            "PACKED_FILE_NONCANONICAL")
    require(type(d) is dict and d["schema"]==SCHEMA
            and d["history"]=="PREVIOUSLY_CONSUMED_PUBLIC_DEVELOPMENT_ONLY"
            and d["original_upstream"]==ORIGINAL_SOURCE
            and d["archive_sha256"]==ORIGINAL_ARCHIVE_SHA
            and d["original_fit_json_sha256"]==ORIGINAL_JSON_SHA
            and d["original_canonical_trace_sha256"]==ORIGINAL_CANON_SHA
            and d["original_fit_replica_sha256"]==list(ORIGINAL_REP_SHA)
            and d["packed_hex_sha256"]==PACKED_SHA
            and d["replica_count"]==3 and d["fit_per_replica"]==256
            and d["source_seed_rule"]=="1100000 + replica*10000 + row_idx"
            and d["artifact_id"]==12492506361
            and d["original_run_id"]==39932201242
            and d["new_original_actions"]==0
            and d["protected_val_dev_contents_included"] is False
            and d["field_order"]==["s1","x1","s2","x2","y"],
            "PACKED_SOURCE_CUSTODY")
    blob=bytes.fromhex(d["packed_hex"])
    require(len(blob)==768 and sha(blob)==PACKED_SHA
            and all(n<=31 for n in blob),"PACKED_SOURCE_BYTES")
    reps=[]
    pairs=((0,0),(0,1),(1,0),(1,1))
    for i in range(3):
        observations=[]
        for n,b in enumerate(blob[i*256:(i+1)*256]):
            s1,x1,s2,x2,y=((b>>4)&1,(b>>3)&1,(b>>2)&1,(b>>1)&1,b&1)
            require((x1,x2)==pairs[n%4],"ORIGINAL_EXPLORATION_DRIFT")
            observations.append({"seed":1100000+10000*i+n,
                                 "s1":s1,"x1":x1,"s2":s2,"x2":x2,"y":y})
        require(sha(canonical(observations))==ORIGINAL_REP_SHA[i],
                "ORIGINAL_REPLICA_SHA_MISMATCH")
        reps.append({"index":i,"fit":observations})
    reconstructed={"schema":"mass.dtr02.fit-public-traces.v1","replicas":reps}
    require(sha(canonical(reconstructed))==ORIGINAL_CANON_SHA,
            "ORIGINAL_CANONICAL_TRACE_MISMATCH")
    source_doc=json.dumps(reconstructed,sort_keys=True,indent=2).encode("ascii")+b"\n"
    require(sha(source_doc)==ORIGINAL_JSON_SHA,"ORIGINAL_FILE_SHA_MISMATCH")
    return tuple(tuple(x["fit"]) for x in reps)

def stage_slot(row):
    return row["s1"]

def reward_slot(row):
    return 2+4*row["s1"]+2*row["x1"]+row["s2"]

def addr(slot):
    require(type(slot) is int and 0<=slot<16,"NATIVE_ADDRESS")
    return (slot,False) if slot<7 else (slot-7,True)

def features(row,target):
    if target=="transition":
        s,x=row["s1"],row["x1"]
        return (1,s,x,s*x)
    if target=="reward":
        s,a,t,b=row["s1"],row["x1"],row["s2"],row["x2"]
        return (1,s,a,t,b,s*a,s*t,s*b,a*t,a*b,t*b)
    raise ValueError("WSP157_TARGET_INVALID")

def observation(row,target):
    if target=="transition":
        return (stage_slot(row),row["x1"],row["s2"])
    return (reward_slot(row),row["x2"],row["y"])

def fit_native(rows):
    model=PublicCausalCells()
    for row in rows:
        for target in ("transition","reward"):
            slot,action,outcome=observation(row,target)
            n,retained=addr(slot)
            model.observe(n,action,outcome,retained=retained)
    cold=PublicCausalCells.restore(model.snapshot())
    require(cold.snapshot()==model.snapshot() and len(model.snapshot())==164,
            "COLD_NATIVE_CHECKPOINT_DIFFERENCE")
    return cold

def native_prob(native,row,target):
    slot,action,_=observation(row,target)
    n,retained=addr(slot)
    num,den=native.outcome_probability(n,action,retained=retained)
    return num,den

def independent_fits(rows):
    counts={}
    for row in rows:
        for target in ("transition","reward"):
            slot,action,outcome=observation(row,target)
            k=(slot,action)
            if k not in counts:
                counts[k]=[0,0]
            counts[k][outcome]+=1
    return counts

def beta(counts,row,target):
    slot,action,_=observation(row,target)
    fails,success=counts.get((slot,action),(0,0))
    return success+1,fails+success+2

def mle(counts,row,target):
    slot,action,_=observation(row,target)
    fails,success=counts.get((slot,action),(0,0))
    return success/(fails+success) if fails+success else 0.5

def sig(x):
    if x>=0:
        z=math.exp(-x)
        return 1/(1+z)
    z=math.exp(x)
    return z/(1+z)

def logistic_fit(rows,target):
    """Pure batch gradient conventional control; no source equations or oracle."""
    # Compress only identical public FIT feature rows; each original episode
    # still independently contributes exactly one observed outcome.
    bag={}
    for r in rows:
        x=features(r,target)
        y=r["s2"] if target=="transition" else r["y"]
        if x not in bag:
            bag[x]=[0,0]
        bag[x][0]+=1
        bag[x][1]+=y
    n=len(rows)
    width=len(next(iter(bag)))
    w=[0.0]*width
    converge=False
    iters=0
    for step in range(LOGISTIC_ITERS):
        grad=[0.0]*width
        for x,(count,successes) in sorted(bag.items()):
            err=count*sig(sum(v*t for v,t in zip(x,w)))-successes
            for j,v in enumerate(x):
                grad[j]+=err*v/n
        for j in range(width):
            grad[j]+=LOGISTIC_L2*w[j]
        # Fixed diminishing step, not tuned on hidden held outcomes.
        rate=0.55/(1+step/3000)
        delta=max(abs(rate*g) for g in grad)
        w=[v-rate*g for v,g in zip(w,grad)]
        iters=step+1
        if delta<LOGISTIC_CONVERGE:
            converge=True
            break
    return tuple(w),{"iterations":iters,"converged":converge,
                     "fit_observations":n,"features":width}

def logistic_prob(model,row,target):
    return sig(sum(x*w for x,w in zip(features(row,target),model)))

def score_for(rows,models):
    native,counts,fit_transition,fit_reward=models
    scores={arm:{"transition_sum_brier":0.0,"reward_sum_brier":0.0}
            for arm in ("native_beta","exact_beta","fitted_mle","logistic","chance")}
    for row in rows:
        for target in ("transition","reward"):
            outcome=row["s2"] if target=="transition" else row["y"]
            n,d=native_prob(native,row,target)
            bn,bd=beta(counts,row,target)
            require((n,d)==(bn,bd),"NATIVE_STRONG_BAYESIAN_PARITY")
            predicted={
                "native_beta":n/d,
                "exact_beta":bn/bd,
                "fitted_mle":mle(counts,row,target),
                "logistic":logistic_prob(
                    fit_transition if target=="transition" else fit_reward,
                    row,target),
                "chance":0.5,
            }
            for arm,p in predicted.items():
                scores[arm][target+"_sum_brier"]+=(p-outcome)**2
    return scores

def run(data_path=DATA):
    began_cpu=time.process_time()
    original=read_original_fit(data_path)
    all_entries=[]
    total={arm:{"transition_sum_brier":0.0,"reward_sum_brier":0.0,"scored":0}
           for arm in ("native_beta","exact_beta","fitted_mle","logistic","chance")}
    retained=[]
    for rid,source in enumerate(original):
        require(len(source)==256 and len(source[HELD_START:])==HELD_N,
                "REPLICA_SPLIT_DRIFT")
        previous=None
        held=source[HELD_START:]
        for k in TRAIN_SIZES:
            train=source[:k]
            model=fit_native(train)
            if previous:
                incremental=PublicCausalCells.restore(previous["checkpoint"])
                for row in source[previous["n"]:k]:
                    for target in ("transition","reward"):
                        slot,action,outcome=observation(row,target)
                        address,retained_flag=addr(slot)
                        incremental.observe(address,action,outcome,
                                            retained=retained_flag)
                require(incremental.snapshot()==model.snapshot(),
                        "NATIVE_INCREMENTAL_COLD_PARITY")
            checkpoint=model.snapshot()
            previous={"n":k,"checkpoint":checkpoint}
            counts=independent_fits(train)
            lt,meta_t=logistic_fit(train,"transition")
            ly,meta_y=logistic_fit(train,"reward")
            score=score_for(held,(model,counts,lt,ly))
            for arm,part in score.items():
                a=total[arm]
                a["transition_sum_brier"]+=part["transition_sum_brier"]
                a["reward_sum_brier"]+=part["reward_sum_brier"]
                a["scored"]+=2*HELD_N
            row={
                "replica":rid,"trained_original_episodes":k,
                "held_original_episodes":HELD_N,"native_checkpoint_sha256":sha(checkpoint),
                "native_bytes":len(checkpoint),
                "logistic_fit_transition":meta_t,"logistic_fit_reward":meta_y,
                "held":{arm:{
                    "transition_brier":round(part["transition_sum_brier"]/HELD_N,12),
                    "reward_brier":round(part["reward_sum_brier"]/HELD_N,12),
                    "pooled_brier":round((part["transition_sum_brier"]+
                                          part["reward_sum_brier"])/(2*HELD_N),12),
                    "scored_targets":2*HELD_N}
                for arm,part in score.items()}
            }
            require(row["held"]["native_beta"]==row["held"]["exact_beta"],
                    "BAYESIAN_HELD_PARITY")
            all_entries.append(row)
            retained.append([rid,k,row["native_checkpoint_sha256"]])
    # Each arm scored 3 replicas * 4 nested exposures *64 held *2 outcomes.
    require(all(x["scored"]==1536 for x in total.values()),
            "HELD_SCORE_DENOMINATOR")
    method_scores={
        arm:{"transition_brier":round(s["transition_sum_brier"]/768,12),
             "reward_brier":round(s["reward_sum_brier"]/768,12),
             "pooled_brier":round((s["transition_sum_brier"]+
                                   s["reward_sum_brier"])/1536,12),
             "scored":s["scored"]}
        for arm,s in total.items()
    }
    require(method_scores["native_beta"]==method_scores["exact_beta"],
            "AGGREGATE_NATIVE_BAYESIAN_PARITY")
    report={
        "schema":"wsp157.historical-original-public-DTR-native-development-result.v1",
        "classification":"AUTHENTIC_CONSUMED_DTR_NATIVE_DEVELOPMENT_QUALIFIED",
        "source_archive_sha256":ORIGINAL_ARCHIVE_SHA,
        "source_traces_sha256":ORIGINAL_CANON_SHA,
        "source_fit_replicas":3,"original_fit_episodes":768,
        "train_sizes":TRAIN_SIZES,"held_start":HELD_START,
        "held_per_replica":HELD_N,"original_source_new_reset_or_do":0,
        "same_source_matched_policies_executed":False,
        "source_first_use":False,"scientific_pass":False,"native_accepted":False,
        "prior_FIT_actions_already_consumed":True,"checkpoint_bytes":164,
        "total_score_per_arm":method_scores,
        "individual_scores":all_entries,
        "checkpoint_lineage_sha256":sha(canonical(retained)),
        "protected_original_valid_dev_unused":True,
        "matched_conventional_and_native_fit_inputs":True,
        "native_vs_exact_beta_gain":0
    }
    stable=sha(canonical(report))
    return report,stable,{"cpu_s":round(time.process_time()-began_cpu,6)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    report,stable,resource=run()
    payload=dict(report,stable_sha256=stable,resource_diagnostic=resource)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print("WSP157_STABLE_SHA256="+stable,flush=True)
    print("WSP157_METRICS="+json.dumps(
        {**report["total_score_per_arm"],"source_first_use":False,
         "new_original_actions":0,"resource":resource},sort_keys=True),
         flush=True)
if __name__=="__main__":
    main()

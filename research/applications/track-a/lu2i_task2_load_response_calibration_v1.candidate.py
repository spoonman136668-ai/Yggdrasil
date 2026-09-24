#!/usr/bin/env python3
import hashlib, json, math, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path

import lu2g_second_task_compositional_service_transfer_v1 as frozen

g=frozen.g
p=g.p

PREREG_LU2I="41cbbac5e7a4d58888c25cd562b9e92ef5cdb44c"
PARENT_LU2H="dba00160c1e783af47c6d43b8d695b608c171736"
PARENT_LU2G="1fcfef885ca9bd8c3219333965d90cc9cc4a60e9"
PARENT_LU2GF1="e9a01aa97587fc97dde073cb2a6a35ad141006cd"
LOADS=(1,2,3)
REPLICATES=10
MAX_LOAD=3

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()

def manifest_identity(m):
    x=dict(m); x.pop("manifest_sha256",None)
    return hashlib.sha256(canonical(x)).hexdigest()

def valid_program(x):
    return g.valid_program(x)

def derive_programs(lu2if1,replicate):
    if not isinstance(lu2if1,str) or len(lu2if1)!=40: raise ValueError("freeze sha")
    if replicate not in range(1,REPLICATES+1): raise ValueError(replicate)
    used=set(); out={}
    for stream in ("C","S"):
        out[stream]={}
        for stage in ("A","B"):
            counter=0
            while True:
                material=f"LU2I-TASK2-LOAD|{lu2if1}|{replicate}|{stream}|{stage}|{counter}"
                cand=int.from_bytes(hashlib.sha256(material.encode()).digest()[:2],"big")
                counter+=1
                if not valid_program(cand) or cand in used: continue
                used.add(cand); out[stream][stage]=cand; break
    return out

def l3_streams(t):
    return tuple(g.arrival_streams(t))

def selected_slots(load,t):
    if load not in LOADS: raise ValueError(load)
    ph=p.phase_of(t)
    mod=t%4
    if load==3:
        return (0,1,2)
    if ph in (0,3,4):
        if load==2:
            return (0,2) if t%2==0 else (0,1)
        return (0,) if t%2==0 else (1,)
    if ph==1:
        if load==2:
            return (0,2) if mod in (0,1) else (0,1)
        return (2,) if mod==0 else (0,)
    if load==2:
        return (0,1) if mod in (0,1) else (1,2)
    return (0,) if mod==0 else (1,)

def make_arrivals(seed,programs,load):
    out=[]
    for t in range(p.T):
        streams=l3_streams(t)
        for slot in selected_slots(load,t):
            rid=t*MAX_LOAD+slot
            stream=streams[slot]
            bits=tuple((p.h64("LU2I-TASK2-BITS",seed,rid,k)>>k)&1 for k in range(4))
            out.append({
                "rid":rid,"t":t,"slot":slot,"stream":stream,"bits":bits,
                "program_a":programs[stream]["A"],"program_b":programs[stream]["B"],
            })
    if len(out)!=p.T*load: raise AssertionError(("arrival count",load,len(out)))
    return out

def calibration_manifest(lu2if1,replicate,load):
    ns=f"LU2I-TASK2-LOAD-CALIBRATION|{lu2if1}|{replicate}"
    seed=hashlib.sha256(ns.encode()).hexdigest()[:32]
    programs=derive_programs(lu2if1,replicate)
    arrivals=make_arrivals(seed,programs,load)
    m={
        "kind":"LU2I_LOAD_CALIBRATION",
        "lu2i_prereg_commit":PREREG_LU2I,
        "parent_lu2h":PARENT_LU2H,
        "parent_lu2g":PARENT_LU2G,
        "parent_lu2gf1":PARENT_LU2GF1,
        "lu2if1":lu2if1,
        "replicate":replicate,
        "load":load,
        "seed_namespace":ns,
        "seed":seed,
        "programs":programs,
        "arrivals":arrivals,
        "corrupt_ids":[x["rid"] for x in arrivals if p.u01("LU2I-TASK2-CORRUPT",seed,x["rid"])<0.05],
        "lesion":sorted(p.lesion_set(seed)),
        "anchors0":p.anchors_for(seed,0),
        "anchors4":p.anchors_for(seed,128),
        "n":p.N,"t":p.T,"d":p.D,"r_task":p.R_TASK,"route_edges":6,
        "g5_full":False,"requests_per_epoch":load,"process_ops_per_request":2,
    }
    m["manifest_sha256"]=manifest_identity(m)
    return m

def calibration_manifests(lu2if1):
    return [calibration_manifest(lu2if1,k,L) for k in range(1,REPLICATES+1) for L in LOADS]

def validate_manifest(m):
    if m["manifest_sha256"]!=manifest_identity(m): raise AssertionError("manifest hash")
    if m["lu2i_prereg_commit"]!=PREREG_LU2I: raise AssertionError("prereg")
    if (m["parent_lu2h"],m["parent_lu2g"],m["parent_lu2gf1"])!=(PARENT_LU2H,PARENT_LU2G,PARENT_LU2GF1):
        raise AssertionError("lineage")
    if m["load"] not in LOADS or m["requests_per_epoch"]!=m["load"]: raise AssertionError("load")
    if (m["n"],m["t"],m["d"],m["r_task"],m["route_edges"],m["g5_full"])!=(64,160,2,2,6,False):
        raise AssertionError("substrate")
    if m["process_ops_per_request"]!=2 or p.EXPIRY!=32: raise AssertionError("task/expiry")
    k=m["replicate"]; freeze=m["lu2if1"]
    ns=f"LU2I-TASK2-LOAD-CALIBRATION|{freeze}|{k}"
    if m["seed_namespace"]!=ns or m["seed"]!=hashlib.sha256(ns.encode()).hexdigest()[:32]:
        raise AssertionError("seed")
    if m["programs"]!=derive_programs(freeze,k): raise AssertionError("programs")
    if m["arrivals"]!=make_arrivals(m["seed"],m["programs"],m["load"]): raise AssertionError("arrivals")
    if m["corrupt_ids"]!=[x["rid"] for x in m["arrivals"] if p.u01("LU2I-TASK2-CORRUPT",m["seed"],x["rid"])<0.05]:
        raise AssertionError("corruption")
    if m["lesion"]!=sorted(p.lesion_set(m["seed"])): raise AssertionError("lesion")
    if m["anchors0"]!=p.anchors_for(m["seed"],0) or m["anchors4"]!=p.anchors_for(m["seed"],128):
        raise AssertionError("anchors")
    by=Counter(x["t"] for x in m["arrivals"])
    if any(by[t]!=m["load"] for t in range(p.T)): raise AssertionError("per-epoch load")
    return True

def strict_baseline(result):
    return (
        all(result["phase"][str(ph)]["correct_done"]>=1 for ph in range(5))
        and result["incorrect_done"]==0
        and all(result["stream_total"][s]>=1 for s in ("C","S"))
        and result["repair"]["repair_integrity"]
        and result["operations_per_correct_completion"] is not None
        and math.isfinite(result["operations_per_correct_completion"])
        and result["matching_duplicate_cell"]==0
        and result["matching_duplicate_request"]==0
    )

def quantile(vals,q):
    if not vals: return None
    ys=sorted(vals)
    idx=max(0,min(len(ys)-1,math.ceil(q*len(ys))-1))
    return ys[idx]

def stat(vals):
    if not vals: return {"count":0,"mean":None,"median":None,"p90":None,"max":None}
    return {
        "count":len(vals),"mean":sum(vals)/len(vals),
        "median":statistics.median(vals),"p90":quantile(vals,.90),"max":max(vals),
    }

def phase_state_counts(snaps):
    labels=("U","H","C","S","FC","FS")
    out={}
    for ph in range(5):
        rows=snaps[ph*32:(ph+1)*32]
        agg={x:[] for x in labels}
        for states in rows:
            c=Counter(states)
            for x in labels: agg[x].append(c[x])
        out[str(ph)]={x:(sum(v)/len(v) if v else None) for x,v in agg.items()}
    return out

def run_observed(m):
    validate_manifest(m)
    old_validate=g.validate_manifest
    old_load=g.REQUESTS_PER_EPOCH
    old_req=g.Task2Request
    old_do=g.do_operation
    old_step=g.developmental_step
    refs={}; first_sense={}; snaps=[]

    def request_factory(*args,**kwargs):
        r=old_req(*args,**kwargs)
        refs[r.rid]=r
        return r

    def observed_do(seed,t,cell,op,r,trace):
        if op=="SENSE" and r.rid not in first_sense:
            first_sense[r.rid]=t
        return old_do(seed,t,cell,op,r,trace)

    def observed_step(mode,seed,t,states,timers,bstate,q_prev,q_prev_side,requests):
        out=old_step(mode,seed,t,states,timers,bstate,q_prev,q_prev_side,requests)
        snaps.append(tuple(states))
        return out

    g.validate_manifest=validate_manifest
    g.REQUESTS_PER_EPOCH=m["load"]
    g.Task2Request=request_factory
    g.do_operation=observed_do
    g.developmental_step=observed_step
    try:
        result,state_history,tel=g.run_world(m,"U_A0")
    finally:
        g.validate_manifest=old_validate
        g.REQUESTS_PER_EPOCH=old_load
        g.Task2Request=old_req
        g.do_operation=old_do
        g.developmental_step=old_step

    waits=[first_sense[rid]-r.created for rid,r in refs.items() if rid in first_sense]
    return {
        "manifest_sha256":m["manifest_sha256"],
        "replicate":m["replicate"],"load":m["load"],
        "strict_baseline_feasible":strict_baseline(result),
        "pre_sense":stat(waits),
        "correct_done":result["correct_done"],
        "incorrect_done":result["incorrect_done"],
        "expired":result["expired"],
        "backlog":result["backlog"],
        "operations_per_correct_completion":result["operations_per_correct_completion"],
        "repair":result["repair"],
        "phase":result["phase"],
        "stream_total":result["stream_total"],
        "events":result["events"],
        "phase_state_mean":phase_state_counts(snaps),
        "u_a0_telemetry_is_none":tel is None,
        "matching_duplicate_cell":result["matching_duplicate_cell"],
        "matching_duplicate_request":result["matching_duplicate_request"],
        "trace_sha256":result["trace_sha256"],
        "state_sha256":result["state_sha256"],
    }

def schedule_counts(load,phase):
    counts=Counter()
    for t in range(phase*32,(phase+1)*32):
        streams=l3_streams(t)
        for slot in selected_slots(load,t): counts[streams[slot]]+=1
    return dict(counts)

def mechanical_gate():
    freeze="0"*40
    programs=derive_programs(freeze,1)
    ms={L:calibration_manifest(freeze,1,L) for L in LOADS}
    for m in ms.values(): validate_manifest(m)
    sets={L:{x["rid"] for x in ms[L]["arrivals"]} for L in LOADS}
    shared_ok=True
    rows={L:{x["rid"]:x for x in ms[L]["arrivals"]} for L in LOADS}
    for rid in sets[1]:
        if rows[1][rid]["bits"]!=rows[2][rid]["bits"] or rows[1][rid]["bits"]!=rows[3][rid]["bits"]: shared_ok=False
        c1=rid in set(ms[1]["corrupt_ids"]); c2=rid in set(ms[2]["corrupt_ids"]); c3=rid in set(ms[3]["corrupt_ids"])
        if not (c1==c2==c3): shared_ok=False
    for rid in sets[2]:
        if rows[2][rid]["bits"]!=rows[3][rid]["bits"]: shared_ok=False
        if (rid in set(ms[2]["corrupt_ids"]))!=(rid in set(ms[3]["corrupt_ids"])): shared_ok=False

    schedule_ok=all(tuple(x["stream"] for x in ms[3]["arrivals"] if x["t"]==t)==l3_streams(t) for t in range(p.T))
    ratios={}
    for L in LOADS:
        ratios[str(L)]={str(ph):schedule_counts(L,ph) for ph in range(5)}
    ratio_ok=True
    for L in LOADS:
        if ratios[str(L)]["0"]["C"]!=ratios[str(L)]["0"]["S"]: ratio_ok=False
        if ratios[str(L)]["3"]["C"]!=ratios[str(L)]["3"]["S"]: ratio_ok=False
        if ratios[str(L)]["4"]["C"]!=ratios[str(L)]["4"]["S"]: ratio_ok=False
        if ratios[str(L)]["1"]["C"]!=3*ratios[str(L)]["1"]["S"]: ratio_ok=False
        if ratios[str(L)]["2"]["S"]!=3*ratios[str(L)]["2"]["C"]: ratio_ok=False

    fixture=g.stage_repair_fixture()
    observed={str(L):run_observed(ms[L]) for L in LOADS}
    probes={
        "l3_exact_lu2g_schedule":schedule_ok,
        "l2_subset_l3":sets[2] < sets[3],
        "l1_subset_l2":sets[1] < sets[2],
        "phase_ratios_exact_all_loads":ratio_ok,
        "shared_request_bits_and_corruption_exact":shared_ok,
        "paired_programs_exact":ms[1]["programs"]==ms[2]["programs"]==ms[3]["programs"],
        "paired_lesion_exact":ms[1]["lesion"]==ms[2]["lesion"]==ms[3]["lesion"],
        "paired_anchors_exact":ms[1]["anchors0"]==ms[2]["anchors0"]==ms[3]["anchors0"] and ms[1]["anchors4"]==ms[2]["anchors4"]==ms[3]["anchors4"],
        "u_a0_no_learned_telemetry":all(observed[str(L)]["u_a0_telemetry_is_none"] for L in LOADS),
        "expiry_32":p.EXPIRY==32,
        "task2_repair_fixture":bool(fixture["stage_order_ok"] and fixture["repair_ok"] and fixture["immutable_provenance_unchanged"]),
        "zero_incorrect_done_mechanical":all(observed[str(L)]["incorrect_done"]==0 for L in LOADS),
        "matching_integrity":all(observed[str(L)]["matching_duplicate_cell"]==0 and observed[str(L)]["matching_duplicate_request"]==0 for L in LOADS),
    }
    return {"probes":probes,"all_pass":all(probes.values()),"ratios":ratios,"observed":observed}

def summarize(rows):
    by={L:[x for x in rows if x["load"]==L] for L in LOADS}
    summary={}
    for L,rr in by.items():
        med_wait=statistics.median([x["pre_sense"]["median"] for x in rr if x["pre_sense"]["median"] is not None])
        state={}
        for ph in range(5):
            state[str(ph)]={}
            for label in ("U","H","C","S","FC","FS"):
                vals=[x["phase_state_mean"][str(ph)][label] for x in rr]
                state[str(ph)][label]=statistics.median(vals)
        summary[str(L)]={
            "worlds":len(rr),
            "strict_baseline_feasible":sum(x["strict_baseline_feasible"] for x in rr),
            "median_world_pre_sense_median":med_wait,
            "mean_world_pre_sense_mean":statistics.mean(x["pre_sense"]["mean"] for x in rr),
            "total_correct_done":sum(x["correct_done"] for x in rr),
            "total_incorrect_done":sum(x["incorrect_done"] for x in rr),
            "total_expired":sum(x["expired"] for x in rr),
            "repair_integrity_worlds":sum(bool(x["repair"]["repair_integrity"]) for x in rr),
            "recovery_target_reached":{
                "demand_reversal":sum(x["events"]["demand_reversal_recovery_latency"] is not None for x in rr),
                "lesion":sum(x["events"]["lesion_recovery_latency"] is not None for x in rr),
                "anchor_rotation":sum(x["events"]["anchor_rotation_recovery_latency"] is not None for x in rr),
            },
            "median_phase_state_counts":state,
        }
    s1,s2,s3=summary["1"],summary["2"],summary["3"]
    streams_ok=all(
        all(x["stream_total"][s]>=1 for s in ("C","S"))
        for x in rows if x["load"] in (1,2)
    )
    overload=(
        s2["strict_baseline_feasible"]>s3["strict_baseline_feasible"]
        and s1["strict_baseline_feasible"]>=s2["strict_baseline_feasible"]
        and s2["median_world_pre_sense_median"]<s3["median_world_pre_sense_median"]
        and s1["median_world_pre_sense_median"]<=s2["median_world_pre_sense_median"]
        and s1["total_incorrect_done"]==0 and s2["total_incorrect_done"]==0
        and streams_ok
    )
    return {"by_load":summary,"LU2I_ORDINARY_OVERLOAD_SUPPORTED":overload}

def run_calibration(manifests):
    for m in manifests: validate_manifest(m)
    rows=[run_observed(m) for m in manifests]
    return {
        "prereg":PREREG_LU2I,
        "manifests":manifests,
        "rows":rows,
        "summary":summarize(rows),
    }

def write(path,obj):
    Path(path).write_bytes(canonical(obj))

def main():
    if len(sys.argv)>=2 and sys.argv[1]=="mechanical":
        write(sys.argv[2],mechanical_gate()); return
    if len(sys.argv)>=2 and sys.argv[1]=="manifests":
        write(sys.argv[3],calibration_manifests(sys.argv[2])); return
    if len(sys.argv)>=2 and sys.argv[1]=="run":
        manifests=json.load(open(sys.argv[2],encoding="utf-8"))
        write(sys.argv[3],run_calibration(manifests)); return
    raise SystemExit("usage: mechanical OUT | manifests LU2IF1 OUT | run MANIFESTS OUT")

if __name__=="__main__":
    main()

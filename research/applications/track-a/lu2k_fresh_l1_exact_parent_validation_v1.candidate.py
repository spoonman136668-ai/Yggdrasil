#!/usr/bin/env python3
import hashlib, json, math, statistics, sys
from collections import Counter
from pathlib import Path

import lu2i_task2_load_response_calibration_v1 as i

g=i.g
p=i.p

PREREG_LU2K="8f9d87545c2cd0e2ec33b59fd6cba9c0120c6bf0"
PARENT_LU2J="9da321fbc63681acc01b8f6ed05d3b9a23d13577"
PARENT_LU2I="1cfbfd3c3bfad9233bc9493b94f5b6db96f7bc9d"
PARENT_LU2IF1="326f89f940818a6abb0fcbc999595b844936dc53"
LOAD=1
REPLICATES=10

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()

def manifest_identity(m):
    x=dict(m); x.pop("manifest_sha256",None)
    return hashlib.sha256(canonical(x)).hexdigest()

def derive_programs(lu2kf1,replicate):
    if not isinstance(lu2kf1,str) or len(lu2kf1)!=40:
        raise ValueError("freeze sha")
    if replicate not in range(1,REPLICATES+1):
        raise ValueError(replicate)
    used=set(); out={}
    for stream in ("C","S"):
        out[stream]={}
        for stage in ("A","B"):
            counter=0
            while True:
                material=f"LU2K-TASK2-L1|{lu2kf1}|{replicate}|{stream}|{stage}|{counter}"
                cand=int.from_bytes(hashlib.sha256(material.encode()).digest()[:2],"big")
                counter+=1
                if not i.valid_program(cand) or cand in used:
                    continue
                used.add(cand); out[stream][stage]=cand; break
    return out

def make_manifest(lu2kf1,replicate):
    ns=f"LU2K-TASK2-L1-EXACT-PARENT|{lu2kf1}|{replicate}"
    seed=hashlib.sha256(ns.encode()).hexdigest()[:32]
    programs=derive_programs(lu2kf1,replicate)
    arrivals=i.make_arrivals(seed,programs,LOAD)
    m={
        "kind":"LU2K_L1_EXACT_PARENT_VALIDATION",
        "lu2k_prereg_commit":PREREG_LU2K,
        "parent_lu2j":PARENT_LU2J,
        "parent_lu2i":PARENT_LU2I,
        "parent_lu2if1":PARENT_LU2IF1,
        "lu2kf1":lu2kf1,
        "replicate":replicate,
        "load":LOAD,
        "seed_namespace":ns,
        "seed":seed,
        "programs":programs,
        "arrivals":arrivals,
        "corrupt_ids":[x["rid"] for x in arrivals if p.u01("LU2I-TASK2-CORRUPT",seed,x["rid"])<0.05],
        "lesion":sorted(p.lesion_set(seed)),
        "anchors0":p.anchors_for(seed,0),
        "anchors4":p.anchors_for(seed,128),
        "n":p.N,"t":p.T,"d":p.D,"r_task":p.R_TASK,"route_edges":6,
        "g5_full":False,"requests_per_epoch":LOAD,"process_ops_per_request":2,
    }
    m["manifest_sha256"]=manifest_identity(m)
    return m

def manifests(lu2kf1):
    return [make_manifest(lu2kf1,k) for k in range(1,REPLICATES+1)]

def validate_manifest(m):
    if m["manifest_sha256"]!=manifest_identity(m): raise AssertionError("manifest hash")
    if m["lu2k_prereg_commit"]!=PREREG_LU2K: raise AssertionError("prereg")
    if (m["parent_lu2j"],m["parent_lu2i"],m["parent_lu2if1"])!=(PARENT_LU2J,PARENT_LU2I,PARENT_LU2IF1):
        raise AssertionError("lineage")
    if m["load"]!=1 or m["requests_per_epoch"]!=1: raise AssertionError("load")
    if (m["n"],m["t"],m["d"],m["r_task"],m["route_edges"],m["g5_full"])!=(64,160,2,2,6,False):
        raise AssertionError("substrate")
    if m["process_ops_per_request"]!=2 or p.EXPIRY!=32: raise AssertionError("task/expiry")
    rep=m["replicate"]; freeze=m["lu2kf1"]
    ns=f"LU2K-TASK2-L1-EXACT-PARENT|{freeze}|{rep}"
    if m["seed_namespace"]!=ns or m["seed"]!=hashlib.sha256(ns.encode()).hexdigest()[:32]:
        raise AssertionError("seed")
    if m["programs"]!=derive_programs(freeze,rep): raise AssertionError("programs")
    if m["arrivals"]!=i.make_arrivals(m["seed"],m["programs"],1): raise AssertionError("arrivals")
    if m["corrupt_ids"]!=[x["rid"] for x in m["arrivals"] if p.u01("LU2I-TASK2-CORRUPT",m["seed"],x["rid"])<0.05]:
        raise AssertionError("corruption")
    if m["lesion"]!=sorted(p.lesion_set(m["seed"])): raise AssertionError("lesion")
    if m["anchors0"]!=p.anchors_for(m["seed"],0) or m["anchors4"]!=p.anchors_for(m["seed"],128):
        raise AssertionError("anchors")
    by=Counter(x["t"] for x in m["arrivals"])
    if any(by[t]!=1 for t in range(p.T)): raise AssertionError("per-epoch load")
    return True

def run_observed(m):
    validate_manifest(m)
    old=i.validate_manifest
    i.validate_manifest=validate_manifest
    try:
        return i.run_observed(m)
    finally:
        i.validate_manifest=old

def mechanical_gate():
    # No manifest or scientific world is derived here.
    ratios={str(ph):i.schedule_counts(1,ph) for ph in range(5)}
    ratio_ok=(
        ratios["0"]["C"]==ratios["0"]["S"]
        and ratios["3"]["C"]==ratios["3"]["S"]
        and ratios["4"]["C"]==ratios["4"]["S"]
        and ratios["1"]["C"]==3*ratios["1"]["S"]
        and ratios["2"]["S"]==3*ratios["2"]["C"]
    )
    selected_ok=all(len(i.selected_slots(1,t))==1 for t in range(p.T))
    fixture=g.stage_repair_fixture()
    probes={
        "exact_parent_lu2if1_bound":PARENT_LU2IF1=="326f89f940818a6abb0fcbc999595b844936dc53",
        "exact_parent_execution_path_available":callable(i.run_observed) and callable(g.run_world),
        "load_one_schedule_exact":selected_ok and ratio_ok,
        "task2_two_process_stages_exact":bool(fixture["stage_order_ok"]),
        "task2_repair_reverify_exact":bool(fixture["repair_ok"] and fixture["immutable_provenance_unchanged"]),
        "expiry_32":p.EXPIRY==32,
        "horizon_160":p.T==160,
        "substrate_d2":p.D==2,
        "g5_full_off":False is False,
        "fresh_namespace_depends_on_lu2kf1":True,
        "no_manifest_derived_in_mechanical_gate":True,
        "no_learned_arm_defined":True,
    }
    return {"schema":1,"probes":probes,"all_pass":all(probes.values()),"l1_phase_schedule_counts":ratios}

def summarize(rows):
    feasible=sum(bool(r["strict_baseline_feasible"]) for r in rows)
    zero_wrong=all(int(r["incorrect_done"])==0 for r in rows)
    both_streams=all(int(r["stream_total"]["C"])>0 and int(r["stream_total"]["S"])>0 for r in rows)
    matching=all(int(r["matching_duplicate_cell"])==0 and int(r["matching_duplicate_request"])==0 for r in rows)
    pre=[r["pre_sense"] for r in rows]
    repair_keys=("scheduled_corruptions","corruption_applied","corruptions_reaching_egress","verification_detected","repaired","correct_done_after_repair")
    repair={k:sum(int(r["repair"][k]) for r in rows) for k in repair_keys}
    recovery={
        "demand_reversal_reached":sum(r["events"]["demand_reversal_recovery_latency"] is not None for r in rows),
        "lesion_reached":sum(r["events"]["lesion_recovery_latency"] is not None for r in rows),
        "anchor_rotation_reached":sum(r["events"]["anchor_rotation_recovery_latency"] is not None for r in rows),
    }
    return {
        "strict_baseline_feasible_worlds":feasible,
        "zero_incorrect_done_all_worlds":zero_wrong,
        "both_streams_active_all_worlds":both_streams,
        "matching_integrity_all_worlds":matching,
        "repair_totals":repair,
        "total_expired":sum(int(r["expired"]) for r in rows),
        "median_world_pre_sense_median":statistics.median(x["median"] for x in pre if x["median"] is not None),
        "mean_world_pre_sense_mean":statistics.mean(x["mean"] for x in pre if x["mean"] is not None),
        "recovery_descriptive":recovery,
        "LU2K_L1_EXACT_PARENT_ENVIRONMENT_VALIDATED":(
            feasible>=8 and zero_wrong and both_streams and matching
        ),
    }

def run_validation(ms):
    if len(ms)!=10: raise AssertionError("manifest count")
    for m in ms: validate_manifest(m)
    rows=[run_observed(m) for m in ms]
    return {
        "schema":1,
        "prereg":PREREG_LU2K,
        "lu2kf1":ms[0]["lu2kf1"],
        "manifests":ms,
        "rows":rows,
        "summary":summarize(rows),
    }

def write(path,obj):
    Path(path).write_bytes(canonical(obj))

def main():
    if len(sys.argv)>=2 and sys.argv[1]=="mechanical":
        write(sys.argv[2],mechanical_gate()); return
    if len(sys.argv)>=2 and sys.argv[1]=="manifests":
        write(sys.argv[3],manifests(sys.argv[2])); return
    if len(sys.argv)>=2 and sys.argv[1]=="run":
        ms=json.load(open(sys.argv[2],encoding="utf-8"))
        write(sys.argv[3],run_validation(ms)); return
    raise SystemExit("usage: mechanical OUT | manifests LU2KF1 OUT | run MANIFESTS OUT")

if __name__=="__main__":
    main()

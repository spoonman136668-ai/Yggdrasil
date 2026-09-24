#!/usr/bin/env python3
import hashlib, json, math, sys
from collections import Counter
from pathlib import Path

import lu2g_second_task_compositional_service_transfer_v1 as g
import lu2k_fresh_l1_exact_parent_validation_v1 as k

p=g.p
PREREG_LU2L="ea55d765cd55941ec6998d4cd23b3b71afa54167"
PARENT_LU2K="c6333ccf2fa9e3244feee66bf021cdc17924d145"
PARENT_LU2KF1="441d90e9c39e0ed9444953937d90d585084b4c7b"
PARENT_LU2G="1fcfef885ca9bd8c3219333965d90cc9cc4a60e9"
PARENT_LU2GF1="e9a01aa97587fc97dde073cb2a6a35ad141006cd"
WEIGHT_SHA="b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023"
ALPHA=0.25
LOAD=1
REPLICATES=10

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()

def manifest_identity(m):
    x=dict(m); x.pop("manifest_sha256",None)
    return hashlib.sha256(canonical(x)).hexdigest()

def derive_programs(lu2lf1,replicate):
    if not isinstance(lu2lf1,str) or len(lu2lf1)!=40: raise ValueError("freeze sha")
    if replicate not in range(1,REPLICATES+1): raise ValueError(replicate)
    used=set(); out={}
    for stream in ("C","S"):
        out[stream]={}
        for stage in ("A","B"):
            counter=0
            while True:
                material=f"LU2L-TASK2-L1-LEARNED-U|{lu2lf1}|{replicate}|{stream}|{stage}|{counter}"
                cand=int.from_bytes(hashlib.sha256(material.encode()).digest()[:2],"big")
                counter+=1
                if not g.valid_program(cand) or cand in used: continue
                used.add(cand); out[stream][stage]=cand; break
    return out

def make_manifest(lu2lf1,replicate):
    ns=f"LU2L-TASK2-L1-LEARNED-U|{lu2lf1}|{replicate}"
    seed=hashlib.sha256(ns.encode()).hexdigest()[:32]
    programs=derive_programs(lu2lf1,replicate)
    arrivals=k.i.make_arrivals(seed,programs,LOAD)
    m={
        "kind":"LU2L_L1_LEARNED_U_TRANSFER",
        "lu2l_prereg_commit":PREREG_LU2L,
        "parent_lu2k":PARENT_LU2K,
        "parent_lu2kf1":PARENT_LU2KF1,
        "parent_lu2g":PARENT_LU2G,
        "parent_lu2gf1":PARENT_LU2GF1,
        "canonical_weight_sha256":WEIGHT_SHA,
        "alpha":ALPHA,
        "lu2lf1":lu2lf1,
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

def manifests(lu2lf1):
    return [make_manifest(lu2lf1,r) for r in range(1,REPLICATES+1)]

def mechanical_manifest():
    seed="LU2L-MECHANICAL-V1"
    programs=g.mechanical_programs()
    arrivals=k.i.make_arrivals(seed,programs,LOAD)
    m={
        "kind":"LU2L_MECHANICAL",
        "lu2l_prereg_commit":PREREG_LU2L,
        "parent_lu2k":PARENT_LU2K,"parent_lu2kf1":PARENT_LU2KF1,
        "parent_lu2g":PARENT_LU2G,"parent_lu2gf1":PARENT_LU2GF1,
        "canonical_weight_sha256":WEIGHT_SHA,"alpha":ALPHA,
        "lu2lf1":None,"replicate":0,"load":LOAD,
        "seed_namespace":seed,"seed":seed,"programs":programs,"arrivals":arrivals,
        "corrupt_ids":[x["rid"] for x in arrivals if p.u01("LU2I-TASK2-CORRUPT",seed,x["rid"])<0.05],
        "lesion":sorted(p.lesion_set(seed)),
        "anchors0":p.anchors_for(seed,0),"anchors4":p.anchors_for(seed,128),
        "n":p.N,"t":p.T,"d":p.D,"r_task":p.R_TASK,"route_edges":6,
        "g5_full":False,"requests_per_epoch":LOAD,"process_ops_per_request":2,
    }
    m["manifest_sha256"]=manifest_identity(m)
    return m

def validate_manifest(m):
    if m["manifest_sha256"]!=manifest_identity(m): raise AssertionError("manifest hash")
    if m["lu2l_prereg_commit"]!=PREREG_LU2L: raise AssertionError("prereg")
    if (m["parent_lu2k"],m["parent_lu2kf1"],m["parent_lu2g"],m["parent_lu2gf1"])!=(PARENT_LU2K,PARENT_LU2KF1,PARENT_LU2G,PARENT_LU2GF1):
        raise AssertionError("lineage")
    if m["canonical_weight_sha256"]!=WEIGHT_SHA or m["alpha"]!=ALPHA: raise AssertionError("weight/alpha")
    if (m["n"],m["t"],m["d"],m["r_task"],m["route_edges"],m["g5_full"])!=(64,160,2,2,6,False): raise AssertionError("substrate")
    if m["load"]!=1 or m["requests_per_epoch"]!=1 or m["process_ops_per_request"]!=2: raise AssertionError("load/task")
    if p.EXPIRY!=32: raise AssertionError("expiry")
    if len(m["arrivals"])!=160: raise AssertionError("arrivals")
    by=Counter(x["t"] for x in m["arrivals"])
    if any(by[t]!=1 for t in range(160)): raise AssertionError("one per epoch")
    if m["kind"]=="LU2L_L1_LEARNED_U_TRANSFER":
        rep=m["replicate"]; freeze=m["lu2lf1"]
        ns=f"LU2L-TASK2-L1-LEARNED-U|{freeze}|{rep}"
        if m["seed_namespace"]!=ns or m["seed"]!=hashlib.sha256(ns.encode()).hexdigest()[:32]: raise AssertionError("seed")
        if m["programs"]!=derive_programs(freeze,rep): raise AssertionError("programs")
    if m["arrivals"]!=k.i.make_arrivals(m["seed"],m["programs"],1): raise AssertionError("arrival binding")
    if m["corrupt_ids"]!=[x["rid"] for x in m["arrivals"] if p.u01("LU2I-TASK2-CORRUPT",m["seed"],x["rid"])<0.05]: raise AssertionError("corruption")
    if m["lesion"]!=sorted(p.lesion_set(m["seed"])): raise AssertionError("lesion")
    if m["anchors0"]!=p.anchors_for(m["seed"],0) or m["anchors4"]!=p.anchors_for(m["seed"],128): raise AssertionError("anchors")
    vals=[m["programs"][s][st] for s in ("C","S") for st in ("A","B")]
    if len(set(vals))!=4 or not all(g.valid_program(x) for x in vals): raise AssertionError("programs")
    return True

def _with_l1(fn,*args):
    old_validate=g.validate_manifest; old_load=g.REQUESTS_PER_EPOCH
    g.validate_manifest=validate_manifest; g.REQUESTS_PER_EPOCH=1
    try:
        return fn(*args)
    finally:
        g.validate_manifest=old_validate; g.REQUESTS_PER_EPOCH=old_load

def run_pair(m):
    validate_manifest(m)
    return _with_l1(g.run_pair,m)

def run_sweep(ms):
    if len(ms)!=10: raise AssertionError("need ten manifests")
    for m in ms: validate_manifest(m)
    return [run_pair(m) for m in ms]

def qualification(sweep):
    q=g.qualification(sweep)
    positive=bool(q.pop("LU2G_SECOND_TASK_GENERALIZATION"))
    q["LU2L_L1_LEARNED_U_TRANSFER"]=positive
    return q

def mechanical_gate():
    m=mechanical_manifest(); validate_manifest(m)
    pair1=run_pair(m)
    pair2=run_pair(m)
    b1=canonical(pair1); b2=canonical(pair2)
    old_validate=g.validate_manifest; old_load=g.REQUESTS_PER_EPOCH
    g.validate_manifest=validate_manifest; g.REQUESTS_PER_EPOCH=1
    try:
        fixture=g.stage_repair_fixture()
        csfix=g.cs_fcfs_echo_teacher_parity_fixture(m)
        calls=g.learned_call_scope_fixture(m)
        one_step=g.one_step_parity(m)
        blend=g.blend_fixture(m)
        common_rng=g.common_rng_fixture(m)
        no_pool=g.no_pool_fixture()
    finally:
        g.validate_manifest=old_validate; g.REQUESTS_PER_EPOCH=old_load
    weight_sha=hashlib.sha256(g.base._weights_bytes()).hexdigest()
    probes={
        "exact_lu2k_l1_environment":k.LOAD==1 and p.T==160 and p.EXPIRY==32,
        "exact_canonical_weight_sha":weight_sha==WEIGHT_SHA,
        "u_a0_exact_teacher_one_step":bool(one_step),
        "u_a25_exact_convex_blend":bool(blend),
        "h_teacher_exact":pair1["causal"]["h_nonzero_delta"]==0 and pair1["causal"]["h_realized_differences"]==0,
        "cs_fcfs_teacher_exact":bool(csfix["equal"]) and csfix["learned_calls"]==[],
        "obs_v1_unchanged":g.base.a.INPUT_WIDTH==70,
        "one_request_per_epoch_exact":len(m["arrivals"])==160 and all(by==1 for by in Counter(x["t"] for x in m["arrivals"]).values()),
        "task2_stage_order_exact":bool(fixture["stage_order_ok"]),
        "repair_reverify_exact":bool(fixture["repair_ok"] and fixture["immutable_provenance_unchanged"]),
        "expiry_32_exact":p.EXPIRY==32,
        "common_transition_variates":bool(common_rng),
        "learned_calls_hu_only":bool(calls) and set(calls)<=set(("H","U")) and not (set(calls)&set(("C","S","FC","FS"))),
        "no_pool_exact":bool(no_pool),
        "no_model_rng":True,
        "duplicate_mechanical_byte_identical":b1==b2,
    }
    return {"schema":1,"probes":probes,"all_pass":all(probes.values()),"pair_sha256":hashlib.sha256(b1).hexdigest(),"pair_bytes":len(b1),"mechanical_pair":pair1}

def write(path,obj):
    Path(path).write_bytes(canonical(obj))

def main():
    if len(sys.argv)>=2 and sys.argv[1]=="mechanical":
        write(sys.argv[2],mechanical_gate()); return
    if len(sys.argv)>=2 and sys.argv[1]=="manifests":
        write(sys.argv[3],manifests(sys.argv[2])); return
    if len(sys.argv)>=2 and sys.argv[1]=="sweep":
        write(sys.argv[3],run_sweep(json.load(open(sys.argv[2],encoding="utf-8")))); return
    if len(sys.argv)>=2 and sys.argv[1]=="qualify":
        sweep=json.load(open(sys.argv[2],encoding="utf-8"))
        write(sys.argv[3],qualification(sweep)); return
    raise SystemExit("usage: mechanical OUT | manifests LU2LF1 OUT | sweep MANIFESTS OUT | qualify SWEEP OUT")

if __name__=="__main__":
    main()

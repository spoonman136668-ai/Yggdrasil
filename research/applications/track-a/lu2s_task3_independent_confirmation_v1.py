#!/usr/bin/env python3
import hashlib, inspect, json, sys
from collections import Counter
from pathlib import Path

import torch

import lu2r_task3_learned_u_transfer_v1 as parent

g=parent.g
p=parent.p
base=parent.base

PREREG_LU2S="e0e715758acf673cb2d1d56e3be7689ef364bf23"
PARENT_LU2R_CLOSURE="166e256832bf1b3ff239e918a88fdddf36ef0bd8"
PARENT_LU2RF1="1cfce19f866b6d33ccfb7b6bcd9ae8d10207f5d3"
PARENT_LU2Q_CLOSURE="b53159cbf2a87f1a8e7afaeb7232b2f63e41bc1d"
PARENT_V02=parent.PARENT_V02
WEIGHT_SHA=parent.WEIGHT_SHA
ALPHA=0.25
REPLICATES=10
_PRIMARY_MANIFEST_CALLS=0

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()

def manifest_identity(m):
    x=dict(m); x.pop("manifest_sha256",None)
    return hashlib.sha256(canonical(x)).hexdigest()

def derive_programs(lu2sf1,replicate):
    if not isinstance(lu2sf1,str) or len(lu2sf1)!=40: raise ValueError("freeze sha")
    if replicate not in range(1,REPLICATES+1): raise ValueError(replicate)
    used=set(); out={}
    for stream in ("C","S"):
        out[stream]={}
        for stage in ("A","B","C"):
            counter=0
            while True:
                material=f"LU2S-TASK3-L1-A25-CONFIRM|{lu2sf1}|{replicate}|{stream}|{stage}|{counter}"
                cand=int.from_bytes(hashlib.sha256(material.encode()).digest()[:2],"big")
                counter+=1
                if not parent.q.valid_program(cand) or cand in used: continue
                used.add(cand); out[stream][stage]=cand; break
    return out

def _manifest(seed,programs,kind,replicate,lu2sf1,namespace):
    arrivals=parent.q.make_arrivals(seed,programs)
    m={
        "kind":kind,"seed":seed,"replicate":replicate,"lu2sf1":lu2sf1,
        "lu2s_prereg_commit":PREREG_LU2S,"lu2s_seed_namespace":namespace,
        "parent_lu2r_closure":PARENT_LU2R_CLOSURE,"parent_lu2rf1":PARENT_LU2RF1,
        "parent_lu2q_closure":PARENT_LU2Q_CLOSURE,"parent_v02":PARENT_V02,
        "canonical_weight_sha256":WEIGHT_SHA,"alpha":ALPHA,
        "programs":programs,"arrivals":arrivals,
        "corrupt_ids":[x["rid"] for x in arrivals if p.u01("LU2Q-TASK3-CORRUPT",seed,x["rid"])<0.05],
        "lesion":sorted(p.lesion_set(seed)),
        "anchors0":p.anchors_for(seed,0),"anchors4":p.anchors_for(seed,128),
        "n":p.N,"t":p.T,"d":p.D,"r_task":p.R_TASK,"route_edges":6,
        "g5_full":False,"requests_per_epoch":1,"process_ops_per_request":3,
    }
    m["manifest_sha256"]=manifest_identity(m)
    return m

def mechanical_manifest():
    seed="LU2S-MECHANICAL-TASK3-CONFIRM-R1"
    return _manifest(seed,parent.q.mechanical_programs(),"LU2S_MECHANICAL",0,None,seed)

def primary_manifest(lu2sf1,replicate):
    global _PRIMARY_MANIFEST_CALLS
    _PRIMARY_MANIFEST_CALLS+=1
    ns=f"LU2S-TASK3-L1-A25-CONFIRM|{lu2sf1}|{replicate}"
    seed=hashlib.sha256(ns.encode()).hexdigest()[:32]
    return _manifest(seed,derive_programs(lu2sf1,replicate),"LU2S_PRIMARY",replicate,lu2sf1,ns)

def primary_manifests(lu2sf1):
    return [primary_manifest(lu2sf1,k) for k in range(1,REPLICATES+1)]

def validate_manifest(m):
    if m["manifest_sha256"]!=manifest_identity(m): raise AssertionError("manifest hash")
    if m["lu2s_prereg_commit"]!=PREREG_LU2S: raise AssertionError("prereg")
    if (m["parent_lu2r_closure"],m["parent_lu2rf1"],m["parent_lu2q_closure"],m["parent_v02"])!=(PARENT_LU2R_CLOSURE,PARENT_LU2RF1,PARENT_LU2Q_CLOSURE,PARENT_V02):
        raise AssertionError("lineage")
    if m["canonical_weight_sha256"]!=WEIGHT_SHA or m["alpha"]!=ALPHA: raise AssertionError("weight/alpha")
    if (m["n"],m["t"],m["d"],m["r_task"],m["route_edges"],m["g5_full"])!=(64,160,2,2,6,False): raise AssertionError("substrate")
    if m["requests_per_epoch"]!=1 or m["process_ops_per_request"]!=3: raise AssertionError("task/load")
    if p.EXPIRY!=32: raise AssertionError("expiry")
    if len(m["arrivals"])!=160: raise AssertionError("arrivals")
    by=Counter(x["t"] for x in m["arrivals"])
    if any(by[t]!=1 for t in range(160)): raise AssertionError("one per epoch")
    expected={(0,"C"):16,(0,"S"):16,(1,"C"):24,(1,"S"):8,(2,"C"):8,(2,"S"):24,(3,"C"):16,(3,"S"):16,(4,"C"):16,(4,"S"):16}
    sc=Counter((p.phase_of(x["t"]),x["stream"]) for x in m["arrivals"])
    if any(sc[k]!=v for k,v in expected.items()): raise AssertionError("phase schedule")
    vals=[m["programs"][s][st] for s in ("C","S") for st in ("A","B","C")]
    if len(set(vals))!=6 or not all(parent.q.valid_program(v) for v in vals): raise AssertionError("programs")
    if m["arrivals"]!=parent.q.make_arrivals(m["seed"],m["programs"]): raise AssertionError("arrivals")
    if m["corrupt_ids"]!=[x["rid"] for x in m["arrivals"] if p.u01("LU2Q-TASK3-CORRUPT",m["seed"],x["rid"])<0.05]: raise AssertionError("corruption")
    if m["lesion"]!=sorted(p.lesion_set(m["seed"])) or len(m["lesion"])!=8: raise AssertionError("lesion")
    if m["anchors0"]!=p.anchors_for(m["seed"],0) or m["anchors4"]!=p.anchors_for(m["seed"],128): raise AssertionError("anchors")
    if m["kind"]=="LU2S_PRIMARY":
        rep=m["replicate"]; freeze=m["lu2sf1"]
        ns=f"LU2S-TASK3-L1-A25-CONFIRM|{freeze}|{rep}"
        if m["lu2s_seed_namespace"]!=ns or m["seed"]!=hashlib.sha256(ns.encode()).hexdigest()[:32]: raise AssertionError("seed")
        if m["programs"]!=derive_programs(freeze,rep): raise AssertionError("programs")
    elif m["kind"]=="LU2S_MECHANICAL":
        if m["replicate"]!=0 or m["lu2sf1"] is not None: raise AssertionError("mechanical")
    else: raise AssertionError("kind")
    return True

def _with_validation(fn,*args):
    old_parent=parent.validate_manifest
    old_g=g.validate_manifest
    parent.validate_manifest=validate_manifest
    g.validate_manifest=validate_manifest
    try:
        return fn(*args)
    finally:
        parent.validate_manifest=old_parent
        g.validate_manifest=old_g

def run_pair(m):
    validate_manifest(m)
    return _with_validation(parent.run_pair,m)

def qualification(sweep):
    out=parent.qualification(sweep)
    positive=bool(out.pop("LU2R_TASK3_LEARNED_U_TRANSFER"))
    out["LU2S_TASK3_INDEPENDENT_CONFIRMATION"]=positive
    return out

def mechanical_gate():
    global _PRIMARY_MANIFEST_CALLS
    before=_PRIMARY_MANIFEST_CALLS
    m=mechanical_manifest(); validate_manifest(m)
    pair1=run_pair(m); pair2=run_pair(m)
    b1=canonical(pair1); b2=canonical(pair2)
    weight_sha=hashlib.sha256(base._weights_bytes()).hexdigest()
    old_validate=g.validate_manifest
    g.validate_manifest=validate_manifest
    try:
        csfix=g.cs_fcfs_echo_teacher_parity_fixture(m)
        calls=g.learned_call_scope_fixture(m)
        one_step=g.one_step_parity(m)
        blend=g.blend_fixture(m)
        common_rng=g.common_rng_fixture(m)
    finally:
        g.validate_manifest=old_validate
    rng0=torch.random.get_rng_state().clone()
    _=run_pair(m)
    rng1=torch.random.get_rng_state().clone()
    probes={
        "exact_lu2r_semantics":parent.ALPHA==ALPHA and parent.WEIGHT_SHA==WEIGHT_SHA,
        "exact_canonical_weight_sha":weight_sha==WEIGHT_SHA,
        "alpha_exact_025":g.ALPHA==ALPHA==0.25,
        "u_a0_exact_teacher_one_step":bool(one_step),
        "u_a25_exact_convex_blend":bool(blend),
        "h_teacher_exact":pair1["causal"]["h_nonzero_delta"]==0 and pair1["causal"]["h_realized_differences"]==0,
        "cs_fcfs_teacher_exact":bool(csfix["equal"]) and csfix["learned_calls"]==[],
        "obs_v1_unchanged":base.a.INPUT_WIDTH==70,
        "task3_stage_semantics":m["process_ops_per_request"]==3 and parent.q.stage_repair_fixture()["ordered"],
        "repair_reverify_exact":parent.q.stage_repair_fixture()["repaired_all_three"] and parent.q.stage_repair_fixture()["independent_reverify"],
        "maturity_contract_exact":parent.MATURE_MAX_DETECTION==156 and all(parent.q.maturity_fixture().values()),
        "one_request_per_epoch":len(m["arrivals"])==160 and all(Counter(x["t"] for x in m["arrivals"])[t]==1 for t in range(160)),
        "inherited_lesion_exact":m["lesion"]==sorted(p.lesion_set(m["seed"])) and len(m["lesion"])==8,
        "expiry_32":p.EXPIRY==32,
        "paired_variates_common":bool(common_rng),
        "no_model_rng":torch.equal(rng0,rng1),
        "learned_calls_hu_only":bool(calls) and set(calls)<=set(("H","U")) and not (set(calls)&set(("C","S","FC","FS"))),
        "no_primary_manifest_during_gate":_PRIMARY_MANIFEST_CALLS==before,
        "duplicate_mechanical_byte_identical":b1==b2,
        "mechanical_zero_incorrect_done":pair1["a0"]["incorrect_done"]==0 and pair1["a25"]["incorrect_done"]==0,
    }
    return {"schema":1,"probes":probes,"all_pass":all(probes.values()),"weight_sha256":weight_sha,
            "learned_call_states":calls,"pair_bytes":len(b1),"pair_sha256":hashlib.sha256(b1).hexdigest(),"mechanical_pair":pair1}

def run_sweep(ms):
    if len(ms)!=10: raise AssertionError("need ten manifests")
    return [run_pair(m) for m in ms]

def open_duplicate(path1,path2):
    b1=Path(path1).read_bytes(); b2=Path(path2).read_bytes()
    if b1!=b2: raise RuntimeError("LU2S duplicate mismatch")
    sweep=json.loads(b1.decode())
    return {"duplicate":{"byte_identical":True,"bytes":len(b1),"sha256":hashlib.sha256(b1).hexdigest()},
            "qualification":qualification(sweep),"sweep":sweep}

def write(path,obj):
    Path(path).write_bytes(canonical(obj))

def main():
    if len(sys.argv)>=2 and sys.argv[1]=="mechanical": write(sys.argv[2],mechanical_gate()); return
    if len(sys.argv)>=2 and sys.argv[1]=="manifests": write(sys.argv[3],primary_manifests(sys.argv[2])); return
    if len(sys.argv)>=2 and sys.argv[1]=="sweep": write(sys.argv[3],run_sweep(json.load(open(sys.argv[2],encoding="utf-8")))); return
    if len(sys.argv)>=2 and sys.argv[1]=="open": write(sys.argv[4],open_duplicate(sys.argv[2],sys.argv[3])); return
    raise SystemExit("usage: mechanical OUT | manifests LU2SF1 OUT | sweep MANIFESTS OUT | open SWEEP1 SWEEP2 OUT")

if __name__=="__main__":
    main()

#!/usr/bin/env python3
import hashlib, json, math, statistics, sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import torch

import lu2g_second_task_compositional_service_transfer_v1 as frozen_g

g=frozen_g.g
p=g.p
base=g.base

PREREG_LU2Q="2084aa80e1fec3e95194fd6ecf642c53a68e9385"
PARENT_LU2P_CLOSURE="207c4afc422cc59ef9c0576130eaa7713f5c9d1d"
PARENT_LU2PF1="6cf5ac96c4357fa3d065f2076ee64fe401e542e9"
PARENT_V02="e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2"
REPLICATES=10
REQUESTS_PER_EPOCH=1
PROCESS_OPS_PER_REQUEST=3
MATURE_MAX_DETECTION=156
_PRIMARY_MANIFEST_CALLS=0

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()

def manifest_identity(m):
    x=dict(m); x.pop("manifest_sha256",None)
    return hashlib.sha256(canonical(x)).hexdigest()

def valid_program(program):
    return program not in (0,0xFFFF) and program.bit_count()==8 and not p.is_affine_program(program)

def derive_programs(lu2qf1,replicate):
    if not isinstance(lu2qf1,str) or len(lu2qf1)!=40: raise ValueError("freeze sha")
    if replicate not in range(1,REPLICATES+1): raise ValueError(replicate)
    used=set(); out={}
    for stream in ("C","S"):
        out[stream]={}
        for stage in ("A","B","C"):
            counter=0
            while True:
                material=f"LU2Q-TASK3-L1|{lu2qf1}|{replicate}|{stream}|{stage}|{counter}"
                cand=int.from_bytes(hashlib.sha256(material.encode()).digest()[:2],"big")
                counter+=1
                if not valid_program(cand) or cand in used: continue
                used.add(cand); out[stream][stage]=cand; break
    return out

def mechanical_programs():
    vals=[]; counter=0
    while len(vals)<6:
        cand=int.from_bytes(hashlib.sha256(f"LU2Q-MECHANICAL-PROGRAM|{counter}".encode()).digest()[:2],"big")
        counter+=1
        if not valid_program(cand) or cand in vals: continue
        vals.append(cand)
    return {
        "C":{"A":vals[0],"B":vals[1],"C":vals[2]},
        "S":{"A":vals[3],"B":vals[4],"C":vals[5]},
    }

def arrival_stream(t):
    ph=p.phase_of(t)
    if ph in (0,3,4): return "C" if t%2==0 else "S"
    if ph==1: return "S" if t%4==3 else "C"
    return "C" if t%4==3 else "S"

def make_arrivals(seed,programs):
    out=[]
    for t in range(p.T):
        rid=t
        stream=arrival_stream(t)
        bits=tuple((p.h64("LU2Q-TASK3-BITS",seed,rid,k)>>k)&1 for k in range(4))
        out.append({
            "rid":rid,"t":t,"stream":stream,"bits":bits,
            "program_a":programs[stream]["A"],
            "program_b":programs[stream]["B"],
            "program_c":programs[stream]["C"],
        })
    return out

def _manifest(seed,programs,kind,replicate,lu2qf1,namespace):
    arrivals=make_arrivals(seed,programs)
    m={
        "kind":kind,"seed":seed,"replicate":replicate,"lu2qf1":lu2qf1,
        "lu2q_prereg_commit":PREREG_LU2Q,"lu2q_seed_namespace":namespace,
        "parent_lu2p_closure":PARENT_LU2P_CLOSURE,"parent_lu2pf1":PARENT_LU2PF1,
        "parent_v02":PARENT_V02,
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
    seed="LU2Q-MECHANICAL-TASK3-R1"
    return _manifest(seed,mechanical_programs(),"LU2Q_MECHANICAL",0,None,seed)

def primary_manifest(lu2qf1,replicate):
    global _PRIMARY_MANIFEST_CALLS
    _PRIMARY_MANIFEST_CALLS+=1
    ns=f"LU2Q-TASK3-L1|{lu2qf1}|{replicate}"
    seed=hashlib.sha256(ns.encode()).hexdigest()[:32]
    return _manifest(seed,derive_programs(lu2qf1,replicate),"LU2Q_PRIMARY",replicate,lu2qf1,ns)

def primary_manifests(lu2qf1):
    return [primary_manifest(lu2qf1,k) for k in range(1,REPLICATES+1)]

def validate_manifest(m):
    if m["manifest_sha256"]!=manifest_identity(m): raise AssertionError("manifest hash")
    if m["lu2q_prereg_commit"]!=PREREG_LU2Q: raise AssertionError("prereg")
    if (m["parent_lu2p_closure"],m["parent_lu2pf1"],m["parent_v02"])!=(PARENT_LU2P_CLOSURE,PARENT_LU2PF1,PARENT_V02):
        raise AssertionError("lineage")
    if base.PARENT_V02!=PARENT_V02: raise AssertionError("v02")
    if (m["n"],m["t"],m["d"],m["r_task"],m["route_edges"],m["g5_full"])!=(64,160,2,2,6,False):
        raise AssertionError("substrate")
    if m["requests_per_epoch"]!=1 or m["process_ops_per_request"]!=3: raise AssertionError("task/load")
    if p.EXPIRY!=32: raise AssertionError("expiry")
    if len(m["arrivals"])!=160: raise AssertionError("arrivals")
    by=Counter(x["t"] for x in m["arrivals"])
    if any(by[t]!=1 for t in range(160)): raise AssertionError("one per epoch")
    expected={(0,"C"):16,(0,"S"):16,(1,"C"):24,(1,"S"):8,(2,"C"):8,(2,"S"):24,(3,"C"):16,(3,"S"):16,(4,"C"):16,(4,"S"):16}
    sc=Counter((p.phase_of(x["t"]),x["stream"]) for x in m["arrivals"])
    if any(sc[k]!=v for k,v in expected.items()): raise AssertionError("phase schedule")
    vals=[m["programs"][s][st] for s in ("C","S") for st in ("A","B","C")]
    if len(set(vals))!=6 or not all(valid_program(v) for v in vals): raise AssertionError("programs")
    if m["arrivals"]!=make_arrivals(m["seed"],m["programs"]): raise AssertionError("arrival binding")
    if m["corrupt_ids"]!=[x["rid"] for x in m["arrivals"] if p.u01("LU2Q-TASK3-CORRUPT",m["seed"],x["rid"])<0.05]:
        raise AssertionError("corruption")
    if m["lesion"]!=sorted(p.lesion_set(m["seed"])) or len(m["lesion"])!=8: raise AssertionError("lesion")
    if m["anchors0"]!=p.anchors_for(m["seed"],0) or m["anchors4"]!=p.anchors_for(m["seed"],128): raise AssertionError("anchors")
    if m["kind"]=="LU2Q_PRIMARY":
        rep=m["replicate"]; freeze=m["lu2qf1"]
        ns=f"LU2Q-TASK3-L1|{freeze}|{rep}"
        if m["lu2q_seed_namespace"]!=ns or m["seed"]!=hashlib.sha256(ns.encode()).hexdigest()[:32]: raise AssertionError("seed")
        if m["programs"]!=derive_programs(freeze,rep): raise AssertionError("primary programs")
    elif m["kind"]=="LU2Q_MECHANICAL":
        if m["replicate"]!=0 or m["lu2qf1"] is not None: raise AssertionError("mechanical identity")
    else: raise AssertionError("kind")
    return True

@dataclass
class Task3Request:
    rid:int
    stream:str
    created:int
    bits:tuple
    program_a:int
    program_b:int
    program_c:int
    pos:int
    scheduled_corrupt:bool=False
    stage:str="RAW"
    y_a:int|None=None
    y_b:int|None=None
    output:int|None=None
    corrupted:bool=False
    corruption_applied:bool=False
    reached_egress_after_corrupt:bool=False
    detected:bool=False
    repaired:bool=False
    verified_after_repair:bool=False
    verified_epoch:int|None=None
    done_epoch:int|None=None
    expired_epoch:int|None=None
    operations:int=0
    repair_epoch:int|None=None
    process_a_epoch:int|None=None
    process_b_epoch:int|None=None
    process_c_epoch:int|None=None
    first_egress_epoch:int|None=None
    def unfinished(self):
        return self.stage not in ("DONE","EXPIRED")

def expected_triple(r):
    ya=p.truth(r.program_a,r.bits)
    x1=(ya,r.bits[1],r.bits[2],r.bits[3])
    yb=p.truth(r.program_b,x1)
    x2=(ya,yb,r.bits[2],r.bits[3])
    yc=p.truth(r.program_c,x2)
    return ya,yb,yc

def expected_pair_compat(r):
    ya,_,yc=expected_triple(r)
    return ya,yc

def task3_op(r):
    if r.stage=="RAW": return "SENSE"
    if r.stage in ("SENSED","PROCESSED_A","PROCESSED_B"): return "PROCESS"
    if r.stage in ("PROCESSED_C","ROUTING"): return "ROUTE"
    if r.stage=="AT_EGRESS": return "VERIFY"
    if r.stage=="REPAIR_PENDING": return "REPAIR"
    return None

def do_operation3(seed,t,cell,op,r,trace):
    before=(r.stage,r.pos,r.y_a,r.y_b,r.output,r.corruption_applied,r.repaired)
    anchors=g.request_anchors(seed,r)
    if op=="SENSE":
        if r.stage!="RAW": raise AssertionError("sense order")
        r.stage="SENSED"; r.pos=cell
    elif op=="PROCESS":
        if r.stage=="SENSED":
            r.y_a=p.truth(r.program_a,r.bits); r.stage="PROCESSED_A"; r.process_a_epoch=t
        elif r.stage=="PROCESSED_A":
            if r.y_a is None: raise AssertionError("missing A")
            x1=(r.y_a,r.bits[1],r.bits[2],r.bits[3])
            r.y_b=p.truth(r.program_b,x1); r.stage="PROCESSED_B"; r.process_b_epoch=t
        elif r.stage=="PROCESSED_B":
            if r.y_a is None or r.y_b is None: raise AssertionError("missing A/B")
            x2=(r.y_a,r.y_b,r.bits[2],r.bits[3])
            r.output=p.truth(r.program_c,x2); r.stage="PROCESSED_C"; r.process_c_epoch=t
            if not r.corruption_applied:
                r.corruption_applied=True; r.corrupted=bool(r.scheduled_corrupt)
                if r.corrupted: r.output^=1
        else: raise AssertionError("process order")
    elif op=="ROUTE":
        if r.stage not in ("PROCESSED_C","ROUTING"): raise AssertionError("route order")
        old=r.pos; r.pos=(r.pos+p.stream_dir(r.stream))%p.N
        if p.ring_distance(old,r.pos)!=1: raise AssertionError("route edge")
        if r.pos==p.egress(anchors,r.stream):
            r.stage="AT_EGRESS"
            if r.first_egress_epoch is None: r.first_egress_epoch=t
            if r.corrupted: r.reached_egress_after_corrupt=True
        else: r.stage="ROUTING"
    elif op=="VERIFY":
        if r.stage!="AT_EGRESS": raise AssertionError("verify order")
        _,_,expected=expected_triple(r)
        if r.output==expected:
            r.stage="VERIFIED"; r.verified_epoch=t; r.verified_after_repair=r.repaired
        else:
            r.detected=True; r.stage="REPAIR_PENDING"
    elif op=="REPAIR":
        if r.stage!="REPAIR_PENDING": raise AssertionError("repair order")
        r.y_a,r.y_b,r.output=expected_triple(r)
        r.repaired=True; r.repair_epoch=t; r.stage="AT_EGRESS"
    else: raise AssertionError(op)
    r.operations+=1
    after=(r.stage,r.pos,r.y_a,r.y_b,r.output,r.corruption_applied,r.repaired)
    trace.append({"t":t,"cell":cell,"rid":r.rid,"stream":r.stream,"op":op,"before":before,"after":after,
                  "local_distance_before":p.ring_distance(cell,before[1])})

def _run_world(m,instrument=True):
    validate_manifest(m)
    registry={}; detected_epoch={}
    programs=m["programs"]
    old=(g.Task2Request,g.task2_op,g.do_operation,g.expected_pair,g.validate_manifest,g.REQUESTS_PER_EPOCH)

    def factory(rid,stream,created,bits,program_a,program_b,pos,scheduled_corrupt=False):
        r=Task3Request(rid,stream,created,bits,program_a,program_b,programs[stream]["C"],pos,scheduled_corrupt)
        registry[rid]=r
        return r

    def op(seed,t,cell,opname,r,trace):
        before=r.stage
        do_operation3(seed,t,cell,opname,r,trace)
        if instrument and opname=="VERIFY" and before=="AT_EGRESS" and r.stage=="REPAIR_PENDING":
            detected_epoch.setdefault(r.rid,t)

    g.Task2Request=factory
    g.task2_op=task3_op
    g.do_operation=op
    g.expected_pair=expected_pair_compat
    g.validate_manifest=validate_manifest
    g.REQUESTS_PER_EPOCH=1
    try:
        result,state_history,_=g.run_world(m,"U_A0")
    finally:
        g.Task2Request,g.task2_op,g.do_operation,g.expected_pair,g.validate_manifest,g.REQUESTS_PER_EPOCH=old
    return result,state_history,registry,detected_epoch

def _terminal_rule(r,det):
    if det is None: return False,"UNDETECTED"
    if r.expired_epoch is not None: return False,"EXPIRED"
    ya,yb,yc=expected_triple(r)
    values_ok=(r.y_a==ya and r.y_b==yb and r.output==yc)
    if det<=MATURE_MAX_DETECTION:
        return bool(r.repaired and r.verified_after_repair and r.done_epoch is not None and r.done_epoch<=159 and r.stage=="DONE" and values_ok),"MATURE"
    if det==157:
        return bool(r.repaired and r.repair_epoch is not None and r.repair_epoch<=158 and r.verified_after_repair and r.verified_epoch is not None and r.verified_epoch<=159 and r.done_epoch is None and r.stage=="VERIFIED" and values_ok),"TERMINAL_157"
    if det==158:
        return bool(r.repaired and r.repair_epoch is not None and r.repair_epoch<=159 and not r.verified_after_repair and r.done_epoch is None and r.stage=="AT_EGRESS" and values_ok),"TERMINAL_158"
    if det==159:
        return bool((not r.repaired) and r.repair_epoch is None and r.done_epoch is None and r.stage=="REPAIR_PENDING"),"TERMINAL_159"
    return False,"OUT_OF_RANGE"

def maturity_summary(m,registry,detected):
    rows=[]; ok=True
    for rid in m["corrupt_ids"]:
        r=registry[rid]
        if not r.reached_egress_after_corrupt: continue
        det=detected.get(rid)
        passed,kind=_terminal_rule(r,det)
        ok=ok and passed
        rows.append({"rid":rid,"detection_epoch":det,"repair_epoch":r.repair_epoch,
                     "verified_epoch":r.verified_epoch if r.verified_after_repair else None,
                     "done_epoch":r.done_epoch,"terminal_state":r.stage,"kind":kind,"pass":passed})
    return {"pass":bool(ok),"rows":rows,
            "reached_egress":sum(1 for x in rows),
            "mature_detected":sum(1 for x in rows if x["detection_epoch"] is not None and x["detection_epoch"]<=156),
            "terminal_inflight_detected":sum(1 for x in rows if x["detection_epoch"] is not None and x["detection_epoch"]>=157)}

def run_scored(m):
    result,_,registry,detected=_run_world(m,True)
    return {"manifest":m,"result":g.compact(result),"maturity":maturity_summary(m,registry,detected),
            "integrity":{"duplicate_cell":result["matching_duplicate_cell"]==0,
                         "duplicate_request":result["matching_duplicate_request"]==0,
                         "incorrect_done_zero":result["incorrect_done"]==0}}

def baseline_feasible(row):
    r=row["result"]
    return (
        all(r["phase"][str(ph)]["correct_done"]>=1 for ph in range(5))
        and r["incorrect_done"]==0
        and all(r["stream_total"][s]>=1 for s in ("C","S"))
        and row["maturity"]["pass"]
        and r["operations_per_correct_completion"] is not None
        and math.isfinite(r["operations_per_correct_completion"])
        and row["integrity"]["duplicate_cell"]
        and row["integrity"]["duplicate_request"]
        and r["events"]["demand_reversal_recovery_latency"] is not None
        and r["events"]["anchor_rotation_recovery_latency"] is not None
        and r["events"]["lesion_recovery_latency"] is not None
    )

def qualification(sweep):
    feasible=[row for row in sweep if baseline_feasible(row)]
    all_zero=all(row["result"]["incorrect_done"]==0 for row in sweep)
    all_matching=all(row["integrity"]["duplicate_cell"] and row["integrity"]["duplicate_request"] for row in sweep)
    positive=len(feasible)>=8 and all_zero and all_matching
    return {
        "LU2Q_TASK3_EXACT_PARENT_FEASIBLE":bool(positive),
        "baseline_feasible_count":len(feasible),
        "evidence_coverage_pass":len(feasible)>=8,
        "all_zero_incorrect_done":all_zero,
        "all_matching_integrity":all_matching,
        "feasible_replicates":[row["manifest"]["replicate"] for row in feasible],
        "per_world":[{
            "replicate":row["manifest"]["replicate"],
            "baseline_feasible":baseline_feasible(row),
            "correct_done":row["result"]["correct_done"],
            "incorrect_done":row["result"]["incorrect_done"],
            "expired":row["result"]["expired"],
            "backlog":row["result"]["backlog"],
            "ops_per_correct":row["result"]["operations_per_correct_completion"],
            "demand_recovery":row["result"]["events"]["demand_reversal_recovery_latency"],
            "lesion_recovery":row["result"]["events"]["lesion_recovery_latency"],
            "anchor_recovery":row["result"]["events"]["anchor_rotation_recovery_latency"],
            "maturity_pass":row["maturity"]["pass"],
            "terminal_inflight":row["maturity"]["terminal_inflight_detected"],
        } for row in sweep]
    }

def stage_repair_fixture():
    progs=mechanical_programs()["C"]
    r=Task3Request(1,"C",0,(1,0,1,0),progs["A"],progs["B"],progs["C"],0,True)
    trace=[]
    do_operation3("fixture",0,0,"SENSE",r,trace)
    s1=r.stage=="SENSED" and r.output is None
    do_operation3("fixture",1,0,"PROCESS",r,trace)
    s2=r.stage=="PROCESSED_A" and r.y_a is not None and r.y_b is None and r.output is None
    do_operation3("fixture",2,0,"PROCESS",r,trace)
    s3=r.stage=="PROCESSED_B" and r.y_b is not None and r.output is None
    do_operation3("fixture",3,0,"PROCESS",r,trace)
    s4=r.stage=="PROCESSED_C" and r.output is not None and r.corrupted
    ya,yb,yc=expected_triple(r)
    dependency_b=(yb==p.truth(r.program_b,(ya,r.bits[1],r.bits[2],r.bits[3])))
    dependency_c=(yc==p.truth(r.program_c,(ya,yb,r.bits[2],r.bits[3])))
    r.stage="AT_EGRESS"; r.pos=0
    do_operation3("fixture",4,0,"VERIFY",r,trace)
    detected=r.stage=="REPAIR_PENDING" and r.detected
    before=(r.bits,r.program_a,r.program_b,r.program_c)
    do_operation3("fixture",5,0,"REPAIR",r,trace)
    repaired=r.stage=="AT_EGRESS" and r.repaired and (r.y_a,r.y_b,r.output)==(ya,yb,yc)
    immutable=before==(r.bits,r.program_a,r.program_b,r.program_c)
    do_operation3("fixture",6,0,"VERIFY",r,trace)
    reverified=r.stage=="VERIFIED" and r.verified_after_repair
    g.finalize_verified({r.rid:r},7)
    done=r.stage=="DONE" and r.done_epoch==7
    return {"stage_a":s2,"stage_b":s3,"stage_c":s4,"ordered":s1 and s2 and s3 and s4,
            "b_depends_on_a":dependency_b,"c_depends_on_b":dependency_c,
            "detected":detected,"repaired_all_three":repaired,
            "immutable_provenance":immutable,"independent_reverify":reverified,"done_after_reverify":done}

def teacher_path_fixture(m):
    counts={"localized":0,"hybrid":0,"learned":0}
    orig_loc=base.c.localized_v0_step; orig_hybrid=base.hybrid_step; orig_learned=base._learned
    def loc(*args,**kwargs):
        counts["localized"]+=1
        return orig_loc(*args,**kwargs)
    def hybrid(*args,**kwargs):
        counts["hybrid"]+=1
        raise AssertionError("hybrid path used in LU2Q")
    def learned(*args,**kwargs):
        counts["learned"]+=1
        raise AssertionError("learned inference used in LU2Q")
    base.c.localized_v0_step=loc; base.hybrid_step=hybrid; base._learned=learned
    try:
        result,_,_,_=_run_world(m,False)
    finally:
        base.c.localized_v0_step=orig_loc; base.hybrid_step=orig_hybrid; base._learned=orig_learned
    return {"localized_calls":counts["localized"],"hybrid_calls":counts["hybrid"],"learned_calls":counts["learned"],
            "pass":counts["localized"]==160 and counts["hybrid"]==0 and counts["learned"]==0 and result["incorrect_done"]==0}

def maturity_fixture():
    progs=mechanical_programs()["C"]
    base_r=Task3Request(99,"C",0,(0,1,0,1),progs["A"],progs["B"],progs["C"],0)
    ya,yb,yc=expected_triple(base_r)
    def R(**kw):
        d=dict(base_r.__dict__)
        d.update(dict(y_a=ya,y_b=yb,output=yc,repaired=False,verified_after_repair=False,
                      done_epoch=None,stage="REPAIR_PENDING",expired_epoch=None,repair_epoch=None,verified_epoch=None))
        d.update(kw)
        return SimpleNamespace(**d)
    return {
        "mature156":_terminal_rule(R(repaired=True,verified_after_repair=True,done_epoch=159,stage="DONE",repair_epoch=157,verified_epoch=158),156)[0],
        "terminal157":_terminal_rule(R(repaired=True,verified_after_repair=True,stage="VERIFIED",repair_epoch=158,verified_epoch=159),157)[0],
        "terminal158":_terminal_rule(R(repaired=True,stage="AT_EGRESS",repair_epoch=159),158)[0],
        "terminal159":_terminal_rule(R(stage="REPAIR_PENDING"),159)[0],
    }

def mechanical_gate():
    global _PRIMARY_MANIFEST_CALLS
    before=_PRIMARY_MANIFEST_CALLS
    m=mechanical_manifest(); validate_manifest(m)
    stage=stage_repair_fixture()
    maturity=maturity_fixture()
    path=teacher_path_fixture(m)
    rng0=torch.random.get_rng_state().clone()
    row1=run_scored(m)
    rng1=torch.random.get_rng_state().clone()
    row2=run_scored(m)
    probes={
        "exact_v02_parent":base.PARENT_V02==PARENT_V02,
        "u_exact_teacher_path":path["pass"],
        "h_cs_fcfs_teacher_exact":path["hybrid_calls"]==0 and path["learned_calls"]==0,
        "d2_exact":p.D==2,
        "local_hedge_preserved":hasattr(base.c,"localized_v0_step"),
        "no_pool_exact":g.no_pool_fixture(),
        "g5_full_off":m["g5_full"] is False,
        "one_request_per_epoch":len(m["arrivals"])==160 and all(Counter(x["t"] for x in m["arrivals"])[t]==1 for t in range(160)),
        "three_process_stages":m["process_ops_per_request"]==3 and stage["stage_a"] and stage["stage_b"] and stage["stage_c"],
        "stage_b_depends_on_a":stage["b_depends_on_a"],
        "stage_c_depends_on_b":stage["c_depends_on_b"],
        "no_stage_skip":stage["ordered"],
        "verify_recomputes_three":stage["detected"],
        "repair_recomputes_three":stage["repaired_all_three"] and stage["immutable_provenance"],
        "independent_reverify_required":stage["independent_reverify"] and stage["done_after_reverify"],
        "inherited_distributed_lesion_8":m["lesion"]==sorted(p.lesion_set(m["seed"])) and len(m["lesion"])==8,
        "lesion_window_exact":p.LESION_START==96 and p.LESION_END==108,
        "anchor_relocation_unchanged":m["anchors0"]==p.anchors_for(m["seed"],0) and m["anchors4"]==p.anchors_for(m["seed"],128),
        "expiry_32":p.EXPIRY==32,
        "maturity_rules_unchanged":MATURE_MAX_DETECTION==156 and all(maturity.values()),
        "no_model_rng":torch.equal(rng0,rng1),
        "no_primary_manifest_during_gate":_PRIMARY_MANIFEST_CALLS==before,
        "duplicate_mechanical_byte_identical":canonical(row1)==canonical(row2),
        "mechanical_zero_incorrect_done":row1["result"]["incorrect_done"]==0,
    }
    return {"schema":1,"probes":probes,"all_pass":all(probes.values()),
            "stage_fixture":stage,"maturity_fixture":maturity,"teacher_path":path,
            "pair_bytes":len(canonical(row1)),"pair_sha256":hashlib.sha256(canonical(row1)).hexdigest(),
            "mechanical_world":row1}

def run_sweep(ms):
    if len(ms)!=10: raise AssertionError("need ten manifests")
    return [run_scored(m) for m in ms]

def open_duplicate(path1,path2):
    b1=Path(path1).read_bytes(); b2=Path(path2).read_bytes()
    if b1!=b2: raise RuntimeError("LU2Q duplicate mismatch")
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
    raise SystemExit("usage: mechanical OUT | manifests LU2QF1 OUT | sweep MANIFESTS OUT | open SWEEP1 SWEEP2 OUT")

if __name__=="__main__":
    main()

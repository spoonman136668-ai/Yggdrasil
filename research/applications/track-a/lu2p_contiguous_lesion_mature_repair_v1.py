#!/usr/bin/env python3
import hashlib, inspect, json, math, statistics, sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

import lu2n_contiguous_16cell_lesion_robustness_v1 as parent

g=parent.g
p=parent.p
base=parent.base

PREREG_LU2P="b1a02b436c223d75ceca40b00d0af852e52d128f"
PARENT_LU2O_CLOSURE="1d5deaa6231b854a00fb50e76b685e437b29e700"
PARENT_LU2N_CLOSURE="096c8dee7ae368f69e322be8e1b8a5ca20feff08"
PARENT_LU2NF1="a4657c94a654d2b4f83b6af0c7844b65e6999593"
PARENT_V02=parent.PARENT_V02
WEIGHT_SHA=parent.WEIGHT_SHA
ALPHA=0.25
REPLICATES=10
LOAD=1
LESION_START=96
LESION_END=108
MATURE_MAX_DETECTION=156

_PRIMARY_MANIFEST_CALLS=0

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()

def manifest_identity(m):
    x=dict(m); x.pop("manifest_sha256",None)
    return hashlib.sha256(canonical(x)).hexdigest()

def derive_programs(lu2pf1,replicate):
    if not isinstance(lu2pf1,str) or len(lu2pf1)!=40:
        raise ValueError("freeze sha")
    if replicate not in range(1,REPLICATES+1):
        raise ValueError(replicate)
    used=set(); out={}
    for stream in ("C","S"):
        out[stream]={}
        for stage in ("A","B"):
            counter=0
            while True:
                material=f"LU2P-TASK2-L1-CONTIG16-MATURE|{lu2pf1}|{replicate}|{stream}|{stage}|{counter}"
                cand=int.from_bytes(hashlib.sha256(material.encode()).digest()[:2],"big")
                counter+=1
                if not g.valid_program(cand) or cand in used:
                    continue
                used.add(cand); out[stream][stage]=cand; break
    return out

def _manifest(seed,programs,kind,replicate,lu2pf1,namespace):
    arrivals=parent.x.k.i.make_arrivals(seed,programs,LOAD)
    m={
        "kind":kind,
        "seed":seed,
        "replicate":replicate,
        "lu2pf1":lu2pf1,
        "lu2p_prereg_commit":PREREG_LU2P,
        "lu2p_seed_namespace":namespace,
        "parent_lu2o_closure":PARENT_LU2O_CLOSURE,
        "parent_lu2n_closure":PARENT_LU2N_CLOSURE,
        "parent_lu2nf1":PARENT_LU2NF1,
        "parent_v02":PARENT_V02,
        "canonical_weight_sha256":WEIGHT_SHA,
        "alpha":ALPHA,
        "programs":programs,
        "arrivals":arrivals,
        "corrupt_ids":[r["rid"] for r in arrivals if p.u01("LU2I-TASK2-CORRUPT",seed,r["rid"])<0.05],
        "lesion":parent.contiguous_lesion(seed),
        "inherited_lesion":sorted(p.lesion_set(seed)),
        "lesion_start":LESION_START,
        "lesion_end":LESION_END,
        "anchors0":p.anchors_for(seed,0),
        "anchors4":p.anchors_for(seed,128),
        "n":p.N,"t":p.T,"d":p.D,"r_task":p.R_TASK,"route_edges":6,
        "g5_full":False,"requests_per_epoch":1,"process_ops_per_request":2,
    }
    m["manifest_sha256"]=manifest_identity(m)
    return m

def mechanical_manifest():
    seed="LU2P-MECHANICAL-CONTIG16-MATURE-R1"
    return _manifest(seed,g.mechanical_programs(),"LU2P_MECHANICAL",0,None,seed)

def primary_manifest(lu2pf1,replicate):
    global _PRIMARY_MANIFEST_CALLS
    _PRIMARY_MANIFEST_CALLS+=1
    ns=f"LU2P-TASK2-L1-CONTIG16-MATURE|{lu2pf1}|{replicate}"
    seed=hashlib.sha256(ns.encode()).hexdigest()[:32]
    return _manifest(seed,derive_programs(lu2pf1,replicate),"LU2P_PRIMARY",replicate,lu2pf1,ns)

def primary_manifests(lu2pf1):
    return [primary_manifest(lu2pf1,k) for k in range(1,REPLICATES+1)]

def validate_manifest(m):
    if m["manifest_sha256"]!=manifest_identity(m): raise AssertionError("manifest hash")
    if m["lu2p_prereg_commit"]!=PREREG_LU2P: raise AssertionError("prereg")
    if (m["parent_lu2o_closure"],m["parent_lu2n_closure"],m["parent_lu2nf1"],m["parent_v02"])!=(PARENT_LU2O_CLOSURE,PARENT_LU2N_CLOSURE,PARENT_LU2NF1,PARENT_V02):
        raise AssertionError("lineage")
    if m["canonical_weight_sha256"]!=WEIGHT_SHA or m["alpha"]!=ALPHA: raise AssertionError("weight/alpha")
    if (m["n"],m["t"],m["d"],m["r_task"],m["route_edges"],m["g5_full"])!=(64,160,2,2,6,False): raise AssertionError("substrate")
    if m["requests_per_epoch"]!=1 or m["process_ops_per_request"]!=2: raise AssertionError("load/task")
    if p.EXPIRY!=32: raise AssertionError("expiry")
    if m["lesion_start"]!=96 or m["lesion_end"]!=108: raise AssertionError("lesion window")
    if m["inherited_lesion"]!=sorted(p.lesion_set(m["seed"])): raise AssertionError("inherited lesion")
    if m["lesion"]!=parent.contiguous_lesion(m["seed"]): raise AssertionError("contiguous lesion")
    if len(m["lesion"])!=16 or not parent.is_contiguous_ring(m["lesion"]): raise AssertionError("lesion geometry")
    if len(m["arrivals"])!=160: raise AssertionError("arrivals")
    by=Counter(r["t"] for r in m["arrivals"])
    if any(by[t]!=1 for t in range(160)): raise AssertionError("one per epoch")
    expected={(0,"C"):16,(0,"S"):16,(1,"C"):24,(1,"S"):8,(2,"C"):8,(2,"S"):24,(3,"C"):16,(3,"S"):16,(4,"C"):16,(4,"S"):16}
    sc=Counter((p.phase_of(r["t"]),r["stream"]) for r in m["arrivals"])
    if any(sc[k]!=v for k,v in expected.items()): raise AssertionError("phase schedule")
    vals=[m["programs"][s][st] for s in ("C","S") for st in ("A","B")]
    if len(set(vals))!=4 or not all(g.valid_program(v) for v in vals): raise AssertionError("programs")
    if m["arrivals"]!=parent.x.k.i.make_arrivals(m["seed"],m["programs"],1): raise AssertionError("arrival binding")
    if m["corrupt_ids"]!=[r["rid"] for r in m["arrivals"] if p.u01("LU2I-TASK2-CORRUPT",m["seed"],r["rid"])<0.05]: raise AssertionError("corruption")
    if m["anchors0"]!=p.anchors_for(m["seed"],0) or m["anchors4"]!=p.anchors_for(m["seed"],128): raise AssertionError("anchors")
    if m["kind"]=="LU2P_PRIMARY":
        rep=m["replicate"]; freeze=m["lu2pf1"]
        ns=f"LU2P-TASK2-L1-CONTIG16-MATURE|{freeze}|{rep}"
        if m["lu2p_seed_namespace"]!=ns or m["seed"]!=hashlib.sha256(ns.encode()).hexdigest()[:32]: raise AssertionError("seed")
        if m["programs"]!=derive_programs(freeze,rep): raise AssertionError("programs")
    elif m["kind"]=="LU2P_MECHANICAL":
        if m["replicate"]!=0 or m["lu2pf1"] is not None: raise AssertionError("mechanical identity")
    else:
        raise AssertionError("kind")
    return True

def _with_validation(fn,*args):
    old_parent=parent.validate_manifest
    old_x=parent.x.validate_manifest
    old_g=g.validate_manifest
    old_load=g.REQUESTS_PER_EPOCH
    parent.validate_manifest=validate_manifest
    parent.x.validate_manifest=validate_manifest
    g.validate_manifest=validate_manifest
    g.REQUESTS_PER_EPOCH=1
    try:
        return fn(*args)
    finally:
        parent.validate_manifest=old_parent
        parent.x.validate_manifest=old_x
        g.validate_manifest=old_g
        g.REQUESTS_PER_EPOCH=old_load

def _terminal_rule(r,det):
    if det is None:
        return False,"UNDETECTED"
    if r.expired_epoch is not None:
        return False,"EXPIRED"
    if det<=MATURE_MAX_DETECTION:
        ok=(r.repaired and r.verified_after_repair and r.done_epoch is not None and r.done_epoch<=159 and r.stage=="DONE" and r.output==g.expected_pair(r)[1])
        return ok,"MATURE"
    if det==157:
        ok=(r.repaired and r.repair_epoch is not None and r.repair_epoch<=158 and r.verified_after_repair and r.verified_epoch is not None and r.verified_epoch<=159 and r.done_epoch is None and r.stage=="VERIFIED" and r.output==g.expected_pair(r)[1])
        return ok,"TERMINAL_157"
    if det==158:
        ok=(r.repaired and r.repair_epoch is not None and r.repair_epoch<=159 and not r.verified_after_repair and r.done_epoch is None and r.stage=="AT_EGRESS" and r.output==g.expected_pair(r)[1])
        return ok,"TERMINAL_158"
    if det==159:
        ok=((not r.repaired) and r.repair_epoch is None and r.done_epoch is None and r.stage=="REPAIR_PENDING")
        return ok,"TERMINAL_159"
    return False,"OUT_OF_RANGE"

def _instrumented_world(m,mode):
    registry={}; detected_epoch={}
    orig_req=g.Task2Request
    orig_do=g.do_operation

    def tracked_request(*args,**kwargs):
        r=orig_req(*args,**kwargs)
        registry[r.rid]=r
        return r

    def tracked_do(seed,t,cell,op,r,trace):
        before=r.stage
        orig_do(seed,t,cell,op,r,trace)
        if op=="VERIFY" and before=="AT_EGRESS" and r.stage=="REPAIR_PENDING":
            detected_epoch.setdefault(r.rid,t)

    g.Task2Request=tracked_request
    g.do_operation=tracked_do
    try:
        result,state_history,telemetry=_with_validation(g.run_world,m,mode)
    finally:
        g.Task2Request=orig_req
        g.do_operation=orig_do

    rows=[]; all_ok=True
    reached=0; mature=0; terminal=0
    for rid in m["corrupt_ids"]:
        r=registry[rid]
        if not r.reached_egress_after_corrupt:
            continue
        reached+=1
        det=detected_epoch.get(rid)
        ok,kind=_terminal_rule(r,det)
        all_ok=all_ok and bool(ok)
        if det is not None and det<=MATURE_MAX_DETECTION: mature+=1
        if det is not None and det>=157: terminal+=1
        rows.append({
            "rid":rid,"arrival":r.created,"detection_epoch":det,
            "repair_epoch":r.repair_epoch,
            "verified_epoch":r.verified_epoch if r.verified_after_repair else None,
            "done_epoch":r.done_epoch,
            "terminal_state":r.stage,
            "expired_epoch":r.expired_epoch,
            "kind":kind,"pass":bool(ok)
        })
    maturity={
        "pass":bool(all_ok),
        "reached_egress":reached,
        "mature_detected":mature,
        "terminal_inflight_detected":terminal,
        "rows":rows,
    }
    return result,state_history,telemetry,maturity

def run_pair(m):
    validate_manifest(m)
    a0,s0,_,mat0=_instrumented_world(m,"U_A0")
    a25,s25,tel,mat25=_instrumented_world(m,"U_A25")
    diffs=[i for i,(x,y) in enumerate(zip(s0,s25)) if x!=y]
    causal={
        "u_evaluations":tel["u_evaluations"],
        "u_nonzero_tv":tel["u_nonzero_tv"],
        "u_realized_differences":tel["u_realized_differences"],
        "u_mean_tv":tel["u_mean_tv"],
        "h_evaluations":tel["h_evaluations"],
        "h_nonzero_delta":tel["h_nonzero_delta"],
        "h_realized_differences":tel["h_realized_differences"],
        "first_divergence_epoch":diffs[0] if diffs else None,
        "state_divergence_epochs":len(diffs),
    }
    return {
        "manifest":m,
        "a0":g.compact(a0),
        "a25":g.compact(a25),
        "maturity":{"a0":mat0,"a25":mat25},
        "causal":causal,
        "integrity":{
            "a0_duplicate_cell":a0["matching_duplicate_cell"]==0,
            "a0_duplicate_request":a0["matching_duplicate_request"]==0,
            "a25_duplicate_cell":a25["matching_duplicate_cell"]==0,
            "a25_duplicate_request":a25["matching_duplicate_request"]==0,
            "a0_incorrect_done_zero":a0["incorrect_done"]==0,
            "a25_incorrect_done_zero":a25["incorrect_done"]==0,
            "a0_repair_integrity":a0["repair"]["repair_integrity"],
            "a25_repair_integrity":a25["repair"]["repair_integrity"],
        }
    }

def baseline_feasible(row):
    r=row["a0"]
    return (
        all(r["phase"][str(ph)]["correct_done"]>=1 for ph in range(5))
        and r["incorrect_done"]==0
        and all(r["stream_total"][s]>=1 for s in ("C","S"))
        and row["maturity"]["a0"]["pass"]
        and r["operations_per_correct_completion"] is not None
        and math.isfinite(r["operations_per_correct_completion"])
        and row["integrity"]["a0_duplicate_cell"]
        and row["integrity"]["a0_duplicate_request"]
    )

def qualification(sweep):
    feasible=[row for row in sweep if baseline_feasible(row)]
    rows=[]; ratios=[]
    for row in feasible:
        a0=row["a0"]; a25=row["a25"]
        den=a0["events"]["correct_completion_area_phases0_4"]; num=a25["events"]["correct_completion_area_phases0_4"]
        ratio=num/den if den else (1.0 if num>=den else 0.0); ratios.append(ratio)
        stream_ok=True
        for ph in range(5):
            for s in ("C","S"):
                tv=a0["stream_phase"][str(ph)][s]; hv=a25["stream_phase"][str(ph)][s]
                if tv>=4 and hv<0.75*tv: stream_ok=False
        ar0=a0["events"]["anchor_rotation_recovery_latency"]; ar25=a25["events"]["anchor_rotation_recovery_latency"]
        dr0=a0["events"]["demand_reversal_recovery_latency"]; dr25=a25["events"]["demand_reversal_recovery_latency"]
        lr0=a0["events"]["lesion_recovery_latency"]; lr25=a25["events"]["lesion_recovery_latency"]
        lesion_ok=((lr0 is not None and lr25 is not None and lr25<=lr0+8) or a25["events"]["lesion_backlog_area"]<=a0["events"]["lesion_backlog_area"])
        checks={
            "area_ge_90pct":ratio>=0.90,
            "final16_backlog_area":a25["final16_total_backlog_area"]<=1.25*a0["final16_total_backlog_area"],
            "final_backlog":a25["backlog"]<=1.25*a0["backlog"],
            "ops":a25["operations_per_correct_completion"] is not None and a0["operations_per_correct_completion"] not in (None,0) and a25["operations_per_correct_completion"]<=1.25*a0["operations_per_correct_completion"],
            "stream_noncollapse":stream_ok,
            "anchor_recovery_pair_plus8":ar0 is not None and ar25 is not None and ar25<=ar0+8,
            "demand_recovery_pair_plus8":dr0 is not None and dr25 is not None and dr25<=dr0+8,
            "contiguous_lesion_recovery":lesion_ok,
            "incorrect_done_zero":a25["incorrect_done"]==0,
            "maturity_repair_integrity":row["maturity"]["a25"]["pass"],
            "matching_integrity":all(row["integrity"][q] for q in ("a0_duplicate_cell","a0_duplicate_request","a25_duplicate_cell","a25_duplicate_request")),
        }
        rows.append({"replicate":row["manifest"]["replicate"],"area_ratio":ratio,"checks":checks,"pass":all(checks.values()),"recovery":{"a0_demand":dr0,"a25_demand":dr25,"a0_anchor":ar0,"a25_anchor":ar25,"a0_lesion":lr0,"a25_lesion":lr25}})
    med=float(np.median(np.asarray(ratios,dtype=float))) if ratios else None
    ueval=sum(r["causal"]["u_evaluations"] for r in feasible)
    utv=sum(r["causal"]["u_nonzero_tv"] for r in feasible)
    udiff=sum(r["causal"]["u_realized_differences"] for r in feasible)
    hdelta=sum(r["causal"]["h_nonzero_delta"] for r in feasible)
    hdiff=sum(r["causal"]["h_realized_differences"] for r in feasible)
    coverage=len(feasible)>=8
    causal=ueval>0 and utv>0 and udiff>0
    h_teacher=hdelta==0 and hdiff==0
    positive=coverage and causal and h_teacher and bool(rows) and all(r["pass"] for r in rows) and med is not None and med>=0.95
    return {
        "LU2P_CONTIGUOUS_LESION_ROBUSTNESS":bool(positive),
        "baseline_feasible_count":len(feasible),
        "evidence_coverage_pass":coverage,
        "causal":bool(causal),
        "h_teacher_preserved":bool(h_teacher),
        "median_area_ratio":med,
        "per_replicate":rows,
        "causal_totals":{"u_evaluations":ueval,"u_nonzero_tv":utv,"u_realized_differences":udiff,"h_nonzero_delta":hdelta,"h_realized_differences":hdiff},
        "descriptive":{
            "a0_correct_total":sum(r["a0"]["correct_done"] for r in sweep),
            "a25_correct_total":sum(r["a25"]["correct_done"] for r in sweep),
            "a0_incorrect_total":sum(r["a0"]["incorrect_done"] for r in sweep),
            "a25_incorrect_total":sum(r["a25"]["incorrect_done"] for r in sweep),
            "a0_expired_total":sum(r["a0"]["expired"] for r in sweep),
            "a25_expired_total":sum(r["a25"]["expired"] for r in sweep),
            "a0_terminal_inflight":sum(r["maturity"]["a0"]["terminal_inflight_detected"] for r in sweep),
            "a25_terminal_inflight":sum(r["maturity"]["a25"]["terminal_inflight_detected"] for r in sweep),
            "state_divergence_epochs_total":sum(r["causal"]["state_divergence_epochs"] for r in sweep),
            "first_divergence_epochs":[r["causal"]["first_divergence_epoch"] for r in sweep],
        }
    }

def _maturity_fixture():
    def R(**kw):
        basekw=dict(repaired=False,verified_after_repair=False,done_epoch=None,stage="REPAIR_PENDING",output=1,expired_epoch=None,repair_epoch=None,verified_epoch=None,bits=(0,0,0,0),program_a=0,program_b=0)
        basekw.update(kw); return SimpleNamespace(**basekw)
    old_expected=g.expected_pair
    g.expected_pair=lambda r:(0,1)
    try:
        cases={
            "mature156":_terminal_rule(R(repaired=True,verified_after_repair=True,done_epoch=159,stage="DONE",repair_epoch=157,verified_epoch=158),156)[0],
            "terminal157":_terminal_rule(R(repaired=True,verified_after_repair=True,stage="VERIFIED",repair_epoch=158,verified_epoch=159),157)[0],
            "terminal158":_terminal_rule(R(repaired=True,stage="AT_EGRESS",repair_epoch=159),158)[0],
            "terminal159":_terminal_rule(R(stage="REPAIR_PENDING"),159)[0],
            "bad157":not _terminal_rule(R(stage="REPAIR_PENDING"),157)[0],
            "bad158":not _terminal_rule(R(stage="REPAIR_PENDING"),158)[0],
        }
    finally:
        g.expected_pair=old_expected
    return cases

def mechanical_gate():
    global _PRIMARY_MANIFEST_CALLS
    before=_PRIMARY_MANIFEST_CALLS
    m=mechanical_manifest(); validate_manifest(m)
    calls=_with_validation(g.learned_call_scope_fixture,m)
    weight_sha=hashlib.sha256(base._weights_bytes()).hexdigest()
    plain=_with_validation(g.run_pair,m)
    rng0=torch.random.get_rng_state().clone()
    pair1=run_pair(m)
    rng1=torch.random.get_rng_state().clone()
    pair2=run_pair(m)
    stripped1={k:v for k,v in pair1.items() if k!="maturity"}
    fixture=_with_validation(g.stage_repair_fixture)
    csfix=_with_validation(g.cs_fcfs_echo_teacher_parity_fixture,m)
    matfix=_maturity_fixture()
    probes={
        "exact_lu2n_dynamics_inert":stripped1==plain,
        "exact_canonical_weight_sha":weight_sha==WEIGHT_SHA,
        "alpha_exact_025":ALPHA==parent.ALPHA==0.25,
        "u_a0_teacher_one_step":_with_validation(g.one_step_parity,m),
        "u_a25_convex_blend":_with_validation(g.blend_fixture,m),
        "h_teacher_exact":pair1["causal"]["h_nonzero_delta"]==0 and pair1["causal"]["h_realized_differences"]==0,
        "cs_fcfs_teacher_exact":bool(csfix["equal"]) and csfix["learned_calls"]==[],
        "obs_v1_unchanged":base.a.INPUT_WIDTH==70,
        "load_one_exact":len(m["arrivals"])==160 and all(Counter(r["t"] for r in m["arrivals"])[t]==1 for t in range(160)),
        "contiguous_lesion_16":len(m["lesion"])==16 and parent.is_contiguous_ring(m["lesion"]),
        "lesion_window_exact":m["lesion_start"]==96 and m["lesion_end"]==108,
        "expiry_32":p.EXPIRY==32,
        "task2_stage_semantics_exact":bool(fixture["stage_order_ok"] and fixture["repair_ok"] and fixture["immutable_provenance_unchanged"]),
        "maturity_boundary_156":MATURE_MAX_DETECTION==156,
        "terminal_rules_exact":all(matfix.values()),
        "no_drain_epochs":p.T==160,
        "common_transition_variates":_with_validation(g.common_rng_fixture,m),
        "no_model_rng":torch.equal(rng0,rng1),
        "learned_scope_hu_only":bool(calls) and set(calls)<=set(("H","U")) and not (set(calls)&set(("C","S","FC","FS"))),
        "no_primary_manifest_during_gate":_PRIMARY_MANIFEST_CALLS==before,
        "duplicate_mechanical_byte_identical":canonical(pair1)==canonical(pair2),
        "mechanical_zero_incorrect_done":pair1["a0"]["incorrect_done"]==0 and pair1["a25"]["incorrect_done"]==0,
    }
    return {"schema":1,"probes":probes,"all_pass":all(probes.values()),"weight_sha256":weight_sha,"maturity_fixture":matfix,"pair_bytes":len(canonical(pair1)),"pair_sha256":hashlib.sha256(canonical(pair1)).hexdigest(),"mechanical_pair":pair1}

def run_sweep(ms):
    if len(ms)!=10: raise AssertionError("need ten manifests")
    return [run_pair(m) for m in ms]

def open_duplicate(path1,path2):
    b1=Path(path1).read_bytes(); b2=Path(path2).read_bytes()
    if b1!=b2: raise RuntimeError("LU2P duplicate mismatch")
    sweep=json.loads(b1.decode())
    return {"duplicate":{"byte_identical":True,"bytes":len(b1),"sha256":hashlib.sha256(b1).hexdigest()},"qualification":qualification(sweep),"sweep":sweep}

def write(path,obj):
    Path(path).write_bytes(canonical(obj))

def main():
    if len(sys.argv)>=2 and sys.argv[1]=="mechanical":
        write(sys.argv[2],mechanical_gate()); return
    if len(sys.argv)>=2 and sys.argv[1]=="manifests":
        write(sys.argv[3],primary_manifests(sys.argv[2])); return
    if len(sys.argv)>=2 and sys.argv[1]=="sweep":
        write(sys.argv[3],run_sweep(json.load(open(sys.argv[2],encoding="utf-8")))); return
    if len(sys.argv)>=2 and sys.argv[1]=="open":
        write(sys.argv[4],open_duplicate(sys.argv[2],sys.argv[3])); return
    raise SystemExit("usage: mechanical OUT | manifests LU2PF1 OUT | sweep MANIFESTS OUT | open SWEEP1 SWEEP2 OUT")

if __name__=="__main__":
    main()

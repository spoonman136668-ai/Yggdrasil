#!/usr/bin/env python3
import hashlib, inspect, json, math, statistics, sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch

import lu2m_doubled_distributed_lesion_robustness_v1 as parent_m

x=parent_m.x
g=parent_m.g
p=parent_m.p
base=parent_m.base

PREREG_LU2N="f35e9330ba703fecdcdcfc6b9134b89e07df0dc3"
PARENT_LU2M_CLOSURE="240e4cd49056a9ec2f80fe66e6e5decca1799be2"
PARENT_LU2MF1="e05168e6452f81cad45474ed0984fe4970762456"
PARENT_LU2L_CLOSURE="ed618450559eb8275557108f758c61949e030653"
PARENT_LU2LF1="799058733a864c1d8437569cf4e8cdc6502fa6c3"
PARENT_LU2K_CLOSURE="c6333ccf2fa9e3244feee66bf021cdc17924d145"
PARENT_V02=x.PARENT_V02
WEIGHT_SHA=x.WEIGHT_SHA
ALPHA=0.25
REPLICATES=10
LOAD=1
LESION_START=96
LESION_END=108

_PRIMARY_MANIFEST_CALLS=0

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()

def manifest_identity(m):
    y=dict(m); y.pop("manifest_sha256",None)
    return hashlib.sha256(canonical(y)).hexdigest()

def contiguous_lesion(seed):
    inherited=sorted(p.lesion_set(seed))
    if len(inherited)!=8:
        raise AssertionError(("inherited lesion geometry",len(inherited)))
    k=min(inherited)
    contiguous={(k+j)%p.N for j in range(16)}
    distributed=set(parent_m.strong_lesion(seed))
    if len(contiguous)!=16 or contiguous==distributed:
        raise AssertionError(("contiguous lesion geometry",len(contiguous)))
    return sorted(contiguous)

def is_contiguous_ring(cells):
    target=set(cells)
    if len(target)!=16:
        return False
    return any({(start+j)%p.N for j in range(16)}==target for start in target)

def derive_programs(lu2nf1,replicate):
    if not isinstance(lu2nf1,str) or len(lu2nf1)!=40:
        raise ValueError("freeze sha")
    if replicate not in range(1,REPLICATES+1):
        raise ValueError(replicate)
    used=set(); out={}
    for stream in ("C","S"):
        out[stream]={}
        for stage in ("A","B"):
            counter=0
            while True:
                material=f"LU2N-TASK2-L1-CONTIG16|{lu2nf1}|{replicate}|{stream}|{stage}|{counter}"
                cand=int.from_bytes(hashlib.sha256(material.encode()).digest()[:2],"big")
                counter+=1
                if not g.valid_program(cand) or cand in used:
                    continue
                used.add(cand); out[stream][stage]=cand; break
    return out

def _manifest(seed,programs,kind,replicate,lu2nf1,namespace):
    arrivals=x.k.i.make_arrivals(seed,programs,LOAD)
    m={
        "kind":kind,
        "seed":seed,
        "replicate":replicate,
        "lu2nf1":lu2nf1,
        "lu2n_prereg_commit":PREREG_LU2N,
        "lu2n_seed_namespace":namespace,
        "parent_lu2m_closure":PARENT_LU2M_CLOSURE,
        "parent_lu2mf1":PARENT_LU2MF1,
        "parent_lu2l_closure":PARENT_LU2L_CLOSURE,
        "parent_lu2lf1":PARENT_LU2LF1,
        "parent_lu2k_closure":PARENT_LU2K_CLOSURE,
        "parent_v02":PARENT_V02,
        "canonical_weight_sha256":WEIGHT_SHA,
        "alpha":ALPHA,
        "programs":programs,
        "arrivals":arrivals,
        "corrupt_ids":[r["rid"] for r in arrivals if p.u01("LU2I-TASK2-CORRUPT",seed,r["rid"])<0.05],
        "lesion":contiguous_lesion(seed),
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
    seed="LU2N-MECHANICAL-CONTIG16-R1"
    return _manifest(seed,g.mechanical_programs(),"LU2N_MECHANICAL",0,None,seed)

def primary_manifest(lu2nf1,replicate):
    global _PRIMARY_MANIFEST_CALLS
    _PRIMARY_MANIFEST_CALLS+=1
    ns=f"LU2N-TASK2-L1-CONTIG16|{lu2nf1}|{replicate}"
    seed=hashlib.sha256(ns.encode()).hexdigest()[:32]
    return _manifest(seed,derive_programs(lu2nf1,replicate),"LU2N_PRIMARY",replicate,lu2nf1,ns)

def primary_manifests(lu2nf1):
    return [primary_manifest(lu2nf1,k) for k in range(1,REPLICATES+1)]

def validate_manifest(m):
    if m["manifest_sha256"]!=manifest_identity(m): raise AssertionError("manifest hash")
    if m["lu2n_prereg_commit"]!=PREREG_LU2N: raise AssertionError("prereg")
    if (m["parent_lu2m_closure"],m["parent_lu2mf1"],m["parent_lu2l_closure"],m["parent_lu2lf1"],m["parent_lu2k_closure"],m["parent_v02"])!=(PARENT_LU2M_CLOSURE,PARENT_LU2MF1,PARENT_LU2L_CLOSURE,PARENT_LU2LF1,PARENT_LU2K_CLOSURE,PARENT_V02):
        raise AssertionError("lineage")
    if m["canonical_weight_sha256"]!=WEIGHT_SHA or m["alpha"]!=ALPHA: raise AssertionError("weight/alpha")
    if (m["n"],m["t"],m["d"],m["r_task"],m["route_edges"],m["g5_full"])!=(64,160,2,2,6,False): raise AssertionError("substrate")
    if m["requests_per_epoch"]!=1 or m["process_ops_per_request"]!=2: raise AssertionError("load/task")
    if p.EXPIRY!=32: raise AssertionError("expiry")
    if m["lesion_start"]!=96 or m["lesion_end"]!=108: raise AssertionError("lesion window")
    inherited=sorted(p.lesion_set(m["seed"]))
    if m["inherited_lesion"]!=inherited: raise AssertionError("inherited lesion")
    if m["lesion"]!=contiguous_lesion(m["seed"]): raise AssertionError("contiguous lesion")
    if len(m["inherited_lesion"])!=8 or len(m["lesion"])!=16: raise AssertionError("lesion size")
    if not is_contiguous_ring(m["lesion"]): raise AssertionError("lesion contiguity")
    if set(m["lesion"])==set(parent_m.strong_lesion(m["seed"])): raise AssertionError("geometry not changed")
    if min(m["lesion"])!=(p.h64("TASK1-LESION-OFFSET",m["seed"])%8): raise AssertionError("base offset family")
    if len(m["arrivals"])!=160: raise AssertionError("arrivals")
    counts=Counter(r["t"] for r in m["arrivals"])
    if any(counts[t]!=1 for t in range(160)): raise AssertionError("one per epoch")
    expected={(0,"C"):16,(0,"S"):16,(1,"C"):24,(1,"S"):8,(2,"C"):8,(2,"S"):24,(3,"C"):16,(3,"S"):16,(4,"C"):16,(4,"S"):16}
    sc=Counter((p.phase_of(r["t"]),r["stream"]) for r in m["arrivals"])
    if any(sc[k]!=v for k,v in expected.items()): raise AssertionError("phase schedule")
    vals=[m["programs"][s][st] for s in ("C","S") for st in ("A","B")]
    if len(set(vals))!=4 or not all(g.valid_program(v) for v in vals): raise AssertionError("programs")
    if m["arrivals"]!=x.k.i.make_arrivals(m["seed"],m["programs"],1): raise AssertionError("arrival binding")
    if m["corrupt_ids"]!=[r["rid"] for r in m["arrivals"] if p.u01("LU2I-TASK2-CORRUPT",m["seed"],r["rid"])<0.05]: raise AssertionError("corruption")
    if m["anchors0"]!=p.anchors_for(m["seed"],0) or m["anchors4"]!=p.anchors_for(m["seed"],128): raise AssertionError("anchors")
    if m["kind"]=="LU2N_PRIMARY":
        rep=m["replicate"]; freeze=m["lu2nf1"]
        ns=f"LU2N-TASK2-L1-CONTIG16|{freeze}|{rep}"
        if m["lu2n_seed_namespace"]!=ns or m["seed"]!=hashlib.sha256(ns.encode()).hexdigest()[:32]: raise AssertionError("seed")
        if m["programs"]!=derive_programs(freeze,rep): raise AssertionError("primary programs")
    elif m["kind"]=="LU2N_MECHANICAL":
        if m["replicate"]!=0 or m["lu2nf1"] is not None: raise AssertionError("mechanical identity")
    else:
        raise AssertionError("kind")
    return True

def _with_validation(fn,*args):
    old_x=x.validate_manifest
    old_g=g.validate_manifest
    old_load=g.REQUESTS_PER_EPOCH
    x.validate_manifest=validate_manifest
    g.validate_manifest=validate_manifest
    g.REQUESTS_PER_EPOCH=1
    try:
        return fn(*args)
    finally:
        x.validate_manifest=old_x
        g.validate_manifest=old_g
        g.REQUESTS_PER_EPOCH=old_load

def run_pair(m):
    validate_manifest(m)
    return _with_validation(g.run_pair,m)

def baseline_feasible(row):
    r=row["a0"]
    return (
        all(r["phase"][str(ph)]["correct_done"]>=1 for ph in range(5))
        and r["incorrect_done"]==0
        and all(r["stream_total"][s]>=1 for s in ("C","S"))
        and r["repair"]["repair_integrity"]
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
        den=a0["events"]["correct_completion_area_phases0_4"]
        num=a25["events"]["correct_completion_area_phases0_4"]
        ratio=num/den if den else (1.0 if num>=den else 0.0)
        ratios.append(ratio)
        stream_ok=True
        for ph in range(5):
            for s in ("C","S"):
                tv=a0["stream_phase"][str(ph)][s]
                hv=a25["stream_phase"][str(ph)][s]
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
            "repair_integrity":a25["repair"]["repair_integrity"],
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
        "LU2N_CONTIGUOUS_LESION_ROBUSTNESS":bool(positive),
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
            "state_divergence_epochs_total":sum(r["causal"]["state_divergence_epochs"] for r in sweep),
            "first_divergence_epochs":[r["causal"]["first_divergence_epoch"] for r in sweep],
            "u_mean_tv":[r["causal"]["u_mean_tv"] for r in sweep],
        }
    }

def mechanical_gate():
    global _PRIMARY_MANIFEST_CALLS
    before=_PRIMARY_MANIFEST_CALLS
    m=mechanical_manifest(); validate_manifest(m)
    inherited=set(m["inherited_lesion"]); contiguous=set(m["lesion"]); distributed=set(parent_m.strong_lesion(m["seed"]))
    # Warm the frozen learned path before measuring RNG consumption.
    # Model construction initializes temporary parameters before loading the
    # canonical state dict; that one-time construction is not inference RNG.
    calls=_with_validation(g.learned_call_scope_fixture,m)
    weight_sha=hashlib.sha256(base._weights_bytes()).hexdigest()
    rng0=torch.random.get_rng_state().clone()
    pair1=run_pair(m)
    rng1=torch.random.get_rng_state().clone()
    pair2=run_pair(m)
    b1=canonical(pair1); b2=canonical(pair2)
    fixture=_with_validation(g.stage_repair_fixture)
    csfix=_with_validation(g.cs_fcfs_echo_teacher_parity_fixture,m)
    probes={
        "exact_lu2m_lu2l_alpha":parent_m.ALPHA==x.ALPHA==ALPHA==0.25,
        "exact_canonical_weight_sha":weight_sha==WEIGHT_SHA,
        "u_a0_teacher_one_step":_with_validation(g.one_step_parity,m),
        "u_a25_convex_blend":_with_validation(g.blend_fixture,m),
        "h_teacher_exact":pair1["causal"]["h_nonzero_delta"]==0 and pair1["causal"]["h_realized_differences"]==0,
        "cs_fcfs_teacher_exact":bool(csfix["equal"]) and csfix["learned_calls"]==[],
        "obs_v1_unchanged":base.a.INPUT_WIDTH==70,
        "l1_load_unchanged":len(m["arrivals"])==160 and all(Counter(r["t"] for r in m["arrivals"])[t]==1 for t in range(160)),
        "task2_stage_repair_exact":bool(fixture["stage_order_ok"] and fixture["repair_ok"] and fixture["immutable_provenance_unchanged"]),
        "expiry_32":p.EXPIRY==32,
        "inherited_lesion_8":len(inherited)==8,
        "contiguous_lesion_16":len(contiguous)==16,
        "contiguous_ring_interval":is_contiguous_ring(contiguous),
        "lesion_footprint_25pct":len(contiguous)/p.N==0.25,
        "same_seed_base_offset":min(contiguous)==min(inherited),
        "differs_from_distributed16":contiguous!=distributed,
        "lesion_duration_12":m["lesion_start"]==96 and m["lesion_end"]==108 and m["lesion_end"]-m["lesion_start"]==12,
        "no_lesion_feature_in_learned_signature":"lesion" not in base._learned.__code__.co_varnames[:base._learned.__code__.co_argcount],
        "common_transition_variates":_with_validation(g.common_rng_fixture,m),
        "no_model_rng":torch.equal(rng0,rng1),
        "learned_scope_hu_only":bool(calls) and set(calls)<=set(("H","U")) and not (set(calls)&set(("C","S","FC","FS"))),
        "no_primary_manifest_during_gate":_PRIMARY_MANIFEST_CALLS==before,
        "duplicate_mechanical_byte_identical":b1==b2,
        "mechanical_zero_incorrect_done":pair1["a0"]["incorrect_done"]==0 and pair1["a25"]["incorrect_done"]==0,
    }
    return {"schema":1,"probes":probes,"all_pass":all(probes.values()),"weight_sha256":weight_sha,"inherited_lesion":sorted(inherited),"distributed_lesion16":sorted(distributed),"contiguous_lesion16":sorted(contiguous),"pair_bytes":len(b1),"pair_sha256":hashlib.sha256(b1).hexdigest(),"mechanical_pair":pair1}

def run_sweep(ms):
    if len(ms)!=10: raise AssertionError("need ten manifests")
    return [run_pair(m) for m in ms]

def open_duplicate(path1,path2):
    b1=Path(path1).read_bytes(); b2=Path(path2).read_bytes()
    if b1!=b2: raise RuntimeError("LU2N duplicate mismatch")
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
    raise SystemExit("usage: mechanical OUT | manifests LU2NF1 OUT | sweep MANIFESTS OUT | open SWEEP1 SWEEP2 OUT")

if __name__=="__main__":
    main()

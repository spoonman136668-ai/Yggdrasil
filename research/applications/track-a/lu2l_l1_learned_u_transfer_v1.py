#!/usr/bin/env python3
import hashlib, inspect, json, math, statistics, sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch

import lu2g_second_task_compositional_service_transfer_v1 as frozen_g
import lu2k_fresh_l1_exact_parent_validation_v1 as k

g=frozen_g.g
p=g.p
base=g.base

PREREG_LU2L="fa0b50d3b5b9abbaf844498011ffbf1f8d8fb20e"
PARENT_LU2K="c6333ccf2fa9e3244feee66bf021cdc17924d145"
PARENT_LU2KF1="441d90e9c39e0ed9444953937d90d585084b4c7b"
PARENT_LU2GF1="e9a01aa97587fc97dde073cb2a6a35ad141006cd"
PARENT_LU2EF1="377fdc6e3b65fe843f77296cf1bbdc82736813a1"
PARENT_V02="e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2"
WEIGHT_SHA="b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023"
ALPHA=0.25
REPLICATES=10
LOAD=1

_PRIMARY_MANIFEST_CALLS=0

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()

def manifest_identity(m):
    x=dict(m); x.pop("manifest_sha256",None)
    return hashlib.sha256(canonical(x)).hexdigest()

def derive_programs(lu2lf1,replicate):
    if not isinstance(lu2lf1,str) or len(lu2lf1)!=40:
        raise ValueError("freeze sha")
    if replicate not in range(1,REPLICATES+1):
        raise ValueError(replicate)
    used=set(); out={}
    for stream in ("C","S"):
        out[stream]={}
        for stage in ("A","B"):
            counter=0
            while True:
                material=f"LU2L-TASK2-L1|{lu2lf1}|{replicate}|{stream}|{stage}|{counter}"
                cand=int.from_bytes(hashlib.sha256(material.encode()).digest()[:2],"big")
                counter+=1
                if not g.valid_program(cand) or cand in used:
                    continue
                used.add(cand); out[stream][stage]=cand; break
    return out

def _base_manifest(seed,programs,kind,replicate,lu2lf1,namespace):
    arrivals=k.i.make_arrivals(seed,programs,LOAD)
    m={
        "kind":kind,
        "seed":seed,
        "replicate":replicate,
        "lu2lf1":lu2lf1,
        "lu2l_prereg_commit":PREREG_LU2L,
        "lu2l_seed_namespace":namespace,
        "parent_lu2k":PARENT_LU2K,
        "parent_lu2kf1":PARENT_LU2KF1,
        "parent_lu2gf1":PARENT_LU2GF1,
        "parent_lu2ef1":PARENT_LU2EF1,
        "parent_v02":PARENT_V02,
        "canonical_weight_sha256":WEIGHT_SHA,
        "alpha":ALPHA,
        "programs":programs,
        "arrivals":arrivals,
        "corrupt_ids":[x["rid"] for x in arrivals if p.u01("LU2I-TASK2-CORRUPT",seed,x["rid"])<0.05],
        "lesion":sorted(p.lesion_set(seed)),
        "anchors0":p.anchors_for(seed,0),
        "anchors4":p.anchors_for(seed,128),
        "n":p.N,
        "t":p.T,
        "d":p.D,
        "r_task":p.R_TASK,
        "route_edges":6,
        "g5_full":False,
        "requests_per_epoch":LOAD,
        "process_ops_per_request":2,
    }
    m["manifest_sha256"]=manifest_identity(m)
    return m

def mechanical_manifest():
    return _base_manifest(
        "LU2L-MECHANICAL-L1-R1",
        g.mechanical_programs(),
        "LU2L_MECHANICAL",
        0,
        None,
        "LU2L-MECHANICAL-L1-R1",
    )

def primary_manifest(lu2lf1,replicate):
    global _PRIMARY_MANIFEST_CALLS
    _PRIMARY_MANIFEST_CALLS+=1
    if not isinstance(lu2lf1,str) or len(lu2lf1)!=40:
        raise ValueError("freeze sha")
    if replicate not in range(1,REPLICATES+1):
        raise ValueError(replicate)
    ns=f"LU2L-TASK2-L1-A25-TRANSFER|{lu2lf1}|{replicate}"
    digest=hashlib.sha256(ns.encode()).hexdigest()
    return _base_manifest(digest[:32],derive_programs(lu2lf1,replicate),"LU2L_PRIMARY",replicate,lu2lf1,ns)

def primary_manifests(lu2lf1):
    return [primary_manifest(lu2lf1,k0) for k0 in range(1,REPLICATES+1)]

def validate_manifest(m):
    if m["manifest_sha256"]!=manifest_identity(m):
        raise AssertionError("manifest hash")
    if m["lu2l_prereg_commit"]!=PREREG_LU2L:
        raise AssertionError("prereg")
    if (m["parent_lu2k"],m["parent_lu2kf1"],m["parent_lu2gf1"],m["parent_lu2ef1"],m["parent_v02"])!=(PARENT_LU2K,PARENT_LU2KF1,PARENT_LU2GF1,PARENT_LU2EF1,PARENT_V02):
        raise AssertionError("lineage")
    if m["canonical_weight_sha256"]!=WEIGHT_SHA or m["alpha"]!=ALPHA:
        raise AssertionError("weight/alpha")
    if (m["n"],m["t"],m["d"],m["r_task"],m["route_edges"],m["g5_full"])!=(64,160,2,2,6,False):
        raise AssertionError("substrate")
    if m["requests_per_epoch"]!=1 or m["process_ops_per_request"]!=2:
        raise AssertionError("load/task")
    if p.EXPIRY!=32:
        raise AssertionError("expiry")
    if len(m["arrivals"])!=160:
        raise AssertionError("arrivals")
    by_epoch=Counter(x["t"] for x in m["arrivals"])
    if any(by_epoch[t]!=1 for t in range(160)):
        raise AssertionError("one per epoch")
    expected_counts={(0,"C"):16,(0,"S"):16,(1,"C"):24,(1,"S"):8,(2,"C"):8,(2,"S"):24,(3,"C"):16,(3,"S"):16,(4,"C"):16,(4,"S"):16}
    counts=Counter((p.phase_of(x["t"]),x["stream"]) for x in m["arrivals"])
    if any(counts[k0]!=v for k0,v in expected_counts.items()):
        raise AssertionError(("phase schedule",counts))
    vals=[m["programs"][s][st] for s in ("C","S") for st in ("A","B")]
    if len(set(vals))!=4 or not all(g.valid_program(x) for x in vals):
        raise AssertionError("programs")
    if m["arrivals"]!=k.i.make_arrivals(m["seed"],m["programs"],1):
        raise AssertionError("arrivals binding")
    if m["corrupt_ids"]!=[x["rid"] for x in m["arrivals"] if p.u01("LU2I-TASK2-CORRUPT",m["seed"],x["rid"])<0.05]:
        raise AssertionError("corruption")
    if m["lesion"]!=sorted(p.lesion_set(m["seed"])):
        raise AssertionError("lesion")
    if m["anchors0"]!=p.anchors_for(m["seed"],0) or m["anchors4"]!=p.anchors_for(m["seed"],128):
        raise AssertionError("anchors")
    if m["kind"]=="LU2L_PRIMARY":
        rep=m["replicate"]; freeze=m["lu2lf1"]
        ns=f"LU2L-TASK2-L1-A25-TRANSFER|{freeze}|{rep}"
        digest=hashlib.sha256(ns.encode()).hexdigest()
        if m["lu2l_seed_namespace"]!=ns or m["seed"]!=digest[:32]:
            raise AssertionError("primary seed")
        if m["programs"]!=derive_programs(freeze,rep):
            raise AssertionError("primary programs")
    elif m["kind"]=="LU2L_MECHANICAL":
        if m["replicate"]!=0 or m["lu2lf1"] is not None or m["seed"]!="LU2L-MECHANICAL-L1-R1":
            raise AssertionError("mechanical identity")
    else:
        raise AssertionError("kind")
    return True

def _with_l1_pair(m):
    old_validate=g.validate_manifest
    old_load=g.REQUESTS_PER_EPOCH
    g.validate_manifest=validate_manifest
    g.REQUESTS_PER_EPOCH=1
    try:
        return g.run_pair(m)
    finally:
        g.validate_manifest=old_validate
        g.REQUESTS_PER_EPOCH=old_load

def baseline_feasible(x):
    r=x["a0"]
    return (
        all(r["phase"][str(ph)]["correct_done"]>=1 for ph in range(5))
        and r["incorrect_done"]==0
        and all(r["stream_total"][s]>=1 for s in ("C","S"))
        and r["repair"]["repair_integrity"]
        and r["operations_per_correct_completion"] is not None
        and math.isfinite(r["operations_per_correct_completion"])
        and x["integrity"]["a0_duplicate_cell"]
        and x["integrity"]["a0_duplicate_request"]
    )

def qualification(sweep):
    feasible=[x for x in sweep if baseline_feasible(x)]
    rows=[]; ratios=[]
    for x in feasible:
        a0=x["a0"]; a25=x["a25"]
        den=a0["events"]["correct_completion_area_phases0_4"]
        num=a25["events"]["correct_completion_area_phases0_4"]
        ratio=num/den if den else (1.0 if num>=den else 0.0)
        ratios.append(ratio)
        stream_ok=True
        for ph in range(5):
            for s in ("C","S"):
                tv=a0["stream_phase"][str(ph)][s]
                hv=a25["stream_phase"][str(ph)][s]
                if tv>=4 and hv<0.75*tv:
                    stream_ok=False
        ar0=a0["events"]["anchor_rotation_recovery_latency"]
        ar25=a25["events"]["anchor_rotation_recovery_latency"]
        dr0=a0["events"]["demand_reversal_recovery_latency"]
        dr25=a25["events"]["demand_reversal_recovery_latency"]
        lesion_lat=a25["events"]["lesion_recovery_latency"]
        lesion_ok=((lesion_lat is not None and lesion_lat<=8) or a25["events"]["lesion_backlog_area"]<=a0["events"]["lesion_backlog_area"])
        checks={
            "area_ge_90pct":ratio>=0.90,
            "final16_backlog_area":a25["final16_total_backlog_area"]<=1.25*a0["final16_total_backlog_area"],
            "final_backlog":a25["backlog"]<=1.25*a0["backlog"],
            "ops":a25["operations_per_correct_completion"] is not None and a0["operations_per_correct_completion"] not in (None,0) and a25["operations_per_correct_completion"]<=1.25*a0["operations_per_correct_completion"],
            "stream_noncollapse":stream_ok,
            "anchor_recovery_pair_plus8":ar0 is not None and ar25 is not None and ar25<=ar0+8,
            "demand_recovery_pair_plus8":dr0 is not None and dr25 is not None and dr25<=dr0+8,
            "lesion_inherited":lesion_ok,
            "incorrect_done_zero":a25["incorrect_done"]==0,
            "repair_integrity":a25["repair"]["repair_integrity"],
            "matching_integrity":(
                x["integrity"]["a0_duplicate_cell"] and
                x["integrity"]["a0_duplicate_request"] and
                x["integrity"]["a25_duplicate_cell"] and
                x["integrity"]["a25_duplicate_request"]
            ),
        }
        rows.append({
            "replicate":x["manifest"]["replicate"],
            "area_ratio":ratio,
            "checks":checks,
            "pass":all(checks.values()),
            "recovery":{
                "a0_demand":dr0,"a25_demand":dr25,
                "a0_anchor":ar0,"a25_anchor":ar25,
                "a0_lesion":a0["events"]["lesion_recovery_latency"],
                "a25_lesion":lesion_lat,
            },
        })
    med=float(np.median(np.asarray(ratios,dtype=float))) if ratios else None
    ueval=sum(x["causal"]["u_evaluations"] for x in feasible)
    utv=sum(x["causal"]["u_nonzero_tv"] for x in feasible)
    udiff=sum(x["causal"]["u_realized_differences"] for x in feasible)
    heval=sum(x["causal"]["h_evaluations"] for x in feasible)
    hdelta=sum(x["causal"]["h_nonzero_delta"] for x in feasible)
    hdiff=sum(x["causal"]["h_realized_differences"] for x in feasible)
    causal=ueval>0 and utv>0 and udiff>0
    h_teacher=(hdelta==0 and hdiff==0)
    coverage=len(feasible)>=8
    positive=coverage and causal and h_teacher and bool(rows) and all(r["pass"] for r in rows) and med is not None and med>=0.95
    return {
        "LU2L_L1_LEARNED_U_TRANSFER":bool(positive),
        "baseline_feasible_count":len(feasible),
        "evidence_coverage_pass":coverage,
        "causal":bool(causal),
        "h_teacher_preserved":bool(h_teacher),
        "median_area_ratio":med,
        "per_replicate":rows,
        "causal_totals":{
            "u_evaluations":ueval,
            "u_nonzero_tv":utv,
            "u_realized_differences":udiff,
            "h_evaluations":heval,
            "h_nonzero_delta":hdelta,
            "h_realized_differences":hdiff,
        },
        "descriptive":{
            "a0_expired_total":sum(x["a0"]["expired"] for x in sweep),
            "a25_expired_total":sum(x["a25"]["expired"] for x in sweep),
            "a0_repair_reaching_egress":sum(x["a0"]["repair"]["corruptions_reaching_egress"] for x in sweep),
            "a25_repair_reaching_egress":sum(x["a25"]["repair"]["corruptions_reaching_egress"] for x in sweep),
            "state_divergence_epochs_total":sum(x["causal"]["state_divergence_epochs"] for x in sweep),
            "first_divergence_epochs":[x["causal"]["first_divergence_epoch"] for x in sweep],
            "u_mean_tv":[x["causal"]["u_mean_tv"] for x in sweep],
        },
    }

def mechanical_gate():
    global _PRIMARY_MANIFEST_CALLS
    before_calls=_PRIMARY_MANIFEST_CALLS
    m=mechanical_manifest()
    validate_manifest(m)
    fixture=g.stage_repair_fixture()
    csfix=g.cs_fcfs_echo_teacher_parity_fixture(m)
    call_states=g.learned_call_scope_fixture(m)
    rng_before=torch.random.get_rng_state().clone()
    pair=_with_l1_pair(m)
    rng_after=torch.random.get_rng_state().clone()
    weight_sha=hashlib.sha256(base._weights_bytes()).hexdigest()
    learned_scope_ok=bool(call_states) and set(call_states)<=set(("H","U")) and not (set(call_states)&set(("C","S","FC","FS")))
    primary_source=inspect.getsource(primary_manifest)
    probes={
        "exact_v02_parent":base.PARENT_V02==PARENT_V02 and g.PARENT_V02==PARENT_V02,
        "exact_lu1e_weight_sha":weight_sha==WEIGHT_SHA,
        "alpha_exact_025":g.ALPHA==ALPHA==0.25,
        "u_a0_exact_teacher_one_step":g.one_step_parity(m),
        "u_a25_exact_convex_blend":g.blend_fixture(m),
        "h_teacher_exact":pair["causal"]["h_nonzero_delta"]==0 and pair["causal"]["h_realized_differences"]==0,
        "cs_fcfs_teacher_exact":csfix["equal"] and csfix["learned_calls"]==[],
        "echo_phase_teacher_parity":csfix["equal"] and csfix["nonzero_echo_exercised"],
        "learned_authority_call_scope_hu_only":learned_scope_ok,
        "obs_v1_unchanged":base.a.INPUT_WIDTH==70,
        "task2_stage_order_no_skip":fixture["stage_order_ok"],
        "verify_repair_immutable_provenance":fixture["repair_ok"] and fixture["immutable_provenance_unchanged"],
        "load_one_exact":len(m["arrivals"])==160 and all(Counter(x["t"] for x in m["arrivals"])[t]==1 for t in range(160)),
        "expiry_32":p.EXPIRY==32,
        "no_model_rng":torch.equal(rng_before,rng_after),
        "paired_transition_variates_common":g.common_rng_fixture(m),
        "no_task_fields_in_learned_signature":base._learned.__code__.co_varnames[:base._learned.__code__.co_argcount]==("i","states","bpre","lc12","ls12","timers","q_prev","q_prev_side","lc3","ls3"),
        "d2_exact":p.D==2,
        "no_pool_exact":g.no_pool_fixture(),
        "g5_full_off":m["g5_full"] is False,
        "fresh_namespace_source_bound":"LU2L-TASK2-L1-A25-TRANSFER|" in primary_source and "lu2lf1" in primary_source,
        "no_primary_manifest_derived_in_mechanical_gate":_PRIMARY_MANIFEST_CALLS==before_calls,
        "mechanical_zero_incorrect_done":pair["a0"]["incorrect_done"]==0 and pair["a25"]["incorrect_done"]==0,
        "mechanical_matching_integrity":all(pair["integrity"][q] for q in ("a0_duplicate_cell","a0_duplicate_request","a25_duplicate_cell","a25_duplicate_request")),
    }
    return {
        "schema":1,
        "probes":probes,
        "all_pass":all(probes.values()),
        "weight_sha256":weight_sha,
        "learned_call_states":call_states,
        "fixture":fixture,
        "mechanical_summary":{
            "a0":pair["a0"],
            "a25":pair["a25"],
            "causal":pair["causal"],
        },
        "runtime":{"python":sys.version.split()[0],"numpy":np.__version__,"torch":torch.__version__},
    }

def run_sweep(ms):
    if len(ms)!=REPLICATES:
        raise AssertionError("need ten manifests")
    out=[]
    for m in ms:
        validate_manifest(m)
        out.append(_with_l1_pair(m))
    return out

def open_duplicate(path1,path2):
    b1=Path(path1).read_bytes(); b2=Path(path2).read_bytes()
    if b1!=b2:
        raise RuntimeError("LU2L duplicate primary mismatch")
    sweep=json.loads(b1.decode())
    return {
        "duplicate":{"byte_identical":True,"bytes":len(b1),"sha256":hashlib.sha256(b1).hexdigest()},
        "qualification":qualification(sweep),
        "sweep":sweep,
    }

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
    raise SystemExit("usage: mechanical OUT | manifests LU2LF1 OUT | sweep MANIFESTS OUT | open SWEEP1 SWEEP2 OUT")

if __name__=="__main__":
    main()

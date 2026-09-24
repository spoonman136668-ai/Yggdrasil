#!/usr/bin/env python3
import hashlib, json, math, sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch

import lu2t_task4_exact_parent_feasibility_v1 as t

g=t.g
p=t.p
base=t.base

PREREG_LU2U="d4149a448eaef8e59b185a3abc977ea73494a51f"
PARENT_LU2T_CLOSURE="bca682d103d70db87b929c7cc09e246f141502ed"
PARENT_LU2TF1="dcdac04ed1fed5ce1fdfc294f133125b6d26cb0e"
PARENT_LU2S_CLOSURE="be87f2ec48859d4b43f50eea136f2801854d1d5e"
PARENT_V02=t.PARENT_V02
WEIGHT_SHA="b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023"
ALPHA=0.25
REPLICATES=10
_PRIMARY_MANIFEST_CALLS=0

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()

def manifest_identity(m):
    x=dict(m); x.pop("manifest_sha256",None)
    return hashlib.sha256(canonical(x)).hexdigest()

def derive_programs(lu2uf1,replicate):
    if not isinstance(lu2uf1,str) or len(lu2uf1)!=40: raise ValueError("freeze sha")
    if replicate not in range(1,REPLICATES+1): raise ValueError(replicate)
    used=set(); out={}
    for stream in ("C","S"):
        out[stream]={}
        for stage in ("A","B","C","D"):
            counter=0
            while True:
                material=f"LU2U-TASK4-L1-A25|{lu2uf1}|{replicate}|{stream}|{stage}|{counter}"
                cand=int.from_bytes(hashlib.sha256(material.encode()).digest()[:2],"big")
                counter+=1
                if not t.valid_program(cand) or cand in used: continue
                used.add(cand); out[stream][stage]=cand; break
    return out

def _manifest(seed,programs,kind,replicate,lu2uf1,namespace):
    arrivals=t.make_arrivals(seed,programs)
    m={
        "kind":kind,"seed":seed,"replicate":replicate,"lu2uf1":lu2uf1,
        "lu2u_prereg_commit":PREREG_LU2U,"lu2u_seed_namespace":namespace,
        "parent_lu2t_closure":PARENT_LU2T_CLOSURE,"parent_lu2tf1":PARENT_LU2TF1,
        "parent_lu2s_closure":PARENT_LU2S_CLOSURE,"parent_v02":PARENT_V02,
        "canonical_weight_sha256":WEIGHT_SHA,"alpha":ALPHA,
        "programs":programs,"arrivals":arrivals,
        "corrupt_ids":[x["rid"] for x in arrivals if p.u01("LU2U-TASK4-CORRUPT",seed,x["rid"])<0.05],
        "lesion":sorted(p.lesion_set(seed)),
        "anchors0":p.anchors_for(seed,0),"anchors4":p.anchors_for(seed,128),
        "n":p.N,"t":p.T,"d":p.D,"r_task":p.R_TASK,"route_edges":6,
        "g5_full":False,"requests_per_epoch":1,"process_ops_per_request":4,
    }
    m["manifest_sha256"]=manifest_identity(m)
    return m

def mechanical_manifest():
    seed="LU2U-MECHANICAL-TASK4-A25-R1"
    return _manifest(seed,t.mechanical_programs(),"LU2U_MECHANICAL",0,None,seed)

def primary_manifest(lu2uf1,replicate):
    global _PRIMARY_MANIFEST_CALLS
    _PRIMARY_MANIFEST_CALLS+=1
    ns=f"LU2U-TASK4-L1-A25|{lu2uf1}|{replicate}"
    seed=hashlib.sha256(ns.encode()).hexdigest()[:32]
    return _manifest(seed,derive_programs(lu2uf1,replicate),"LU2U_PRIMARY",replicate,lu2uf1,ns)

def primary_manifests(lu2uf1):
    return [primary_manifest(lu2uf1,k) for k in range(1,REPLICATES+1)]

def validate_manifest(m):
    if m["manifest_sha256"]!=manifest_identity(m): raise AssertionError("manifest hash")
    if m["lu2u_prereg_commit"]!=PREREG_LU2U: raise AssertionError("prereg")
    if (m["parent_lu2t_closure"],m["parent_lu2tf1"],m["parent_lu2s_closure"],m["parent_v02"])!=(PARENT_LU2T_CLOSURE,PARENT_LU2TF1,PARENT_LU2S_CLOSURE,PARENT_V02):
        raise AssertionError("lineage")
    if m["canonical_weight_sha256"]!=WEIGHT_SHA or m["alpha"]!=ALPHA: raise AssertionError("weight/alpha")
    if base.PARENT_V02!=PARENT_V02: raise AssertionError("v02")
    if (m["n"],m["t"],m["d"],m["r_task"],m["route_edges"],m["g5_full"])!=(64,160,2,2,6,False): raise AssertionError("substrate")
    if m["requests_per_epoch"]!=1 or m["process_ops_per_request"]!=4: raise AssertionError("task/load")
    if p.EXPIRY!=32: raise AssertionError("expiry")
    if len(m["arrivals"])!=160: raise AssertionError("arrivals")
    by=Counter(x["t"] for x in m["arrivals"])
    if any(by[k]!=1 for k in range(160)): raise AssertionError("one per epoch")
    expected={(0,"C"):16,(0,"S"):16,(1,"C"):24,(1,"S"):8,(2,"C"):8,(2,"S"):24,(3,"C"):16,(3,"S"):16,(4,"C"):16,(4,"S"):16}
    sc=Counter((p.phase_of(x["t"]),x["stream"]) for x in m["arrivals"])
    if any(sc[k]!=v for k,v in expected.items()): raise AssertionError("phase schedule")
    vals=[m["programs"][s][st] for s in ("C","S") for st in ("A","B","C","D")]
    if len(set(vals))!=8 or not all(t.valid_program(v) for v in vals): raise AssertionError("programs")
    if m["arrivals"]!=t.make_arrivals(m["seed"],m["programs"]): raise AssertionError("arrivals")
    if m["corrupt_ids"]!=[x["rid"] for x in m["arrivals"] if p.u01("LU2U-TASK4-CORRUPT",m["seed"],x["rid"])<0.05]: raise AssertionError("corruption")
    if m["lesion"]!=sorted(p.lesion_set(m["seed"])) or len(m["lesion"])!=8: raise AssertionError("lesion")
    if m["anchors0"]!=p.anchors_for(m["seed"],0) or m["anchors4"]!=p.anchors_for(m["seed"],128): raise AssertionError("anchors")
    if m["kind"]=="LU2U_PRIMARY":
        rep=m["replicate"]; freeze=m["lu2uf1"]
        ns=f"LU2U-TASK4-L1-A25|{freeze}|{rep}"
        if m["lu2u_seed_namespace"]!=ns or m["seed"]!=hashlib.sha256(ns.encode()).hexdigest()[:32]: raise AssertionError("seed")
        if m["programs"]!=derive_programs(freeze,rep): raise AssertionError("programs")
    elif m["kind"]=="LU2U_MECHANICAL":
        if m["replicate"]!=0 or m["lu2uf1"] is not None: raise AssertionError("mechanical")
    else: raise AssertionError("kind")
    return True

def _run_world(m,mode,instrument=True):
    validate_manifest(m)
    registry={}; detected_epoch={}
    programs=m["programs"]
    old=(g.Task2Request,g.task2_op,g.do_operation,g.expected_pair,g.validate_manifest,g.REQUESTS_PER_EPOCH)
    def factory(rid,stream,created,bits,program_a,program_b,pos,scheduled_corrupt=False):
        r=t.Task4Request(rid,stream,created,bits,program_a,program_b,programs[stream]["C"],programs[stream]["D"],pos,scheduled_corrupt)
        registry[rid]=r
        return r
    def op(seed,tick,cell,opname,r,trace):
        before=r.stage
        t.do_operation4(seed,tick,cell,opname,r,trace)
        if instrument and opname=="VERIFY" and before=="AT_EGRESS" and r.stage=="REPAIR_PENDING":
            detected_epoch.setdefault(r.rid,tick)
    g.Task2Request=factory; g.task2_op=t.task4_op; g.do_operation=op; g.expected_pair=t.expected_pair_compat
    g.validate_manifest=validate_manifest; g.REQUESTS_PER_EPOCH=1
    try:
        result,state_history,telemetry=g.run_world(m,mode)
    finally:
        g.Task2Request,g.task2_op,g.do_operation,g.expected_pair,g.validate_manifest,g.REQUESTS_PER_EPOCH=old
    return result,state_history,telemetry,registry,detected_epoch

def run_pair(m):
    validate_manifest(m)
    a0,s0,_,reg0,det0=_run_world(m,"U_A0",True)
    a25,s25,tel,reg25,det25=_run_world(m,"U_A25",True)
    diffs=[i for i,(x,y) in enumerate(zip(s0,s25)) if x!=y]
    return {
        "manifest":m,
        "a0":g.compact(a0),"a25":g.compact(a25),
        "maturity":{"a0":t.maturity_summary(m,reg0,det0),"a25":t.maturity_summary(m,reg25,det25)},
        "causal":{
            "u_evaluations":tel["u_evaluations"],"u_nonzero_tv":tel["u_nonzero_tv"],
            "u_realized_differences":tel["u_realized_differences"],"u_mean_tv":tel["u_mean_tv"],
            "h_evaluations":tel["h_evaluations"],"h_nonzero_delta":tel["h_nonzero_delta"],
            "h_realized_differences":tel["h_realized_differences"],
            "first_divergence_epoch":diffs[0] if diffs else None,
            "state_divergence_epochs":len(diffs),
        },
        "integrity":{
            "a0_duplicate_cell":a0["matching_duplicate_cell"]==0,
            "a0_duplicate_request":a0["matching_duplicate_request"]==0,
            "a25_duplicate_cell":a25["matching_duplicate_cell"]==0,
            "a25_duplicate_request":a25["matching_duplicate_request"]==0,
        }
    }

def baseline_feasible(row):
    r=row["a0"]
    return (
        all(r["phase"][str(ph)]["correct_done"]>=1 for ph in range(5))
        and r["incorrect_done"]==0
        and all(r["stream_total"][s]>=1 for s in ("C","S"))
        and row["maturity"]["a0"]["pass"]
        and r["operations_per_correct_completion"] is not None and math.isfinite(r["operations_per_correct_completion"])
        and row["integrity"]["a0_duplicate_cell"] and row["integrity"]["a0_duplicate_request"]
        and r["events"]["demand_reversal_recovery_latency"] is not None and r["events"]["demand_reversal_recovery_latency"]<=8
        and r["events"]["anchor_rotation_recovery_latency"] is not None and r["events"]["anchor_rotation_recovery_latency"]<=8
        and r["events"]["lesion_recovery_latency"] is not None and r["events"]["lesion_recovery_latency"]<=8
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
            "lesion_recovery":lesion_ok,
            "incorrect_done_zero":a25["incorrect_done"]==0,
            "maturity_repair_integrity":row["maturity"]["a25"]["pass"],
            "matching_integrity":all(row["integrity"][k] for k in ("a0_duplicate_cell","a0_duplicate_request","a25_duplicate_cell","a25_duplicate_request")),
        }
        rows.append({"replicate":row["manifest"]["replicate"],"area_ratio":ratio,"checks":checks,"pass":all(checks.values()),
                     "recovery":{"a0_demand":dr0,"a25_demand":dr25,"a0_anchor":ar0,"a25_anchor":ar25,"a0_lesion":lr0,"a25_lesion":lr25}})
    med=float(np.median(np.asarray(ratios,dtype=float))) if ratios else None
    ueval=sum(r["causal"]["u_evaluations"] for r in feasible)
    utv=sum(r["causal"]["u_nonzero_tv"] for r in feasible)
    udiff=sum(r["causal"]["u_realized_differences"] for r in feasible)
    hdelta=sum(r["causal"]["h_nonzero_delta"] for r in feasible)
    hdiff=sum(r["causal"]["h_realized_differences"] for r in feasible)
    coverage=len(feasible)>=8; causal=ueval>0 and utv>0 and udiff>0; h_teacher=hdelta==0 and hdiff==0
    positive=coverage and causal and h_teacher and bool(rows) and all(r["pass"] for r in rows) and med is not None and med>=0.95
    return {
        "LU2U_TASK4_LEARNED_U_TRANSFER":bool(positive),
        "baseline_feasible_count":len(feasible),"evidence_coverage_pass":coverage,
        "causal":bool(causal),"h_teacher_preserved":bool(h_teacher),"median_area_ratio":med,
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
            "u_mean_tv":[r["causal"]["u_mean_tv"] for r in sweep],
        }
    }

def mechanical_gate():
    global _PRIMARY_MANIFEST_CALLS
    before=_PRIMARY_MANIFEST_CALLS
    m=mechanical_manifest(); validate_manifest(m)
    stage=t.stage_repair_fixture(); maturity=t.maturity_fixture()
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
    pair1=run_pair(m)
    rng1=torch.random.get_rng_state().clone()
    pair2=run_pair(m)
    b1=canonical(pair1); b2=canonical(pair2)
    probes={
        "exact_lu2t_task4_semantics":t.PARENT_V02==PARENT_V02 and stage["ordered"] and stage["stage_d"],
        "exact_canonical_weight_sha":weight_sha==WEIGHT_SHA,
        "alpha_exact_025":g.ALPHA==ALPHA==0.25,
        "u_a0_exact_teacher_one_step":bool(one_step),
        "u_a25_exact_convex_blend":bool(blend),
        "h_teacher_exact":pair1["causal"]["h_nonzero_delta"]==0 and pair1["causal"]["h_realized_differences"]==0,
        "cs_fcfs_teacher_exact":bool(csfix["equal"]) and csfix["learned_calls"]==[],
        "obs_v1_unchanged":base.a.INPUT_WIDTH==70,
        "one_request_per_epoch":len(m["arrivals"])==160 and all(Counter(x["t"] for x in m["arrivals"])[i]==1 for i in range(160)),
        "four_stage_ordering":stage["ordered"] and stage["b_depends_on_a"] and stage["c_depends_on_b"] and stage["d_depends_on_c"],
        "four_stage_repair_reverify":stage["repaired_all_four"] and stage["immutable_provenance"] and stage["independent_reverify"] and stage["done_after_reverify"],
        "maturity_contract_exact":t.MATURE_MAX_DETECTION==156 and all(maturity.values()),
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
            "learned_call_states":calls,"stage_fixture":stage,"maturity_fixture":maturity,
            "pair_bytes":len(b1),"pair_sha256":hashlib.sha256(b1).hexdigest(),"mechanical_pair":pair1}

def run_sweep(ms):
    if len(ms)!=10: raise AssertionError("need ten manifests")
    return [run_pair(m) for m in ms]

def open_duplicate(path1,path2):
    b1=Path(path1).read_bytes(); b2=Path(path2).read_bytes()
    if b1!=b2: raise RuntimeError("LU2U duplicate mismatch")
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
    raise SystemExit("usage: mechanical OUT | manifests LU2UF1 OUT | sweep MANIFESTS OUT | open SWEEP1 SWEEP2 OUT")

if __name__=="__main__":
    main()

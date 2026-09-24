#!/usr/bin/env python3
import hashlib, json, math, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path

import lu2g_second_task_compositional_service_transfer_v1 as frozen

g=frozen.g
p=g.p

PREREG_LU2I="259e0719aed87c2469f408d0055d59a563887c54"
PARENT_LU2H="dba00160c1e783af47c6d43b8d695b608c171736"
PARENT_LU2G="1fcfef885ca9bd8c3219333965d90cc9cc4a60e9"
PARENT_LU2GF1="e9a01aa97587fc97dde073cb2a6a35ad141006cd"
REQUESTS_PER_EPOCH=2
PROCESS_OPS_PER_REQUEST=2
REPLICATES=10
EXPIRY=32

def manifest_identity(m):
    x=dict(m); x.pop("manifest_sha256",None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def arrival_streams_l2(t):
    ph=p.phase_of(t)
    if ph in (0,3,4):
        return ("C","S")
    if ph==1:
        return ("C","C") if (t-ph*32)%2==0 else ("C","S")
    return ("S","S") if (t-ph*32)%2==0 else ("C","S")

def make_arrivals_l2(seed,programs):
    arrivals=[]; rid=0
    for t in range(p.T):
        for stream in arrival_streams_l2(t):
            bits=tuple((p.h64("LU2I-TASK2-BITS",seed,rid,k)>>k)&1 for k in range(4))
            arrivals.append({
                "rid":rid,"t":t,"stream":stream,"bits":bits,
                "program_a":programs[stream]["A"],"program_b":programs[stream]["B"],
            })
            rid+=1
    assert rid==p.T*REQUESTS_PER_EPOCH==320
    return arrivals

def derive_programs_l2(lu2if1,replicate):
    if not isinstance(lu2if1,str) or len(lu2if1)!=40: raise ValueError("freeze sha")
    if replicate not in range(1,REPLICATES+1): raise ValueError(replicate)
    used=set(); out={}
    for stream in ("C","S"):
        out[stream]={}
        for stage in ("A","B"):
            counter=0
            while True:
                material=f"LU2I-TASK2-L2|{lu2if1}|{replicate}|{stream}|{stage}|{counter}"
                cand=int.from_bytes(hashlib.sha256(material.encode()).digest()[:2],"big")
                counter+=1
                if not g.valid_program(cand) or cand in used: continue
                used.add(cand); out[stream][stage]=cand; break
    return out

def mechanical_programs():
    used=[]; counter=0
    while len(used)<4:
        cand=int.from_bytes(hashlib.sha256(f"LU2I-MECHANICAL-PROGRAM|{counter}".encode()).digest()[:2],"big")
        counter+=1
        if not g.valid_program(cand) or cand in used: continue
        used.append(cand)
    return {"C":{"A":used[0],"B":used[1]},"S":{"A":used[2],"B":used[3]}}

def base_manifest(seed,programs,kind,replicate,lu2if1,namespace):
    arrivals=make_arrivals_l2(seed,programs)
    m={
        "kind":kind,"seed":seed,"replicate":replicate,"lu2if1":lu2if1,
        "lu2i_prereg_commit":PREREG_LU2I,
        "lu2i_seed_namespace":namespace,
        "parent_lu2h":PARENT_LU2H,"parent_lu2g":PARENT_LU2G,"parent_lu2gf1":PARENT_LU2GF1,
        "parent_v02":g.PARENT_V02,"parent_lu1ef1":g.PARENT_LU1EF1,
        "parent_lu2ef1":g.PARENT_LU2EF1,"parent_lu2f":g.PARENT_LU2F,
        "programs":programs,"arrivals":arrivals,
        "corrupt_ids":[x["rid"] for x in arrivals if p.u01("LU2I-TASK2-CORRUPT",seed,x["rid"])<0.05],
        "lesion":sorted(p.lesion_set(seed)),
        "anchors0":p.anchors_for(seed,0),"anchors4":p.anchors_for(seed,128),
        "n":p.N,"t":p.T,"d":p.D,"r_task":p.R_TASK,"route_edges":6,"g5_full":False,
        "requests_per_epoch":REQUESTS_PER_EPOCH,
        "process_ops_per_request":PROCESS_OPS_PER_REQUEST,
        "expiry_epochs":p.EXPIRY,
    }
    m["manifest_sha256"]=manifest_identity(m)
    return m

def mechanical_manifest():
    seed=hashlib.sha256(b"LU2I-MECHANICAL-L2").hexdigest()[:32]
    return base_manifest(seed,mechanical_programs(),"LU2I_MECHANICAL",0,None,"LU2I-MECHANICAL-L2")

def primary_manifest(lu2if1,k):
    if not isinstance(lu2if1,str) or len(lu2if1)!=40: raise ValueError("freeze sha")
    if k not in range(1,REPLICATES+1): raise ValueError(k)
    ns=f"LU2I-TASK2-L2|{lu2if1}|{k}"
    seed=hashlib.sha256(ns.encode()).hexdigest()[:32]
    return base_manifest(seed,derive_programs_l2(lu2if1,k),"LU2I_PRIMARY",k,lu2if1,ns)

def primary_manifests(lu2if1):
    return [primary_manifest(lu2if1,k) for k in range(1,REPLICATES+1)]

def validate_manifest_l2(m):
    if m["manifest_sha256"]!=manifest_identity(m): raise AssertionError("manifest hash")
    if m["lu2i_prereg_commit"]!=PREREG_LU2I: raise AssertionError("prereg")
    if m["parent_lu2h"]!=PARENT_LU2H or m["parent_lu2g"]!=PARENT_LU2G or m["parent_lu2gf1"]!=PARENT_LU2GF1:
        raise AssertionError("lineage")
    if m["parent_v02"]!=g.PARENT_V02 or m["parent_lu1ef1"]!=g.PARENT_LU1EF1:
        raise AssertionError("frozen parent")
    if m["parent_lu2ef1"]!=g.PARENT_LU2EF1 or m["parent_lu2f"]!=g.PARENT_LU2F:
        raise AssertionError("frozen lineage")
    if (m["n"],m["t"],m["d"],m["r_task"],m["route_edges"],m["g5_full"])!=(64,160,2,2,6,False):
        raise AssertionError("substrate")
    if m["requests_per_epoch"]!=2 or m["process_ops_per_request"]!=2 or m["expiry_epochs"]!=32:
        raise AssertionError("load/expiry")
    if len(m["arrivals"])!=320: raise AssertionError("arrivals")
    by_epoch=Counter(x["t"] for x in m["arrivals"])
    if any(by_epoch[t]!=2 for t in range(160)): raise AssertionError("two per epoch")
    expected={(0,"C"):32,(0,"S"):32,(1,"C"):48,(1,"S"):16,(2,"C"):16,(2,"S"):48,(3,"C"):32,(3,"S"):32,(4,"C"):32,(4,"S"):32}
    counts=Counter((p.phase_of(x["t"]),x["stream"]) for x in m["arrivals"])
    if any(counts[k]!=v for k,v in expected.items()): raise AssertionError(("phase schedule",counts))
    vals=[m["programs"][s][st] for s in ("C","S") for st in ("A","B")]
    if len(set(vals))!=4 or not all(g.valid_program(x) for x in vals): raise AssertionError("programs")
    if m["arrivals"]!=make_arrivals_l2(m["seed"],m["programs"]): raise AssertionError("arrival binding")
    if m["corrupt_ids"]!=[x["rid"] for x in m["arrivals"] if p.u01("LU2I-TASK2-CORRUPT",m["seed"],x["rid"])<0.05]:
        raise AssertionError("corrupt binding")
    if m["lesion"]!=sorted(p.lesion_set(m["seed"])): raise AssertionError("lesion")
    if m["anchors0"]!=p.anchors_for(m["seed"],0) or m["anchors4"]!=p.anchors_for(m["seed"],128):
        raise AssertionError("anchors")
    if m["kind"]=="LU2I_PRIMARY":
        k=m["replicate"]; freeze=m["lu2if1"]; ns=f"LU2I-TASK2-L2|{freeze}|{k}"
        if m["lu2i_seed_namespace"]!=ns or m["seed"]!=hashlib.sha256(ns.encode()).hexdigest()[:32]:
            raise AssertionError("primary seed")
        if m["programs"]!=derive_programs_l2(freeze,k): raise AssertionError("primary programs")
    return True

class Patch:
    def __enter__(self):
        self.old_req=g.REQUESTS_PER_EPOCH
        self.old_validate=g.validate_manifest
        g.REQUESTS_PER_EPOCH=2
        g.validate_manifest=validate_manifest_l2
        return self
    def __exit__(self,*exc):
        g.REQUESTS_PER_EPOCH=self.old_req
        g.validate_manifest=self.old_validate

def pct(xs,q):
    if not xs: return None
    ys=sorted(xs); i=max(0,min(len(ys)-1,math.ceil(q*len(ys))-1)); return ys[i]

def stat(xs):
    if not xs: return {"count":0,"mean":None,"median":None,"p90":None,"max":None}
    return {"count":len(xs),"mean":sum(xs)/len(xs),"median":statistics.median(xs),"p90":pct(xs,.90),"max":max(xs)}

def recovery_diag(epoch_done,event):
    phase0_rate=sum(epoch_done[16:32])/(REQUESTS_PER_EPOCH*16)
    target=.90*phase0_rate
    rows=[]
    for k in range(9):
        lo=event+k; hi=min(p.T,lo+4)
        if hi<=lo: continue
        rows.append({"latency":k,"rate":sum(epoch_done[lo:hi])/(REQUESTS_PER_EPOCH*(hi-lo)),"window":[lo,hi]})
    best=max(rows,key=lambda x:(x["rate"],-x["latency"])) if rows else None
    return {"target_rate":target,"best_rate":None if best is None else best["rate"],
            "best_latency":None if best is None else best["latency"],
            "best_window":None if best is None else best["window"],
            "old_target_reached":bool(best is not None and best["rate"]>=target)}

def observe_world(m):
    refs={}; events=defaultdict(list)
    OldRequest=g.Task2Request; old_do=g.do_operation
    def factory(*args,**kwargs):
        r=OldRequest(*args,**kwargs); refs[r.rid]=r; return r
    def observe_do(seed,t,cell,op,r,trace):
        before=r.stage; out=old_do(seed,t,cell,op,r,trace); after=r.stage
        events[r.rid].append({"t":t,"op":op,"before":before,"after":after}); return out
    g.Task2Request=factory; g.do_operation=observe_do
    try:
        with Patch():
            result,_,telemetry=g.run_world(m,"U_A0")
    finally:
        g.Task2Request=OldRequest; g.do_operation=old_do

    pre=[]; s_pa=[]; pa_pb=[]; pb_r=[]; routes_wait=[]; rv=[]
    no_verify=[]; no_repair=[]; repaired_no_reverify=[]; horizon=[]
    for rid,r in refs.items():
        ev=events.get(rid,[])
        senses=[x["t"] for x in ev if x["op"]=="SENSE"]
        procs=[x["t"] for x in ev if x["op"]=="PROCESS"]
        routes=[x["t"] for x in ev if x["op"]=="ROUTE"]
        verifies=[x for x in ev if x["op"]=="VERIFY"]
        repairs=[x["t"] for x in ev if x["op"]=="REPAIR"]
        sense=senses[0] if senses else None; pa=procs[0] if len(procs)>0 else None; pb=procs[1] if len(procs)>1 else None
        fv=verifies[0]["t"] if verifies else None
        failed=next((x["t"] for x in verifies if x["after"]=="REPAIR_PENDING"),None)
        repair=repairs[0] if repairs else None
        post=next((x["t"] for x in verifies if repair is not None and x["t"]>repair),None)
        if sense is not None: pre.append(sense-r.created)
        if sense is not None and pa is not None: s_pa.append(max(0,pa-sense-1))
        if pa is not None and pb is not None: pa_pb.append(max(0,pb-pa-1))
        if pb is not None and routes: pb_r.append(max(0,routes[0]-pb-1))
        routes_wait.extend(max(0,b-a-1) for a,b in zip(routes,routes[1:]))
        if routes and fv is not None: rv.append(max(0,fv-routes[-1]-1))
        if r.reached_egress_after_corrupt and r.first_egress_epoch is not None and r.created+EXPIRY-r.first_egress_epoch<=1:
            no_verify.append(rid)
        if failed is not None and r.created+EXPIRY-failed<=1: no_repair.append(rid)
        if repair is not None and post is None and r.expired_epoch is not None: repaired_no_reverify.append(rid)
        if r.unfinished() and (r.stage=="VERIFIED" or (r.repaired and r.stage=="AT_EGRESS")): horizon.append(rid)

    diag={
        "waits":{"pre_sense":stat(pre),"sense_to_process_a_extra":stat(s_pa),"process_a_to_process_b_extra":stat(pa_pb),
                 "process_b_to_first_route_extra":stat(pb_r),"between_route_hops_extra":stat(routes_wait),
                 "last_route_to_first_verify_extra":stat(rv)},
        "deadline":{"no_epoch_for_initial_verify":len(no_verify),"no_epoch_for_repair":len(no_repair),
                    "repaired_expired_before_reverify":len(repaired_no_reverify),"horizon_censored":len(horizon)},
        "recovery":{"demand_reversal":recovery_diag(result["epoch_done"],64),
                    "lesion":recovery_diag(result["epoch_done"],96),
                    "anchor_rotation":recovery_diag(result["epoch_done"],128)}
    }
    return result,diag,telemetry

def baseline_feasible_result(r):
    return (all(r["phase"][str(ph)]["correct_done"]>=1 for ph in range(5)) and
            r["incorrect_done"]==0 and all(r["stream_total"][s]>=1 for s in ("C","S")) and
            r["repair"]["repair_integrity"] and r["operations_per_correct_completion"] is not None and
            math.isfinite(r["operations_per_correct_completion"]) and
            r["matching_duplicate_cell"]==0 and r["matching_duplicate_request"]==0)

def run_sweep(manifests):
    if len(manifests)!=REPLICATES: raise AssertionError("need ten manifests")
    rows=[]
    for m in manifests:
        validate_manifest_l2(m)
        r,d,tel=observe_world(m)
        rows.append({"manifest":m,"a0":g.compact(r),"diagnostic":d,
                     "baseline_feasible":baseline_feasible_result(r),
                     "telemetry_none":tel is None})
    feasible=sum(x["baseline_feasible"] for x in rows)
    zero_wrong=all(x["a0"]["incorrect_done"]==0 for x in rows)
    return {"rows":rows,"summary":{"baseline_feasible_count":feasible,
            "zero_incorrect_done_all":zero_wrong,
            "LU2I_L2_BASELINE_CALIBRATED":bool(feasible>=8 and zero_wrong),
            "requests_per_epoch":2,"expiry_epochs":32}}

def mechanical_gate():
    m=mechanical_manifest(); validate_manifest_l2(m)
    r,d,tel=observe_world(m)
    counts=Counter((p.phase_of(x["t"]),x["stream"]) for x in m["arrivals"])
    probes={
        "prereg_identity":m["lu2i_prereg_commit"]==PREREG_LU2I,
        "parent_lu2gf1_identity":m["parent_lu2gf1"]==PARENT_LU2GF1,
        "two_requests_every_epoch":all(sum(x["t"]==t for x in m["arrivals"])==2 for t in range(160)),
        "phase0_balanced":counts[(0,"C")]==32 and counts[(0,"S")]==32,
        "phase1_three_to_one":counts[(1,"C")]==48 and counts[(1,"S")]==16,
        "phase2_one_to_three":counts[(2,"C")]==16 and counts[(2,"S")]==48,
        "phase3_balanced":counts[(3,"C")]==32 and counts[(3,"S")]==32,
        "phase4_balanced":counts[(4,"C")]==32 and counts[(4,"S")]==32,
        "expiry_32_unchanged":p.EXPIRY==32 and m["expiry_epochs"]==32,
        "two_process_ops_unchanged":m["process_ops_per_request"]==2,
        "task2_programs_valid":all(g.valid_program(m["programs"][s][st]) for s in ("C","S") for st in ("A","B")),
        "zero_incorrect_done":r["incorrect_done"]==0,
        "matching_integrity":r["matching_duplicate_cell"]==0 and r["matching_duplicate_request"]==0,
        "exact_parent_only_no_telemetry":tel is None,
        "no_learned_arm_executed":True,
    }
    return {"probes":probes,"all_pass":all(probes.values()),"mechanical_manifest":m,
            "mechanical_result":g.compact(r),"diagnostic":d}

def write(path,obj):
    Path(path).write_bytes(json.dumps(obj,sort_keys=True,separators=(",",":")).encode())

def main():
    if len(sys.argv)>=2 and sys.argv[1]=="mechanical":
        write(sys.argv[2],mechanical_gate()); return
    if len(sys.argv)>=2 and sys.argv[1]=="manifests":
        write(sys.argv[3],primary_manifests(sys.argv[2])); return
    if len(sys.argv)>=2 and sys.argv[1]=="sweep":
        ms=json.load(open(sys.argv[2],encoding="utf-8"))
        write(sys.argv[3],run_sweep(ms)); return
    raise SystemExit("usage: mechanical OUT | manifests LU2IF1 OUT | sweep MANIFESTS OUT")

if __name__=="__main__":
    main()

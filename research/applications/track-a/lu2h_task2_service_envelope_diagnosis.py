#!/usr/bin/env python3
import hashlib, json, math, statistics, sys
from collections import defaultdict
from pathlib import Path

import lu2g_second_task_compositional_service_transfer_v1 as frozen

g=frozen.g
LU2GF1="e9a01aa97587fc97dde073cb2a6a35ad141006cd"
BOUND_BUNDLE_SHA256="1c711199238d3a223c75262ca490a1dfb4e4eab34cceb64992e8f378b4ecfe78"
EXPIRY=32

def pct(xs,q):
    if not xs: return None
    ys=sorted(xs)
    i=max(0,min(len(ys)-1,math.ceil(q*len(ys))-1))
    return ys[i]

def stat(xs):
    if not xs:
        return {"count":0,"mean":None,"median":None,"p90":None,"max":None}
    return {
        "count":len(xs),
        "mean":sum(xs)/len(xs),
        "median":statistics.median(xs),
        "p90":pct(xs,.90),
        "max":max(xs),
    }

def max_recovery_rate(epoch_done,event,window=4,max_latency=8):
    vals=[]
    for k in range(max_latency+1):
        lo=event+k; hi=min(g.p.T,lo+window)
        if hi<=lo: continue
        vals.append({
            "latency":k,
            "rate":sum(epoch_done[lo:hi])/(g.REQUESTS_PER_EPOCH*(hi-lo)),
            "lo":lo,"hi":hi,
        })
    return max(vals,key=lambda x:(x["rate"],-x["latency"])) if vals else None

def observe_world(m):
    refs={}
    events=defaultdict(list)
    OldRequest=g.Task2Request
    old_do=g.do_operation

    def factory(*args,**kwargs):
        r=OldRequest(*args,**kwargs)
        refs[r.rid]=r
        return r

    def observe_do(seed,t,cell,op,r,trace):
        before=r.stage
        out=old_do(seed,t,cell,op,r,trace)
        after=r.stage
        events[r.rid].append({
            "t":t,"op":op,"before":before,"after":after,
            "pos":r.pos,
        })
        return out

    g.Task2Request=factory
    g.do_operation=observe_do
    try:
        result,_,_=g.run_world(m,"U_A0")
    finally:
        g.Task2Request=OldRequest
        g.do_operation=old_do

    pre_sense=[]; s_pa=[]; pa_pb=[]; pb_route=[]; between_route=[]; route_verify=[]
    first_verify_age=[]; first_verify_remaining=[]; failed_verify_remaining=[]
    no_initial_verify=[]; no_repair_epoch=[]; repaired_no_reverify_expiry=[]; horizon_censored=[]
    request_rows=[]

    for rid,r in sorted(refs.items()):
        ev=events.get(rid,[])
        senses=[x["t"] for x in ev if x["op"]=="SENSE"]
        procs=[x["t"] for x in ev if x["op"]=="PROCESS"]
        routes=[x["t"] for x in ev if x["op"]=="ROUTE"]
        verifies=[x for x in ev if x["op"]=="VERIFY"]
        repairs=[x["t"] for x in ev if x["op"]=="REPAIR"]
        sense=senses[0] if senses else None
        pa=procs[0] if len(procs)>=1 else None
        pb=procs[1] if len(procs)>=2 else None
        fv=verifies[0]["t"] if verifies else None
        failed=next((x["t"] for x in verifies if x["after"]=="REPAIR_PENDING"),None)
        repair=repairs[0] if repairs else None
        post_verify=next((x["t"] for x in verifies if repair is not None and x["t"]>repair),None)

        if sense is not None:
            pre_sense.append(sense-r.created)
        if sense is not None and pa is not None:
            s_pa.append(max(0,pa-sense-1))
        if pa is not None and pb is not None:
            pa_pb.append(max(0,pb-pa-1))
        if pb is not None and routes:
            pb_route.append(max(0,routes[0]-pb-1))
        for a,b in zip(routes,routes[1:]):
            between_route.append(max(0,b-a-1))
        if routes and fv is not None:
            route_verify.append(max(0,fv-routes[-1]-1))
        if fv is not None:
            first_verify_age.append(fv-r.created)
            first_verify_remaining.append(r.created+EXPIRY-fv)
        if failed is not None:
            rem=r.created+EXPIRY-failed
            failed_verify_remaining.append(rem)
            if rem<=1:
                no_repair_epoch.append(rid)

        if r.reached_egress_after_corrupt and r.first_egress_epoch is not None:
            rem_egress=r.created+EXPIRY-r.first_egress_epoch
            if rem_egress<=1:
                no_initial_verify.append(rid)

        if repair is not None and post_verify is None and r.expired_epoch is not None:
            repaired_no_reverify_expiry.append(rid)

        if r.unfinished():
            if r.stage=="VERIFIED" or (r.repaired and r.stage=="AT_EGRESS"):
                horizon_censored.append(rid)

        request_rows.append({
            "rid":rid,"created":r.created,"stage":r.stage,
            "sense":sense,"process_a":pa,"process_b":pb,
            "first_route":routes[0] if routes else None,
            "last_route":routes[-1] if routes else None,
            "route_count":len(routes),
            "first_verify":fv,"failed_first_verify":failed,
            "repair":repair,"post_repair_verify":post_verify,
            "done":r.done_epoch,"expired":r.expired_epoch,
            "scheduled_corrupt":bool(r.scheduled_corrupt),
            "corruption_applied":bool(r.corruption_applied),
            "reached_egress_after_corrupt":bool(r.reached_egress_after_corrupt),
            "detected":bool(r.detected),"repaired":bool(r.repaired),
        })

    phase0_rate=sum(result["epoch_done"][16:32])/(g.REQUESTS_PER_EPOCH*16)
    target=.90*phase0_rate
    recovery={}
    for name,event in (("demand_reversal",64),("lesion",96),("anchor_rotation",128)):
        best=max_recovery_rate(result["epoch_done"],event)
        recovery[name]={
            "target_rate":target,
            "best_rate":None if best is None else best["rate"],
            "best_latency":None if best is None else best["latency"],
            "best_window":None if best is None else [best["lo"],best["hi"]],
            "target_reached":bool(best is not None and best["rate"]>=target),
            "frozen_reported_latency":result["events"][name+"_recovery_latency"] if name!="anchor_rotation" else result["events"]["anchor_rotation_recovery_latency"],
        }

    return {
        "replicate":m["replicate"],
        "manifest_sha256":m["manifest_sha256"],
        "waits":{
            "pre_sense":stat(pre_sense),
            "sense_to_process_a_extra":stat(s_pa),
            "process_a_to_process_b_extra":stat(pa_pb),
            "process_b_to_first_route_extra":stat(pb_route),
            "between_route_hops_extra":stat(between_route),
            "last_route_to_first_verify_extra":stat(route_verify),
        },
        "first_verify":{
            "age":stat(first_verify_age),
            "remaining_lifetime":stat(first_verify_remaining),
            "failed_verify_remaining_lifetime":stat(failed_verify_remaining),
        },
        "deadline":{
            "corrupted_at_egress_no_epoch_for_initial_verify":len(no_initial_verify),
            "ids_no_epoch_for_initial_verify":no_initial_verify,
            "detected_no_epoch_for_repair":len(no_repair_epoch),
            "ids_no_epoch_for_repair":no_repair_epoch,
            "repaired_expired_before_reverify":len(repaired_no_reverify_expiry),
            "ids_repaired_expired_before_reverify":repaired_no_reverify_expiry,
            "horizon_censored_repair_or_verified":len(horizon_censored),
            "ids_horizon_censored":horizon_censored,
        },
        "recovery":recovery,
        "service":{
            "correct_done":result["correct_done"],
            "incorrect_done":result["incorrect_done"],
            "expired":result["expired"],
            "backlog":result["backlog"],
            "operations_per_correct_completion":result["operations_per_correct_completion"],
            "phase":result["phase"],
            "repair":result["repair"],
        },
        "requests":request_rows,
    }

manifests=g.primary_manifests(LU2GF1)
bundle=json.dumps(manifests,sort_keys=True,separators=(",",":")).encode()
if hashlib.sha256(bundle).hexdigest()!=BOUND_BUNDLE_SHA256:
    raise SystemExit("LU2H bound manifest mismatch")
for m in manifests:
    g.validate_manifest(m)

worlds=[observe_world(m) for m in manifests]

all_waits=defaultdict(list)
for w in worlds:
    for name in w["waits"]:
        vals=[]
        for r in w["requests"]:
            if name=="pre_sense" and r["sense"] is not None:
                vals.append(r["sense"]-r["created"])
            elif name=="sense_to_process_a_extra" and r["sense"] is not None and r["process_a"] is not None:
                vals.append(max(0,r["process_a"]-r["sense"]-1))
            elif name=="process_a_to_process_b_extra" and r["process_a"] is not None and r["process_b"] is not None:
                vals.append(max(0,r["process_b"]-r["process_a"]-1))
            elif name=="process_b_to_first_route_extra" and r["process_b"] is not None and r["first_route"] is not None:
                vals.append(max(0,r["first_route"]-r["process_b"]-1))
            elif name=="last_route_to_first_verify_extra" and r["last_route"] is not None and r["first_verify"] is not None:
                vals.append(max(0,r["first_verify"]-r["last_route"]-1))
        all_waits[name].extend(vals)

aggregate_waits={k:stat(v) for k,v in all_waits.items()}
deadline_totals={
    k:sum(w["deadline"][k] for w in worlds)
    for k in (
        "corrupted_at_egress_no_epoch_for_initial_verify",
        "detected_no_epoch_for_repair",
        "repaired_expired_before_reverify",
        "horizon_censored_repair_or_verified",
    )
}
recovery_events=[x for w in worlds for x in w["recovery"].values()]
recovery_unreached=sum(not x["target_reached"] for x in recovery_events)

largest_wait=max(
    (k,v["mean"]) for k,v in aggregate_waits.items() if v["mean"] is not None
)[0] if aggregate_waits else None

flags=[]
if largest_wait=="pre_sense":
    flags.append("PRE_SENSE_CONGESTION")
if deadline_totals["corrupted_at_egress_no_epoch_for_initial_verify"] or deadline_totals["detected_no_epoch_for_repair"]:
    flags.append("EXPIRY_ENVELOPE_MISMATCH")
if recovery_unreached:
    flags.append("RECOVERY_TARGET_MISMATCH")
if deadline_totals["horizon_censored_repair_or_verified"]:
    flags.append("FINITE_HORIZON_CENSORING")
if largest_wait in ("process_b_to_first_route_extra","last_route_to_first_verify_extra"):
    flags.append("ROUTE_OR_VERIFY_CONGESTION")
if not flags:
    flags.append("UNRESOLVED")

out={
    "lu2h_prereg":"d9f0da965a3a94453a95e9a17de9961d45c9033f",
    "lu2g_parent_closure":"1fcfef885ca9bd8c3219333965d90cc9cc4a60e9",
    "lu2gf1":LU2GF1,
    "manifest_bundle_sha256":BOUND_BUNDLE_SHA256,
    "observation_only":True,
    "dynamics_changed":False,
    "aggregate_waits":aggregate_waits,
    "deadline_totals":deadline_totals,
    "recovery_windows_total":len(recovery_events),
    "recovery_windows_unreached":recovery_unreached,
    "diagnostic_flags":flags,
    "structural_task2_minimum":{
        "clean_operations":10,
        "corrupted_operations_through_mandatory_reverify":12,
        "separate_verified_to_done_epoch":True,
        "expiry_epochs":EXPIRY,
    },
    "worlds":worlds,
}
Path(sys.argv[1]).write_bytes(json.dumps(out,sort_keys=True,separators=(",",":")).encode())

#!/usr/bin/env python3
import hashlib, json, sys
from collections import Counter
from pathlib import Path
import torch

import lu2t_task4_exact_parent_feasibility_v1 as t

g=t.g
p=t.p

PREREG="44e5db473c0a0aa4c6065b77aa2d83cedecfc1eb"

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def manifest():
    programs=t.mechanical_programs()
    m=t._manifest("YGG-A1-MECHANICAL-FORK-JOIN-R1",programs,"LU2T_MECHANICAL",0,None,"YGG-A1-MECHANICAL-FORK-JOIN-R1")
    return m

def expected(r):
    a=p.truth(r.program_a,r.bits)
    b=p.truth(r.program_b,(a,r.bits[1],r.bits[2],r.bits[3]))
    c=p.truth(r.program_c,(a,r.bits[1],r.bits[2],r.bits[3]))
    d=p.truth(r.program_d,(a,b,c,r.bits[3]))
    return a,b,c,d

def expected_pair(r):
    a,_,_,d=expected(r)
    return a,d

def maturity_summary(m,registry,detected):
    old=t.expected_quad
    t.expected_quad=expected
    try:
        return t.maturity_summary(m,registry,detected)
    finally:
        t.expected_quad=old

def expected_pair_fork(r):
    a,_,_,d=expected(r)
    return a,d

def terminal_rule_fork(r,det):
    if det is None:
        return False,"UNDETECTED"
    if r.expired_epoch is not None:
        return False,"EXPIRED"
    a,b,c,d=expected(r)
    values_ok=(r.y_a==a and r.y_b==b and r.y_c==c and r.output==d)
    if det<=t.MATURE_MAX_DETECTION:
        return bool(r.repaired and r.verified_after_repair and r.done_epoch is not None and r.done_epoch<=159 and r.stage=="DONE" and values_ok),"MATURE"
    if det==157:
        return bool(r.repaired and r.repair_epoch is not None and r.repair_epoch<=158 and r.verified_after_repair and r.verified_epoch is not None and r.verified_epoch<=159 and r.done_epoch is None and r.stage=="VERIFIED" and values_ok),"TERMINAL_157"
    if det==158:
        return bool(r.repaired and r.repair_epoch is not None and r.repair_epoch<=159 and not r.verified_after_repair and r.done_epoch is None and r.stage=="AT_EGRESS" and values_ok),"TERMINAL_158"
    if det==159:
        return bool((not r.repaired) and r.repair_epoch is None and r.done_epoch is None and r.stage=="REPAIR_PENDING"),"TERMINAL_159"
    return False,"OUT_OF_RANGE"

def maturity_summary_fork(m,registry,detected):
    rows=[]; ok=True
    for rid in m["corrupt_ids"]:
        r=registry[rid]
        if not r.reached_egress_after_corrupt:
            continue
        det=detected.get(rid)
        passed,kind=terminal_rule_fork(r,det)
        ok=ok and passed
        rows.append({"rid":rid,"detection_epoch":det,"repair_epoch":r.repair_epoch,
                     "verified_epoch":r.verified_epoch if r.verified_after_repair else None,
                     "done_epoch":r.done_epoch,"terminal_state":r.stage,"kind":kind,"pass":passed})
    return {"pass":bool(ok),"rows":rows,
            "reached_egress":len(rows),
            "mature_detected":sum(1 for x in rows if x["detection_epoch"] is not None and x["detection_epoch"]<=156),
            "terminal_inflight_detected":sum(1 for x in rows if x["detection_epoch"] is not None and x["detection_epoch"]>=157)}

def task_op(r):
    if r.stage=="RAW": return "SENSE"
    if r.stage in ("SENSED","PROCESSED_A","PROCESSED_B_ONLY","PROCESSED_C_ONLY","PROCESSED_BC"): return "PROCESS"
    if r.stage in ("PROCESSED_D","ROUTING"): return "ROUTE"
    if r.stage=="AT_EGRESS": return "VERIFY"
    if r.stage=="REPAIR_PENDING": return "REPAIR"
    return None

def do_op(seed,tick,cell,op,r,trace):
    before=(r.stage,r.pos,r.y_a,r.y_b,r.y_c,r.output,r.corruption_applied,r.repaired)
    anchors=g.request_anchors(seed,r)
    if op=="SENSE":
        assert r.stage=="RAW"
        r.stage="SENSED"; r.pos=cell
    elif op=="PROCESS":
        if r.stage=="SENSED":
            r.y_a=p.truth(r.program_a,r.bits); r.stage="PROCESSED_A"; r.process_a_epoch=tick
        elif r.stage=="PROCESSED_A":
            if r.rid%2==0:
                r.y_b=p.truth(r.program_b,(r.y_a,r.bits[1],r.bits[2],r.bits[3]))
                r.stage="PROCESSED_B_ONLY"; r.process_b_epoch=tick
            else:
                r.y_c=p.truth(r.program_c,(r.y_a,r.bits[1],r.bits[2],r.bits[3]))
                r.stage="PROCESSED_C_ONLY"; r.process_c_epoch=tick
        elif r.stage=="PROCESSED_B_ONLY":
            assert r.y_a is not None and r.y_b is not None and r.y_c is None
            r.y_c=p.truth(r.program_c,(r.y_a,r.bits[1],r.bits[2],r.bits[3]))
            r.stage="PROCESSED_BC"; r.process_c_epoch=tick
        elif r.stage=="PROCESSED_C_ONLY":
            assert r.y_a is not None and r.y_c is not None and r.y_b is None
            r.y_b=p.truth(r.program_b,(r.y_a,r.bits[1],r.bits[2],r.bits[3]))
            r.stage="PROCESSED_BC"; r.process_b_epoch=tick
        elif r.stage=="PROCESSED_BC":
            assert r.y_a is not None and r.y_b is not None and r.y_c is not None
            r.output=p.truth(r.program_d,(r.y_a,r.y_b,r.y_c,r.bits[3]))
            r.stage="PROCESSED_D"; r.process_d_epoch=tick
            if not r.corruption_applied:
                r.corruption_applied=True; r.corrupted=bool(r.scheduled_corrupt)
                if r.corrupted: r.output^=1
        else:
            raise AssertionError("process order")
    elif op=="ROUTE":
        assert r.stage in ("PROCESSED_D","ROUTING")
        old=r.pos; r.pos=(r.pos+p.stream_dir(r.stream))%p.N
        assert p.ring_distance(old,r.pos)==1
        if r.pos==p.egress(anchors,r.stream):
            r.stage="AT_EGRESS"
            if r.first_egress_epoch is None: r.first_egress_epoch=tick
            if r.corrupted: r.reached_egress_after_corrupt=True
        else:
            r.stage="ROUTING"
    elif op=="VERIFY":
        assert r.stage=="AT_EGRESS"
        if r.output==expected(r)[3]:
            r.stage="VERIFIED"; r.verified_epoch=tick; r.verified_after_repair=r.repaired
        else:
            r.detected=True; r.stage="REPAIR_PENDING"
    elif op=="REPAIR":
        assert r.stage=="REPAIR_PENDING"
        r.y_a,r.y_b,r.y_c,r.output=expected(r)
        r.repaired=True; r.repair_epoch=tick; r.stage="AT_EGRESS"
    else:
        raise AssertionError(op)
    r.operations+=1
    after=(r.stage,r.pos,r.y_a,r.y_b,r.y_c,r.output,r.corruption_applied,r.repaired)
    trace.append({"t":tick,"cell":cell,"rid":r.rid,"stream":r.stream,"op":op,"before":before,"after":after,
                  "local_distance_before":p.ring_distance(cell,before[1])})

def run_world(m):
    registry={}; detected={}
    programs=m["programs"]
    old=(g.Task2Request,g.task2_op,g.do_operation,g.expected_pair,g.validate_manifest,g.REQUESTS_PER_EPOCH)
    def factory(rid,stream,created,bits,program_a,program_b,pos,scheduled_corrupt=False):
        r=t.Task4Request(rid,stream,created,bits,program_a,program_b,programs[stream]["C"],programs[stream]["D"],pos,scheduled_corrupt)
        registry[rid]=r
        return r
    def op(seed,tick,cell,name,r,trace):
        pre=r.stage
        do_op(seed,tick,cell,name,r,trace)
        if name=="VERIFY" and pre=="AT_EGRESS" and r.stage=="REPAIR_PENDING":
            detected.setdefault(r.rid,tick)
    g.Task2Request=factory; g.task2_op=task_op; g.do_operation=op; g.expected_pair=expected_pair
    g.validate_manifest=t.validate_manifest; g.REQUESTS_PER_EPOCH=1
    try:
        result,history,_=g.run_world(m,"U_A0")
    finally:
        g.Task2Request,g.task2_op,g.do_operation,g.expected_pair,g.validate_manifest,g.REQUESTS_PER_EPOCH=old
    return result,history,registry,detected

def fixture(order):
    pr=t.mechanical_programs()["C"]
    rid=2 if order=="BC" else 3
    r=t.Task4Request(rid,"C",0,(1,0,1,0),pr["A"],pr["B"],pr["C"],pr["D"],0,True)
    tr=[]
    do_op("fixture",0,0,"SENSE",r,tr)
    do_op("fixture",1,0,"PROCESS",r,tr)
    do_op("fixture",2,0,"PROCESS",r,tr)
    sibling1=r.stage
    d_blocked=r.output is None
    do_op("fixture",3,0,"PROCESS",r,tr)
    siblings_done=r.stage=="PROCESSED_BC" and r.y_b is not None and r.y_c is not None and r.output is None
    do_op("fixture",4,0,"PROCESS",r,tr)
    d_done=r.stage=="PROCESSED_D" and r.output is not None
    exp=expected(r)
    deps=(r.y_a,r.y_b,r.y_c)==exp[:3]
    r.stage="AT_EGRESS"; r.pos=0
    do_op("fixture",5,0,"VERIFY",r,tr)
    detected=r.stage=="REPAIR_PENDING"
    do_op("fixture",6,0,"REPAIR",r,tr)
    repaired=(r.y_a,r.y_b,r.y_c,r.output)==exp
    do_op("fixture",7,0,"VERIFY",r,tr)
    reverified=r.stage=="VERIFIED" and r.verified_after_repair
    return {"order":order,"sibling1":sibling1,"d_blocked_until_join":d_blocked and siblings_done,
            "d_after_join":d_done,"dependencies_exact":deps,"detected":detected,
            "repaired":repaired,"reverified":reverified}

def mechanical():
    m=manifest()
    f_bc=fixture("BC"); f_cb=fixture("CB")
    rng0=torch.random.get_rng_state().clone()
    a=run_world(m)
    rng1=torch.random.get_rng_state().clone()
    b=run_world(m)
    rowa={"result":g.compact(a[0]),"maturity":maturity_summary(m,a[2],a[3])}
    rowb={"result":g.compact(b[0]),"maturity":maturity_summary(m,b[2],b[3])}
    ba=canonical(rowa); bb=canonical(rowb)
    probes={
      "prereg_bound":PREREG=="44e5db473c0a0aa4c6065b77aa2d83cedecfc1eb",
      "bc_order_exercised":f_bc["sibling1"]=="PROCESSED_B_ONLY",
      "cb_order_exercised":f_cb["sibling1"]=="PROCESSED_C_ONLY",
      "join_blocks_d":f_bc["d_blocked_until_join"] and f_cb["d_blocked_until_join"],
      "d_after_both":f_bc["d_after_join"] and f_cb["d_after_join"],
      "dependencies_exact":f_bc["dependencies_exact"] and f_cb["dependencies_exact"],
      "repair_reverify":f_bc["detected"] and f_bc["repaired"] and f_bc["reverified"] and f_cb["detected"] and f_cb["repaired"] and f_cb["reverified"],
      "duplicate_byte_identical":ba==bb,
      "zero_incorrect_done":rowa["result"]["incorrect_done"]==0,
      "maturity_pass":rowa["maturity"]["pass"],
      "no_model_rng":torch.equal(rng0,rng1)
    }
    return {"schema":1,"experiment":"YGG-A1","all_pass":all(probes.values()),"probes":probes,
            "fixture_bc":f_bc,"fixture_cb":f_cb,
            "duplicate":{"bytes":len(ba),"sha256":hashlib.sha256(ba).hexdigest()},
            "world":rowa}

def scored_world(m):
    t.validate_manifest(m)
    result,history,registry,detected=run_world(m)
    return {
        "manifest":m,
        "result":g.compact(result),
        "maturity":maturity_summary(m,registry,detected),
        "integrity":{
            "duplicate_cell":result["matching_duplicate_cell"]==0,
            "duplicate_request":result["matching_duplicate_request"]==0,
            "incorrect_done_zero":result["incorrect_done"]==0,
        },
    }

def primary():
    manifests=t.primary_manifests(PREREG)
    first=[scored_world(m) for m in manifests]
    second=[scored_world(m) for m in manifests]
    b1=canonical(first); b2=canonical(second)

    feasible=[row for row in first if t.baseline_feasible(row)]
    all_zero=all(row["result"]["incorrect_done"]==0 for row in first)
    all_matching=all(row["integrity"]["duplicate_cell"] and row["integrity"]["duplicate_request"] for row in first)
    all_repair=all(row["result"]["repair"]["repair_integrity"] for row in first)
    all_maturity=all(row["maturity"]["pass"] for row in first)
    f_bc=fixture("BC"); f_cb=fixture("CB")
    ordering=(f_bc["sibling1"]=="PROCESSED_B_ONLY" and f_cb["sibling1"]=="PROCESSED_C_ONLY")
    join=(f_bc["d_blocked_until_join"] and f_cb["d_blocked_until_join"] and
          f_bc["d_after_join"] and f_cb["d_after_join"])
    dependency=(f_bc["dependencies_exact"] and f_cb["dependencies_exact"])
    repair_fixture=(f_bc["detected"] and f_bc["repaired"] and f_bc["reverified"] and
                    f_cb["detected"] and f_cb["repaired"] and f_cb["reverified"])
    duplicate=(b1==b2)
    q={
        "baseline_feasible_count":len(feasible),
        "evidence_coverage_pass":len(feasible)>=8,
        "all_zero_incorrect_done":all_zero,
        "all_matching_integrity":all_matching,
        "both_sibling_orders_exercised":ordering,
        "d_never_before_join":join,
        "fork_dependencies_exact":dependency,
        "all_repair_integrity":all_repair,
        "all_maturity_pass":all_maturity,
        "repair_reverify_fixture":repair_fixture,
        "duplicate_byte_identical":duplicate,
    }
    q["YGG_A1_FORK_JOIN_EXACT_PARENT_FEASIBLE"]=all([
        q["evidence_coverage_pass"],q["all_zero_incorrect_done"],q["all_matching_integrity"],
        q["both_sibling_orders_exercised"],q["d_never_before_join"],q["fork_dependencies_exact"],
        q["all_repair_integrity"],q["all_maturity_pass"],q["repair_reverify_fixture"],
        q["duplicate_byte_identical"],
    ])
    q["feasible_replicates"]=[row["manifest"]["replicate"] for row in feasible]
    q["per_world"]=[{
        "replicate":row["manifest"]["replicate"],
        "baseline_feasible":t.baseline_feasible(row),
        "correct_done":row["result"]["correct_done"],
        "incorrect_done":row["result"]["incorrect_done"],
        "expired":row["result"]["expired"],
        "backlog":row["result"]["backlog"],
        "ops_per_correct":row["result"]["operations_per_correct_completion"],
        "demand_recovery":row["result"]["events"]["demand_reversal_recovery_latency"],
        "lesion_recovery":row["result"]["events"]["lesion_recovery_latency"],
        "anchor_recovery":row["result"]["events"]["anchor_rotation_recovery_latency"],
        "maturity_pass":row["maturity"]["pass"],
        "repair_integrity":row["result"]["repair"]["repair_integrity"],
    } for row in first]
    return {
        "schema":1,
        "experiment":"YGG-A1",
        "stage":"primary",
        "prereg":PREREG,
        "duplicate":{"byte_identical":duplicate,"bytes":len(b1),"sha256":hashlib.sha256(b1).hexdigest()},
        "qualification":q,
        "sweep":first,
    }

def main():
    if len(sys.argv)!=3 or sys.argv[1] not in ("mechanical","primary"):
        raise SystemExit("usage: mechanical OUT | primary OUT")
    out=mechanical() if sys.argv[1]=="mechanical" else primary()
    Path(sys.argv[2]).write_bytes(canonical(out))

if __name__=="__main__":
    main()

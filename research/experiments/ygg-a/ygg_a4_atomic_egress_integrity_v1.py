#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a1_fork_join_v1 as a1

g=a1.g
p=a1.p
t=a1.t
PREREG="6c7d11b0a2acf1b97b39f5510d2c02f83cc31acd"
A1_PREREG=a1.PREREG

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def atomic_do_op(stats,seed,tick,cell,name,r,trace):
    pre=r.stage
    a1.do_op(seed,tick,cell,name,r,trace)
    if name=="ROUTE" and pre in ("PROCESSED_D","ROUTING") and r.stage=="AT_EGRESS":
        stats["atomic_egress_checks"]+=1
        if r.output==a1.expected(r)[3]:
            r.stage="VERIFIED"
            r.verified_epoch=tick
            r.verified_after_repair=r.repaired
            stats["atomic_correct_verifications"]+=1
        else:
            r.detected=True
            r.stage="REPAIR_PENDING"
            stats["atomic_corruption_detections"]+=1
            if tick==159:
                stats["atomic_detections_epoch_159"]+=1
        if trace:
            trace[-1]["after"]=(r.stage,r.pos,r.y_a,r.y_b,r.y_c,r.output,r.corruption_applied,r.repaired)
            trace[-1]["atomic_egress_verify"]=True

def run_world(m):
    registry={}
    detected={}
    programs=m["programs"]
    stats={
        "atomic_egress_checks":0,
        "atomic_correct_verifications":0,
        "atomic_corruption_detections":0,
        "atomic_detections_epoch_159":0,
    }
    old=(g.Task2Request,g.task2_op,g.do_operation,g.expected_pair,g.validate_manifest,g.REQUESTS_PER_EPOCH)

    def factory(rid,stream,created,bits,program_a,program_b,pos,scheduled_corrupt=False):
        r=t.Task4Request(rid,stream,created,bits,program_a,program_b,programs[stream]["C"],programs[stream]["D"],pos,scheduled_corrupt)
        registry[rid]=r
        return r

    def op(seed,tick,cell,name,r,trace):
        before=r.stage
        atomic_do_op(stats,seed,tick,cell,name,r,trace)
        if (
            (name=="VERIFY" and before=="AT_EGRESS" and r.stage=="REPAIR_PENDING")
            or
            (name=="ROUTE" and before in ("PROCESSED_D","ROUTING") and r.stage=="REPAIR_PENDING")
        ):
            detected.setdefault(r.rid,tick)

    g.Task2Request=factory
    g.task2_op=a1.task_op
    g.do_operation=op
    g.expected_pair=a1.expected_pair
    g.validate_manifest=t.validate_manifest
    g.REQUESTS_PER_EPOCH=1
    try:
        result,history,_=g.run_world(m,"U_A0")
    finally:
        g.Task2Request,g.task2_op,g.do_operation,g.expected_pair,g.validate_manifest,g.REQUESTS_PER_EPOCH=old
    return result,history,registry,detected,stats

def route_fixture(corrupt=False,non_egress=False):
    programs=t.mechanical_programs()["C"]
    r=t.Task4Request(2,"C",0,(1,0,1,0),programs["A"],programs["B"],programs["C"],programs["D"],0,False)
    ya,yb,yc,yd=a1.expected(r)
    r.y_a,r.y_b,r.y_c,r.output=ya,yb,yc,yd
    r.stage="PROCESSED_D"
    r.corruption_applied=True
    if corrupt:
        r.corrupted=True
        r.output^=1
    seed="YGG-A4-HANDOFF-FIXTURE"
    anchors=g.request_anchors(seed,r)
    egress=p.egress(anchors,r.stream)
    direction=p.stream_dir(r.stream)
    steps=2 if non_egress else 1
    r.pos=(egress-steps*direction)%p.N
    stats={
        "atomic_egress_checks":0,
        "atomic_correct_verifications":0,
        "atomic_corruption_detections":0,
        "atomic_detections_epoch_159":0,
    }
    trace=[]
    atomic_do_op(stats,seed,159,0,"ROUTE",r,trace)
    return r,stats,trace,egress

def mechanical():
    correct,cs,ctrace,ce=route_fixture(False,False)
    corrupt,ks,ktrace,ke=route_fixture(True,False)
    non,ns,ntrace,ne=route_fixture(False,True)

    before_repair=corrupt.operations
    atomic_do_op(ks,"YGG-A4-HANDOFF-FIXTURE",160,0,"REPAIR",corrupt,ktrace)
    after_repair=(corrupt.stage=="AT_EGRESS" and corrupt.repaired and corrupt.operations==before_repair+1)
    atomic_do_op(ks,"YGG-A4-HANDOFF-FIXTURE",161,0,"VERIFY",corrupt,ktrace)
    reverified=(corrupt.stage=="VERIFIED" and corrupt.verified_after_repair)

    f_bc=a1.fixture("BC")
    f_cb=a1.fixture("CB")
    m=a1.manifest()
    rng0=torch.random.get_rng_state().clone()
    a=run_world(m)
    rng1=torch.random.get_rng_state().clone()
    b=run_world(m)
    rowa={"result":g.compact(a[0]),"maturity":a1.maturity_summary(m,a[2],a[3]),"atomic":a[4]}
    rowb={"result":g.compact(b[0]),"maturity":a1.maturity_summary(m,b[2],b[3]),"atomic":b[4]}
    ba=canonical(rowa); bb=canonical(rowb)

    probes={
        "prereg_bound":PREREG=="6c7d11b0a2acf1b97b39f5510d2c02f83cc31acd",
        "correct_handoff_verified_same_route":correct.stage=="VERIFIED" and correct.verified_epoch==159 and cs["atomic_correct_verifications"]==1,
        "corrupt_handoff_detected_same_route":ks["atomic_corruption_detections"]==1 and ks["atomic_detections_epoch_159"]==1,
        "single_operation_for_atomic_handoff":correct.operations==1 and before_repair==1,
        "non_egress_route_unchanged":non.stage=="ROUTING" and non.operations==1 and ns["atomic_egress_checks"]==0,
        "repair_separate_operation":after_repair,
        "repair_reverify_exact":reverified,
        "bc_order_exercised":f_bc["sibling1"]=="PROCESSED_B_ONLY",
        "cb_order_exercised":f_cb["sibling1"]=="PROCESSED_C_ONLY",
        "join_blocks_d":f_bc["d_blocked_until_join"] and f_cb["d_blocked_until_join"],
        "d_after_both":f_bc["d_after_join"] and f_cb["d_after_join"],
        "dependencies_exact":f_bc["dependencies_exact"] and f_cb["dependencies_exact"],
        "duplicate_byte_identical":ba==bb,
        "zero_incorrect_done":rowa["result"]["incorrect_done"]==0,
        "maturity_pass":rowa["maturity"]["pass"],
        "no_model_rng":torch.equal(rng0,rng1),
    }
    return {
        "schema":1,
        "experiment":"YGG-A4",
        "stage":"mechanical",
        "prereg":PREREG,
        "all_pass":all(probes.values()),
        "probes":probes,
        "correct_fixture":{"stage":correct.stage,"verified_epoch":correct.verified_epoch,"operations":correct.operations,"atomic":cs},
        "corrupt_fixture":{"stage":corrupt.stage,"operations":corrupt.operations,"atomic":ks},
        "non_egress_fixture":{"stage":non.stage,"operations":non.operations,"atomic":ns},
        "world":rowa,
        "duplicate":{"bytes":len(ba),"sha256":hashlib.sha256(ba).hexdigest()},
    }

def scored_world(m):
    t.validate_manifest(m)
    result,history,registry,detected,stats=run_world(m)
    target=registry.get(141)
    return {
        "manifest":m,
        "result":g.compact(result),
        "maturity":a1.maturity_summary(m,registry,detected),
        "atomic":stats,
        "integrity":{
            "duplicate_cell":result["matching_duplicate_cell"]==0,
            "duplicate_request":result["matching_duplicate_request"]==0,
            "incorrect_done_zero":result["incorrect_done"]==0,
        },
        "target_141":{
            "present":target is not None,
            "stage":target.stage if target is not None else None,
            "detected":target.detected if target is not None else None,
            "repaired":target.repaired if target is not None else None,
            "first_egress_epoch":target.first_egress_epoch if target is not None else None,
        },
    }

def primary():
    manifests=t.primary_manifests(A1_PREREG)
    first=[scored_world(m) for m in manifests]
    second=[scored_world(m) for m in manifests]
    b1=canonical(first); b2=canonical(second)

    feasible=[row for row in first if t.baseline_feasible(row)]
    all_zero=all(row["result"]["incorrect_done"]==0 for row in first)
    all_matching=all(row["integrity"]["duplicate_cell"] and row["integrity"]["duplicate_request"] for row in first)
    all_repair=all(row["result"]["repair"]["repair_integrity"] for row in first)
    all_maturity=all(row["maturity"]["pass"] for row in first)
    f_bc=a1.fixture("BC"); f_cb=a1.fixture("CB")
    ordering=(f_bc["sibling1"]=="PROCESSED_B_ONLY" and f_cb["sibling1"]=="PROCESSED_C_ONLY")
    join=(f_bc["d_blocked_until_join"] and f_cb["d_blocked_until_join"] and f_bc["d_after_join"] and f_cb["d_after_join"])
    dependency=(f_bc["dependencies_exact"] and f_cb["dependencies_exact"])
    repair_fixture=(f_bc["detected"] and f_bc["repaired"] and f_bc["reverified"] and f_cb["detected"] and f_cb["repaired"] and f_cb["reverified"])
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
    q["YGG_A4_ATOMIC_EGRESS_INTEGRITY_HANDOFF"]=all(q.values())
    q["feasible_replicates"]=[row["manifest"]["replicate"] for row in feasible]
    q["atomic_totals"]={
        "checks":sum(r["atomic"]["atomic_egress_checks"] for r in first),
        "correct_verifications":sum(r["atomic"]["atomic_correct_verifications"] for r in first),
        "corruption_detections":sum(r["atomic"]["atomic_corruption_detections"] for r in first),
        "detections_epoch_159":sum(r["atomic"]["atomic_detections_epoch_159"] for r in first),
    }
    q["per_world"]=[{
        "replicate":row["manifest"]["replicate"],
        "baseline_feasible":t.baseline_feasible(row),
        "correct_done":row["result"]["correct_done"],
        "incorrect_done":row["result"]["incorrect_done"],
        "backlog":row["result"]["backlog"],
        "maturity_pass":row["maturity"]["pass"],
        "repair_integrity":row["result"]["repair"]["repair_integrity"],
        "atomic":row["atomic"],
        "target_141":row["target_141"],
    } for row in first]
    return {
        "schema":1,
        "experiment":"YGG-A4",
        "stage":"primary",
        "prereg":PREREG,
        "frozen_a1_prereg":A1_PREREG,
        "duplicate":{"byte_identical":duplicate,"bytes":len(b1),"sha256":hashlib.sha256(b1).hexdigest()},
        "qualification":q,
        "sweep":first,
    }

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    mech=mechanical()
    if not mech["all_pass"]:
        raise SystemExit("YGG_A4_MECHANICAL_GATE_FAILED")
    prim=primary()
    out={"schema":1,"experiment":"YGG-A4","prereg":PREREG,"mechanical":mech,"primary":prim}
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()

#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a1_fork_join_v1 as a1
import ygg_a4_atomic_egress_integrity_v1 as a4
import ygg_a6_horizon_aware_atomic_egress_confirmation_v1 as a6

g=a1.g
p=a1.p
t=a1.t

PREREG="b33bbf51a2aa7ba2b1715b0a64886a81694ef999"
PARENT_CLOSURE="422fddf4c7f6b0d463b7dd0688a8e26cef731380"
A1_PREREG=a1.PREREG
DAMAGE_PER_WORLD=8

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def damage_schedule(m):
    excluded=set(m["corrupt_ids"])
    candidates=[rid for rid in range(160) if rid not in excluded]
    ranked=sorted(
        candidates,
        key=lambda rid:(p.h64("YGG-A8-BRANCH-DAMAGE",m["seed"],rid),rid),
    )
    chosen=ranked[:DAMAGE_PER_WORLD]
    out={}
    for rid in chosen[:4]:
        out[rid]="B"
    for rid in chosen[4:8]:
        out[rid]="C"
    if len(out)!=8 or sum(1 for x in out.values() if x=="B")!=4 or sum(1 for x in out.values() if x=="C")!=4:
        raise AssertionError("branch damage schedule")
    if set(out)&excluded:
        raise AssertionError("branch/terminal corruption overlap")
    return out

def init_branch_fields(r,target=None):
    r.branch_damage_target=target
    r.branch_damage_scheduled=target is not None
    r.branch_damage_applied=False
    r.branch_damage_epoch=None
    r.branch_repaired=False
    r.branch_repair_epoch=None

def branch_mismatch(r):
    _,b,c,_=a1.expected(r)
    return r.y_b!=b or r.y_c!=c

def manual_branch_repair(seed,tick,cell,r,trace,stats):
    before=(r.stage,r.pos,r.y_a,r.y_b,r.y_c,r.output,r.corruption_applied,r.repaired)
    a,b,c,d=a1.expected(r)
    wrong_b=r.y_b!=b
    wrong_c=r.y_c!=c
    if wrong_b==wrong_c:
        raise AssertionError("expected exactly one damaged sibling")
    if wrong_b:
        if r.branch_damage_target!="B":
            raise AssertionError("branch target B mismatch")
        r.y_b=b
    else:
        if r.branch_damage_target!="C":
            raise AssertionError("branch target C mismatch")
        r.y_c=c
    r.branch_repaired=True
    r.branch_repair_epoch=tick
    r.operations+=1
    stats["branch_repairs"]+=1
    if wrong_b:
        stats["branch_repairs_b"]+=1
    else:
        stats["branch_repairs_c"]+=1
    after=(r.stage,r.pos,r.y_a,r.y_b,r.y_c,r.output,r.corruption_applied,r.repaired)
    trace.append({
        "t":tick,"cell":cell,"rid":r.rid,"stream":r.stream,
        "op":"BRANCH_REPAIR","before":before,"after":after,
        "local_distance_before":p.ring_distance(cell,before[1]),
    })

def run_world_mode(m,mode,damage_on):
    registry={}
    detected={}
    programs=m["programs"]
    schedule=damage_schedule(m) if damage_on else {}
    stats={
        "atomic_egress_checks":0,
        "atomic_correct_verifications":0,
        "atomic_corruption_detections":0,
        "atomic_detections_epoch_159":0,
        "branch_damage_events":0,
        "branch_damage_b":0,
        "branch_damage_c":0,
        "branch_repairs":0,
        "branch_repairs_b":0,
        "branch_repairs_c":0,
        "d_while_branch_incorrect":0,
    }
    old=(g.Task2Request,g.task2_op,g.do_operation,g.expected_pair,g.validate_manifest,g.REQUESTS_PER_EPOCH)

    def factory(rid,stream,created,bits,program_a,program_b,pos,scheduled_corrupt=False):
        r=t.Task4Request(
            rid,stream,created,bits,program_a,program_b,
            programs[stream]["C"],programs[stream]["D"],pos,scheduled_corrupt
        )
        init_branch_fields(r,schedule.get(rid))
        registry[rid]=r
        return r

    def op(seed,tick,cell,name,r,trace):
        pre=r.stage
        if damage_on and name=="PROCESS" and r.stage=="PROCESSED_BC" and branch_mismatch(r):
            manual_branch_repair(seed,tick,cell,r,trace,stats)
            return

        a4.atomic_do_op(stats,seed,tick,cell,name,r,trace)

        if (
            damage_on
            and name=="PROCESS"
            and pre in ("PROCESSED_B_ONLY","PROCESSED_C_ONLY")
            and r.stage=="PROCESSED_BC"
            and r.branch_damage_scheduled
            and not r.branch_damage_applied
        ):
            if r.branch_damage_target=="B":
                r.y_b ^= 1
                stats["branch_damage_b"]+=1
            elif r.branch_damage_target=="C":
                r.y_c ^= 1
                stats["branch_damage_c"]+=1
            else:
                raise AssertionError("unknown branch target")
            r.branch_damage_applied=True
            r.branch_damage_epoch=tick
            stats["branch_damage_events"]+=1
            if not branch_mismatch(r):
                raise AssertionError("branch damage did not change sibling")
            if trace:
                trace[-1]["after"]=(r.stage,r.pos,r.y_a,r.y_b,r.y_c,r.output,r.corruption_applied,r.repaired)
                trace[-1]["branch_damage_target"]=r.branch_damage_target

        if name=="PROCESS" and pre=="PROCESSED_BC" and r.stage=="PROCESSED_D" and branch_mismatch(r):
            stats["d_while_branch_incorrect"]+=1
            raise AssertionError("D executed on damaged sibling")

        if (
            (name=="VERIFY" and pre=="AT_EGRESS" and r.stage=="REPAIR_PENDING")
            or
            (name=="ROUTE" and pre in ("PROCESSED_D","ROUTING") and r.stage=="REPAIR_PENDING")
        ):
            detected.setdefault(r.rid,tick)

    g.Task2Request=factory
    g.task2_op=a1.task_op
    g.do_operation=op
    g.expected_pair=a1.expected_pair
    g.validate_manifest=t.validate_manifest
    g.REQUESTS_PER_EPOCH=1
    try:
        result,history,telemetry=g.run_world(m,mode)
    finally:
        g.Task2Request,g.task2_op,g.do_operation,g.expected_pair,g.validate_manifest,g.REQUESTS_PER_EPOCH=old

    scheduled=[registry[rid] for rid in sorted(schedule)]
    branch_summary={
        "scheduled":len(schedule),
        "scheduled_b":sum(1 for x in schedule.values() if x=="B"),
        "scheduled_c":sum(1 for x in schedule.values() if x=="C"),
        "applied":sum(1 for r in scheduled if r.branch_damage_applied),
        "repaired":sum(1 for r in scheduled if r.branch_repaired),
        "all_repaired_before_d":all(
            r.branch_repaired
            and r.branch_repair_epoch is not None
            and r.process_d_epoch is not None
            and r.branch_repair_epoch<r.process_d_epoch
            for r in scheduled
        ) if scheduled else True,
        "unrepaired_terminal":sum(
            1 for r in scheduled
            if (not r.branch_repaired) and r.stage in ("PROCESSED_D","ROUTING","AT_EGRESS","VERIFIED","DONE","REPAIR_PENDING")
        ),
        "damage_ids":sorted(schedule),
        "damage_targets":{str(k):v for k,v in sorted(schedule.items())},
    }
    return result,history,telemetry,registry,detected,stats,branch_summary

def scored(m,mode,damage_on):
    t.validate_manifest(m)
    result,history,telemetry,registry,detected,stats,branch=run_world_mode(m,mode,damage_on)
    row={
        "manifest":m,
        "mode":mode,
        "damage_on":damage_on,
        "result":g.compact(result),
        "maturity":a1.maturity_summary(m,registry,detected),
        "atomic":{k:v for k,v in stats.items() if k.startswith("atomic_")},
        "branch":branch,
        "branch_stats":{k:v for k,v in stats.items() if k.startswith("branch_") or k=="d_while_branch_incorrect"},
        "integrity":{
            "duplicate_cell":result["matching_duplicate_cell"]==0,
            "duplicate_request":result["matching_duplicate_request"]==0,
            "incorrect_done_zero":result["incorrect_done"]==0,
        },
    }
    summary=a6.summarize_world(row)
    row["horizon_aware_repair_integrity"]=summary["horizon_aware_repair_integrity"]
    row["terminal159_count"]=summary["terminal159_count"]
    row["terminal159_rows"]=summary["terminal159_rows"]
    return row

def branch_fixture(order,target):
    programs=t.mechanical_programs()["C"]
    rid=2 if order=="BC" else 3
    r=t.Task4Request(rid,"C",0,(1,0,1,0),programs["A"],programs["B"],programs["C"],programs["D"],0,False)
    init_branch_fields(r,target)
    stats={
        "atomic_egress_checks":0,"atomic_correct_verifications":0,
        "atomic_corruption_detections":0,"atomic_detections_epoch_159":0,
        "branch_damage_events":0,"branch_damage_b":0,"branch_damage_c":0,
        "branch_repairs":0,"branch_repairs_b":0,"branch_repairs_c":0,
        "d_while_branch_incorrect":0,
    }
    trace=[]

    def fixture_op(tick,name):
        pre=r.stage
        if name=="PROCESS" and r.stage=="PROCESSED_BC" and branch_mismatch(r):
            manual_branch_repair("YGG-A8-FIXTURE",tick,0,r,trace,stats)
            return
        a4.atomic_do_op(stats,"YGG-A8-FIXTURE",tick,0,name,r,trace)
        if (
            name=="PROCESS" and pre in ("PROCESSED_B_ONLY","PROCESSED_C_ONLY")
            and r.stage=="PROCESSED_BC" and not r.branch_damage_applied
        ):
            if target=="B":
                r.y_b^=1; stats["branch_damage_b"]+=1
            else:
                r.y_c^=1; stats["branch_damage_c"]+=1
            r.branch_damage_applied=True; r.branch_damage_epoch=tick
            stats["branch_damage_events"]+=1
            trace[-1]["after"]=(r.stage,r.pos,r.y_a,r.y_b,r.y_c,r.output,r.corruption_applied,r.repaired)

    fixture_op(0,"SENSE")
    fixture_op(1,"PROCESS")
    fixture_op(2,"PROCESS")
    fixture_op(3,"PROCESS")
    damaged_stage=r.stage
    damaged=branch_mismatch(r) and r.output is None
    operations_before_repair=r.operations
    fixture_op(4,"PROCESS")
    repaired=not branch_mismatch(r) and r.stage=="PROCESSED_BC" and r.output is None and r.operations==operations_before_repair+1
    fixture_op(5,"PROCESS")
    d_after_repair=r.stage=="PROCESSED_D" and r.output==a1.expected(r)[3]
    return {
        "order":order,"target":target,
        "damaged_stage":damaged_stage,"damage_applied":damaged,
        "repair_separate_operation":repaired,
        "d_after_repair":d_after_repair,
        "branch_damage_events":stats["branch_damage_events"],
        "branch_repairs":stats["branch_repairs"],
        "d_while_branch_incorrect":stats["d_while_branch_incorrect"],
    }

def mechanical():
    f1=branch_fixture("BC","B")
    f2=branch_fixture("CB","C")
    terminal=a4.mechanical()
    checks={
        "b_damage_fixture":f1["damage_applied"] and f1["target"]=="B",
        "c_damage_fixture":f2["damage_applied"] and f2["target"]=="C",
        "damage_after_both_siblings":f1["damaged_stage"]=="PROCESSED_BC" and f2["damaged_stage"]=="PROCESSED_BC",
        "repair_separate_operation":f1["repair_separate_operation"] and f2["repair_separate_operation"],
        "d_after_repair_only":f1["d_after_repair"] and f2["d_after_repair"],
        "no_d_while_damaged":f1["d_while_branch_incorrect"]==0 and f2["d_while_branch_incorrect"]==0,
        "both_sibling_orders":f1["order"]=="BC" and f2["order"]=="CB",
        "atomic_terminal_mechanical_exact":bool(terminal["all_pass"]),
    }
    return {"all_pass":all(checks.values()),"checks":checks,"bc_b":f1,"cb_c":f2,"terminal":terminal}

def one_pass():
    manifests=t.primary_manifests(A1_PREREG)
    rows=[]
    for m in manifests:
        a0_off=scored(m,"U_A0",False)
        a0_on=scored(m,"U_A0",True)
        a25_off=scored(m,"U_A25",False)
        a25_on=scored(m,"U_A25",True)
        rows.append({
            "replicate":m["replicate"],
            "a0_off":a0_off,"a0_on":a0_on,
            "a25_off":a25_off,"a25_on":a25_on,
            "a0_damage_ratio":a0_on["result"]["correct_done"]/a0_off["result"]["correct_done"] if a0_off["result"]["correct_done"] else None,
            "a25_damage_ratio":a25_on["result"]["correct_done"]/a25_off["result"]["correct_done"] if a25_off["result"]["correct_done"] else None,
            "damaged_state_diverged":a0_on["result"]["state_sha256"]!=a25_on["result"]["state_sha256"],
        })

    mech=mechanical()
    damaged=[r[k] for r in rows for k in ("a0_on","a25_on")]
    a25_off_total=sum(r["a25_off"]["result"]["correct_done"] for r in rows)
    a25_on_total=sum(r["a25_on"]["result"]["correct_done"] for r in rows)
    a0_off_total=sum(r["a0_off"]["result"]["correct_done"] for r in rows)
    a0_on_total=sum(r["a0_on"]["result"]["correct_done"] for r in rows)

    branch_exact=all(
        x["branch"]["scheduled"]==8
        and x["branch"]["scheduled_b"]==4
        and x["branch"]["scheduled_c"]==4
        and x["branch"]["applied"]==8
        and x["branch"]["repaired"]==8
        and x["branch"]["all_repaired_before_d"]
        and x["branch"]["unrepaired_terminal"]==0
        and x["branch_stats"]["d_while_branch_incorrect"]==0
        for x in damaged
    )
    damaged_integrity=all(
        x["result"]["incorrect_done"]==0
        and x["result"]["matching_duplicate_cell"]==0
        and x["result"]["matching_duplicate_request"]==0
        and x["maturity"]["pass"]
        and x["horizon_aware_repair_integrity"]
        for x in damaged
    )
    a25_aggregate_ratio=a25_on_total/a25_off_total if a25_off_total else None
    a0_aggregate_ratio=a0_on_total/a0_off_total if a0_off_total else None
    q={
        "mechanical_gate":bool(mech["all_pass"]),
        "branch_schedule_and_repair_exact":branch_exact,
        "damaged_terminal_integrity_exact":damaged_integrity,
        "a25_aggregate_damage_ratio_ge_095":a25_aggregate_ratio is not None and a25_aggregate_ratio>=0.95,
        "all_a25_world_damage_ratio_ge_090":all(r["a25_damage_ratio"] is not None and r["a25_damage_ratio"]>=0.90 for r in rows),
        "learned_arm_materially_exercised_under_damage":any(r["damaged_state_diverged"] for r in rows),
        "damage_off_a7_aggregate_reproduced":a0_off_total==1438 and a25_off_total==1443,
    }
    return {
        "schema":1,
        "experiment":"YGG-A8",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "mechanical":mech,
        "aggregate":{
            "a0_off_correct_done":a0_off_total,
            "a0_on_correct_done":a0_on_total,
            "a0_damage_ratio":a0_aggregate_ratio,
            "a25_off_correct_done":a25_off_total,
            "a25_on_correct_done":a25_on_total,
            "a25_damage_ratio":a25_aggregate_ratio,
        },
        "qualification":q,
        "rows":rows,
    }

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    first=one_pass()
    second=one_pass()
    b1=canonical(first); b2=canonical(second)
    duplicate=b1==b2
    first["qualification"]["duplicate_complete_execution_byte_identical"]=duplicate
    first["qualification"]["YGG_A8_BRANCH_LOCAL_REPAIR"]=all(first["qualification"].values())
    out={
        "schema":1,
        "experiment":"YGG-A8",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "duplicate_byte_identical":duplicate,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "primary":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()

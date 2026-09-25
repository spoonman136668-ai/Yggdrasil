#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a8_branch_local_repair_v1 as a8

PREREG="2745c668b7d4d8d20ae86c98432648892c81345b"
PARENT_CLOSURE="c5ee026ed7ff5ec3aa10d9d509c219bcfc37a651"
DAMAGE_PER_WORLD=16
PARENT_DAMAGE_SCHEDULE=a8.damage_schedule

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def damage_schedule16(m):
    excluded=set(m["corrupt_ids"])
    candidates=[rid for rid in range(64) if rid not in excluded]
    ranked=sorted(
        candidates,
        key=lambda rid:(a8.p.h64("YGG-A8-BRANCH-DAMAGE",m["seed"],rid),rid),
    )
    chosen=ranked[:DAMAGE_PER_WORLD]
    out={}
    for rid in chosen[:4]:
        out[rid]="B"
    for rid in chosen[4:8]:
        out[rid]="C"
    for rid in chosen[8:12]:
        out[rid]="B"
    for rid in chosen[12:16]:
        out[rid]="C"

    parent=PARENT_DAMAGE_SCHEDULE(m)
    if len(out)!=16:
        raise AssertionError("A9 schedule cardinality")
    if sum(1 for x in out.values() if x=="B")!=8:
        raise AssertionError("A9 B schedule cardinality")
    if sum(1 for x in out.values() if x=="C")!=8:
        raise AssertionError("A9 C schedule cardinality")
    if set(out)&excluded:
        raise AssertionError("A9 branch/terminal corruption overlap")
    if any(out.get(rid)!=target for rid,target in parent.items()):
        raise AssertionError("A9 first eight assignments differ from A8")
    return out

def one_pass():
    old=a8.damage_schedule
    a8.damage_schedule=damage_schedule16
    try:
        parent=a8.one_pass()
    finally:
        a8.damage_schedule=old

    rows=parent["rows"]
    agg=parent["aggregate"]
    damaged=[r[k] for r in rows for k in ("a0_on","a25_on")]

    schedule_exact=all(
        x["branch"]["scheduled"]==16
        and x["branch"]["scheduled_b"]==8
        and x["branch"]["scheduled_c"]==8
        and x["branch"]["applied"]==16
        and x["branch"]["repaired"]==16
        and x["branch"]["all_repaired_before_d"]
        and x["branch"]["unrepaired_terminal"]==0
        and x["branch_stats"]["d_while_branch_incorrect"]==0
        for x in damaged
    )

    integrity=all(
        x["result"]["incorrect_done"]==0
        and x["result"]["matching_duplicate_cell"]==0
        and x["result"]["matching_duplicate_request"]==0
        and x["maturity"]["pass"]
        and x["horizon_aware_repair_integrity"]
        for x in damaged
    )

    lineage=True
    for row in rows:
        m=row["a0_on"]["manifest"]
        parent_sched=PARENT_DAMAGE_SCHEDULE(m)
        new_sched=damage_schedule16(m)
        lineage=lineage and len(parent_sched)==8
        lineage=lineage and all(new_sched.get(k)==v for k,v in parent_sched.items())

    q={
        "mechanical_gate":bool(parent["mechanical"]["all_pass"]),
        "nested_first_eight_a8_assignments_exact":bool(lineage),
        "branch_schedule_and_repair_exact_16":bool(schedule_exact),
        "damaged_terminal_integrity_exact":bool(integrity),
        "a25_aggregate_damage_ratio_ge_095":agg["a25_damage_ratio"] is not None and agg["a25_damage_ratio"]>=0.95,
        "all_a25_world_damage_ratio_ge_090":all(
            r["a25_damage_ratio"] is not None and r["a25_damage_ratio"]>=0.90
            for r in rows
        ),
        "learned_arm_materially_exercised_under_damage":any(r["damaged_state_diverged"] for r in rows),
        "damage_off_a7_a8_aggregate_reproduced":(
            agg["a0_off_correct_done"]==1438 and agg["a25_off_correct_done"]==1443
        ),
    }

    return {
        "schema":1,
        "experiment":"YGG-A9",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "mechanical":parent["mechanical"],
        "aggregate":agg,
        "qualification":q,
        "rows":rows,
    }

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    first=one_pass()
    second=one_pass()
    b1=canonical(first)
    b2=canonical(second)
    duplicate=b1==b2
    first["qualification"]["duplicate_complete_execution_byte_identical"]=duplicate
    first["qualification"]["YGG_A9_DOUBLED_BRANCH_REPAIR_LOAD"]=all(first["qualification"].values())
    out={
        "schema":1,
        "experiment":"YGG-A9",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "duplicate_byte_identical":duplicate,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "primary":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()

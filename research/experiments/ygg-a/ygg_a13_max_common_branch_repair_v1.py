#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a12_near_saturation_branch_repair_v1 as a12

PREREG="4b67797b4e123bfc29e805773722671c15dc9afa"
PARENT_CLOSURE="6d547932682313f3c2728f7440153ddc07922a75"
DAMAGE_PER_WORLD=58
a8=a12.a8
PARENT_A12_SCHEDULE=a12.damage_schedule56

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def damage_schedule58(m):
    excluded=set(m["corrupt_ids"])
    candidates=[rid for rid in range(64) if rid not in excluded]
    ranked=sorted(
        candidates,
        key=lambda rid:(a8.p.h64("YGG-A8-BRANCH-DAMAGE",m["seed"],rid),rid),
    )
    if len(ranked)<DAMAGE_PER_WORLD:
        raise AssertionError("A13 insufficient candidate pool")
    chosen=ranked[:DAMAGE_PER_WORLD]
    out={}
    for block_start in range(0,56,4):
        target="B" if (block_start//4)%2==0 else "C"
        for rid in chosen[block_start:block_start+4]:
            out[rid]=target
    out[chosen[56]]="B"
    out[chosen[57]]="C"

    parent=PARENT_A12_SCHEDULE(m)
    if len(out)!=58:
        raise AssertionError("A13 schedule cardinality")
    if sum(1 for x in out.values() if x=="B")!=29:
        raise AssertionError("A13 B cardinality")
    if sum(1 for x in out.values() if x=="C")!=29:
        raise AssertionError("A13 C cardinality")
    if set(out)&excluded:
        raise AssertionError("A13 terminal overlap")
    if any(out.get(k)!=v for k,v in parent.items()):
        raise AssertionError("A13 first 56 differ from A12")
    return out

def one_pass():
    old=a8.damage_schedule
    a8.damage_schedule=damage_schedule58
    try:
        parent=a8.one_pass()
    finally:
        a8.damage_schedule=old

    rows=parent["rows"]
    agg=parent["aggregate"]
    damaged=[r[k] for r in rows for k in ("a0_on","a25_on")]

    schedule_exact=all(
        x["branch"]["scheduled"]==58
        and x["branch"]["scheduled_b"]==29
        and x["branch"]["scheduled_c"]==29
        and x["branch"]["applied"]==58
        and x["branch"]["repaired"]==58
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
    min_eligible=64
    for row in rows:
        m=row["a0_on"]["manifest"]
        eligible=64-len([rid for rid in m["corrupt_ids"] if 0<=rid<64])
        min_eligible=min(min_eligible,eligible)
        p12=PARENT_A12_SCHEDULE(m)
        new=damage_schedule58(m)
        lineage=lineage and len(p12)==56 and len(new)==58
        lineage=lineage and all(new.get(k)==v for k,v in p12.items())

    q={
        "mechanical_gate":bool(parent["mechanical"]["all_pass"]),
        "minimum_eligible_pool_ge_58":min_eligible>=58,
        "nested_first_56_a12_assignments_exact":bool(lineage),
        "branch_schedule_and_repair_exact_58":bool(schedule_exact),
        "damaged_terminal_integrity_exact":bool(integrity),
        "a25_aggregate_damage_ratio_ge_095":agg["a25_damage_ratio"] is not None and agg["a25_damage_ratio"]>=0.95,
        "all_a25_world_damage_ratio_ge_090":all(
            r["a25_damage_ratio"] is not None and r["a25_damage_ratio"]>=0.90
            for r in rows
        ),
        "learned_arm_materially_exercised_under_damage":any(r["damaged_state_diverged"] for r in rows),
        "damage_off_aggregate_reproduced":(
            agg["a0_off_correct_done"]==1438 and agg["a25_off_correct_done"]==1443
        ),
    }

    return {
        "schema":1,
        "experiment":"YGG-A13",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "mechanical":parent["mechanical"],
        "aggregate":agg,
        "minimum_eligible_pool":min_eligible,
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
    first["qualification"]["YGG_A13_MAX_COMMON_BRANCH_REPAIR"]=all(first["qualification"].values())
    out={
        "schema":1,
        "experiment":"YGG-A13",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "duplicate_byte_identical":duplicate,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "primary":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()

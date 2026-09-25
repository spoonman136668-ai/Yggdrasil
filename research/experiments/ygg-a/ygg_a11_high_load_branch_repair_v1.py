#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a10_quadrupled_branch_repair_load_v1 as a10

PREREG="99608e34dbcaacc0a7c87dee00545355a4024ceb"
PARENT_CLOSURE="1b909266d35c14b47904e2d4b5010a8b8f09fc0"
DAMAGE_PER_WORLD=48
a8=a10.a8
PARENT_A8_SCHEDULE=a10.PARENT_A8_SCHEDULE
PARENT_A9_SCHEDULE=a10.PARENT_A9_SCHEDULE
PARENT_A10_SCHEDULE=a10.damage_schedule32

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def damage_schedule48(m):
    excluded=set(m["corrupt_ids"])
    candidates=[rid for rid in range(64) if rid not in excluded]
    ranked=sorted(
        candidates,
        key=lambda rid:(a8.p.h64("YGG-A8-BRANCH-DAMAGE",m["seed"],rid),rid),
    )
    if len(ranked)<DAMAGE_PER_WORLD:
        raise AssertionError("A11 insufficient candidate pool")
    chosen=ranked[:DAMAGE_PER_WORLD]
    out={}
    for block_start in range(0,DAMAGE_PER_WORLD,4):
        target="B" if (block_start//4)%2==0 else "C"
        for rid in chosen[block_start:block_start+4]:
            out[rid]=target

    p8=PARENT_A8_SCHEDULE(m)
    p9=PARENT_A9_SCHEDULE(m)
    p10=PARENT_A10_SCHEDULE(m)
    if len(out)!=48:
        raise AssertionError("A11 schedule cardinality")
    if sum(1 for x in out.values() if x=="B")!=24:
        raise AssertionError("A11 B schedule cardinality")
    if sum(1 for x in out.values() if x=="C")!=24:
        raise AssertionError("A11 C schedule cardinality")
    if set(out)&excluded:
        raise AssertionError("A11 branch/terminal corruption overlap")
    if any(out.get(rid)!=target for rid,target in p8.items()):
        raise AssertionError("A11 first eight assignments differ from A8")
    if any(out.get(rid)!=target for rid,target in p9.items()):
        raise AssertionError("A11 first sixteen assignments differ from A9")
    if any(out.get(rid)!=target for rid,target in p10.items()):
        raise AssertionError("A11 first thirty-two assignments differ from A10")
    return out

def one_pass():
    old=a8.damage_schedule
    a8.damage_schedule=damage_schedule48
    try:
        parent=a8.one_pass()
    finally:
        a8.damage_schedule=old

    rows=parent["rows"]
    agg=parent["aggregate"]
    damaged=[r[k] for r in rows for k in ("a0_on","a25_on")]

    schedule_exact=all(
        x["branch"]["scheduled"]==48
        and x["branch"]["scheduled_b"]==24
        and x["branch"]["scheduled_c"]==24
        and x["branch"]["applied"]==48
        and x["branch"]["repaired"]==48
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
        p8=PARENT_A8_SCHEDULE(m)
        p9=PARENT_A9_SCHEDULE(m)
        p10=PARENT_A10_SCHEDULE(m)
        new=damage_schedule48(m)
        lineage=lineage and len(p8)==8 and len(p9)==16 and len(p10)==32 and len(new)==48
        lineage=lineage and all(new.get(k)==v for k,v in p8.items())
        lineage=lineage and all(new.get(k)==v for k,v in p9.items())
        lineage=lineage and all(new.get(k)==v for k,v in p10.items())

    q={
        "mechanical_gate":bool(parent["mechanical"]["all_pass"]),
        "nested_a8_a9_a10_assignments_exact":bool(lineage),
        "branch_schedule_and_repair_exact_48":bool(schedule_exact),
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
        "experiment":"YGG-A11",
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
    first["qualification"]["YGG_A11_HIGH_LOAD_BRANCH_REPAIR"]=all(first["qualification"].values())
    out={
        "schema":1,
        "experiment":"YGG-A11",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "duplicate_byte_identical":duplicate,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "primary":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()

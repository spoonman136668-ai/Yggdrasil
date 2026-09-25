#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a9_doubled_branch_repair_load_v1 as a9

PREREG="9b694e31952ae90a5e843b1eb8eb26005aa61127"
PARENT_CLOSURE="22ba556b651fe865e70288d33f1aba800defa66a"
DAMAGE_PER_WORLD=32
a8=a9.a8
PARENT_A8_SCHEDULE=a9.PARENT_DAMAGE_SCHEDULE
PARENT_A9_SCHEDULE=a9.damage_schedule16

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def damage_schedule32(m):
    excluded=set(m["corrupt_ids"])
    candidates=[rid for rid in range(64) if rid not in excluded]
    ranked=sorted(
        candidates,
        key=lambda rid:(a8.p.h64("YGG-A8-BRANCH-DAMAGE",m["seed"],rid),rid),
    )
    chosen=ranked[:DAMAGE_PER_WORLD]
    if len(chosen)!=32:
        raise AssertionError("A10 insufficient candidate pool")
    out={}
    for block_start in range(0,32,4):
        target="B" if (block_start//4)%2==0 else "C"
        for rid in chosen[block_start:block_start+4]:
            out[rid]=target

    p8=PARENT_A8_SCHEDULE(m)
    p9=PARENT_A9_SCHEDULE(m)
    if len(out)!=32:
        raise AssertionError("A10 schedule cardinality")
    if sum(1 for x in out.values() if x=="B")!=16:
        raise AssertionError("A10 B schedule cardinality")
    if sum(1 for x in out.values() if x=="C")!=16:
        raise AssertionError("A10 C schedule cardinality")
    if set(out)&excluded:
        raise AssertionError("A10 branch/terminal corruption overlap")
    if any(out.get(rid)!=target for rid,target in p8.items()):
        raise AssertionError("A10 first eight assignments differ from A8")
    if any(out.get(rid)!=target for rid,target in p9.items()):
        raise AssertionError("A10 first sixteen assignments differ from A9")
    return out

def one_pass():
    old=a8.damage_schedule
    a8.damage_schedule=damage_schedule32
    try:
        parent=a8.one_pass()
    finally:
        a8.damage_schedule=old

    rows=parent["rows"]
    agg=parent["aggregate"]
    damaged=[r[k] for r in rows for k in ("a0_on","a25_on")]

    schedule_exact=all(
        x["branch"]["scheduled"]==32
        and x["branch"]["scheduled_b"]==16
        and x["branch"]["scheduled_c"]==16
        and x["branch"]["applied"]==32
        and x["branch"]["repaired"]==32
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
        new=damage_schedule32(m)
        lineage=lineage and len(p8)==8 and len(p9)==16 and len(new)==32
        lineage=lineage and all(new.get(k)==v for k,v in p8.items())
        lineage=lineage and all(new.get(k)==v for k,v in p9.items())

    q={
        "mechanical_gate":bool(parent["mechanical"]["all_pass"]),
        "nested_first_eight_a8_assignments_exact":bool(lineage),
        "nested_first_sixteen_a9_assignments_exact":bool(lineage),
        "branch_schedule_and_repair_exact_32":bool(schedule_exact),
        "damaged_terminal_integrity_exact":bool(integrity),
        "a25_aggregate_damage_ratio_ge_095":agg["a25_damage_ratio"] is not None and agg["a25_damage_ratio"]>=0.95,
        "all_a25_world_damage_ratio_ge_090":all(
            r["a25_damage_ratio"] is not None and r["a25_damage_ratio"]>=0.90
            for r in rows
        ),
        "learned_arm_materially_exercised_under_damage":any(r["damaged_state_diverged"] for r in rows),
        "damage_off_a7_a8_a9_aggregate_reproduced":(
            agg["a0_off_correct_done"]==1438 and agg["a25_off_correct_done"]==1443
        ),
    }

    return {
        "schema":1,
        "experiment":"YGG-A10",
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
    first["qualification"]["YGG_A10_QUADRUPLED_BRANCH_REPAIR_LOAD"]=all(first["qualification"].values())
    out={
        "schema":1,
        "experiment":"YGG-A10",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "duplicate_byte_identical":duplicate,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "primary":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()

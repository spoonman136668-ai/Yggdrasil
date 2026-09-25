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

PREREG="fa24a72c0a0f9e9a2c602d0acb4b85e99eb3fa94"
PARENT_CLOSURE="c2432d153f6e21e89173cd46e5ee822b65a5df86"
A1_PREREG=a1.PREREG

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def run_world_mode(m,mode):
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
        a4.atomic_do_op(stats,seed,tick,cell,name,r,trace)
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
        result,history,telemetry=g.run_world(m,mode)
    finally:
        g.Task2Request,g.task2_op,g.do_operation,g.expected_pair,g.validate_manifest,g.REQUESTS_PER_EPOCH=old
    return result,history,telemetry,registry,detected,stats

def scored(m,mode):
    t.validate_manifest(m)
    result,history,telemetry,registry,detected,stats=run_world_mode(m,mode)
    row={
        "manifest":m,
        "mode":mode,
        "result":g.compact(result),
        "maturity":a1.maturity_summary(m,registry,detected),
        "atomic":stats,
        "target_141":{
            "present":141 in registry,
            "stage":registry[141].stage if 141 in registry else None,
            "detected":registry[141].detected if 141 in registry else None,
            "repaired":registry[141].repaired if 141 in registry else None,
            "first_egress_epoch":registry[141].first_egress_epoch if 141 in registry else None,
        },
        "telemetry":telemetry,
    }
    summary=a6.summarize_world(row)
    row["horizon_aware_repair_integrity"]=summary["horizon_aware_repair_integrity"]
    row["terminal159_count"]=summary["terminal159_count"]
    row["terminal159_rows"]=summary["terminal159_rows"]
    return row

def one_pass():
    manifests=t.primary_manifests(A1_PREREG)
    pairs=[]
    for m in manifests:
        a0=scored(m,"U_A0")
        a25=scored(m,"U_A25")
        ratio=(a25["result"]["correct_done"]/a0["result"]["correct_done"]) if a0["result"]["correct_done"] else None
        pairs.append({
            "replicate":m["replicate"],
            "a0":a0,
            "a25":a25,
            "correct_done_ratio":ratio,
            "state_diverged":a0["result"]["state_sha256"]!=a25["result"]["state_sha256"],
        })

    a0_total=sum(x["a0"]["result"]["correct_done"] for x in pairs)
    a25_total=sum(x["a25"]["result"]["correct_done"] for x in pairs)
    aggregate_ratio=a25_total/a0_total if a0_total else None
    mech=a4.mechanical()
    q={
        "all_a25_horizon_aware_repair_integrity":all(x["a25"]["horizon_aware_repair_integrity"] for x in pairs),
        "all_a25_zero_incorrect_done":all(x["a25"]["result"]["incorrect_done"]==0 for x in pairs),
        "all_a25_matching_integrity":all(
            x["a25"]["result"]["matching_duplicate_cell"]==0 and x["a25"]["result"]["matching_duplicate_request"]==0
            for x in pairs
        ),
        "all_a25_maturity_pass":all(x["a25"]["maturity"]["pass"] for x in pairs),
        "aggregate_a25_vs_a0_correct_done_ge_095":aggregate_ratio is not None and aggregate_ratio>=0.95,
        "all_world_a25_vs_a0_correct_done_ge_090":all(x["correct_done_ratio"] is not None and x["correct_done_ratio"]>=0.90 for x in pairs),
        "learned_arm_materially_exercised":any(x["state_diverged"] for x in pairs),
        "fork_join_mechanical_fixture_exact":bool(mech["all_pass"]),
    }
    return {
        "schema":1,
        "experiment":"YGG-A7",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "aggregate_a0_correct_done":a0_total,
        "aggregate_a25_correct_done":a25_total,
        "aggregate_a25_vs_a0_correct_done_ratio":aggregate_ratio,
        "state_divergence_count":sum(1 for x in pairs if x["state_diverged"]),
        "mechanical":mech,
        "qualification":q,
        "pairs":pairs,
    }

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    first=one_pass()
    second=one_pass()
    b1=canonical(first)
    b2=canonical(second)
    duplicate=b1==b2
    first["qualification"]["duplicate_complete_paired_execution_byte_identical"]=duplicate
    first["qualification"]["YGG_A7_LEARNED_ARM_INTEGRITY_COMPATIBILITY"]=all(first["qualification"].values())
    out={
        "schema":1,
        "experiment":"YGG-A7",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "duplicate_byte_identical":duplicate,
        "duplicate_sha256":hashlib.sha256(b1).hexdigest(),
        "primary":first,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()

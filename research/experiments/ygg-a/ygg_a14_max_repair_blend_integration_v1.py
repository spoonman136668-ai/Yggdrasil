#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a13_max_common_branch_repair_v1 as a13

PREREG="eb9732a48950ed8b1437b3ddb7a22fcb883caa05"
PARENT_CLOSURE="93d5b08fd6e89b745105f76ec3ab958aa07bb8c6"
ALPHAS=(0.25,0.50)
A13_ACCEPTED_HASH="ac93fda604f8da8aa3149c0251d74470ec65e052cfbeb1c685446491cb1c636c"
g=a13.a8.g

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def integration_checks(result):
    q=result["qualification"]
    return {
        "mechanical_gate":bool(q["mechanical_gate"]),
        "minimum_eligible_pool_ge_58":bool(q["minimum_eligible_pool_ge_58"]),
        "nested_first_56_a12_assignments_exact":bool(q["nested_first_56_a12_assignments_exact"]),
        "branch_schedule_and_repair_exact_58":bool(q["branch_schedule_and_repair_exact_58"]),
        "damaged_terminal_integrity_exact":bool(q["damaged_terminal_integrity_exact"]),
        "a25_aggregate_damage_ratio_ge_095":bool(q["a25_aggregate_damage_ratio_ge_095"]),
        "all_a25_world_damage_ratio_ge_090":bool(q["all_a25_world_damage_ratio_ge_090"]),
        "learned_arm_materially_exercised_under_damage":bool(q["learned_arm_materially_exercised_under_damage"]),
    }

def run_alpha(alpha):
    if alpha not in ALPHAS:
        raise AssertionError("unregistered alpha")
    if not hasattr(g,"ALPHA"):
        raise AssertionError("runtime ALPHA unavailable")
    old=float(g.ALPHA)
    g.ALPHA=float(alpha)
    try:
        first=a13.one_pass()
        second=a13.one_pass()
    finally:
        g.ALPHA=old

    b1=canonical(first)
    b2=canonical(second)
    return {
        "alpha":alpha,
        "duplicate_byte_identical":b1==b2,
        "evidence_sha256":hashlib.sha256(b1).hexdigest(),
        "runtime_alpha_restored":float(g.ALPHA)==old,
        "aggregate":first["aggregate"],
        "checks":integration_checks(first),
        "all_integration_gates":all(integration_checks(first).values()),
    }

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    if not hasattr(g,"ALPHA"):
        raise SystemExit("YGG_A14_ALPHA_CONTROL_UNAVAILABLE")

    before=float(g.ALPHA)
    rows=[run_alpha(a) for a in ALPHAS]
    by={float(r["alpha"]):r for r in rows}

    validity={
        "alpha_levels_exact":[r["alpha"] for r in rows]==list(ALPHAS),
        "alpha025_a13_anchor_exact":by[0.25]["evidence_sha256"]==A13_ACCEPTED_HASH,
        "alpha025_duplicate_exact":bool(by[0.25]["duplicate_byte_identical"]),
        "alpha050_duplicate_exact":bool(by[0.50]["duplicate_byte_identical"]),
        "alpha025_runtime_restored":bool(by[0.25]["runtime_alpha_restored"]),
        "alpha050_runtime_restored":bool(by[0.50]["runtime_alpha_restored"]),
        "runtime_alpha_restored_final":float(g.ALPHA)==before,
    }
    qualification={
        "YGG_A14_MAX_REPAIR_BLEND_INTEGRATION":bool(
            all(validity.values()) and by[0.50]["all_integration_gates"]
        ),
        "alpha050_integration_gates":by[0.50]["checks"],
        "alpha050_aggregate":by[0.50]["aggregate"],
    }
    out={
        "schema":1,
        "experiment":"YGG-A14",
        "prereg":PREREG,
        "parent_closure":PARENT_CLOSURE,
        "alphas":list(ALPHAS),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":qualification,
        "alpha_results":rows,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()

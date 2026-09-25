#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_a14_max_repair_blend_integration_v1 as a14

PREREG="e16bc62d6e1b7001a994a22aa5020c0249576464"
PARENT_CLOSURE="ee3e1710939fed04c51dc4602adec963d1ed5799"
ALPHAS=(0.50,1.00)
A14_ALPHA050_HASH="5b8cc8a5c6c2732000fee3efe0bf6ee01fa7b86484d927e92234e977bd95ab9f"
a13=a14.a13
g=a14.g

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def run_alpha(alpha):
    if alpha not in ALPHAS:
        raise AssertionError("unregistered alpha")
    old=float(g.ALPHA)
    g.ALPHA=float(alpha)
    try:
        first=a13.one_pass()
        second=a13.one_pass()
    finally:
        g.ALPHA=old
    b1=canonical(first)
    b2=canonical(second)
    checks=a14.integration_checks(first)
    return {
        "alpha":alpha,
        "duplicate_byte_identical":b1==b2,
        "evidence_sha256":hashlib.sha256(b1).hexdigest(),
        "runtime_alpha_restored":float(g.ALPHA)==old,
        "aggregate":first["aggregate"],
        "checks":checks,
        "all_integration_gates":all(checks.values()),
    }

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    if not hasattr(g,"ALPHA"):
        raise SystemExit("YGG_A15_ALPHA_CONTROL_UNAVAILABLE")
    before=float(g.ALPHA)
    rows=[run_alpha(a) for a in ALPHAS]
    by={float(r["alpha"]):r for r in rows}

    validity={
        "alpha_levels_exact":[r["alpha"] for r in rows]==list(ALPHAS),
        "alpha050_a14_anchor_exact":by[0.50]["evidence_sha256"]==A14_ALPHA050_HASH,
        "alpha050_duplicate_exact":bool(by[0.50]["duplicate_byte_identical"]),
        "alpha100_duplicate_exact":bool(by[1.00]["duplicate_byte_identical"]),
        "alpha050_runtime_restored":bool(by[0.50]["runtime_alpha_restored"]),
        "alpha100_runtime_restored":bool(by[1.00]["runtime_alpha_restored"]),
        "runtime_alpha_restored_final":float(g.ALPHA)==before,
    }
    qualification={
        "YGG_A15_FULL_BLEND_MAX_REPAIR_INTEGRATION":bool(
            all(validity.values()) and by[1.00]["all_integration_gates"]
        ),
        "alpha100_integration_gates":by[1.00]["checks"],
        "alpha100_aggregate":by[1.00]["aggregate"],
    }
    out={
        "schema":1,
        "experiment":"YGG-A15",
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

#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b65_prevention_collateral_ledger_v1 as b65
import ygg_b66_matched_intervention_cohort_decomposition_v1 as b66

PREREG="c7759178229ea2aafb6e27c334882c5996f3bcff"
PARENT_RUN="36482941191"
ANCHOR_SEEDS=[2888,2999,3111,3222,3333]
PARENT_B66_SEEDS=[3444,3555,3666,3777,3888]
SHARED_KEYS=(
    "control_failures_by6",
    "gated_failures_by6",
    "d5_failures_by6",
    "gated_interventions",
    "d5_interventions",
    "gated_final_target_accuracy",
    "d5_final_target_accuracy",
    "gated_collateral_new_error_count",
    "gated_collateral_repair_count",
    "d5_collateral_new_error_count",
    "d5_collateral_repair_count",
)

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def b65_shared(a):
    return {k:a[k] for k in SHARED_KEYS}

def b66_shared(a):
    f=a["full_population"]
    return {k:f[k] for k in SHARED_KEYS}

def b66_with_seeds(seeds):
    old=list(b66.SEEDS)
    try:
        b66.SEEDS=list(seeds)
        return b66.one()
    finally:
        b66.SEEDS=old

def one():
    a65=b65.one()
    a66_parent=b66.one()
    a66_anchor=b66_with_seeds(ANCHOR_SEEDS)
    m65=b65_shared(a65)
    m66=b66_shared(a66_anchor)
    metrics_equal=(m65==m66)
    b65_anchor=(a65["classification"]=="D5_PARETO_DOMINATES_SIGNAL")
    b66_parent_anchor=(a66_parent["classification"]=="ANCHOR_NOT_REPRODUCED")
    anchor_pareto=bool(a66_anchor["full_population_d5_pareto"])
    if not metrics_equal:
        cat="INSTRUMENTATION_DRIFT"
    elif not b65_anchor:
        cat="B65_ANCHOR_NOT_REPRODUCED"
    elif not b66_parent_anchor:
        cat="PARENT_B66_NOT_REPRODUCED"
    elif anchor_pareto:
        cat="SEED_COHORT_SENSITIVITY"
    else:
        cat="OTHER_VALID_PATTERN"
    return {
        "classification":cat,
        "b65_classification":a65["classification"],
        "parent_b66_classification":a66_parent["classification"],
        "anchor_b66_classification":a66_anchor["classification"],
        "anchor_b66_full_population_d5_pareto":anchor_pareto,
        "b65_shared_metrics":m65,
        "b66_anchor_shared_metrics":m66,
        "shared_metrics_exact":metrics_equal,
        "anchor_b66_cohorts":a66_anchor["cohorts"],
        "anchor_seeds":ANCHOR_SEEDS,
        "parent_b66_seeds":PARENT_B66_SEEDS,
        "gate":b66.GATE,
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "prereg_commit_exact":PREREG=="c7759178229ea2aafb6e27c334882c5996f3bcff",
        "anchor_seeds_exact":a["anchor_seeds"]==ANCHOR_SEEDS,
        "parent_b66_seeds_exact":a["parent_b66_seeds"]==PARENT_B66_SEEDS and b66.SEEDS==PARENT_B66_SEEDS,
        "q_positions_exact":b65.QPOS==[0,1,2,3,4] and b66.QPOS==[0,1,2,3,4],
        "gate_bit_exact":a["gate"]==b65.GATE==b66.GATE==2.6009554862976074,
        "b65_parent_anchor_exact":a["b65_classification"]=="D5_PARETO_DOMINATES_SIGNAL",
        "b66_parent_anchor_exact":a["parent_b66_classification"]=="ANCHOR_NOT_REPRODUCED",
        "shared_metrics_exact":a["shared_metrics_exact"],
        "state_exact":b65.b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b65.b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"SEED_COHORT_SENSITIVITY","OTHER_VALID_PATTERN"}
    out={
        "schema":1,
        "experiment":"YGG-B67",
        "prereg":PREREG,
        "parent_run":PARENT_RUN,
        "duplicate_sha256":hashlib.sha256(ba).hexdigest(),
        "validity":validity,
        "valid":all(validity.values()),
        "qualification":{
            "YGG_B67_ANCHOR_COHORT_REPRODUCTION_BRIDGE":all(validity.values()) and cat in allowed,
            "classification":cat,
        },
        "analysis":a,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__": main()

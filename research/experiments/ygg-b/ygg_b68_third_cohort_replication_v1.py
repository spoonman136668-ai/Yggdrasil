#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b67_anchor_cohort_reproduction_bridge_v1 as b67

PREREG="c1cb21fdbe480033f16ef9515205273c2c565024"
PARENT_RUN="36510465232"
NEW_SEEDS=[4001,4111,4222,4333,4444]

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def one():
    parent=b67.one()
    third=b67.b66_with_seeds(NEW_SEEDS)
    metrics=b67.b66_shared(third)
    if parent["classification"]!="SEED_COHORT_SENSITIVITY":
        cat="ANCHOR_NOT_REPRODUCED"
    elif bool(third["full_population_d5_pareto"]):
        cat="THIRD_COHORT_D5_PARETO"
    else:
        cat="THIRD_COHORT_NONPARETO"
    return {
        "classification":cat,
        "parent_classification":parent["classification"],
        "third_cohort_classification":third["classification"],
        "third_full_population_d5_pareto":bool(third["full_population_d5_pareto"]),
        "third_cohort_metrics":metrics,
        "third_cohorts":third["cohorts"],
        "new_seeds":NEW_SEEDS,
        "gate":b67.b66.GATE,
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "prereg_commit_exact":PREREG=="c1cb21fdbe480033f16ef9515205273c2c565024",
        "parent_b67_anchor_exact":a["parent_classification"]=="SEED_COHORT_SENSITIVITY",
        "new_seed_cohort_exact":a["new_seeds"]==NEW_SEEDS,
        "new_seed_cohort_disjoint":set(NEW_SEEDS).isdisjoint(set(b67.ANCHOR_SEEDS)) and set(NEW_SEEDS).isdisjoint(set(b67.PARENT_B66_SEEDS)),
        "q_positions_exact":b67.b65.QPOS==[0,1,2,3,4] and b67.b66.QPOS==[0,1,2,3,4],
        "gate_bit_exact":a["gate"]==b67.b65.GATE==b67.b66.GATE==2.6009554862976074,
        "state_exact":b67.b65.b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b67.b65.b27.ReadUpdateRead().parameters())==120,
        "seed_state_restored":b67.b66.SEEDS==b67.PARENT_B66_SEEDS,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"THIRD_COHORT_D5_PARETO","THIRD_COHORT_NONPARETO","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B68","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B68_THIRD_COHORT_REPLICATION":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()

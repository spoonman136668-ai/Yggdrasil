#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b68_third_cohort_replication_v1 as b68

PREREG="f24a0304514c0d95c08e91bf5b1957b4ce59276f"
PARENT_RUN="36529446659"
NEW_SEEDS=[4555,4666,4777,4888,4999]

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def one():
    parent=b68.one()
    fourth=b68.b67.b66_with_seeds(NEW_SEEDS)
    metrics=b68.b67.b66_shared(fourth)
    if parent["classification"]!="THIRD_COHORT_NONPARETO":
        cat="ANCHOR_NOT_REPRODUCED"
    elif bool(fourth["full_population_d5_pareto"]):
        cat="FOURTH_COHORT_D5_PARETO"
    else:
        cat="FOURTH_COHORT_NONPARETO"
    return {
        "classification":cat,
        "parent_classification":parent["classification"],
        "fourth_cohort_classification":fourth["classification"],
        "fourth_full_population_d5_pareto":bool(fourth["full_population_d5_pareto"]),
        "fourth_cohort_metrics":metrics,
        "fourth_cohorts":fourth["cohorts"],
        "new_seeds":NEW_SEEDS,
        "gate":b68.b67.b66.GATE,
    }

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    old1=set(b68.NEW_SEEDS); old2=set(b68.b67.ANCHOR_SEEDS); old3=set(b68.b67.PARENT_B66_SEEDS)
    validity={
        "prereg_commit_exact":PREREG=="f24a0304514c0d95c08e91bf5b1957b4ce59276f",
        "parent_b68_anchor_exact":a["parent_classification"]=="THIRD_COHORT_NONPARETO",
        "new_seed_cohort_exact":a["new_seeds"]==NEW_SEEDS,
        "new_seed_cohort_disjoint":set(NEW_SEEDS).isdisjoint(old1|old2|old3),
        "q_positions_exact":b68.b67.b65.QPOS==[0,1,2,3,4] and b68.b67.b66.QPOS==[0,1,2,3,4],
        "gate_bit_exact":a["gate"]==b68.b67.b65.GATE==b68.b67.b66.GATE==2.6009554862976074,
        "state_exact":b68.b67.b65.b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b68.b67.b65.b27.ReadUpdateRead().parameters())==120,
        "seed_state_restored":b68.b67.b66.SEEDS==b68.b67.PARENT_B66_SEEDS,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"FOURTH_COHORT_D5_PARETO","FOURTH_COHORT_NONPARETO","OTHER_VALID_PATTERN"}
    out={"schema":1,"experiment":"YGG-B69","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B69_FOURTH_COHORT_REPLICATION":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()

"""Read-only evidence and numerical conservation checks for CKAD21."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical,digest
ARMS=("two_timescale_dynamic","two_timescale_static","early_only","late_only",
      "native_ckad20","full_beta","trailing64_mle")
COHORTS=("eval-0","eval-1","eval-2","eval-3")
SEEDS=(101,202,303)
SOURCE_PIN="20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"
PARENT_SHA="d8f27db46af889afdfeb104fc471a710fc6d5c06"


def need(ok,msg):
    if not ok:raise ValueError("CKAD21_AUDIT_"+msg)


def audit(result):
    need(type(result) is dict and result.get("schema")=="yggdrasil.ckad21.two-timescale-belief-result.v1",
         "SCHEMA")
    stable={k:v for k,v in result.items() if k not in ("stable_sha256","whole_wall_seconds")}
    need(digest(canonical(stable))==result["stable_sha256"],"STABLE_PIN")
    need(result["source_sha256"]==SOURCE_PIN and result["parent_sha"]==PARENT_SHA,"SOURCE_OR_PARENT")
    need(result["training_updates"]==result["held_training_updates"]==result["new_original_source_actions"]==
         result["checkpoint_mutations"]==result["source_owner_mutations"]==0,"MUTATIONS")
    need(result["scientific_pass"] is False and result["accepted_native"] is False
         and result["deployment"]=="NONE", "NO_PROMOTION")
    need(result["seeds"]==list(SEEDS) and len(result["per_seed"])==3,"SEED_SCOPE")
    need(result["formula_parity_checks"]==96 and result["cases_per_cohort"]==288,"FORMULA_SCOPE")
    reconstructed={cohort:{arm:0 for arm in ARMS} for cohort in COHORTS}
    seen=set()
    for row in result["per_seed"]:
        seed=row["seed"]
        need(seed in SEEDS and seed not in seen,"DUPLICATE_SEED")
        seen.add(seed)
        need(row["training_episodes"]==224 and row["anchor_episodes"]==64
             and row["recent_episodes"]==96,"EVIDENCE_COUNT")
        need(row["projection"] in (0,1),"PUBLIC_PROJECTION")
        for cohort in COHORTS:
            entry=row["evaluation"][cohort]
            need(entry["denominator"]==96,"HELD_SCOPE")
            need(set(entry["successes"])==set(ARMS)
                 and set(entry["trace_sha256"])==set(ARMS),"ARM_SCOPE")
            for arm in ARMS:
                val=entry["successes"][arm]
                need(type(val) is int and 0<=val<=96,"EXECUTED_REWARD")
                sha=entry["trace_sha256"][arm]
                need(type(sha) is str and len(sha)==64 and all(v in "0123456789abcdef" for v in sha),
                     "EPISODE_TRACE")
                reconstructed[cohort][arm]+=val
    need(reconstructed==result["totals"],"TOTALS")
    need((reconstructed["eval-0"]["native_ckad20"],reconstructed["eval-2"]["native_ckad20"])==
         (204,227),"LEGACY_NATIVE_REWARD")
    g={
      "prior_retention":reconstructed["eval-0"]["two_timescale_dynamic"]>=233,
      "shift_vs_strongest_control":reconstructed["eval-2"]["two_timescale_dynamic"]>=245,
      "mixture_vs_static_prior":reconstructed["eval-0"]["two_timescale_dynamic"]>=
                                reconstructed["eval-0"]["two_timescale_static"]+6,
      "mixture_vs_static_shift":reconstructed["eval-2"]["two_timescale_dynamic"]>=
                                reconstructed["eval-2"]["two_timescale_static"]+6
    }
    need(result["gates"]==g and result["classification"]==
         ("DEVELOPMENT_GO" if all(g.values()) else "DEVELOPMENT_NO_GO"),"FROZEN_GATES")
    return {"result":"PASS","cases":1152,"seed_groups":3,
            "stable_sha256":result["stable_sha256"],
            "development":result["classification"],"frozen_gates":g,
            "scientific_pass":False,"deployment":"NONE"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--result",type=Path,default=HERE/"result.json")
    a=p.parse_args()
    print(json.dumps(audit(json.loads(a.result.read_text())),sort_keys=True))

"""WSP96 exact public development receipt is NOT independent science authority.

Public successful GitHub job IDs, SHA, hashes and every frozen check must be
verified outside this schema before authoring a source-controlled receipt.
This verifier only checks a sealed receipt for internal contradictions.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
FILE=HERE/"PUBLIC_PASS.json"
PREREG="6bf44edc2c45f62142f70ff15c5ba8bbcf95a485"

def verify_public_positive()->dict:
    v=json.loads(FILE.read_text(encoding="utf-8"))
    score=v.get("correct",{})
    if (v.get("schema")!="wsp96.verified-public-hidden-confounder-do.v1"
        or v.get("prereg_commit")!=PREREG
        or v.get("classification")!="PUBLIC_HIDDEN_CONFOUNDER_DO_FEASIBLE"
        or v.get("ubuntu")!="success" or v.get("windows")!="success"
        or v.get("attempt")!=1
        or type(v.get("run_id")) is not int or v["run_id"]<1
        or len(v.get("exact_sha",""))!=40
        or v.get("total_checks",0)<17
        or v.get("passed_checks")!=v["total_checks"]
        or v.get("worlds")!=12 or v.get("goals")!=240
        or v.get("real_randomized_do_interventions")!=1728
        or v.get("passively_logged_observations")!=1728
        or score.get("direct_do",0)<200
        or score.get("fully_trained_logistic_do",0)<190
        or score.get("independent_symbolic_do")!=score.get("direct_do")
        or score.get("oracle_upper_bound")!=240
        or score.get("direct_do",0)-score.get("naive_observational_only",10000)<35
        or score.get("direct_do",0)-score.get("shuffled_action_mapping",10000)<75
        or v.get("true_do_effect_bits_correct",0)/360<.94
        or v.get("ordinary_do_effect_bits_correct",0)/360<.93
        or v.get("latent_action_assignment_shift_worlds",0)<10
        or v.get("naive_favorite_misbound_worlds",0)<8
        or not isinstance(v.get("per_world_prediction_sha256"),list)
        or len(v["per_world_prediction_sha256"])!=12
        or any(not isinstance(x,str) or len(x)!=64 for x in
               v["per_world_prediction_sha256"])):
        raise ValueError("WSP96 original dual-OS public development admission invalid")
    return v

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--public-pass",required=True,action="store_true")
    ap.parse_args()
    receipt=verify_public_positive()
    print("WSP96_PUBLIC_RECEIPT_VERIFIED="+json.dumps({
        "source_sha":receipt["exact_sha"],
        "run_id":receipt["run_id"],
        "classification":receipt["classification"],
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()

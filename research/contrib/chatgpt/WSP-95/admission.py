"""WSP95 public development qualification receipt schema.

Source-controlled corroboration is advisory, not scientific-first-use or
execution authority. Original GitHub workflow jobs/source SHA must be checked
before creating any positive receipt; no receipt may be forged from fixture
tests alone.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
FILE=HERE/"PUBLIC_PASS.json"
PREREG="5b9bf6780a2073ed3223892ca0582cfdc1288d8f"

def read():
    x=json.loads(FILE.read_text(encoding="utf-8"))
    c=x.get("correct",{})
    if (x.get("schema")!="wsp95.public-development-dual-platform-receipt.v1" or
        x.get("prereg_commit")!=PREREG or
        x.get("classification")!="PUBLIC_NOISY_CAUSAL_SLOTS_FEASIBLE" or
        type(x.get("run_id")) is not int or x["run_id"]<=0 or
        x.get("run_attempt")!=1 or
        x.get("ubuntu")!="success" or x.get("windows")!="success" or
        not isinstance(x.get("exact_source_sha"),str) or
        len(x["exact_source_sha"])!=40 or
        x.get("passed_checks")!=x.get("total_checks") or
        x.get("total_checks",0)<15 or
        x.get("worlds")!=12 or x.get("goals")!=420 or
        x.get("probes_active")!=360 or
        x.get("probes_uniform")!=360 or
        x.get("probes_random")!=360 or
        c.get("direct_active",0)<270 or
        c.get("direct_active")!=c.get("independent_symbolic") or
        c.get("fully_trained_logistic",0)<230 or
        c.get("direct_active",0)-c.get("direct_random_probing",10000)<5 or
        c.get("direct_active",0)-c.get("wrong_action_binding",10000)<90 or
        c.get("fully_trained_logistic",10000)-c.get("direct_active",0)>80 or
        x.get("causal_channel_maps_correct",0)<8 or
        x.get("direct_true_effect_bits_correct",0)/504 < .76 or
        not isinstance(x.get("per_world_prediction_sha256"),list) or
        len(x["per_world_prediction_sha256"])!=12 or
        any(not isinstance(v,str) or len(v)!=64 for v in
            x["per_world_prediction_sha256"])):
        raise ValueError("missing or invalid original dual-OS public causal result")
    return x

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--public-pass",action="store_true",required=True)
    a.parse_args()
    q=read()
    print("WSP95_PUBLIC_ADMISSION_VERIFIED="+json.dumps({
        "original_sha":q["exact_source_sha"],"run_id":q["run_id"],
        "classification":q["classification"],
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()

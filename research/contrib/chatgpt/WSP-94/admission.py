"""Immutable WSP94 public-development admission receipt verification.

This verifies engineering source and classifier consistency. It is NOT
scientific first-use or execution authority; independent qualification
and project owners remain outside this research branch.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PREREG="195d2c6c284831a7019fd858dc0b972ca6fd83c3"
PASS=HERE/"PUBLIC_PASS.json"
EXPECTED_SCHEMA="wsp94.verified-public-development-admission.v1"

def verify_public_pass()->dict:
    d=json.loads(PASS.read_text(encoding="utf-8"))
    c=d.get("correct",{})
    if (d.get("schema")!=EXPECTED_SCHEMA or
        d.get("prereg_commit")!=PREREG or
        d.get("classification")!="PUBLIC_CAUSAL_SLOT_FEASIBLE" or
        d.get("worlds")!=10 or d.get("goals")!=200 or
        d.get("interventions")!=50 or
        d.get("direct_signature_bits_correct")!=250 or
        d.get("conventional_signature_bits_correct")!=250 or
        not isinstance(c,dict) or
        c.get("direct_numeric",0)<190 or
        c.get("direct_numeric")!=c.get("symbolic_exact") or
        c.get("conventional_trained",0)<190 or
        c.get("shuffled_action",1000)>60 or
        c.get("passive_no_identity",1000)>90 or
        c.get("random_plan",1000)>80 or
        c.get("direct_numeric",0)-c.get("shuffled_action",1000)<100 or
        d.get("public_check_count")!=d.get("public_passed_check_count") or
        d.get("public_check_count",0)<12 or
        d.get("ubuntu_conclusion")!="success" or
        d.get("windows_conclusion")!="success" or
        type(d.get("run_id")) is not int or d["run_id"]<1 or
        not isinstance(d.get("exact_source_sha"),str) or
        len(d["exact_source_sha"])!=40 or
        not isinstance(d.get("source_and_prediction_sha256"),str) or
        len(d["source_and_prediction_sha256"])!=64):
        raise ValueError("WSP94 public scientific qualification not proven by frozen receipt")
    return d

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--public-pass",action="store_true",required=True)
    p.parse_args()
    receipt=verify_public_pass()
    print("WSP94_PUBLIC_ADMISSION_VERIFIED="+json.dumps({
        "source_sha":receipt["exact_source_sha"],
        "run_id":receipt["run_id"],
        "classification":receipt["classification"],
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()

"""WSP97 internal integrity check for source-controlled original PUBLIC_PASS.

Receipt is advisory qualification evidence, not original CI source of truth,
scientific acceptance authority, controller access or protected first-use.
"""
import argparse
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PREREG="01315e8bcaa4b53c6ca83eb9c6e37037a68c0e97"

def verify():
    p=json.loads((HERE/"PUBLIC_PASS.json").read_text(encoding="utf-8"))
    c=p.get("correct",{})
    d=c.get("direct_active",{})
    r=c.get("direct_random_probes",{})
    passive=c.get("passive_only_causal",{})
    symbol=c.get("independent_symbolic",{})
    ordinary=c.get("fully_trained_conventional",{})
    oracle=c.get("oracle_true_regime",{})
    if (p.get("schema")!="wsp97.original-public-dual-OS-admission.v1" or
        p.get("prereg_commit")!=PREREG or
        p.get("classification")!="PUBLIC_OBSERVATIONAL_EQUIVALENCE_BROKEN" or
        p.get("ubuntu")!="success" or p.get("windows")!="success" or
        p.get("attempt")!=1 or
        type(p.get("run_id")) is not int or p["run_id"]<1 or
        not isinstance(p.get("exact_sha"),str) or len(p["exact_sha"])!=40 or
        p.get("total_checks",0)<19 or
        p.get("passed_checks")!=p["total_checks"] or
        p.get("pair_count")!=12 or p.get("worlds")!=24 or
        p.get("diagnostic_requests")!=144 or p.get("full_requests")!=576 or
        p.get("passive_identical_pairs")!=12 or
        p.get("interventional_divergence_pairs")!=12 or
        p.get("active_probes")!=72 or p.get("random_probes")!=72 or
        p.get("direct_training_fit")!=768 or
        p.get("ordinary_training_fit")!=768 or
        d.get("diagnostic",0)<130 or
        d.get("diagnostic",0)-r.get("diagnostic",100000)<12 or
        d.get("diagnostic",0)-passive.get("diagnostic",100000)<40 or
        d!=symbol or ordinary.get("diagnostic",100000)>d.get("diagnostic",0) or
        oracle!={"full":576,"diagnostic":144} or
        not isinstance(p.get("original_prediction_sha256"),list) or
        len(p["original_prediction_sha256"])!=24 or
        any(not isinstance(h,str) or len(h)!=64 for h in p["original_prediction_sha256"])):
        raise ValueError("original public causal equivalence result not verified")
    return p

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--public-pass",action="store_true",required=True)
    parser.parse_args()
    x=verify()
    print("WSP97_PUBLIC_ADMISSION_VERIFIED="+json.dumps({
        "sha":x["exact_sha"],"run_id":x["run_id"],
        "classification":x["classification"],
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()

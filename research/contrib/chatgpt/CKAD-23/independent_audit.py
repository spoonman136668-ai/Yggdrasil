"""Retained-source independent CKAD23 numerical and custody audit."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from audit import combine,PARENTS,WORLDS,canonical,digest,need

HERE=Path(__file__).resolve().parent
CK22=HERE.parent/"CKAD-22"

def check(root=HERE):
    original=json.loads((CK22/"result.json").read_bytes())
    need(original["stable_sha256"]==
         "4b20ef3b9229eddfd509e5897e6aa8f8d5226288ab331c4a98f8a7bc46fbccc2",
         "ORIGINAL_RESULT")
    recorded=json.loads((root/"result.json").read_bytes())
    windows=json.loads((root/"replication-windows.json").read_bytes())
    linux_shards=json.loads((root/"shards-linux.json").read_bytes())
    windows_shards=json.loads((root/"shards-windows.json").read_bytes())
    a,b=combine(linux_shards),combine(windows_shards)
    need(a==b==recorded==windows,"INDEPENDENT_RECOMPUTE")
    expect=digest(canonical({k:v for k,v in a.items() if k!="stable_sha256"}))
    need(a["stable_sha256"]==expect,"STABLE_RESULT_PIN")
    need(a["contexts_trained"]==48 and a["new_probes"]==768 and
         a["new_world_held_episodes"]==2304 and
         a["familiar_held_episodes"]==2304,"CASE_ACCOUNTING")
    need(a["scientific_pass"] is False and a["accepted_native"] is False
         and a["deployment"]=="NONE","PROMOTION_BARRIER")
    for world in WORLDS:
        rewards=a["by_world"][world]["scores"][world]
        need(rewards["novel_active"]==rewards["exact_mixture"],"EXACT_HYPOTHESIS_CONTROL")
        prior=a["by_world"][world]["scores"]["familiar"]
        need(prior["novel_active"]==prior["exact_mixture"],"EXACT_RETENTION_CONTROL")
        for arm in rewards:
            need(0<=rewards[arm]<=1152,"REWARD_RANGE")
    return {"audit":"PASS","source":"CKAD23_UNPROTECTED_SYNTHETIC",
            "source_exact_ckad22_stable_sha256":original["stable_sha256"],
            "result_stable_sha256":a["stable_sha256"],
            "classification":a["classification"],
            "frozen_gates":a["frozen_gates"],
            "independent_parent_groups":3,
            "environment_seeds":8,"scientific_pass":False}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=HERE)
    args=p.parse_args()
    print(json.dumps(check(args.root),sort_keys=True))

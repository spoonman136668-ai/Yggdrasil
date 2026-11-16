"""CVH-05 exact original source constructor in a distinct OS process.

One-shot source custody, two independent constructor-only process receipts.
No actual original source reset/do/step, model action, source seed, reward,
training, protected first use, runner, owner controller or network service.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from constructor_ipc import (
    SCHEMA,PIN,run_checked_constructor,identical_public_receipt_sha256
)


def evaluate(checkout):
    first=run_checked_constructor(checkout)
    second=run_checked_constructor(checkout)
    if first!=second:
        raise RuntimeError("CVH05_ORIGINAL_SOURCE_CUSTODY_CROSS_PROCESS_DRIFT")
    if first["source_sha"]!=PIN or first["source_actions"]!=0 or first["source_resets"]!=0:
        raise RuntimeError("CVH05_SOURCE_ACTION_FENCE_FAILED")
    if first["original_objects"]!=1 or first["source_blobs"]!=16:
        raise RuntimeError("CVH05_NOT_ORIGINAL_VERIFIED_OBJECT")
    if first["source_process_isolated"] is not True:
        raise RuntimeError("CVH05_NOT_SEPARATE_PROCESS")
    if first["source_seed_first_use"] or first["model_updated"]:
        raise RuntimeError("CVH05_PROTECTED_FIRSTUSE_OR_MODEL_WRITE")
    return {
        "schema":"yggdrasil.cvh05.original-source-child-receipt.v1",
        "source_sha":PIN,
        "original_source_class":"causal_gym.envs.mdp.MDPPCH",
        "original_objects_constructed":2,
        "two_separately_reaped_source_processes":True,
        "original_source_actions":0,
        "original_source_resets":0,
        "source_seed_first_uses":0,
        "accepted_model_changed":False,
        "native_learned_return_not_executed":True,
        "scientific_pass":False,
        "source_first_use":False,
        "public_custody_sha256":identical_public_receipt_sha256(first),
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--checkout",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--source-action",action="store_true")
    args=p.parse_args()
    if args.source_action:
        p.error("CVH05_SOURCE_RESET_DO_FIRST_USE_NOT_AUTHORIZED")
    result=evaluate(args.checkout)
    path=Path(args.out)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",
                    encoding="utf-8")
    print("CVH05_REAL_CHILD_SOURCE_CONSTRUCTOR="+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()

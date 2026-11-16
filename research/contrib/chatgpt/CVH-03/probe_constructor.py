"""CVH-03 one-shot exact upstream factory/constructor probe; NO reset or do.

Requires a clean detached exact pinned Causal-Gymnasium checkout, with FKP25
pinned lightweight dependencies. It imports unchanged original core and mdp,
constructs two native MDPPCH objects using the source-facing factory shape,
and verifies the factory refuses use outside the controlled import context.
It deliberately CANNOT run any actual action, policy training, or evaluator.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from source_binding import verified_original_factory

def canonical(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=True,
                      allow_nan=False,separators=(",",":")).encode("ascii")


def probe(checkout):
    with verified_original_factory(checkout) as (original_factory,receipt):
        first=original_factory()
        second=original_factory()
        if first is second:
            raise AssertionError("CVH03_NOT_FRESH_NATIVE_ORIGINAL_OBJECTS")
        if first.__class__ is not second.__class__:
            raise AssertionError("CVH03_MIXED_ORIGINAL_SOURCE_CLASS")
        if original_factory.constructed != 2:
            raise AssertionError("CVH03_FACTORY_CONSTRUCTION_COUNT")
        if getattr(first.env,"num_step",None)!=0 or getattr(second.env,"num_step",None)!=0:
            raise AssertionError("CVH03_CONSTRUCTOR_CONSUMED_ACTION")
        # Both are only constructed. They have never been reset or acted on.
        report={
            **receipt,
            "native_objects_constructed":2,
            "source_action_calls":0,
            "source_reset_calls":0,
            "native_model_transitions":0,
            "original_class_identity_equal":True,
            "external_world_seed_consumed":False,
            "actual_source_run":False,
            "scientific_pass":False,
            "native_accepted":False,
        }
    try:
        original_factory()
    except PermissionError as exc:
        if "FACTORY_CLOSED" not in str(exc):
            raise
        report["closed_factory_reuse_denied"]=True
    else:
        raise AssertionError("CVH03_FACTORY_REUSED_AFTER_CONTEXT")
    report["source_receipt_sha256"]=sha256(canonical(report)).hexdigest()
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--checkout",required=True)
    parser.add_argument("--out",required=True)
    parser.add_argument("--source-action",action="store_true")
    args=parser.parse_args()
    if args.source_action:
        parser.error("CVH03_SOURCE_FIRST_USE_AND_PHYSICAL_ACTIONS_DISARMED")
    receipt=probe(args.checkout)
    output=Path(args.out)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("CVH03_VERIFIED_FACTORY="+json.dumps(receipt,sort_keys=True))


if __name__=="__main__":
    main()

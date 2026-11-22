"""NKR-10: run prespecified P31/P279 masked transfer against full NKR05 image.

This reads the *existing* already consumed historical TRAIN artifact only.
The native source remains immutable, with no inference admitted as ground truth,
no official valid/test, and no independent scientific first use.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))

from yggdrasil.native_knowledge_activation import (
    PINNED_ROWS, PINNED_PACKED_SHA, open_installed_session)
from yggdrasil.native_historical_transfer import frozen_split,evaluate_split
from yggdrasil.public_causal_cells import PublicCausalCells


def run(installed):
    started=time.monotonic()
    native_before=PublicCausalCells().snapshot()
    with open_installed_session(installed) as base:
        image=base._weights
        if len(image)!=PINNED_ROWS or image.manifest["packed_sha256"]!=PINNED_PACKED_SHA:
            raise AssertionError("NKR10_ORIGINAL_21M_IMAGE_SHA_OR_ROWS_DRIFT")
        first=image.row_at(0)
        last=image.row_at(len(image)-1)
        if (first!=(1,361,3327819) or last!=(43380424,31,5)
                or not base.fact(*first)["witnessed"]
                or not base.fact(*last)["witnessed"]):
            raise AssertionError("NKR10_ORIGINAL_21M_COLD_SOURCE_DRIFT")
        native,secret,inventory=frozen_split(image)
        results=evaluate_split(native,secret,inventory)
        # Explicit source split must never mutate or enter the original live
        # native counters. Unknown facts remain unknown in source facts.
        if (len(image)!=PINNED_ROWS
                or image.manifest["packed_sha256"]!=PINNED_PACKED_SHA
                or not base.fact(*first)["witnessed"]
                or not base.fact(*last)["witnessed"]
                or PublicCausalCells().snapshot()!=native_before):
            raise AssertionError("NKR10_BASE_OR_CAUSAL_STATE_CHANGED")
        results.update({
            "historical_source_records":PINNED_ROWS,
            "historical_source_image_sha256":PINNED_PACKED_SHA,
            "historical_first_record":list(first),
            "historical_last_record":list(last),
            "source_readonly_restoration_pass":True,
            "native_legacy_state_unchanged":True,
            "cold_source_verified":True,
            "total_test_wall_seconds_excluding_artifact_download":time.monotonic()-started,
        })
    print("NKR10_HISTORICAL_MASKED_TRANSFER="+json.dumps(
        results,sort_keys=True,separators=(",",":")),flush=True)
    return results


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--installed-session",required=True)
    args=parser.parse_args()
    run(args.installed_session)

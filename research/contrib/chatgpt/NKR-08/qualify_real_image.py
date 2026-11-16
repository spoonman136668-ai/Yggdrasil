"""NKR-08: engineering corroboration against the *existing* 21M-fact image.

Reuses NKR-05's previously materialized historical TRAIN artifact. No original
training-source redownload, no official valid/test, no independent real first
use. Injects 256 strictly *synthetic development* observations into a
disconnected candidate overlay without changing any historical image bytes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from yggdrasil.native_cumulative_facts import (
    BUNDLE_SCHEMA, CumulativeNativeFacts, canonical, digest)
from yggdrasil.native_knowledge_activation import (
    PINNED_ROWS, PINNED_PACKED_SHA, open_installed_session)
from yggdrasil.public_causal_cells import PublicCausalCells


def fixture(source_id, rows):
    rows = sorted(rows, key=lambda row: row[3])
    return canonical({
        "schema": BUNDLE_SCHEMA,
        "source_id": source_id,
        "source_kind": "direct_public_observation",
        "source_mode": "engineering_fixture_only",
        "records": rows,
    })


def prove_full_image(installed_dir):
    start = time.monotonic()
    before = PublicCausalCells().snapshot()
    with open_installed_session(installed_dir) as base:
        first = base._weights.row_at(0)
        last = base._weights.row_at(PINNED_ROWS - 1)
        if len(base._weights) != PINNED_ROWS:
            raise AssertionError("NKR08_REAL_IMAGE_INVENTORY_DRIFT")
        if base._weights.manifest["packed_sha256"] != PINNED_PACKED_SHA:
            raise AssertionError("NKR08_REAL_IMAGE_DIGEST_DRIFT")
        if not base.fact(*first)["witnessed"] or not base.fact(*last)["witnessed"]:
            raise AssertionError("NKR08_EXISTING_HISTORICAL_FACT_MISSING")
        # Deliberately above known maximum original source subject from
        # NKR-06 readback; verify absence directly before any staged update.
        phase_a = [(4294960000+i, 901, 4294961000+i) for i in range(128)]
        phase_b = [(4294961000+i, 902, 4294962000+i) for i in range(128)]
        for triple in phase_a + phase_b:
            if base.fact(*triple)["witnessed"]:
                raise AssertionError("NKR08_PROPOSED_FIXTURE_COLLIDES_WITH_BASE")
        a = fixture("nkr08-real-image-synthetic-phase-a",
                    [[*triple, f"a:{i:04d}"] for i, triple in enumerate(phase_a)])
        b_rows = [[*triple, f"b:{i:04d}"] for i, triple in enumerate(phase_b)]
        b_rows += [[*phase_a[i], f"b-duplicate:{i:04d}"] for i in range(32)]
        b_rows += [[*triple, f"b-base:{i:04d}"]
                   for i, triple in enumerate((first, last))]
        b = fixture("nkr08-real-image-synthetic-phase-b", b_rows)
        initial = CumulativeNativeFacts(base)
        candidate_a, receipt_a = initial.stage(a, digest(a))
        candidate_b, receipt_b = candidate_a.stage(b, digest(b))
        if (receipt_a["new_unique_facts"] != 128
                or receipt_b["new_unique_facts"] != 128
                or receipt_b["already_in_delta"] != 32
                or receipt_b["already_in_historical"] != 2
                or receipt_b["total_candidate_delta_facts"] != 256):
            raise AssertionError("NKR08_REAL_IMAGE_CUMULATIVE_RECEIPT_DRIFT")
        cold = CumulativeNativeFacts(
            base, candidate_b.checkpoint(),
            checkpoint_sha256=candidate_b.checkpoint_sha256)
        if (cold.checkpoint() != candidate_b.checkpoint()
                or candidate_a.checkpoint() == candidate_b.checkpoint()):
            raise AssertionError("NKR08_REAL_IMAGE_COLD_RETENTION_FAIL")
        # Equal-information exact symbolic records; fixture and historical
        # source are never treated as an independently held out benchmark.
        independent = set(phase_a + phase_b)
        for fact in independent:
            result = cold.fact(*fact)
            if (not result["witnessed"]
                    or result["classification"] !=
                    "DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
                    or result["native_accepted"]
                    or result["verified_new_real_knowledge"]):
                raise AssertionError("NKR08_REAL_IMAGE_SYMBOLIC_PARITY_FAIL")
        for i in range(128):
            origin = phase_a[i][0]
            if (cold.objects(origin, 901)["objects"] != [phase_a[i][2]]
                    or cold.hypothesize(origin, 901, 902)["objects"] !=
                    [phase_b[i][2]]):
                raise AssertionError("NKR08_REAL_IMAGE_TWO_HOP_CONTROL_FAIL")
        if not cold.fact(*first)["witnessed"] or not cold.fact(*last)["witnessed"]:
            raise AssertionError("NKR08_REAL_IMAGE_HISTORICAL_RETENTION_FAIL")
        unknown = cold.fact(0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF)
        if unknown["classification"] != "UNKNOWN_ABSTAIN":
            raise AssertionError("NKR08_REAL_IMAGE_UNKNOWN_ABSTENTION_FAIL")
        if PublicCausalCells().snapshot() != before:
            raise AssertionError("NKR08_NATIVE_CAUSAL_STATE_CHANGED")
        if len(base._weights) != PINNED_ROWS:
            raise AssertionError("NKR08_BASE_STORAGE_MUTATED")
        result = {
            "schema": "yggdrasil.nkr08.full-image-cumulative-dev-diagnostic.v1",
            "classification": "FULL_IMAGE_CUMULATIVE_ENGINEERING_PASS",
            "source_records": PINNED_ROWS,
            "source_image_sha256": PINNED_PACKED_SHA,
            "source_original_history_unchanged": True,
            "historical_first_triple": list(first),
            "historical_last_triple": list(last),
            "new_fixture_facts_after_two_phases": 256,
            "duplicate_prior_fixture_facts": 32,
            "duplicate_historical_source_facts": 2,
            "independent_exact_symbolic_membership_parity": 256,
            "independent_exact_symbolic_path_parity": 128,
            "cold_checkpoint_sha256": cold.checkpoint_sha256,
            "unsupported_unknown_abstention": True,
            "new_real_world_knowledge": False,
            "scientific_pass": False,
            "native_accepted": False,
            "original_source_first_use": False,
            "wall_seconds": time.monotonic() - start,
        }
    print("NKR08_FULL_IMAGE_CUMULATIVE_PROOF=" +
          json.dumps(result, sort_keys=True, separators=(",", ":")),
          flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--installed-session", required=True)
    args = parser.parse_args()
    prove_full_image(args.installed_session)

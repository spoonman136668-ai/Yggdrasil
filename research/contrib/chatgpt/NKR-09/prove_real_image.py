"""NKR-09: full historical image rule-composition *interface* proof only.

One-shot read-only rehydration of the previously qualified NKR-05 numeric
image, no historical source rescan, hidden validation labels or new science.
Fixture trains a synthetic relation template; the target path's second edge
comes from a REAL HISTORICAL SOURCE fact. This is a hypothetical deduction,
not source-certified newly learned knowledge.
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
from yggdrasil.native_relation_discovery import NativeRelationDiscovery
from yggdrasil.public_causal_cells import PublicCausalCells


def run_full_knowledge_proof(install):
    started = time.monotonic()
    before_native = PublicCausalCells().snapshot()
    with open_installed_session(install) as base:
        if len(base._weights) != PINNED_ROWS:
            raise AssertionError("NKR09_HISTORICAL_BASE_ROW_DRIFT")
        if base._weights.manifest["packed_sha256"] != PINNED_PACKED_SHA:
            raise AssertionError("NKR09_HISTORICAL_BASE_SHA_DRIFT")
        first = base._weights.row_at(0)
        last = base._weights.row_at(PINNED_ROWS - 1)
        if first != (1, 361, 3327819):
            raise AssertionError("NKR09_REAL_SOURCE_FIRST_TRIPLE_DRIFT")
        if not base.fact(*first)["witnessed"] or not base.fact(*last)["witnessed"]:
            raise AssertionError("NKR09_HISTORICAL_BASE_RETENTION_FAIL")
        # Prequalified historical path segment Q1 -- P361 --> Q3327819.
        # The new subject and schema P901/P903 are fixture-only and never
        # mistaken for real historical source assertions.
        train = []
        for i in range(8):
            s = 4_294_950_000 + i
            mid = 4_294_951_000 + i
            end = 4_294_952_000 + i
            train.extend([(s, 901, mid), (mid, 361, end),
                          (s, 903, end)])
        query = (4_294_960_000, 901, 1)
        train.append(query)
        for triple in train:
            if base.fact(*triple)["witnessed"]:
                raise AssertionError("NKR09_SYNTHETIC_COLLISION_WITH_HISTORICAL")
        raw = canonical({
            "schema": BUNDLE_SCHEMA,
            "source_id": "nkr09-real-image-fixture-only",
            "source_kind": "direct_public_observation",
            "source_mode": "engineering_fixture_only",
            "records": [
                [*fact, f"synthetic-nkr09:{i:04d}"]
                for i, fact in enumerate(train)]})
        initial = CumulativeNativeFacts(base)
        candidate, receipt = initial.stage(raw, digest(raw))
        if (receipt["new_unique_facts"] != len(train)
                or not base.fact(*first)["witnessed"]):
            raise AssertionError("NKR09_REAL_SOURCE_OR_CANDIDATE_CHANGED")
        model = NativeRelationDiscovery(candidate)
        if not any(
                (row["target_relation"], row["first_relation"],
                 row["second_relation"], row["training_support"])
                == (903, 901, 361, 8)
                for row in model.rules()):
            raise AssertionError("NKR09_LEARNED_SYNTHETIC_TEMPLATE_MISSING")
        guess = model.predict(query[0], 903)
        if (guess["classification"] != "UNVERIFIED_ADAPTIVE_RELATION_HYPOTHESES"
                or guess["verified_new_knowledge"]
                or guess["native_accepted"]
                or guess["can_write_causal_consequence"]
                or 3327819 not in [x["object_q"] for x in guess["proposals"]]):
            raise AssertionError("NKR09_REAL_SOURCE_TWO_HOP_HYPOTHESIS_FAIL")
        if candidate.fact(query[0], 903, 3327819)["witnessed"]:
            raise AssertionError("NKR09_FALSE_INFERRED_FACT_ADMISSION")
        if model.predict(query[0], 999)["classification"] != "UNKNOWN_ABSTAIN":
            raise AssertionError("NKR09_REAL_SOURCE_UNKNOWN_RELATION_NOT_ABSTAIN")
        cold = NativeRelationDiscovery(
            candidate, model.checkpoint(),
            checkpoint_sha256=model.checkpoint_sha256)
        if cold.predict(query[0], 903)["proposals"] != guess["proposals"]:
            raise AssertionError("NKR09_REAL_IMAGE_COLD_RULE_DRIFT")
        if PublicCausalCells().snapshot() != before_native:
            raise AssertionError("NKR09_ACCEPTED_NATIVE_STATE_DRIFT")
        if len(base._weights) != PINNED_ROWS:
            raise AssertionError("NKR09_REAL_BASE_MUTATED")
        receipt = {
            "schema":"yggdrasil.nkr09.full-image-rule-inference-probe.v1",
            "classification":"FULL_IMAGE_SOURCE_BOUND_RULE_INTERFACE_PASS",
            "historical_train_rows":PINNED_ROWS,
            "historical_image_sha256":PINNED_PACKED_SHA,
            "historical_first_triple":list(first),
            "historical_last_triple":list(last),
            "synthetic_training_rule_subjects":8,
            "synthetic_training_records":len(train),
            "induced_rule":[903,901,361,8],
            "historical_fact_used":list(first),
            "hypothesized_object_q":3327819,
            "hypothesis_is_verified":False,
            "original_historical_image_unchanged":True,
            "original_native_causal_cells_unchanged":True,
            "cold_rule_checkpoint_sha256":cold.checkpoint_sha256,
            "no_real_source_retraining":True,
            "scientific_pass":False,
            "native_accepted":False,
            "wall_seconds":time.monotonic()-started,
        }
    print("NKR09_FULL_IMAGE_RULE_PROOF="+json.dumps(
        receipt,sort_keys=True,separators=(",",":")),flush=True)
    return receipt


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--installed-session", required=True)
    args = parser.parse_args()
    run_full_knowledge_proof(args.installed_session)

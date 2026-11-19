"""KNOW03: original NKR-08 fact memory paired read-only with archived Amalgam bytes.

Uses the previously consumed full historical TRAIN-only NKR-05 image. Four
synthetic engineering fixture Q/P/Q records are staged in immutable candidate
overlays. No owner checkpoint, Amalgam policy, causal trainer or new real-world
scientific source is executed. An archived Amalgam envelope is NOT a restored
native learner; only the central coordinator can qualify that separate step.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

from typed_readout_bridge import TypedFactualReadoutBridge

JOINT_SHA = "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
NATIVE_SHA = "5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d"
SOURCE_SHA = "6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1"
SOURCE_RECORDS = 21_343_681

def insist(ok, reason):
    if not ok:
        raise ValueError("YGG_KNOW03_" + reason)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def bundle(source_id, rows):
    from yggdrasil.native_cumulative_facts import BUNDLE_SCHEMA
    return canonical({
        "schema": BUNDLE_SCHEMA,
        "source_id": source_id,
        "source_kind": "direct_public_observation",
        "source_mode": "engineering_fixture_only",
        "records": sorted(rows, key=lambda row: row[3]),
    })

class ArchivedJointReadOnly:
    """A checkpoint-only reader; NEVER an authenticated Amalgam runtime."""
    __slots__ = ("_raw",)
    def __init__(self, raw):
        insist(type(raw) is bytes and sha(raw) == JOINT_SHA,
               "ARCHIVED_RESEARCH_JOINT_PIN")
        data = json.loads(raw.decode("ascii"))
        insist(type(data) is dict and type(data.get("native_ascii")) is str
               and sha(data["native_ascii"].encode("ascii")) == NATIVE_SHA,
               "ARCHIVED_NATIVE_SHA")
        self._raw = raw

    def checkpoint(self):
        return self._raw

    def plan(self, *_args):
        raise PermissionError("KNOW03_NO_NATIVE_POLICY_INVOCATION")

def prove(installed_session, joint_file):
    from yggdrasil.native_cumulative_facts import CumulativeNativeFacts
    from yggdrasil.native_knowledge_activation import (
        PINNED_ROWS, PINNED_PACKED_SHA, open_installed_session)
    started = time.monotonic()
    joint_raw = Path(joint_file).read_bytes()
    insist(0 < len(joint_raw) <= 32 * 1024 * 1024, "JOINT_FILE_LENGTH")
    native = ArchivedJointReadOnly(joint_raw)
    with open_installed_session(installed_session) as base:
        insist(PINNED_ROWS == SOURCE_RECORDS and
               PINNED_PACKED_SHA == SOURCE_SHA and
               len(base._weights) == SOURCE_RECORDS and
               base._weights.manifest["packed_sha256"] == SOURCE_SHA,
               "FULL_HISTORICAL_SOURCE_IDENTITY")
        first, last = (tuple(base._weights.row_at(i))
                       for i in (0, SOURCE_RECORDS - 1))
        insist(base.fact(*first)["witnessed"] and
               base.fact(*last)["witnessed"], "HISTORICAL_EDGE_LOST")

        # These four numerically distant Q/P/Q tuples were used only as
        # synthetic engineering fixtures; no source-derived claim is added.
        a1 = (4294960000, 901, 4294961000)
        a2 = (4294960001, 901, 4294961001)
        b1 = (4294961000, 902, 4294962000)
        b2 = (4294961001, 902, 4294962001)
        for triple in (a1, a2, b1, b2):
            insist(not base.fact(*triple)["witnessed"],
                   "FIXTURE_COLLIDES_WITH_HISTORICAL")

        original = CumulativeNativeFacts(base)
        original_pin = original.checkpoint_sha256
        initial = TypedFactualReadoutBridge(native, original,
            native_checkpoint_sha256=JOINT_SHA,
            facts_checkpoint_sha256=original_pin)
        for old in (first, last):
            insist(initial.fact(*old)["evidence_kind"] == "HISTORICAL_STORED_QPQ",
                   "HISTORICAL_BRIDGE_READOUT")
        insist(initial.fact(*a1)["evidence_kind"] == "UNSUPPORTED_ABSTAIN",
               "PRE_STAGE_UNKNOWN_NOT_ABSTAINED")

        phase1 = bundle("know03-fixture-phase-a", [
            [*a1, "a:0001"], [*a2, "a:0002"]])
        phase2 = bundle("know03-fixture-phase-b", [
            [*b1, "b:0001"], [*b2, "b:0002"],
            [*a1, "b:duplicate-a"], [*first, "b:historic-first"]])
        stage1, receipt1 = original.stage(phase1, sha(phase1))
        stage2, receipt2 = stage1.stage(phase2, sha(phase2))
        insist((receipt1["new_unique_facts"],
                receipt2["new_unique_facts"],
                receipt2["already_in_delta"],
                receipt2["already_in_historical"],
                receipt2["total_candidate_delta_facts"]) == (2, 2, 1, 1, 4),
               "TWO_PHASE_RECEIPT_DRIFT")
        replay, duplicate = stage2.stage(phase2, sha(phase2))
        insist(replay is stage2 and
               duplicate["classification"] == "DUPLICATE_BUNDLE_NO_CHANGE",
               "REISSUE_NOT_IDEMPOTENT")

        cold = CumulativeNativeFacts(base, stage2.checkpoint(),
                                    checkpoint_sha256=stage2.checkpoint_sha256)
        insist(cold.checkpoint() == stage2.checkpoint(),
               "COLD_FACTUAL_RESTORE_MISMATCH")
        bridge = TypedFactualReadoutBridge(native, cold,
            native_checkpoint_sha256=JOINT_SHA,
            facts_checkpoint_sha256=cold.checkpoint_sha256)
        for new in (a1, a2, b1, b2):
            row = bridge.fact(*new)
            insist(row["evidence_kind"] == "SYNTHETIC_ENGINEERING_QPQ" and
                   row["causal_observation_admitted"] is False and
                   row["native_model_knowledge_updated"] is False,
                   "FACTUAL_DATA_MASQUERADED_AS_CAUSAL")
        for old in (first, last):
            insist(bridge.fact(*old)["evidence_kind"] == "HISTORICAL_STORED_QPQ",
                   "HISTORICAL_RETENTION_LOST")
        for src, expected in ((a1[0], b1[2]), (a2[0], b2[2])):
            hypo = bridge.hypotheses(src, 901, 902)
            insist(hypo["unverified_objects"] == [expected] and
                   hypo["causal_observation_admitted"] is False and
                   hypo["scientific_pass"] is False,
                   "PATH_HYPOTHESIS_LAUNDERED")
        insist(bridge.fact(0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF)[
            "evidence_kind"] == "UNSUPPORTED_ABSTAIN",
            "UNSUPPORTED_FACT_NOT_ABSTAINED")
        for fn in (lambda: bridge.stage(phase1, sha(phase1)),
                   lambda: bridge.observe_experience()):
            try:
                fn()
            except PermissionError as exc:
                insist("NO_FACTUAL_WRITE" in str(exc), "WRONG_WRITE_DENIAL")
            else:
                raise AssertionError("KNOW03_BRIDGE_ALLOWED_CAUSAL_MUTATION")
        insist(original.checkpoint_sha256 == original_pin and
               original.checkpoint() != cold.checkpoint() and
               native.checkpoint() == joint_raw and
               sha(native.checkpoint()) == JOINT_SHA,
               "PREEXISTING_CHECKPOINT_MUTATED")
        return {
            "schema": "yggdrasil.know03.full-historical-image-readout-compat.v1",
            "classification": "EXPERIMENTAL_RESEARCH_ONLY_ENGINEERING",
            "historical_train_records": SOURCE_RECORDS,
            "historical_image_sha256": SOURCE_SHA,
            "amalgam_archived_checkpoint_sha256": JOINT_SHA,
            "amalgam_native_checkpoint_sha256": NATIVE_SHA,
            "original_fact_checkpoint_sha256": original_pin,
            "candidate_fact_checkpoint_sha256": cold.checkpoint_sha256,
            "native_archived_checkpoint_unchanged": True,
            "historical_first_last_facts_retained": True,
            "synthetic_added_facts": 4,
            "prior_duplicate_facts": 1,
            "historical_duplicate_source_refs": 1,
            "unverified_two_hop_paths": 2,
            "unsupported_unknown_abstained": True,
            "native_causal_observations_admitted": 0,
            "factual_cold_restore_identical": True,
            "duplicate_bundle_idempotent": True,
            "amalgam_live_learner_restored": False,
            "amalgam_policy_called": False,
            "knowledge_source_original_first_use": False,
            "new_real_world_knowledge_learned": 0,
            "native_learning_executed": False,
            "scientific_pass": False,
            "canonical_owner_checkpoint": "UNVERIFIED",
            "deployment": "NONE",
            "probe_seconds_excluding_source_fetch_install": round(
                time.monotonic() - started, 6),
        }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--installed-session", type=Path, required=True)
    p.add_argument("--joint-checkpoint", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = prove(args.installed_session, args.joint_checkpoint)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n",
                           encoding="utf-8")
    print("YGG_KNOW03_REAL_HISTORICAL_COMPAT_PASS " +
          json.dumps({"historical_train_records": result["historical_train_records"],
                      "synthetic_added_facts": result["synthetic_added_facts"],
                      "archived_native_sha256": NATIVE_SHA,
                      "scientific_pass": False}, sort_keys=True), flush=True)

if __name__ == "__main__":
    main()

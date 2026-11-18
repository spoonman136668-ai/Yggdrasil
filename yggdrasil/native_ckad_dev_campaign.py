"""Bounded, source-owned CKAD development campaign; no autonomous scheduler.

Performs two *real* native observe stages, persists cumulative checkpoints,
then evaluates held synthetic rows without revealing them to the learner.
Uses only previously consumed developer fixture. Nothing admits first-use
science, dispatches FORGE jobs or promotes native/accepted models.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile
import time

from yggdrasil.native_ckad_dev_stage import (
    SCHEMA as STAGE_SCHEMA, COMPONENT, SOURCE_REPO, checkout_identity,
    run_fixture_stage,
)
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from yggdrasil.native_property_knowledge import NativePropertyKnowledge

SCHEMA = "yggdrasil.ckad.bounded-development-campaign.v1"
SOURCE = "previously-consumed-engineering-fixture-only"
CAMPAIGN = "ckad-two-stage-dev-20261118"
REFERENCE = "a" * 64
FILES = ("initial.native.json", "stage-01.native.json", "stage-02.native.json",
         "stage-01.packet.json", "stage-02.packet.json",
         "stage-01.receipt.json", "stage-02.receipt.json",
         "evaluation.json", "campaign-result.json")


def need(ok, code):
    if not ok:
        raise ValueError("CKAD_DEV_CAMPAIGN_" + code)


def _atomic(root, filename, raw):
    need(filename in FILES and type(raw) is bytes and 1 <= len(raw) <= 16*1024*1024,
         "FILE_SCOPE")
    target = root / filename
    need(not target.exists() and not target.is_symlink(), "FILE_ALREADY_EXISTS")
    with tempfile.NamedTemporaryFile(dir=root, prefix=".ckad-stage-", delete=False) as f:
        temp = Path(f.name)
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    try:
        need(not target.exists(), "FILE_ALREADY_EXISTS")
        temp.replace(target)
    finally:
        if temp.exists():
            temp.unlink()


def fixture():
    p = NativePropertyKnowledge("ckad-stage-test", entities=8, context_bits=3)
    facts = [[e, b, (e >> b) & 1] for e in range(8) for b in range(3)]
    p = p.stage_properties(facts, digest(canonical(facts)),
                           source_namespace="ckad-stage-test")
    raw = p.checkpoint()
    return NativeCumulativeLearner(raw, digest(raw)).checkpoint()


def witnessed():
    # Same already-consumed deterministic synthetic developer fixture as
    # test_native_ckad_dev_stage.py; neither original nor novel source.
    return [[x & 7, x >> 3, int((x & 3) == 3)] for x in range(16)]


def _packet(rows):
    return canonical({"source_mode": "engineering_fixture_only",
                      "source_kind": "engineering_public_binary_consequence",
                      "source_ref": REFERENCE, "slot": 0, "rows": rows})


def _request(source_sha, source_tree, raw, packet, index):
    return {"schema": STAGE_SCHEMA, "campaign_id": CAMPAIGN,
            "stage_index": index, "stage_id": "learn-stage-0" + str(index+1),
            "phase": "learn", "source_repo": SOURCE_REPO,
            "source_commit": source_sha, "source_tree": source_tree,
            "native_component": COMPONENT, "source_mode": SOURCE,
            "source_ref_sha256": REFERENCE,
            "input_checkpoint_sha256": digest(raw),
            "packet_sha256": digest(packet),
            "max_observations": 8, "max_wall_seconds": 60,
            "scientific_first_use": False, "forge_dispatch_authorized": False,
            "promotion_authorized": False, "paid_api_calls": 0}


def _metric(model, held):
    predictions = [model.predict(0, c, a) for c, a, _ in held]
    correct = sum(p == r[2] for p, r in zip(predictions, held))
    return {"held": len(held), "answered": sum(p is not None for p in predictions),
            "correct": correct, "predictions": predictions,
            "constant_zero_correct": sum(r[2] == 0 for r in held),
            "constant_one_correct": sum(r[2] == 1 for r in held)}


def run(output_directory):
    """Execute exactly two developer stages into a new, exclusive directory."""
    root = Path(output_directory)
    need(not root.exists() and not root.is_symlink(), "OUTPUT_DIRECTORY_MUST_BE_NEW")
    root.mkdir(parents=True, exist_ok=False)
    sha, tree = checkout_identity()
    start = time.monotonic()
    initial = fixture()
    _atomic(root, FILES[0], initial)
    raw, rows, receipts = initial, witnessed(), []
    need(len(rows) == 16, "FIXTURE_DRIFT")
    for index, batch in enumerate((rows[:8], rows[8:12])):
        packet = _packet(batch)
        request = _request(sha, tree, raw, packet, index)
        old, previous = raw, (None if not receipts else receipts[-1])
        raw, result = run_fixture_stage(request, raw, packet,
                                        checkout_sha=sha, checkout_tree=tree)
        need(result["input_checkpoint_sha256"] == digest(old)
             and result["output_checkpoint_sha256"] == digest(raw)
             and result["native_cold_restore_verified"] is True,
             "SOURCE_STAGE_RECEIPT_DRIFT")
        if previous is not None:
            need(result["input_checkpoint_sha256"] ==
                 previous["output_checkpoint_sha256"], "COLD_CHAIN_DRIFT")
        stable = dict(result)
        stable.pop("wall_milliseconds")
        stable["parent_receipt_sha256"] = (None if previous is None
                                           else previous["stable_receipt_sha256"])
        result["stable_receipt_sha256"] = digest(canonical(stable))
        result["parent_receipt_sha256"] = stable["parent_receipt_sha256"]
        receipts.append(result)
        _atomic(root, "stage-0" + str(index+1) + ".packet.json", packet)
        _atomic(root, "stage-0" + str(index+1) + ".native.json", raw)
        _atomic(root, "stage-0" + str(index+1) + ".receipt.json", canonical(result))
    restored = NativeCumulativeLearner.restore(raw, digest(raw))
    need(restored.checkpoint() == raw
         and restored.info()["stored_properties"] == 24
         and restored.info()["events"] == 2,
         "COLD_HISTORY_OR_PROPERTIES_LOST")
    held = rows[12:]
    metric = _metric(restored, held)
    eval_doc = {"schema": "yggdrasil.ckad.development-held-evaluation.v1",
                "held_inputs_sha256": digest(canonical([[c, a] for c,a,_ in held])),
                "held_truth_sha256": digest(canonical([r[2] for r in held])),
                "checkpoint_sha256": digest(raw), "metrics": metric,
                "frozen_controls": ["constant_zero","constant_one"],
                "scientific_pass": False, "independent_science": False}
    _atomic(root, "evaluation.json", canonical(eval_doc))
    stable = {"schema": SCHEMA, "campaign_id": CAMPAIGN,
              "source_repo": SOURCE_REPO, "source_sha": sha, "source_tree": tree,
              "source_mode": SOURCE, "scientific_first_use": False,
              "forge_dispatch_authorized": False, "scientific_pass": False,
              "accepted_native": False, "stages_completed": 2,
              "evaluations_completed": 1,
              "observations": 12, "interventions": 0,
              "initial_checkpoint_sha256": digest(initial),
              "final_checkpoint_sha256": digest(raw),
              "receipts": [r["stable_receipt_sha256"] for r in receipts],
              "evaluation_sha256": digest(canonical(eval_doc)),
              "held_correct": metric["correct"], "held_answered": metric["answered"],
              "held_total": metric["held"]}
    _atomic(root, "campaign-result.json", canonical(stable))
    need(time.monotonic()-start <= 180, "TOTAL_CAMPAIGN_WALL_BUDGET")
    return stable


def verify(output_directory):
    """Independently cold restore persisted stage bytes and verify all digests."""
    root = Path(output_directory)
    need(root.is_dir() and not root.is_symlink()
         and {p.name for p in root.iterdir()} == set(FILES)
         and all(p.is_file() and not p.is_symlink() for p in root.iterdir()),
         "ARTIFACT_INVENTORY")
    values = {name:(root/name).read_bytes() for name in FILES}
    out = json.loads(values["campaign-result.json"])
    need(type(out) is dict and out["schema"] == SCHEMA
         and out["scientific_first_use"] is False
         and out["scientific_pass"] is False
         and out["forge_dispatch_authorized"] is False,
         "RESULT_AUTHORITY")
    sha, tree = checkout_identity()
    need(out["source_sha"] == sha and out["source_tree"] == tree
         and out["initial_checkpoint_sha256"] == digest(values[FILES[0]])
         and values[FILES[0]] == fixture(),
         "RESULT_SOURCE_OR_INITIAL")
    last = values[FILES[0]]
    parent = None
    for i in (1,2):
        filename = "stage-0" + str(i)
        packet = values[filename+".packet.json"]
        receipt_raw = values[filename+".receipt.json"]
        need(canonical(json.loads(receipt_raw)) == receipt_raw,
             "RECEIPT_CANONICAL")
        receipt = json.loads(receipt_raw)
        nxt = values[filename+".native.json"]
        need(receipt["input_checkpoint_sha256"] == digest(last)
             and receipt["output_checkpoint_sha256"] == digest(nxt)
             and receipt["packet_sha256"] == digest(packet)
             and receipt["native_cold_restore_verified"] is True
             and receipt["parent_receipt_sha256"] == parent,
             "CHAIN_RECEIPT")
        stable = dict(receipt)
        stable.pop("wall_milliseconds")
        stable.pop("stable_receipt_sha256")
        need(receipt["stable_receipt_sha256"] == digest(canonical(stable))
             and out["receipts"][i-1] == receipt["stable_receipt_sha256"],
             "CHAIN_HASH")
        m = NativeCumulativeLearner.restore(nxt, digest(nxt))
        need(m.checkpoint() == nxt, "NATIVE_COLD_RESTORE_DRIFT")
        last, parent = nxt, receipt["stable_receipt_sha256"]
    eval_raw = values["evaluation.json"]
    need(digest(eval_raw) == out["evaluation_sha256"]
         and canonical(json.loads(eval_raw)) == eval_raw,
         "EVALUATION_BYTES_DRIFT")
    evaluator = json.loads(eval_raw)
    held = witnessed()[12:]
    metrics = _metric(NativeCumulativeLearner.restore(last,digest(last)),held)
    need(evaluator["metrics"] == metrics
         and out["final_checkpoint_sha256"] == digest(last)
         and out["held_correct"] == metrics["correct"]
         and out["held_answered"] == metrics["answered"]
         and out["held_total"] == metrics["held"],
         "EVALUATION_NOT_REPRODUCED")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()
    result = (verify(args.output_directory) if args.verify_existing
              else run(args.output_directory))
    print("CKAD_DEVELOPMENT_CAMPAIGN=" + canonical(result).decode("ascii"))

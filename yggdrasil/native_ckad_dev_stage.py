"""Development-only single-stage CKAD native causal learning.

Runs actual NativeCumulativeLearner.observe() on ALREADY CONSUMED synthetic
engineering witnesses. Does not confer source ownership, controller dispatch,
first-use, accepted-model promotion, or scientific superiority. FORGE's inert
work orders must not be mistaken for a Yggdrasil authorization.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import time

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

SCHEMA = "yggdrasil.ckad.native-development-stage.v1"
RECEIPT = "yggdrasil.ckad.native-development-stage-receipt.v1"
SOURCE_REPO = "spoonman136668-ai/Yggdrasil"
COMPONENT = "yggdrasil.native_cumulative_learner.NativeCumulativeLearner"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
STAGE_ID = re.compile(r"[a-z][a-z0-9-]{3,63}\Z")
FIELDS = frozenset((
    "schema", "campaign_id", "stage_index", "stage_id", "phase",
    "source_repo", "source_commit", "source_tree", "native_component",
    "source_mode", "source_ref_sha256", "input_checkpoint_sha256",
    "packet_sha256", "max_observations", "max_wall_seconds",
    "scientific_first_use", "forge_dispatch_authorized",
    "promotion_authorized", "paid_api_calls",
))
PACKET_FIELDS = frozenset(("source_mode", "source_kind", "source_ref", "slot", "rows"))
COLD_SCRIPT = """import json,sys
from yggdrasil.native_context_basis import digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
raw=sys.stdin.buffer.read()
m=NativeCumulativeLearner.restore(raw,digest(raw))
assert m.checkpoint()==raw
print(json.dumps({"sha256":digest(raw),"native_cold_restore":True,
"stored_properties":m.info()["stored_properties"]},sort_keys=True))
"""


class StageDenied(ValueError):
    pass


def need(condition, code):
    if not condition:
        raise StageDenied("CKAD_DEV_STAGE_" + code)


def checkout_identity():
    """Developer checkout identity only; never original owner authentication."""
    root = Path(__file__).resolve().parents[1]
    def git(*args):
        x = subprocess.run(["git", "-C", str(root), *args],
                           capture_output=True, text=True, timeout=10, check=True)
        return x.stdout.strip()
    return git("rev-parse", "HEAD"), git("rev-parse", "HEAD^{tree}")


def _load_canonical(raw):
    need(type(raw) is bytes and 1 <= len(raw) <= 1024 * 1024,
         "PACKET_MISSING_OR_OVERSIZE")
    def unique(pairs):
        output = {}
        for key, value in pairs:
            need(key not in output, "DUPLICATE_PACKET_KEY")
            output[key] = value
        return output
    try:
        obj = json.loads(raw.decode("ascii"), object_pairs_hook=unique,
                         parse_constant=lambda _: need(False, "NONFINITE"))
    except (ValueError, UnicodeError, TypeError) as exc:
        raise StageDenied("CKAD_DEV_STAGE_PACKET_INVALID") from exc
    need(canonical(obj) == raw, "PACKET_NOT_CANONICAL")
    return obj


def run_fixture_stage(request, checkpoint_raw, packet_raw, *,
                      checkout_sha, checkout_tree):
    """Run one real native learning stage on a prior synthetic fixture.

    The caller MUST independently qualify the checkout and its fixture.
    Source-owner authenticated execution is not established by this method.
    The output bytes and receipt may be persisted by the CKAD-owned caller.
    """
    need(type(request) is dict and set(request) == FIELDS,
         "WORK_ORDER_FIELDS")
    need(request["schema"] == SCHEMA
         and type(request["campaign_id"]) is str
         and STAGE_ID.fullmatch(request["campaign_id"]) is not None
         and type(request["stage_index"]) is int
         and 0 <= request["stage_index"] < 12
         and type(request["stage_id"]) is str
         and STAGE_ID.fullmatch(request["stage_id"]) is not None
         and request["phase"] == "learn"
         and request["source_repo"] == SOURCE_REPO
         and request["native_component"] == COMPONENT
         and request["source_mode"] == "previously-consumed-engineering-fixture-only"
         and type(checkout_sha) is str and SHA40.fullmatch(checkout_sha) is not None
         and type(checkout_tree) is str and SHA40.fullmatch(checkout_tree) is not None
         and request["source_commit"] == checkout_sha
         and request["source_tree"] == checkout_tree
         and request["scientific_first_use"] is False
         and request["forge_dispatch_authorized"] is False
         and request["promotion_authorized"] is False
         and type(request["paid_api_calls"]) is int
         and request["paid_api_calls"] == 0
         and type(request["max_observations"]) is int
         and 1 <= request["max_observations"] <= 2048
         and type(request["max_wall_seconds"]) is int
         and 1 <= request["max_wall_seconds"] <= 120
         and type(request["source_ref_sha256"]) is str
         and SHA64.fullmatch(request["source_ref_sha256"]) is not None
         and type(request["input_checkpoint_sha256"]) is str
         and SHA64.fullmatch(request["input_checkpoint_sha256"]) is not None
         and type(request["packet_sha256"]) is str
         and SHA64.fullmatch(request["packet_sha256"]) is not None,
         "UNQUALIFIED_DEVELOPMENT_SCOPE")
    need(type(checkpoint_raw) is bytes and 0 < len(checkpoint_raw) <= 16*1024*1024
         and digest(checkpoint_raw) == request["input_checkpoint_sha256"],
         "INPUT_COLD_CHECKPOINT_SHA")
    need(type(packet_raw) is bytes and digest(packet_raw) == request["packet_sha256"],
         "SOURCE_PACKET_SHA")
    packet = _load_canonical(packet_raw)
    need(type(packet) is dict and set(packet) == PACKET_FIELDS
         and packet["source_mode"] == "engineering_fixture_only"
         and packet["source_kind"] == "engineering_public_binary_consequence"
         and packet["source_ref"] == request["source_ref_sha256"]
         and type(packet["slot"]) is int and 0 <= packet["slot"] < 16
         and type(packet["rows"]) is list
         and 1 <= len(packet["rows"]) <= request["max_observations"]
         and all(type(row) is list and len(row) == 3
                 and all(type(value) is int for value in row)
                 for row in packet["rows"]),
         "SOURCE_PACKET_SCOPE_OR_BUDGET")
    begin = time.monotonic()
    original = NativeCumulativeLearner.restore(checkpoint_raw,
                                               request["input_checkpoint_sha256"])
    old_properties = original._properties.checkpoint()
    old_events = original._events
    old_seen = original._source._seen
    rows = packet["rows"]
    child = original.observe(packet["slot"], rows, digest(canonical(rows)),
                             source_ref=packet["source_ref"])
    need(child is not original and child.checkpoint() != checkpoint_raw,
         "REPLAY_OR_NO_LEARNING")
    need(child._properties.checkpoint() == old_properties
         and child._events[:len(old_events)] == old_events
         and all(child._source._seen[i] == old_seen[i]
                 for i in range(16) if i != packet["slot"]),
         "OLD_KNOWLEDGE_OR_UNRELATED_SLOT_CHANGED")
    output_raw = child.checkpoint()
    need(original.checkpoint() == checkpoint_raw,
         "MUTATED_INPUT_CHECKPOINT")
    root = Path(__file__).resolve().parents[1]
    env = {"PYTHONPATH": str(root), "PYTHONDONTWRITEBYTECODE": "1",
           "PYTHONHASHSEED": "0"}
    remaining = request["max_wall_seconds"] - (time.monotonic() - begin)
    need(remaining > 0, "WALL_BUDGET")
    try:
        cold = subprocess.run([sys.executable, "-B", "-c", COLD_SCRIPT],
                              input=output_raw, capture_output=True,
                              timeout=remaining, cwd=root, env=env, check=True)
        restored = json.loads(cold.stdout)
    except (OSError, subprocess.SubprocessError, UnicodeError, ValueError) as exc:
        raise StageDenied("CKAD_DEV_STAGE_INDEPENDENT_COLD_RESTORE_FAILED") from exc
    need(restored == {"sha256": digest(output_raw), "native_cold_restore": True,
                      "stored_properties": child.info()["stored_properties"]},
         "INDEPENDENT_COLD_RESTORE_MISMATCH")
    elapsed_ms = int((time.monotonic() - begin) * 1000)
    need(elapsed_ms <= request["max_wall_seconds"] * 1000, "FINAL_WALL_BUDGET")
    receipt = {
        "schema": RECEIPT, "campaign_id": request["campaign_id"],
        "stage_index": request["stage_index"], "stage_id": request["stage_id"],
        "source_commit": checkout_sha, "source_tree": checkout_tree,
        "input_checkpoint_sha256": digest(checkpoint_raw),
        "output_checkpoint_sha256": digest(output_raw),
        "packet_sha256": digest(packet_raw),
        "observations": len(rows), "wall_milliseconds": elapsed_ms,
        "checkpoint_changed": True, "native_cold_restore_verified": True,
        "development_fixture_training_executed": True,
        "original_source_authenticated": False,
        "scientific_first_use": False,
        "forge_dispatch_authorized": False,
        "scientific_pass": False, "model_promotion_authorized": False,
    }
    return output_raw, receipt

"""Original native eight-cell state: source-FREE cold-process evidence artifact.

Exactly the existing public FIT development cohort; no original Shuttle data,
scientific admission, source-owner credential, F139 worker, or promotion.
Three distinct invocations (prefix, resume, verify) retain genuine saved model
bytes with existing append-only journals in a GitHub Actions artifact.
This is NOT the 16/7/9 accepted portable cognition-consumer model contract.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

# Direct script invocation sets sys.path[0] to scripts/, not the checkout root.
# Import only the exact checkout-owned native module; no global installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yggdrasil.itd02_native_public_cohort_dev import train_or_resume_public_cohort
from yggdrasil.itd02_public_source_journal_dev import inspect_custody, load_verified_native_model
from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev

FIXTURE = b"ygg.itd02.source-free.docked-mrv.nothing.0.reward.two-steps.v1"
SOURCE_SHA256 = hashlib.sha256(FIXTURE).hexdigest()
SCHEMA = "ygg.itd02.native-checkpoint-cold-artifact.sourcefree.dev.v1"
PREFIX_SCHEMA = "ygg.itd02.native-checkpoint-prefix.sourcefree.dev.v1"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")

class Rejected(ValueError):
    pass

def need(ok, reason):
    if not ok:
        raise Rejected("YGG_COLD_ARTIFACT_" + reason)

def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                       allow_nan=False) + "\n").encode("ascii")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read(path):
    path = Path(path)
    need(path.is_file() and not path.is_symlink() and path.stat().st_size <= 16384,
         "REPORT_INVALID")
    data = path.read_bytes()
    try:
        return json.loads(data), digest(data)
    except (UnicodeError, ValueError) as error:
        raise Rejected("YGG_COLD_ARTIFACT_REPORT_JSON_INVALID") from error

class SourceFreePublicFixture:
    """Only an explicitly labeled source-free engineering control, no original task."""
    def __init__(self, number):
        self.number = number
        self.actions = []
    @property
    def source_receipt(self):
        return {"source_sha256": SOURCE_SHA256,
                "role": "PUBLIC_FIT_ONLY_NOT_INDEPENDENT_SCIENCE",
                "protected_first_use": False}
    def reset_public(self):
        need(not self.actions, "DUPLICATE_RESET")
        return "docked_MRV"
    def step_public(self, action):
        self.actions.append(action)
        need(len(self.actions) <= 2, "STEP_BUDGET")
        # Honest source-owner TRUNCATION, never a claimed task success.
        return ("Nothing", 0, False, len(self.actions) == 2)

def checkpoints(root, expected_count):
    cohort = Path(root) / "cohort"
    found = sorted(p.name for p in cohort.iterdir()
                   if p.name.startswith("episode-"))
    need(found == [f"episode-{i:06d}" for i in range(1, expected_count + 1)],
         "EPISODE_INVENTORY")
    rows = []
    for index, name in enumerate(found, 1):
        location = cohort / name
        receipt = inspect_custody(location, expected_source_sha256=SOURCE_SHA256)
        need(receipt["status"] == "COMMITTED" and receipt["steps"] == 2 and
             receipt["episode"] == f"ep-{index:06d}", "SOURCE_CUSTODY")
        model = load_verified_native_model(location, expected_source_sha256=SOURCE_SHA256)
        raw = (location / "learned-checkpoint.bin").read_bytes()
        journal = (location / "public-events.jsonl").read_bytes()
        need(0 < len(raw) <= 65536 and
             NativeTaskRingBridgeDev.restore(raw).model_identities() ==
             model.model_identities(), "NATIVE_MODEL_RESTORE")
        rows.append({"episode": index, "checkpoint_sha256": digest(raw),
                     "checkpoint_bytes": len(raw), "journal_sha256": digest(journal),
                     "journal_head": receipt["head"], "steps": 2,
                     "native_model_identities": model.model_identities()})
    return rows

def phase(root, mode, source_sha):
    root = Path(root)
    need(root.is_absolute() and not root.is_symlink(), "ROOT")
    need(type(source_sha) is str and HEX40.fullmatch(source_sha) is not None,
         "CHECKED_OUT_SOURCE_SHA")
    prefix_path = root / "prefix-evidence.json"
    result_path = root / "evidence.json"
    cohort = root / "cohort"
    if mode == "prefix":
        need(not root.exists(), "PREFIX_ALREADY_EXISTS")
        root.mkdir(mode=0o700, parents=False)
        created = []
        def factory(index):
            need(index in (1, 2), "UNEXPECTED_PREFIX_EPISODE")
            created.append(index)
            return SourceFreePublicFixture(index)
        out = train_or_resume_public_cohort(
            cohort, factory, source_sha256=SOURCE_SHA256,
            episodes=3, max_steps=2, new_episodes_limit=2)
        need(out["completed_episodes"] == 2 and out["total_public_actions"] == 4 and
             created == [1, 2], "PREFIX_TRAINING")
        rows = checkpoints(root, 2)
        data = {"schema": PREFIX_SCHEMA, "source_commit_sha": source_sha,
                "project": "Yggdrasil", "source_free_fixture_sha256": SOURCE_SHA256,
                "checkpoints": rows, "native_model_identities": out["native_model_identities"],
                "scientific_first_use": False, "promotion_authority": False}
        prefix_path.write_bytes(encode(data))
        return data

    need(root.is_dir() and prefix_path.is_file(), "PREFIX_MISSING")
    prev, _ = read(prefix_path)
    need(prev.get("schema") == PREFIX_SCHEMA and
         prev.get("project") == "Yggdrasil" and
         prev.get("source_commit_sha") == source_sha and
         prev.get("source_free_fixture_sha256") == SOURCE_SHA256 and
         prev.get("scientific_first_use") is False and
         prev.get("promotion_authority") is False, "PREFIX_IDENTITY")
    if mode == "resume":
        need(prev.get("checkpoints") == checkpoints(root, 2), "PREFIX_BYTES_DRIFT")
    # No unknown checkpoint or event may be skipped or treated as accepted.
    if mode == "resume":
        need(not result_path.exists(), "RESUME_ALREADY_COMMITTED")
        created = []
        def factory(index):
            need(index == 3, "PREVIOUS_SOURCE_REPLAY_FORBIDDEN")
            created.append(index)
            return SourceFreePublicFixture(index)
        out = train_or_resume_public_cohort(
            cohort, factory, source_sha256=SOURCE_SHA256,
            episodes=3, max_steps=2)
        need(out["completed_episodes"] == 3 and
             out["past_episodes_skipped_without_replay"] == 2 and
             out["total_public_actions"] == 6 and created == [3],
             "COLD_PROCESS_CONTINUATION")
        rows = checkpoints(root, 3)
        need(rows[:2] == prev["checkpoints"] and
             rows[1]["checkpoint_sha256"] != rows[2]["checkpoint_sha256"] and
             rows[0]["checkpoint_sha256"] != rows[2]["checkpoint_sha256"],
             "PARENT_CHILD_NATIVE_STATE")
        data = {"schema": SCHEMA, "project": "Yggdrasil",
                "source_commit_sha": source_sha,
                "source_free_fixture_sha256": SOURCE_SHA256,
                "checkpoint_history": rows,
                "parent_checkpoint_sha256": rows[1]["checkpoint_sha256"],
                "child_checkpoint_sha256": rows[2]["checkpoint_sha256"],
                "independent_process_continuation": True,
                "previous_episodes_skipped_without_replay": 2,
                "native_source_selected_actions": 6,
                "native_model_identities": out["native_model_identities"],
                "actual_original_world_executed": False,
                "source_authentication": "SELF_DECLARED_FIXTURE_ONLY",
                "unfamiliar_transfer": "UNVERIFIED",
                "retention_vs_fresh_control": "UNVERIFIED",
                "scientific_first_use": False,
                "scientific_accepted": False,
                "successor_authority": False,
                "promotion_authority": False,
                "portable_16_slot_accepted_model": False}
        result_path.write_bytes(encode(data))
        return data

    need(mode == "verify" and result_path.is_file(), "PHASE_INVALID")
    recorded, _ = read(result_path)
    need(recorded.get("schema") == SCHEMA and
         recorded.get("source_commit_sha") == source_sha and
         recorded.get("source_free_fixture_sha256") == SOURCE_SHA256 and
         recorded.get("independent_process_continuation") is True and
         recorded.get("scientific_accepted") is False and
         recorded.get("promotion_authority") is False and
         recorded.get("portable_16_slot_accepted_model") is False,
         "FINAL_IDENTITY")
    rows = checkpoints(root, 3)
    need(recorded["checkpoint_history"] == rows and
         recorded["parent_checkpoint_sha256"] == rows[1]["checkpoint_sha256"] and
         recorded["child_checkpoint_sha256"] == rows[2]["checkpoint_sha256"] and
         prev["checkpoints"] == rows[:2], "FINAL_BYTES_DRIFT")
    def forbidden(_):
        raise Rejected("YGG_COLD_ARTIFACT_SOURCE_REPLAY_FORBIDDEN")
    out = train_or_resume_public_cohort(
        cohort, forbidden, source_sha256=SOURCE_SHA256, episodes=3, max_steps=2)
    need(out["past_episodes_skipped_without_replay"] == 3 and
         out["native_model_identities"] == recorded["native_model_identities"],
         "COLD_READBACK_CHANGED_MODEL")
    return {"schema": SCHEMA, "cold_readback": "PASS",
            "parent_checkpoint_sha256": rows[1]["checkpoint_sha256"],
            "child_checkpoint_sha256": rows[2]["checkpoint_sha256"],
            "science": "NOT_TESTED"}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--phase", choices=("prefix", "resume", "verify"), required=True)
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--source-commit-sha", required=True)
    args = ap.parse_args()
    print(json.dumps(phase(args.root, args.phase, args.source_commit_sha),
                     sort_keys=True, separators=(",", ":"), allow_nan=False))

if __name__ == "__main__":
    main()

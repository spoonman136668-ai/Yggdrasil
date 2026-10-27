"""Bounded local native self-training across public-owner episodes.

The native eight-cell model, not ChatGPT/Codex, chooses every action. This is
an on-device FIT *development* runner, not another FORGE controller/scheduler.
Every episode owns its own append-only source journal and checkpoint; on
cold-process re-entry we ONLY skip fully committed episodes and refuse to
repeat any episode with uncertain prior source effects.

Source roles are attestations provided by caller/source owner, NOT independent
verification of scientific first-use or protected environmental permission.
Unit tests only use source-FREE fixtures, never the published original Shuttle.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import time

from .itd02_native_training_session_dev import NativeTrainingSessionDev
from .itd02_public_source_journal_dev import (
    JournaledPublicSourceDev, SourceCustodyDenied, inspect_custody,
    load_verified_native_model,
)

COHORT_SCHEMA = "ygg.itd02.public-native-cohort.dev.v1"
ROLE = "OWNER_PUBLIC_FIT_DEVELOPMENT_ONLY"
SOURCE_ROLE = "PUBLIC_FIT_ONLY_NOT_INDEPENDENT_SCIENCE"
MAX_EPISODES = 128
MAX_STEPS = 512
EXPECTED_FILES = {"cohort.json"}


def _require(ok, why):
    if not ok:
        raise SourceCustodyDenied("YGG_PUBLIC_COHORT_" + why)


def _json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _write_manifest_once(root, data):
    path = root / "cohort.json"
    raw = _json(data) + b"\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        rest = raw
        while rest:
            count = os.write(fd, rest)
            _require(count > 0, "COHORT_MANIFEST_WRITE")
            rest = rest[count:]
        os.fsync(fd)
    finally:
        os.close(fd)


def _manifest(root, expected):
    path = root / "cohort.json"
    _require(path.is_file() and not path.is_symlink(),
             "COHORT_MANIFEST_MISSING")
    _require(path.stat().st_size <= 2048, "COHORT_MANIFEST_TOO_LARGE")
    raw = path.read_bytes()
    _require(raw == _json(expected) + b"\n",
             "COHORT_MANIFEST_IDENTITY_DRIFT")


def _check_source_identity(source, source_sha256):
    # Read-only outside-learner metadata. A self-asserted receipt does not
    # confer an independently authenticated source-owner permission.
    receipt = getattr(source, "source_receipt", None)
    _require(type(receipt) is dict or hasattr(receipt, "items"),
             "SOURCE_RECEIPT_REQUIRED")
    receipt = dict(receipt)
    _require(receipt.get("source_sha256") == source_sha256,
             "SOURCE_IDENTITY_MISMATCH")
    _require(receipt.get("role") == SOURCE_ROLE and
             receipt.get("protected_first_use") is False,
             "NO_PUBLIC_DEVELOPMENT_ROLE")


def _verify_root_files(root):
    names = {p.name for p in root.iterdir()}
    unknown = names - EXPECTED_FILES
    for name in unknown:
        _require(re.fullmatch(r"episode-[0-9]{6}", name) is not None,
                 "UNEXPECTED_ROOT_ENTRY")
        p = root / name
        _require(p.is_dir() and not p.is_symlink(), "EPISODE_DIR_INVALID")
    return unknown


def train_or_resume_public_cohort(
    root, source_factory, *, source_sha256, episodes, max_steps,
    role=ROLE,
):
    """Continue a finite local dev training cohort without replaying actions.

    source_factory(one_based_episode_index) must supply a fresh source OWNER
    that exposes public reset/step, plus outside-model source_receipt identity.
    The factory MUST be source-owner-approved externally; the role string
    does not substitute for approval. If it fails after causing side effects,
    the already reserved episode path blocks automatic retry.
    """
    _require(type(source_sha256) is str and
             re.fullmatch(r"[0-9a-f]{64}", source_sha256) is not None,
             "SOURCE_SHA_INVALID")
    _require(type(episodes) is int and 1 <= episodes <= MAX_EPISODES,
             "EPISODE_BUDGET")
    _require(type(max_steps) is int and 1 <= max_steps <= MAX_STEPS,
             "STEP_BUDGET")
    _require(role == ROLE, "OWNER_ROLE_REQUIRED")
    _require(callable(source_factory), "SOURCE_FACTORY_REQUIRED")
    root = Path(root)
    _require(not root.is_symlink(), "COHORT_ROOT_SYMLINK")
    if not root.exists():
        root.mkdir(mode=0o700)
    _require(root.is_dir() and not root.is_symlink(), "COHORT_ROOT_INVALID")
    contract = {
        "schema": COHORT_SCHEMA, "source_sha256": source_sha256,
        "episodes": episodes, "max_steps": max_steps, "role": ROLE,
        "protected_first_use": False,
    }
    if not (root / "cohort.json").exists():
        # Any unexpected entries indicate an ambiguous prior attempt.
        _require(not list(root.iterdir()), "MISSING_COHORT_MANIFEST")
        _write_manifest_once(root, contract)
    _manifest(root, contract)
    known_dirs = _verify_root_files(root)
    # Reject gaps or out-of-budget directories. Never silently skip them.
    dirs = sorted(known_dirs)
    for i, name in enumerate(dirs, 1):
        _require(name == f"episode-{i:06d}" and i <= episodes,
                 "EPISODE_CHAIN_GAP_OR_BUDGET")
    model = None
    past = []
    for i, name in enumerate(dirs, 1):
        path = root / name
        result = inspect_custody(path, expected_source_sha256=source_sha256)
        _require(result["status"] == "COMMITTED",
                 "UNRESOLVED_SOURCE_EFFECT_AT_EPISODE_" + str(i))
        _require(result["episode"] == f"ep-{i:06d}" and
                 1 <= result["steps"] <= max_steps,
                 "PREVIOUS_EPISODE_IDENTITY")
        model = load_verified_native_model(
            path, expected_source_sha256=source_sha256)
        past.append(result)
    receipts = list(past)
    for i in range(len(past) + 1, episodes + 1):
        # Reserve exact identity BEFORE invoking source factory; its creation
        # might itself consume an external source or throw ambiguously.
        path = root / f"episode-{i:06d}"
        path.mkdir(mode=0o700)
        source = source_factory(i)
        _check_source_identity(source, source_sha256)
        session = NativeTrainingSessionDev(model=model, max_steps=max_steps)
        begin = time.perf_counter_ns()
        cpu = time.process_time_ns()
        with JournaledPublicSourceDev(
            path, source, episode_id=f"ep-{i:06d}",
            source_sha256=source_sha256, max_steps=max_steps, role=ROLE,
        ) as journal:
            output = journal.execute_one(session)
        _check_source_identity(source, source_sha256)
        model = load_verified_native_model(
            path, expected_source_sha256=source_sha256)
        receipt = inspect_custody(path, expected_source_sha256=source_sha256)
        _require(receipt["status"] == "COMMITTED" and
                 output["steps"] == receipt["steps"],
                 "POST_TRAINING_CUSTODY_MISMATCH")
        # Costs are DEV engineering diagnostics, not hardware qualification.
        receipt = dict(receipt)
        receipt["wall_ns"] = time.perf_counter_ns() - begin
        receipt["parent_process_cpu_ns"] = time.process_time_ns() - cpu
        receipt["journal_checkpoint_bytes"] = sum(
            x.stat().st_size for x in path.iterdir() if x.is_file())
        receipts.append(receipt)
    return {
        "source_sha256": source_sha256,
        "completed_episodes": len(receipts),
        "total_public_actions": sum(x["steps"] for x in receipts),
        "native_model_identities": model.model_identities() if model else None,
        "past_episodes_skipped_without_replay": len(past),
        "receipts": receipts,
        "assessment": "SOURCE_FREE_ENGINEERING_NOT_SCIENCE",
    }

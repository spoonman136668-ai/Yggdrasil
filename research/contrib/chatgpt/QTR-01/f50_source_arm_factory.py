#!/usr/bin/env python3
"""Source-only F50 checkpoint admission and 12-arm factory.

Uses previously trained GitHub Actions artifact ZIPs; no model retraining,
development-target construction, oracle access or scientific first-use.
Source history for 4096 controls is preserved without relabeling the weights.
"""
import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import stat
import tempfile
from zipfile import ZipFile, BadZipFile

import f50_worlds as world
import f50_comparison_harness as harness
import f50_source_artifact_audit as audit4096
import f50_source_fit as sourcefit
import f50_native_assoc as native
import f50_bayesian_controls as bayes
import f50_target_public_controls as control

LOWER_ARTIFACT_ID = 14191256763
LOWER_RUN_ID = 43786499201
LOWER_ARCHIVE_SHA256 = "117d15cedd4f096376ecf6180f0b89453adb2f603be903ee315143d5e54e67ff"
LOWER_TRAINING_SOURCE = "704d8720fcc9b43ec1540b4d52749a875f0989f8"
KINDS = tuple(harness.TRAINED_SOURCE_KINDS)
_TOKEN = object()


class SourceAdmissionRejected(RuntimeError):
    pass


def require(condition, code):
    if not condition:
        raise SourceAdmissionRejected("F50_SOURCE_ADMISSION_" + code)


def expected_members(size):
    prefix = "" if size == 4096 else str(size) + "/"
    receipt = (audit4096.RECEIPT_NAME if size == 4096
               else "f50-source-fit-receipt.json")
    return {prefix + receipt} | {
        prefix + "f50-source-" + str(size) + "-" + kind + ".npz"
        for kind in KINDS}


def verified_zip(path, digest, expected):
    """Verify archive bytes and fixed inventory before reading any model."""
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "ARCHIVE_MISSING")
    require(0 < path.stat().st_size <= 20_000_000, "ARCHIVE_TOO_LARGE")
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == digest, "ARCHIVE_DIGEST_MISMATCH")
    try:
        with ZipFile(io.BytesIO(raw)) as archive:
            members = archive.infolist()
            names = [m.filename for m in members if not m.is_dir()]
            require(len(names) == len(set(names)) and set(names) == expected,
                    "ARCHIVE_INVENTORY")
            for m in members:
                require((m.filename in expected or
                         (m.is_dir() and m.filename.rstrip("/") in ("1024","2048")))
                        and not (m.flag_bits & 1)
                        and stat.S_IFMT(m.external_attr >> 16) != stat.S_IFLNK,
                        "ARCHIVE_UNSAFE_MEMBER")
                if not m.is_dir():
                    require(0 < m.file_size <=
                            (32_000 if m.filename.endswith(".json") else 10_000_000),
                            "ARCHIVE_MEMBER_UNBOUNDED")
            return {m.filename: archive.read(m) for m in members if not m.is_dir()}
    except (OSError, ValueError, BadZipFile) as exc:
        raise SourceAdmissionRejected("F50_SOURCE_ADMISSION_BAD_ZIP") from exc


def _store(directory, files):
    for name, data in files.items():
        path = Path(directory) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def _identity(digest, metadata):
    return {"checkpoint_sha256": digest, "source_sha": metadata["candidate_sha"],
            "source_dataset_sha256": metadata["source_data_sha256"],
            "prereg_blob": world.PREREG_BLOB}


def _load_4096(root):
    report = audit4096.audit(root)
    require(report["status"] == "THREE_4096_SOURCE_MODELS_ACTUAL_BYTES_VERIFIED"
            and report["dev_target_outcomes"] == 0, "4096_AUDIT_FAILED")
    models, identities = {}, {}
    for kind in KINDS:
        digest, original_sha = audit4096.ROLES[kind]
        model, meta = sourcefit.load_checkpoint(
            Path(root) / ("f50-source-4096-" + kind + ".npz"),
            digest, original_sha, expected_kind=kind, expected_size=4096)
        require(meta["source_data_sha256"] == audit4096.SOURCE_DATA,
                "4096_DATASET_DRIFT")
        models[kind] = (model, meta, digest)
        identities[kind] = _identity(digest, meta)
    return models, identities


def _load_lower(root, size):
    base = Path(root) / str(size)
    raw = (base / "f50-source-fit-receipt.json").read_bytes()
    try:
        receipt = json.loads(raw, object_pairs_hook=audit4096.no_duplicate_keys)
    except (ValueError, TypeError, UnicodeError) as exc:
        raise SourceAdmissionRejected("F50_SOURCE_ADMISSION_RECEIPT_INVALID") from exc
    source = receipt.get("source")
    require(receipt.get("schema") == sourcefit.SCHEMA
            and receipt.get("source_commit") == LOWER_TRAINING_SOURCE
            and receipt.get("frozen_prereg_blob") == world.PREREG_BLOB
            and receipt.get("size") == size
            and receipt.get("status") == "ALL_THREE_SOURCE_ONLY_TRAINED"
            and receipt.get("target_outcomes") == 0
            and receipt.get("scientific_pass") is False
            and type(source) is dict
            and source.get("size") == size
            and source.get("fit_laws") == size * 4 // 5
            and source.get("validation_laws") == size - size * 4 // 5
            and source.get("frozen_prereg_blob") == world.PREREG_BLOB,
            "LOWER_RECEIPT_CUSTODY")
    models, identities = {}, {}
    entries = receipt.get("models")
    require(type(entries) is list and
            [m.get("kind") for m in entries] == list(KINDS),
            "LOWER_MODEL_INVENTORY")
    for kind, entry in zip(KINDS, entries):
        name = "f50-source-" + str(size) + "-" + kind + ".npz"
        path = base / name
        digest = entry.get("sha256")
        require(entry.get("checkpoint") == name
                and re.fullmatch("[0-9a-f]{64}", str(digest))
                and entry.get("bytes") == path.stat().st_size
                and entry.get("cold_restored") is True
                and type(entry.get("fit")) is dict
                and entry["fit"].get("status") == "TRAINED_SOURCE_ONLY"
                and entry["fit"].get("source_training_complete") is True
                and entry["fit"].get("validation_law_disjoint") is True,
                "LOWER_MODEL_TRAINING")
        model, meta = sourcefit.load_checkpoint(
            path, digest, LOWER_TRAINING_SOURCE,
            expected_kind=kind, expected_size=size)
        require(meta["model_training"] == entry["fit"]
                and meta["source_data_sha256"] == source["source_data_sha256"]
                and meta["no_target_first_use"] is True,
                "LOWER_MODEL_METADATA")
        models[kind] = (model, meta, digest)
        identities[kind] = _identity(digest, meta)
    return models, identities


def arm_role(kind):
    require(kind in harness.KINDS, "UNKNOWN_ARM")
    if kind in KINDS:
        return "conventional"
    if kind in bayes.KINDS:
        return "bayesian"
    return "native"


class SourceArmFactory:
    __slots__ = ("_models", "source_roles", "candidate_sha")

    def __init__(self, models, source_roles, candidate_sha, *, token=None):
        require(token is _TOKEN, "UNAUDITED_FACTORY")
        harness.checkpoint_inventory(source_roles)
        require(type(models) is dict and set(models) == set(world.BANK_SIZES)
                and all(set(models[s]) == set(KINDS) for s in world.BANK_SIZES),
                "INCOMPLETE_MODEL_MAP")
        self._models = models
        self.source_roles = source_roles
        self.candidate_sha = candidate_sha

    def make_arm(self, size, seed, kind):
        require((size, seed) in harness.frozen_plan()
                and kind in harness.KINDS, "WORLD_OR_ARM_NOT_FROZEN")
        role = arm_role(kind)
        if role == "conventional":
            model, meta, digest = self._models[size][kind]
            arm = control.TargetPublicArm(size, seed, kind, model, meta, digest)
            restore = lambda pkt: control.TargetPublicArm.restore(
                pkt, model, meta, digest)
        elif role == "bayesian":
            arm = bayes.BayesianPublicArm(size, seed, kind)
            restore = bayes.BayesianPublicArm.restore
        else:
            settings = {
                "native": ("none", "native"),
                "random": ("none", "random"),
                "uniform": ("none", "uniform"),
                "native_no_causal_slot_retention": ("no_causal_slot_retention", "native"),
                "native_public_outcome_shuffle": ("public_outcome_shuffle", "native"),
                "native_random_proposals_equal_2048": ("random_proposals_equal_2048", "native"),
                "native_permuted_action_outcome_alignment": ("permuted_action_outcome_alignment", "native")
            }
            require(kind in settings, "NATIVE_MODE_UNREGISTERED")
            mode, policy = settings[kind]
            arm = native.NativeAssociation(size, seed, mode=mode, query_policy=policy)
            restore = native.NativeAssociation.restore
        require(getattr(arm, "target_graph_available", False) is False
                and arm.observed_bits == 0 and arm.used == [],
                "DIRTY_START")
        return arm, restore


def preflight(archive_4096, archive_lower, *, candidate_sha):
    """No oracle is imported, constructed, or opened by this preflight."""
    world.freeze()
    require(type(candidate_sha) is str and
            re.fullmatch("[0-9a-f]{40}", candidate_sha),
            "CANDIDATE_INVALID")
    upper = verified_zip(
        archive_4096, audit4096.ARCHIVE_SHA256, expected_members(4096))
    lower = verified_zip(
        archive_lower, LOWER_ARCHIVE_SHA256,
        expected_members(2048) | expected_members(1024))
    with tempfile.TemporaryDirectory(prefix="f50-source-only-") as directory:
        _store(directory, upper)
        _store(directory, lower)
        models, roles = {}, {}
        models[4096], roles[4096] = _load_4096(directory)
        for size in (2048, 1024):
            models[size], roles[size] = _load_lower(directory, size)
    harness.checkpoint_inventory(roles)
    return SourceArmFactory(models, roles, candidate_sha, token=_TOKEN)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-only", required=True, action="store_true")
    parser.add_argument("--archive-4096", required=True)
    parser.add_argument("--archive-lower", required=True)
    parser.add_argument("--candidate-sha", required=True)
    args = parser.parse_args()
    ready = preflight(
        args.archive_4096, args.archive_lower, candidate_sha=args.candidate_sha)
    print("F50_NINE_REAL_SOURCE_CHECKPOINTS=PASS", flush=True)
    print("F50_SOURCE_ONLY_ARM_FACTORIES=12", flush=True)
    print("F50_CANDIDATE_SHA=" + ready.candidate_sha, flush=True)
    print("F50_DEVELOPMENT_FIRST_USE=BLOCKED", flush=True)


if __name__ == "__main__":
    main()

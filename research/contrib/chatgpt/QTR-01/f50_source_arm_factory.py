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
        # The retained 4096 archive has an exact flat-file inventory. Keep
        # lower-bank directories outside its audited root; otherwise the
        # existing 4096 custodian correctly rejects those extra entries.
        upper_root = Path(directory) / "4096"
        upper_root.mkdir()
        _store(upper_root, upper)
        _store(directory, lower)
        models, roles = {}, {}
        models[4096], roles[4096] = _load_4096(upper_root)
        for size in (2048, 1024):
            models[size], roles[size] = _load_lower(directory, size)
    harness.checkpoint_inventory(roles)
    return SourceArmFactory(models, roles, candidate_sha, token=_TOKEN)


def _prove_cold_arm(arm, restore, *, size, seed, kind, source_identity):
    """Public source-only state custody, without choosing actions or outcomes."""
    require(callable(restore) and arm.size == size
            and arm.seed == seed and arm.observed_bits == 0
            and arm.used == [] and len(arm.pool) == world.PUBLIC_QUERIES
            and getattr(arm, "target_graph_available", False) is False,
            "COLD_DIRTY_START")
    require(getattr(arm, "pending", None) is None
            and getattr(arm, "awaiting", None) is None,
            "COLD_PENDING_ACTION")
    if kind in KINDS:
        require(type(source_identity) is dict
                and arm.model_sha == source_identity["checkpoint_sha256"]
                and arm.source_sha == source_identity["source_sha"]
                and arm.source_data_sha == source_identity["source_dataset_sha256"],
                "COLD_REAL_MODEL_IDENTITY")
    else:
        require(source_identity is None, "COLD_UNEXPECTED_WEIGHT_IDENTITY")
    original = arm.cold_checkpoint()
    require(type(original) is bytes and 0 < len(original) < 1_000_000,
            "COLD_PACKET_UNBOUNDED")
    restored = restore(original)
    require(type(restored) is type(arm)
            and restored.cold_checkpoint() == original
            and restored.size == size and restored.seed == seed
            and restored.used == [] and restored.observed_bits == 0
            and restored.pool == arm.pool
            and getattr(restored, "target_graph_available", False) is False,
            "COLD_BIT_EXACT_RESTORE")
    # Reject a deliberately damaged checksum rather than merely comparing
    # pristine object states. Never submit fake target actions or labels.
    damaged = original[:-1] + (b"0" if original[-1:] != b"0" else b"1")
    try:
        restore(damaged)
    except Exception:
        pass
    else:
        raise SourceAdmissionRejected("F50_SOURCE_ADMISSION_COLD_TAMPER_ACCEPTED")
    return restored


def _prove_public_prediction_pair(arm, restored):
    """One identical PUBLIC candidate, deterministic zero-feedback parity.

    No evaluator, target AST, target outcome, observed event or new source fit.
    """
    import math
    episode = arm.pool[0]
    first = arm.probability(episode)
    again = restored.probability(episode)
    require(type(first) in (tuple, list) and len(first) == 3
            and type(again) in (tuple, list) and len(again) == 3
            and all(type(x) in (int, float) and math.isfinite(x)
                    and 0 <= x <= 1 for x in first)
            and tuple(first) == tuple(again)
            and arm.cold_checkpoint() == restored.cold_checkpoint()
            and arm.observed_bits == 0 and restored.observed_bits == 0
            and arm.used == [] and restored.used == [],
            "PUBLIC_ZERO_FEEDBACK_PREDICTION_PARITY")


def cold_source_arms(factory, *, max_cpu_seconds=900):
    """Actual 9-world x 12-arm cold reconstruction; no target first use.

    One public-only prediction parity per kind/size at first seed. All 108
    combinations must cold-check; failure/resource stop is never accepted.
    """
    from time import process_time
    require(type(factory) is SourceArmFactory
            and type(max_cpu_seconds) is int
            and 1 <= max_cpu_seconds <= 1800,
            "COLD_SOURCE_SCOPE_INVALID")
    harness.checkpoint_inventory(factory.source_roles)
    start = process_time()
    checked = []
    predictions = 0
    for size, seed in harness.frozen_plan():
        for kind in harness.KINDS:
            if process_time() - start > max_cpu_seconds:
                raise SourceAdmissionRejected("F50_SOURCE_ADMISSION_RESOURCE_STOP")
            arm, restore = factory.make_arm(size, seed, kind)
            identity = (factory.source_roles[size][kind]
                        if kind in KINDS else None)
            clone = _prove_cold_arm(
                arm, restore, size=size, seed=seed, kind=kind,
                source_identity=identity)
            if seed == world.DEV_SEEDS[0]:
                _prove_public_prediction_pair(arm, clone)
                predictions += 1
            checked.append((size, seed, kind))
            del arm, clone
        print("F50_COLD_WORLD_COMPLETE_SIZE=" + str(size)
              + "_SEED=" + str(seed), flush=True)
    require(len(checked) == 9 * 12 and predictions == 3 * 12
            and len(set(checked)) == 9 * 12,
            "COLD_108_WORLD_ARM_COVERAGE")
    return {"status": "F50_COLD_108_PASS",
            "worlds": 9, "arm_kinds": 12, "cold_restores": len(checked),
            "zero_feedback_public_prediction_pairs": predictions,
            "target_outcomes": 0, "scientific_pass": False,
            "process_cpu_seconds": round(process_time()-start, 6)}



def synthetic_public_bits(episode):
    """Explicit public-only delayed-action/context fixture; never a DEV law."""
    a,b,c,context = world.validate_trajectory(episode)
    return ((a >> 0) & 1,
            ((b >> 1) ^ (a >> 2)) & 1,
            ((c >> 2) ^ (b >> 3) ^ (context >> 0)) & 1)


def synthetic_single_event_arms(factory, *, max_cpu_seconds=900):
    """12 high-bank source-backed arms, one fake public event each.

    This is a post-feedback custody smoke check, NOT scientific evaluation.
    No private target evaluator, withheld outcome or weight optimization.
    """
    from time import process_time
    import math

    require(type(factory) is SourceArmFactory
            and type(max_cpu_seconds) is int
            and 1 <= max_cpu_seconds <= 1800, "SYNTHETIC_SCOPE_INVALID")
    harness.checkpoint_inventory(factory.source_roles)
    size, seed = world.BANK_SIZES[0], world.DEV_SEEDS[0]
    start = process_time()
    completed = []
    for kind in harness.KINDS:
        require(process_time() - start <= max_cpu_seconds,
                "SYNTHETIC_RESOURCE_STOP")
        arm, restore = factory.make_arm(size, seed, kind)
        require(arm.used == [] and arm.observed_bits == 0
                and getattr(arm, "target_graph_available", False) is False,
                "SYNTHETIC_DIRTY_INITIAL_STATE")
        index, episode = arm.select()
        require(type(index) is int and 0 <= index < world.PUBLIC_QUERIES
                and episode == arm.pool[index],
                "SYNTHETIC_ACTION_MISMATCH")
        bits = synthetic_public_bits(episode)
        arm.observe(index, bits)
        require(arm.used == [index] and arm.observed_bits == 3
                and getattr(arm, "pending", None) is None
                and getattr(arm, "awaiting", None) is None
                and getattr(arm, "optimizer_steps", 0) == 0
                and getattr(arm, "target_graph_available", False) is False,
                "SYNTHETIC_FEEDBACK_STATE_INVALID")
        expected_proposals = 2048 if (arm_role(kind) == "native"
                                     or kind == "compositional_grammar_bayes") else 0
        require(getattr(arm, "proposals", 0) == expected_proposals,
                "SYNTHETIC_PROPOSAL_COUNT_INVALID")
        packet = arm.cold_checkpoint()
        clone = restore(packet)
        require(type(clone) is type(arm)
                and clone.cold_checkpoint() == packet
                and clone.used == [index] and clone.observed_bits == 3
                and clone.pool == arm.pool
                and getattr(clone, "optimizer_steps", 0) == 0
                and getattr(clone, "target_graph_available", False) is False,
                "SYNTHETIC_COLD_MISMATCH")
        # Compare PUBLIC predictions only, never held-out scientific scores.
        first, second = arm.probability(episode), clone.probability(episode)
        require(type(first) in (tuple, list) and len(first) == 3
                and tuple(first) == tuple(second)
                and all(type(x) in (float, int)
                        and math.isfinite(x) and 0 <= x <= 1 for x in first)
                and arm.cold_checkpoint() == clone.cold_checkpoint(),
                "SYNTHETIC_PREDICTION_PARITY_FAILED")
        before = arm.cold_checkpoint()
        try:
            arm.observe(index, bits)
        except Exception:
            pass
        else:
            raise SourceAdmissionRejected("F50_SOURCE_ADMISSION_SYNTHETIC_REPLAY")
        require(arm.cold_checkpoint() == before, "SYNTHETIC_REPLAY_MUTATION")
        damaged = packet[:-1] + (b"0" if packet[-1:] != b"0" else b"1")
        try:
            restore(damaged)
        except Exception:
            pass
        else:
            raise SourceAdmissionRejected("F50_SOURCE_ADMISSION_SYNTHETIC_TAMPER")
        completed.append(kind)
        print("F50_SYNTHETIC_PUBLIC_EVENT_ARM=" + kind, flush=True)
        del arm, clone
    require(completed == list(harness.KINDS),
            "SYNTHETIC_TWELVE_ARM_INCOMPLETE")
    return {"synthetic_events": len(completed), "cold_restores": len(completed),
            "size": size, "seed": seed, "target_outcomes": 0,
            "scientific_pass": False,
            "process_cpu_seconds": round(process_time()-start, 6)}



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-only", required=True, action="store_true")
    parser.add_argument("--archive-4096", required=True)
    parser.add_argument("--archive-lower", required=True)
    parser.add_argument("--candidate-sha", required=True)
    parser.add_argument("--cold-arms", action="store_true")
    parser.add_argument("--synthetic-one-event", action="store_true")
    args = parser.parse_args()
    ready = preflight(
        args.archive_4096, args.archive_lower, candidate_sha=args.candidate_sha)
    print("F50_NINE_REAL_SOURCE_CHECKPOINTS=PASS", flush=True)
    print("F50_SOURCE_ONLY_ARM_FACTORIES=12", flush=True)
    print("F50_CANDIDATE_SHA=" + ready.candidate_sha, flush=True)
    print("F50_DEVELOPMENT_FIRST_USE=BLOCKED", flush=True)
    if args.cold_arms:
        result = cold_source_arms(ready)
        print("F50_COLD_ALL_108_SOURCE_ARMS=PASS", flush=True)
        print("F50_COLD_PUBLIC_ZERO_FEEDBACK_PAIRS="
              + str(result["zero_feedback_public_prediction_pairs"]), flush=True)
        print("F50_TARGET_OUTCOMES=0", flush=True)
    if args.synthetic_one_event:
        result = synthetic_single_event_arms(ready)
        print("F50_SYNTHETIC_POST_FEEDBACK_ALL_12_ARMS=PASS", flush=True)
        print("F50_SYNTHETIC_PUBLIC_EVENTS=" + str(result["synthetic_events"]), flush=True)
        print("F50_SYNTHETIC_DEV_TARGET_OUTCOMES=0", flush=True)


if __name__ == "__main__":
    main()

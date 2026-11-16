#!/usr/bin/env python3
"""Auditable actual-byte custody for retained F50 4096-law source models.

Source-only: never creates DEV laws/outcomes, never loads evaluator, and never
substitutes 4096 checkpoints for missing 2048/1024 science controls.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import f50_source_fit as sourcefit
import f50_source_reconcile as reconciliation
import f50_worlds as world

SCHEMA = "yggdrasil.qtr01.f50.source-model-byte-audit.v1"
ARTIFACT_ID = 14185250784
ARTIFACT_RUN_ID = 43771961699
RECEIPT_NAME = "f50-source-reconciliation-receipt.json"
RECEIPT_SHA256 = "c404f4a85655e05bbd740bd22ede155f895328e679a3cc8a61bd7b5356bd80ed"
ARCHIVE_SHA256 = "b62d6854ae47dd52db37e6523c7f68ee701df6202f2a471cd74f3fd603d199e0"
PREREG = "4bd3c4e0d3de0e3910094e38c14a0141c97ad380"
CANDIDATE = "4f02269f7a21d0207bfb335d1c435b9037a9d07a"
SOURCE_DATA = "5ffae27d69f20188f9fe987b2139cf6a8ca17be74875da269e4caaea8c9ce369"
# Each checkpoint deliberately retains the actual training commit, rather than
# forging current-source identity; neural mathematical role equivalence was
# separately qualified in the earlier reconciliation.
ROLES = {
    "graph_conditioned_gru": (
        "334c562ba6c3b48f1ea8233e9a7efcb787b37fcaf38dd3d06c3d1bf4f5395ecf",
        "def7e7a88517b9afadc6854bd7847d7e4a5d42e6"),
    "law_conditioned_set_mlp": (
        "33e57b5fe4eea03f3b1778589776a9219dd1f9f51291577e54af0ad971e952e8",
        "0f62f98e1a8778e9d7afd8f229d8f5635ec7d3ee"),
    "graph_conditioned_logistic": (
        "155574a006f2d184edcab42e2e7e4b7a09b2c297c0785d2d9fb12d1df8b54344",
        CANDIDATE),
}
NAMES = frozenset({RECEIPT_NAME} | {
    "f50-source-4096-" + kind + ".npz" for kind in ROLES
})


class AuditRejected(RuntimeError):
    pass


def require(cond, reason):
    if not cond:
        raise AuditRejected("F50_BYTE_CUSTODY_" + reason)


def pinned_bytes(path, expected_sha, maximum):
    require(path.is_file() and not path.is_symlink(), "FILE_MISSING_OR_SYMLINK")
    require(0 < path.stat().st_size <= maximum, "UNBOUNDED_FILE")
    content = path.read_bytes()
    require(sha256(content).hexdigest() == expected_sha, "DIGEST_MISMATCH")
    return content


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "DUPLICATE_RECEIPT_KEY")
        result[key] = value
    return result


def audit(directory):
    world.freeze()
    require(world.PREREG_BLOB == PREREG, "PREREG_CHANGED")
    root = Path(directory)
    require(root.is_dir(), "ARTIFACT_MISSING")
    require({p.name for p in root.iterdir()} == NAMES,
            "EXACT_FILE_INVENTORY")
    raw = pinned_bytes(root / RECEIPT_NAME, RECEIPT_SHA256, 20000)
    receipt = json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicate_keys)
    require(type(receipt) is dict and
            receipt.get("schema") == reconciliation.SCHEMA and
            receipt.get("status") == "ALL_THREE_SOURCE_CONTROLS_ROLE_KEY_VERIFIED" and
            receipt.get("candidate_source_sha") == CANDIDATE and
            receipt.get("source_data_sha256") == SOURCE_DATA and
            receipt.get("frozen_prereg_blob") == PREREG and
            receipt.get("target_outcomes") == 0 and
            receipt.get("scientific_pass") is False and
            receipt.get("protected_first_use") is False and
            receipt.get("v1_artifact_id") == reconciliation.OLD_ARTIFACT and
            receipt.get("v2_artifact_id") == reconciliation.NEW_ARTIFACT,
            "SOURCE_ONLY_RECEIPT")
    require(receipt.get("semantic_role_keys") ==
            reconciliation.verify_role_semantics(), "SOURCE_MATH_ROLE_MISMATCH")
    records = receipt.get("models")
    require(type(records) is list and
            [x.get("kind") for x in records] == list(ROLES),
            "THREE_QUALIFIED_MODEL_ROLES")
    result = []
    for entry in records:
        kind = entry["kind"]
        digest, training_sha = ROLES[kind]
        filename = "f50-source-4096-" + kind + ".npz"
        require(entry.get("checkpoint") == filename and
                entry.get("sha256") == digest and
                entry.get("original_source_sha") == training_sha,
                "CHECKPOINT_ORIGINAL_PROVENANCE")
        training = entry.get("source_fit")
        cold = entry.get("synthetic_cold")
        require(type(training) is dict and type(cold) is dict and
                training.get("kind") == kind and
                training.get("status") == "TRAINED_SOURCE_ONLY" and
                training.get("source_training_complete") is True and
                training.get("validation_law_disjoint") is True and
                training.get("source_fit_laws") == 3276 and
                training.get("source_validation_laws") == 820 and
                training.get("scientific_pass") is False and
                cold.get("source_model_sha256") == digest and
                cold.get("cold_bit_exact") is True and
                cold.get("corruption_rejected") is True and
                cold.get("dev_target_outcomes") == 0 and
                cold.get("target_ast_seen") is False and
                cold.get("model_weights_updated") is False,
                "TRAINING_COLD_OR_SCIENCE_FENCE")
        if kind == "graph_conditioned_logistic":
            require(training.get("target_graph_unknown_compatible") is True
                    and training.get("validation_target_graph_hidden") is True
                    and training.get("solver_success") is True,
                    "LOGISTIC_HIDDEN_TARGET_GRAPH_PARITY")
        contents = pinned_bytes(root / filename, digest, 3000000)
        # Real original weights: check NPZ no-pickle array inventory, shapes,
        # dtypes, finite values and checkpoint model cold reconstruction.
        try:
            model, meta = sourcefit.load_checkpoint(
                root / filename, digest, training_sha,
                expected_kind=kind, expected_size=4096)
        except (sourcefit.SourceFitRejected, OSError, ValueError) as exc:
            raise AuditRejected("F50_BYTE_CUSTODY_REAL_MODEL_LOAD") from exc
        require(model is not None and
                meta.get("source_data_sha256") == SOURCE_DATA and
                meta.get("frozen_prereg_blob") == PREREG and
                meta.get("source_fit_laws") == 3276 and
                meta.get("source_validation_laws") == 820 and
                meta.get("episodes_per_law") == 64 and
                meta.get("model_training") == training and
                meta.get("scientific_pass") is False and
                meta.get("no_target_first_use") is True,
                "RESTORED_BYTES_AND_TRAINING_RECEIPT")
        result.append({"kind": kind, "bytes": len(contents),
                       "sha256": digest, "training_sha": training_sha,
                       "model_cold_reconstructed": True})
    return {"schema": SCHEMA,
            "status": "THREE_4096_SOURCE_MODELS_ACTUAL_BYTES_VERIFIED",
            "artifact_id": ARTIFACT_ID, "artifact_run_id": ARTIFACT_RUN_ID,
            "retained_archive_sha256": ARCHIVE_SHA256,
            "receipt_sha256": RECEIPT_SHA256,
            "source_data_sha256": SOURCE_DATA,
            "models": result, "missing_model_sizes": [2048, 1024],
            "dev_target_outcomes": 0, "scientific_pass": False,
            "accepted_weights_changed": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-only", action="store_true", required=True)
    parser.add_argument("--artifact-directory", required=True)
    args = parser.parse_args()
    receipt = audit(args.artifact_directory)
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    print("F50_REAL_4096_MODEL_BYTE_CUSTODY=PASS")
    print("F50_2048_1024_SOURCE_MODELS=UNVERIFIED")
    print("F50_DEV_TARGET_OUTCOMES=0")


if __name__ == "__main__":
    main()

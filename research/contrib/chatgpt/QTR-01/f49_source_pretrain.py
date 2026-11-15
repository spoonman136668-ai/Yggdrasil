#!/usr/bin/env python3
"""F49 source-only pretraining and immutable, reusable baseline checkpoint custody.

NO F49 target outcomes, reserved seeds, or evaluator laws are imported or called.
The single public TRAIN-source table is shared across the conventional controls.
Source fitting is not a scientific DEV or independent evaluation result.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from time import perf_counter

import numpy as np
import f49_worlds as world
import f49_conventional_controls as conventional

SCHEMA = "yggdrasil.qtr01.f49.source-only-pretraining.v1"
KINDS = ("conventional_mlp", "conventional_logistic")
BANK_SIZES = (1024, 512, 256)
FROZEN_BLOB = world.FROZEN_BLOB


def _canonical_bytes(x):
    return np.ascontiguousarray(x, dtype="<f8").tobytes()


def source_dataset_digest(x, y):
    if x.ndim != 2 or x.shape[1] != 18 or y.shape != (len(x),):
        raise conventional.ControlRejected("F49_SOURCE_DATA_SHAPE_INVALID")
    return sha256(b"F49/source-training/dataset/v1\0"
                  + len(y).to_bytes(8, "little")
                  + _canonical_bytes(x) + _canonical_bytes(y)).hexdigest()


def _model_arrays(kind, model):
    if kind == "conventional_logistic":
        if type(model) is not conventional.Logistic:
            raise conventional.ControlRejected("F49_SOURCE_MODEL_TYPE")
        return {"w": model.w}
    if kind != "conventional_mlp" or type(model) is not conventional.MLP:
        raise conventional.ControlRejected("F49_SOURCE_MODEL_TYPE")
    arrays = {}
    for prefix, group in (("p", model.params), ("m", model.m), ("v", model.v)):
        for index, value in enumerate(group):
            arrays[f"{prefix}{index}"] = value
    return arrays


def _checkpoint_meta(kind, size, fit_receipt, source_hash, source_commit, source_seconds):
    if (kind not in KINDS or type(size) is not int or size not in BANK_SIZES
        or not re.fullmatch(r"[0-9a-f]{40}", source_commit)
        or not re.fullmatch(r"[0-9a-f]{64}", source_hash)):
        raise conventional.ControlRejected("F49_CHECKPOINT_META_INVALID")
    return {"schema": SCHEMA, "kind": kind, "bank_size": size,
            "source_commit": source_commit,
            "frozen_prereg_blob": FROZEN_BLOB,
            "source_observations": size * 128,
            "source_data_sha256": source_hash,
            "source_training_seconds": round(source_seconds, 6),
            "fit_details": fit_receipt,
            "optimizer_steps": None}


def write_checkpoint(destination, kind, size, model, fit_details, source_hash,
                     source_commit, source_seconds):
    """Write and immediately cold-verify full params and optimizer moments."""
    meta = _checkpoint_meta(kind, size, fit_details, source_hash,
                            source_commit, source_seconds)
    meta["optimizer_steps"] = int(model.steps)
    arr = _model_arrays(kind, model)
    out = {"meta": np.frombuffer(json.dumps(meta, sort_keys=True, separators=(",", ":")).encode("ascii"), dtype=np.uint8)}
    for name, value in arr.items():
        if value.dtype != np.float64 or not np.isfinite(value).all():
            raise conventional.ControlRejected("F49_NONFINITE_OR_BAD_MODEL_WEIGHT")
        out[name] = value
    destination = Path(destination)
    if destination.exists():
        raise conventional.ControlRejected("F49_REFUSE_OVERWRITE_SOURCE_MODEL")
    np.savez_compressed(destination, **out)
    digest = sha256(destination.read_bytes()).hexdigest()
    recovered = load_checkpoint(destination, digest, source_commit)
    for name, value in arr.items():
        if not np.array_equal(_model_arrays(kind, recovered.model)[name], value):
            raise conventional.ControlRejected("F49_COLD_RESTORATION_MISMATCH")
    return digest, destination.stat().st_size, recovered


def load_checkpoint(path, expected_sha256, expected_source_commit):
    """Fail-closed on checksum, shape, source commit, and protocol pin."""
    world.freeze()
    path = Path(path)
    if (not re.fullmatch(r"[0-9a-f]{64}", expected_sha256)
        or not re.fullmatch(r"[0-9a-f]{40}", expected_source_commit)
        or sha256(path.read_bytes()).hexdigest() != expected_sha256):
        raise conventional.ControlRejected("F49_SOURCE_CHECKPOINT_HASH_MISMATCH")
    try:
        with np.load(path, allow_pickle=False) as checkpoint:
            meta = json.loads(checkpoint["meta"].tobytes().decode("ascii"))
            kind = meta["kind"]
            size = meta["bank_size"]
            if (meta.get("schema") != SCHEMA or kind not in KINDS
                or type(size) is not int or size not in BANK_SIZES
                or meta.get("frozen_prereg_blob") != FROZEN_BLOB
                or meta.get("source_commit") != expected_source_commit
                or meta.get("source_observations") != size * 128
                or not re.fullmatch(r"[0-9a-f]{64}", meta["source_data_sha256"])):
                raise ValueError("invalid metadata")
            model = conventional.MLP(seed=11) if kind == "conventional_mlp" else conventional.Logistic()
            expected = _model_arrays(kind, model)
            if set(checkpoint.files) != {"meta", *expected}:
                raise ValueError("invalid array inventory")
            for name, template in expected.items():
                actual = checkpoint[name]
                if actual.dtype != np.float64 or actual.shape != template.shape or not np.isfinite(actual).all():
                    raise ValueError("invalid model array")
                if kind == "conventional_logistic":
                    model.w = actual.copy()
                else:
                    index = int(name[1:])
                    {"p": model.params, "m": model.m, "v": model.v}[name[0]][index] = actual.copy()
            steps = meta["optimizer_steps"]
            if type(steps) is not int or steps < 0:
                raise ValueError("invalid optimizer steps")
            model.steps = steps
            return conventional.Pretrained(
                kind, size, model, meta["source_observations"],
                meta["source_training_seconds"], meta["fit_details"])
    except (OSError, KeyError, ValueError, TypeError, OverflowError, UnicodeError) as exc:
        raise conventional.ControlRejected("F49_SOURCE_CHECKPOINT_REJECTED") from exc


def train_bank(size, out_dir, source_commit):
    """Full PRE-DEV source fit; ordered high-first by caller."""
    world.freeze()
    if type(size) is not int or size not in BANK_SIZES:
        raise conventional.ControlRejected("F49_UNREGISTERED_BANK_SIZE")
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    start = perf_counter()
    x, y = conventional.permitted_source_training(size)
    source_time = perf_counter() - start
    digest = source_dataset_digest(x, y)
    results = []
    for kind in KINDS:
        t0 = perf_counter()
        if kind == "conventional_mlp":
            model = conventional.MLP(seed=11)
            train_x, train_y, val_x, val_y = conventional.split_train_validation(x, y)
            fitted = model.pretrain(train_x, train_y, val_x, val_y,
                                    max_epochs=200, patience=20)
            source_fit_score = conventional._loss(model.probabilities(val_x), val_y)
        else:
            model = conventional.Logistic()
            fitted = model.fit(x, y, max_iter=500, tolerance=1e-8)
            source_fit_score = conventional._loss(model.probabilities(x), y)
        fit_time = perf_counter() - t0
        file_name = f"f49-source-{size}-{kind}.npz"
        path = root / file_name
        if path.exists():
            raise conventional.ControlRejected("F49_REFUSE_RETRAINED_CHECKPOINT_OVERWRITE")
        checkpoint_hash, nbytes, recovered = write_checkpoint(
            path, kind, size, model, fitted, digest, source_commit,
            source_time + fit_time)
        results.append({"kind": kind, "size": size,
                        "source_rows": len(y), "train_only": True,
                        "data_sha256": digest,
                        "fit_details": fitted,
                        "postfit_train_or_validation_bce": round(source_fit_score, 10),
                        "source_generation_seconds": round(source_time, 6),
                        "fit_seconds": round(fit_time, 6),
                        "whole_source_fit_seconds": round(source_time + fit_time, 6),
                        "checkpoint": file_name, "checkpoint_sha256": checkpoint_hash,
                        "checkpoint_bytes": nbytes,
                        "cold_restore": recovered.model.steps == model.steps,
                        "source_predictions_only": True,
                        "target_first_use": False})
    return results


def run(source_commit, output_dir):
    world.freeze()
    output_dir = Path(output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise conventional.ControlRejected("F49_SOURCE_OUTPUT_DIR_NOT_EMPTY")
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for size in BANK_SIZES:  # 1024, then 512, then 256; no post-result reseeding.
        rows = train_bank(size, output_dir, source_commit)
        results.extend(rows)
        print("F49_SOURCE_BANK_TRAINED="+str(size), flush=True)
    record = {"schema": SCHEMA,
              "classification": "SOURCE_TRAINING_ONLY_NOT_DEV_OR_SCIENTIFIC_PASS",
              "source_commit": source_commit, "prereg_blob": FROZEN_BLOB,
              "bank_sizes_high_first": list(BANK_SIZES),
              "results": results, "full_source_fits": len(results),
              "dev_target_observations": 0,
              "protected_first_use": False,
              "accepted_native_weights_changed": False,
              "scientific_pass": False}
    receipt = output_dir / "f49-source-pretrain-receipt.json"
    receipt.write_text(json.dumps(record, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    return record


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-fit-only", action="store_true")
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args=parser.parse_args()
    if not args.source_fit_only:
        parser.error("F49_SOURCE_TRAINING_REQUIRES_EXPLICIT_SOURCE_ONLY")
    receipt=run(args.source_commit, args.out)
    print("F49_SOURCE_TRAINED_CONTROLS="+str(receipt["full_source_fits"]))
    print("F49_NO_DEVELOPMENT_TARGET_FIRST_USE=PASS")


if __name__ == "__main__":
    main()

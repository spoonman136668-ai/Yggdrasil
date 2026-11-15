"""One-off PUBLIC foundation-only FKP-17 full recurrent training qualification.

No source-private DEV/TRANSFER generator, transfer evaluation, scientific first
use, native-model migration, or source-owner/runner authority is provided here.
To run only after source-safe focus/G29/full regression on this exact candidate.
"""
from __future__ import annotations

import os
import tempfile
import json
from pathlib import Path
import time

import public_policies
import portable_recurrent
import recurrent_control
import source_fixture

EXPECTED_PRIOR = 32768
SEEDS = (1515, 2626)
EPOCHS_PER_SEED = 24


def run_public_foundation_training():
    t0 = time.perf_counter()
    rows = tuple(row for _, _, row in source_fixture.foundation_facts())
    if len(rows) != EXPECTED_PRIOR:
        raise AssertionError("FKP17_RECURRENT_INCOMPLETE_PUBLIC_PRIOR")
    validation = []
    for seed in source_fixture.VALIDATION:
        tape = source_fixture.public_actions(seed, 24)
        validation.extend(source_fixture.collect_public(seed, tape))
    if len(validation) != 384:
        raise AssertionError("FKP17_RECURRENT_VAL_PUBLIC_DRIFT")
    reference = public_policies.PublicRelationArm(
        "STRUCTURED").fit_public_foundation(rows)
    learner = recurrent_control.FullyTrainedRecurrent().fit_public_foundation(
        rows, tuple(validation))
    if not recurrent_control.assert_science_ready(
            learner, reference.foundation_sha256):
        raise AssertionError("FKP17_RECURRENT_FULL_TRAINING_NOT_QUALIFIED")
    learner.begin_world()
    snapshot = learner.state_receipt()
    initial = learner.choose_public(validation[0].before)
    if not 0 <= initial < 8:
        raise AssertionError("FKP17_RECURRENT_FIRST_ACTION_INVALID")
    if learner.state_receipt() != snapshot:
        raise AssertionError("FKP17_RECURRENT_CHOICE_MUTATED_PRIOR")
    # Demonstrates public action feedback only. This is not a held score.
    for record in validation[:24]:
        learner.observe_public(record)
    post = learner.state_receipt()
    if post == snapshot:
        raise AssertionError("FKP17_RECURRENT_PUBLIC_CONTEXT_NOT_UPDATED")
    learner.begin_world()
    if learner.state_receipt() != snapshot:
        raise AssertionError("FKP17_RECURRENT_COLD_RESET_NOT_EXACT")
    # Persistent file is intentionally a public foundation-only artifact;
    # it is never added to the accepted/native repository history.
    checkpoint_file = Path(os.environ.get(
        "FKP17_CHECKPOINT_PATH",
        str(Path(tempfile.gettempdir()) / "fkp17-public-gru-f32.json")))
    snapshot_info = portable_recurrent.export_public_gru(learner, checkpoint_file)
    replay = portable_recurrent.restore_public_gru(
        checkpoint_file, reference.foundation_sha256)
    if replay.state_receipt() != snapshot or (
            not recurrent_control.assert_science_ready(
                replay, reference.foundation_sha256)):
        raise AssertionError("FKP17_RECURRENT_PORTABLE_REPLAY_MISMATCH")
    for public_state in ((0,) * 8, tuple(range(8)), (15,) * 8):
        if replay.choose_public(public_state) != learner.choose_public(public_state):
            raise AssertionError("FKP17_RECURRENT_PORTABLE_PUBLIC_ACTION_MISMATCH")
    if not checkpoint_file.exists() or checkpoint_file.stat().st_size > 512000:
        raise AssertionError("FKP17_RECURRENT_PORTABLE_CHECKPOINT_SIZE")
    receipt = learner.training_receipt
    output = {
        "schema": "fkp17.public-recurrent-foundation-only.v1",
        "result": "ENGINEERING_FOUNDATION_FULL_TRAINING_ONLY",
        "source_prior_sha256": reference.foundation_sha256,
        "public_foundation_rows": len(rows),
        "public_validation_rows": len(validation),
        "trained_seeds": SEEDS,
        "epochs_per_seed": EPOCHS_PER_SEED,
        "selected_seed": receipt["selected_seed"],
        "selected_epoch": receipt["selected_epoch"],
        "per_register_val_crossentropy": receipt["validation_crossentropy_per_register"],
        "learned_bytes": receipt["learned_bytes"],
        "parameters": receipt["parameters"],
        "fit_wall_seconds": receipt["wall_seconds"],
        "total_wall_seconds": time.perf_counter() - t0,
        "cold_public_context_reset": "PASS",
        "portable_cold_replay": "PASS",
        "checkpoint_sha256": snapshot_info["checkpoint_sha256"],
        "checkpoint_bytes": snapshot_info["checkpoint_bytes"],
        "checkpoint_cold_state_sha256": snapshot_info["cold_state_sha256"],
        "original_dev_opened": False,
        "reserved_transfer_opened": False,
        "scientific_pass": False,
        "native_model_promoted": False,
    }
    return output


if __name__ == "__main__":
    record = run_public_foundation_training()
    text = json.dumps(record, sort_keys=True, separators=(",", ":"))
    print("FKP17_ORIGINAL_PUBLIC_FOUNDATION_FULL_TRAIN=" + text)

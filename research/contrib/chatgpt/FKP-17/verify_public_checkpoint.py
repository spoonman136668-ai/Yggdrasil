"""Independent fresh-process and cross-OS portable public GRU checkpoint audit.

Never instantiates a generator or runs original DEV, reserved TRANSFER,
owner-protected worlds, or learner re-training. Source-safe training ONLY.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import portable_recurrent
import recurrent_control

KNOWN_PUBLIC_FOUNDATION_SHA256 = (
    "c8400f67e8d26147de702c0c9bdba1f05581ee6f70635b3e9c90d73d6af81ecf"
)


def verify_public_checkpoint(path, expected_file_sha256):
    path = Path(path)
    if type(expected_file_sha256) is not str or len(expected_file_sha256) != 64:
        raise ValueError("FKP17_COLD_WRONG_DIGEST_TYPE")
    data = path.read_bytes()
    if sha256(data).hexdigest() != expected_file_sha256:
        raise ValueError("FKP17_COLD_FILE_SHA256_MISMATCH")
    learner = portable_recurrent.restore_public_gru(
        path, KNOWN_PUBLIC_FOUNDATION_SHA256)
    recurrent_control.assert_science_ready(
        learner, KNOWN_PUBLIC_FOUNDATION_SHA256)
    ref = learner.state_receipt()
    actions = [learner.choose_public(st) for st in (
        (0,) * 8, tuple(range(8)), (15,) * 8)]
    if learner.state_receipt() != ref:
        raise ValueError("FKP17_COLD_READOUT_MUTATION")
    learner.begin_world()
    if learner.state_receipt() != ref:
        raise ValueError("FKP17_COLD_RESET_NOT_EXACT")
    return {
        "classification": "PORTABLE_PUBLIC_FOUNDATION_ONLY",
        "checkpoint_sha256": expected_file_sha256,
        "source_public_sha256": KNOWN_PUBLIC_FOUNDATION_SHA256,
        "restored_parameter_bytes": learner.learned_bytes,
        "fully_trained_receipt": "PASS",
        "cold_reset": "PASS",
        "three_public_action_choices": actions,
        "held_dev_opened": False,
        "held_transfer_opened": False,
        "scientific_pass": False,
        "native_model_promoted": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint_file")
    parser.add_argument("expected_file_sha256")
    args = parser.parse_args()
    result = verify_public_checkpoint(
        args.checkpoint_file, args.expected_file_sha256)
    print("FKP17_FRESH_PROCESS_PORTABLE_COLD_PASS=" +
          json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

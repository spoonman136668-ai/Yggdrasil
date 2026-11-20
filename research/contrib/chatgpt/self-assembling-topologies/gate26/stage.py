"""Gate26 research-only native public-counter cross-process stages.

No phase or causal-preference oracle is passed to PublicCausalCells.choose().
Each invocation is a fresh Python interpreter and exits after writing/reading.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from yggdrasil.public_causal_cells import PublicCausalCells

MASK = (1 << 32) - 1


def mix(*values: int) -> int:
    x = 0x81F53E67
    for index, value in enumerate(values):
        x ^= ((value + 1) * (0x9E3779B1 + index * 0x23C4A9D7)) & MASK
        x ^= x >> 16
        x = (x * 0x7FEB352D) & MASK
        x ^= x >> 15
        x = (x * 0x846CA68B) & MASK
        x ^= x >> 16
    return x & MASK


def preference(seed: int, retained: bool, address: int) -> int:
    return mix(seed, int(retained), address, 7919) & 1


def observation(seed: int, phase: str, retained: bool, address: int,
                action: int, visit: int, *, held: bool = False) -> int:
    wanted = preference(seed, retained, address)
    if phase == "B" and not retained:
        wanted ^= 1
    threshold = 9 if action == wanted else 1
    domain = 7 if phase == "A" else 17
    if held:
        domain += 101
    return int(mix(seed, domain, int(retained), address, action, visit) % 10 < threshold)


def training_events(seed: int, phase: str):
    """Deterministic exploratory interventions; never an autonomous action selector."""
    if phase not in ("A", "B"):
        raise ValueError("GATE26_INVALID_PHASE")
    retained_types = (False, True) if phase == "A" else (False,)
    count = 24 if phase == "A" else 64
    for retained in retained_types:
        for address in range(5):
            for action in (0, 1):
                for visit in range(count):
                    yield retained, address, action, observation(
                        seed, phase, retained, address, action, visit
                    )


def apply_events(cells: PublicCausalCells, seed: int, phase: str) -> None:
    for retained, address, action, outcome in training_events(seed, phase):
        cells.observe(address, action, outcome, retained=retained)


def readout(cells: PublicCausalCells):
    """Functional historical readout, including completely unseen addresses."""
    rows = []
    for retained, limit in ((False, 7), (True, 9)):
        for address in range(limit):
            contrast = cells.observed_action_contrast(address, retained=retained)
            rows.append({
                "retained": retained,
                "address": address,
                "choice": cells.choose(address, retained=retained),
                "wilson": cells.choose_wilson(address, retained=retained),
                "contrast": list(contrast) if contrast is not None else None,
            })
    return rows


def stage_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=("train_a", "train_b", "read_b"))
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--input", dest="input_checkpoint", type=Path)
    parser.add_argument("--output", dest="output_checkpoint", type=Path)
    args = parser.parse_args()

    if args.phase == "train_a":
        if args.input_checkpoint is not None or args.output_checkpoint is None:
            raise ValueError("GATE26_A_PATHS_INVALID")
        cells = PublicCausalCells()
        apply_events(cells, args.seed, "A")
    else:
        if args.input_checkpoint is None:
            raise ValueError("GATE26_B_OR_READ_MISSING_INPUT")
        raw = args.input_checkpoint.read_bytes()
        cells = PublicCausalCells.restore(raw)
        if cells.snapshot() != raw:
            raise AssertionError("GATE26_RESTORED_BYTE_MISMATCH")
        if args.phase == "train_b":
            if args.output_checkpoint is None:
                raise ValueError("GATE26_B_MISSING_OUTPUT")
            apply_events(cells, args.seed, "B")
        elif args.output_checkpoint is not None:
            raise ValueError("GATE26_READ_MUST_NOT_WRITE")

    output = cells.snapshot()
    if args.output_checkpoint is not None:
        args.output_checkpoint.write_bytes(output)
    print(json.dumps({
        "stage": args.phase, "pid": os.getpid(),
        "digest": hashlib.sha256(output).hexdigest(),
        "size": len(output), "readout": readout(cells)
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    stage_main()

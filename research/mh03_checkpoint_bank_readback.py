"""MH03 evaluator-only V32E bank storage probe. Never selects a bank for a learner.

No native state, training schedule, original cohort or source action is executed here.
This source-pinned implementation reconstructs *read-only* V32E numeric scoring.
The forced-bank forecasts are oracle evaluator diagnostics, NOT native retrieval.
"""
from __future__ import annotations

import hashlib
import math
import struct
from pathlib import Path

MAGIC = b"V32EMIC1"
SIZE = 2264
N, C, A = 8, 4, 3
GAIN, HOPS = 0.92, 4
INPUT = (1, 3, 7, 4)
OUTPUT = (0, 2, 5)
CELL_BYTES = 280
WINDOW = 24
SOURCE_BLOB = "85237dcc82905e05a273b11023b5be5db722726e"
# The original source Git blob is separately checked in exact-SHA GitHub Actions.
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "itd02_v32e_pair_consensus.rs"


def fnv64(data: bytes) -> int:
    h = 0xCBF29CE484222325
    for byte in data:
        h = ((h ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h


def parse_checkpoint(snapshot: bytes) -> dict:
    """Validate and decode only source-owned checkpoint fields, never modify input."""
    if type(snapshot) is not bytes or len(snapshot) != SIZE:
        raise ValueError("MH03_CHECKPOINT_LENGTH")
    if snapshot[:8] != MAGIC:
        raise ValueError("MH03_CHECKPOINT_MAGIC")
    (recorded,) = struct.unpack_from("<Q", snapshot, SIZE - 8)
    if recorded != fnv64(snapshot[:-8]):
        raise ValueError("MH03_CHECKPOINT_FNV")
    (updates,) = struct.unpack_from("<Q", snapshot, 8)
    if updates > 100_000_000:
        raise ValueError("MH03_CHECKPOINT_UPDATES")
    cells = []
    for i in range(N):
        pos = 16 + i * CELL_BYTES
        count, active, age0, age1, switches, events, certified, resets = (
            struct.unpack_from("<8Q", snapshot, pos))
        if (active > 1 or events > 36 or certified > 12 or switches > updates
                or age0 + age1 != count or count > updates):
            raise ValueError("MH03_CHECKPOINT_LEDGER")
        window = snapshot[pos + 64:pos + 64 + WINDOW]
        if (any(x > 3 for x in window[:12])
                or any(x > 1 for x in window[12:])
                or sum(window[12:]) != certified):
            raise ValueError("MH03_CHECKPOINT_WINDOW")
        weights = struct.unpack_from("<24d", snapshot, pos + 64 + WINDOW)
        if any(not math.isfinite(v) or abs(v) > 8.0 for v in weights):
            raise ValueError("MH03_CHECKPOINT_WEIGHTS")
        # Native serialized order: [bank][action][cue].
        banks = tuple(tuple(tuple(weights[b * 12 + a * 4 + c]
                for c in range(C)) for a in range(A)) for b in range(2))
        cells.append({"index": i, "active": int(active), "age": (age0, age1),
                      "count": count, "switches": switches, "weights": banks})
    return {"sha256": hashlib.sha256(snapshot).hexdigest(),
            "update_calls": updates, "cells": tuple(cells)}


def scores(checkpoint: dict, cue: int, bank: int | None = None) -> tuple[float, ...]:
    """Source-equivalent four-hop ring readout; forced bank is evaluator-only."""
    if type(cue) is not int or not 0 <= cue < C:
        raise ValueError("MH03_BAD_CUE")
    if bank is not None and (type(bank) is not int or bank not in (0, 1)):
        raise ValueError("MH03_BAD_EVALUATOR_BANK")
    cells = checkpoint["cells"]
    if len(cells) != N:
        raise ValueError("MH03_INVALID_CELL_COUNT")
    sense = [[0.0] * C for _ in range(N)]
    sense[INPUT[cue]][cue] = 1.0
    for _ in range(HOPS):
        sense = [[max(sense[i][c],
                     GAIN * max(sense[(i - 1) % N][c],
                                sense[(i + 1) % N][c]))
                  for c in range(C)] for i in range(N)]
    outputs = []
    for action in range(A):
        local = [sum(sense[i][c] *
                     cells[i]["weights"][cells[i]["active"] if bank is None else bank][action][c]
                     for c in range(C)) for i in range(N)]
        for _ in range(HOPS):
            local = [0.5 * local[i] + 0.25 * local[(i - 1) % N] +
                     0.25 * local[(i + 1) % N] for i in range(N)]
        outputs.append(local[OUTPUT[action]])
    return tuple(outputs)


def inspect_snapshot(snapshot: bytes) -> dict:
    """Compare current active-bank behavior against each *offline* bank choice."""
    state = parse_checkpoint(snapshot)
    return {
        "checkpoint_sha256": state["sha256"],
        "active_bank_vector": tuple(c["active"] for c in state["cells"]),
        "bank_ages": tuple(c["age"] for c in state["cells"]),
        "update_calls": state["update_calls"],
        "readouts": {name: tuple(scores(state, cue, bank) for cue in range(C))
                     for name, bank in (("active", None), ("forced_bank0", 0),
                                        ("forced_bank1", 1))},
        "forced_bank_readouts_are_evaluator_only": True,
        "scientific_gain_verified": False,
    }

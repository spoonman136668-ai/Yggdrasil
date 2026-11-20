"""DWSA-01: restricted weight-only compiler; isolated development, no donor inference.

Synthetic donor artifacts are generated as numeric layer tensors, but there is
intentionally no donor forward/evaluate function in this module. The oracle
uses the independent symbolic law specification, never donor activations.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import struct
import time

INPUT_BITS = 8
OUTPUTS = 2
HIDDEN = 12
SLOTS = 16
SEEDS = (19, 41, 73)
MAGIC = b"DWS1"
CHECKPOINT_BYTES = 4 + 1 + 4 * SLOTS + 32
SOURCE_BYTES = HIDDEN * (INPUT_BITS + 1 + OUTPUTS) * 8


def synthetic_artifact(seed: int) -> tuple[dict, tuple]:
    """Construct a numerical checkpoint plus *separately held* truth rules.

    This is a controlled source generator, not training a teacher or running
    donor inference. Its data are not an authentic pretrained checkpoint.
    """
    rng = random.Random(seed)
    hidden, biases = [], []
    readout = [[], []]
    laws = []
    for _ in range(HIDDEN):
        count = 2 + rng.randrange(2)
        indices = rng.sample(range(INPUT_BITS), count)
        positive = negative = 0
        for index in indices:
            if rng.randrange(2):
                positive |= 1 << index
            else:
                negative |= 1 << index
        routes = (rng.choice((-3, -2, -1, 1, 2, 3)),
                  rng.choice((-3, -2, -1, 1, 2, 3)))
        scale = rng.choice((1.0, 2.0, 4.0))
        row = [0.0] * INPUT_BITS
        for i in range(INPUT_BITS):
            if positive & (1 << i):
                row[i] = 2.0 * scale
            elif negative & (1 << i):
                row[i] = -2.0 * scale
        hidden.append(row)
        biases.append(scale * (1 - 2 * positive.bit_count()))
        for channel in range(OUTPUTS):
            readout[channel].append(routes[channel] / scale)
        laws.append((positive, negative, routes[0], routes[1]))
    return {"hidden": hidden, "bias": biases, "readout": readout}, tuple(laws)


def oracle_scores(laws: tuple, bits: int) -> tuple[int, int]:
    """Independently encoded law evaluator, not a donor model forward pass."""
    assert 0 <= bits < (1 << INPUT_BITS)
    s0 = s1 = 0
    for pos, neg, a, b in laws:
        if bits & pos == pos and bits & neg == 0:
            s0 += a
            s1 += b
    return s0, s1


def decision(scores: tuple[int, int]) -> int | None:
    if scores[0] == scores[1]:
        return None
    return 0 if scores[0] > scores[1] else 1


class NativeRouter:
    """Versioned fixed-footprint 16-slot compiled motif router."""

    __slots__ = ("_raw",)

    def __init__(self, raw: bytes) -> None:
        self._raw = raw

    def snapshot(self) -> bytes:
        return self._raw

    @classmethod
    def restore(cls, raw: bytes) -> "NativeRouter":
        if (type(raw) is not bytes or len(raw) != CHECKPOINT_BYTES or
                raw[:4] != MAGIC or
                hashlib.sha256(raw[:-32]).digest() != raw[-32:]):
            raise ValueError("DWSA_CHECKPOINT_REJECTED")
        count = raw[4]
        if not 0 < count <= SLOTS:
            raise ValueError("DWSA_SLOT_COUNT_REJECTED")
        for i in range(SLOTS):
            rec = raw[5 + i * 4:9 + i * 4]
            pos, neg, a, b = struct.unpack(">BBbb", rec)
            if i >= count:
                if rec != b"\0\0\0\0":
                    raise ValueError("DWSA_PADDING_REJECTED")
            elif (pos & neg or not 2 <= (pos | neg).bit_count() <= 3 or
                  not (-3 <= a <= 3 and -3 <= b <= 3) or
                  (a == 0 and b == 0)):
                raise ValueError("DWSA_MOTIF_REJECTED")
        return cls(raw)

    def score(self, bits: int) -> tuple[int, int]:
        if type(bits) is not int or not 0 <= bits < (1 << INPUT_BITS):
            raise ValueError("DWSA_INPUT_REJECTED")
        a_total = b_total = 0
        for i in range(self._raw[4]):
            pos, neg, a, b = struct.unpack_from(">BBbb", self._raw, 5 + 4 * i)
            if bits & pos == pos and bits & neg == 0:
                a_total += a
                b_total += b
        return a_total, b_total

    def choose(self, bits: int) -> int | None:
        return decision(self.score(bits))


def compile_weight_only(donor: dict) -> NativeRouter:
    """Recover restricted binary conjunctions from numeric tensors only.

    No access to the independent truth specification, samples, labels,
    gradients, donor hidden activations, or teacher outputs.
    """
    if type(donor) is not dict or set(donor) != {"hidden", "bias", "readout"}:
        raise ValueError("DWSA_DONOR_SCHEMA_REJECTED")
    hidden, biases, readout = (donor["hidden"], donor["bias"],
                               donor["readout"])
    if (type(hidden) is not list or not 0 < len(hidden) <= SLOTS or
        type(biases) is not list or len(biases) != len(hidden) or
        type(readout) is not list or len(readout) != OUTPUTS or
        any(type(ch) is not list or len(ch) != len(hidden)
            for ch in readout)):
        raise ValueError("DWSA_DONOR_SHAPE_REJECTED")
    records = bytearray()
    for j, row in enumerate(hidden):
        if type(row) is not list or len(row) != INPUT_BITS or any(
            type(v) not in (int, float) or not math.isfinite(v) for v in row
        ):
            raise ValueError("DWSA_HIDDEN_REJECTED")
        used = [abs(v) for v in row if v != 0.0]
        if not 2 <= len(used) <= 3 or len(set(used)) != 1:
            raise ValueError("DWSA_UNSUPPORTED_WEIGHT_MOTIF")
        scale = used[0] / 2
        pos = sum((1 << i) for i, v in enumerate(row) if v > 0)
        neg = sum((1 << i) for i, v in enumerate(row) if v < 0)
        bias = biases[j]
        if (type(bias) not in (int, float) or not math.isfinite(bias) or
                bias != scale * (1 - 2 * pos.bit_count())):
            raise ValueError("DWSA_UNSUPPORTED_BIAS")
        routes = []
        for channel in range(OUTPUTS):
            w = readout[channel][j]
            if type(w) not in (int, float) or not math.isfinite(w):
                raise ValueError("DWSA_READOUT_REJECTED")
            recovered = w * scale
            if (not recovered.is_integer() if isinstance(recovered, float)
                    else recovered != int(recovered)) or not -3 <= recovered <= 3:
                raise ValueError("DWSA_NONINTEGRAL_READOUT")
            routes.append(int(recovered))
        if routes == [0, 0]:
            raise ValueError("DWSA_EMPTY_ROUTE")
        records.extend(struct.pack(">BBbb", pos, neg, *routes))
    body = MAGIC + bytes([len(hidden)]) + bytes(records).ljust(4 * SLOTS, b"\0")
    return NativeRouter.restore(body + hashlib.sha256(body).digest())


def gauge_variant(donor: dict, seed: int, variant: int) -> dict:
    """Permute hidden units and apply positive diagonal ReLU symmetry."""
    rng = random.Random(seed + 1009 * variant)
    n = len(donor["hidden"])
    perm = list(range(n))
    rng.shuffle(perm)
    factors = [rng.choice((0.5, 1.0, 2.0, 4.0)) for _ in range(n)]
    return {
        "hidden": [[v * factors[k] for v in donor["hidden"][k]] for k in perm],
        "bias": [donor["bias"][k] * factors[k] for k in perm],
        "readout": [[channel[k] / factors[k] for k in perm]
                    for channel in donor["readout"]],
    }


def shuffled_route_sham(donor: dict) -> dict:
    """Same tensors and capacity with output routes paired to wrong units."""
    return {"hidden": [row[:] for row in donor["hidden"]],
            "bias": donor["bias"][:],
            "readout": [channel[1:] + channel[:1]
                        for channel in donor["readout"]]}


def run_frozen_development() -> dict:
    started = time.perf_counter()
    exact_scores = exact_choices = non_tie = sham_agree = sham_cases = 0
    cases = source_cases = 0
    abstentions = 0
    cold_restores = 0
    for seed in SEEDS:
        donor, laws = synthetic_artifact(seed)
        raw_native = compile_weight_only(donor).snapshot()
        cold = NativeRouter.restore(raw_native)
        assert cold.snapshot() == raw_native
        cold_restores += 1
        sham = compile_weight_only(shuffled_route_sham(donor))
        for bits in range(1 << INPUT_BITS):
            expected = oracle_scores(laws, bits)
            got = cold.score(bits)
            source_cases += 1
            if decision(expected) is None:
                abstentions += 1
            if decision(expected) is not None:
                sham_cases += 1
                sham_agree += int(sham.choose(bits) == decision(expected))
        for variant in range(4):
            candidate = (cold if variant == 0 else
                         compile_weight_only(gauge_variant(donor, seed, variant)))
            candidate = NativeRouter.restore(candidate.snapshot())
            for bits in range(1 << INPUT_BITS):
                expected = oracle_scores(laws, bits)
                got = candidate.score(bits)
                cases += 1
                exact_scores += (got == expected)
                exact_choices += (candidate.choose(bits) == decision(expected))
                non_tie += (decision(expected) is not None)
    return {
        "schema": "dwsa01.synthetic-mechanical-dev.v1",
        "seeds": list(SEEDS),
        "source_world_input_pairs": source_cases,
        "tested_cases": cases,
        "score_exact_cases": exact_scores,
        "choice_exact_cases": exact_choices,
        "non_tie_cases": non_tie,
        "source_oracle_abstentions": abstentions,
        "sham_nontie_agreements": sham_agree,
        "sham_nontie_cases": sham_cases,
        "checkpoint_bytes": CHECKPOINT_BYTES,
        "serialized_donor_bytes": SOURCE_BYTES,
        "compression_ratio": SOURCE_BYTES / CHECKPOINT_BYTES,
        "cold_restores": cold_restores,
        "donor_forward_calls": 0,
        "independent_exact_control_gap": 0,
        "wall_seconds_development_diagnostic": time.perf_counter() - started,
    }


if __name__ == "__main__":
    print(json.dumps(run_frozen_development(), sort_keys=True, indent=2))

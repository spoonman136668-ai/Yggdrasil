"""DWSA-02: zero-teacher, static trained-weight routing extraction (DEV ONLY).

Use only the pinned archived donor artifact. Never import or call donor model.
Do not interpret a compressed linear routing projection as nonlinear competence.
Protocol: DWSA-02-PROTOCOL.md (pre-scoring git commit 25515d5173a699c9ad04bf2b9b1bd9f926047d17).
"""
from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path
import random
import struct
import sys
import time
import zipfile

ZIP_SHA = "b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d"
STATE_SHA = "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
STATE_MEMBER = "amalgam-joint-state.json"
SCHEMA = "yggdrasil.ckad.native-causal-amalgam.v1"
DIMS = (3, 5, 43, 45)
NATIVE_BYTES = 320
BODY_BYTES = NATIVE_BYTES - 32
PARAMETER_FLOATS = 872
MAGIC = b"DWS2"
MAX_ZIP_BYTES = 8_000_000
MAX_MEMBER_BYTES = 4_000_000


def need(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("DWSA02_REJECT_" + reason)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def read_archive(path: Path) -> tuple[dict, tuple]:
    raw = path.read_bytes()
    need(len(raw) <= MAX_ZIP_BYTES and sha(raw) == ZIP_SHA, "ZIP_CUSTODY")
    with zipfile.ZipFile(io.BytesIO(raw)) as arc:
        need(len(arc.namelist()) == 3 and STATE_MEMBER in arc.namelist(), "ZIP_MEMBERS")
        info = arc.getinfo(STATE_MEMBER)
        need(info.file_size == 2921047 and info.file_size <= MAX_MEMBER_BYTES,
             "MEMBER_SIZE")
        state_raw = arc.read(STATE_MEMBER)
    need(sha(state_raw) == STATE_SHA, "STATE_CUSTODY")
    state = json.loads(state_raw)
    need(type(state) is dict and state.get("schema") == SCHEMA, "STATE_SCHEMA")
    heads = state.get("action_heads")
    temporal = state.get("temporal_heads")
    need(type(heads) is list and type(temporal) is list and
         len(heads) == len(temporal) == 2, "HEAD_ROSTER")
    four = tuple(heads + temporal)
    for i, head in enumerate(four):
        validate_head(head, DIMS[i], "transition" if i % 2 == 0 else "reward")
    return state, four


def validate_head(head: object, dimension: int, kind: str) -> None:
    need(type(head) is dict and set(head) == {
        "kind", "encoder", "encoder_bias", "predictor", "predictor_bias", "steps"
    }, "HEAD_KEYS")
    need(head["kind"] == kind and type(head["steps"]) is int and
         head["steps"] == 2109, "HEAD_SOURCE")
    e, b, p, q = (head[k] for k in
                  ("encoder", "encoder_bias", "predictor", "predictor_bias"))
    need(type(e) is list and len(e) == 8 and type(b) is list and len(b) == 8 and
         type(p) is list and len(p) == 2 and type(q) is list and len(q) == 2,
         "HEAD_SHAPE")
    need(all(type(row) is list and len(row) == dimension for row in e) and
         all(type(row) is list and len(row) == 8 for row in p), "HEAD_MATRIX")
    vals = [v for row in e+p for v in row] + b + q
    need(len(vals) == 8*dimension + 8 + 16 + 2 and
         all(type(v) is float and math.isfinite(v) for v in vals), "HEAD_VALUES")
    need(any(v != 0.0 for v in vals), "HEAD_EMPTY")


def algebraic_route(head: dict) -> tuple[float, ...]:
    """Only matrix products of stored weights, never tanh or source forward."""
    e, b, p, q = (head[k] for k in
                  ("encoder", "encoder_bias", "predictor", "predictor_bias"))
    dimension = len(e[0])
    coeff = []
    for channel in range(2):
        coeff.extend(math.fsum(p[channel][h]*e[h][i] for h in range(8))
                     for i in range(dimension))
    coeff.extend(math.fsum(p[channel][h]*b[h] for h in range(8)) + q[channel]
                 for channel in range(2))
    return tuple(coeff)


def exact_routes(heads: tuple) -> tuple[tuple[float, ...], ...]:
    return tuple(algebraic_route(head) for head in heads)


def compile_routes(heads: tuple) -> bytes:
    need(type(heads) is tuple and len(heads) == 4, "COMPILE_ROSTER")
    body = bytearray(MAGIC + b"\x01" + bytes(DIMS))
    scales = []
    qbytes = bytearray()
    for i, head in enumerate(heads):
        validate_head(head, DIMS[i], "transition" if i % 2 == 0 else "reward")
        coefficients = algebraic_route(head)
        scale = max(map(abs, coefficients)) / 127 or 1.0
        need(math.isfinite(scale) and scale > 0, "SCALE")
        scales.append(scale)
        for v in coefficients:
            quantized = max(-127, min(127, round(v/scale)))
            qbytes.extend(struct.pack(">b", quantized))
    need(len(qbytes) == 200, "COEFFICIENT_COUNT")
    for s in scales:
        body.extend(struct.pack(">d", s))
    body.extend(qbytes)
    body.extend(bytes(BODY_BYTES - len(body)))
    need(len(body) == BODY_BYTES, "BODY_SIZE")
    return bytes(body) + hashlib.sha256(body).digest()


def restore(raw: bytes) -> tuple[tuple[float, ...], ...]:
    need(type(raw) is bytes and len(raw) == NATIVE_BYTES and
         raw[:4] == MAGIC and raw[4] == 1 and raw[5:9] == bytes(DIMS) and
         hashlib.sha256(raw[:BODY_BYTES]).digest() == raw[BODY_BYTES:],
         "NATIVE_HEADER_OR_HASH")
    scales = struct.unpack(">4d", raw[9:41])
    need(all(math.isfinite(s) and s > 0 for s in scales), "NATIVE_SCALES")
    need(raw[241:BODY_BYTES] == bytes(47), "NATIVE_PADDING")
    values = struct.unpack(">200b", raw[41:241])
    need(all(-127 <= v <= 127 for v in values), "NATIVE_VALUES")
    offset = 0
    result = []
    for index, dim in enumerate(DIMS):
        count = 2*dim + 2
        result.append(tuple(v*scales[index] for v in values[offset:offset+count]))
        offset += count
    need(offset == 200, "NATIVE_COUNT")
    return tuple(result)


def gauge(head: dict, seed: int) -> dict:
    """Joint hidden signed permutation leaves P@E and P@b invariant."""
    rng = random.Random(seed)
    permutation = list(range(8))
    rng.shuffle(permutation)
    signs = [rng.choice((-1, 1)) for _ in range(8)]
    return {
        "kind": head["kind"], "steps": head["steps"],
        "encoder": [[head["encoder"][h][i] * signs[h]
                     for i in range(len(head["encoder"][h]))]
                    for h in permutation],
        "encoder_bias": [head["encoder_bias"][h] * signs[h] for h in permutation],
        "predictor": [[head["predictor"][k][h] * signs[h] for h in permutation]
                      for k in range(2)],
        "predictor_bias": list(head["predictor_bias"]),
    }


def sham(head: dict) -> dict:
    return {
        **head,
        "predictor": [list(row[1:] + row[:1]) for row in head["predictor"]],
    }


def squared_error(candidate: tuple, reference: tuple) -> float:
    return math.fsum((a-b)**2 for aa, bb in zip(candidate, reference)
                     for a, b in zip(aa, bb))


def run_dev(path: Path) -> dict:
    started = time.perf_counter()
    _, heads = read_archive(path)
    reference = exact_routes(heads)
    checkpoint = compile_routes(heads)
    measured = restore(checkpoint)
    duplicate_match = checkpoint == compile_routes(heads)
    cold_restores = sum(restore(bytes(checkpoint)) == measured for _ in range(3))
    gauge_checks = 0
    max_gauge_error = 0.0
    for index, head in enumerate(heads):
        for seed in (101, 202, 303):
            candidate = gauge(head, seed)
            validate_head(candidate, DIMS[index],
                          "transition" if index % 2 == 0 else "reward")
            rv = algebraic_route(candidate)
            max_gauge_error = max(max_gauge_error,
                                  max(abs(a-b) for a,b in zip(reference[index], rv)))
            gauge_checks += 1
    max_error = max(abs(a-b) for aa,bb in zip(measured,reference)
                    for a,b in zip(aa,bb))
    scales = struct.unpack(">4d", checkpoint[9:41])
    quantization_bounds = all(abs(a-b) <= scales[i]/2 + 1e-12
                              for i, (m, r) in enumerate(zip(measured, reference))
                              for a,b in zip(m,r))
    sham_routes = tuple(algebraic_route(sham(h)) for h in heads)
    zeros = tuple(tuple(0.0 for _ in row) for row in reference)
    error = squared_error(measured, reference)
    ref_norm = squared_error(zeros, reference)
    need(ref_norm > 0, "REFERENCE_ZERO")
    need(sham_routes != reference, "SHAM_INERT")
    # Arithmetic oracle and independently expressed ordinary uniform int8
    # product-quantization baseline are not superiority targets: they tie.
    baseline = tuple(tuple(round(v/s)*s for v in row)
                     for row,s in zip(reference,scales))
    need(all(abs(a-b) <= 1e-12 for rr,bb in zip(measured,baseline)
             for a,b in zip(rr,bb)), "MATCHED_CONTROL")
    need(quantization_bounds and max_gauge_error <= 1e-12 and
         gauge_checks == 12 and cold_restores == 3 and duplicate_match,
         "STATIC_MECHANICAL_GATE")
    return {
        "schema": "dwsa02.archived-trained-structure-dev.v1",
        "protocol_precommit": "25515d5173a699c9ad04bf2b9b1bd9f926047d17",
        "donor_zip_sha256": ZIP_SHA, "donor_state_sha256": STATE_SHA,
        "donor_forward_calls": 0, "donor_training_steps_executed": 0,
        "donor_head_steps_recorded": [2109]*4,
        "input_dimensions": list(DIMS), "coefficients": 200,
        "native_bytes": NATIVE_BYTES, "source_parameter_float64_bytes": PARAMETER_FLOATS*8,
        "ratio_vs_float64_parameters_only": (PARAMETER_FLOATS*8)/NATIVE_BYTES,
        "cold_restores": cold_restores, "deterministic_duplicate": duplicate_match,
        "gauge_cases": gauge_checks, "max_gauge_error": max_gauge_error,
        "max_quantized_coefficient_error": max_error,
        "normalized_l2_coefficient_error": math.sqrt(error/ref_norm),
        "exact_algebraic_oracle_error": 0,
        "ordinary_uniform_int8_product_control_ties": True,
        "sham_squared_error": squared_error(sham_routes, reference),
        "zero_squared_error": ref_norm,
        "quantization_bound_pass": quantization_bounds,
        "wall_seconds_local_diagnostic": time.perf_counter()-started,
        "engineering": "LOCAL_STATIC_DEV_PASS",
        "scientific": "UNVERIFIED", "deployment": "NONE",
    }


if __name__ == "__main__":
    need(len(sys.argv) == 2, "USAGE_EXPECT_ZIP_PATH")
    print(json.dumps(run_dev(Path(sys.argv[1])), sort_keys=True, indent=2))

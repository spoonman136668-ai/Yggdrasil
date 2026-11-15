"""Portable, bounded, pickle-free GRU checkpoint with SHA256 integrity.

This is deterministic numeric custody, not a signed authority attestation,
general intelligence proof, or permission to score fresh protected worlds.
Weights are stored as named little-endian float32 arrays in canonical JSON.
"""
from __future__ import annotations

from base64 import b64encode, b64decode
from hashlib import sha256
import json
from pathlib import Path
import struct

import recurrent_control as recurrent

SCHEMA = "fkp17.public-gru-f32-checkpoint.v1"
MAX_FILE_BYTES = 512000
MAX_MODEL_BYTES = 1048576
REQUIRED_OUTER = {"payload", "payload_sha256"}
REQUIRED_PAYLOAD = {"schema", "source_public_sha256", "training_receipt",
                    "cold_state_sha256", "tensors"}


def _canonical(value):
    return json.dumps(value, ensure_ascii=True, allow_nan=False,
                      sort_keys=True, separators=(",", ":")).encode("ascii")


def _unique_pairs(pairs):
    output = {}
    for key, value in pairs:
        if key in output:
            raise ValueError("FKP17_DUPLICATE_JSON_KEY")
        output[key] = value
    return output


def _no_constants(_):
    raise ValueError("FKP17_NONFINITE_JSON")


def _tensor_blob(tensor):
    contiguous = tensor.detach().cpu().contiguous().reshape(-1)
    if tensor.dtype != recurrent._torch().float32:
        raise ValueError("FKP17_CHECKPOINT_NON_FLOAT32")
    values = contiguous.tolist()
    raw = struct.pack("<" + "f" * len(values), *values)
    return raw


def export_public_gru(learner, file_path):
    if type(learner) is not recurrent.FullyTrainedRecurrent or learner._net is None:
        raise ValueError("FKP17_CHECKPOINT_UNTRAINED_MODEL")
    if learner.world_count:
        raise ValueError("FKP17_CHECKPOINT_NONCOLD_WORLD")
    layers = []
    for name, tensor in sorted(learner._net.state_dict().items()):
        raw = _tensor_blob(tensor)
        layers.append({"name": name, "shape": list(tensor.shape),
                       "dtype": "f32le", "sha256": sha256(raw).hexdigest(),
                       "data": b64encode(raw).decode("ascii")})
    receipt = learner.training_receipt
    if not isinstance(receipt, dict):
        raise ValueError("FKP17_CHECKPOINT_MISSING_FIT_RECEIPT")
    payload = {"schema": SCHEMA,
               "source_public_sha256": learner.foundation_sha256,
               "training_receipt": receipt,
               "cold_state_sha256": learner.state_receipt(),
               "tensors": layers}
    envelope = {"payload": payload, "payload_sha256": sha256(_canonical(payload)).hexdigest()}
    data = _canonical(envelope) + b"\n"
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("FKP17_CHECKPOINT_TOO_LARGE")
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Write a bounded file, no pickle or untrusted code execution.
    path.write_bytes(data)
    return {"checkpoint_sha256": sha256(data).hexdigest(),
            "checkpoint_bytes": len(data),
            "cold_state_sha256": payload["cold_state_sha256"],
            "source_public_sha256": payload["source_public_sha256"]}


def restore_public_gru(file_path, expected_source_sha256):
    if type(expected_source_sha256) is not str or len(expected_source_sha256) != 64:
        raise ValueError("FKP17_CHECKPOINT_EXPECTED_DIGEST")
    path = Path(file_path)
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("FKP17_CHECKPOINT_SIZE_LIMIT")
    try:
        envelope = json.loads(path.read_bytes().decode("ascii"),
                              object_pairs_hook=_unique_pairs,
                              parse_constant=_no_constants)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("FKP17_CHECKPOINT_BAD_JSON") from exc
    if type(envelope) is not dict or set(envelope) != REQUIRED_OUTER:
        raise ValueError("FKP17_CHECKPOINT_OUTER_SCHEMA")
    payload = envelope["payload"]
    if type(payload) is not dict or set(payload) != REQUIRED_PAYLOAD:
        raise ValueError("FKP17_CHECKPOINT_PAYLOAD_SCHEMA")
    if sha256(_canonical(payload)).hexdigest() != envelope["payload_sha256"]:
        raise ValueError("FKP17_CHECKPOINT_PAYLOAD_TAMPER")
    if payload["schema"] != SCHEMA or payload["source_public_sha256"] != expected_source_sha256:
        raise ValueError("FKP17_CHECKPOINT_SOURCE_OR_VERSION")
    torch = recurrent._torch()
    net = recurrent._network(torch).to("cpu")
    wanted = net.state_dict()
    entries = payload["tensors"]
    if type(entries) is not list or len(entries) != len(wanted):
        raise ValueError("FKP17_CHECKPOINT_LAYER_COUNT")
    restored = {}
    total = 0
    for item, (key, original) in zip(entries, sorted(wanted.items())):
        if type(item) is not dict or set(item) != {"name", "shape", "dtype", "sha256", "data"}:
            raise ValueError("FKP17_CHECKPOINT_LAYER_SCHEMA")
        if item["name"] != key or item["dtype"] != "f32le" or item["shape"] != list(original.shape):
            raise ValueError("FKP17_CHECKPOINT_LAYER_IDENTITY")
        if type(item["data"]) is not str:
            raise ValueError("FKP17_CHECKPOINT_LAYER_TYPE")
        try:
            raw = b64decode(item["data"], validate=True)
        except Exception as exc:
            raise ValueError("FKP17_CHECKPOINT_INVALID_BASE64") from exc
        total += len(raw)
        if total > MAX_MODEL_BYTES or len(raw) != original.numel() * 4:
            raise ValueError("FKP17_CHECKPOINT_PARAMETER_SIZE")
        if sha256(raw).hexdigest() != item["sha256"]:
            raise ValueError("FKP17_CHECKPOINT_LAYER_TAMPER")
        floats = struct.unpack("<" + "f" * original.numel(), raw)
        restored[key] = torch.tensor(floats, dtype=torch.float32,
                                      device="cpu").reshape(original.shape)
    net.load_state_dict(restored, strict=True)
    net.eval()
    learner = recurrent.FullyTrainedRecurrent()
    learner._net, learner._torch = net, torch
    learner._digest = expected_source_sha256
    learner.foundation_count = payload["training_receipt"]["foundation_public_rows"]
    learner.training_receipt = payload["training_receipt"]
    learner.begin_world()
    if learner.state_receipt() != payload["cold_state_sha256"]:
        raise ValueError("FKP17_CHECKPOINT_COLD_RECEIPT_MISMATCH")
    return learner

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import sys
from typing import Any

import torch


EVIDENCE_SCHEMA = "yggdrasil.dg1a.p0.run.v1"


def environment_fingerprint() -> dict[str, object]:
    device_name = None
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(torch.cuda.current_device())
    return {
        "python_version": sys.version.split()[0],
        "torch_version": torch.__version__,
        "platform": platform.platform(),
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_name": device_name,
    }


def file_sha256(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_evidence(
    path: str | os.PathLike[str],
    record: dict[str, Any],
) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    payload = dict(record)
    payload.setdefault("schema", EVIDENCE_SCHEMA)
    _assert_json_finite(payload)

    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, destination)
    return destination


def _assert_json_finite(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        if not torch.isfinite(torch.tensor(value)):
            raise ValueError(f"non-finite float at {path}")
        return
    if isinstance(value, dict):
        for key, child in value.items():
            _assert_json_finite(child, f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_json_finite(child, f"{path}[{index}]")

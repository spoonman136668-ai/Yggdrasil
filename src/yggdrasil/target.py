from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json

import torch
from torch import Tensor


@dataclass(frozen=True)
class TargetSpec:
    kind: str = "disk"
    radius: int = 6
    rgba: tuple[float, float, float, float] = (0.15, 0.75, 0.30, 1.0)

    def validate(self, *, height: int, width: int) -> None:
        if self.kind != "disk":
            raise ValueError(f"unsupported target kind: {self.kind}")
        if self.radius <= 0:
            raise ValueError("radius must be positive")
        if self.radius >= min(height, width) // 2:
            raise ValueError("radius must fit inside the configured grid")
        if len(self.rgba) != 4:
            raise ValueError("rgba must contain four values")
        if any(not 0.0 <= value <= 1.0 for value in self.rgba):
            raise ValueError("rgba values must be in [0, 1]")


def make_target(
    *,
    batch_size: int,
    channels: int,
    height: int,
    width: int,
    spec: TargetSpec | None = None,
    device: torch.device | str | None = None,
    dtype: torch.dtype = torch.float32,
) -> Tensor:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if channels < 4:
        raise ValueError("channels must be at least 4")
    if height <= 0 or width <= 0:
        raise ValueError("height and width must be positive")

    spec = spec or TargetSpec()
    spec.validate(height=height, width=width)

    target = torch.zeros((batch_size, channels, height, width), device=device, dtype=dtype)
    yy = torch.arange(height, device=device)[:, None]
    xx = torch.arange(width, device=device)[None, :]
    cy, cx = height // 2, width // 2
    mask = (yy - cy) ** 2 + (xx - cx) ** 2 <= spec.radius ** 2
    for channel, value in enumerate(spec.rgba):
        target[:, channel, mask] = value
    return target


def target_identity(spec: TargetSpec, *, height: int, width: int) -> str:
    spec.validate(height=height, width=width)
    payload = {
        "spec": asdict(spec),
        "height": height,
        "width": width,
        "schema": "yggdrasil.target.v1",
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

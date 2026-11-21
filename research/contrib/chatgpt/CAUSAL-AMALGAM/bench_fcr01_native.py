"""Reproducible FCR01-S development CPU comparison. No external source actions."""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha1
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from statistics import median
import json
import platform
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = next((p for p in (HERE, *HERE.parents)
             if (p / "yggdrasil" / "native_episode_experience.py").is_file()),
            HERE)  # exact-repo checkout or local authenticated source subset
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from yggdrasil.native_context_basis import digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience
PINNED_BLOBS = {
    "native_episode_experience.py": "5a18b00a4c4131526e71f51d63dfd9eb9471c81e",
    "public_causal_cells.py": "de8722f38d987ef7bcb4b7a0c23466b8e6f25712",
    "factorized_context_readout.py": "78641c1ea7de0781ae6da172eb8e2a213da7289e",
}
VIEWS = ((0, 0), (0, 1))


def blob_sha(path):
    data = path.read_bytes()
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def validate_pins():
    for name, expected in PINNED_BLOBS.items():
        path = HERE / name if name.startswith("factorized") else ROOT / "yggdrasil" / name
        actual = blob_sha(path)
        if actual != expected:
            raise RuntimeError(f"SOURCE_PIN_MISMATCH {name} {actual} != {expected}")


def row(i):
    return {"s1": 0, "x1": i & 1, "s2": (i >> 1) & 1,
            "x2": (i >> 2) & 1, "y": (i >> 3) & 1}


def admit(native, i):
    return native.observe(format(i + 1, "064x"), VIEWS, row(i))


def main():
    validate_pins()
    spec = spec_from_file_location("fcr01_benchmark", HERE / "factorized_context_readout.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    anchor = NativeEpisodeExperience()
    for i in range(1024):
        anchor = admit(anchor, i)
    anchor = anchor.begin_stream().enable_context_refresh().extend_witness_capacity()
    anchor_sha = digest(anchor.checkpoint())
    assert len(anchor._context_models) == 33
    measures = {"native": [], "factorized": []}
    final_hashes = set()
    sidecar_bytes = None
    for arm in ("native", "factorized"):
        for _ in range(3):
            native = anchor
            sidecar = module.FactorizedContextReadout(native) if arm == "factorized" else None
            started = time.process_time()
            for i in range(1024, 1120):
                event = row(i)
                if sidecar is None:
                    native.context_forecast(VIEWS[0], event["x1"])
                    native.context_forecast(VIEWS[0], event["x1"], event["s2"], event["x2"])
                else:
                    sidecar.transition(VIEWS[0], event["x1"])
                    sidecar.reward(VIEWS[0], event["x1"], event["s2"], event["x2"])
                descendant = admit(native, i)
                if sidecar is not None:
                    sidecar = sidecar.advance(descendant)
                native = descendant
            measures[arm].append(time.process_time() - started)
            final_hashes.add(digest(native.checkpoint()))
            if sidecar is not None:
                raw = sidecar.checkpoint()
                sidecar_bytes = len(raw)
                cold_native = NativeEpisodeExperience.restore(native.checkpoint(), digest(native.checkpoint()))
                cold_sidecar = module.FactorizedContextReadout.restore(cold_native, raw, digest(raw))
                if raw != cold_sidecar.checkpoint():
                    raise RuntimeError("FCR01_COLD_MISMATCH")
    if len(final_hashes) != 1 or digest(anchor.checkpoint()) != anchor_sha:
        raise RuntimeError("FCR01_NATIVE_CHECKPOINT_DRIFT")
    ratio = median(measures["factorized"]) / median(measures["native"])
    out = {
        "classification": "ENGINEERING_RESOURCE_NO_GO" if ratio > 2 else "DEV_RESOURCE_WITHIN_CEILING",
        "engineering_fixture_only": True, "scientific_pass": False, "accepted_native": False,
        "target_cpu_ratio_max": 2.0, "observed_median_cpu_ratio": round(ratio, 6),
        "cpu_seconds": {k: [round(x, 6) for x in v] for k, v in measures.items()},
        "repeat_count": 3, "existing_witnesses": 1024, "new_witnesses": 96,
        "context_experts": 33, "final_native_checkpoint_sha256": final_hashes.pop(),
        "original_native_checkpoint_unchanged": True,
        "cold_sidecar_parity": True, "sidecar_checkpoint_bytes": sidecar_bytes,
        "source_blobs": PINNED_BLOBS, "python": sys.version.split()[0], "platform": platform.platform(),
        "source_note": "Same source-free deterministic binary episode tape. No protected world actions. Local utility shim is NOT the full repository.",
        "ci_full_regression": "NOT_RUN", "cross_os": "NOT_RUN",
    }
    print(json.dumps(out, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

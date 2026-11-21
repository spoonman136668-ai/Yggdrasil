"""G39 original native-class cold parity from GitHub Actions' extracted artifacts.

Source archive references are fixed to run 44499793023; no source/world actions.
Only original source class restores can yield the success result.
"""
from pathlib import Path
import json
import sys
from tempfile import TemporaryDirectory
import subprocess

import native_segment_qualification as G39

JOINT_HASHES = {
    "linux": "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8",
    "windows": "65b22e284b94fe022fb6345757e364e1a44f8156edf7f081e1b7420e5561f454",
}


def original_from_unpacked(path, label):
    G39.require(label in JOINT_HASHES and isinstance(path, Path) and path.is_file(),
                "ORIGINAL_UNPACKED_ABSENT")
    raw = path.read_bytes()
    G39.require(G39.sha(raw) == JOINT_HASHES[label], "ORIGINAL_UNPACKED_PIN:" + label)
    document = json.loads(raw)
    G39.require(type(document) is dict and type(document.get("native_ascii")) is str,
                "ORIGINAL_UNPACKED_SCHEMA")
    native_raw = document["native_ascii"].encode("ascii")
    G39.require(G39.sha(native_raw) == G39.NATIVE_SHA, "ORIGINAL_NATIVE_PIN:" + label)
    episode_ascii = json.loads(native_raw)["experience_ascii"]
    G39.require(type(episode_ascii) is str, "ORIGINAL_EPISODE_TYPE")
    episode_raw = episode_ascii.encode("ascii")
    G39.require(G39.sha(episode_raw) == G39.EPISODE_SHA,
                "ORIGINAL_EPISODE_PIN:" + label)
    return native_raw, episode_raw


def qualify(linux_json, windows_json):
    G39.pin_sources()  # Exact source blob pin required before importing native classes.
    original_linux = original_from_unpacked(linux_json, "linux")
    original_windows = original_from_unpacked(windows_json, "windows")
    G39.require(original_linux == original_windows, "ORIGINAL_CROSS_OS_MISMATCH")
    native_raw, episode_raw = original_linux
    manifest, segments = G39.CODEC.seal(episode_raw)
    G39.require(G39.CODEC.restore(manifest, segments) == episode_raw,
                "CODEC_ORIGINAL_ROUNDTRIP")
    with TemporaryDirectory(prefix="g39-original-native-") as folder:
        root = Path(folder)
        (root / "manifest.json").write_bytes(manifest)
        (root / "native-raw.json").write_bytes(native_raw)
        for index, compressed in enumerate(segments):
            (root / f"{index:03d}.bin").write_bytes(compressed)
        parent = G39.original_native_readback(native_raw, episode_raw)
        children = []
        for _ in range(2):
            raw = subprocess.check_output(
                [sys.executable, "-B", str(Path(G39.__file__).resolve()),
                 "--child", str(root)], timeout=180)
            children.append(json.loads(raw))
        G39.require(parent == children[0] == children[1], "COLD_PROCESS_PARITY")
    return {
        "status": "G39_ORIGINAL_NATIVE_COLD_PARITY_PASS",
        "original_artifact_run": 44499793023,
        "original_joint_hashes": JOINT_HASHES,
        "native_source_blobs": G39.SOURCE_BLOBS,
        "original_native_sha256": parent["native_sha256"],
        "original_episode_sha256": parent["episode_sha256"],
        "model_experts": parent["expert_count"],
        "witnesses": parent["episode_count"],
        "public_view_plan_sha256": parent["plan_sha256"],
        "cold_child_count": len(children),
        "segments": len(segments),
        "scientific_gain_verified": False,
        "witness_capacity_extended": False,
        "protected_first_use": False,
    }


def main():
    G39.require(len(sys.argv) == 3, "ARGUMENT_SHAPE")
    print(json.dumps(qualify(Path(sys.argv[1]), Path(sys.argv[2])), sort_keys=True))


if __name__ == "__main__":
    main()

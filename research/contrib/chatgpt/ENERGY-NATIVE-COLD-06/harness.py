#!/usr/bin/env python3
"""ENERGY-NATIVE-COLD-06: native causal counter checkpoint/interference boundary.

Read-only import of accepted Yggdrasil PublicCausalCells. No new learner.
Run: python research/contrib/chatgpt/ENERGY-NATIVE-COLD-06/harness.py --out result.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.public_causal_cells import PublicCausalCells as Cells

NATIVE = ROOT / "yggdrasil" / "public_causal_cells.py"
EXPECTED_BLOB = "5c9a9904e31688bebc2e53723569e1fb988a981f"
SOURCE_MAIN = "5e74f8db85b2f5839c42148c0dfba69a88b1a2c9"


def source_blob() -> str:
    source = NATIVE.read_bytes()
    blob = b"blob " + str(len(source)).encode("ascii") + b"\x00" + source
    return hashlib.sha1(blob).hexdigest()


def readouts(cells: Cells) -> list[dict]:
    result = []
    for retained, n in ((False, 7), (True, 9)):
        for address in range(n):
            numerator = cells.observed_action_contrast(address, retained=retained)
            result.append({
                "retained": retained, "address": address,
                "choose": cells.choose(address, retained=retained),
                "wilson": cells.choose_wilson(address, retained=retained),
                "contrast": list(numerator) if numerator is not None else None,
            })
    return result


def expected_digest(rows: list[dict]) -> str:
    text = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def child(checkpoint: Path, expected: str) -> int:
    assert source_blob() == EXPECTED_BLOB, "native source drift"
    try:
        restored = Cells.restore(checkpoint.read_bytes())
    except ValueError as err:
        print(str(err), file=sys.stderr)
        return 2
    if expected == "REJECT":
        print("UNEXPECTED_CHECKPOINT_ACCEPT", file=sys.stderr)
        return 3
    expected_rows = json.loads(Path(expected).read_text(encoding="utf-8"))
    actual = readouts(restored)
    if actual != expected_rows or restored.snapshot() != checkpoint.read_bytes():
        print("COLD_FUNCTIONAL_READOUT_MISMATCH", file=sys.stderr)
        return 4
    print(json.dumps({
        "result": "FRESH_INTERPRETER_FUNCTIONAL_PASS",
        "native_blob": source_blob(),
        "checkpoint_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
        "readout_sha256": expected_digest(actual),
        "readouts": len(actual),
    }, sort_keys=True))
    return 0


def rejection_checks(cells: Cells) -> int:
    before = cells.snapshot()
    negative_calls = (
        lambda: cells.observe(0, 2, 1),
        lambda: cells.observe(0, 0, 2),
        lambda: cells.observe(7, 0, 1),
        lambda: cells.observe(0, 0, 1, retained=1),
    )
    rejected = 0
    for call in negative_calls:
        try:
            call()
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("invalid native input accepted")
    assert cells.snapshot() == before, "invalid input mutated checkpoint"
    return rejected


def main(out: Path) -> None:
    started = time.perf_counter()
    assert source_blob() == EXPECTED_BLOB, "exact native Git blob mismatch"
    c = Cells()
    assert c.choose(0) is None and c.choose_wilson(0) is None
    assert c.observed_action_contrast(0) is None
    for address in range(7):
        for _ in range(8):
            c.observe(address, 0, 1)
            c.observe(address, 1, 0)
    for address in range(8):
        preferred = address % 2
        for _ in range(12):
            c.observe(address, preferred, 1, retained=True)
            c.observe(address, 1-preferred, 0, retained=True)
    for action in (0, 1):
        for _ in range(12):
            c.observe(8, action, 1, retained=True)
            c.observe(8, action, 0, retained=True)
    rows_a = readouts(c)
    snap_a = c.snapshot()
    assert len(snap_a) == Cells.CHECKPOINT_BYTES == 164
    assert all(rows_a[i]["choose"] == 0 for i in range(7))
    assert all(rows_a[7+i]["choose"] == i % 2 for i in range(8))
    assert rows_a[-1]["choose"] is None
    assert rows_a[-1]["wilson"] is None
    assert rows_a[-1]["contrast"] == [0, 576]
    for address in range(7):
        for _ in range(64):
            c.observe(address, 0, 0)
            c.observe(address, 1, 1)
    rows_b = readouts(c)
    snap_b = c.snapshot()
    assert len(snap_b) == 164 and snap_b != snap_a
    active_flipped = sum(rows_a[i]["choose"] == 0 and rows_b[i]["choose"] == 1
                         for i in range(7))
    retained_unchanged = sum(rows_a[7+i] == rows_b[7+i] for i in range(9))
    assert active_flipped == 7, "active overwritten-readout control failed"
    assert retained_unchanged == 9, "historical retained readout changed"
    bad_inputs_rejected = rejection_checks(c)
    assert bad_inputs_rejected == 4
    with tempfile.TemporaryDirectory(prefix="ygg-native-cold-06-") as tmp:
        folder = Path(tmp)
        env = dict(os.environ, PYTHONPATH=str(ROOT))
        child_receipts = []
        for label, checkpoint, expected in (("A", snap_a, rows_a), ("B", snap_b, rows_b)):
            cp = folder / (label + ".bin")
            ref = folder / (label + ".json")
            cp.write_bytes(checkpoint)
            ref.write_text(json.dumps(expected), encoding="utf-8")
            cmd = [sys.executable, str(Path(__file__).resolve()),
                   "--child", str(cp), str(ref)]
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  env=env, cwd=ROOT, timeout=15, check=False)
            assert proc.returncode == 0, (label, proc.stderr, proc.stdout)
            receipt = json.loads(proc.stdout)
            assert receipt["checkpoint_sha256"] == hashlib.sha256(checkpoint).hexdigest()
            assert receipt["readout_sha256"] == expected_digest(expected)
            child_receipts.append(dict(phase=label, **receipt))
        corruptions = (
            bytes([snap_a[0] ^ 1]) + snap_a[1:],
            snap_a[:-1],
            snap_a[:8] + bytes([snap_a[8] ^ 1]) + snap_a[9:],
        )
        rejected_corrupt = 0
        for i, corruption in enumerate(corruptions):
            cp = folder / ("corrupt_" + str(i) + ".bin")
            cp.write_bytes(corruption)
            proc = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()),
                 "--child", str(cp), "REJECT"],
                capture_output=True, text=True, env=env, cwd=ROOT,
                timeout=15, check=False)
            assert proc.returncode == 2, (i, proc.returncode, proc.stdout, proc.stderr)
            assert proc.stderr.strip() == "PUBLIC_CAUSAL_CHECKPOINT_REJECTED"
            rejected_corrupt += 1
    assert rejected_corrupt == 3
    receipt = {
        "schema": "yggdrasil.external-research-native-boundary.v1",
        "experiment_id": "ENERGY-NATIVE-COLD-06",
        "source_free": True, "science_classification": "NOT_TESTED",
        "native_source_main": SOURCE_MAIN,
        "native_source_git_blob": source_blob(),
        "python": sys.version.split()[0], "os": platform.platform(),
        "snapshot_bytes": len(snap_a),
        "checkpoint_a_sha256": hashlib.sha256(snap_a).hexdigest(),
        "checkpoint_b_sha256": hashlib.sha256(snap_b).hexdigest(),
        "observed_active_preference_flip": active_flipped,
        "retained_full_readouts_unchanged": retained_unchanged,
        "independent_process_restores": len(child_receipts),
        "independent_process_receipts": child_receipts,
        "corrupt_checkpoints_rejected": rejected_corrupt,
        "invalid_inputs_rejected_without_mutation": bad_inputs_rejected,
        "null_retained_address_abstains": True,
        "elapsed_wall_seconds": time.perf_counter() - started,
        "engineering": "PASS", "scientific_gain_verified": False,
        "deployment": "NONE",
        "interpretation": "Conventional fixed-address counters preserve nine protected slots; seven overwritten active preferences reveal historical interference, not novel causal reasoning or cumulative old-context retention.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print("ENERGY_NATIVE_COLD06_ENGINEERING_PASS " + json.dumps({
        "active_flipped": active_flipped,
        "retained_unchanged": retained_unchanged,
        "new_process_restores": len(child_receipts),
        "corrupted_rejected": rejected_corrupt,
        "invalid_rejected": bad_inputs_rejected,
    }, sort_keys=True))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    ap.add_argument("--child", nargs=2)
    args = ap.parse_args()
    if args.child:
        sys.exit(child(Path(args.child[0]), args.child[1]))
    if args.out is None:
        ap.error("parent requires --out")
    main(args.out)

"""NCI-04L5A: native Yggdrasil cold-process continuity, engineering-only.

This test uses *caller-provided* own-next bits from the existing G6 fixture.
It does not authenticate an external sensor or confer scientific admission.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yggdrasil.nci04g6_native_credit import NativeSurvivorCredit
from yggdrasil.task_runtime import LocalTaskRuntime

MODE_KEY = "NCI04L5A_Y_COLD_MODE"
SNAPSHOT_KEY = "NCI04L5A_Y_COLD_SNAPSHOT"
REPORT_KEY = "NCI04L5A_Y_COLD_REPORT="


def new_runtime():
    runtime = LocalTaskRuntime()
    for n in range(6):
        bits = [((n + i) % 2) for i in range(8)]
        outcomes = [bits[(i + 1) % 8] for i in range(8)]
        runtime.observe(bits, outcomes)
    runtime.lesion([0])
    return runtime


def child_main():
    mode, destination = os.environ[MODE_KEY], Path(os.environ[SNAPSHOT_KEY])
    if mode not in ("full", "prefix", "resume"):
        raise RuntimeError("invalid cold-process mode")
    if mode == "resume":
        runtime = LocalTaskRuntime.restore(destination.read_text(encoding="utf-8"))
    else:
        runtime = new_runtime()
    credit = NativeSurvivorCredit(runtime)
    if mode in ("full", "prefix"):
        credit.observe_own_transition(0, 7, (0, 1, 0), 1, 1)
    if mode in ("full", "resume"):
        credit.observe_own_transition(0, 7, (1, 0, 1), 0, 2)
    state = runtime.snapshot()
    if mode == "prefix":
        fd, name = tempfile.mkstemp(prefix=".nci04l5a-", dir=destination.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(state)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, destination)
        finally:
            if os.path.exists(name):
                os.unlink(name)
    report = {
        "checkpoint_sha256": hashlib.sha256(state.encode("utf-8")).hexdigest(),
        "prediction": credit.predict_survivor(7, (1, 0, 1)),
        "events": runtime.core.events,
        "steps": runtime.steps,
        "source_attestation": "UNVERIFIED_CALLER_OWN_NEXT_BIT",
        "scientific_first_use": False,
    }
    print(REPORT_KEY + json.dumps(report, sort_keys=True))


class TestNCI04G6ColdProcess(unittest.TestCase):
    def test_cold_process_prefix_resume_matches_uninterrupted(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot = str(Path(folder) / "prefix.snapshot")

            def run(mode):
                env = dict(os.environ)
                env[MODE_KEY] = mode
                env[SNAPSHOT_KEY] = snapshot
                completed = subprocess.run(
                    [sys.executable, "-B", str(Path(__file__).resolve())],
                    env=env, capture_output=True, text=True, timeout=45, check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                matches = [line[len(REPORT_KEY):] for line in completed.stdout.splitlines()
                           if line.startswith(REPORT_KEY)]
                self.assertEqual(len(matches), 1, completed.stdout)
                return json.loads(matches[0])

            full = run("full")
            prefix = run("prefix")
            self.assertEqual(prefix["events"], 7)
            continued = run("resume")
            self.assertEqual(full, continued)
            self.assertEqual(continued["events"], 8)
            self.assertEqual(continued["source_attestation"], "UNVERIFIED_CALLER_OWN_NEXT_BIT")
            print("NCI04L5A_YGGDRASIL_COLD_PROCESS_FIXTURE_PASS=" +
                  json.dumps(continued, sort_keys=True))


if __name__ == "__main__":
    if MODE_KEY in os.environ:
        child_main()
    else:
        unittest.main()
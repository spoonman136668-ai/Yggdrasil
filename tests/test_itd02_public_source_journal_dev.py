"""Source-FREE fault-injection tests of durable source-action custody.

Never import the original published POMDP or reset/step it here.
The author-built source fixture is a plumbing test only, not science.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from yggdrasil.itd02_public_source_journal_dev import (
    JournaledPublicSourceDev, SourceCustodyDenied, inspect_custody,
    load_verified_native_model,
)
from yggdrasil.itd02_native_training_session_dev import NativeTrainingSessionDev

IDENTITY = "a69baec2d6e83e239bafa4c6b74faead794e7c91400bf69c7d3813ed114cea94"
ROLE = "OWNER_PUBLIC_FIT_DEVELOPMENT_ONLY"


class SourceFreePublicFixture:
    def __init__(self, *, steps=2, fail_step=False, fail_reset=False,
                 lie=False, truncate=True):
        self.resets = 0
        self.steps = 0
        self.limit = steps
        self.fail_step = fail_step
        self.fail_reset = fail_reset
        self.lie = lie
        self.truncate = truncate
        self.actions = []

    def reset_public(self):
        self.resets += 1
        if self.fail_reset:
            raise ConnectionError("source reset may have occurred")
        return "docked_MRV"

    def step_public(self, action):
        self.steps += 1
        self.actions.append(action)
        if self.fail_step:
            raise ConnectionError("source step may have occurred")
        if self.lie:
            return ("Nothing", 0, True, True)
        return ("Nothing", 0, False,
                self.truncate and self.steps >= self.limit)


def source(root, fixture, *, limit=2):
    return JournaledPublicSourceDev(
        root, fixture, episode_id="source-free-fixture-1",
        source_sha256=IDENTITY, max_steps=limit, role=ROLE)


class PublicSourceJournalTests(unittest.TestCase):
    def test_exact_native_learner_action_and_durable_cold_commit(self):
        with tempfile.TemporaryDirectory() as temp:
            f = SourceFreePublicFixture()
            with source(temp, f) as custody:
                result = custody.execute_one(NativeTrainingSessionDev(max_steps=2))
                self.assertEqual(result["steps"], 2)
                self.assertFalse(result["terminal"])
                self.assertTrue(result["truncated"])
                self.assertEqual(result["custody"]["status"], "COMMITTED")
                self.assertEqual(result["custody"]["steps"], 2)
                self.assertEqual(len(f.actions), 2)
                self.assertEqual(f.resets, 1)
                self.assertTrue((Path(temp) / "learned-checkpoint.bin").is_file())
                with self.assertRaisesRegex(SourceCustodyDenied, "STEP_NOT_ELIGIBLE"):
                    custody.step_public("GoForward")
            cold = inspect_custody(temp, expected_source_sha256=IDENTITY)
            self.assertEqual(cold["status"], "COMMITTED")
            self.assertTrue(cold["checkpoint_verified"])
            self.assertEqual(cold["episode"], "source-free-fixture-1")
            # An existing episode cannot be silently replayed, even by a
            # newly constructed owner process.
            with self.assertRaises(FileExistsError):
                source(temp, f)
            # Public-only journal: never serializes hidden state/seed.
            raw = (Path(temp) / "public-events.jsonl").read_bytes()
            self.assertNotIn(b"hidden", raw)
            self.assertNotIn(b"seed", raw)
            self.assertIn(b"step_intent", raw)
            self.assertIn(b"checkpoint_result", raw)

    def test_native_learned_state_cold_restores_and_trains_again(self):
        # Two source-FREE independent owner episodes with distinct durable
        # journals; no model-writing agent between native learning episodes.
        with tempfile.TemporaryDirectory() as temp:
            first_dir = Path(temp) / "first"
            second_dir = Path(temp) / "second"
            learner = NativeTrainingSessionDev(max_steps=2)
            with source(first_dir, SourceFreePublicFixture()) as first:
                result1 = first.execute_one(learner)
            cold = load_verified_native_model(
                first_dir, expected_source_sha256=IDENTITY)
            self.assertEqual(cold.model_identities(),
                             learner.model.model_identities())
            # Provenance/custody can be verified from a different Python
            # process without replaying any source interaction.
            check = subprocess.run([
                sys.executable, "-B", "-c",
                "import json,sys;from yggdrasil.itd02_public_source_journal_dev "
                "import inspect_custody; print(json.dumps(inspect_custody(sys.argv[1])))",
                str(first_dir)], text=True, capture_output=True, check=True)
            self.assertEqual(json.loads(check.stdout)["status"], "COMMITTED")
            with source(second_dir, SourceFreePublicFixture()) as second:
                result2 = second.execute_one(
                    NativeTrainingSessionDev(model=cold, max_steps=2))
            self.assertEqual(result2["transitions"],
                             result1["transitions"] + 2)
            self.assertEqual(result2["custody"]["status"], "COMMITTED")
            self.assertNotEqual(result1["custody"]["head"],
                                result2["custody"]["head"])

    def test_quarantined_source_cannot_cold_restore_native_state(self):
        with tempfile.TemporaryDirectory() as temp:
            with source(temp, SourceFreePublicFixture(fail_step=True)) as custody:
                with self.assertRaises(ConnectionError):
                    custody.execute_one(NativeTrainingSessionDev(max_steps=2))
            with self.assertRaisesRegex(SourceCustodyDenied,
                                        "COLD_RESTORE_NOT_COMMITTED"):
                load_verified_native_model(
                    temp, expected_source_sha256=IDENTITY)

    def test_unknown_step_is_durably_quarantined_and_not_reissued(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = SourceFreePublicFixture(fail_step=True)
            with source(temp, fixture) as custody:
                with self.assertRaises(ConnectionError):
                    custody.execute_one(NativeTrainingSessionDev(max_steps=2))
                self.assertTrue(custody.blocked)
                with self.assertRaises(SourceCustodyDenied):
                    custody.step_public("GoForward")
                self.assertEqual(len(fixture.actions), 1)
            self.assertEqual(inspect_custody(temp)["status"], "QUARANTINE")
            with self.assertRaises(FileExistsError):
                source(temp, fixture)
            self.assertEqual(len(fixture.actions), 1)

    def test_reset_error_refuses_second_reset(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = SourceFreePublicFixture(fail_reset=True)
            with source(temp, fixture) as custody:
                with self.assertRaises(ConnectionError):
                    custody.execute_one(NativeTrainingSessionDev(max_steps=2))
                with self.assertRaises(SourceCustodyDenied):
                    custody.reset_public()
            self.assertEqual(fixture.resets, 1)
            self.assertEqual(inspect_custody(temp)["status"], "QUARANTINE")

    def test_illegal_benchmark_end_is_not_committed(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = SourceFreePublicFixture(lie=True)
            with source(temp, fixture) as custody:
                with self.assertRaisesRegex(SourceCustodyDenied,
                                            "SOURCE_OUTCOME_PUBLIC_FIELDS"):
                    custody.execute_one(NativeTrainingSessionDev(max_steps=2))
            self.assertEqual(fixture.steps, 1)
            self.assertEqual(inspect_custody(temp)["status"], "QUARANTINE")

    def test_budget_exhaustion_without_source_end_is_not_success(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = SourceFreePublicFixture(truncate=False)
            with source(temp, fixture) as custody:
                with self.assertRaisesRegex(ValueError, "NO_SOURCE_TERMINAL"):
                    custody.execute_one(NativeTrainingSessionDev(max_steps=2))
            check = inspect_custody(temp)
            self.assertEqual(check["status"], "QUARANTINE")
            self.assertEqual(check["steps"], 2)
            self.assertFalse((Path(temp) / "learned-checkpoint.bin").exists())

    def test_checkpoint_unknown_write_quarantines_and_never_replays(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = SourceFreePublicFixture()
            with source(temp, fixture) as custody:
                with patch(
                    "yggdrasil.itd02_public_source_journal_dev._atomic_checkpoint",
                    side_effect=OSError("disk may have written checkpoint"),
                ):
                    with self.assertRaises(OSError):
                        custody.execute_one(NativeTrainingSessionDev(max_steps=2))
                self.assertEqual(custody.state, "checkpoint_intent")
                self.assertTrue(custody.blocked)
            self.assertEqual(inspect_custody(temp)["status"], "QUARANTINE")
            self.assertEqual(fixture.steps, 2)

    def test_chain_tampering_or_partial_append_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = SourceFreePublicFixture()
            with source(temp, fixture) as custody:
                custody.execute_one(NativeTrainingSessionDev(max_steps=2))
            journal = Path(temp) / "public-events.jsonl"
            raw = journal.read_bytes()
            journal.write_bytes(raw.replace(b"source-free-fixture-1", b"source-free-fixture-2", 1))
            with self.assertRaises(SourceCustodyDenied):
                inspect_custody(temp)
            journal.write_bytes(raw[:-1])
            with self.assertRaisesRegex(SourceCustodyDenied, "TORN_EVENT_STREAM"):
                inspect_custody(temp)

    def test_checkpoint_digest_and_source_identity_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            with source(temp, SourceFreePublicFixture()) as custody:
                custody.execute_one(NativeTrainingSessionDev(max_steps=2))
            with self.assertRaisesRegex(SourceCustodyDenied, "SOURCE_IDENTITY_CHANGED"):
                inspect_custody(temp, expected_source_sha256="f" * 64)
            path = Path(temp) / "learned-checkpoint.bin"
            path.write_bytes(path.read_bytes() + b"tamper")
            with self.assertRaisesRegex(SourceCustodyDenied, "CHECKPOINT_INTEGRITY"):
                inspect_custody(temp)

    def test_real_process_exit_after_source_step_intent_cold_quarantines(self):
        # A separate Python process exits while applying a SOURCE-FREE toy
        # action, without unwinding or calling any cleanup code. The parent
        # proves the intent was already durable and no action was replayed.
        with tempfile.TemporaryDirectory() as temp:
            child = """
import os,sys
from yggdrasil.itd02_public_source_journal_dev import JournaledPublicSourceDev
from yggdrasil.itd02_native_training_session_dev import NativeTrainingSessionDev
class CrashAfterIntent:
    def reset_public(self):
        return 'docked_MRV'
    def step_public(self, action):
        os._exit(71)
with JournaledPublicSourceDev(
    sys.argv[1], CrashAfterIntent(), episode_id='child-crash-after-intent',
    source_sha256=sys.argv[2], max_steps=2,
    role='OWNER_PUBLIC_FIT_DEVELOPMENT_ONLY',
) as owner:
    owner.execute_one(NativeTrainingSessionDev(max_steps=2))
raise AssertionError('source crash not reached')
"""
            done = subprocess.run(
                [sys.executable, "-B", "-c", child, temp, IDENTITY],
                capture_output=True, text=True, timeout=15)
            self.assertEqual(done.returncode, 71, done.stderr)
            cold = inspect_custody(temp, expected_source_sha256=IDENTITY)
            self.assertEqual(cold["status"], "QUARANTINE")
            self.assertEqual(cold["steps"], 0)
            journal = (Path(temp) / "public-events.jsonl").read_text("ascii")
            self.assertIn('"kind":"step_intent"', journal)
            self.assertNotIn('"kind":"step_result"', journal)
            self.assertFalse((Path(temp) / "learned-checkpoint.bin").exists())
            with self.assertRaises(FileExistsError):
                source(temp, SourceFreePublicFixture())

    def test_real_process_exit_after_checkpoint_intent_cold_quarantines(self):
        # Source-FREE end-of-episode process crash after checkpoint INTENT,
        # before final journal commit. This isn't a power-loss durability test.
        with tempfile.TemporaryDirectory() as temp:
            child = """
import os,sys
import yggdrasil.itd02_public_source_journal_dev as j
from yggdrasil.itd02_native_training_session_dev import NativeTrainingSessionDev
class FinishedToySource:
    def reset_public(self):
        return 'docked_MRV'
    def step_public(self, action):
        return ('Nothing', 0, False, True)
def die_before_checkpoint(directory, payload):
    os._exit(72)
j._atomic_checkpoint = die_before_checkpoint
with j.JournaledPublicSourceDev(
    sys.argv[1], FinishedToySource(), episode_id='child-crash-before-checkpoint',
    source_sha256=sys.argv[2], max_steps=1,
    role='OWNER_PUBLIC_FIT_DEVELOPMENT_ONLY',
) as owner:
    owner.execute_one(NativeTrainingSessionDev(max_steps=1))
raise AssertionError('checkpoint crash not reached')
"""
            done = subprocess.run(
                [sys.executable, "-B", "-c", child, temp, IDENTITY],
                capture_output=True, text=True, timeout=15)
            self.assertEqual(done.returncode, 72, done.stderr)
            cold = inspect_custody(temp, expected_source_sha256=IDENTITY)
            self.assertEqual(cold["status"], "QUARANTINE")
            self.assertEqual(cold["steps"], 1)
            self.assertFalse(cold["checkpoint_verified"])
            raw = (Path(temp) / "public-events.jsonl").read_text("ascii")
            self.assertIn('"kind":"checkpoint_intent"', raw)
            self.assertNotIn('"kind":"checkpoint_result"', raw)
            with self.assertRaisesRegex(
                SourceCustodyDenied, "COLD_RESTORE_NOT_COMMITTED"):
                load_verified_native_model(
                    temp, expected_source_sha256=IDENTITY)

    def test_source_owner_role_and_session_ceiling_required(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(SourceCustodyDenied, "NO_PUBLIC_FIT_OWNER_ROLE"):
                JournaledPublicSourceDev(
                    temp, SourceFreePublicFixture(), episode_id="1",
                    source_sha256=IDENTITY, max_steps=2, role="HOLDOUT")
            with source(temp, SourceFreePublicFixture(), limit=2) as custody:
                with self.assertRaisesRegex(SourceCustodyDenied,
                                            "SESSION_SHORTER_THAN_OWNER"):
                    custody.execute_one(NativeTrainingSessionDev(max_steps=1))
            self.assertEqual(inspect_custody(temp)["status"], "QUARANTINE")


if __name__ == "__main__":
    unittest.main()

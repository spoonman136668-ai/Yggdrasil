"""Engineering-only source-free qualification of unattended native episodes."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from yggdrasil.itd02_native_public_cohort_dev import (
    SourceCustodyDenied, train_or_resume_public_cohort,
)

SOURCE = "a69baec2d6e83e239bafa4c6b74faead794e7c91400bf69c7d3813ed114cea94"


class PublicSourceFixture:
    """No published source data; a synthetic consequence used for contracts."""
    def __init__(self, index, *, fail_step=False, bad_role=False,
                 wrong_source=False):
        self.index = index
        self.actions = []
        self.resets = 0
        self.fail_step = fail_step
        self.bad_role = bad_role
        self.wrong_source = wrong_source

    @property
    def source_receipt(self):
        return {
            "source_sha256": "0" * 64 if self.wrong_source else SOURCE,
            "role": ("HOLDOUT" if self.bad_role else
                     "PUBLIC_FIT_ONLY_NOT_INDEPENDENT_SCIENCE"),
            "protected_first_use": False,
        }

    def reset_public(self):
        self.resets += 1
        return "docked_MRV"

    def step_public(self, action):
        self.actions.append(action)
        if self.fail_step:
            raise ConnectionError("source effect may have occurred")
        return "Nothing", 0, False, len(self.actions) == 2


class NativeCohortTests(unittest.TestCase):
    def test_native_runs_multiple_episodes_and_cold_skips_all_on_reentry(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "native-cohort"
            created = []
            def factory(index):
                f = PublicSourceFixture(index)
                created.append(f)
                return f
            out = train_or_resume_public_cohort(
                root, factory, source_sha256=SOURCE, episodes=3, max_steps=2)
            self.assertEqual(out["completed_episodes"], 3)
            self.assertEqual(out["total_public_actions"], 6)
            self.assertEqual(out["past_episodes_skipped_without_replay"], 0)
            self.assertEqual(len(created), 3)
            self.assertTrue(all(len(f.actions) == 2 and f.resets == 1
                                for f in created))
            self.assertEqual(len(set(
                x["head"] for x in out["receipts"])), 3)
            self.assertEqual(out["assessment"],
                             "SOURCE_FREE_ENGINEERING_NOT_SCIENCE")
            self.assertTrue(all(x["parent_process_cpu_ns"] >= 0 and
                                x["wall_ns"] > 0 and
                                x["journal_checkpoint_bytes"] > 0
                                for x in out["receipts"]))
            def should_never_replay(_):
                self.fail("cold re-entry must not consume or reset source")
            cold = train_or_resume_public_cohort(
                root, should_never_replay, source_sha256=SOURCE,
                episodes=3, max_steps=2)
            self.assertEqual(cold["past_episodes_skipped_without_replay"], 3)
            self.assertEqual(cold["native_model_identities"],
                             out["native_model_identities"])
            script = (
                "import json,sys; from "
                "yggdrasil.itd02_native_public_cohort_dev "
                "import train_or_resume_public_cohort;"
                "def_forbidden=lambda _: (_ for _ in ()).throw("
                "RuntimeError('REPLAY_FORBIDDEN'));"
                "r=train_or_resume_public_cohort(sys.argv[1],def_forbidden,"
                "source_sha256=sys.argv[2],episodes=3,max_steps=2);"
                "print(json.dumps({'skip':r['past_episodes_skipped_without_replay'],"
                "'moves':r['total_public_actions']}))")
            proc = subprocess.run(
                [sys.executable, "-B", "-c", script, str(root), SOURCE],
                capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(proc.stdout),
                             {"skip": 3, "moves": 6})

    def test_ambiguous_step_never_replays_even_after_new_process(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "cohort"
            sources = []
            def factory(i):
                s = PublicSourceFixture(i, fail_step=(i == 2))
                sources.append(s)
                return s
            with self.assertRaises(ConnectionError):
                train_or_resume_public_cohort(
                    root, factory, source_sha256=SOURCE,
                    episodes=3, max_steps=2)
            self.assertEqual([len(x.actions) for x in sources], [2, 1])
            with self.assertRaises(SourceCustodyDenied):
                train_or_resume_public_cohort(
                    root, lambda _: self.fail("must not invoke"),
                    source_sha256=SOURCE, episodes=3, max_steps=2)
            self.assertEqual(len(sources), 2)
            self.assertTrue((root / "episode-000002/public-events.jsonl").exists())

    def test_ambiguous_factory_leaves_reserved_no_replay_gap(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "cohort"
            def source_factory(i):
                if i == 2:
                    raise ConnectionError("source factory may have side effect")
                return PublicSourceFixture(i)
            with self.assertRaises(ConnectionError):
                train_or_resume_public_cohort(
                    root, source_factory, source_sha256=SOURCE,
                    episodes=2, max_steps=2)
            self.assertTrue((root / "episode-000002").is_dir())
            with self.assertRaises(SourceCustodyDenied):
                train_or_resume_public_cohort(
                    root, lambda _: self.fail("replay"),
                    source_sha256=SOURCE, episodes=2, max_steps=2)

    def test_self_asserted_bad_source_identity_and_role_refused(self):
        for flags in ({"wrong_source": True}, {"bad_role": True}):
            with self.subTest(flags=flags):
                with tempfile.TemporaryDirectory() as temp:
                    source = PublicSourceFixture(1, **flags)
                    with self.assertRaises(SourceCustodyDenied):
                        train_or_resume_public_cohort(
                            Path(temp) / "cohort", lambda _: source,
                            source_sha256=SOURCE, episodes=1, max_steps=2)
                    self.assertEqual(source.resets, 0)
                    self.assertEqual(source.actions, [])

    def test_changed_budget_and_source_never_replay(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "cohort"
            train_or_resume_public_cohort(
                root, lambda i: PublicSourceFixture(i),
                source_sha256=SOURCE, episodes=1, max_steps=2)
            with self.assertRaisesRegex(SourceCustodyDenied,
                                        "COHORT_MANIFEST_IDENTITY_DRIFT"):
                train_or_resume_public_cohort(
                    root, lambda _: self.fail("replay"),
                    source_sha256=SOURCE, episodes=2, max_steps=2)
            with self.assertRaises(SourceCustodyDenied):
                train_or_resume_public_cohort(
                    root, lambda _: self.fail("replay"),
                    source_sha256="f" * 64, episodes=1, max_steps=2)

    def test_tampered_journal_and_unexpected_path_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "cohort"
            train_or_resume_public_cohort(
                root, lambda i: PublicSourceFixture(i),
                source_sha256=SOURCE, episodes=1, max_steps=2)
            journal = root / "episode-000001/public-events.jsonl"
            journal.write_bytes(journal.read_bytes()[:-1])
            with self.assertRaises(SourceCustodyDenied):
                train_or_resume_public_cohort(
                    root, lambda _: self.fail("replay"),
                    source_sha256=SOURCE, episodes=1, max_steps=2)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "cohort"
            train_or_resume_public_cohort(
                root, lambda i: PublicSourceFixture(i),
                source_sha256=SOURCE, episodes=1, max_steps=2)
            (root / "episode-000003").mkdir()
            with self.assertRaisesRegex(SourceCustodyDenied,
                                        "EPISODE_CHAIN_GAP_OR_BUDGET"):
                train_or_resume_public_cohort(
                    root, lambda _: self.fail("replay"),
                    source_sha256=SOURCE, episodes=1, max_steps=2)


if __name__ == "__main__":
    unittest.main()

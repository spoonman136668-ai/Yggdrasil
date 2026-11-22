"""CAID-05: primary native-engineering interface and source-free negative tests.

The ``test_native_*`` cases require the exact pinned Yggdrasil checkout.
The ``test_pure_*`` cases exercise only the deterministic ledger summarizer.
No protected original-world actor or outside data is used.
"""
import hashlib
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).with_name("native_history_support.py")
spec = importlib.util.spec_from_file_location("caid05_native_support", SCRIPT)
readout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readout)
PublicHistorySupport = readout.PublicHistorySupport


def public_event(i, *, second_action=None, outcome=None):
    c, nuisance, first = (i >> 1) & 1, i & 1, (i >> 2) & 1
    state = c ^ first
    x2 = (i >> 3) & 1 if second_action is None else second_action
    y = c ^ state ^ x2 if outcome is None else outcome
    identifier = hashlib.sha256(f"caid05-engineering-public-{i}".encode()).hexdigest()
    return (identifier, ((c, nuisance), (c, 1 - nuisance)), first, state, x2, y)


def pure_history(n=24, **kwargs):
    return tuple(public_event(i, **kwargs) for i in range(n))


def actual_native(n=24):
    from yggdrasil.native_episode_experience import NativeEpisodeExperience
    model = NativeEpisodeExperience(repair=False)
    for event in pure_history(n):
        identifier, views, first, state, second, reward = event
        row = {"s1": views[0][0], "x1": first, "s2": state,
               "x2": second, "y": reward}
        frozen = model.checkpoint()
        candidate = model.observe(identifier, views, row)
        if model.checkpoint() != frozen:
            raise AssertionError("CAID05_NATIVE_PARENT_MUTATED")
        model = candidate
    return model


class Caid05SourceFreeTests(unittest.TestCase):
    def test_pure_exact_statistics_match_full_observation_counts(self):
        ledger = pure_history()
        model = PublicHistorySupport(ledger, 0, source_checkpoint_sha256="a" * 64)
        for c in (0, 1):
            for x1 in (0, 1):
                rows = [e for e in ledger if e[1][0][0] == c and e[2] == x1]
                if rows:
                    result = model.transition((c, 0), x1)
                    self.assertEqual(result, (1 + sum(e[3] for e in rows), 2 + len(rows)))
                for state in (0, 1):
                    for action in (0, 1):
                        matches = [e for e in rows if e[3] == state and e[4] == action]
                        found = model.reward((c, 1), x1, state, action)
                        expected = ((1 + sum(e[5] for e in matches), 2 + len(matches))
                                    if matches else None)
                        self.assertEqual(found, expected)

    def test_pure_learned_projection_ignores_nuisance_view_bit(self):
        model = PublicHistorySupport(pure_history(), 0, source_checkpoint_sha256="a" * 64)
        for c in (0, 1):
            for first in (0, 1):
                for state in (0, 1):
                    for second in (0, 1):
                        self.assertEqual(model.reward((c, 0), first, state, second),
                                         model.reward((c, 1), first, state, second))
        self.assertEqual(model.ambiguous, 0)

    def test_pure_missing_action_evidence_abstains(self):
        model = PublicHistorySupport(pure_history(second_action=0), 0,
                                     source_checkpoint_sha256="a" * 64)
        self.assertTrue(all(model.reward((c, 0), x1, c ^ x1, 1) is None
                            for c in (0, 1) for x1 in (0, 1)))
        self.assertEqual(model.document()["causal_graph_identified"], False)
        self.assertEqual(model.document()["can_act"], False)

    def test_pure_context_conflict_is_excluded_not_guessed(self):
        rows = list(pure_history())
        identifier, views, x1, state, x2, reward = rows[-1]
        rows[-1] = (identifier, (views[0], (1 - views[0][0], views[1][1])),
                    x1, state, x2, reward)
        obj = PublicHistorySupport(tuple(rows), 0,
                                   source_checkpoint_sha256="a" * 64)
        self.assertEqual(obj.ambiguous, 1)
        self.assertEqual(obj.observed, 24)
        self.assertEqual(sum(a + b for a, b in obj._reward.values()), 23)

    def test_pure_stochastic_outcomes_are_counts_not_deterministic_facts(self):
        rows = []
        for i in range(16):
            r = public_event(i, second_action=0, outcome=i & 1)
            rows.append((r[0], ((0, 0), (0, 1)), 0, 0, 0, r[-1]))
        model = PublicHistorySupport(tuple(rows), 0,
                                     source_checkpoint_sha256="a" * 64)
        self.assertEqual(model.reward((0, 0), 0, 0, 0), (9, 18))
        self.assertIsNone(model.reward((0, 0), 0, 0, 1))
        self.assertFalse(model.document()["scientific_pass"])

    def test_pure_replayed_identifier_is_rejected(self):
        rows = list(pure_history())
        rows[-1] = rows[0]
        with self.assertRaisesRegex(ValueError, "DUPLICATE_WITNESS_ID"):
            PublicHistorySupport(tuple(rows), 0, source_checkpoint_sha256="a" * 64)

    def test_pure_projection_unknown_abstains(self):
        with self.assertRaisesRegex(ValueError, "PROJECTION_NOT_LEARNED"):
            PublicHistorySupport(pure_history(), None, source_checkpoint_sha256="a" * 64)
        with self.assertRaisesRegex(ValueError, "PROJECTION_NOT_LEARNED"):
            PublicHistorySupport(pure_history(), True, source_checkpoint_sha256="a" * 64)

    def test_pure_checkpoint_pin_and_public_type_are_strict(self):
        with self.assertRaisesRegex(ValueError, "CHECKPOINT_PIN"):
            PublicHistorySupport(pure_history(), 0, source_checkpoint_sha256="garbage")
        model = PublicHistorySupport(pure_history(), 0, source_checkpoint_sha256="a" * 64)
        with self.assertRaises(ValueError):
            model.reward((0, True), 0, 0, 0)
        self.assertEqual(model.fingerprint, model.fingerprint)

    def test_native_source_blob_is_exactly_the_pinned_architecture(self):
        root = Path(__file__).resolve().parents[5]
        pins = {
            "yggdrasil/native_episode_experience.py":
                "5a18b00a4c4131526e71f51d63dfd9eb9471c81e",
            "yggdrasil/native_cumulative_learner.py":
                "1bdeaa4277fc9b34bbf7c0f36c6d0a4cc00e1ca4",
        }
        for path, expected in pins.items():
            raw = (root / path).read_bytes()
            actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            self.assertEqual(actual, expected, path)

    def test_native_real_reader_checkpoint_immutable_and_same_counts(self):
        native = actual_native(24)
        self.assertEqual(native._projection, 0)
        raw = native.checkpoint()
        expected = hashlib.sha256(raw).hexdigest()
        read = PublicHistorySupport.from_native(native, expected)
        pure = PublicHistorySupport(native._ledger, native._projection,
                                    source_checkpoint_sha256=expected)
        self.assertEqual(read.fingerprint, pure.fingerprint)
        self.assertEqual(native.checkpoint(), raw)
        self.assertEqual(read.document()["native_accepted"], False)
        self.assertEqual(read.document()["original_world_first_use"], False)

    def test_native_cold_restart_works_with_unmutated_native_checkpoint(self):
        from yggdrasil.native_episode_experience import NativeEpisodeExperience
        native = actual_native(24)
        raw = native.checkpoint()
        checkpoint_sha = hashlib.sha256(raw).hexdigest()
        restored = NativeEpisodeExperience.restore(raw, checkpoint_sha)
        self.assertEqual(restored.checkpoint(), raw)
        before = PublicHistorySupport.from_native(native, checkpoint_sha)
        after = PublicHistorySupport.from_native(restored, checkpoint_sha)
        self.assertEqual(before.fingerprint, after.fingerprint)
        for c in (0, 1):
            for first in (0, 1):
                for state in (0, 1):
                    for action in (0, 1):
                        self.assertEqual(before.reward((c, 0), first, state, action),
                                         after.reward((c, 0), first, state, action))

    def test_native_rejects_wrong_reader_pin_and_unsupported_growth(self):
        from yggdrasil.native_episode_experience import (
            MAX_EPISODES, GROWN_MAX_EPISODES, NativeEpisodeExperience,
        )
        self.assertEqual((MAX_EPISODES, GROWN_MAX_EPISODES), (1024, 1152))
        native = actual_native(8)
        with self.assertRaisesRegex(ValueError, "CHECKPOINT_MISMATCH"):
            PublicHistorySupport.from_native(native, "0" * 64)
        with self.assertRaisesRegex(ValueError, "GROWTH_PARENT"):
            native.extend_witness_capacity()
        with self.assertRaises(TypeError):
            PublicHistorySupport.from_native(object(), "a" * 64)


if __name__ == "__main__":
    unittest.main(verbosity=2)

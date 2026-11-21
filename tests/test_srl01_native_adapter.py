"""SRL01 source-free native checkpoint/adapter contract, opt-in branch only.

Uses the historically consumed CKAD25 development checkpoint read-only. The
new 12 source effects and six history effects are deterministic source-free
engineering fixtures; NOT original-world first-use or a scientific trial.
No target/held labels or private data are supplied to the selector.
"""
import hashlib
import itertools
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import canonical, digest, feature_row
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from yggdrasil.native_shared_fault_risk import NativeSharedFaultRisk

ROOT = Path(__file__).resolve().parents[1]
PINNED_CHECKPOINT = ROOT / 'research/contrib/chatgpt/CKAD-25/qualified-development-runs/44331408493/linux/stage-02.native.json'
PINNED_SHA256 = 'c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f'
SOURCE_ADDRESSES = (10, 12, 8, 13, 11, 1, 5, 14, 0, 6, 4, 2)
PUBLIC_CANDIDATES = (3, 7, 9, 15)
FROZEN_WEIGHT = 578  # 3-monomial ANF source law, a synthetic engineering fixture
PUBLIC_WORLDS = (
    ((3, 0), (7, 0)),
    ((3, 0), (7, 0)),
    ((3, 1), (9, 0)),
)


def truth(mask):
    return (FROZEN_WEIGHT & feature_row(mask, 4)).bit_count() & 1


def pin(label):
    return hashlib.sha256(('SRL01_NATIVE_ADAPTER_FIXTURE|' + label).encode('ascii')).hexdigest()


def source_packet():
    return [[x & 7, x >> 3, truth(x)] for x in SOURCE_ADDRESSES]


def history_packets(worlds=PUBLIC_WORLDS):
    return [[[mask & 7, mask >> 3, truth(mask) ^ contradiction]
             for mask, contradiction in witnesses]
            for witnesses in worlds]


def restored_stage2():
    raw = PINNED_CHECKPOINT.read_bytes()
    if digest(raw) != PINNED_SHA256:
        raise ValueError('PINNED_NATIVE_CKAD25_CHECKPOINT_SHA_DRIFT')
    obj = NativeCumulativeLearner.restore(raw, PINNED_SHA256)
    if obj.checkpoint() != raw:
        raise ValueError('NATIVE_CHECKPOINT_COLD_CANONICAL_MISMATCH')
    return obj


def prepared(worlds=PUBLIC_WORLDS):
    original = restored_stage2()
    source = source_packet()
    native, slot, status = original.incorporate_causal_world(
        source, digest(canonical(source)), source_ref=pin('source'),
        available_slots=(1,))
    if (slot, status) != (1, 'ACQUIRED') or native._compiled[1].model_count != 1:
        raise ValueError('SOURCE_ONLY_NATIVE_RELATION_NOT_UNIQUE')
    for slot, rows in zip((12, 13, 14), history_packets(worlds)):
        native = native.observe(slot, rows, digest(canonical(rows)),
                                source_ref=pin('historical_world_' + str(slot)))
    return original, native


def public_records():
    return [[mask & 7, mask >> 3] for mask in PUBLIC_CANDIDATES]


def proposed_mask_list(proposal):
    return tuple(c | (a << 3) for c, a in proposal)


class NativeSRL01AdapterCheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original, cls.prepared = prepared()
        cls.original_raw = cls.original.checkpoint()
        cls.learned_raw = cls.prepared.checkpoint()

    def test_pinned_native_checkpoint_and_cold_restoration(self):
        self.assertEqual(digest(self.original_raw), PINNED_SHA256)
        cold = NativeCumulativeLearner.restore(self.learned_raw,
                                               digest(self.learned_raw))
        self.assertEqual(cold.checkpoint(), self.learned_raw)
        self.assertEqual(cold._compiled[1].model_count, 1)
        self.assertEqual([cold._source._seen[s].bit_count()
                          for s in (12, 13, 14)], [2, 2, 2])

    def test_real_native_adapter_matches_independent_source_only_posterior(self):
        before = self.prepared.checkpoint()
        choice = self.prepared.propose_shared_source_change_witnesses(
            1, (12, 13, 14), public_records())
        reference = NativeSharedFaultRisk(PUBLIC_CANDIDATES, PUBLIC_WORLDS)
        self.assertEqual(proposed_mask_list(choice), reference.select())
        self.assertEqual(proposed_mask_list(choice), (9, 15))
        self.assertEqual(self.prepared.checkpoint(), before)
        self.assertEqual(before, self.learned_raw)

    def test_original_beta_adapter_has_distinct_source_based_choice(self):
        old = self.prepared.propose_source_change_witnesses(
            1, (12, 13, 14), public_records())
        new = self.prepared.propose_shared_source_change_witnesses(
            1, (12, 13, 14), public_records())
        self.assertEqual(proposed_mask_list(old), (15, 3))
        self.assertEqual(proposed_mask_list(new), (9, 15))
        self.assertNotEqual(old, new)

    def test_original_native_memories_survive_all_source_free_observations(self):
        cold = NativeCumulativeLearner.restore(self.learned_raw,
                                               digest(self.learned_raw))
        self.assertEqual(cold._source._seen[0], self.original._source._seen[0])
        self.assertEqual(cold._properties.checkpoint(),
                         self.original._properties.checkpoint())
        self.assertEqual(cold._events[:len(self.original._events)],
                         self.original._events)
        for mask in range(16):
            self.assertEqual(cold.predict(0, mask & 7, mask >> 3),
                             self.original.predict(0, mask & 7, mask >> 3))
        self.assertEqual(cold.propose_shared_source_change_witnesses(
            1, (12, 13, 14), public_records()),
            self.prepared.propose_shared_source_change_witnesses(
                1, (12, 13, 14), public_records()))

    def test_negative_source_overlap_duplicate_and_invalid_history(self):
        candidates = public_records()
        for bad in (candidates[:3], candidates + [candidates[0]],
                    [candidates[0], candidates[0], *candidates[2:]],
                    [[x & 7, x >> 3] for x in SOURCE_ADDRESSES[:4]],
                    [[True, 0], *candidates[1:]]):
            with self.subTest(public=bad), self.assertRaises(ValueError):
                self.prepared.propose_shared_source_change_witnesses(
                    1, (12, 13, 14), bad)
        for bad_slots in ((12, 13), (12, 13, 15), (12, 12, 14)):
            with self.subTest(history=bad_slots), self.assertRaises(ValueError):
                self.prepared.propose_shared_source_change_witnesses(
                    1, bad_slots, candidates)
        with self.assertRaises(ValueError):
            self.original.propose_shared_source_change_witnesses(
                1, (12, 13, 14), candidates)
        with self.assertRaises(ValueError):
            self.prepared.propose_shared_source_change_witnesses(
                1, (12, 13, 14), candidates, count=1)
        self.assertEqual(self.prepared.checkpoint(), self.learned_raw)

    def test_negative_two_contradictions_in_one_world_fail_closed(self):
        invalid = (PUBLIC_WORLDS[0], ((3, 1), (7, 1)), PUBLIC_WORLDS[2])
        _, candidate = prepared(invalid)
        before = candidate.checkpoint()
        with self.assertRaises(ValueError):
            candidate.propose_shared_source_change_witnesses(
                1, (12, 13, 14), public_records())
        self.assertEqual(candidate.checkpoint(), before)

    def test_fixture_unique_full_source_and_no_hidden_labels_in_native_packet(self):
        self.assertEqual(len(set(SOURCE_ADDRESSES + PUBLIC_CANDIDATES)), 16)
        source = source_packet()
        self.assertEqual(len(source), 12)
        for rows in history_packets():
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(len(row) == 3 for row in rows))
        all_models = (sum(1 << i for i in combo)
                      for n in range(4)
                      for combo in itertools.combinations(range(16), n))
        matches = [w for w in all_models
                   if all(((w & feature_row(x, 4)).bit_count() & 1) == truth(x)
                          for x in SOURCE_ADDRESSES)]
        self.assertEqual(matches, [FROZEN_WEIGHT])
        self.assertFalse(self.original.info()['accepted_native'])
        self.assertFalse(self.prepared.info()['accepted_native'])
        self.assertFalse(self.prepared.info()['scientific_pass'])


if __name__ == '__main__':
    unittest.main()

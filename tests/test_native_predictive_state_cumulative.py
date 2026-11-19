"""Exact-source, read-only CAP03-to-CAP04 native/JEPA custody qualification.

This test NEVER generates development data or advances the native training
ledger. It only imports publicly witnessed historical events as controls.
"""
import json
from pathlib import Path
import sys
import unittest

from yggdrasil.native_context_basis import digest
from yggdrasil.native_evidence_recall import restore_original_sealed_native
from yggdrasil.native_predictive_state_split import PredictiveStateSplit
from yggdrasil.native_predictive_state_controls import MatchedHistoryControls, ARMS

ROOT = Path(__file__).resolve().parents[1]
PLATFORM = 'windows' if sys.platform == 'win32' else 'linux'
EXPECTED = {14071: 1118, 14072: 1093}

class NativeCumulativeCustodyTests(unittest.TestCase):
    def test_both_original_six_head_native_checkpoints_remain_unchanged(self):
        for seed, count in EXPECTED.items():
            with self.subTest(seed=seed, platform=PLATFORM):
                path = (ROOT / 'research/contrib/chatgpt/YGG-CAP03/original' /
                        PLATFORM / f'seed-{seed}-state.json')
                evidence = json.loads(path.read_bytes())
                before = evidence['model_ascii'].encode('ascii')
                self.assertEqual(digest(before), evidence['model_sha256'])
                model = restore_original_sealed_native(before, digest(before))
                self.assertEqual(model.total_count, count)
                original_readouts = tuple((model.archived_forecast(e[1][0], e[2]),
                                           model.archived_forecast(e[1][0], e[2], e[3], e[4]))
                                          for e in model._events[-8:])
                original_history = tuple(model._events)
                archived_before = bytes(model._archive_raw)
                head_before = tuple([h.as_data() for h in model._one] +
                                    [h.data() for h in model._temporal] +
                                    [h.checkpoint() for h in model._future])
                proposal = PredictiveStateSplit.from_native_events(original_history)
                controls = MatchedHistoryControls.from_native_events(original_history)
                self.assertEqual((proposal.count, controls.count), (count, count))
                self.assertEqual(model.checkpoint(), before)
                self.assertEqual(tuple(model._events), original_history)
                self.assertEqual(model._archive_raw, archived_before)
                self.assertEqual(tuple([h.as_data() for h in model._one] +
                                       [h.data() for h in model._temporal] +
                                       [h.checkpoint() for h in model._future]), head_before)
                self.assertEqual(tuple((model.archived_forecast(e[1][0], e[2]),
                                        model.archived_forecast(e[1][0], e[2], e[3], e[4]))
                                       for e in model._events[-8:]), original_readouts)
                st = original_history[-1][6]
                views = ((st[0], st[1]), (st[1], st[2]))
                self.assertTrue(0 <= proposal.forecast(views, (0, 0), 'transition') <= 1)
                comparators = controls.forecast(views, (0, 0), 'transition')
                self.assertEqual(set(comparators), set(ARMS))
                self.assertTrue(all(0 <= p <= 1 for p in comparators.values()))
                self.assertEqual(model.checkpoint(), before)

if __name__ == '__main__': unittest.main()

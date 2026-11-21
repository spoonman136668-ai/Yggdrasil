"""Real NativeEpisodeExperience source-free compatibility; no original-world actions."""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

MODULE = Path(__file__).with_name("factorized_context_readout.py")
SPEC = spec_from_file_location("fcr01_real_native_readout", MODULE)
FCR = module_from_spec(SPEC)
SPEC.loader.exec_module(FCR)
VIEWS = ((0, 0), (0, 1))


def row(i):
    return {"s1": 0, "x1": i & 1, "s2": (i >> 1) & 1,
            "x2": (i >> 2) & 1, "y": (i >> 3) & 1}


def admitted(native, index):
    return native.observe(format(index + 1, "064x"), VIEWS, row(index))


def fixture():
    native = NativeEpisodeExperience()
    for index in range(32):
        native = admitted(native, index)
    self_state = native.checkpoint()
    stream = native.begin_stream()
    assert len(stream._context_models) == 2
    assert native.checkpoint() == self_state
    return stream


class NativeInterfaceContractTests(unittest.TestCase):
    def test_actual_native_one_witness_then_cold_restore(self):
        before = fixture()
        frozen = before.checkpoint()
        wrapper = FCR.FactorizedContextReadout(before)
        first = wrapper.transition(VIEWS[0], 0)
        terminal = wrapper.reward(VIEWS[0], 0, 1, 0)
        successor = admitted(before, 32)
        next_readout = wrapper.advance(successor)
        self.assertEqual(len(successor._ledger), 33)
        self.assertEqual(before.checkpoint(), frozen)
        self.assertEqual(wrapper.transition(VIEWS[0], 0), first)
        self.assertEqual(wrapper.reward(VIEWS[0], 0, 1, 0), terminal)
        self.assertEqual(len(next_readout._transition), 2)
        self.assertEqual(len(next_readout._reward), 2)
        native_raw = successor.checkpoint()
        cold_native = NativeEpisodeExperience.restore(native_raw, digest(native_raw))
        sidecar_raw = next_readout.checkpoint()
        cold = FCR.FactorizedContextReadout.restore(
            cold_native, sidecar_raw, FCR.digest(sidecar_raw))
        self.assertEqual(cold.checkpoint(), sidecar_raw)
        self.assertEqual(cold.transition(VIEWS[0], 0),
                         next_readout.transition(VIEWS[0], 0))
        self.assertEqual(cold.reward(VIEWS[0], 0, 1, 0),
                         next_readout.reward(VIEWS[0], 0, 1, 0))

    def test_actual_native_replay_rejects_and_does_not_mutate_adapter(self):
        before = fixture()
        wrapper = FCR.FactorizedContextReadout(before)
        old_native = before.checkpoint()
        old_adapter = wrapper.checkpoint()
        same = admitted(before, 32)
        cold = same.checkpoint()
        with self.assertRaisesRegex(ValueError, "REPLAY_OR_NONADMITTED_WITNESS"):
            wrapper.advance(before)
        with self.assertRaisesRegex(ValueError, "REPLAY_OR_NONADMITTED_WITNESS"):
            wrapper.advance(admitted(same, 33))
        same_again = same.observe(format(33, "064x"), VIEWS, row(32))
        self.assertIs(same_again, same)
        accepted = wrapper.advance(same)
        with self.assertRaisesRegex(ValueError, "REPLAY_OR_NONADMITTED_WITNESS"):
            accepted.advance(same_again)
        self.assertEqual(same.checkpoint(), cold)
        self.assertEqual(before.checkpoint(), old_native)
        self.assertEqual(wrapper.checkpoint(), old_adapter)
        with self.assertRaises(ValueError):
            same.observe(format(33, "064x"), VIEWS,
                         {**row(32), "y": 1 - row(32)["y"]})

    def test_existing_native_context_change_is_not_auto_rebased(self):
        before = fixture()
        wrapper = FCR.FactorizedContextReadout(before)
        different_context = before.enable_context_refresh()
        with self.assertRaisesRegex(ValueError, "REPLAY_OR_NONADMITTED_WITNESS"):
            wrapper.advance(different_context)
        new_witness = admitted(different_context, 32)
        with self.assertRaisesRegex(ValueError, "EXPERT_SET_DRIFT"):
            wrapper.advance(new_witness)
        self.assertEqual(wrapper._native.checkpoint(), before.checkpoint())

    def test_no_oracle_and_source_free_episode_budget(self):
        before = fixture()
        untouched = before.checkpoint()
        adapter = FCR.FactorizedContextReadout(before)
        for first in (0, 1):
            p = adapter.transition(VIEWS[0], first)
            self.assertTrue(0 <= p <= 1)
            for state in (0, 1):
                for second in (0, 1):
                    q = adapter.reward(VIEWS[0], first, state, second)
                    self.assertTrue(0 <= q <= 1)
        self.assertEqual(before.checkpoint(), untouched)
        self.assertEqual(len(before._ledger), 32)
        self.assertFalse(adapter.checkpoint().find(b'"scientific_pass":true') >= 0)


if __name__ == "__main__":
    unittest.main()

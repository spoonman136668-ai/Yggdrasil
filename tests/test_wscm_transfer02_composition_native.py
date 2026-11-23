"""Original NativeEpisodeExperience fixture intake + WSCM composition diagnostics.

Must run against exact repo native modules. No mock, real source world, or held seed.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

from yggdrasil.native_episode_experience import NativeEpisodeExperience
from yggdrasil.native_external_action_identity import RECEIPT_SCHEMA, SOURCE_MODE, _canonical
from yggdrasil.native_context_basis import digest

READOUT = Path(__file__).resolve().parents[1] / 'research' / 'contrib' / 'chatgpt' / 'WSCM-TRANSFER-02' / 'composition_wire_dev.py'
SPEC = importlib.util.spec_from_file_location('composition_wire_native', READOUT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
propose = MOD.propose_two_step_composition

STATES = ((0, 0), (0, 1), (1, 0), (1, 1))
FIRST = (0, 1, 1, 0)
SECOND = (0, 0, 1, 1)


def receipt(action, state, outcome, source_number):
    data = {'schema': RECEIPT_SCHEMA, 'source_mode': SOURCE_MODE,
            'source_id': f'{source_number:064x}', 'public_view': list(state),
            'external_action_id': action, 'outcome': outcome}
    raw = _canonical(data)
    return raw, hashlib.sha256(raw).hexdigest()


def add_witnesses(native, action, outcomes, initial=1, limit=4):
    for i, state in enumerate(STATES[:limit]):
        raw, pin = receipt(action, state, outcomes[i], initial + i)
        native = native.observe_external_fixture(
            {'public_view': list(state), 'external_action_id': action}, raw, pin)
    return native


def trace(source, start, wire='y_then_output'):
    x, y = start
    z = FIRST[2 * x + y]
    intermediate = {'output_then_x': (z, x), 'output_then_y': (z, y),
                    'x_then_output': (x, z), 'y_then_output': (y, z)}[wire]
    return {'source_id': f'{source:064x}', 'public_view': list(start),
            'first_outcome': z, 'second_public_view': list(intermediate),
            'second_outcome': SECOND[2 * intermediate[0] + intermediate[1]]}


class CompositionActualNativeGate(unittest.TestCase):
    def setUp(self):
        self.original = NativeEpisodeExperience()
        self.native = add_witnesses(self.original, 1301, FIRST, 1)
        self.native = add_witnesses(self.native, 22007, SECOND, 10)
        self.rows = (trace(100, (0, 1)), trace(101, (1, 0)))

    def call(self, native=None, rows=None, query=None):
        return propose(self.native if native is None else native, 1301, 22007,
                       self.rows if rows is None else rows,
                       [1, 1] if query is None else query)

    def test_actual_native_full_primitive_signatures_and_symbolic_parity(self):
        for i, state in enumerate(STATES):
            self.assertEqual(self.native.observed_external_fixture_value(state, 1301), FIRST[i])
            self.assertEqual(self.native.observed_external_fixture_value(state, 22007), SECOND[i])
        result = self.call()
        self.assertEqual((result['status'], result['compatible_wirings'],
                          result['predicted_next_bit']), ('HYPOTHESIS', ['y_then_output'], 1))
        self.assertEqual(result['predicted_next_bit'], SECOND[2*1 + FIRST[3]])

    def test_native_checkpoint_and_original_causal_bank_unchanged_by_readout(self):
        raw = self.native.checkpoint()
        before = self.native.info().get('state_sha256')
        self.call()
        self.assertEqual(self.native.checkpoint(), raw)
        self.assertEqual(self.native.info().get('state_sha256'), before)
        self.assertEqual(self.original.checkpoint(), NativeEpisodeExperience().checkpoint())

    def test_true_native_cold_restore(self):
        raw = self.native.checkpoint()
        restored = NativeEpisodeExperience.restore(raw, digest(raw))
        self.assertEqual(raw, restored.checkpoint())
        self.assertEqual(self.call(), self.call(native=restored))

    def test_no_native_source_authority_or_action_permit(self):
        output = self.call()
        for key in ('structural_chain_authenticated', 'action_authorized',
                    'native_state_updated', 'scientific_gain_verified'):
            self.assertFalse(output[key])
        envelope = json.loads(self.native.checkpoint())
        self.assertFalse(envelope['scientific_pass'])
        self.assertFalse(envelope['native_accepted'])
        self.assertEqual(self.native.info().get('external_action_source_mode'),
                         'engineering_fixture_only')

    def test_incomplete_original_native_signature_abstains(self):
        partial = add_witnesses(NativeEpisodeExperience(), 1301, FIRST, 1000)
        partial = add_witnesses(partial, 22007, SECOND, 2000, limit=3)
        self.assertEqual(self.call(native=partial)['reason'], 'PRIMITIVE_NOT_FULLY_WITNESSED')

    def test_renamed_action_has_no_zero_shot_transfer(self):
        self.assertIsNone(self.native.observed_external_fixture_value((0, 0), 90017))
        seen = add_witnesses(self.native, 90017, SECOND, 1000, limit=3)
        self.assertIsNone(seen.observed_external_fixture_value((0, 0), 90017))
        raw, pin = receipt(90017, (1, 1), SECOND[3], 1003)
        complete = seen.observe_external_fixture(
            {'public_view': [1, 1], 'external_action_id': 90017}, raw, pin)
        self.assertEqual(complete.observed_external_fixture_value((0, 1), 90017), SECOND[1])
        self.assertTrue(complete._external_action_fixture.observed_equivalent(22007, 90017))

    def test_ambiguous_wiring_must_abstain(self):
        rows = (trace(101, (0, 0)), trace(102, (0, 1)))
        self.assertEqual(self.call(rows=rows)['reason'], 'AMBIGUOUS_WIRING')

    def test_conflicting_structural_traces(self):
        rows = (trace(102, (0, 1)), trace(103, (0, 1), 'x_then_output'))
        self.assertEqual(self.call(rows=rows)['status'], 'CONTRADICTION')

    def test_structural_source_ids_are_only_syntactic_pins(self):
        output = self.call()
        self.assertEqual(output['source_mode'], 'engineering_fixture_only')
        self.assertFalse(output['structural_chain_authenticated'])
        with self.assertRaisesRegex(ValueError, 'WSCM_COMPOSE_TRACE_FIELDS'):
            self.call(rows=(self.rows[0] | {'phase': 'A'}, self.rows[1]))

    def test_corrupted_native_receipt_rejected(self):
        raw, _ = receipt(1301, (0, 0), 0, 900)
        doc = json.loads(raw)
        doc['role'] = 2
        forged = _canonical(doc)
        with self.assertRaises(ValueError):
            self.native.observe_external_fixture(
                {'public_view': [0, 0], 'external_action_id': 1301},
                forged, hashlib.sha256(forged).hexdigest())

    def test_original_binary_episode_remains_compatible(self):
        grown = self.native.observe(
            'f'*64, ((0, 0), (0, 0)),
            {'s1': 0, 'x1': 0, 's2': 0, 'x2': 0, 'y': 0})
        self.assertEqual(grown.observed_external_fixture_value((1, 0), 1301), 1)
        self.assertEqual(self.call(native=grown), self.call())
        cold = NativeEpisodeExperience.restore(grown.checkpoint(), digest(grown.checkpoint()))
        self.assertEqual(self.call(native=cold), self.call())

    def test_unchanged_default_native_checkpoint_format(self):
        empty = NativeEpisodeExperience()
        self.assertNotIn('fixture-dev', json.loads(empty.checkpoint())['schema'])
        self.assertIsNone(empty.observed_external_fixture_value((0, 0), 1301))

if __name__ == '__main__':
    unittest.main()

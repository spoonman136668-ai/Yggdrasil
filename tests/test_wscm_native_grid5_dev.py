"""Grid5 v8 DEV evidence in the ORIGINAL cumulative/native classes; no source steps."""
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import (
    NativeEpisodeExperience, GRID5_FIXTURE_SCHEMA, EXTERNAL_FIXTURE_SCHEMA,
)
from yggdrasil.native_grid5_ingress import (
    SCHEMA as GRID5_RECEIPT_SCHEMA, SOURCE_MODE as GRID5_SOURCE_MODE,
)
from yggdrasil.native_external_action_identity import (
    SCHEMA as LEGACY_SCHEMA, RECEIPT_SCHEMA as LEGACY_RECEIPT_SCHEMA,
    SOURCE_MODE as LEGACY_SOURCE_MODE,
)
from yggdrasil.native_property_knowledge import NativePropertyKnowledge
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner, EXPERIENCE_SOURCE
from yggdrasil.native_causal_amalgam import NativeCausalAmalgam
from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
from yggdrasil.native_jepa_temporal import TemporalLatentSpecialist
from yggdrasil.native_dtr_history import SOURCE_PIN as DTR_PIN
from yggdrasil.native_stochastic_history import SOURCE_PIN as MDP_PIN

ROOT = Path(__file__).resolve().parents[1]


def grid5_fixture(step=0, action=0, before=(0, 0), after=(1, 0), sid=1,
                  episode='a'*64, term=None):
    if term is None:
        term = step == 49
    request = {'episode_id': episode, 'step_index': step,
               'public_state': list(before), 'public_action': action}
    raw = canonical({
        **request, 'schema': GRID5_RECEIPT_SCHEMA,
        'source_mode': GRID5_SOURCE_MODE, 'source_id': f'{sid:064x}',
        'next_state': list(after), 'reward': 0,
        'terminated': term, 'truncated': term,
    })
    return request, raw, digest(raw)


def legacy_fixture(action=1301, view=(0, 0), outcome=0):
    request = {'public_view': list(view), 'external_action_id': action}
    raw = canonical({
        'schema': LEGACY_RECEIPT_SCHEMA, 'source_mode': LEGACY_SOURCE_MODE,
        'source_id': '9'*64, **request, 'outcome': outcome,
    })
    return request, raw, digest(raw)


def parent():
    p = NativePropertyKnowledge('ckad13-test', entities=8, context_bits=3)
    rows = [[e,b,(e>>b)&1] for e in range(8) for b in range(3)]
    p = p.stage_properties(rows, digest(canonical(rows)), source_namespace='ckad13-test')
    native = NativeCumulativeLearner(p.checkpoint(), digest(p.checkpoint()))
    rows = [[x & 7, x >> 3, int(sum((x >> b) & 1 for b in range(3)) >= 2)]
            for x in range(16)]
    native = native.observe(0, rows, digest(canonical(rows)), source_ref='b'*64)
    mdp = (ROOT / 'research/contrib/chatgpt/NKR-20/source_fixture.json').read_bytes()
    dtr = (ROOT / 'research/contrib/chatgpt/CKAD-16/source_public_fit.json').read_bytes()
    native = native.observe_cached_history(mdp, MDP_PIN, 23)
    return native.observe_cached_dtr(dtr, DTR_PIN, 64)


class NativeGrid5EnvelopeIntegration(unittest.TestCase):
    def test_legacy_default_checkpoint_unchanged(self):
        baseline = NativeEpisodeExperience()
        raw = baseline.checkpoint()
        cold = NativeEpisodeExperience.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        self.assertNotEqual(json.loads(raw)['schema'], GRID5_FIXTURE_SCHEMA)
        self.assertIsNone(cold._grid5_fixture)

    def test_v8_stages_only_in_the_existing_learner(self):
        baseline = NativeEpisodeExperience()
        untouched = baseline.checkpoint()
        before = baseline.forecast((0, 0), 0)
        staged = baseline.observe_grid5_fixture(*grid5_fixture())
        self.assertEqual(baseline.checkpoint(), untouched)
        self.assertEqual(staged.info()['state_sha256'], baseline.info()['state_sha256'])
        self.assertEqual(staged.forecast((0, 0), 0), before)
        self.assertEqual(staged._transition.snapshot(), baseline._transition.snapshot())
        self.assertEqual(staged._terminal.snapshot(), baseline._terminal.snapshot())
        self.assertEqual(staged.grid5_fixture_forecast([0,0],0), [1,0])
        self.assertEqual(staged.grid5_fixture_plan([0,0])['public_action'], 1)
        self.assertEqual(json.loads(staged.checkpoint())['schema'], GRID5_FIXTURE_SCHEMA)

    def test_v8_native_cold_and_consolidation_bit_identical(self):
        native = NativeEpisodeExperience()
        for a in range(5):
            native = native.observe_grid5_fixture(*grid5_fixture(
                step=a, action=a, before=(0, 0), after=(0, 0), sid=a+1))
        raw = native.checkpoint()
        cold = NativeEpisodeExperience.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        self.assertEqual(cold.grid5_fixture_plan([0,0]),
                         native.grid5_fixture_plan([0,0]))
        self.assertEqual(cold.consolidate().checkpoint(), raw)

    def test_legacy_v7_and_grid5_v8_coexist_without_alias(self):
        base = NativeEpisodeExperience()
        legacy = base.observe_external_fixture(*legacy_fixture())
        v7 = legacy.checkpoint()
        self.assertEqual(json.loads(v7)['schema'], EXTERNAL_FIXTURE_SCHEMA)
        native = legacy.observe_grid5_fixture(*grid5_fixture())
        raw = native.checkpoint()
        self.assertEqual(json.loads(raw)['schema'], GRID5_FIXTURE_SCHEMA)
        cold = NativeEpisodeExperience.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        self.assertEqual(cold._external_action_fixture.checkpoint(),
                         legacy._external_action_fixture.checkpoint())
        self.assertEqual(cold.consolidate().checkpoint(), raw)

    def test_rehashed_public_outcome_forgery_fails_v8(self):
        native = NativeEpisodeExperience().observe_grid5_fixture(*grid5_fixture())
        obj = json.loads(native.checkpoint())
        obj['grid5_checkpoint']['records'][0][5] = [0,0]
        obj['grid5_sha256'] = digest(canonical(obj['grid5_checkpoint']))
        raw = canonical(obj)
        with self.assertRaises(ValueError):
            NativeEpisodeExperience.restore(raw, digest(raw))

    def test_native_original_binary_action_does_not_expand(self):
        model = NativeEpisodeExperience().observe_grid5_fixture(*grid5_fixture())
        with self.assertRaises(ValueError):
            model.forecast((0,0),4)
        self.assertEqual(model.grid5_fixture_plan([0,0])['source_mode'],
                         'engineering_fixture_only')

    def test_existing_parent_gate_is_preserved(self):
        p = NativePropertyKnowledge('ckad13-test', entities=8, context_bits=3)
        data=p.checkpoint()
        m=NativeCumulativeLearner(data,digest(data))
        with self.assertRaisesRegex(ValueError, 'EPISODE_REQUIRES_INTEGRATED_PARENT'):
            m.observe_grid5_fixture(*grid5_fixture())

    def test_cumulative_original_native_cold_and_binary_isolation(self):
        original = parent()
        original_raw = original.checkpoint()
        model = original.observe_grid5_fixture(*grid5_fixture())
        self.assertEqual(original.checkpoint(), original_raw)
        self.assertEqual(model.grid5_fixture_forecast([0,0],0),[1,0])
        saved = model.checkpoint()
        cold = NativeCumulativeLearner.restore(saved, digest(saved))
        self.assertEqual(cold.checkpoint(), saved)
        self.assertEqual(cold.consolidate_experience().checkpoint(),saved)

    def test_amalgam_reconstructs_grid5_suffix_not_shadow_training(self):
        heads=(ActionLatentSpecialist('transition'),ActionLatentSpecialist('reward'),
               TemporalLatentSpecialist('transition'),TemporalLatentSpecialist('reward'))
        base = NativeCausalAmalgam(parent(),heads,'a'*64,'b'*64)
        original_head_steps=tuple(h.steps for h in base._heads)
        model=base.observe_grid5_fixture(*grid5_fixture())
        model=model.observe_grid5_fixture(*grid5_fixture(
            step=1,action=1,before=(1,0),after=(1,1),sid=2))
        self.assertEqual(tuple(h.steps for h in model._heads),original_head_steps)
        self.assertEqual(model.plan_grid5_fixture([1,0])['public_action'],0)
        raw=model.checkpoint()
        with patch.object(NativeCausalAmalgam,'activate',return_value=base):
            restored=NativeCausalAmalgam.restore(
                raw,digest(raw),native_parent=b'',native_pin='a'*64,
                donor_parent=b'',donor_pin='b'*64)
        self.assertEqual(restored.checkpoint(),raw)
        self.assertEqual(restored.grid5_fixture_forecast([1,0],1),[1,1])
        self.assertEqual(tuple(h.steps for h in restored._heads),original_head_steps)


if __name__ == '__main__':
    unittest.main()

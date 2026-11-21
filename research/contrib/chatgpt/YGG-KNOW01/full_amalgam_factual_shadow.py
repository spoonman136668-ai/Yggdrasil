"""KNOW10: restore the complete archived Amalgam and audit factual readout.

Source-bound engineering replay: no policy activation, new source observations,
trainer execution, owner-controlled checkpoint or scientific acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path

from typed_readout_bridge import TypedFactualReadoutBridge
from explicit_view_projection import ExplicitPublicViewProjection, make_fixture_manifest
from real_image_pairing import bundle
from native_cold_shadow import JOINT_SHA, NATIVE_SHA, valid_nested

NATIVE_PARENT_SHA = 'a00119c73a6431172c19b39ec67a1d94b470897a32c55c1c946071793f37dcc4'
DONOR_FILE_SHA = '7e7507af589ae6b08a7599f1abafa9dd998895299fbb423cfc2995ecbcf741cd'
DONOR_PARENT_SHA = 'ae83529696b566a12765f16749c258d9ed6addf111da41ef76dc1027938910da'
SOURCE_ROWS = 21_343_681
STEPS_PER_HEAD = 2109
EXPECTED_PROBES = 160


def insist(value, reason):
    if not value:
        raise ValueError('YGG_KNOW10_' + reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def read_exact(path, expected, maximum):
    path = Path(path)
    insist(path.is_file() and not path.is_symlink() and 0 < path.stat().st_size <= maximum,
           'PARENT_MISSING_OR_OVERSIZE')
    data = path.read_bytes()
    insist(digest(data) == expected, 'EXTERNAL_PARENT_SHA')
    return data


def original_parents(native_file, donor_file):
    native = read_exact(native_file, NATIVE_PARENT_SHA, 8 * 1024 * 1024)
    donor_blob = read_exact(donor_file, DONOR_FILE_SHA, 1024 * 1024)
    try:
        outer = json.loads(donor_blob.decode('ascii'))
        raw = outer['state_ascii'].encode('ascii')
    except (UnicodeError, ValueError, KeyError, TypeError) as exc:
        raise ValueError('YGG_KNOW10_DONOR_ENVELOPE') from exc
    insist(outer.get('state_sha256') == DONOR_PARENT_SHA and
           digest(raw) == DONOR_PARENT_SHA, 'DONOR_PARENT_PIN')
    return dict(native_parent=native, native_pin=NATIVE_PARENT_SHA,
                donor_parent=raw, donor_pin=DONOR_PARENT_SHA)


def restore(joint, parents):
    from yggdrasil.native_causal_amalgam import NativeCausalAmalgam
    valid_nested(joint, JOINT_SHA, NATIVE_SHA)
    model = NativeCausalAmalgam.restore(joint, JOINT_SHA, **parents)
    insist(model.checkpoint() == joint and
           digest(model.native.checkpoint()) == NATIVE_SHA and
           len(model.native._episode_reader()._ledger) == 1025,
           'COMPLETE_RESTORATION_DRIFT')
    head_steps = [h.steps for h in model._heads]
    insist(head_steps == [STEPS_PER_HEAD] * 4, 'FOUR_HEAD_STEPS')
    return model


def readout(model):
    """Source-frozen 160 model-probability probes; not heldout science."""
    x = []
    for context, nuisance1, nuisance2 in product((0, 1), repeat=3):
        views = ((context, nuisance1), (context, nuisance2))
        for first in (0, 1):
            x.extend(model.specialist_forecasts(views, first))
            for state, second in product((0, 1), repeat=2):
                x.extend(model.specialist_forecasts(views, first, state, second))
    insist(len(x) == EXPECTED_PROBES and
           all(type(v) is float and 0.0 <= v <= 1.0 for v in x),
           'SPECIALIST_READOUT_INVALID')
    return {'probes': len(x), 'readout_sha256': digest(canonical(x))}


class FrozenJoint:
    """Read-only view for the existing KNOW02 bridge; no observe method."""
    __slots__ = ('_joint', '_model')

    def __init__(self, joint, model):
        insist(model.checkpoint() == joint and digest(joint) == JOINT_SHA,
               'FROZEN_JOINT_MISMATCH')
        self._joint, self._model = joint, model

    def checkpoint(self):
        insist(self._model.checkpoint() == self._joint,
               'FROZEN_JOINT_MUTATED')
        return self._joint

    def plan(self, view):
        self.checkpoint()
        answer = self._model.plan(view)
        self.checkpoint()
        return answer


def prove(session, joint_path, native_path, donor_path):
    from yggdrasil.native_cumulative_facts import CumulativeNativeFacts
    from yggdrasil.native_knowledge_activation import open_installed_session

    joint = read_exact(joint_path, JOINT_SHA, 32 * 1024 * 1024)
    parents = original_parents(native_path, donor_path)
    live = restore(joint, parents)
    old = readout(live)
    old_native = live.native.checkpoint()
    wrapper = FrozenJoint(joint, live)
    with open_installed_session(session) as historical:
        insist(len(historical._weights) == SOURCE_ROWS, 'HISTORICAL_FACTS')
        first, last = (tuple(historical._weights.row_at(i))
                       for i in (0, SOURCE_ROWS - 1))
        base = CumulativeNativeFacts(historical)
        base_raw = base.checkpoint()
        old_bridge = TypedFactualReadoutBridge(
            wrapper, base, native_checkpoint_sha256=JOINT_SHA,
            facts_checkpoint_sha256=base.checkpoint_sha256)
        for triple in (first, last):
            insist(old_bridge.fact(*triple)['evidence_kind'] ==
                   'HISTORICAL_STORED_QPQ', 'BEFORE_HISTORICAL_FACT')
        # Two new synthetic direct facts in the NKR08 *separate* overlay.
        # They are not causal interventions and are not added to Amalgam.
        synthetic = [(4294960000, 901, 4294961000),
                     (4294960001, 901, 4294961001)]
        insist(all(not historical.fact(*v)['witnessed'] for v in synthetic),
               'FIXTURE_BASE_COLLISION')
        b = bundle('know10-complete-heads-fixture',
                   [[*t, f'know10:{i:02d}'] for i, t in enumerate(synthetic)])
        staged, stage_receipt = base.stage(b, digest(b))
        insist(stage_receipt['new_unique_facts'] == 2, 'SYNTHETIC_STAGE')
        after_stage = readout(live)
        cold_facts = CumulativeNativeFacts(
            historical, staged.checkpoint(), checkpoint_sha256=staged.checkpoint_sha256)
        cold = restore(joint, parents)
        after_cold = readout(cold)
        insist(old == after_stage == after_cold, 'SPECIALISTS_CHANGED_BY_FACTS')
        insist(live.native.checkpoint() == cold.native.checkpoint() == old_native,
               'NATIVE_FORGOT')
        insist(cold_facts.checkpoint() == staged.checkpoint() and
               base.checkpoint() == base_raw, 'FACT_COLD_RESTORE')
        for t in synthetic:
            insist(cold_facts.fact(*t)['classification'] ==
                   'DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED', 'NEW_FACT_LOST')
        for t in (first, last):
            insist(cold_facts.fact(*t)['classification'] ==
                   'HISTORICAL_TRAIN_FACT', 'HISTORICAL_FACT_LOST')
        frozen = FrozenJoint(joint, cold)
        bridge = TypedFactualReadoutBridge(
            frozen, cold_facts, native_checkpoint_sha256=JOINT_SHA,
            facts_checkpoint_sha256=cold_facts.checkpoint_sha256)
        rows = sorted([[list(first), [[0, 0], [0, 1]]],
                       [list(last), [[1, 1], [1, 0]]]], key=lambda x: x[0])
        mapping, pin = make_fixture_manifest(JOINT_SHA,
                        cold_facts.checkpoint_sha256, rows)
        projection = ExplicitPublicViewProjection(bridge, mapping, pin)
        for fact, view in ((first, (0, 0)), (last, (1, 1))):
            answer = projection.shadow_plan(*fact)
            insist(answer['native_plan_called'] is True and
                   answer['shadow_plan'] == frozen.plan(view) and
                   answer['native_training_performed'] is False and
                   answer['causal_observation_admitted'] is False,
                   'POLICY_SHADOW_DRIFT')
        insist(projection.shadow_plan(0xffffffff, 0xffffffff, 0xffffffff)[
            'classification'] == 'ABSTAIN_UNKNOWN_FACT', 'UNKNOWN_NOT_ABSTAINED')
        insist(readout(cold) == old and frozen.checkpoint() == joint and
               base.checkpoint() == base_raw, 'POST_SHADOW_DRIFT')
    return {
        'schema': 'yggdrasil.know10.complete-archived-amalgam-factual-shadow.v1',
        'classification': 'RESEARCH_ENGINEERING_ONLY',
        'original_joint_checkpoint_sha256': JOINT_SHA,
        'original_native_checkpoint_sha256': NATIVE_SHA,
        'native_parent_sha256': NATIVE_PARENT_SHA,
        'donor_parent_sha256': DONOR_PARENT_SHA,
        'original_witnessed_episodes': 1025,
        'fully_restored_specialist_heads': 4,
        'original_gradient_steps_per_head': STEPS_PER_HEAD,
        'historical_training_facts': SOURCE_ROWS,
        'new_synthetic_fact_candidates': 2,
        'old_historical_facts_retained': 2,
        'factual_cold_restoration': True,
        'native_cold_restoration': True,
        'four_specialists_cold_restoration': True,
        'specialist_readouts_before_and_after_identical': True,
        'specialist_readout': old,
        'existing_native_policy_changed': False,
        'unverified_real_world_knowledge': 0,
        'source_actions': 0,
        'scientific_pass': False,
        'canonical_checkpoint_owner': 'UNVERIFIED',
        'deployment': 'NONE',
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--installed-session', required=True, type=Path)
    p.add_argument('--joint-checkpoint', required=True, type=Path)
    p.add_argument('--native-parent', required=True, type=Path)
    p.add_argument('--donor-parent', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    result = prove(a.installed_session, a.joint_checkpoint,
                   a.native_parent, a.donor_parent)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n',
                        encoding='utf-8')
    print('KNOW10_FULL_RESEARCH_COLD_RESTORE_PASS ' + json.dumps({
        'heads': result['fully_restored_specialist_heads'],
        'head_steps': result['original_gradient_steps_per_head'],
        'specialist_readout_count': result['specialist_readout']['probes'],
        'scientific_pass': False}, sort_keys=True))

if __name__ == '__main__':
    main()
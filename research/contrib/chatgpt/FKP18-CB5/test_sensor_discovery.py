"""CB5 focused source-safe tests: public-only evidence, six causal candidates."""
from __future__ import annotations
from collections import namedtuple
from itertools import combinations
from pathlib import Path
import ast
import unittest

import public_source as source
import sensor_inference as learner

FOUR=(1,6,17,22)
PAIRS=tuple(combinations(FOUR,2))
BEFORE=(0,)*8
SENSORS=(0,)*8

def bit_row(feature):
    state=list(BEFORE)
    state[feature//4]^=1<<(feature%4)
    changed=tuple(int(feature in pair) for pair in PAIRS)+(0,0)
    return source.PublicBitProbe(BEFORE,feature,tuple(state),SENSORS,changed,1)

def outcome_row(channel, mediator_channel=3):
    after=list(SENSORS)
    if channel>=0:after[channel]^=1
    earned=-1 if channel==mediator_channel else 1
    return source.PublicOutcomeProbe(BEFORE,channel,SENSORS,tuple(after),0,earned,1)

def fit_on_fabricated(mediator_channel):
    direct=learner.DirectCausalSensor(FOUR)
    conventional=learner.ConventionalSensorPosterior(FOUR)
    for f in FOUR:
        row=bit_row(f)
        direct.observe_bit(row);conventional.observe_bit(row)
    direct.observe_baseline(outcome_row(-1))
    conventional.observe_baseline(outcome_row(-1))
    while (ch:=direct.next_channel()) is not None:
        direct.observe_sensor(outcome_row(ch,mediator_channel))
    while (ch:=conventional.next_channel()) is not None:
        conventional.observe_sensor(outcome_row(ch,mediator_channel))
    return direct,conventional

class CB5BlindMechanismContract(unittest.TestCase):
    def test_new_public_cohort_fence_and_no_private_in_public_probe(self):
        self.assertEqual(len(source.SEEDS),32)
        for wrong in (True,82532,82400,978500,978600):
            with self.assertRaises(PermissionError):source.PaidInterventionWorld(wrong)
        env=source.PaidInterventionWorld(82500)
        row=env.bit_probe(FOUR[0])
        self.assertEqual(tuple(row._fields),learner.BIT_FIELDS)
        self.assertFalse(hasattr(row,'_mediator_channel'))
        self.assertEqual(env.paid,1)
        self.assertNotEqual(row.before_state,row.after_state)

    def test_six_candidates_shown_to_both_without_source_identity(self):
        a,b=learner.DirectCausalSensor(FOUR),learner.ConventionalSensorPosterior(FOUR)
        for f in FOUR:
            a.observe_bit(bit_row(f));b.observe_bit(bit_row(f))
        self.assertEqual(len(a.candidates()),6)
        self.assertEqual(set(pair for _,pair in a.candidates()),set(PAIRS))
        b.observe_baseline(outcome_row(-1))
        self.assertEqual(len(b._hypotheses),6)
        self.assertEqual(a.candidates()[0],(0,PAIRS[0]))

    def test_each_of_six_possible_causal_mediators_requires_real_outcome(self):
        for channel in range(6):
            with self.subTest(channel=channel):
                a,b=fit_on_fabricated(channel)
                self.assertEqual(a.selected,(channel,PAIRS[channel]))
                self.assertEqual(a.selected,b.selected)
                self.assertEqual(a.wrong_attribution,(channel+1)%6)
                self.assertLessEqual(a.paid,11)
                self.assertEqual(a.paid,b.paid)
                self.assertNotEqual(a.no_downstream_guess[0],channel) if channel else None

    def test_strict_validation_and_invalid_probe_is_atomic(self):
        a=learner.DirectCausalSensor(FOUR)
        row=bit_row(FOUR[0])
        Extra=namedtuple('Extra',learner.BIT_FIELDS+('private_mediator',))
        invalid=(Extra(*row,3),row._replace(cost=0),
                 row._replace(target_feature=True),
                 row._replace(after_state=row.before_state),
                 row._replace(sensor_after=(0,)*7))
        for fake in invalid:
            with self.assertRaises(ValueError):a.observe_bit(fake)
            self.assertEqual(a.paid,0)
        a.observe_bit(row)
        before=a.paid
        with self.assertRaises(ValueError):a.observe_bit(bit_row(FOUR[0]))
        self.assertEqual(a.paid,before)

    def test_cold_76byte_receipt_and_corruption_fail_closed(self):
        a,_=fit_on_fabricated(4)
        raw=a.snapshot()
        self.assertEqual(len(raw),76)
        cold=learner.DirectCausalSensor.restore(raw)
        self.assertEqual(cold.selected,a.selected)
        self.assertEqual(cold.proof(),raw)
        damaged=bytearray(raw);damaged[4]^=1
        for invalid in (bytes(damaged),b'',raw+b' '):
            with self.assertRaises(ValueError):learner.DirectCausalSensor.restore(invalid)

    def test_outcome_false_confirmation_and_extra_private_fields(self):
        a=learner.DirectCausalSensor(FOUR)
        for f in FOUR:a.observe_bit(bit_row(f))
        a.observe_baseline(outcome_row(-1))
        row=outcome_row(a.next_channel(),mediator_channel=3)
        Extra=namedtuple('Extra',learner.OUT_FIELDS+('future_best_action',))
        for fake in (Extra(*row,0),row._replace(action=True),
                     row._replace(cost=2),row._replace(reward=0),
                     row._replace(target_channel=6),row._replace(sensor_after=SENSORS)):
            with self.assertRaises(ValueError):a.observe_sensor(fake)
            self.assertEqual(a.paid,5)
        a.observe_sensor(row)
        self.assertEqual(a.paid,6)

    def test_physical_source_budget_and_no_duplicate_charges(self):
        env=source.PaidInterventionWorld(82500)
        for f in FOUR:env.bit_probe(f)
        with self.assertRaises(ValueError):env.bit_probe(FOUR[0])
        env.baseline_action()
        with self.assertRaises(ValueError):env.baseline_action()
        for i in range(6):env.sensor_action(i)
        self.assertEqual(env.paid,11)
        for bad in (7,0):
            with self.assertRaises(ValueError):env.sensor_action(bad)

    def test_model_never_imports_source_owner_private_laws(self):
        raw=Path(learner.__file__).read_text('utf-8')
        tree=ast.parse(raw)
        imports=set()
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):imports.update(x.name for x in node.names)
            if isinstance(node,ast.ImportFrom):imports.add(node.module)
        self.assertNotIn('public_source',imports)
        self.assertNotIn('_private_audit',raw)
        self.assertNotIn('_mediator_channel',raw)

if __name__=='__main__':unittest.main()

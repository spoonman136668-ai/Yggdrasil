"""WSCM-EPOCH-01 unscored exact-contract tests, no development outcome use."""
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research/contrib/chatgpt/WSCM-EPOCH-01/experiment.py"
SPEC = spec_from_file_location("wscm_epoch01", SCRIPT)
MOD = module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class EpochTests(unittest.TestCase):
    def test_epoch_banks_keep_a_prior_constant(self):
        x = MOD.EpochMemory(lambda c,a: .2 if a == 0 else .8)
        before = x.old
        for i in range(10):
            x.observe(0,i%2,1 if i%2==0 else 0)
        self.assertEqual(x.old,before)
        self.assertLessEqual(x.activation_count,2)

    def test_standalone_paired_evidence_selects_lower_brier(self):
        x=MOD.EpochMemory(lambda c,a:.1)
        x.activated[0]=True
        for i in range(4):
            x.paired[0].append((.64,.25))
        self.assertEqual(x._weight(0),1.)
        self.assertEqual(x._weight(1),0.)

    def test_exact_native_counter_in_alternate_and_cold_replay(self):
        x = MOD.EpochMemory(lambda c,a:.2)
        x.activated[0]=True
        x.paired[0].extend([(.64,.25)]*4)
        x.observe(0,0,1)
        self.assertEqual(x.alternate._counts[0][0],[0,1])
        restored=MOD.EpochMemory.restore(x.snapshot())
        self.assertEqual(restored.snapshot(),x.snapshot())
        self.assertEqual(restored.predict(0,0),x.predict(0,0))
        with self.assertRaises(Exception):
            MOD.EpochMemory.restore(x.snapshot()[:-1]+b'?')

    def test_frozen_gate_minimum_four_observations(self):
        x=MOD.EpochMemory(lambda c,a:.1)
        x.activated[0]=True
        x.paired[0].extend([(.64,.25)]*3)
        self.assertEqual(x._weight(0),0.)
        x.paired[0].append((.64,.25))
        self.assertEqual(x._weight(0),1.)

    def test_beta_fitted_exact_increment_and_full_information(self):
        model=MOD.CumulativeBeta([(0,0,1),(0,0,1),(0,0,0)])
        self.assertEqual(model.predict(0,0),3/5)
        model.observe(0,0,1)
        self.assertEqual(model.predict(0,0),4/6)

    def test_conventional_controls_are_finite(self):
        history=[(c,a,i%2) for i in range(40) for c,a in ((0,0),(1,1))]
        b=MOD.BayesianChangePoint32(history)
        t=MOD.TrailingBeta(history)
        for c in (0,1):
            for a in (0,1):
                self.assertGreater(b.predict(c,a),0)
                self.assertLess(b.predict(c,a),1)
                self.assertGreater(t.predict(c,a),0)
                self.assertLess(t.predict(c,a),1)

    def test_generator_fixed_public_intervention_schedule_and_no_label_leak(self):
        for scenario,seeds in MOD.SEEDS.items():
            for seed in seeds:
                x=list(MOD.new_outcomes(seed,scenario))
                self.assertEqual(len(x),112)
                self.assertEqual(x,[*MOD.new_outcomes(seed,scenario)])
                self.assertEqual({k:sum(v['context']==k for v in x) for k in (0,1)}, {0:56,1:56})
                self.assertEqual({k:sum(v['action']==k for v in x) for k in (0,1)}, {0:56,1:56})
                self.assertFalse(any('stage' in e or 'regime' in e for e in x))

    def test_public_bit_and_seed_negatives(self):
        with self.assertRaisesRegex(ValueError,'EPOCH_BIT'):
            MOD._bit(2)
        with self.assertRaisesRegex(ValueError,'EPOCH_SEED_OR_REGIME'):
            list(MOD.new_outcomes(1,'B'))
        with self.assertRaisesRegex(ValueError,'EPOCH_SEED_OR_REGIME'):
            list(MOD.new_outcomes(92011,'D'))

    def test_source_pins_without_world_use(self):
        self.assertEqual(MOD.PREREG_COMMIT,'c8dbfb5156e3ebe2878bf518806579c311df9467')
        self.assertEqual(MOD.PREREG_BLOB,'55dbc55bf9722d02bb1f5adfea537d47e055bb15')
        self.assertEqual(MOD.ARTIFACT_SHA,'576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8')


if __name__=='__main__':
    unittest.main()

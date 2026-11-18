"""Focused YNCA-11 gates. All world evaluation in tests is A-only."""
import json
import unittest
import experiment as m


class RetainedOperatorTests(unittest.TestCase):
    def test_vocab_closed_and_distinct(self):
        self.assertEqual(len(m.CANDIDATES),24)
        self.assertEqual(len(set(m.CANDIDATES)),24)
        self.assertTrue(all(0<=x<256 for x in m.CANDIDATES))

    def test_composition_semantics(self):
        opA,opB=m.chosen_ops('A')
        self.assertNotEqual(opA,opB)
        for a in m.ACTIONS:
            intermediate=m.bit(opA,a)
            self.assertEqual(m.truth(opA,opB,'C',a),m.bit(opB,intermediate|(a&6)))

    def test_world_does_not_pass_oracle_to_fitting(self):
        obs,p=m.noisy_world('A','C',93000,2)
        self.assertEqual(len(obs),2)
        self.assertEqual(len(set(x for x,y in obs)),2)
        self.assertEqual(set(p),{0,1,2})
        self.assertTrue(all(y in (0,1) for x,y in obs))

    def test_training_interference_schedule_and_budget(self):
        h=m.context_train('A')
        self.assertEqual(len(h),16)
        self.assertEqual(''.join(k for k,_ in h),'AAAABBBBAAAABBBB')
        self.assertTrue(all(len(obs)==4 for kind,obs in h))

    def test_disjoint_first_use_cohorts(self):
        self.assertTrue(set(m.SPLITS['A']).isdisjoint(set(m.SPLITS['B'])))
        self.assertNotEqual(m.chosen_ops('A'),m.chosen_ops('B'))

    def test_context_posterior_and_compressed_weights(self):
        memories=m.bank('A')
        for prior in memories['separate']:
            self.assertEqual(len(prior),24)
            self.assertAlmostEqual(sum(prior.values()),1,places=9)
            compressed=m.compress(prior)
            self.assertEqual(len(compressed),3)
            self.assertAlmostEqual(sum(compressed.values()),1,places=9)

    def test_memory_restore_without_training_replay(self):
        a,b=m.bank('A')['separate']
        saved=json.dumps({'A':{str(k):v for k,v in m.compress(a).items()},
                          'B':{str(k):v for k,v in m.compress(b).items()}},sort_keys=True)
        x=json.loads(saved)
        pa,pb=[{int(t):v for t,v in x[k].items()} for k in ('A','B')]
        obs,_=m.noisy_world('A','C',93001,2)
        pred=m.gated_prediction(pa,pb,'C',obs)
        self.assertTrue(all(0<=v<=1+1e-12 for v in pred))

    def test_gating_uses_only_observed_consequences(self):
        pa,pb=tuple(map(m.compress,m.bank('A')['separate']))
        obs,_=m.noisy_world('A','C',93002,2)
        out=m.gated_prediction(pa,pb,'C',obs)
        self.assertEqual(len(out),8)
        self.assertEqual(out,m.gated_prediction(pa,pb,'C',obs))

    def test_pass_a_diagnostic_and_known_weakness(self):
        r=m.evaluate('A')
        self.assertEqual(r['memory_entries'],{'A':3,'B':3})
        self.assertAlmostEqual(r['metrics']['A']['TWO_SLOT_TOP3'],.19517037)
        self.assertAlmostEqual(r['metrics']['A']['LAST_B_OVERWRITE'],.31895454)
        self.assertAlmostEqual(r['metrics']['C']['TWO_SLOT_TOP3'],.21402614)
        self.assertAlmostEqual(r['metrics']['C']['GATED_TOP3'],.19425172)
        self.assertLess(r['metrics']['C']['NO_MEMORY'],r['metrics']['C']['GATED_TOP3'])

if __name__=='__main__':unittest.main()

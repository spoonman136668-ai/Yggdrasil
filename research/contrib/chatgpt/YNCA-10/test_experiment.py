"""Unit tests for YNCA-10 (A diagnostics only; B must remain unused)."""
import json
import unittest
import experiment as m


class OperatorMemoryTests(unittest.TestCase):
    def test_complete_boolean_space(self):
        self.assertEqual(len(m.TABLES), 256)
        self.assertEqual(len(m.PERMS), 6)
        self.assertEqual(len(m.KNOWN), 46)
        self.assertEqual(len(m.NOVEL), 210)
        self.assertFalse(set(m.KNOWN).intersection(m.NOVEL))

    def test_input_permutation_preserves_truth_bits(self):
        for p in m.PERMS:
            self.assertEqual(set(m.perm_action(a,p) for a in range(8)), set(range(8)))

    def test_unlisted_operator_a_only(self):
        self.assertIn(m.hidden_table('A'), m.NOVEL)
        self.assertEqual(m.hidden_table('A'), m.hidden_table('A'))

    def test_frozen_disjoint_seed_definitions(self):
        self.assertTrue(set(range(m.SPLITS['A'][0], m.SPLITS['A'][1])).isdisjoint(
            range(m.SPLITS['B'][0], m.SPLITS['B'][1])))
        self.assertTrue(set(range(m.SPLITS['A'][2],m.SPLITS['A'][3])).isdisjoint(
            range(m.SPLITS['B'][2],m.SPLITS['B'][3])))
        self.assertEqual(m.N_TRAIN,48)
        self.assertEqual(m.TOP_K,8)

    def test_observation_budget_a_only(self):
        rows=tuple(m.generate_worlds('A',True))
        self.assertEqual(len(rows),48)
        self.assertTrue(all(len(w['observations'])==5 for w in rows))
        self.assertTrue(all(len({a for a,_ in w['observations']})==5 for w in rows))
        self.assertTrue(all(all(0<=a<8 and y in (0,1) for a,y in w['observations']) for w in rows))

    def test_posterior_is_probability_a_only(self):
        learned=m.train_posterior('A')
        self.assertEqual(len(learned),256)
        self.assertAlmostEqual(sum(learned.values()),1,places=10)
        compressed=m.compress(learned)
        self.assertEqual(len(compressed),8)
        self.assertAlmostEqual(sum(compressed.values()),1,places=10)

    def test_no_heldout_truth_entering_policy_a_only(self):
        learned=m.compress(m.train_posterior('A'))
        w=next(m.generate_worlds('A',False))
        p=m.predict(learned,w['observations'])
        self.assertEqual(len(p),8)
        self.assertTrue(all(0<=v<=1+1e-12 for v in p))
        restored={int(k):v for k,v in json.loads(json.dumps({str(k):v for k,v in learned.items()})).items()}
        self.assertEqual(p,m.predict(restored,w['observations']))

    def test_full_exact_generator_control_a_only(self):
        learned=m.train_posterior('A',m.NOVEL)
        self.assertEqual(len(learned),210)
        self.assertAlmostEqual(sum(learned.values()),1,places=10)

    def test_exploratory_a_replay_no_b_use(self):
        a=m.eval_split('A')
        self.assertEqual(a['worlds_test'],64)
        self.assertEqual(a['metrics']['COMPACT_LEARNED']['brier'],0.05932920)
        self.assertEqual(a['metrics']['EXACT_HIERARCHICAL_BAYES']['brier'],0.05932920)
        self.assertEqual(a['metrics']['UNTRAINED_EXACT']['brier'],0.25)
        self.assertEqual(a['decision'],'DEVELOPMENT_SIGNAL')


if __name__=='__main__':
    unittest.main()

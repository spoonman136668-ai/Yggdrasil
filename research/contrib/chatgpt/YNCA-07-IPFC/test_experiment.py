"""YNCA07 frozen pre-B controls; deliberately excludes B and reserved FRESH seeds."""
import unittest
import experiment as m


class IPFCTests(unittest.TestCase):
    def test_grammar_unique_and_nontrivial(self):
        self.assertEqual(len(m.PROGRAMS),59)
        self.assertEqual(len({p.table for p in m.PROGRAMS}),59)
        self.assertEqual(sum(len(x) for x in m.BY_FAMILY.values()),33)
        self.assertEqual(len(m.PROGRAMS[0].table),16)

    def test_prior_trained_on_separate_seeds(self):
        self.assertEqual(len(m.TRAIN_SEEDS),64)
        self.assertTrue(set(m.TRAIN_SEEDS).isdisjoint(range(*m.SEEDS['B'])))
        self.assertEqual(len(m.PRIOR),len(m.PROGRAMS))
        self.assertAlmostEqual(sum(m.PRIOR.values()),len(m.PROGRAMS)*.25+64)

    def test_no_hidden_truth_in_falsifier(self):
        w=m.world(160001,'TRAIN')
        obs={a:w.table[a] for a in m.PASSIVE}
        cand=m.survivors(obs.items())
        self.assertIn(w,cand)
        a,alt=m.select('IPFC_B',cand,obs,160001,0,{})
        self.assertIsNotNone(a)
        self.assertNotIn(a,obs)
        self.assertIn(alt,cand)
        self.assertNotEqual(alt.table[a],m.choice(cand).table[a])

    def test_candidate_truth_never_leaks_synthetic_outcomes(self):
        w=m.world(160002,'TRAIN')
        self.assertEqual(m.world(160002,'TRAIN'),w)
        a=m.episode(w,'IPFC_B',160002)
        for action,counter,outcome in a['trace']:
            self.assertEqual(outcome,w.table[action])
            self.assertIsInstance(counter,str)

    def test_pass_b_bisection_correction_is_targeted(self):
        w=m.world(160003,'TRAIN')
        obs={a:w.table[a] for a in m.PASSIVE}
        cand=m.survivors(obs.items())
        minimalist=m.choice(cand)
        a=next(x for x in range(16) if x not in obs and m.score_falsifier(cand,minimalist,x,{},False)[1] is not None)
        score_a,prog_a=m.score_falsifier(cand,minimalist,a,{},False)
        score_b,prog_b=m.score_falsifier(cand,minimalist,a,{},True)
        self.assertEqual(prog_a,prog_b)
        self.assertNotEqual(score_a,score_b)

    def test_same_budget_controls(self):
        w=m.world(160004,'TRAIN')
        for method in ('IPFC_A','IPFC_B','EIG','EIG_TRAINED','fixed','random'):
            z=m.episode(w,method,160004)
            self.assertLessEqual(z['probes'],m.N_PROBES)
            self.assertEqual(z['cost'],z['probes']*m.PROBE_COST)
            self.assertLessEqual(z['brier'],1)
            self.assertGreaterEqual(z['accuracy'],0)

    def test_a_replay_without_inspecting_new_cohorts(self):
        r=m.evaluate('A')
        self.assertEqual(r['n'],128)
        self.assertEqual(r['decision'],'NO_CLEAR_SIGNAL')
        self.assertEqual(r['metrics']['IPFC_A']['brier'],.1237971)
        self.assertEqual(r['metrics']['EIG']['brier'],.1007487)


if __name__=='__main__': unittest.main()

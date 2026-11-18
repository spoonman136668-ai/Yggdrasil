"""YNCA-04 exact-source focused controls (train-only)."""
import unittest
import experiment as m


class FrozenProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = m.fit()

    def test_disjoint_sources(self):
        train=set(range(*m.RANGES["train"]))
        dev=set(range(*m.RANGES["dev"]))
        held=set(range(*m.RANGES["heldout"]))
        self.assertFalse(train & dev)
        self.assertFalse(train & held)
        self.assertFalse(dev & held)

    def test_new_mechanisms_not_in_train_grammar(self):
        self.assertFalse(set(m.TRAIN_LAWS) & set(m.NEW_LAWS))
        for a in range(8):
            self.assertIn(m.truth("MAJ3",a),(0,1))
            self.assertIn(m.truth("MUX3",a),(0,1))
        self.assertNotIn(tuple(m.truth("MAJ3",a) for a in range(8)),
                         [tuple(m.truth(l,a) for a in range(8)) for l in m.TRAIN_LAWS])

    def test_actions_are_available_to_all_policies(self):
        law, obs, pair=m.world(250001,"train")
        weights=m.posterior(obs)
        self.assertAlmostEqual(sum(weights),1.0)
        self.assertEqual(len(obs),m.N_PASSIVE)
        for p in m.POLICIES:
            _,_,steps,cost,acts=m.simulate(p,self.model,250001,"train",law,obs,pair)
            self.assertLessEqual(steps,m.MAX_PROBES)
            self.assertLessEqual(cost,m.MAX_PROBE_COST+1e-12)
            self.assertEqual(len(acts),steps)

    def test_exact_bayesian_value_and_entropy(self):
        _,obs,pair=m.world(250002,"train")
        weights=m.posterior(obs)
        for a in range(8):
            self.assertGreaterEqual(m.exact_gain(weights,pair,a,"bayes_value"),-1e-10)
            self.assertGreaterEqual(m.exact_gain(weights,pair,a,"bayes_eig"),-1e-10)

    def test_outcome_deterministic_common_random_numbers(self):
        law,obs,_=m.world(250003,"train")
        self.assertEqual(m.world(250003,"train")[1],obs)
        self.assertEqual(m.probe_outcomes(250003,"train",law,4,0),
                         m.probe_outcomes(250003,"train",law,4,0))
        self.assertEqual(len(m.probe_outcomes(250003,"train",law,4,0)),2)

    def test_no_inference_truth_argument(self):
        _,obs,pair=m.world(250004,"train")
        w=m.posterior(obs)
        for p in ("native","shuffled","trained_global","bayes_value","bayes_eig"):
            a=m.choose_probe(p,self.model,w,pair,250004,"train",0,0)
            self.assertTrue(a is None or 0<=a<=7)

    def test_sham_changes_scores(self):
        _,obs,pair=m.world(250005,"train")
        key=m.context(m.posterior(obs),pair,0)
        self.assertTrue(any(m.memory_estimate(self.model,key,a) !=
                            m.memory_estimate(self.model,key,a,negative=True)
                            for a in range(8)))

    def test_checkpoint_audit_and_source_isolation(self):
        audit=m.audit(self.model)
        self.assertTrue(all(audit.values()))
        self.assertEqual(self.model["worlds"],1024)


if __name__=="__main__":
    unittest.main()

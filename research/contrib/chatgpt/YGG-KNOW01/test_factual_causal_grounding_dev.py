"""KNOW11 development harness tests, no original-world/source-first-use."""
from fractions import Fraction
import unittest

from factual_causal_grounding_dev import (
    SEEDS, PHASE_P, canonical, digest, modes, subject, object_id,
    expected_outcome, witnessed_context, disclosed_interventions,
    exact_symbolic_fit, conventional_tree_fit, blind_fit, score)


class FakeFacts:
    def __init__(self, sources=None):
        self.records=set(sources or ())
    def fact(self,s,p,o):
        observed=(s,p,o) in self.records
        return {'classification': 'DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED'
                if observed else 'UNKNOWN_ABSTAIN',
                'witnessed':observed, 'native_accepted':False,
                'can_write_causal_consequence':False}


def known(seed=101, seed_index=0, phase=0):
    return FakeFacts({(subject(seed_index,i), PHASE_P[phase], object_id(phase,m))
                      for i,m in enumerate(modes(seed,phase))})

class FakeFittedNative:
    def predict(self,address,mode,action):
        return expected_outcome(address,mode,action)


class Know11Tests(unittest.TestCase):
    def test_frozen_seeds_and_balanced_contexts(self):
        self.assertEqual(SEEDS,(101,202,303))
        for seed in SEEDS:
            for phase in (0,1):
                roster=modes(seed,phase)
                self.assertEqual((len(roster),sum(roster)),(64,32))
                self.assertIn(0,roster[:32]);self.assertIn(1,roster[:32])

    def test_explicit_separate_action_consequence_law(self):
        for action in (0,1):
            for mode in (0,1):
                self.assertEqual(expected_outcome(0,mode,action),int(action==mode))
                self.assertEqual(expected_outcome(1,mode,action),int(action!=mode))
        with self.assertRaisesRegex(AssertionError,'ACTION_OUTCOME_DOMAIN'):
            expected_outcome(0,0,True)

    def test_unknown_context_abstains(self):
        self.assertIsNone(witnessed_context(FakeFacts(),subject(0,0),910))
        with self.assertRaisesRegex(AssertionError,'UNQUALIFIED_PREDICATE'):
            witnessed_context(FakeFacts(),subject(0,0),912)

    def test_conflicting_two_fact_context_abstains(self):
        s=subject(0,0)
        fs=FakeFacts({(s,910,object_id(0,0)),(s,910,object_id(0,1))})
        self.assertIsNone(witnessed_context(fs,s,910))

    def test_development_rows_use_only_fit_entities(self):
        fs=known()
        events=disclosed_interventions(fs,101,0,0)
        self.assertEqual(len(events),64)
        self.assertEqual(set((x[0],x[1]) for x in events),
                         {(0,0),(0,1),(1,0),(1,1)})
        self.assertTrue(all(all(type(v) is int for v in r) for r in events))

    def test_fully_trained_exact_symbolic_and_tree_tie(self):
        rows=disclosed_interventions(known(),101,0,0)
        symbolic=exact_symbolic_fit(rows)
        tree=conventional_tree_fit(rows)
        for mode in (0,1):
            for action in (0,1):
                self.assertEqual(symbolic[(mode,action)],Fraction(expected_outcome(0,mode,action)))
                self.assertEqual(tree(mode,action),symbolic[(mode,action)])

    def test_held_entity_comparison_prospective_no_label_in_fit(self):
        facts=known()
        rows=disclosed_interventions(facts,101,0,0)
        output=score(facts,101,0,0,FakeFittedNative(),0,
                     exact_symbolic_fit(rows),conventional_tree_fit(rows),blind_fit(rows))
        self.assertEqual(output['readout_count'],64)
        self.assertEqual(output['brier']['native'],[0,1])
        self.assertEqual(output['brier']['symbolic'],[0,1])
        self.assertEqual(output['brier']['conventional'],[0,1])
        self.assertEqual(output['brier']['facts_only'],[1,4])
        self.assertEqual(output['rewards']['native'],32)

    def test_public_shuffled_facts_without_valid_witness_fail_closed(self):
        facts=known()
        probe=subject(0,32)
        original=modes(101,0)[32]
        facts.records.remove((probe,910,object_id(0,original)))
        with self.assertRaisesRegex(AssertionError,'HELD_SOURCE_GROUNDING'):
            rows=disclosed_interventions(known(),101,0,0)
            score(facts,101,0,0,FakeFittedNative(),0,
                  exact_symbolic_fit(rows),conventional_tree_fit(rows),blind_fit(rows))

    def test_no_historical_or_real_checkpoint_mutation_methods(self):
        import factual_causal_grounding_dev as module
        for name in ('activate','deploy','merge','update_owner','modify_amalgam'):
            self.assertFalse(hasattr(module,name))

    def test_duplicate_and_canonical_hash(self):
        self.assertEqual(canonical({'b':1,'a':2}),b'{"a":2,"b":1}')
        self.assertEqual(digest(b'fixture'),__import__('hashlib').sha256(b'fixture').hexdigest())

if __name__=='__main__':
    unittest.main()

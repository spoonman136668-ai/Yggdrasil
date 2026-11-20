"""KNOW18 raw-four-bit query utility, negative source controls, no original image."""
import unittest
from fractions import Fraction
from raw_intervention_utility_dev import (
    TRAIN,HELD_SEEDS,SEEDS,ROLES,PREDICATES,PROBE,HELD,
    patterns,subject,object_id,source_rows,raw_properties,
    numeric_context,outcome,utility_from_witnesses,training_rows,
    symbolic,conventional_tree,attempt,choose_query
)
class FactsDouble:
    def __init__(self,mode="engineering_fixture_only",provenance="SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED"):
        self.rows={(q,p,o) for seed in SEEDS for q,p,o,ref in source_rows(seed)}
        self.mode=mode
        self.provenance=provenance
    def fact(self,q,p,o):
        present=(q,p,o) in self.rows
        return {"classification":"DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED" if present else "UNKNOWN_ABSTAIN",
                "witnessed":present,"source_mode":self.mode,"source_provenance":self.provenance,
                "native_accepted":False,"verified_new_real_knowledge":False,
                "can_write_causal_consequence":False}
class Know18Tests(unittest.TestCase):
    def test_frozen_seed_isolation(self):
        self.assertEqual(TRAIN,(2111,2221))
        self.assertEqual(HELD_SEEDS,(2333,2441,2551))
        self.assertEqual(len(set(SEEDS)),5)
        self.assertTrue(set(SEEDS).isdisjoint((1301,1403,1601,1709,1801)))
    def test_source_graph_independent_of_hidden_world_role(self):
        for seed in SEEDS:
            rows=source_rows(seed)
            self.assertEqual(len(rows),136)
            self.assertEqual(len({r[0] for r in rows}),34)
            self.assertEqual(len({r[2] for r in rows}),8)
            self.assertEqual(sorted(patterns(seed)[:16]),list(range(16)))
            self.assertEqual(sorted(patterns(seed)[18:]),list(range(16)))
            for k in ROLES:
                self.assertEqual(sum((p>>k)&1 for p in patterns(seed)),17)
                self.assertEqual(source_rows(seed),rows)
    def test_training_utility_requires_four_witnesses(self):
        facts=FactsDouble()
        A,nA=training_rows(facts,TRAIN[0])
        B,nB=training_rows(facts,TRAIN[1])
        self.assertEqual((nA,nB),(128,128))
        self.assertEqual((len(A),len(B)),(32,32))
        self.assertEqual({(p,a) for p,a,y in A},
                         {(p,a) for p in range(16) for a in (0,1)})
        for pattern,action,label in A+B:
            self.assertEqual(label,int(action==1 and pattern.bit_count()==2))
        with self.assertRaises(ValueError):utility_from_witnesses([0,1])
        with self.assertRaises(ValueError):utility_from_witnesses([0,0,0,True])
    def test_exact_symbolic_and_fully_fitted_tree(self):
        f=FactsDouble()
        fit=training_rows(f,TRAIN[0])[0]+training_rows(f,TRAIN[1])[0]
        exact=symbolic(fit);tree=conventional_tree(fit)
        for p in range(16):
            for a in (0,1):
                expected=Fraction(int(a==1 and p.bit_count()==2))
                self.assertEqual(exact[p,a],expected)
                self.assertEqual(tree(p,a),expected)
    def test_learned_initial_query_uses_raw_bits_not_balanced_feature(self):
        f=FactsDouble();s=HELD_SEEDS[0]
        exact=symbolic(training_rows(f,TRAIN[0])[0]+training_rows(f,TRAIN[1])[0])
        q=choose_query(f,s,ROLES,set(),lambda p,a:exact[p,a])
        self.assertIsNotNone(q)
        e,a=q
        self.assertEqual(a,1)
        self.assertEqual(numeric_context(raw_properties(f,s,e)).bit_count(),2)
    def test_transfer_outcomes_measured_not_fabricated(self):
        f=FactsDouble()
        exact=symbolic(training_rows(f,TRAIN[0])[0]+training_rows(f,TRAIN[1])[0])
        for seed in HELD_SEEDS:
            for role in ROLES:
                native=attempt(f,seed,role,lambda p,a:exact[p,a])
                oracle=attempt(f,seed,role,"oracle")
                self.assertEqual(native["witnessed_actions"],2)
                self.assertTrue(native["selected"] is None or native["selected"]==role)
                self.assertEqual(attempt(f,seed,role,"passive")["selected"],None)
                self.assertEqual(attempt(f,seed,role,"zero")["selected"],None)
                self.assertTrue(oracle["selected"] is None or oracle["selected"]==role)
    def test_missing_conflict_forged_qpq_abstain(self):
        f=FactsDouble();seed=HELD_SEEDS[0]
        ctx=raw_properties(f,seed,0)
        q=subject(seed,0);f.rows.remove((q,PREDICATES[0],object_id(0,ctx[0])))
        with self.assertRaisesRegex(ValueError,"MISSING_CONFLICTING_OR_FORGED_SOURCE"):
            raw_properties(f,seed,0)
        f.rows.add((q,PREDICATES[0],object_id(0,ctx[0])))
        f.rows.add((q,PREDICATES[0],object_id(0,1-ctx[0])))
        with self.assertRaisesRegex(ValueError,"MISSING_CONFLICTING_OR_FORGED_SOURCE"):
            raw_properties(f,seed,0)
        with self.assertRaisesRegex(ValueError,"MISSING_CONFLICTING_OR_FORGED_SOURCE"):
            raw_properties(FactsDouble(mode="claimed_owner"),seed,0)
        with self.assertRaisesRegex(ValueError,"MISSING_CONFLICTING_OR_FORGED_SOURCE"):
            raw_properties(FactsDouble(provenance="unverified_self_signed"),seed,0)
    def test_bad_input_types_and_untrained_policy(self):
        for invalid in (True,-1,34):
            with self.assertRaises(ValueError):subject(SEEDS[0],invalid)
        with self.assertRaises(ValueError):object_id(0,True)
        with self.assertRaises(ValueError):outcome(True,1)
        with self.assertRaises(ValueError):numeric_context((1,0,1,True))
        f=FactsDouble()
        self.assertIsNone(choose_query(f,HELD_SEEDS[0],ROLES,set(),lambda c,a:None))
    def test_no_control_plane_or_accepted_model_write(self):
        import raw_intervention_utility_dev as m
        for forbidden in ("activate","merge","deploy","controller",
                          "write_canonical","owner_train","schedule"):
            self.assertFalse(hasattr(m,forbidden))
if __name__=="__main__":unittest.main()

"""WSP117 first-use-safe calibration: all outcomes are synthetic fixtures only."""
from __future__ import annotations
import unittest
import numpy as np
import fixture

class RelationDiscoveryFixture(unittest.TestCase):
    def test_public_cohorts_and_source_reproducibility(self):
        self.assertEqual(len(fixture.PUBLIC_SEEDS),8)
        self.assertEqual(len(fixture.PROTECTED_SEEDS),64)
        self.assertTrue(set(fixture.PUBLIC_SEEDS).isdisjoint(fixture.PROTECTED_SEEDS))
        for seed in (117800,117863,117008,970100,True):
            with self.assertRaises((PermissionError,ValueError)):
                fixture.world(seed)
        a=fixture.world(117000)
        self.assertEqual(a.visible_edges_sha256(),fixture.world(117000).visible_edges_sha256())
        self.assertNotEqual(a.visible_edges_sha256(),fixture.world(117001).visible_edges_sha256())

    def test_operator_is_learned_from_public_observations_and_symbolic_tie(self):
        for seed in fixture.PUBLIC_SEEDS:
            world=fixture.world(seed)
            for op in ((0,1),(2,3),(4,0)):
                demos=fixture.find_identifiable_demonstrations(world,op)
                self.assertGreaterEqual(len(demos),1)
                self.assertLessEqual(len(demos),12)
                self.assertEqual(fixture.legal_operators(world,demos),(op,))
                direct=fixture.NumericDirectRelations().learn(world,demos)
                control=fixture.IndependentExactSymbolic(world,demos)
                self.assertEqual(direct.hypotheses(),control.possible)
                self.assertEqual(direct.w.shape,(6,6))
                self.assertEqual(direct.w.nbytes,144)
                used={s for s,_ in demos}
                unseen=[s for s in range(fixture.ENTITIES) if s not in used]
                self.assertGreaterEqual(len(unseen),52)
                for s in unseen[:16]:
                    self.assertEqual(direct.predict(world,s),world.compose(s,*op))
                    self.assertEqual(direct.predict(world,s),control.predict(world,s))
                cold=direct.cold()
                recovered=fixture.NumericDirectRelations.restore(cold)
                self.assertEqual(recovered.cold(),cold)
                self.assertEqual(recovered.predict(world,unseen[0]),direct.predict(world,unseen[0]))
                broken=bytearray(cold);broken[12]^=1
                with self.assertRaises(ValueError):
                    fixture.NumericDirectRelations.restore(bytes(broken))

    def test_nonidentifiable_laws_must_abstain(self):
        for seed in fixture.PUBLIC_SEEDS:
            w=fixture.world(seed)
            # These two laws are observationally identical on the lone public
            # demonstration but their predictions diverge on other sources.
            self.assertEqual(w.compose(0,0,4),w.compose(0,0,5))
            demos=fixture.evidence(w,(0,4),(0,))
            variants=fixture.legal_operators(w,demos)
            self.assertIn((0,4),variants)
            self.assertIn((0,5),variants)
            d=fixture.NumericDirectRelations().learn(w,demos)
            ctrl=fixture.IndependentExactSymbolic(w,demos)
            self.assertIsNone(d.predict(w,1))
            self.assertIsNone(ctrl.predict(w,1))
            self.assertGreaterEqual(len(d.hypotheses()),2)

    def test_examples_need_public_provenance_and_no_target_leakage(self):
        w=fixture.world(117000)
        for bad in ((),((0,1),(0,1)),((-1,2),),((0,64),)):
            with self.assertRaises(ValueError):
                fixture.legal_operators(w,bad)
        with self.assertRaises(ValueError):
            fixture.evidence(w,(6,0),(0,))
        with self.assertRaises(ValueError):
            w.compose(0,6,0)
        with self.assertRaises(ValueError):
            fixture.NumericDirectRelations.restore(b"W117"+b"123")

    def test_equal_data_control_is_not_misrepresented_as_agi(self):
        w=fixture.world(117002)
        direct=fixture.NumericDirectRelations().learn(w,fixture.evidence(w,(2,4),(0,1,2,3,4)))
        ctrl=fixture.IndependentExactSymbolic(w,fixture.evidence(w,(2,4),(0,1,2,3,4)))
        self.assertEqual(direct.hypotheses(),ctrl.possible)
        self.assertEqual(direct.predict(w,51),ctrl.predict(w,51))
        self.assertEqual(direct.observations,5)

if __name__=="__main__":unittest.main()

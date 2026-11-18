"""CKAD31 tests are source-only and never consume pilot/primary outcomes."""
import importlib.util
import itertools
import unittest
from pathlib import Path

HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location("ckad31_frozen",HERE/"campaign.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CKAD31Tests(unittest.TestCase):
    def test_guard_is_conservative_and_can_abstain(self):
        self.assertEqual(mod.gate(1.,1),1.)
        self.assertEqual(mod.gate(0.,0),0.)
        self.assertEqual(mod.gate(1.,0),0.5)
        self.assertEqual(mod.gate(0.,None),0.5)
        self.assertEqual(mod.gate(.5,1),.5)
        self.assertEqual(mod.gate(.5,None),.5)

    def test_source_entailment_only_when_identified(self):
        rows=[[0,0,1],[1,0,0]]
        pivots=mod.source_span(rows)
        self.assertEqual(mod.entailment(pivots,0),1)
        self.assertEqual(mod.entailment(pivots,1),0)
        self.assertIsNone(mod.entailment(pivots,31))
        self.assertEqual(len(pivots),2)

    def test_conflicting_public_witness_rejected(self):
        with self.assertRaises(ValueError):
            mod.source_span([[0,0,1],[0,0,0]])
        with self.assertRaises(ValueError):
            mod.source_span([[0,0,1],[0,0,1]])

    def test_all_degree2_world_source_consistency_without_primary(self):
        # Source-only synthetically generated fixture, not a held score.
        spec=(1,21,2,7)
        obs=[[x & 15,x >> 4,mod.outcome(spec,x)] for x in (0,1,2,3,4,6,7,8)]
        pivots=mod.source_span(obs)
        for c,a,y in obs:
            self.assertEqual(mod.entailment(pivots,c|(a<<4)),y)
        self.assertLessEqual(len(pivots),16)

    def test_pilot_stop_and_disjoint_primary(self):
        self.assertEqual(mod.PILOT,(9311,9322))
        self.assertEqual(mod.PRIMARY,(1311,1322,1333))
        self.assertFalse(set(mod.PILOT)&set(mod.PRIMARY))
        def case(seed,old=.25,raw=.30,gated=.25,cov=.05):
            return {"seed":seed,
                    "cold_restore_exact":True,
                    "old_primitive_retention_exact":True,
                    "local_quarantine_exact":True,
                    "coverage":{"native_guarded":cov},
                    "metrics":{"native_guarded":{"brier":gated},
                               "native_sparse":{"brier":raw},
                               "native_original":{"brier":old}}}
        self.assertEqual(mod.pilot_decision([case(9311),case(9322)]),
                         {"screen_go":False,"decision":"SCREEN_NO_GO"})
        self.assertTrue(mod.pilot_decision([
            case(9311,gated=.20,cov=.25),case(9322)
        ])["screen_go"])

    def test_public_graph_functions_on_boolean_inputs(self):
        for g in mod.GRAPHS:
            for bits in itertools.product((0,1),repeat=3):
                self.assertIn(mod.C30.composition(g,bits),(0,1))


if __name__=="__main__":
    unittest.main()

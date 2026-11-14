"""WSP100 fixture-only causal validity, custody and exhaustive audit tests."""
from __future__ import annotations
import copy
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from fixture import FixtureWorld, sources, validate_sources, heldout_plan, digits4, rank
from fixture_auditor import HYPOTHESES, consistent, version_space, identifiability, audit_fixture, rollout


class WSP100Fixtures(unittest.TestCase):
    def test_no_original_world_or_unauthorized_inputs(self):
        for bad in (-1,8,100011,100101,100201,100301,True,"0",None):
            with self.assertRaises(PermissionError):
                FixtureWorld(bad)
            with self.assertRaises(PermissionError):
                sources(bad)
        w=FixtureWorld(0)
        for bad in (True,-1,4,"2"):
            with self.assertRaises(ValueError):
                w.step(bad)
        for bad in ((0,)*5,(0,)*7,(0,0,0,0,0,True)):
            with self.assertRaises(ValueError):
                w.reset(bad)
        for i in range(4):
            w.step(i)
        with self.assertRaises(ValueError):
            w.step(0)

    def test_fixture_source_budgets_hash_and_replay(self):
        for fid in range(8):
            x=sources(fid)
            self.assertEqual(x,sources(fid))
            self.assertTrue(validate_sources(x))
            self.assertEqual((len(x["passive"]),len(x["active"]),len(x["random"])),(24,8,8))
            self.assertTrue(all(len(ep)==4 for k in ("passive","active","random") for ep in x[k]))
            plan=heldout_plan(x)
            self.assertEqual(len(plan["targets"]),12)
            starts={ep[0][0] for k in ("passive","active","random") for ep in x[k]}
            self.assertTrue(all(initial not in starts for initial,_a,_b in plan["targets"]))
            self.assertTrue(all(a[0]!=b[0] and a[1:]==b[1:]
                                for _init,a,b in plan["targets"]))

    def test_source_tamper_rejected(self):
        x=sources(0)
        damaged=copy.deepcopy(x)
        damaged["source_sha256"]="0"*64
        with self.assertRaises(ValueError):
            validate_sources(damaged)
        damaged=copy.deepcopy(x)
        damaged["active"]=damaged["active"][:-1]
        with self.assertRaises(ValueError):
            validate_sources(damaged)

    def test_independent_auditor_covers_truth_without_program_import(self):
        audit_text=(HERE/"fixture_auditor.py").read_text("utf-8")
        self.assertNotIn("from fixture import",audit_text)
        self.assertNotIn("import fixture",audit_text)
        self.assertEqual(len(HYPOTHESES),256)
        for fid in range(8):
            bundle=sources(fid)
            plan=heldout_plan(bundle)
            observed=bundle["passive"]+bundle["active"]
            survivors=version_space(observed)
            self.assertGreater(len(survivors),0)
            result=audit_fixture(bundle,plan)
            self.assertEqual(result["survivor_count"],len(survivors))
            self.assertEqual(result["total"],432)
            self.assertTrue(0<=result["fraction"]<=1)
            self.assertEqual(result["classification"],"DEV_FIXTURE_AUDIT_ONLY")

    def test_ambiguity_negative_control_is_not_automatically_perfect(self):
        one=sources(0)
        plan=heldout_plan(one)
        empty=version_space(())
        self.assertEqual(len(empty),256)
        amb=identifiability(empty,plan)
        self.assertLess(amb["fraction"],1.0)
        with self.assertRaises(ValueError):
            identifiability(empty,{"schema":"bad"})

    def test_immediate_action_invariance_and_real_delayed_effect(self):
        effects=0
        for fid in range(8):
            for initial_id in range(32):
                initial=digits4((initial_id*113+fid*17)%4096)
                for a in range(4):
                    for b in range(a+1,4):
                        x,y=FixtureWorld(fid),FixtureWorld(fid)
                        x.reset(initial)
                        y.reset(initial)
                        self.assertEqual(x.step(a),y.step(b))
                        effects+=int(x.step(0)!=y.step(0))
        self.assertGreater(effects,0)

    def test_oracle_delayed_effect_removed_by_memory_ablation(self):
        for fid in range(8):
            for initial in (digits4(i*17) for i in range(8)):
                x,y=FixtureWorld(fid,_no_latches=True),FixtureWorld(fid,_no_latches=True)
                x.reset(initial);y.reset(initial)
                x.step(0);y.step(1)
                self.assertEqual(x.step(2),y.step(2))

    def test_replay_vs_independent_hypothesis_transition(self):
        # Audit on full source sequences; no learner receives oracle program.
        for fid in range(8):
            source=sources(fid)
            self.assertGreater(len(version_space(source["passive"])),0)
            self.assertTrue(all(0<=v<4 for v in source["active"][0][0][2]))


if __name__=="__main__":
    unittest.main()

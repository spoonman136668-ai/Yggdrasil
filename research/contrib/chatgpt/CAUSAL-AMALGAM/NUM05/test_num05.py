"""NUM05 fixture-only engineering qualification. Registered DEV seeds forbidden."""
import json
import math
from pathlib import Path
import unittest

from num05 import (ACTIONS, SOURCE_TAG, Bank, NumericRegimeMemory, canonical,
                   digest, public_action, public_row, public_state, region,
                   error, target)
from num05_dev import (CellHistory, KNNHistory, RidgeHistory, ZeroPredictor,
                       source_rows, source_free_fixture, FIXTURE_SEED,
                       DEV_SEEDS, NULL_SEED)


def row(i, *, dx=0.0, dy=0.0, reward=0.0,
        before=(0.7, 0.7), action=0):
    after=(before[0] + dx, before[1] + dy)
    return public_row(digest(("num05-manual-fixture-"+str(i)).encode()),
                      before, action, after, reward)


class NUM05NumericCausalFixtureTests(unittest.TestCase):
    def test_01_source_first_prereg_and_no_external_first_use(self):
        p=json.loads(Path(__file__).with_name("prereg.json").read_text())
        self.assertEqual(p["id"],"NUM05")
        self.assertEqual(p["parent"]["owner_pr"],1278)
        self.assertEqual(p["parent"]["sha"],
                         "86264b41a08d49f558418c0fba367f3a2636befa")
        self.assertEqual(p["fixed_source"]["development_seeds"],[520117,520131])
        self.assertFalse(p["authority"]["source_owner_426_protected_first_use"])
        self.assertFalse(p["authority"]["accepted_model_mutation"])
        self.assertEqual(p["fixed_source"]["phase_clock"],[0,160,320,416])
        self.assertEqual(p["fixed_source"]["budgets"]["max_banks"],2)

    def test_02_all_five_actions_accepted_exactly_no_binary_truncation(self):
        self.assertEqual(ACTIONS,5)
        for action in range(5):
            self.assertEqual(public_action(action),action)
            self.assertEqual(row(action,action=action)["action"],action)
        for bad in (-1,5,True,False,2.0,"2",None,{},[]):
            with self.assertRaises(ValueError):
                public_action(bad)

    def test_03_public_numeric_state_and_reward_exact(self):
        self.assertEqual(public_state([1.25,-.875]),(1.25,-.875))
        x=row(0,dx=.375,dy=-.25,reward=-.125)
        z=target(x)
        self.assertAlmostEqual(z[0],.375)
        self.assertAlmostEqual(z[1],-.25)
        self.assertEqual(z[2],-.125)
        self.assertAlmostEqual(error(z,z),0)
        for bad in (None,0,[0],[[0,1]],[0,1,2],[True,0],
                    [0,float("inf")],[float("nan"),0],[0,11],["1",0]):
            with self.assertRaises(ValueError):
                public_state(bad)
        with self.assertRaises(ValueError):
            public_row("a"*64,[0,1],0,[0,1],float("nan"))
        with self.assertRaises(ValueError):
            public_row("a"*64,[0,1],0,[0,1],True)

    def test_04_provenance_and_flags_refuse_fabricated_source_claim(self):
        for bad_source in ("MetaHighwayEnv","MHE01",None,"original",True):
            with self.assertRaises(ValueError):
                public_row("a"*64,[0.,1.],1,[.1,1.],.1,
                           source_tag=bad_source)
        for bad_id in ("a"*63,"A"*64,"z"*64,1,None,True):
            with self.assertRaises(ValueError):
                public_row(bad_id,[0,1],0,[0,1],0)
        with self.assertRaises(ValueError):
            public_row("a"*64,[0,1],0,[0,1],0,terminated=1)
        self.assertEqual(row(1)["source_tag"],SOURCE_TAG)

    def test_05_public_quadrant_covers_four_nonoracle_regions(self):
        expected=[(-1.,-1.),(1.,-1.),(-1.,1.),(1.,1.)]
        self.assertEqual([region(x) for x in expected],[0,1,2,3])
        self.assertEqual(region((0.,0.)),3)

    def test_06_prequential_train_save_restore_never_fabricates_outcomes(self):
        m=NumericRegimeMemory()
        before=m.forecast([.8,.8],4)
        self.assertEqual(before,[0.,0.,0.])
        r=row(9,dx=.4,dy=.2,reward=.6,action=4)
        self.assertEqual(m.observe(r),before)
        for actual, expected in zip(m.forecast([.8,.8],4),(.2,.1,.3)):
            self.assertAlmostEqual(actual,expected)
        source_rows_before=len(m.rows)
        raw=m.checkpoint()
        second=NumericRegimeMemory.restore(raw,digest(raw))
        self.assertEqual(second.checkpoint(),raw)
        self.assertEqual(second.forecast([.8,.8],4),m.forecast([.8,.8],4))
        self.assertEqual(source_rows_before,len(m.rows))
        self.assertEqual(len(second.rows),1)
        self.assertFalse(m.info()["native_admission"])
        self.assertFalse(m.info()["source_owner_authenticated"])

    def test_07_duplicate_or_forged_outcome_rejected(self):
        m=NumericRegimeMemory()
        first=row(0)
        m.observe(first)
        prior=m.checkpoint()
        with self.assertRaisesRegex(ValueError,"NUM05_DUPLICATE_OR_REORDERED_ID"):
            m.observe(first)
        altered=dict(first)
        altered["reward"]=1.
        with self.assertRaises(ValueError):
            m.observe(altered)
        forged=dict(row(1))
        forged["source_owner_authenticated"]=True
        with self.assertRaisesRegex(ValueError,"NUM05_ROW_SCHEMA"):
            m.observe(forged)
        self.assertEqual(prior,m.checkpoint())

    def test_08_candidate_archive_freezes_old_bank_on_confirmed_contradiction(self):
        m=NumericRegimeMemory()
        for i in range(110):
            m.observe(row(i))
        old_hash=m.info()["old_bank_sha256"]
        for i in range(110,113):
            m.observe(row(i,dx=1.,dy=-1.,reward=1.))
        self.assertEqual(m.info()["bank_count"],2)
        self.assertEqual(m.info()["active"],1)
        self.assertEqual(old_hash,m.info()["old_bank_sha256"])
        self.assertEqual(m.info()["mode_switches"],[[113,1]])
        self.assertEqual(len(m.rows),113)

    def test_09_phase_blind_return_chooses_retained_old_bank(self):
        m=NumericRegimeMemory()
        for i in range(110):
            m.observe(row(i))
        for i in range(110,125):
            m.observe(row(i,dx=1.,dy=-1.,reward=1.))
        self.assertEqual(m.info()["active"],1)
        archived=m.info()["old_bank_sha256"]
        restored=NumericRegimeMemory.restore(m.checkpoint(),digest(m.checkpoint()))
        self.assertEqual(restored.info()["old_bank_sha256"],archived)
        for i in range(125,128):
            m.observe(row(i))
        self.assertEqual(m.info()["active"],0)
        self.assertEqual(m.info()["bank_count"],2)
        self.assertEqual(m.info()["mode_switches"][-1],[128,0])
        final=NumericRegimeMemory.restore(m.checkpoint(),digest(m.checkpoint()))
        self.assertEqual(final.checkpoint(),m.checkpoint())

    def test_10_no_archive_ablation_retains_exactly_one_bank(self):
        m=NumericRegimeMemory(single_bank=True)
        for i in range(110):
            m.observe(row(i))
        for i in range(110,125):
            m.observe(row(i,dx=1.,dy=-1.,reward=1.))
        self.assertEqual(m.info()["bank_count"],1)
        self.assertEqual(m.info()["active"],0)
        self.assertEqual(m.info()["mode_switches"],[])
        with self.assertRaises(ValueError):
            NumericRegimeMemory(single_bank=1)

    def test_11_checkpoint_wrong_sha_tampered_state_and_format_fail_closed(self):
        m=NumericRegimeMemory()
        for i in range(30):
            m.observe(row(i,dx=.1*i/30.,reward=.2))
        raw=m.checkpoint()
        with self.assertRaisesRegex(ValueError,"NUM05_CHECKPOINT_SHA"):
            NumericRegimeMemory.restore(raw,"f"*64)
        corrupted=json.loads(raw)
        corrupted["native_admission"]=True
        bad=canonical(corrupted)
        with self.assertRaises(ValueError):
            NumericRegimeMemory.restore(bad,digest(bad))
        corrupted=json.loads(raw)
        corrupted["banks"][0]["3:0"][1][0]+=1.
        bad=canonical(corrupted)
        with self.assertRaisesRegex(ValueError,"NUM05_CHECKPOINT_REPLAY_MISMATCH"):
            NumericRegimeMemory.restore(bad,digest(bad))

    def test_12_bounded_ledger_capacity_and_no_secret_learner_fields(self):
        m=NumericRegimeMemory()
        for i in range(512):
            m.observe(row(i))
        self.assertEqual(len(m.rows),512)
        with self.assertRaisesRegex(ValueError,"NUM05_EVIDENCE_CAPACITY"):
            m.observe(row(513))
        d=json.loads(m.checkpoint())
        for k in ("source_owner_authenticated","native_admission","scientific_pass"):
            self.assertIs(d[k],False)
        self.assertNotIn("true_phase",json.dumps(d))
        self.assertNotIn("weather",json.dumps(d))

    def test_13_all_fitted_same_evidence_baselines_are_prequential(self):
        seq=[row(i,dx=.25+0.01*i,dy=.15,reward=.3,action=i%5)
             for i in range(30)]
        controls=(CellHistory(),CellHistory(window=10),
                  KNNHistory(),KNNHistory(window=10),RidgeHistory(),ZeroPredictor())
        for control in controls:
            self.assertEqual(control.predict([.7,.7],0),[0.,0.,0.])
            for event in seq:
                pred=control.predict(event["observation"],event["action"])
                self.assertTrue(all(math.isfinite(z) for z in pred))
                control.observe(event)
            self.assertTrue(all(math.isfinite(z) for z in
                                control.predict([.7,.7],0)))

    def test_14_fixture_only_source_and_no_reserved_seed_partial_use(self):
        fixture=source_free_fixture()
        self.assertTrue(fixture["pass"])
        self.assertEqual(fixture["fixture_rows"],80)
        self.assertEqual(len(fixture["archive_sha256"]),64)
        for used in DEV_SEEDS + (NULL_SEED,):
            with self.assertRaisesRegex(ValueError,"REGISTERED_SEED_PARTIAL_USE"):
                list(source_rows(used,count=80))

    def test_15_no_external_source_or_native_owner_code_import(self):
        script=(Path(__file__).with_name("num05.py").read_text()+
                Path(__file__).with_name("num05_dev.py").read_text())
        for forbidden in ("import gymnasium","import highway_env",
                          "import yggdrasil","from yggdrasil",
                          "requests","subprocess","native.observe_experience(",
                          "import torch","from transformers"):
            self.assertNotIn(forbidden,script)
        self.assertEqual(SOURCE_TAG,"num05.synthetic-public-dev.v1")

    def test_16_preprimary_source_precision_exact_public_six_decimal_grid(self):
        from num05_dev import source_rows
        fixture=list(source_rows(FIXTURE_SEED,null=True,count=80))
        self.assertEqual(len(fixture),80)
        for row in fixture:
            self.assertEqual(row["source_tag"], SOURCE_TAG)
            for v in (row["observation"] + row["successor"] + [row["reward"]]):
                self.assertAlmostEqual(v,round(v,6),places=11)
        self.assertTrue(all(row["action"]==i%5 for i,row in enumerate(fixture)))



if __name__ == "__main__":
    unittest.main()

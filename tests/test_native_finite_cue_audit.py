"""CUE-02 native public-domain verification, source fences, negative controls."""
import importlib.util
import inspect
import pathlib
import re
import subprocess
import sys
import unittest

from yggdrasil.native_cumulative_action_bank import NativeCumulativeActionBank
from yggdrasil.native_finite_cue_audit import (
    ALL_PUBLIC_PROBES, MAX_PUBLIC_PROBES, BUDGET_SWEEP,
    audit,probe_order,
)

ROOT=pathlib.Path(__file__).resolve().parents[1]
DEV=ROOT/"research/contrib/chatgpt/CUE-02/dev.py"
spec=importlib.util.spec_from_file_location("cue02_tests_evaluator",DEV)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class NativeFiniteCueAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank,cls.models,cls.public_sha=m.fixture.build_bank()

    def test_native_auditor_has_no_source_or_world_identity(self):
        self.assertEqual(tuple(inspect.signature(audit).parameters),
                         ("bank","public_cues"))
        s=pathlib.Path(inspect.getsourcefile(audit)).read_text()
        for forbidden in ("import study","import fixture","import world",
                          "true_step","world_id","hidden_mask",
                          "source_id","env.intervene"):
            self.assertNotRegex(s,r"\b"+re.escape(forbidden)+r"\b")

    def test_source_domains_exhaustive_and_unique(self):
        self.assertEqual(MAX_PUBLIC_PROBES,32)
        self.assertEqual(len(ALL_PUBLIC_PROBES),32)
        self.assertEqual(len(set(ALL_PUBLIC_PROBES)),32)
        self.assertEqual(ALL_PUBLIC_PROBES[0],(0,0))
        self.assertEqual(ALL_PUBLIC_PROBES[-1],(15,1))

    def test_predeclared_budget_high_to_low(self):
        self.assertEqual(BUDGET_SWEEP,(32,24,16,12,8))

    def test_deterministic_all_policies(self):
        for p in ("dense","lex","hash"):
            order=probe_order(p)
            self.assertEqual(order,probe_order(p))
            self.assertEqual(set(order),set(ALL_PUBLIC_PROBES))
            self.assertEqual(len(order),32)
        with self.assertRaisesRegex(ValueError,"UNKNOWN_POLICY"):
            probe_order("oracle")

    def test_dense_order_prefers_complex_inputs_but_no_source(self):
        dense=probe_order("dense")
        self.assertEqual(dense[0],(15,1))
        self.assertEqual(dense[-1],(0,0))

    def test_empty_bank_never_claims_a_world(self):
        d=audit(NativeCumulativeActionBank(),())
        self.assertEqual(d["classification"],"NO_STORED_RELATIONS_ABSTAIN")
        self.assertIsNone(d["candidate_slot"])
        self.assertFalse(d["safe_to_activate_accepted_model"])

    def test_partial_empty_observations_uncertain(self):
        r=audit(self.bank,[])
        self.assertEqual(r["public_observations"],0)
        self.assertEqual(len(r["compatible_slots"]),12)
        self.assertFalse(r["full_domain_observed"])
        self.assertFalse(r["source_identity_authenticated"])

    def test_beyond_full_domain_capacity_rejected(self):
        bad=[[x,a,0] for x,a in ALL_PUBLIC_PROBES]+[[0,0,1]]
        with self.assertRaisesRegex(ValueError,"PROBE_BUDGET"):
            audit(self.bank,bad)

    def test_duplicate_public_probe_rejected_even_conflicting(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            audit(self.bank,[(0,0,0),(0,0,1)])

    def test_untyped_nonpublic_hidden_cues_rejected(self):
        bad=(
          [(0,0,True)],[(0,0,2)],[(True,0,0)],[(0,True,0)],
          [(16,0,0)],[(0,4,0)],[(0,0,0,"private_id")],
          [{"context":0,"hidden":1}],[("world-id",1,0)],
        )
        for cues in bad:
            with self.subTest(cues=cues),self.assertRaises(ValueError):
                audit(self.bank,cues)

    def test_native_bank_type_rejected(self):
        with self.assertRaisesRegex(ValueError,"BANK_REQUIRED"):
            audit({},[])

    def test_partial_one_match_is_never_certificate(self):
        env=m.fixture.study.ComputationalEnvironment(0)
        cues=[(x,a,env.intervene(x,a)) for x,a in probe_order("dense")[:31]]
        v=m.one_audit(self.bank,self.models,cues)
        self.assertEqual(v["candidate_slot"],0)
        self.assertFalse(v["full_domain_observed"])
        self.assertFalse(v["observational_equivalence_only"])
        self.assertFalse(v["source_identity_authenticated"])

    def test_full_observation_matches_only_observable_law_not_source(self):
        env=m.fixture.study.ComputationalEnvironment(0)
        cues=[(x,a,env.intervene(x,a)) for x,a in ALL_PUBLIC_PROBES]
        x=m.one_audit(self.bank,self.models,cues)
        self.assertEqual(x["candidate_slot"],0)
        self.assertEqual(x["classification"],
            "COMPLETE_DOMAIN_OBSERVATIONAL_EQUIVALENCE_NOT_AUTHENTICITY")
        self.assertTrue(x["observational_equivalence_only"])
        self.assertFalse(x["source_identity_authenticated"])
        self.assertFalse(x["native_accepted"])

    def test_outside_family_fails_full_domain_compatibility(self):
        for i in range(4):
            cues=[(x,a,m.fixture.unknown_outcome(i,x,a))
                  for x,a in probe_order("dense")]
            v=m.one_audit(self.bank,self.models,cues)
            self.assertEqual(v["compatible_slots"],[])
            self.assertEqual(v["classification"],
                             "FALSIFIED_ALL_STORED_RELATIONS")

    def test_constructive_31_step_identical_observation_witness(self):
        order=probe_order("dense")
        for slot in range(12):
            model=self.models[slot]
            cues=[(x,a,model.predict(x,a)["public_outcome"])
                  for x,a in order]
            fake=list(cues)
            x,a,y=fake[-1];fake[-1]=(x,a,1-y)
            self.assertEqual(m.one_audit(self.bank,self.models,cues[:31]),
                             m.one_audit(self.bank,self.models,fake[:31]))
            self.assertFalse(audit(self.bank,cues[:31])["full_domain_observed"])
            self.assertEqual(audit(self.bank,cues)["candidate_slot"],slot)
            self.assertNotEqual(audit(self.bank,fake)["candidate_slot"],slot)

    def test_bank_bytes_unchanged_by_all_audits(self):
        before=self.bank.checkpoint()
        for p in ("dense","lex","hash"):
            cues=[(x,a,m.fixture.unknown_outcome(0,x,a))
                  for x,a in probe_order(p)]
            audit(self.bank,cues)
        self.assertEqual(self.bank.checkpoint(),before)

    def test_cold_replay_same_32_probe_decision(self):
        restored=NativeCumulativeActionBank.restore(self.bank.checkpoint(),
                                                      self.bank.checkpoint_sha256)
        env=m.fixture.study.ComputationalEnvironment(1)
        cues=[(x,a,env.intervene(x,a)) for x,a in probe_order("dense")]
        self.assertEqual(audit(self.bank,cues),audit(restored,cues))

    def test_no_protected_science_first_use(self):
        x=subprocess.run([sys.executable,str(DEV),"--primary"],
                         capture_output=True,text=True)
        self.assertNotEqual(x.returncode,0)
        self.assertIn("CUE02 SCIENTIFIC FIRST USE DISARMED",x.stderr)

    def test_full_frozen_source_screen_and_controls(self):
        receipt=m.evaluate()
        self.assertEqual(receipt["known_source_worlds"],12)
        self.assertEqual(receipt["nonresident_nonlinear_worlds"],4)
        self.assertEqual(receipt["complete_31_of_32_indistinguishable_witnesses"],12)
        self.assertEqual(receipt["independent_scientific_first_use"],0)
        self.assertTrue(all(receipt["frozen_gates"].values()))
        self.assertFalse(receipt["accepted_main_changed"])

if __name__=="__main__":
    unittest.main()

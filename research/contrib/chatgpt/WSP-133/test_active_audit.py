"""WSP133 R2 original-source-safe 16+16 budgeted causal challenger qualification."""
from __future__ import annotations
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
import json
import source as S
import learner as N
import controls as C
import experiment as E

class BoundedCausalAuditTests(TestCase):
    def test_full_96_world_original_prospective_source_safe_R2(self):
        r=E.run_engineering()
        print("WSP133_FINAL_ENGINEERING_JSON="+S.canon(r))
        self.assertFalse(r["scientific_pass"])
        self.assertFalse(r["native_admission"])
        self.assertFalse(r["original_first_use"])
        self.assertTrue(r["independent_exact_symbolic_action_and_decision_parity"])
        self.assertTrue(r["original_warm_weights_unchanged"])
        self.assertTrue(r["cold_replay_all_worlds"])
        self.assertEqual(r["repair_attempt"],2)
        self.assertEqual(r["repair_attempt_max"],3)
        self.assertEqual(r["warm_paid_actions_per_arm"],8192)
        self.assertEqual(r["source_target_worlds"],{"known":64,"shear":32})
        self.assertEqual(r["source_paid_actions_per_arm"],3072)
        self.assertEqual(r["source_paid_actions_per_world_per_arm"],32)
        self.assertEqual(r["paired_R2_R1_known_bootstrap"]["seed"],133)
        self.assertEqual(r["paired_R2_R1_known_bootstrap"]["resamples"],10000)
        for kind,worlds in (("known",64),("shear",32)):
            for arm in E.ARMS:
                score=r["world_scores"][kind][arm]
                self.assertEqual(score["held"],worlds*224)
                self.assertEqual(score["source_calls"],worlds*32)
            self.assertEqual(r["world_scores"][kind]["R2_ACTIVE_NUMERIC"],
                             r["world_scores"][kind]["R2_INDEPENDENT_EXACT_SYMBOLIC"])
            self.assertEqual(r["world_scores"][kind]["R1_FROZEN_NUMERIC"],
                             r["world_scores"][kind]["R1_INDEPENDENT_EXACT_SYMBOLIC"])
        for arm in E.ARMS:
            self.assertEqual(r["transfer_relabel"][arm]["source_calls"],0)
            self.assertEqual(r["transfer_relabel"][arm]["held"],4096)
        self.assertIn(r["status"],(
            "DEVELOPMENT_REPAIR_R2_SUPPORTED_WITHIN_SUPPLIED_PERMUTATION_PLUS_SHEAR",
            "DEVELOPMENT_REPAIR_R2_NO_GO"))
        self.assertEqual(r["resource"]["whole_process_energy"],"UNQUALIFIED")

    def test_protected_unregistered_sources_denied_before_rng(self):
        self.assertFalse(S.ALLOWED&S.DENIED)
        with patch.object(S.random,"Random",side_effect=AssertionError(
                "WSP133_PROTECTED_RNG_WAS_USED")):
            for seed in (131000,131063,131800,131863,135800,135863,
                         138800,138863,148800,148863,150800,150863,
                         154800,154863,155800,155863,156000,156063,
                         160800,161800,162800,165000,165063,166000,166031,
                         167000,167015,168999,169064,169999,170032,
                         170999,171016,172000,172063,True,-1,"169000"):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):S.world(seed)
                    with self.assertRaises(PermissionError):S.open_original(seed)
        self.assertNotIn("source",N.__dict__)
        self.assertNotIn("source",C.__dict__)
        self.assertNotIn("learner",C.__dict__)

    def test_truly_disjoint_prospective_shear_family(self):
        self.assertEqual(len(S.ALLOWED),112)
        self.assertEqual(len(N.PERMS),720)
        self.assertEqual(len(N.SHEARS),30)
        self.assertEqual(N.TOTAL,22320)
        self.assertEqual(len(S.S._origins()),64)
        for seed in (169000,169063,170000,170031,171000,171015):
            v=S.world(seed)
            self.assertEqual(len(v.records),256)
            self.assertFalse(hasattr(v,"condition"))
            self.assertFalse(hasattr(v,"shear"))
            self.assertFalse(hasattr(v,"permutation"))
            self.assertEqual(v.cohort,"transfer" if 171000<=seed<171016 else "probe")
        for seed in (170000,170012,170031):
            truth=bytes(S._truth(seed))
            prior=S.S.P._law(S.S._origins()[seed-170000])["truth"]
            pure={bytes(prior[S.S._permute(x,p)] for x in range(256))
                  for p in S.PERMS}
            self.assertNotIn(truth,pure)

    def test_small_source_blind_active_policy_and_tamper_negative(self):
        class FakeView:
            seed=199991
            law_id=3
            cohort="probe"
            legal=frozenset(range(256))
            def subject(self,x):return x
            def input(self,s):return s
            def fingerprint(self):return "unit-source-fingerprint"
        class Prior:
            def infer(self,v,x):
                return (x&43).bit_count()%2
        v=FakeView()
        original=Prior()
        numeric=N.ActiveCausalAudit(original,E.N131.NativeBinder)
        symbolic=C.IndependentAuditedSymbolic(original)
        available=set(range(256))
        receipt=N.digest([v.fingerprint(),"begin"])
        # The source law is the old parity under a known hidden permutation.
        pure=N.PERMS[19]
        for k in range(32):
            x=numeric.choose(v,available)
            y=symbolic.choose(v,available)
            self.assertEqual(x,y)
            self.assertIn(x,available)
            available.remove(x)
            bit=original.infer(v,N._permuted(x,pure))
            row=[v.seed,v.law_id,x,x,bit]
            receipt=N.digest([receipt,row])
            evidence=SimpleNamespace(seed=v.seed,law_id=v.law_id,
                                     subject=x,input=x,effect=bit,receipt=receipt)
            numeric.observe(v,evidence)
            symbolic.observe(v,evidence)
        self.assertIsNone(numeric.choose(v,available))
        self.assertEqual(numeric.count(v),symbolic.count(v))
        for x in range(256):
            self.assertEqual(numeric.infer(v,x),symbolic.infer(v,x))
        frozen=numeric.snapshot()
        restored=N.ActiveCausalAudit.restore(original,E.N131.NativeBinder,
                                             frozen,lambda seed:v)
        self.assertEqual(restored.snapshot(),frozen)
        forged=json.loads(frozen)
        st=next(iter(forged["payload"]["states"].values()))
        st["candidate_weights_hex"]=hex(int(st["candidate_weights_hex"],16)^1)
        with self.assertRaisesRegex(ValueError,"WSP133_SNAPSHOT_DIGEST_INVALID"):
            N.ActiveCausalAudit.restore(original,E.N131.NativeBinder,
                                        S.canon(forged),lambda seed:v)
        forged["sha256"]=N.digest(forged["payload"])
        with self.assertRaisesRegex(ValueError,"WSP133_FORGED_NUMERICAL_WEIGHTS"):
            N.ActiveCausalAudit.restore(original,E.N131.NativeBinder,
                                        S.canon(forged),lambda seed:v)

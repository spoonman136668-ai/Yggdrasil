"""WSP130 full preregistered source-safe development and negative controls."""
from __future__ import annotations
import json
from unittest import TestCase
from unittest.mock import patch
import source as S
import learner as N
import controls as C
import experiment as E

class StructuralInductionTests(TestCase):
    def test_full_144_world_frozen_source_safe_study(self):
        x=E.run_engineering()
        print("WSP130_FINAL_ENGINEERING_JSON="+S.canon(x))
        self.assertFalse(x["scientific_pass"])
        self.assertFalse(x["original_first_use"])
        self.assertFalse(x["native_admission"])
        self.assertFalse(x["universal_source_safety_proven"])
        self.assertTrue(x["grammar_supplied"])
        self.assertTrue(x["same_evidence_symbolic_exact_parity"])
        self.assertTrue(x["cold_state_replay"])
        self.assertTrue(x["retention_after_interference"])
        self.assertEqual(x["source_actions_per_arm"],18432)
        self.assertEqual(x["condition_counts"],
                         {"none":32,"quartic":32,"quintic":32,
                          "double":32,"stealth":16})
        self.assertEqual(x["paired_bootstrap"]["resamples"],10000)
        self.assertEqual(x["paired_bootstrap"]["seed"],130)
        self.assertGreaterEqual(x["stealth_confident_wrong"],1)
        self.assertGreaterEqual(x["stealth_worlds_with_confident_wrong"],1)
        for mode in E.MODES:
            for arm in E.ARMS:
                z=x["scores"][mode][arm]
                self.assertEqual(z["held"],x["condition_counts"][mode]*128)
                self.assertEqual(z["source_calls"],x["condition_counts"][mode]*128)
            self.assertEqual(x["scores"][mode]["DIRECT_NUMERIC"],
                             x["scores"][mode]["SAME_ACTION_EXACT_SYMBOLIC"])
        for arm in E.ARMS:
            self.assertEqual(x["transfer"][arm]["held"],8192)
            self.assertEqual(x["transfer"][arm]["source_calls"],0)
        self.assertIn(x["status"],(
           "DEVELOPMENT_MIXED_WITHIN_SUPPLIED_ANF_FAMILY","DEVELOPMENT_NO_GO"))
        self.assertEqual(x["strong_conventional_trained_baseline"],
                         "UNQUALIFIED_NOT_RUN")

    def test_protected_sources_rejected_before_rng(self):
        self.assertFalse(S.ALLOWED&S.DENIED)
        with patch.object(S.random,"Random",side_effect=AssertionError(
                "WSP130_PROTECTED_GENERATION_MUST_NOT_RUN")):
            for seed in (131000,131063,131800,131863,135800,135863,
                         138800,138863,148800,148863,150800,150863,
                         154800,154863,155800,155863,156000,156063,
                         153999,154128,154499,154516,155032,True,-1,
                         "154000"):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError): S.world(seed)
                    with self.assertRaises(PermissionError): S.open_original(seed)

    def test_exact_orthogonal_hidden_relationships_and_custody(self):
        self.assertEqual(len(S.LOW),93)
        self.assertEqual(len(S.CORE),9)
        self.assertEqual(len(S.HASH_AUDIT),154)
        self.assertEqual(len(set(S.LOW+S.CORE+S.HASH_AUDIT)),256)
        self.assertEqual(len(S.MASKS4),70)
        self.assertEqual(len(S.MASKS5),56)
        modes=S._modes()
        self.assertEqual({kind:modes.count(kind) for kind in E.MODES[:4]},
                         {"none":32,"quartic":32,"quintic":32,"double":32})
        for law in range(144):
            truth=S._law(law)
            if truth["mode"]=="quartic":
                self.assertEqual(truth["high"][0].bit_count(),4)
            elif truth["mode"]=="quintic":
                self.assertEqual(truth["high"][0].bit_count(),5)
            elif truth["mode"]=="double":
                self.assertEqual(len(truth["high"]),2)
                self.assertNotEqual(*truth["high"])
            elif truth["mode"]=="stealth":
                self.assertIn(truth["stealth_target"],
                              set(range(256))-set(S.LOW+S.CORE+S.HASH_AUDIT[:26]))
            else:
                self.assertEqual(truth["high"],())
        self.assertNotIn("source",N.__dict__)
        self.assertNotIn("source",C.__dict__)
        self.assertNotIn("learner",C.__dict__)

    def test_cold_checkpoint_rejects_recomputed_digest_forgery(self):
        view=S.world(154002)
        m=N.DirectInducer()
        c=S.Custodian(view)
        available=set(view.legal)
        for _ in range(128):
            action=m.choose(view,available)
            self.assertIn(action,available)
            available.remove(action)
            m.observe(view,c.query(action))
        self.assertIsNone(m.choose(view,available))
        with self.assertRaises(PermissionError):
            c.query(next(iter(available)))
        with self.assertRaises(ValueError):
            c.score_once({})
        frozen=m.snapshot()
        restored=N.DirectInducer.restore(frozen,S.world)
        self.assertEqual(restored.snapshot(),frozen)
        tampered=json.loads(frozen)
        state=next(iter(tampered["payload"]["states"].values()))
        state["low_coeff_bits_hex"]=hex(int(state["low_coeff_bits_hex"],16)^1)
        with self.assertRaisesRegex(ValueError,"WSP130_SNAPSHOT_DIGEST_INVALID"):
            N.DirectInducer.restore(S.canon(tampered),S.world)
        tampered["sha256"]=N._digest(tampered["payload"])
        with self.assertRaisesRegex(ValueError,"WSP130_FORGED_LEARNED_NUMERICAL_WEIGHTS"):
            N.DirectInducer.restore(S.canon(tampered),S.world)

    def test_stealth_impossibility_source_blind_witness(self):
        for law in range(128,144):
            source=S._law(law)
            self.assertEqual(source["mode"],"stealth")
            target=source["stealth_target"]
            self.assertNotIn(target,set(S.LOW+S.CORE+S.HASH_AUDIT[:26]))
            for x in range(256):
                old=sum((x&low)==low for low in source["coefs"])%2
                self.assertEqual(source["truth"][x],
                                 old^int(x==target))
        for seed in (155000,155031):
            view=S.world(seed)
            self.assertEqual(view.cohort,"transfer")
            self.assertFalse(view.legal)
            zero=S.Custodian(view)
            self.assertEqual(zero.budget,0)
            with self.assertRaises(PermissionError):
                zero.query(view.records[0][0])

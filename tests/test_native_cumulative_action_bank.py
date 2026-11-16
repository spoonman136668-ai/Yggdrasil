"""NKR-12 true-native bank tests; all source worlds reused from NKR-11 DEV."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
import unittest

from yggdrasil.native_cumulative_action_bank import NativeCumulativeActionBank
from yggdrasil.native_intervention_repair import (
    NativeInterventionRepair, canonical, digest,
)
from yggdrasil.public_causal_cells import PublicCausalCells

SCRIPT = (Path(__file__).resolve().parents[1] /
          "research/contrib/chatgpt/NKR-11/experiment.py")
spec = importlib.util.spec_from_file_location("nkr12_tests_reused_fixture", SCRIPT)
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)
DEV = (Path(__file__).resolve().parents[1] /
       "research/contrib/chatgpt/NKR-12/dev.py")


def warm(world_id, source=None):
    env=study.ComputationalEnvironment(world_id)
    rows=study.collect_warmup(env)
    raw=study.evidence(source or f"warm-bundle-world-{world_id:02d}",rows)
    return env,rows,raw


def repaired(bank, world_id, address, retained=False):
    env=study.ComputationalEnvironment(world_id)
    rows=study.collect_paired_interventions(env)
    raw=study.evidence(f"repair-bundle-world-{world_id:02d}",rows)
    return bank.repair_public(address,raw,digest(raw),retained=retained),raw


class CumulativeBankTests(unittest.TestCase):
    def test_empty_cold_and_absence_abstains(self):
        b=NativeCumulativeActionBank()
        self.assertEqual(b.stored_slots,())
        self.assertEqual(b.prior(0,0,0),None)
        p=b.predict(0,0,0)
        self.assertEqual(p["classification"],"UNKNOWN_ABSTAIN")
        self.assertIsNone(p["public_outcome"])
        self.assertFalse(p["native_accepted"])
        self.assertEqual(
            NativeCumulativeActionBank.restore(
                b.checkpoint(),b.checkpoint_sha256
            ).checkpoint(),b.checkpoint())

    def test_install_public_source_only_and_immutable(self):
        b=NativeCumulativeActionBank()
        env,rows,raw=warm(0)
        next_,receipt=b.install_public(0,raw,digest(raw))
        self.assertEqual(b.stored_slots,())
        self.assertEqual(next_.stored_slots,(0,))
        self.assertEqual(next_.prior(0,0,1),1)
        self.assertFalse(receipt["native_accepted"])
        self.assertEqual(next_.checkpoint(),next_.checkpoint())

    def test_duplicate_slot_install_fails_closed(self):
        _,_,raw=warm(0)
        b,_=NativeCumulativeActionBank().install_public(0,raw,digest(raw))
        with self.assertRaisesRegex(ValueError,"ALREADY_OCCUPIED"):
            b.install_public(0,raw,digest(raw))

    def test_global_warm_source_rebind_is_denied(self):
        _,_,raw=warm(0)
        b,_=NativeCumulativeActionBank().install_public(0,raw,digest(raw))
        with self.assertRaisesRegex(ValueError,"SOURCE_OR_EVIDENCE_REBOUND"):
            b.install_public(1,raw,digest(raw))

    def test_global_observation_ref_rebind_is_denied(self):
        _,rows,raw=warm(0)
        b,_=NativeCumulativeActionBank().install_public(0,raw,digest(raw))
        other=study.evidence("other-source-world-zero",rows)
        with self.assertRaisesRegex(ValueError,"SOURCE_OR_EVIDENCE_REBOUND"):
            b.install_public(1,other,digest(other))

    def test_wrong_source_kind_or_tampered_sha_fails(self):
        _,_,raw=warm(0)
        obj=json.loads(raw.decode("ascii"))
        obj["source_kind"]="predicted_consequence"
        other=canonical(obj)
        with self.assertRaises(PermissionError):
            NativeCumulativeActionBank().install_public(0,other,digest(other))
        with self.assertRaises(ValueError):
            NativeCumulativeActionBank().install_public(0,raw,"0"*64)

    def test_cannot_repair_missing_slot(self):
        env=study.ComputationalEnvironment(0)
        raw=study.evidence("repair-bundle-world-00",study.collect_paired_interventions(env))
        with self.assertRaisesRegex(ValueError,"UNKNOWN_SLOT"):
            NativeCumulativeActionBank().repair_public(0,raw,digest(raw))

    def test_atomic_repair_does_not_modify_original(self):
        _,_,raw=warm(0)
        original,_=NativeCumulativeActionBank().install_public(0,raw,digest(raw))
        before=original.checkpoint()
        (next_,receipt),repair= repaired(original,0,0)
        self.assertEqual(before,original.checkpoint())
        self.assertNotEqual(next_.checkpoint(),before)
        self.assertEqual(next_.prior(0,0,1),1)
        self.assertEqual(next_.predict(0,0,1)["public_outcome"],0)
        self.assertFalse(receipt["scientific_pass"])

    def test_exact_same_repair_is_idempotent(self):
        _,_,raw=warm(0)
        b,_=NativeCumulativeActionBank().install_public(0,raw,digest(raw))
        (changed,_),repair=repaired(b,0,0)
        returned,receipt=changed.repair_public(0,repair,digest(repair))
        self.assertIs(returned,changed)
        self.assertEqual(receipt["new_events"],0)
        self.assertEqual(changed.checkpoint(),returned.checkpoint())

    def test_different_repair_after_single_epoch_denied(self):
        _,_,raw=warm(0)
        b,_=NativeCumulativeActionBank().install_public(0,raw,digest(raw))
        (changed,_),repair=repaired(b,0,0)
        tamper=json.loads(repair.decode("ascii"))
        tamper["source_id"]="new-repeat-repair-world-00"
        other=canonical(tamper)
        with self.assertRaises(PermissionError):
            changed.repair_public(0,other,digest(other))

    def test_retained_native_slot_matches_canonical_address(self):
        _,_,raw=warm(0)
        b,_=NativeCumulativeActionBank().install_public(0,raw,digest(raw),retained=True)
        self.assertEqual(b.stored_slots,(7,))
        self.assertEqual(b.prior(0,0,1,retained=True),1)
        self.assertIsNone(b.prior(0,0,1))
        with self.assertRaises(ValueError):
            b.prior(9,0,1)
        with self.assertRaises(ValueError):
            b.prior(9,0,1,retained=True)

    def test_cold_digest_tamper_fails_closed(self):
        _,_,raw=warm(0)
        b,_=NativeCumulativeActionBank().install_public(0,raw,digest(raw))
        snapshot=b.checkpoint()
        with self.assertRaises(ValueError):
            NativeCumulativeActionBank.restore(snapshot,"0"*64)
        doc=json.loads(snapshot)
        doc["data"]["slots"][0][2]="invalid"
        corrupt=canonical(doc)
        with self.assertRaises(ValueError):
            NativeCumulativeActionBank.restore(corrupt,digest(corrupt))

    def test_forged_acceptance_flag_always_denied(self):
        _,_,raw=warm(0)
        b,_=NativeCumulativeActionBank().install_public(0,raw,digest(raw))
        doc=json.loads(b.checkpoint())
        doc["data"]["scientific_pass"]=True
        doc["sha256"]=digest(canonical(doc["data"]))
        payload=canonical(doc)
        with self.assertRaises(ValueError):
            NativeCumulativeActionBank.restore(payload,digest(payload))

    def test_member_checkpoint_mutation_never_accepted(self):
        _,_,raw=warm(0)
        b,_=NativeCumulativeActionBank().install_public(0,raw,digest(raw))
        doc=json.loads(b.checkpoint())
        raw_member=json.loads(doc["data"]["slots"][0][2])
        raw_member["accepted_native"]=True
        newraw=canonical(raw_member)
        doc["data"]["slots"][0][1]=digest(newraw)
        doc["data"]["slots"][0][2]=newraw.decode("ascii")
        doc["sha256"]=digest(canonical(doc["data"]))
        output=canonical(doc)
        with self.assertRaises(ValueError):
            NativeCumulativeActionBank.restore(output,digest(output))

    def test_strict_capacity_sixteen_slots_and_overflow(self):
        bank=NativeCumulativeActionBank()
        _,rows,_=warm(0)
        for slot in range(16):
            clone=[(f"clone-{slot:02d}-{i:02d}",x,a,y)
                   for i,(_,x,a,y) in enumerate(rows)]
            raw=study.evidence(f"clone-source-{slot:02d}",clone)
            addr=slot if slot<7 else slot-7
            bank,_=bank.install_public(addr,raw,digest(raw),retained=slot>=7)
        self.assertEqual(bank.stored_slots,tuple(range(16)))
        self.assertLessEqual(bank.checkpoint_bytes,262144)
        restored=NativeCumulativeActionBank.restore(bank.checkpoint(),bank.checkpoint_sha256)
        self.assertEqual(bank.checkpoint(),restored.checkpoint())
        extra=study.evidence("clone-source-overflow",clone)
        with self.assertRaises(ValueError):
            bank.install_public(7,extra,digest(extra))

    def test_legacy_ypc1_bytes_unchanged(self):
        old=PublicCausalCells().snapshot()
        _,_,raw=warm(0)
        bank,_=NativeCumulativeActionBank().install_public(0,raw,digest(raw))
        (bank,_),_=repaired(bank,0,0)
        NativeCumulativeActionBank.restore(bank.checkpoint(),bank.checkpoint_sha256)
        self.assertEqual(PublicCausalCells().snapshot(),old)
        self.assertEqual(len(old),164)

    def test_reused_twelve_worlds_full_cold_return_and_reference_tie(self):
        spec=importlib.util.spec_from_file_location("nkr12_dev_test",DEV)
        m=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        x=m.run()
        self.assertEqual(x["warm_correct"],384)
        self.assertEqual(x["cold_correct"],192)
        self.assertEqual(x["fully_fit_symbolic_correct"],192)
        self.assertEqual(x["independent_reference_equal_predictions"],192)
        self.assertEqual(x["loaded_slots"],12)
        self.assertTrue(x["legacy_ypc1_unchanged"])
        self.assertEqual(x["scientific_first_use_consumed"],0)

    def test_protected_first_use_denied(self):
        p=subprocess.run([sys.executable,str(DEV),"--primary"],
                         capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn("NKR12 SCIENTIFIC FIRST USE DISARMED",p.stderr)


if __name__=="__main__":unittest.main()

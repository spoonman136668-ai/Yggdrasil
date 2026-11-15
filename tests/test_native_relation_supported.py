"""NKR03 frozen fabricated public-only evidence support and novelty controls."""
import hashlib
import unittest

from yggdrasil.native_relation_memory import NativeRelationMemory
from yggdrasil.public_causal_cells import PublicCausalCells

from pathlib import Path
import sys

SOURCE_DIR = Path(__file__).resolve().parent.parent / "research/contrib/chatgpt/NKR-03"
sys.path.insert(0, str(SOURCE_DIR))
from source import TRAIN, AUDIT, UNAUDITED, PAIR_TERMS, TRIPLE_TERMS, law


def fitted(slot,family):
    cells=PublicCausalCells()
    bank=NativeRelationMemory()
    ret=slot>=7
    addr=slot-7 if ret else slot
    for context in TRAIN:
        for action in (0,1):
            effect=law(slot,context,action,family)
            cells.observe(addr,action,effect,retained=ret)
            assert bank.observe_public(addr,context,action,effect,
                                       f"nkr03:{slot}:{context}:{action}",
                                       retained=ret)
    v1=bank.checkpoint()
    for context in AUDIT:
        for action in (0,1):
            effect=law(slot,context,action,family)
            cells.observe(addr,action,effect,retained=ret)
            assert bank.observe_public_verified(addr,context,action,effect,
                  f"nkr03:audit:{slot}:{context}:{action}",retained=ret)
    return cells,bank,v1


class NKR03EvidenceTests(unittest.TestCase):
    def test_frozen_contexts_and_novel_laws_indistinguishable_on_singletons(self):
        self.assertEqual(len(TRAIN),5)
        self.assertEqual(len(AUDIT),6)
        self.assertEqual(len(UNAUDITED),5)
        self.assertEqual(set(TRAIN)&set(AUDIT),set())
        self.assertEqual(set(AUDIT)&set(UNAUDITED),set())
        self.assertEqual(set(AUDIT)|set(UNAUDITED),set(range(16))-set(TRAIN))
        for slot in range(16):
            for family in ("quadratic","cubic"):
                for context in TRAIN:
                    h=hashlib.sha256(f"NKR03|fresh|20261115|{family}|{slot}".encode()).digest()
                    expected=((context&(h[0]&15)).bit_count()&1)^(h[1]&1)
                    self.assertEqual(law(slot,context,0,family),expected)

    def test_96_source_supported_pair_decisions_per_family_no_80_unsupported_claims(self):
        for family in ("quadratic","cubic"):
            supported_correct=0
            unsupported=0
            for slot in range(16):
                cells,bank,_=fitted(slot,family)
                ret=slot>=7
                addr=slot-7 if ret else slot
                self.assertEqual(bank.unique_observations,22)
                for context in AUDIT:
                    pair=bank.observed_action_pair(addr,context,retained=ret)
                    self.assertEqual(pair,(law(slot,context,0,family),
                                            law(slot,context,1,family)))
                    chosen=cells.choose_verified_contextual(addr,context,bank,
                                                            retained=ret)
                    supported_correct+=law(slot,context,chosen,family)
                for context in UNAUDITED:
                    self.assertIsNone(bank.observed_action_pair(
                        addr,context,retained=ret))
                    self.assertEqual(cells.choose_verified_contextual(
                        addr,context,bank,retained=ret),
                        cells.choose(addr,retained=ret))
                    unsupported+=1
            self.assertEqual(supported_correct,96)
            self.assertEqual(unsupported,80)

    def test_legacy_checkpoint_v1_preserved_and_novel_exception_v2_roundtrip(self):
        # Quadratic family has an interaction that is absent in singleton
        # training and will conflict with the frozen affine 10-feature writer.
        observed_exceptions=0
        for slot in range(16):
            cells,bank,base=fitted(slot,"quadratic")
            ret=slot>=7
            addr=slot-7 if ret else slot
            original=NativeRelationMemory.restore(base)
            self.assertEqual(original.checkpoint(),base)
            self.assertEqual(original.verified_exception_count,0)
            observed_exceptions+=bank.verified_exception_count
            frozen=cells.snapshot()
            self.assertEqual(len(frozen),164)
            self.assertEqual(PublicCausalCells.restore(frozen).snapshot(),frozen)
            saved=bank.checkpoint()
            cold=NativeRelationMemory.restore(saved)
            self.assertEqual(cold.checkpoint(),saved)
            self.assertEqual(cold.unique_observations,22)
            for context in AUDIT+UNAUDITED:
                self.assertEqual(cells.choose_verified_contextual(
                    addr,context,bank,retained=ret),
                    cells.choose_verified_contextual(addr,context,cold,retained=ret))
        self.assertGreater(observed_exceptions,0)

    def test_alias_dedup_and_conflict_do_not_change_state(self):
        cells,bank,_=fitted(0,"quadratic")
        old=bank.checkpoint()
        for context in TRAIN+AUDIT:
            for action in (0,1):
                outcome=law(0,context,action,"quadratic")
                self.assertFalse(bank.observe_public_verified(
                    0,context,action,outcome,"new:source:alias"))
                self.assertFalse(bank.observe_public(
                    0,context,action,outcome,"duplicate:base"))
                self.assertEqual(bank.checkpoint(),old)
                with self.assertRaises(ValueError):
                    bank.observe_public_verified(0,context,action,1-outcome,
                                                 "conflict:verified")
                self.assertEqual(bank.checkpoint(),old)
        self.assertEqual(bank.unique_observations,22)
        self.assertEqual(cells.choose_verified_contextual(0,3,bank),
                         cells.choose_verified_contextual(
                             0,3,NativeRelationMemory.restore(old)))
        self.assertEqual(cells.snapshot(),PublicCausalCells.restore(cells.snapshot()).snapshot())

    def test_checkpoint_tamper_and_bounded_bad_inputs(self):
        _,bank,_=fitted(0,"quadratic")
        checkpoint=bank.checkpoint()
        changed=bytearray(checkpoint)
        changed[-50]^=1
        for value in (bytes(changed),checkpoint[:-1],bytearray(checkpoint),
                      b"{}",b"X"*160001):
            with self.subTest(kind=type(value),size=len(value)):
                with self.assertRaises(ValueError):
                    NativeRelationMemory.restore(value)
        for bad in ((0,-1,0,1,"source"),(0,16,0,1,"source"),
                    (0,3,2,1,"source"),(0,3,0,2,"source"),
                    (0,3,0,1,""),(7,3,0,1,"source")):
            with self.assertRaises(ValueError):
                bank.observe_public_verified(*bad)
            self.assertEqual(bank.checkpoint(),checkpoint)

    def test_unaudited_context_is_never_model_qualified_and_legacy_untouched(self):
        for family in ("quadratic","cubic"):
            cells,bank,_=fitted(0,family)
            legacy=cells.snapshot()
            for ctx in UNAUDITED:
                self.assertIsNone(bank.observed_action_pair(0,ctx))
                self.assertEqual(cells.choose_verified_contextual(0,ctx,bank),
                                 cells.choose(0))
            with self.assertRaises(ValueError):
                cells.choose_verified_contextual(0,3,None)
            self.assertEqual(cells.snapshot(),legacy)


if __name__=="__main__":
    unittest.main()

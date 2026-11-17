"""WSP155 complete-witness 6->5 intervention projection tests; fixtures only."""
from __future__ import annotations
import json
import unittest

from yggdrasil.native_evidence_compiler import canonical_json,digest
from yggdrasil.native_relation_memory import NativeRelationMemory
from yggdrasil.public_causal_cells import PublicCausalCells
from yggdrasil.native_sixbit_projection import (
    SCHEMA, stage_sixbit_do_bundle
)

def fixture(*,slot=0,action_bit=5,nuisance_bit=4,source_id=None):
    cb=tuple(i for i in range(6) if i not in (action_bit,nuisance_bit))
    def values(mask):
        context=sum(((mask>>i)&1)<<k for k,i in enumerate(cb))
        action=(mask>>action_bit)&1
        # Conditioned on four bits plus executed do action; nonlinear in
        # the context, independent of nuisance. Never use an answer oracle.
        effect=action ^ (context&1) ^ (((context>>1)&1)&((context>>2)&1)) ^ (slot&1)
        return context,action,effect
    d={"schema":SCHEMA,"source_id":source_id or "wsp155-fixture-slot-"+str(slot),
       "source_mode":"engineering_fixture_only",
       "source_kind":"observed_public_intervention",
       "license":"synthetic-fixture",
       "slot":slot,"action_bit":action_bit,"nuisance_bit":nuisance_bit,
       "records":[[x,values(x)[2],"observed_do","w155:observed:"+str(x)]
                  for x in range(64)]}
    return d,values

def stage(doc,*,prior_checkpoint=None):
    raw=canonical_json(doc)
    return stage_sixbit_do_bundle(raw,digest(raw),
                                  prior_checkpoint=prior_checkpoint)

class NativeSixBitProjectionTests(unittest.TestCase):
    def test_01_exact_64_witnesses_into_32_native_programmed_weights(self):
        doc,values=fixture()
        candidate=stage(doc)
        receipt=candidate.receipt
        self.assertEqual(receipt["charged_do_witnesses"],64)
        self.assertEqual(receipt["native_observations"],32)
        self.assertEqual(receipt["invariance_comparisons"],32)
        self.assertEqual(receipt["projection_bits"],
                         {"action":5,"nuisance":4,"context":(0,1,2,3)})
        self.assertEqual(receipt["native_receipt"]["total_native_observations"],32)
        self.assertFalse(receipt["scientific_pass"])
        self.assertFalse(receipt["native_admission"])
        self.assertFalse(receipt["accepted_main_mutated"])
        self.assertFalse(receipt["source_first_use"])
        self.assertEqual(receipt["candidate_checkpoint_sha256"],
                         digest(candidate.checkpoint))
        memory=NativeRelationMemory.restore(candidate.checkpoint)
        incumbent=PublicCausalCells()
        legacy=incumbent.snapshot()
        self.assertEqual(len(legacy),164)
        for context in range(16):
            # Independent original source lookup for *both* nuisance values.
            effects={}
            for action in (0,1):
                x=context+(action<<5)
                x_alt=x|(1<<4)
                self.assertEqual(values(x)[2],values(x_alt)[2])
                effects[action]=values(x)[2]
            expected=0 if effects[0]>effects[1] else 1
            self.assertEqual(memory.observed_action_pair(0,context),
                             (effects[0],effects[1]))
            self.assertEqual(incumbent.choose_verified_contextual(
                0,context,memory),expected)
            self.assertEqual(effects[expected],1)
        self.assertEqual(incumbent.snapshot(),legacy)
        self.assertEqual(memory.checkpoint(),candidate.checkpoint)

    def test_02_configurable_bit_roles_and_retained_native_slot(self):
        for slot,action_bit,nuisance_bit in ((12,4,5),(6,0,5),(7,3,2)):
            doc,values=fixture(slot=slot,action_bit=action_bit,
                               nuisance_bit=nuisance_bit)
            candidate=stage(doc)
            memory=NativeRelationMemory.restore(candidate.checkpoint)
            incumbent=PublicCausalCells()
            loc=slot-7 if slot>=7 else slot
            for ctx in range(16):
                for act in (0,1):
                    x=(act<<action_bit)|sum(
                        ((ctx>>k)&1)<<i for k,i in enumerate(
                            v for v in range(6) if v not in (action_bit,nuisance_bit)))
                    self.assertEqual(memory.observed_action_pair(
                        loc,ctx,retained=slot>=7)[act],values(x)[2])
                chosen=incumbent.choose_verified_contextual(
                    loc,ctx,memory,retained=slot>=7)
                self.assertIn(chosen,(0,1))

    def test_03_a_single_nuisance_dependent_effect_rejects_all(self):
        doc,_=fixture()
        original=stage(doc)
        tampered,_=fixture()
        # Same four-bit context & do action, other nuisance value now differs.
        tampered["records"][16][1]^=1
        with self.assertRaisesRegex(ValueError,
                                    "WSP155_NUISANCE_DEPENDENCE_UNREPRESENTABLE"):
            stage(tampered,prior_checkpoint=original.checkpoint)
        self.assertEqual(NativeRelationMemory.restore(
            original.checkpoint).checkpoint(),original.checkpoint)

    def test_04_no_missing_replayed_or_unpaid_effects(self):
        doc,_=fixture()
        for mutate in ("missing","extra","replay","wrong-do","duplicate-ref"):
            b=json.loads(canonical_json(doc))
            if mutate=="missing":b["records"].pop()
            elif mutate=="extra":b["records"].append(b["records"][-1])
            elif mutate=="replay":b["records"][4][0]=3
            elif mutate=="wrong-do":b["records"][0][2]="passive"
            else:b["records"][5][3]=b["records"][4][3]
            with self.subTest(mutate=mutate):
                with self.assertRaises(ValueError):stage(b)

    def test_05_source_and_role_types_fail_closed(self):
        original,_=fixture()
        bads=[
            ("slot",16),("slot",True),("action_bit",6),
            ("action_bit",True),("nuisance_bit",-1),
            ("nuisance_bit",5),("source_id","not valid source"),
        ]
        for name,val in bads:
            b=json.loads(canonical_json(original))
            b[name]=val
            with self.subTest(field=name,value=val):
                with self.assertRaises(ValueError):stage(b)
        for k,v in (("source_mode","owner_qualified"),
                    ("source_kind","knowledge_graph_triple"),
                    ("source_kind","counterfactual"),
                    ("license","unknown")):
            b=json.loads(canonical_json(original))
            b[k]=v
            with self.subTest(key=k):
                with self.assertRaises(PermissionError):stage(b)

    def test_06_canonical_pin_and_provenance_attacks_rejected(self):
        doc,_=fixture()
        raw=canonical_json(doc)
        with self.assertRaisesRegex(ValueError,"WSP155_SOURCE_PIN_MISMATCH"):
            stage_sixbit_do_bundle(raw,"0"*64)
        with self.assertRaisesRegex(ValueError,"WSP155_NONCANONICAL_SOURCE"):
            stage_sixbit_do_bundle(
                json.dumps(doc,indent=2).encode("ascii"),
                digest(json.dumps(doc,indent=2).encode("ascii")))
        duplicate=raw.replace(b'"license":"synthetic-fixture",',
                              b'"license":"synthetic-fixture","license":"synthetic-fixture",')
        with self.assertRaisesRegex(ValueError,"WSP155_DOCUMENT_INVALID"):
            stage_sixbit_do_bundle(duplicate,digest(duplicate))
        b=json.loads(raw)
        b["records"][3][1]=True
        with self.assertRaises(ValueError):stage(b)
        b=json.loads(raw)
        b["records"][2][3]="bad\nref"
        with self.assertRaises(ValueError):stage(b)

    def test_07_prior_checkpoint_cold_restore_and_idempotence(self):
        doc,_=fixture(slot=0)
        first=stage(doc)
        duplicate=stage(doc,prior_checkpoint=first.checkpoint)
        self.assertEqual(duplicate.checkpoint,first.checkpoint)
        self.assertEqual(duplicate.receipt["native_receipt"]["unique_added"],0)
        self.assertEqual(duplicate.receipt["native_receipt"]["duplicates_ignored"],32)
        second_doc,_=fixture(slot=7)
        later=stage(second_doc,prior_checkpoint=first.checkpoint)
        memory=NativeRelationMemory.restore(later.checkpoint)
        self.assertEqual(memory.unique_observations,64)
        self.assertEqual(memory.checkpoint(),later.checkpoint)
        self.assertEqual(NativeRelationMemory.restore(
            first.checkpoint).checkpoint(),first.checkpoint)
        bad=bytearray(first.checkpoint)
        bad[-5]^=1
        with self.assertRaises(ValueError):
            stage(doc,prior_checkpoint=bytes(bad))

    def test_08_source_free_capacity_and_no_state_injection(self):
        doc,_=fixture(slot=15)
        out=stage(doc)
        self.assertEqual(out.receipt["native_receipt"]["populated_native_slots"],1)
        self.assertEqual(out.receipt["native_receipt"]["total_native_observations"],32)
        self.assertEqual(out.receipt["native_receipt"]["source_authenticity"],
                         "UNVERIFIED_EXACT_BYTES_ONLY")
        self.assertEqual(out.receipt["source_authenticity"],
                         "UNVERIFIED_EXACT_BYTES_ONLY")
        self.assertEqual(stage(doc).checkpoint,out.checkpoint)
        self.assertEqual(stage(doc).receipt,out.receipt)
        self.assertEqual(out.receipt["native_receipt"]["source_first_use"],False)

if __name__=="__main__":
    unittest.main()

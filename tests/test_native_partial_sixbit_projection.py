"""WSP156: complete source-safe partial-witness and native persistence checks."""
import importlib.util
import json
from pathlib import Path
import unittest

from yggdrasil.native_evidence_compiler import canonical_json,digest
from yggdrasil.native_partial_sixbit_projection import (
    SCHEMA,stage_partial_sixbit_bundle
)
from yggdrasil.native_relation_memory import NativeRelationMemory
from yggdrasil.public_causal_cells import PublicCausalCells

ROOT=Path(__file__).resolve().parents[1]
DEV=ROOT/"research"/"contrib"/"chatgpt"/"WSP-156"/"development.py"
spec=importlib.util.spec_from_file_location("_wsp156_sourcefree_development",DEV)
D=importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)

def stage(doc,*,prior=None):
    raw=canonical_json(doc)
    return stage_partial_sixbit_bundle(raw,digest(raw),prior_checkpoint=prior)

def custom(slot=12,action_bit=0,nuisance_bit=5):
    bits=tuple(i for i in range(6) if i not in (action_bit,nuisance_bit))
    rows=[]
    for context in range(8):
        for action in (0,1):
            for nuisance in (0,1):
                mask=(action<<action_bit)|(nuisance<<nuisance_bit)
                mask|=sum(((context>>j)&1)<<v for j,v in enumerate(bits))
                effect=action ^ (context&1) ^ (slot&1)
                rows.append([mask,effect,"observed_do","w156:custom:"+str(slot)+":"+str(mask)])
    rows.sort(key=lambda x:x[0])
    return {"schema":SCHEMA,"source_id":"w156-custom-"+str(slot),
            "source_mode":"engineering_fixture_only",
            "source_kind":"observed_public_intervention","license":"synthetic-fixture",
            "slot":slot,"action_bit":action_bit,"nuisance_bit":nuisance_bit,
            "records":rows}

class PartialNativeWitnessTests(unittest.TestCase):
    def test_01_paid32_programs_eight_verified_contexts_only(self):
        doc=D.make_doc(2,"paired")
        self.assertEqual(len(doc["records"]),32)
        native=stage(doc)
        sym=D.independent_symbolic(doc)
        self.assertFalse(sym["rejected"])
        self.assertEqual(native.verified_actions,sym["decisions"])
        self.assertEqual(native.receipt["charged_do_effects"],32)
        self.assertEqual(native.receipt["certified_native_observations"],16)
        self.assertEqual(native.receipt["verified_non_tied_actions"],8)
        self.assertEqual(native.receipt["both_actions_witnessed_contexts"],8)
        self.assertEqual(native.receipt["single_nuisance_observations"],0)
        self.assertEqual(native.receipt["unobserved_native_coordinates"],16)
        self.assertEqual(sum(x is None for x in native.verified_actions),8)
        self.assertFalse(native.receipt["science_pass"])
        self.assertFalse(native.receipt["native_admission"])
        self.assertFalse(native.receipt["source_first_use"])
        self.assertFalse(native.receipt["accepted_main_mutated"])
        self.assertEqual(digest(native.checkpoint),native.receipt["candidate_checkpoint_sha256"])
        self.assertEqual(NativeRelationMemory.restore(
            native.checkpoint).checkpoint(),native.checkpoint)

    def test_02_single_nuisance_variants_never_certify_a_context(self):
        doc=D.make_doc(3,"fixed_balanced")
        doc["records"]=[[x,D._private_fixture_effect(3,x),"observed_do",
                         "w156:single:"+str(x)] for x in range(16)]
        doc["records"]+= [[x,D._private_fixture_effect(3,x),"observed_do",
                          "w156:single:"+str(x)] for x in range(32,48)]
        out=stage(doc)
        self.assertEqual(out.receipt["charged_do_effects"],32)
        self.assertEqual(out.receipt["certified_native_observations"],0)
        self.assertEqual(out.receipt["single_nuisance_observations"],32)
        self.assertEqual(out.verified_actions,(None,)*16)
        self.assertEqual(NativeRelationMemory.restore(
            out.checkpoint).unique_observations,0)

    def test_03_one_missing_partner_abstains_and_never_infers(self):
        doc=D.make_doc(0,"fixed_balanced")
        doc["records"].pop(0)
        out=stage(doc)
        self.assertEqual(out.receipt["charged_do_effects"],31)
        self.assertEqual(out.receipt["certified_native_observations"],15)
        self.assertEqual(out.receipt["single_nuisance_observations"],1)
        self.assertEqual(out.receipt["verified_non_tied_actions"],7)
        self.assertIsNone(out.choose_certified(0))
        with self.assertRaises(ValueError):out.choose_certified(True)
        with self.assertRaises(ValueError):out.choose_certified(16)

    def test_04_observed_contradiction_refuses_atomic_checkpoint(self):
        doc=D.make_doc(0,"fixed_balanced")
        valid=stage(doc)
        tampered=json.loads(canonical_json(doc))
        # Raw mask=16 is nuisance sibling of mask=0.
        for row in tampered["records"]:
            if row[0]==16:row[1]^=1
        with self.assertRaisesRegex(ValueError,
                                    "WSP156_WITNESSED_NUISANCE_CONTRADICTION"):
            stage(tampered,prior=valid.checkpoint)
        self.assertEqual(NativeRelationMemory.restore(
            valid.checkpoint).checkpoint(),valid.checkpoint)

    def test_05_prior_conflict_duplication_and_incremental_cold(self):
        first_doc=D.make_doc(2,"fixed_balanced")
        first=stage(first_doc)
        repeated=stage(first_doc,prior=first.checkpoint)
        self.assertEqual(first.checkpoint,repeated.checkpoint)
        self.assertEqual(repeated.receipt["native_receipt"]["unique_added"],0)
        self.assertEqual(repeated.receipt["native_receipt"]["duplicates_ignored"],16)
        second_doc=D.make_doc(2,"paired")
        continued=stage(second_doc,prior=first.checkpoint)
        restored=NativeRelationMemory.restore(continued.checkpoint)
        self.assertGreaterEqual(restored.unique_observations,16)
        self.assertLessEqual(restored.unique_observations,32)
        self.assertEqual(restored.checkpoint(),continued.checkpoint)
        # New source certificates never use additional prior-only contexts.
        self.assertEqual(continued.verified_actions,
                         D.independent_symbolic(second_doc)["decisions"])
        conflicting=json.loads(canonical_json(first_doc))
        for row in conflicting["records"]:
            if row[0] in (0,16):row[1]^=1
        with self.assertRaises(ValueError):
            stage(conflicting,prior=first.checkpoint)
        self.assertEqual(NativeRelationMemory.restore(
            first.checkpoint).checkpoint(),first.checkpoint)

    def test_06_source_trust_types_pin_order_and_duplicate_ref(self):
        doc=D.make_doc(0,"fixed_balanced")
        raw=canonical_json(doc)
        with self.assertRaisesRegex(ValueError,"WSP156_SOURCE_PIN_MISMATCH"):
            stage_partial_sixbit_bundle(raw,"0"*64)
        pretty=json.dumps(doc,indent=2).encode("ascii")
        with self.assertRaisesRegex(ValueError,"WSP156_NONCANONICAL_SOURCE"):
            stage_partial_sixbit_bundle(pretty,digest(pretty))
        repeated=raw.replace(b'"license":"synthetic-fixture",',
                             b'"license":"synthetic-fixture","license":"synthetic-fixture",')
        with self.assertRaises(ValueError):
            stage_partial_sixbit_bundle(repeated,digest(repeated))
        for field,value in (("slot",16),("slot",True),("action_bit",6),
                            ("action_bit",True),("nuisance_bit",-1),
                            ("nuisance_bit",5),("source_id","white space")):
            bad=json.loads(raw);bad[field]=value
            with self.subTest(field=field):
                with self.assertRaises(ValueError):stage(bad)
        for field,value in (("source_mode","owner_qualified"),
                            ("source_kind","model_prediction"),
                            ("source_kind","passive_observation"),
                            ("license","not-licensed")):
            bad=json.loads(raw);bad[field]=value
            with self.subTest(field=field):
                with self.assertRaises(PermissionError):stage(bad)
        variants=[]
        zero=json.loads(raw);zero["records"]=[];variants.append(zero)
        flip=json.loads(raw);flip["records"][0][2]="passive";variants.append(flip)
        duplicate=json.loads(raw);duplicate["records"][1][0]=duplicate["records"][0][0];variants.append(duplicate)
        alias=json.loads(raw);alias["records"][1][3]=alias["records"][0][3];variants.append(alias)
        boolean=json.loads(raw);boolean["records"][0][1]=False;variants.append(boolean)
        for variant in variants:
            with self.subTest(rows=variant["records"][:2]):
                with self.assertRaises(ValueError):stage(variant)

    def test_07_native_retained_slot_alternate_roles_and_legacy_unchanged(self):
        old=PublicCausalCells()
        legacy=old.snapshot()
        for slot,action,nuisance in ((12,0,5),(6,3,2),(7,1,4)):
            doc=custom(slot,action,nuisance)
            out=stage(doc)
            bank=NativeRelationMemory.restore(out.checkpoint)
            local=slot if slot<7 else slot-7
            for ctx in range(16):
                want=None if ctx>=8 else (1 if ctx%2==0 else 0)
                self.assertEqual(out.choose_certified(ctx),want)
                if ctx<8:
                    pair=bank.observed_action_pair(local,ctx,retained=slot>=7)
                    self.assertEqual(pair,((ctx&1)^(slot&1),
                                           1^(ctx&1)^(slot&1)))
            self.assertEqual(out.receipt["verified_non_tied_actions"],8)
        self.assertEqual(len(legacy),164)
        self.assertEqual(old.snapshot(),legacy)

    def test_08_tie_never_makes_unsupported_choice(self):
        doc=D.make_doc(0,"fixed_balanced")
        for row in doc["records"]:
            row[1]=(row[0]&1)
        out=stage(doc)
        self.assertEqual(out.receipt["certified_native_observations"],16)
        self.assertEqual(out.receipt["both_actions_witnessed_contexts"],8)
        self.assertEqual(out.receipt["verified_non_tied_actions"],0)
        self.assertEqual(out.verified_actions,(None,)*16)

    def test_09_native_capacity_prior_tamper_and_overflow_denied(self):
        doc=D.make_doc(1,"paired")
        out=stage(doc)
        corrupted=bytearray(out.checkpoint)
        corrupted[-1]^=1
        with self.assertRaises(ValueError):
            stage(doc,prior=bytes(corrupted))
        # A complete WSP155 source checkpoint for a slot fills its 32
        # native observation positions. Future exact duplicates remain okay.
        from yggdrasil.native_sixbit_projection import (
            SCHEMA as COMPLETE_SCHEMA,stage_sixbit_do_bundle
        )
        complete=D.make_doc(1,"paired")
        complete["schema"]=COMPLETE_SCHEMA
        complete["records"]=[[x,D._private_fixture_effect(1,x),"observed_do",
                              "w156:all:"+str(x)] for x in range(64)]
        raw=canonical_json(complete)
        full=stage_sixbit_do_bundle(raw,digest(raw))
        self.assertEqual(NativeRelationMemory.restore(full.checkpoint).unique_observations,32)
        repeated=stage(doc,prior=full.checkpoint)
        self.assertEqual(repeated.checkpoint,full.checkpoint)
        self.assertEqual(repeated.receipt["native_receipt"]["unique_added"],0)

    def test_10_new_fabricated_cohort_frozen_equal_budget_controls(self):
        a=D.study()
        self.assertEqual(a["worlds"],24)
        self.assertEqual(a["source_paid_total"],2304)
        self.assertEqual(a["source_paid_per_arm_world"],32)
        self.assertEqual(a["scores"]["paired"]["on_certified_actions"],96)
        self.assertEqual(a["scores"]["fixed_balanced"]["on_certified_actions"],96)
        self.assertGreaterEqual(a["paired_gain_vs_random_contexts_per_on_world"],4)
        self.assertFalse(a["science_pass"])
        self.assertFalse(a["native_admission"])
        self.assertEqual(len(a["source_trace_sha256"]),64)
        self.assertIn(a["classification"],(
            "SOURCEFREE_PARTIAL_NATIVE_OBSERVATION_SUPPORTED",
            "SOURCEFREE_PARTIAL_NATIVE_OBSERVATION_NO_GO"))
        # Preserve exact input/metrics receipt across the two OS, excluding
        # runtime-dependent machine timing.
        import json
        no_resource={k:v for k,v in a.items() if k not in ("wall_s","cpu_s")}
        print("WSP156_NONRESOURCE_SHA256",digest(canonical_json(no_resource)))
        print("WSP156_SOURCEFREE_DEVELOPMENT",json.dumps(a,sort_keys=True))

if __name__=="__main__":
    unittest.main()

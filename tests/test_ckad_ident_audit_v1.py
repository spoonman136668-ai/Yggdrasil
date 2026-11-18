"""CKAD identifiability audit: true source-free archival and negative controls."""
import importlib.util
from pathlib import Path
import unittest

MODULE=Path(__file__).resolve().parents[1]/"research/contrib/chatgpt/CKAD-IDENT-AUDIT-V1/audit.py"
s=importlib.util.spec_from_file_location("ckad_ident_audit_v1",MODULE)
a=importlib.util.module_from_spec(s)
s.loader.exec_module(a)

class IdentifiabilityArchiveTests(unittest.TestCase):
    def test_program_class_has_25_positive_conjunctions(self):
        self.assertEqual(len(a.EXPANDED_GATES),25)
        self.assertEqual(a.EXPRESSION_COUNT,3200)
        self.assertEqual(a.public_program(32,0,1,0),0)
        self.assertEqual(a.public_program(33,0,1,0),1)
        self.assertEqual(a.public_program(39,0,7,0),1)

    def test_ambiguous_hypothesis_is_not_certified(self):
        options=[(0,1,0),(1,1,0)]
        self.assertEqual(a.consensus_at(options,0),0)
        self.assertIsNone(a.consensus_at(options,1))
        self.assertIsNone(a.consensus_at([],1))

    def test_witness_only_enumeration_never_uses_truth(self):
        candidates,minimum,n=a.expanded_candidates([(0,0),(1,1)])
        self.assertTrue(candidates)
        self.assertEqual(minimum,0)
        self.assertGreater(n,1)
        self.assertTrue(all(a.public_program(0,*p)==0 and
                            a.public_program(1,*p)==1 for p in candidates))

    def test_proposals_are_input_only_and_deterministic(self):
        programs=[(0,1,0),(1,1,0),(0,3,1),(6,2,0)]
        allowed=(5,8,11,20,33,34)
        a1=a.input_only_proposals(programs,allowed,16)
        a2=a.input_only_proposals(programs,allowed,16)
        self.assertEqual(a1,a2)
        self.assertEqual(len(a1["masks"]),4)
        self.assertEqual(len(set(a1["masks"])),4)
        self.assertTrue(set(a1["masks"]).issubset(allowed))
        self.assertTrue(a1["hypothetical_nonexecuted"])
        self.assertEqual(a1["source_effects_performed"],0)
        self.assertEqual(a1["mask_sha256"],a.digest(a.canonical(a1["masks"])))

    def test_archived_custody_and_immutable_cold_model(self):
        model,raw,result=a.load_anchored()
        self.assertEqual(result["classification"],"SHARED_OPERATOR_DEV_NO_GO")
        self.assertEqual(model.checkpoint(),raw)
        self.assertEqual(model.fit_worlds,16)
        self.assertEqual(len(a.held_input_masks()),32)
        self.assertEqual(len(a.witness_rows(model,16)),8)
        self.assertEqual(len(a.witness_rows(model,0)),16)

    def test_audit_accounting_and_no_mutation(self):
        result=a.audit()
        self.assertEqual(result["classification"],a.SUITE_CLASS)
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["accepted_native"])
        self.assertEqual(result["new_original_source_actions"],0)
        self.assertEqual(result["new_synthetic_source_actions"],0)
        self.assertEqual(result["new_model_training_calls"],0)
        self.assertEqual(result["held_outcome_reads"],0)
        self.assertEqual(len(result["cases"]),64)
        self.assertEqual(result["family_terms"],25)
        self.assertTrue(all(x["unobserved_inputs"]==(64-x["source_observations"])
                            for x in result["cases"]))
        self.assertTrue(all(not c["input_only_proposals"]["source_effects_performed"]
                            for c in result["cases"]))

    def test_never_imports_old_source_actor_or_private_outcomes(self):
        code=MODULE.read_text()
        for forbidden in ("source_truth(", "SimulatedWorld(", "held_truth(",
                          "CausalGym", "old.dataset(", "source.reset(",
                          "new_original_source_actions += 1"):
            self.assertNotIn(forbidden,code)

if __name__=="__main__":
    unittest.main()

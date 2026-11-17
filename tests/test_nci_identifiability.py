"""Independent source-free input-rank and anti-leakage controls."""
import unittest
from pathlib import Path
import importlib.util
from yggdrasil.native_context_basis import NativeContextBasis,canonical,digest
from yggdrasil.native_context_basis import feature_row

PATH=Path(__file__).resolve().parents[1]/'research/contrib/chatgpt/NCI-ID-A1/diagnostic.py'
spec=importlib.util.spec_from_file_location('nci_id_a1_diagnostic',PATH)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class IdentifiabilityTests(unittest.TestCase):
    def test_independent_rank_matches_native_on_fabricated_truth(self):
        for degree in (4,5):
            xs=list(range(32))
            truth=lambda m: (m.bit_count() & 1)
            rows=[[m&1023,m>>10,truth(m)] for m in xs]
            model=NativeContextBasis(10).stage_fit(0,rows,digest(canonical(rows)),max_degree=degree)
            self.assertEqual(len(mod.rank_state(xs,degree)),model.profile_info(0)['rank'])

    def test_missing_context_cannot_be_assumed_true(self):
        rows=[[m,0,0] for m in range(8)]
        model=NativeContextBasis(10).stage_fit(0,rows,digest(canonical(rows)),max_degree=4)
        self.assertIsNone(model.predict(0,1023,1))

    def test_input_only_proposals_are_new_and_deterministic(self):
        xs=list(range(512))
        a=mod.proposed_inputs(xs,5,32);b=mod.proposed_inputs(xs,5,32)
        self.assertEqual(a,b)
        self.assertFalse(set(a['masks'])&set(xs))
        self.assertEqual(a['potential_rank_gain'],len(a['masks']))
        self.assertFalse(a['action_performed'])
        self.assertFalse(a['outcome_accessed'])
        self.assertEqual(a['masks_sha256'],digest(canonical(a['masks'])))

    def test_proposal_rank_equivalence_to_fresh_elimination(self):
        xs=list(range(512))
        proposal=mod.proposed_inputs(xs,5,32)
        self.assertEqual(len(mod.rank_state(xs+proposal['masks'],5)),
                         proposal['ending_rank'])

    def test_input_validation_refuses_duplicate_or_invalid(self):
        for xs in ([1,1],[2048],[-1]):
            with self.assertRaises(ValueError):
                mod.proposed_inputs(xs,5)
        with self.assertRaises(ValueError):
            mod.proposed_inputs([0],5,33)

    def test_source_free_module_has_no_owner_source_calls(self):
        text=PATH.read_text()
        for forbidden in ('old.dataset(', 'do(', 'reset(', 'original_rows,held,truth', 'source_factory('):
            self.assertNotIn(forbidden,text)

if __name__=='__main__':
    unittest.main()

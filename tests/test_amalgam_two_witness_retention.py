"""G31 negative controls over frozen two-consecutive-consumed-event custody."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

from yggdrasil.native_context_basis import canonical

HERE=Path(__file__).resolve().parents[1]/"research/contrib/chatgpt/CAUSAL-AMALGAM"
sys.path.insert(0, str(HERE))
SPEC=spec_from_file_location("g31_two_witness", HERE/"two_witness_retention.py")
G31=module_from_spec(SPEC)
SPEC.loader.exec_module(G31)
FIX=spec_from_file_location("g31_testfixture",Path(__file__).with_name(
    "test_amalgam_headwise_consolidation.py"))
BASE=module_from_spec(FIX)
FIX.loader.exec_module(BASE)


class TwoWitnessControlTests(unittest.TestCase):
    def test_frozen_ordinals_and_source_hash(self):
        self.assertEqual(G31.STARTS,(1,32,33,64))
        for pos in (0,2,31,34,65,96,True,-1):
            with self.subTest(pos=pos):
                with self.assertRaisesRegex(ValueError,"G31_UNFROZEN_START"):
                    G31._next_consumed(b"[]",pos,())
        with self.assertRaisesRegex(ValueError,"G28_FROZEN_TRACE_PIN"):
            G31._next_consumed(b"[]",1,())

    def test_source_free_fixture_cannot_impersonate_native(self):
        anchor=BASE._Core(BASE._history())
        with self.assertRaisesRegex(ValueError,"G31_SOURCE_NATIVE_REQUIRED"):
            G31.assess_two_witness_source(
                anchor,anchor,anchor,anchor,anchor,{}, {},b"[]",1)

    def test_second_postfit_requires_valid_head_order(self):
        anchor=BASE._Core(BASE._history())
        event=BASE._history()[-1]
        heads=anchor._heads[::-1]
        # The wrapper caller must verify identity BEFORE attempting scoring.
        with self.assertRaisesRegex(ValueError, "G31_HEAD_ORDER"):
            G31._score_new(heads,event,BASE._history()[:-1])

    def test_no_claim_of_gain_from_fake_steps_or_no_updates(self):
        samples=[{"ordinal":n,"analysis":{
            "all_fine_old_heads_within_frozen_bound":True,
            "both_transition_heads_changed_on_both_steps":False,
            "fine_two_row_better_than_coarse":True,
            "fine_two_row_better_than_frozen":True,
            "fine_two_row_not_worse_than_coarse":True,
        }} for n in G31.STARTS]
        r=G31.summarize_frozen_two_witnesses(samples)
        self.assertEqual(r["development_classification"],
                         "DEV_TWO_STEP_STALL_OR_NO_GO")
        self.assertFalse(r["scientific_pass"])

    def test_wrong_second_sample_or_failed_old_bound_is_no_go(self):
        samples=[{"ordinal":n,"analysis":{
            "all_fine_old_heads_within_frozen_bound":True,
            "both_transition_heads_changed_on_both_steps":True,
            "fine_two_row_better_than_coarse":True,
            "fine_two_row_better_than_frozen":True,
            "fine_two_row_not_worse_than_coarse":True,
        }} for n in G31.STARTS]
        self.assertEqual(G31.summarize_frozen_two_witnesses(
            samples)["development_classification"],
            "DEV_TWO_STEP_CONTINUATION_HELPFUL")
        samples[3]["analysis"]["all_fine_old_heads_within_frozen_bound"]=False
        self.assertEqual(G31.summarize_frozen_two_witnesses(
            samples)["development_classification"],"DEV_TWO_STEP_STALL_OR_NO_GO")
        samples[3]["ordinal"]=63
        with self.assertRaisesRegex(ValueError,"G31_FROZEN_SAMPLE_SET"):
            G31.summarize_frozen_two_witnesses(samples)

    def test_g32_fake_data_rejected_and_no_false_learning(self):
        from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
        anchor=BASE._Core(BASE._history())
        first=anchor.clone(BASE._history()+(
            ("first", ((0,0),(0,1)), 0,0,0,0),))
        second=first.clone(first.native._ledger+(
            ("second", ((0,0),(0,1)), 0,1,0,1),))
        for h in first._heads:
            h.steps+=3
        for h in second._heads:
            h.steps+=6
        with self.assertRaisesRegex(ValueError,"G32_SOURCE_TWO_EXACT_PREFIX"):
            G31.protect_immediate_memory(anchor,anchor,first,second)
        self.assertEqual(G31.G32_RECENT_TOL,1e-12)
        no_weight_change=ActionLatentSpecialist("transition")
        self.assertEqual(G31._weight_delta_norm(
            no_weight_change, no_weight_change.clone()),0.0)

    def test_g32_frozen_decision_fails_without_real_second_step(self):
        samples=[{"ordinal":n,"both_transition_heads_changed_first_fine":True,
                  "rehearsal":{"all_old_memory_protected":True,
                               "all_recent_witnesses_protected":True,
                               "at_least_one_second_transition_changed":False,
                               "old_brier_evaluations":8,
                               "prior_witness_evaluations":7},
                  "two_row_postfit_mean_transition_brier":{
                      "coarse":.2,"fine":.3,"rehearsal":.15}}
                 for n in G31.STARTS]
        result=G31.summarize_g32(samples)
        self.assertEqual(result["development_classification"],
                         "DEV_REHEARSAL_NO_GO")
        self.assertFalse(result["scientific_pass"])
        samples[0]["ordinal"]=2
        with self.assertRaisesRegex(ValueError,"G32_FROZEN_STARTS"):
            G31.summarize_g32(samples)


if __name__=="__main__":
    unittest.main()

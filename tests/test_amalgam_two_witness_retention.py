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


if __name__=="__main__":
    unittest.main()

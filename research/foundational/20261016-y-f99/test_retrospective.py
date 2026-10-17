"""F99 retired-cohort retrospective contract: synthetic fixtures only, NO cohort reads."""
from __future__ import annotations
import importlib.util
import inspect
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "f99_retired_contract_under_test", HERE / "retrospective.py")
M = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = M
spec.loader.exec_module(M)


def row(kind=M.FOUR, arrival="original", cohort="f93b_guard", correct=1,
        rescue=0, harm=0, eligible_harm=0, resources=0):
    return dict(kind=kind, arrival=arrival, cohort=cohort, f60_correct=correct,
                native_alternatives=4, closure_preserving=2, closure_eligible=1,
                eligible_rescue_actions=rescue,
                closure_preserving_harm_actions=harm,
                eligible_harm_actions=eligible_harm,
                source_resource_ineligible=resources)


class RetrospectiveContractTests(unittest.TestCase):
    def test_fixed_exact_retired_cohort_registry(self):
        self.assertEqual(M.RETIRED, {
            "f93b_guard": (-6041, -6057, False, 32),
            "f96_holdout": (-6241, -6257, True, 64),
            "f98_validation": (-6421, -6429, True, 32),
            "f98_guard": (-6441, -6457, True, 64),
        })

    def test_reject_fresh_and_protected_seeds(self):
        for seed, fam in ((761000, -2), (-6040, -2), (-6057, -1),
                          (-6241, 1460), (-6441, 0), (762000, -1)):
            with self.assertRaises(ValueError):
                M.assert_retired_source("f93b_guard", seed, fam, "original")
        with self.assertRaises(ValueError):
            M.assert_retired_source("f98_guard", -6441, -2, "bad_order")

    def test_f93b_historical_observation_order_not_duplicated(self):
        M.assert_retired_source("f93b_guard", -6041, -2, "original")
        M.assert_retired_source("f93b_guard", -6041, -1, "local_rotate4")
        with self.assertRaises(ValueError):
            M.assert_retired_source("f93b_guard", -6041, -2, "local_rotate4")
        with self.assertRaises(ValueError):
            M.assert_retired_source("f93b_guard", -6041, -1, "original")

    def test_no_future_query_argument_at_causal_preparation(self):
        self.assertEqual(tuple(inspect.signature(M.prepare_public_prefixes).parameters),
                         ("public", "C", "native", "pack"))
        self.assertEqual(tuple(inspect.signature(M.audit_offline_outcomes).parameters),
                         ("prepared", "public", "question", "F85", "native", "pack"))

    def test_witness_is_retrospective_only_and_harm_retained(self):
        out = M.summarize((row(), row(M.SIX, "local_rotate4",
                                      "f96_holdout", 0, rescue=3, harm=0),
                           row(M.FOUR, "local_rotate4", "f98_guard",
                               1, harm=2, eligible_harm=1)))
        self.assertEqual(out["classification"], "RETROSPECTIVE_FEASIBLE_ONLY")
        self.assertEqual(out["six_step_failed_episodes_rescuable"], 1)
        self.assertEqual(out["four_step"]["closure_preserving_harm_actions"], 2)
        self.assertEqual(out["by_order"]["local_rotate4"]["eligible_harm_actions"], 1)

    def test_negative_means_no_witness_no_threshold_relaxation(self):
        result = M.summarize((row(M.SIX, "original", correct=0),))
        self.assertEqual(result["classification"], "RETROSPECTIVE_NO_WITNESS")
        self.assertEqual(result["six_step_failed_episodes_rescuable"], 0)

    def test_resource_ineligibility_never_claims_success(self):
        result = M.summarize((row(M.SIX, correct=0, rescue=1, resources=1),))
        self.assertEqual(result["classification"], "SOURCE_RESOURCE_INELIGIBLE")

    def test_empty_retrospective_denied(self):
        with self.assertRaises(ValueError):
            M.summarize(())


if __name__ == "__main__":
    unittest.main()

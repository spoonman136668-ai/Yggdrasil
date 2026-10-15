"""F51 PRECODE-only: all public memory controls and fresh cohorts."""
import copy
import json
import pathlib
import unittest

P=pathlib.Path(__file__).with_name("prereg-candidate.json")
def validate(p):
    assert p["schema"]=="yggdrasil.f51.online-memory-complete-controls.prereg.v1"
    assert p["stage"]=="PRECODE_FROZEN_CANDIDATE_NOT_OWNER_ADMITTED"
    assert p["parent_f50_source_sha"]=="ab83bd0cb2df4409f73ca9a9337e803467020477"
    assert p["independent_f50_review"]["conclusion"]=="UNQUALIFIED_FAILURE_UNREGISTERED_PUBLIC_TAG_ONLY_CONTROL"
    required={"learned_retention","public_tag_only","public_frequency_priority","FIFO_last12",
      "public_hash_reservoir","public_degree_priority","public_role_coverage","private_future_query_oracle_unfair"}
    assert required==set(p["controls"]) and len(required)==len(p["controls"])
    assert p["evaluator_only_controls"]==["private_future_query_oracle_unfair"]
    m=p["memory"]
    assert m["events_per_stream"]==64 and m["capacity_edges"]==12
    assert m["question_hidden_until_after_all_retention_decisions"] is True
    assert p["thresholds"]["minimum_gain_vs_strongest_fair"]==0.05
    assert p["strong_control_requirements"]["exact_control_set_required_at_runtime"] is True
    ranges=[(p[k]["seeds_start_inclusive"],p[k]["seeds_end_exclusive"])
            for k in ("fresh_fit","fresh_diagnostic","proposed_original_NOT_RESERVED")]
    ranges += [tuple(r) for r in p["excluded_prior_originals"]]
    assert all(type(a) is int and type(b) is int and a<b for a,b in ranges)
    assert all(a[1]<=b[0] or b[1]<=a[0]
               for i,a in enumerate(ranges) for b in ranges[i+1:])
    families=[set(p[k]["families"]) for k in ("fresh_fit","fresh_diagnostic","proposed_original_NOT_RESERVED")]
    assert all(len(x)==4 for x in families)
    assert not any(a&b for i,a in enumerate(families) for b in families[i+1:])
    for flag in ("source_code_implemented","train_or_diagnostic_executed","owner_admitted",
                 "primary_original_executed","independent_F3","accepted_ref_mutation",
                 "dreamrsi_gain_proven","thetaevolve_training_authorized"):
        assert p[flag] is False
    assert p["paid_api_calls"]==0
    return True

class FrozenF51(unittest.TestCase):
    def setUp(self):self.p=json.loads(P.read_text())
    def test_precode_contract(self):self.assertTrue(validate(self.p))
    def test_missing_registered_public_tag_rejected(self):
        p=copy.deepcopy(self.p);p["controls"].remove("public_tag_only")
        with self.assertRaises(AssertionError):validate(p)
    def test_future_query_leak_rejected(self):
        p=copy.deepcopy(self.p);p["memory"]["question_hidden_until_after_all_retention_decisions"]=False
        with self.assertRaises(AssertionError):validate(p)
    def test_original_collision_rejected(self):
        p=copy.deepcopy(self.p);p["fresh_diagnostic"]["seeds_start_inclusive"]=531010
        with self.assertRaises(AssertionError):validate(p)
    def test_false_science_promotion_rejected(self):
        p=copy.deepcopy(self.p);p["independent_F3"]=True
        with self.assertRaises(AssertionError):validate(p)
if __name__=="__main__":unittest.main()

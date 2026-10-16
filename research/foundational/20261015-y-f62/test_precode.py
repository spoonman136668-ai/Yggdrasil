"""Y-F62 precode-only guard: cannot dispatch a scientific FIT use.

Prereg exists before source. Enforces distinct frozen cohorts, registered
same-byte controls and false original/F3/Dream/Theta authority.
"""
import copy,json,pathlib,unittest
P=pathlib.Path(__file__).with_name("prereg.json")
def verify(p):
    assert p["schema"]=="yggdrasil.f62.causal-counterfactual-retention-action-value.prereg.v1"
    assert p["stage"]=="PRECODE_FROZEN_NO_FIT_OR_SCIENCE_EXECUTED"
    assert p["tracking_issue"]==285
    parent=p["parent_F61"]
    assert parent["first_fit_validation_run"]==38834803583
    assert parent["result_verdict"]=="FIT_VALIDATION_LEARNED_QUERY_VALUE_NEGATIVE"
    assert (parent["learned_correct"],parent["strongest_fair_correct"],
            parent["total_cases"])==(5,21,32)
    assert parent["exposed_F61_validation_must_never_be_retrained_on"] is True
    assert p["fit"]["seeds"]==[761000,761016]
    assert p["fit"]["training"]==[761000,761008]
    assert p["fit"]["within_fit_validation"]==[761008,761016]
    assert p["fit"]["families"]==[1460,1461,1462,1463]
    assert p["diagnostic_UNAUTHORIZED"]["seeds"]==[761100,761116]
    assert p["original_UNRESERVED"]["seeds"]==[762000,762016]
    cohorts=[p["fit"],p["diagnostic_UNAUTHORIZED"],p["original_UNRESERVED"]]
    for i,a in enumerate(cohorts):
        for b in cohorts[i+1:]:
            assert a["seeds"][1]<=b["seeds"][0] or b["seeds"][1]<=a["seeds"][0]
            assert not set(a["families"])&set(b["families"])
    for old in ((741000,741016),(741100,741116),(742000,742016),
                (731000,731016),(711000,711016)):
        assert p["fit"]["seeds"][1]<=old[0] or old[1]<=p["fit"]["seeds"][0]
    learning=p["learned_policy"]
    assert learning["parameters_max"]==12 and learning["parameter_encoding"]=="signed_int8"
    assert learning["max_lossless_stored_records"]==12
    assert learning["bytes_per_record"]==12
    assert learning["max_serialized_retained_memory_bytes"]==144
    assert learning["learned_parameter_bytes_counted_separately"] is True
    assert learning["not_qualified_as_total_native_576B"] is True
    assert learning["candidate_actions"]==[
        "append_public_edge","compose_contiguous_role_path_with_existing_record",
        "evict_single_retained_record_if_at_capacity"]
    assert len(learning["available_online_inputs"])==3
    assert "future" not in " ".join(learning["available_online_inputs"]).lower()
    assert "validation or DIAG" in learning["learning_label"]
    controls=p["frozen_controls"]
    assert controls==["learned_counterfactual_action_value",
        "F60_exact_source_fixed_online","F59_exact_source_deferred",
        "F58_exact_source_frontier","F61_frozen_learned_policy_no_refit",
        "fixed_public_pair_triple_DAG","fixed_public_FIFO_hash",
        "offline_full_public_graph_extra_work_noncompetitive",
        "future_question_oracle_unfair"]
    assert len(set(controls))==len(controls)
    src=p["source"];assert src["public_events_per_case"]==72
    assert src["future_question_hidden_from_online_actions"] is True
    assert src["balanced_public_tags_not_used_by_any_online_policy"] is True
    provenance=p["frozen_control_provenance"]
    assert provenance["F61_historical_trained_int8_weights"]==[
        39,11,-10,35,17,18,18,28,-7,-83,12,1]
    assert provenance["exact_historical_methods_no_adaptive_refit"] is True
    gates=p["thresholds"]
    assert gates["extra_work_public_witness_min_accuracy"]==.85
    assert gates["fixed_online_feasibility_min_accuracy"]==.25
    assert gates["learned_accuracy_gain_vs_strongest_equal_byte_fair_min"]==.05
    assert gates["per_heldout_fit_validation_family_nondegradation"] is True
    assert gates["positive_composition_retrieval_ablation"] is True
    authority=p["authority"]
    for flag in ("source_independent_F3","protected_primary_original_executed",
        "accepted_ref_mutation","live_Dream_RSI_Pareto_Theta_policy_promotion",
        "controller_or_Cloudflare_mutation","paid_API_or_Codex_reviews"):
        assert authority[flag] is False
    assert authority["validation_once_only_no_reruns"] is True
    assert not P.with_name("source_pilot.py").exists(), "F62 still PRECODE only"
    return True
class FrozenPrecode(unittest.TestCase):
    def setUp(self):self.p=json.loads(P.read_text())
    def test_registered_contract(self):self.assertTrue(verify(self.p))
    def test_no_recycled_diagnostic(self):
        p=copy.deepcopy(self.p);p["fit"]["seeds"]=[741100,741116]
        with self.assertRaises(AssertionError):verify(p)
    def test_no_removed_fair_control(self):
        p=copy.deepcopy(self.p);p["frozen_controls"].remove("F60_exact_source_fixed_online")
        with self.assertRaises(AssertionError):verify(p)
    def test_no_unaccounted_bytes(self):
        p=copy.deepcopy(self.p);p["learned_policy"]["max_serialized_retained_memory_bytes"]=156
        with self.assertRaises(AssertionError):verify(p)
    def test_no_false_accepted_science(self):
        p=copy.deepcopy(self.p);p["authority"]["source_independent_F3"]=True
        with self.assertRaises(AssertionError):verify(p)
    def test_no_retrained_old_F61_weights(self):
        p=copy.deepcopy(self.p)
        p["frozen_control_provenance"]["F61_historical_trained_int8_weights"][0]+=1
        with self.assertRaises(AssertionError):verify(p)
if __name__=="__main__":unittest.main()

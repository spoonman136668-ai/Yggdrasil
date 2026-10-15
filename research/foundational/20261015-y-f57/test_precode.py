"""F57 pre-source negative tests only: never generate FIT/DIAG or dispatch."""
import copy,json,pathlib,unittest
D=pathlib.Path(__file__).with_name("prereg.json")
def gate(p):
    assert p["schema"]=="yggdrasil.f57.causal-incremental-component-memory.prereg.v1"
    assert p["stage"]=="PRECODE_FROZEN_NO_SOURCE_OR_DIAGNOSTIC"
    assert p["parent_f56_source_sha"]=="6c8f49c47f4d93fbb2283f7e994e2eca4bc164cb"
    assert p["parent_f56_run"]==38824305540
    assert p["parent_f56_failed_first_gate"] is True
    cohorts=[p["fit"],p["diagnostic_NOT_AUTHORIZED"],p["proposed_original_NOT_RESERVED"]]
    ranges=[c["seed_range"] for c in cohorts]
    assert ranges==[[671000,671016],[671100,671116],[672000,672016]]
    assert [c["families"] for c in cohorts]==[
        [1260,1261,1262,1263],
        [1264,1265,1266,1267],
        [1268,1269,1270,1271]]
    for idx,a in enumerate(cohorts):
        for b in cohorts[idx+1:]:
            assert not set(a["families"])&set(b["families"])
            assert a["seed_range"][1]<=b["seed_range"][0]
    assert len(p["controls"])==len(set(p["controls"]))
    assert p["controls"]==["learned_incremental_component_state","frozen_F56_constructive_online","fixed_public_component_aggregation","fixed_public_pair_compression","fixed_public_triple_compression","raw_degree_FIFO","public_hash","full_public_offline_extra_work_noncompetitive","private_future_question_oracle_unfair"]
    assert p["FIT_gate_before_diagnostic"]["full_public_offline_accuracy_min"]==.85
    assert p["FIT_gate_before_diagnostic"]["online_constructive_accuracy_min"]==.25
    assert p["FIT_gate_before_diagnostic"]["public_source_identifiability_verified_independently"] is True
    assert p["heldout_gates"]["gain_over_strongest_equal_byte_online_fair_min_pp"]==5
    assert p["heldout_gates"]["no_regression_any_heldout_family"] is True
    for name in ("diagnostic_unconsumed","originals_unconsumed"):
        assert p["restrictions"][name] is True
    for name in ("independent_F3","accepted_ref_mutation","live_optimizer_policy_promotion"):
        assert p["restrictions"][name] is False
    assert p["restrictions"]["paid_model_API_calls"]==0
    assert p["resource"]["max_serialized_payload_bytes"]==144 and p["resource"]["retained_records_max"]==12
    assert p["resource"]["future_question_hidden_until_memory_frozen"] is True
    return True
class PrecodeFrozen(unittest.TestCase):
    def setUp(self): self.p=json.loads(D.read_text())
    def test_frozen_protocol(self):self.assertTrue(gate(self.p))
    def test_cross_fold_collision_rejected(self):
        p=copy.deepcopy(self.p);p["proposed_original_NOT_RESERVED"]["seed_range"]=list(p["diagnostic_NOT_AUTHORIZED"]["seed_range"])
        with self.assertRaises(AssertionError):gate(p)
    def test_false_policy_promotion_rejected(self):
        p=copy.deepcopy(self.p);p["restrictions"]["live_optimizer_policy_promotion"]=True
        with self.assertRaises(AssertionError):gate(p)
    def test_wrong_parent_rejected(self):
        p=copy.deepcopy(self.p);p["parent_f56_failed_first_gate"]=False
        with self.assertRaises(AssertionError):gate(p)
    def test_weak_public_reference_rejected(self):
        p=copy.deepcopy(self.p);p["FIT_gate_before_diagnostic"]["full_public_offline_accuracy_min"]=.5
        with self.assertRaises(AssertionError):gate(p)
    def test_future_query_leak_rejected(self):
        p=copy.deepcopy(self.p);p["resource"]["future_question_hidden_until_memory_frozen"]=False
        with self.assertRaises(AssertionError):gate(p)
    def test_missing_control_rejected(self):
        p=copy.deepcopy(self.p);p["controls"].pop()
        with self.assertRaises(AssertionError):gate(p)
if __name__=="__main__":unittest.main()

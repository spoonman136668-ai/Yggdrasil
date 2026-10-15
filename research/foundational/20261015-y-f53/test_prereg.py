"""F53 preregistration-only qualification: explicit source/arm identities and false-admission gates.

No training, diagnostic, original, or acceptance operation is performed here.
"""
import copy,json,pathlib,unittest

P=pathlib.Path(__file__).with_name("prereg.json")
ARMS=("fit_role_path_cohesion_retention","learned_bridge_retention",
      "learned_topology_retention","public_role_path_greedy",
      "public_connected_component","public_degree_adjacency",
      "public_tag_only","FIFO_last12","public_frequency","public_hash",
      "private_future_question_oracle_unfair")
def guard(p):
    assert p["schema"]=="yggdrasil.f53.path-cohesion-memory.prereg.v1"
    assert p["stage"]=="PRECODE_FROZEN_BEFORE_SOURCE"
    assert p["parent_f52_head"]=="48178ffd200371ba360b8dfb0874e1b758daa8ff"
    assert p["parent_f52_run"]==38815175032
    assert p["parent_f52_negative"]=={
      "bridge_correct":5,"best_fair_correct":8,"cases":64,
      "reason":"failed_accuracy_and_per_family_gates"}
    assert tuple([p["candidate"],*p["controls"],p["unfair_control"]])==ARMS
    assert p["fit_seeds"]==[591000,591016]
    assert p["diagnostic_seeds"]==[591100,591116]
    assert p["proposed_original_seeds_NOT_RESERVED"]==[592000,592016]
    assert p["fit_families"]==[1120,1121,1122,1123]
    assert p["diagnostic_families"]==[1124,1125,1126,1127]
    assert p["fit_calibration_noise"] if "fit_calibration_noise" in p else True
    assert p["memory_capacity_edges"]==12
    assert p["events_per_stream"]==64
    assert p["public_tags_exactly_balanced"] is True
    assert p["future_question_hidden_until_after_ingestion"] is True
    assert p["threshold_gain_pp"]==5
    assert p["require_no_family_regression"] is True
    for k in ("source_implementation_present","original_executed","accepted_ref_mutation"):
        assert p[k] is False
    assert p["paid_api_calls"]==0
    return True

class F53Freeze(unittest.TestCase):
    def setUp(self):self.p=json.loads(P.read_text())
    def test_complete_precode(self):self.assertTrue(guard(self.p))
    def test_missing_strong_graph_control_fails(self):
        p=copy.deepcopy(self.p);p["controls"].remove("public_connected_component")
        with self.assertRaises(AssertionError):guard(p)
    def test_original_collision_fails(self):
        p=copy.deepcopy(self.p);p["proposed_original_seeds_NOT_RESERVED"]=[591100,591116]
        with self.assertRaises(AssertionError):guard(p)
    def test_future_query_leak_fails(self):
        p=copy.deepcopy(self.p);p["future_question_hidden_until_after_ingestion"]=False
        with self.assertRaises(AssertionError):guard(p)
    def test_false_promotion_fails(self):
        p=copy.deepcopy(self.p);p["accepted_ref_mutation"]=True
        with self.assertRaises(AssertionError):guard(p)

if __name__=="__main__":unittest.main()

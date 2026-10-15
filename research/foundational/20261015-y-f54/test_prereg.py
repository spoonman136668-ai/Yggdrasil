"""Y-F54 independent pre-code qualification. Never starts an experiment.

The parent Y-F53 original failure cannot be converted into accepted science;
this preregistered new mechanism needs complete, fresh source qualification.
"""
import copy,json,pathlib,unittest
P=pathlib.Path(__file__).with_name("prereg-candidate.json")
ARMS=("learned_global_relation_state","F53_frozen_learned_chunker",
      "fixed_public_triple_chunks","fixed_public_pair_chunks",
      "public_connected_component_chunks","public_DAG_path_compression",
      "raw_degree_and_FIFO","public_hash","private_future_question_oracle_unfair")
def guard(p):
    assert p["schema"]=="yggdrasil.f54.public-identifiability-and-learned-global-memory.prereg.v1"
    assert p["stage"]=="PRECODE_FROZEN_NOT_EXECUTED"
    assert p["F53_original_source_run"]==38816902386
    assert p["F53_archive_audit_run"]==38817309656
    assert p["parent_F53_archive_audit_head"]=="74e96e063a5916d0e7b34220de81c0a375918c0c"
    assert tuple(p["controls"])==ARMS
    assert p["fit"]["seeds"]==[591000,591016]
    assert p["fit"]["families"]==[1060,1061,1062,1063]
    assert p["diagnostic"]["seeds"]==[591100,591116]
    assert p["diagnostic"]["families"]==[1064,1065,1066,1067]
    assert p["future_original_NOT_RESERVED"]["seeds"]==[592000,592016]
    assert p["future_original_NOT_RESERVED"]["families"]==[1068,1069,1070,1071]
    folds=[p[x] for x in ("fit","diagnostic","future_original_NOT_RESERVED")]
    for i,x in enumerate(folds):
        for y in folds[i+1:]:
            assert not (set(x["families"])&set(y["families"]))
            assert x["seeds"][1]<=y["seeds"][0] or y["seeds"][1]<=x["seeds"][0]
    stream=p["stream"]
    assert stream["public_edges_per_stream"]==72
    assert stream["memory_payload_max_bytes"]==144
    assert stream["record_bytes"]==12 and stream["records_max"]==12
    assert stream["memory_payload_max_bytes"]==stream["record_bytes"]*stream["records_max"]
    assert stream["future_question_path_lengths"]==[4,6,8]
    assert stream["never_reveal_question_during_ingestion"] is True
    assert stream["lossless_codec_includes_decoder_bits"] is True
    assert stream["public_tags_balanced"] is True
    assert "never used as equal-cost fair" in p["reference_noncompetitive"]
    assert p["thresholds"]["gain_vs_strongest_equal_byte_fair_min"]==0.05
    assert p["thresholds"]["per_family_nondegradation"] is True
    assert p["thresholds"]["positive_chunk_retrieval_ablation"] is True
    assert p["thresholds"]["serialized_bytes_and_decoder_correctness_audited"] is True
    authority=p["authority"]
    for k in ("independent_F3","primary_original_first_use",
              "accepted_ref_mutation","live_optimizer_policy_promotion"):
        assert authority[k] is False
    assert authority["FIT_labels_only_no_F53_holdout_training"] is True
    assert authority["paid_API_calls"]==0
    return True
class F54Prereg(unittest.TestCase):
    def setUp(self):self.pr=json.loads(P.read_text())
    def test_pinned_frozen_protocol(self): self.assertTrue(guard(self.pr))
    def test_missing_fair_baseline_fails(self):
        x=copy.deepcopy(self.pr);x["controls"].remove("public_connected_component_chunks")
        with self.assertRaises(AssertionError):guard(x)
    def test_reserved_original_collision_fails(self):
        x=copy.deepcopy(self.pr);x["future_original_NOT_RESERVED"]["seeds"]=[591100,591116]
        with self.assertRaises(AssertionError):guard(x)
    def test_future_query_leakage_fails(self):
        x=copy.deepcopy(self.pr);x["stream"]["never_reveal_question_during_ingestion"]=False
        with self.assertRaises(AssertionError):guard(x)
    def test_byte_budget_mismatch_fails(self):
        x=copy.deepcopy(self.pr);x["stream"]["memory_payload_max_bytes"]=156
        with self.assertRaises(AssertionError):guard(x)
    def test_laundered_authority_fails(self):
        x=copy.deepcopy(self.pr);x["authority"]["independent_F3"]=True
        with self.assertRaises(AssertionError):guard(x)
if __name__=="__main__":unittest.main()

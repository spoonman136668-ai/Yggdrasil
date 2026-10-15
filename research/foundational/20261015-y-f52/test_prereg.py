"""F52 frozen precode qualification, no diagnostic or original execution."""
import copy,json,pathlib,unittest

DOC=pathlib.Path(__file__).with_name("prereg-candidate.json")
REQUIRED=["learned_relation_chunking","fixed_public_greedy_pair_chunks","fixed_public_greedy_triple_chunks","raw_degree_priority","raw_connected_component","raw_FIFO","public_hash","private_future_question_oracle_unfair"]
def validate(p):
    assert p["schema"]=="yggdrasil.f52.future-task-chunk-compression.prereg.v1"
    assert p["stage"]=="PRECODE_ONLY_NO_SCIENCE_CONSUMED"
    assert p["controls"]==REQUIRED
    assert len(set(p["controls"]))==len(p["controls"])
    assert p["train"]["seeds"]==[551000,551016]
    assert p["diagnostic"]["seeds"]==[551100,551116]
    assert p["future_original_NOT_RESERVED"]["seeds"]==[552000,552016]
    spans=[p[k]["seeds"] for k in ("train","diagnostic","future_original_NOT_RESERVED")]
    assert all(a[0]<a[1] for a in spans)
    assert all(a[1]<=b[0] or b[1]<=a[0] for i,a in enumerate(spans) for b in spans[i+1:])
    families=[set(p[k]["families"]) for k in ("train","diagnostic","future_original_NOT_RESERVED")]
    assert all(len(f)==4 for f in families)
    assert not any(a&b for i,a in enumerate(families) for b in families[i+1:])
    assert p["limits"]["independent_F3"] is False
    assert p["limits"]["accepted_ref_mutation"] is False
    assert p["limits"]["paid_API_calls"]==0
    return True
class FrozenStudy(unittest.TestCase):
    def setUp(self):self.p=json.loads(DOC.read_text())
    def test_exact_control_identity(self):self.assertTrue(validate(self.p))
    def test_reject_unregistered_control(self):
        p=copy.deepcopy(self.p);p["controls"][1]="unregistered"
        with self.assertRaises(AssertionError):validate(p)
    def test_reject_consumed_cohort(self):
        p=copy.deepcopy(self.p);p["future_original_NOT_RESERVED"]["seeds"][0]=p["diagnostic"]["seeds"][0]
        with self.assertRaises(AssertionError):validate(p)
    def test_reject_science_promotion(self):
        p=copy.deepcopy(self.p);p["limits"]["independent_F3"]=True
        with self.assertRaises(AssertionError):validate(p)
if __name__=="__main__":unittest.main()

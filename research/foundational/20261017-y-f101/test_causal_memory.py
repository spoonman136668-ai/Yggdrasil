"""Y-F101 causal native-memory trace contracts: no cohorts, learning or originals."""
import importlib.util
import inspect
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("y_f101_native_memory_under_test",
                                           HERE/"causal_memory.py")
M=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=M
spec.loader.exec_module(M)

BASE=((10,11,(0,)),(11,12,(2,)),(12,13,(4,)),(13,14,(6,)))
SIX=BASE+((14,15,(0,)),(15,16,(2,)))
SECOND=((10,21,(0,)),(21,22,(2,)),(22,23,(4,)),(23,14,(6,)))

class F101SourceOnlyContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f99,cls.native=M.frozen_sources()

    def test_precode_freeze_and_source_parent_exact_sha(self):
        self.assertEqual(M.blob(HERE/"prereg.json"),M.PREREG_BLOB)
        self.assertEqual(M.blob(HERE.parent/"20261016-y-f99"/"causal_closure.py"),
                         M.F99_BLOB)

    def test_api_cannot_receive_future_events_answers_or_learner_labels(self):
        self.assertEqual(tuple(inspect.signature(M.explain).parameters),
                         ("memory","signature","f99","max_states"))
        self.assertEqual(tuple(inspect.signature(M.witness).parameters),
                         ("memory","signature","f99","max_states"))

    def test_four_hop_every_source_record_is_necessary(self):
        x=M.explain(BASE,(10,(0,2,4,6),14),self.f99)
        self.assertEqual(x["status"],"STRUCTURAL_PATH_FOUND")
        self.assertEqual(x["total_necessary_records"],4)
        self.assertEqual([p["record_index"] for p in x["exact_lex_first_witness"]],
                         [0,1,2,3])
        self.assertEqual(len(x["single_record_interventions"]),4)
        self.assertTrue(all(not v["survived_single_record_role_shift"]
                            for v in x["single_record_interventions"]))
        self.assertEqual(x["retained_native_bytes"],48)
        self.assertFalse(x["any_question_answer_or_future_event_accessed"])

    def test_six_hop_exact_signed_roles_and_causal_deletion(self):
        x=M.explain(SIX,(10,(0,2,4,6,0,2),16),self.f99)
        self.assertEqual(x["total_necessary_records"],6)
        self.assertEqual([p["orientation"] for p in x["exact_lex_first_witness"]],
                         ["stored"]*6)
        self.assertEqual(x["retained_native_bytes"],72)

    def test_reverse_is_exact_signed_inverse_in_reversed_order(self):
        x=M.explain(BASE,(14,(7,5,3,1),10),self.f99)
        self.assertEqual(x["status"],"STRUCTURAL_PATH_FOUND")
        self.assertEqual([p["record_index"] for p in x["exact_lex_first_witness"]],
                         [3,2,1,0])
        self.assertEqual([p["orientation"] for p in x["exact_lex_first_witness"]],
                         ["signed_inverse"]*4)
        self.assertEqual(x["total_necessary_records"],4)

    def test_duplicate_independent_paths_make_every_record_nonnecessary(self):
        x=M.explain(BASE+SECOND,(10,(0,2,4,6),14),self.f99)
        self.assertTrue(x["present_in_frozen_f99_closure"])
        self.assertEqual(x["total_necessary_records"],0)
        self.assertEqual(len(x["single_record_interventions"]),8)
        self.assertTrue(all(not row["necessary_under_single_record_deletion"]
                            for row in x["single_record_interventions"]))
        self.assertTrue(all(row["survived_single_record_role_shift"]
                            for row in x["single_record_interventions"]))
        self.assertTrue(any(row["present_in_lex_first_witness"]
                            for row in x["single_record_interventions"]))
        self.assertTrue(any(not row["present_in_lex_first_witness"]
                            for row in x["single_record_interventions"]))

    def test_atomic_multirole_edge_has_no_false_internal_vertex(self):
        b=((10,40,(0,2,4)),)
        self.assertEqual(M.explain(b,(10,(0,2,4),40),self.f99)["total_necessary_records"],1)
        x=M.explain(b,(10,(0,),40),self.f99)
        self.assertEqual(x["status"],"NO_NATIVE_PATH")
        self.assertEqual(x["exact_lex_first_witness"],[])
        self.assertEqual(x["single_record_interventions"],[])

    def test_repeated_use_of_one_record_is_bounded_and_source_grounded(self):
        mem=((100,200,(0,)),)
        sig=(100,(0,1),100)
        x=M.explain(mem,sig,self.f99)
        self.assertEqual(x["status"],"STRUCTURAL_PATH_FOUND")
        self.assertEqual([p["record_index"] for p in x["exact_lex_first_witness"]],
                         [0,0])
        self.assertEqual(x["total_necessary_records"],1)

    def test_invalid_role_code_endpoints_or_overbudget_fail_closed(self):
        for mem in (((1,2,(8,)),),((1,1,(0,)),),
                    tuple((a,a+1,(0,)) for a in range(13)),
                    ((1,2,()),),((1,2,(0,1,2,3,4,5,6)),)):
            with self.subTest(mem=mem):
                with self.assertRaises(ValueError):
                    M.explain(mem,(1,(0,),2),self.f99)

    def test_bounded_search_raises_instead_of_claiming_partial_trace(self):
        with self.assertRaisesRegex(M.AttributionBoundExceeded,
                                    "F101_WITNESS_STATE_BOUND"):
            M.explain(BASE,(10,(0,2,4,6),14),self.f99,max_states=1)

    def test_memory_not_mutated_by_deletion_role_ablations(self):
        original=tuple(BASE)
        proof=M.explain(original,(10,(0,2,4,6),14),self.f99)
        self.assertEqual(original,BASE)
        self.assertEqual(proof["memory_structural_sha256"],M.memory_digest(BASE))
        self.assertEqual(M.role_shift((10,11,(0,3))),(10,11,(2,5)))

    def test_disconnected_endpoint_and_wrong_signed_role_do_not_match(self):
        mem=((1,2,(0,)),(9,10,(2,)))
        self.assertEqual(M.explain(mem,(1,(0,2),10),self.f99)["status"],
                         "NO_NATIVE_PATH")
        self.assertEqual(M.explain(BASE,(10,(0,3,4,6),14),self.f99)["status"],
                         "NO_NATIVE_PATH")

    def test_pack_is_real_native_codec_on_separate_unregistered_smoke_only(self):
        pack=self.native.codec()
        input_record=pack.edge_record((10,0,11))
        self.assertEqual(len(pack.pack(*input_record)),12)
        self.assertEqual(pack.unpack(pack.pack(*input_record)),input_record)
        self.assertTrue(M.frozen_sources()[0] is not None)

if __name__=="__main__":
    unittest.main()

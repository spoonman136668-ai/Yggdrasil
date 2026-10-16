"""F96 same-graph arrival-pair and no-query public-descriptor contracts."""
from __future__ import annotations
import importlib.util,inspect,sys,unittest
from pathlib import Path
file=Path(__file__).with_name("paired_order_probe.py")
spec=importlib.util.spec_from_file_location("f96_pure_contract",file)
M=importlib.util.module_from_spec(spec);sys.modules[spec.name]=M
spec.loader.exec_module(M)
class Source:
    def shift(self,public,family):
        if family%2==0:return tuple(public),"original"
        return tuple(v for i in range(0,72,4)
                     for v in (public[i+1],public[i+2],public[i+3],public[i])),"local_rotate4"
class Native:
    def _f60_step(self,memory,event,pack):
        after=memory+((event[0],event[2],(event[1]*2,)),)
        return after[-12:]
    def actions(self,memory,event,index,pack):
        b=self._f60_step(memory,event,pack)
        return (("append",-1,-1,b,()),)
    def _valid_memory(self,mem,pack):
        assert len(mem)<=12
class Tests(unittest.TestCase):
    def setUp(self):
        self.public=tuple((i,i%4,i+1) for i in range(72))
    def test_inverse_is_true_rotation_inverse(self):
        src=Source();rotated,_=src.shift(self.public,-1)
        self.assertEqual(M.undo_rotate4(rotated),self.public)
        self.assertNotEqual(rotated,self.public)
    def test_pair_same_public_graph_both_source_regimes(self):
        src=Source();rotated,_=src.shift(self.public,-1)
        for observed,name in ((self.public,"original"),(rotated,"local_rotate4")):
            a,b=M.matched_orders(observed,name,src)
            self.assertEqual(a,self.public)
            self.assertEqual(b,rotated)
    def test_mismatched_source_regime_fails(self):
        with self.assertRaises(AssertionError):
            M.matched_orders(self.public,"local_rotate4",Source())
        with self.assertRaises(AssertionError):
            M.matched_orders(self.public,"unsupported",Source())
    def test_public_descriptors_do_not_see_question(self):
        self.assertEqual(tuple(inspect.signature(M.public_prefix_descriptors).parameters),
                         ("public","pack","F62"))
        report=M.public_prefix_descriptors(self.public,None,Native())
        self.assertEqual(report["prefix_positions"],36)
        self.assertEqual(report["native_alternatives"],0)
        self.assertLessEqual(report["final_record_count"],12)
    def test_paired_summaries_use_exact_same_graph(self):
        def side(right,rescue,touch):
            return dict(f60_correct=int(right),rescue_feasible=int(rescue),
                        harmful_alternative_exists=int(right),
                        legal_single_deviation_actions=10,
                        public_descriptors={"directed_memory_joins":touch,
                                            "memory_endpoint_touches":touch,
                                            "native_alternatives":0})
        rows=[dict(question_type="crosslink_reach_6_steps",
                   original=side(False,False,1),rotated=side(True,False,2)),
              dict(question_type="within_component_4_steps",
                   original=side(True,False,3),rotated=side(False,False,4))]
        result=M.paired_summary(rows)
        self.assertEqual(result["graphs"],2)
        self.assertEqual(result["episodes"],4)
        self.assertEqual(result["F60_rotated_only_correct"],1)
        self.assertEqual(result["F60_original_only_correct"],1)
        self.assertEqual(result["joins_observed_original"],4)
        self.assertEqual(result["joins_observed_rotated"],6)
    def test_invalid_length_source_fails(self):
        with self.assertRaises(AssertionError):
            M.undo_rotate4(self.public[:-1])
if __name__=="__main__":
    unittest.main()

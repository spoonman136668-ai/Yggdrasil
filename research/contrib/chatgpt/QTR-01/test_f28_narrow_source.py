"""F28 source-free association identity and two-hop provenance negatives."""
import json
import unittest

from f28_narrow_source import (
    capture, endpoints_prioritizing_bridge, preflight, source_rows, NotAdmitted,
    SEEDS, PROPS,
)
from f27_versioned_entitydata import LiveEntityData
from test_f27_versioned_entitydata import Response, entity, item_claim


class Stub:
    def __init__(self, *, tamper=False, no_bridge=False, unbound=False, missing_label=False):
        self.tamper=tamper
        self.no_bridge=no_bridge
        self.unbound=unbound
        self.missing_label=missing_label
        self.calls=[]
    def open(self, req, timeout):
        self.calls.append(req.full_url)
        assert timeout==15
        id_=req.full_url.rsplit("/",1)[-1].split(".json")[0]
        assert id_ in SEEDS+PROPS+("Q2250224",)
        x=entity(id_,"independent label "+id_)
        if id_=="Q42":
            x["claims"]={"P31":[item_claim("Q42","P31","Q5",1)]}
        if id_=="Q5" and not self.no_bridge:
            x["claims"]={"P279":[item_claim("Q99" if self.unbound else "Q5","P279","Q2250224",2)]}
        if self.tamper and id_=="Q42" and "revision=" in req.full_url:
            x["labels"]["en"]["value"]="tampered source"
        if self.missing_label and id_=="Q2250224":
            x["labels"]={}
        return Response(json.dumps({"entities":{id_:x}}).encode())


class F28(unittest.TestCase):
    def test_sealed_smaller_cohort_and_read_budget(self):
        x=preflight()
        self.assertEqual(x["schema"],"yggdrasil.qtr01.f28.versioned-narrow-knowledge-snapshot.v1")
        self.assertEqual((len(SEEDS),len(PROPS),x["endpoint_budget"]),(2,8,24))

    def test_fixture_live_shape_proves_two_hop_and_cold_restore(self):
        stub=Stub()
        obj=capture(LiveEntityData(opener=stub))
        self.assertEqual(obj["carrier_summary"]["admitted_semantic_edges"],2)
        self.assertEqual(obj["carrier_summary"]["twohop_compositions_checked"],1)
        self.assertTrue(obj["carrier_summary"]["equal_info_symbolic_control_parity"])
        self.assertTrue(obj["carrier_summary"]["cold_restore_exact"])
        self.assertEqual(obj["carrier_summary"]["numeric_carrier_bytes"],24)
        self.assertEqual(obj["endpoint_count"],1)
        self.assertEqual(len(obj["source_request_receipts"]),2+2+1+8)
        self.assertFalse(obj["native_model_weights_edited"])
        self.assertFalse(obj["scientific_pass"])
        self.assertTrue(any(row["o_label"]=="independent label Q2250224"
                            for row in obj["admitted_rows"]))

    def test_source_revision_tampering_fails(self):
        with self.assertRaises(NotAdmitted):
            capture(LiveEntityData(opener=Stub(tamper=True)))

    def test_no_path_learned_no_silent_promotion(self):
        with self.assertRaises(NotAdmitted):
            capture(LiveEntityData(opener=Stub(no_bridge=True)))

    def test_unbound_provenance_or_unlabeled_bridge_never_admitted(self):
        for opts in ({"unbound":True},{"missing_label":True}):
            with self.subTest(opts=opts):
                with self.assertRaises(NotAdmitted):
                    capture(LiveEntityData(opener=Stub(**opts)))

    def test_causal_source_and_endpoint_priority_are_deterministic(self):
        source={
            "Q42":entity("Q42","Douglas Adams",{"P31":[item_claim("Q42","P31","Q5")]}),
            "Q5":entity("Q5","human",{"P279":[item_claim("Q5","P279","Q2250224")]})
        }
        rows,inventory=source_rows(source)
        self.assertEqual(len(rows),2)
        self.assertFalse(inventory["truncated"])
        self.assertEqual(endpoints_prioritizing_bridge(rows),["Q2250224"])


if __name__=="__main__":
    unittest.main()

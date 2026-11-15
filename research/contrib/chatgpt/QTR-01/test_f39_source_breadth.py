"""F39 frozen FIT-only breadth: synthetic negatives; never query Wikidata."""
import json
import tempfile
import unittest
from pathlib import Path

from f26_semantic_association import NotAdmitted, digest
from f39_source_breadth import (
    ROOTS, RESERVED, PROPS, POLICY, preflight, extract, paths_for, capture,
)


def claim(subject, pid, object_, n, qualified=False, rank="normal"):
    return {
        "id":subject+"$synthetic-"+str(n),
        "rank":rank,
        "mainsnak":{"snaktype":"value",
                    "datavalue":{"value":{"entity-type":"item","id":object_}}},
        **({"qualifiers":{"P580":[]}} if qualified else {}),
    }


class FakeReader:
    def __init__(self, qualified_second=False, reserved=False, revision_drift=False, unlabeled_target=False):
        self.qualified_second=qualified_second
        self.reserved=reserved
        self.revision_drift=revision_drift
        self.unlabeled_target=unlabeled_target
        self.receipts=[]
        self.total_bytes=0
        self.calls=[]

    def fetch(self, qid, revision=None):
        if qid in RESERVED:
            raise AssertionError("RESERVED_UNSEEN_ROOT_WAS_READ")
        self.calls.append((qid,revision))
        claims={}
        if qid in ROOTS:
            pos=ROOTS.index(qid)
            first = "Q"+str(900001+2*pos)
            second = "Q142" if self.reserved and pos==0 else "Q"+str(900002+2*pos)
            claims={
                "P31":[claim(qid,"P31",first,1)],
                "P279":[claim(qid,"P279",second,2)]
            }
        elif qid.startswith("Q9000"):
            idx=int(qid[1:])-900001
            qualified=self.qualified_second
            claims={
                "P17":[claim(qid,"P17","Q"+str(990001+2*idx),3,qualified)],
                "P31":[claim(qid,"P31","Q"+str(990002+2*idx),4,qualified)]
            }
        labels={"en":{"language":"en","value":"synthetic label "+qid}}
        if self.unlabeled_target and qid.startswith("Q9900"):
            labels={}
        ent={"id":qid,"lastrevid":123456,"claims":claims,"labels":labels}
        if self.revision_drift and revision is not None and qid==ROOTS[0]:
            ent["lastrevid"]+=1
        self.receipts.append({"entity":qid,"revision":ent["lastrevid"],
                              "synthetic_only":True})
        self.total_bytes+=120
        return ent,digest(ent)


class F39Tests(unittest.TestCase):
    def test_frozen_protocol_and_sealed_nonoverlapping_roots(self):
        p=preflight()
        self.assertEqual(len(ROOTS),8)
        self.assertEqual(len(RESERVED),4)
        self.assertFalse(set(ROOTS)&set(RESERVED))
        self.assertEqual(p["headroom"]["min_distinct_fit_roots_with_composable_paths"],5)

    def test_frozen_rules_fail_closed_on_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=json.loads(POLICY.read_text())
            d["caps"]["max_total_gets"]+=1
            path=Path(tmp)/"changed.json"
            path.write_text(json.dumps(d))
            with self.assertRaisesRegex(NotAdmitted,"FROZEN_POLICY_DRIFT"):
                preflight(path)

    def test_broad_source_synthetic_fixture_reaches_structural_eligibility_only(self):
        reader=FakeReader()
        result=capture(reader)
        self.assertEqual(result["headroom_status"],"FIT_SOURCE_BREADTH_PRESENT")
        self.assertEqual(len(result["fit_roots_with_twohop"]),8)
        self.assertEqual(len(result["fit_groups_with_twohop"]),5)
        self.assertEqual(len(result["fit_relation_pairs"]),4)
        self.assertEqual(len(result["fit_query_signatures"]),32)
        self.assertEqual(result["labeled_witnessed_rows"],48)
        self.assertEqual(result["graph_fit_root_twohop_paths"],32)
        self.assertEqual(result["reserved_unseen_read_count"],0)
        self.assertLessEqual(result["source_http_get_count"],100)
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["native_model_weights_edited"])
        self.assertFalse(result["protected_scientific_first_use_consumed"])

    def test_source_unqualified_expansion_negative_is_no_headroom(self):
        result=capture(FakeReader(qualified_second=True))
        self.assertEqual(result["headroom_status"],"INSUFFICIENT_SOURCE_HEADROOM")
        self.assertEqual(result["graph_fit_root_twohop_paths"],0)
        self.assertEqual(result["labeled_witnessed_rows"],16)

    def test_reserved_subject_and_object_are_never_read_or_admitted(self):
        reader=FakeReader(reserved=True)
        result=capture(reader)
        self.assertEqual(result["reserved_unseen_read_count"],0)
        self.assertTrue(all(qid not in RESERVED for qid,rev in reader.calls))
        self.assertTrue(all(r["s"] not in RESERVED and r["o"] not in RESERVED
                            for r in result["witnessed_rows"]))

    def test_revision_pin_detects_first_party_content_drift(self):
        with self.assertRaisesRegex(NotAdmitted,"PINNED_REVISION_MISMATCH"):
            capture(FakeReader(revision_drift=True))

    def test_unlabeled_endpoints_not_invented(self):
        result=capture(FakeReader(unlabeled_target=True))
        self.assertEqual(result["labeled_witnessed_rows"],16)
        self.assertEqual(result["headroom_status"],"INSUFFICIENT_SOURCE_HEADROOM")

    def test_qualified_deprecated_unbound_never_accepted(self):
        x=FakeReader().fetch(ROOTS[0])[0]
        x["claims"]["P31"] += [
            claim(ROOTS[0],"P31","Q555500",8,qualified=True),
            claim(ROOTS[0],"P31","Q555501",9,rank="deprecated"),
            claim("Q999","P31","Q555502",10)]
        rows, inventory=extract(x,ROOTS[0],4)
        self.assertEqual(len(rows),2)
        self.assertGreaterEqual(inventory["rejected_invalid"],3)

    def test_no_unwitnessed_graph_path(self):
        a=[{"s":"Q2","p":"P31","o":"Q900001","source_claim":"Q2$a"}]
        b=[{"s":"Q900001","p":"P279","o":"Q123","source_claim":"Q900001$b"}]
        self.assertEqual(paths_for(a),[])
        self.assertEqual(len(paths_for(a+b)),1)
        self.assertEqual(paths_for(a+[{"s":"Q900001","p":"P279","o":"Q142","source_claim":"Q900001$x"}]),[])


if __name__=="__main__":
    unittest.main()

"""CAP02 native evidence recall: stage, leakage, source and cold replay controls."""
import hashlib
import importlib.util
import json
import pathlib
import unittest

from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_evidence_recall import EvidenceRecall,context
from yggdrasil.native_segmented_continuation import SegmentedNativeJEPA

ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/contrib/chatgpt/YGG-CAP02/source.py"
ORIGINAL=ROOT/"research/contrib/chatgpt/YGG-CAP01/original/linux/seed-14071-state.json"

def source():
    spec=importlib.util.spec_from_file_location("cap02_test_source",SOURCE)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def original_model():
    data=json.loads(ORIGINAL.read_bytes())
    blob=data["continued_ascii"].encode("ascii")
    assert digest(blob)==data["continued_sha256"]
    return SegmentedNativeJEPA.restore(blob,digest(blob))

class NativeEvidenceRecallTests(unittest.TestCase):
    def test_evidence_is_not_read_before_witness(self):
        gate=EvidenceRecall()
        source_id=hashlib.sha256(b"cap02-test-1").hexdigest()
        a=gate.predict("transition",(0,1),1,.8,.2)
        self.assertEqual(a["archive_weight"],.5)
        self.assertEqual(a["support"],0)
        gate.witness(source_id,"transition",(0,1),1,1,.8,.2)
        b=gate.predict("transition",(0,1),1,.8,.2)
        self.assertEqual(b["archive_weight"],.5)
        self.assertEqual(b["support"],1)
        self.assertEqual(b["prob"],a["prob"])
        self.assertEqual(gate.checkpoint(),
                         EvidenceRecall.restore(
                             gate.checkpoint(),digest(gate.checkpoint())
                         ).checkpoint())

    def test_context_specific_evidence_selects_better_predictor(self):
        gate=EvidenceRecall()
        for i in range(5):
            gate.witness(hashlib.sha256(f"event{i}".encode()).hexdigest(),
                         "transition",(1,0),0,1,.9,.1)
        good=gate.predict("transition",(1,0),0,.9,.1)
        unused=gate.predict("transition",(0,1),0,.9,.1)
        self.assertGreater(good["archive_weight"],.9)
        self.assertEqual(good["support"],5)
        self.assertEqual(unused["archive_weight"],.5)
        self.assertEqual(unused["support"],0)

    def test_source_replay_conflict_and_stage_mismatch(self):
        gate=EvidenceRecall()
        sha=hashlib.sha256(b"evt").hexdigest()
        gate.witness(sha,"transition",(1,1),0,0,.7,.3)
        with self.assertRaisesRegex(ValueError,"WITNESS_REPLAY"):
            gate.witness(sha,"transition",(1,1),0,1,.7,.3)
        with self.assertRaisesRegex(ValueError,"STAGE_ONE_CLOCK"):
            gate.predict("transition",(1,1),0,.5,.5,0,1)
        with self.assertRaisesRegex(ValueError,"PUBLIC_BIT"):
            gate.predict("terminal",(1,2),0,.5,.5,1,0)

    def test_cold_rehashed_forged_evidence_rejected(self):
        gate=EvidenceRecall()
        sha=hashlib.sha256(b"evt").hexdigest()
        gate.witness(sha,"terminal",(0,1),1,0,.7,.2,1,1)
        raw=gate.checkpoint()
        obj=json.loads(raw)
        obj["events"][0][2][1]=1
        tampered=canonical(obj)
        with self.assertRaisesRegex(ValueError,"COLD_REJECTED"):
            EvidenceRecall.restore(tampered,digest(tampered))

    def test_fresh_disjoint_source_on_cumulative_checkpoint(self):
        model=original_model()
        s=source()
        self.assertEqual(model.total_count,1054)
        old_sha=digest(model.checkpoint())
        start=model._events[-1][6]
        new=s.generate(99721,start)
        self.assertEqual(len(new),32)
        self.assertEqual(new[0]["views"],
                         ((start[0],start[1]),(start[1],start[2])))
        self.assertTrue(set(e["id"] for e in new).isdisjoint(
            e[0] for e in model._history()))
        self.assertEqual(digest(model.checkpoint()),old_sha)
        for i in range(3):
            item=new[i]
            model=model.observe(item["id"],item["views"],
                                item["row"],item["post"])
        self.assertEqual(model.total_count,1057)
        self.assertEqual(model.new_count,35)
        self.assertEqual(digest(model._archive_raw),
                         digest(original_model()._archive_raw))

if __name__=="__main__":
    unittest.main()

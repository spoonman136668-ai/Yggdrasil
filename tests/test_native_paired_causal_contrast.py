"""CAP03 causal intervention identity, forecast clock and native custody tests."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_paired_causal_contrast import (
    ARMS,PairedCausalContrast,
)
from yggdrasil.native_evidence_recall import restore_original_sealed_native

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/"research/contrib/chatgpt/YGG-CAP03"
ORIGINAL=(ROOT/"research/contrib/chatgpt/YGG-CAP02/original"/
          ("windows" if sys.platform=="win32" else "linux")/
          "seed-14071-state.json")

def source():
    spec=importlib.util.spec_from_file_location(
        "cap03_frozen_source",HERE/"source.py")
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def prior():
    data=json.loads(ORIGINAL.read_bytes())
    raw=data["model_ascii"].encode("ascii")
    assert digest(raw)==data["model_sha256"]
    return restore_original_sealed_native(raw,digest(raw))

class PairedActionCausalTests(unittest.TestCase):
    def test_actual_sequential_native_parent_is_source_locked(self):
        model=prior()
        self.assertEqual(model.total_count,1086)
        self.assertEqual(model.new_count,64)
        original=model.checkpoint()
        s=source()
        tape=s.generate(99811,model._events[-1][6])
        self.assertEqual(len(tape),32)
        self.assertEqual(len({e["id"] for e in tape}),32)
        self.assertEqual(
            tape[0]["views"],
            ((model._events[-1][6][0],model._events[-1][6][1]),
             (model._events[-1][6][1],model._events[-1][6][2]))
        )
        for i,e in enumerate(tape):
            self.assertEqual(e["chosen"],s.chosen(99811,i))
            self.assertEqual(tuple(x["action"] for x in e["forks"]),ARMS)
            self.assertEqual(e["selected"]["s2"],e["post"][1])
            # Second future action cannot causally affect prior s2.
            self.assertEqual(e["forks"][0]["s2"],e["forks"][1]["s2"])
            self.assertEqual(e["forks"][2]["s2"],e["forks"][3]["s2"])
        new=tape[0]
        after=model.observe(new["id"],new["views"],
                            new["selected"],new["post"])
        self.assertEqual(after.total_count,1087)
        self.assertEqual([len(s._ledger) for s in after._segments],[64,1])
        self.assertEqual(after._archive_raw,model._archive_raw)
        self.assertEqual(model.checkpoint(),original)

    def test_forecasts_are_pure_prequential_readouts(self):
        s=source()
        forks=s.generate(99811,(0,1,0))[0]
        learner=PairedCausalContrast()
        before=learner.checkpoint()
        for arm in ARMS:
            self.assertAlmostEqual(
                learner.forecast(forks["views"],arm,"transition"),.5)
            p=learner.forecast(forks["views"],arm,"terminal",0)
            self.assertAlmostEqual(p,.5)
        self.assertEqual(learner.checkpoint(),before)
        with self.assertRaisesRegex(ValueError,"FIRST_STAGE_NO_FUTURE_SENSOR"):
            learner.forecast(forks["views"],(0,1),"transition",1)

    def test_true_matched_interventions_learn_not_only_store(self):
        s=source();e=s.generate(99811,(0,1,0))[0]
        correct=PairedCausalContrast();sham=PairedCausalContrast(mispair=True)
        for i in range(10):
            identifier=hashlib.sha256(f"fork{i}".encode()).hexdigest()
            correct.observe(identifier,e["views"],e["forks"])
            sham.observe(identifier,e["views"],e["forks"])
        self.assertEqual(correct.count,10)
        c=[correct.forecast(e["views"],a,"transition") for a in ARMS]
        s=[sham.forecast(e["views"],a,"transition") for a in ARMS]
        self.assertNotEqual(c,s)
        raw=correct.checkpoint()
        self.assertEqual(
            PairedCausalContrast.restore(raw,digest(raw)).checkpoint(),raw)

    def test_duplicate_and_rehashed_structural_forgery_rejected(self):
        s=source();e=s.generate(99811,(1,0,1))[0]
        learner=PairedCausalContrast().observe(
            e["id"],e["views"],e["forks"])
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            learner.observe(e["id"],e["views"],e["forks"])
        with self.assertRaisesRegex(ValueError,"WITNESSED_ACTION_ORDER"):
            swapped=list(e["forks"])
            swapped[0],swapped[1]=swapped[1],swapped[0]
            PairedCausalContrast().observe(
                hashlib.sha256(b"bad").hexdigest(),e["views"],
                tuple(swapped))
        data=json.loads(learner.checkpoint())
        data["events"][0][2][0][0]=[1,1]
        forged=canonical(data)
        with self.assertRaisesRegex(ValueError,"COLD_REJECTED"):
            PairedCausalContrast.restore(forged,digest(forged))

    def test_hidden_labels_cannot_change_public_feature_forecast(self):
        e=source().generate(99811,(1,1,0))[0]
        native=PairedCausalContrast()
        first=native.forecast(e["views"],(1,1),"transition")
        metadata=dict(e,phase="PRIVATE_REDACTED",family="UNKNOWN")
        second=native.forecast(metadata["views"],(1,1),"transition")
        self.assertEqual(first,second)

if __name__=="__main__":
    unittest.main()

"""Focused YGG-CAP02 original native causal-memory and negative controls."""
from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path
import unittest
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_segmented_continuation import SegmentedNativeJEPA
from yggdrasil.native_causal_rule_memory import (
    CausalMemory,CausalPosterior,MAX_BANKS,NOISE,BANK_SIZE
)

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"research/contrib/chatgpt/YGG-CAP02"
ORIGINAL=ROOT/"research/contrib/chatgpt/YGG-CAP01/original"/("windows" if sys.platform=="win32" else "linux")
SOURCES={
    14071:(99811,"2d08c7e2d6d4d80acfc53727cdd0880d3f632c0f44bdb405b78feffba405938e" if sys.platform=="win32" else "6babc23f4baf30afde14db5f2ca8eb3e55e321169aa245482478ff9855b68f14"),
    14072:(99829,"e09b0cbbe47b95686f3ed3732baf080fe6b47301f0128c360437bf29bf9dfbfb" if sys.platform=="win32" else "c503ccf979f90d6d4954f0e8d42133fc177017d4b47de80ee64c9524b870d827"),
}

def source():
    s=importlib.util.spec_from_file_location("cap02_test_source",DIR/"source.py")
    mod=importlib.util.module_from_spec(s)
    s.loader.exec_module(mod)
    return mod

def model(old_seed):
    pin=SOURCES[old_seed][1]
    payload=json.loads((ORIGINAL/f"seed-{old_seed}-state.json").read_bytes())
    raw=payload["continued_ascii"].encode("ascii")
    assert digest(raw)==pin==payload["continued_sha256"]
    return SegmentedNativeJEPA.restore(raw,pin)

class CAP02NativeMemoryTests(unittest.TestCase):
    def test_source_disjoint_two_old_models_and_public_chronology(self):
        src=source()
        self.assertEqual(BANK_SIZE,16)
        self.assertEqual(MAX_BANKS,5)
        self.assertEqual(NOISE,.075)
        for old_seed,(seed,_) in SOURCES.items():
            old=model(old_seed)
            new=src.generate(seed)
            self.assertEqual(len(new),48)
            self.assertEqual([sum(e["phase"]==tag for e in new)
                              for tag in ("A","B","A_return")],[16,16,16])
            self.assertEqual(new[0]["views"],
                ((old._events[-1][6][0],old._events[-1][6][1]),
                 (old._events[-1][6][1],old._events[-1][6][2])))
            self.assertFalse({x["identifier"] for x in new}&
                             {x[0] for x in old._events})
            self.assertEqual(new,src.generate(seed))

    def test_original_two_causal_banks_fitted_from_cap01_witnesses(self):
        for old_seed in SOURCES:
            parent=model(old_seed)
            before=parent.checkpoint()
            mem=CausalMemory.from_native(parent)
            self.assertEqual(mem.bank_sizes,(16,16))
            self.assertEqual(mem.new_count,0)
            self.assertEqual(mem.total,32)
            self.assertEqual(parent.checkpoint(),before)
            self.assertTrue(all(
                b.transition.updates==b.reward.updates==16
                for b in mem._banks))

    def test_prequential_stage_public_actions_purity_and_controls(self):
        parent=model(14071)
        mem=CausalMemory.from_native(parent)
        src=source()
        event=src.generate(99811)[0]
        views=event["views"]
        a,b=event["actions"]
        before=mem.checkpoint()
        for arm in ("evidence","uniform","latest","action_masked"):
            p=mem.forecast(views,a,variant=arm)
            q=mem.forecast(views,a,event["row"]["s2"],b,variant=arm)
            self.assertTrue(0<=p<=1 and 0<=q<=1)
        self.assertEqual(mem.checkpoint(),before)
        with self.assertRaises(ValueError):
            mem.forecast(views,a,None,b)
        with self.assertRaises(ValueError):
            mem.forecast(views,a,variant="hidden_phase_oracle")
        # Evaluator labels and hidden regime family are not arguments.
        self.assertEqual(mem.forecast(views,a),
                         mem.forecast(dict(event,phase="X")["views"],a))

    def test_actual_48_new_witnesses_and_frozen_old_posterior(self):
        parent=model(14071)
        original=parent.checkpoint()
        m=CausalMemory.from_native(parent)
        frozen=[(b.transition.snapshot(),b.reward.snapshot())
                for b in m._banks]
        for e in source().generate(99811):
            m.observe(e["identifier"],e["views"],e["row"],e["post"])
        self.assertEqual(m.bank_sizes,(16,16,16,16,16))
        self.assertEqual(m.new_count,48)
        self.assertEqual(m.total,80)
        self.assertEqual(parent.checkpoint(),original)
        for b,(before_t,before_r) in zip(m._banks,frozen):
            self.assertEqual(b.transition.snapshot(),before_t)
            self.assertEqual(b.reward.snapshot(),before_r)
        raw=m.checkpoint()
        self.assertEqual(
            CausalMemory.restore(raw,digest(raw),parent._events).checkpoint(),
            raw)

    def test_rehashed_forged_weight_and_source_rejected(self):
        parent=model(14072)
        m=CausalMemory.from_native(parent)
        e=source().generate(99829)[0]
        m.observe(e["identifier"],e["views"],e["row"],e["post"])
        raw=m.checkpoint()
        d=json.loads(raw)
        d["banks"][0]["transition"]["weights"][0]+=.1
        fake=canonical(d)
        with self.assertRaisesRegex(ValueError,"COLD_REPLAY_REJECTED"):
            CausalMemory.restore(fake,digest(fake),parent._events)
        with self.assertRaises(ValueError):
            CausalMemory.restore(raw,"0"*64,parent._events)
        d=json.loads(raw)
        d["new_events"][0][5]=1-d["new_events"][0][5]
        fake=canonical(d)
        with self.assertRaises(ValueError):
            CausalMemory.restore(fake,digest(fake),parent._events)

    def test_source_replay_not_training_twice(self):
        parent=model(14071)
        m=CausalMemory.from_native(parent)
        e=source().generate(99811)[0]
        m.observe(e["identifier"],e["views"],e["row"],e["post"])
        with self.assertRaises(ValueError):
            m.observe(e["identifier"],e["views"],e["row"],e["post"])
        altered=dict(e["row"],y=1-e["row"]["y"])
        with self.assertRaises(ValueError):
            m.observe(e["identifier"],e["views"],altered,e["post"])
        self.assertEqual(m.new_count,1)

    def test_rule_posterior_learns_from_actual_bit_outcomes(self):
        p=CausalPosterior(4)
        a=(1,0,0,1)
        before=p.predict(a)
        for _ in range(8):
            p.learn(a,1)
        self.assertGreater(p.predict(a),before+.1)
        self.assertEqual(p.updates,8)

if __name__=="__main__":
    unittest.main()

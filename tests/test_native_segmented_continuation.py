"""YGG-CAP01 native source and six-head capacity/retention contract tests."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import MAX_EPISODES
from yggdrasil.native_segmented_continuation import (
    SegmentedNativeJEPA,
)

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/"research/contrib/chatgpt/YGG-CAP01"
PREVIOUS=ROOT/"research/contrib/chatgpt/YGG-JEPA2-05/original/linux"
PINS={
    14071:"646058e49adf75d2cf74b16b901e801b24ea38f017a717d68fe65a93ab4cad9e",
    14072:"ef8e1b6daa9b0349d675aee6c30a79d759d6e21c460b5fc900461417c1970609",
}

def source():
    spec=importlib.util.spec_from_file_location("cap01_source",HERE/"source.py")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def original(seed):
    d=json.loads((PREVIOUS/f"seed-{seed}-state.json").read_bytes())
    raw=d["model_ascii"].encode("ascii")
    assert digest(raw)==d["model_sha256"]==PINS[seed]
    return raw

def train_few(count=3):
    state=SegmentedNativeJEPA.from_archive(original(14071),PINS[14071])
    events=source().generate(99601)
    for e in events[:count]:
        state=state.observe(e["identifier"],e["views"],e["row"],e["post"])
    return state,events

class NativeSegmentedContinuationTests(unittest.TestCase):
    def test_legacy_cap_remains_unmodified(self):
        self.assertEqual(MAX_EPISODES,1024)

    def test_restore_genuine_learned_original_on_both_seeds(self):
        for seed,n in ((14071,1022),(14072,997)):
            raw=original(seed)
            state=SegmentedNativeJEPA.from_archive(raw,digest(raw))
            self.assertEqual(state.original_count,n)
            self.assertEqual(state.new_count,0)
            self.assertEqual(state.archive_sha256,digest(raw))
            self.assertEqual(state.total_count,n)
            self.assertTrue(state._validate_custody())
            self.assertEqual(state._source.checkpoint(),raw)

    def test_genuine_training_crosses_old_1024_capacity(self):
        model,events=train_few(3)
        self.assertEqual(model.original_count,1022)
        self.assertEqual(model.total_count,1025)
        self.assertEqual(model.future_windows,1)
        self.assertEqual(model._source.checkpoint(),original(14071))
        self.assertEqual([z.steps for z in model._one],[9,9])
        self.assertEqual([z.steps for z in model._temporal],[9,9])
        self.assertEqual([z.windows for z in model._future],
                         [z.windows+1 for z in
                          (model._source.sensory,model._source.reward)])

    def test_archive_old_native_reads_exact_before_after(self):
        initial=SegmentedNativeJEPA.from_archive(original(14071),PINS[14071])
        view=(0,1)
        before=(initial.archived_forecast(view,0),
                initial.archived_forecast(view,0,1,0))
        state,_=train_few(4)
        after=(state.archived_forecast(view,0),
               state.archived_forecast(view,0,1,0))
        self.assertEqual(before,after)
        self.assertNotEqual(initial._source.original.base.native.info()["count"],
                            state.total_count)

    def test_future_forecast_public_actions_only_and_read_purity(self):
        state,events=train_few(4)
        s=source()
        plans=tuple(s.announced_plan(99601,i) for i in range(4,7))
        snapshot=state.checkpoint()
        f=state.future_forecast(events[4]["views"],plans)
        self.assertEqual(len(f),6)
        self.assertTrue(all(0<=p<=1 for p in f))
        self.assertEqual(state.checkpoint(),snapshot)
        with self.assertRaises(ValueError):
            state.future_forecast(events[4]["views"],plans[:2])
        with self.assertRaises(ValueError):
            state.archived_forecast((0,1),0,1,None)

    def test_duplicate_noop_conflict_and_private_row_fail(self):
        state,events=train_few(3)
        e=events[0]
        self.assertIs(state,state.observe(
            e["identifier"],e["views"],e["row"],e["post"]))
        wrong=dict(e["row"],y=1-e["row"]["y"])
        with self.assertRaises(ValueError):
            state.observe(e["identifier"],e["views"],wrong,e["post"])
        with self.assertRaises(ValueError):
            state.observe("not_sha",e["views"],e["row"],e["post"])
        with self.assertRaises(ValueError):
            state.observe(hashlib.sha256(b"badpost").hexdigest(),
                          e["views"],e["row"],(0,0,1-e["row"]["s2"]))

    def test_checkpoint_bytes_cold_and_independent_forgery_reject(self):
        model,_=train_few(4)
        raw=model.checkpoint()
        restored=SegmentedNativeJEPA.restore(raw,digest(raw))
        self.assertEqual(restored.checkpoint(),raw)
        with self.assertRaises(ValueError):
            SegmentedNativeJEPA.restore(raw,"0"*64)
        d=json.loads(raw)
        d["one"][0]["predictor_bias"][0]+=.1
        forged=canonical(d)
        with self.assertRaises(ValueError):
            SegmentedNativeJEPA.restore(forged,digest(forged))

    def test_shard_rollover_with_frozen_capacity_override(self):
        from yggdrasil import native_segmented_continuation as module
        size=module.MAX_SHARD
        module.MAX_SHARD=2
        try:
            model,events=train_few(3)
            self.assertEqual(len(model._segments),2)
            self.assertEqual([len(x._ledger) for x in model._segments],[2,1])
            self.assertEqual(model.total_count,1025)
            raw=model.checkpoint()
            self.assertEqual(
                module.SegmentedNativeJEPA.restore(raw,digest(raw)).checkpoint(),
                raw)
        finally:
            module.MAX_SHARD=size

if __name__=="__main__":
    unittest.main()

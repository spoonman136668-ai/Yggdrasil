"""YGG-RET01 exact pinned native readout retrieval engineering negatives."""
import importlib.util
import json
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_readout_retention import (
    ArchivedEvidenceReadout,PRIOR_ARCHIVED,POSTERIOR_FLOOR,POSTERIOR_CEIL,
)

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/"research/contrib/chatgpt/YGG-RET01"


def src():
    spec=importlib.util.spec_from_file_location("ygg_ret01_unit_source",HERE/"source.py")
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def inputs(seed=14071):
    old=json.loads((HERE.parent/"YGG-JEPA2-03"/f"seed-{seed}-state.json").read_bytes())
    new=json.loads((HERE.parent/"YGG-JEPA2-04"/f"seed-{seed}-state.json").read_bytes())
    a=old["state_ascii"].encode("ascii")
    b=new["checkpoint_ascii"].encode("ascii")
    assert digest(a)==old["state_sha256"]
    assert digest(b)==new["checkpoint_sha256"]
    return a,b


class RetentionTest(unittest.TestCase):
    def test_public_source_is_disjoint_and_phase_is_evaluator_only(self):
        source=src()
        original=set()
        for seed in source.SEEDS:
            for world in source.WORLDS:
                records=source.generate(seed,world)
                self.assertEqual(records,source.generate(seed,world))
                self.assertEqual(len(records),32)
                self.assertEqual(
                    [records[t]["phase"] for t in (0,8,16,20,24,28)],
                    ["warm_A","stable_A","early_B","late_B",
                     "early_return_A","late_return_A"])
                for row in records:
                    self.assertEqual(
                        set(row),{"source_id","views","row",
                                  "seed","world","index","phase"})
                    self.assertNotIn(row["source_id"],original)
                    original.add(row["source_id"])
        self.assertEqual(len(original),128)
        with self.assertRaises(ValueError):
            source.generate(95413,0)

    def test_pinned_archived_native_preserved_and_living_heads_cold_continue(self):
        archived_raw,live_raw=inputs()
        reader=ArchivedEvidenceReadout(archived_raw,live_raw)
        source=src().generate(97241,0)
        old_n=reader.current.original.base.native.info()["count"]
        old_native=reader.current.original.base.native.checkpoint()
        archive=reader.archived.checkpoint()
        old_future=canonical({
            "sensory":reader.current.sensory.checkpoint(),
            "reward":reader.current.reward.checkpoint()})
        self.assertEqual(reader.posterior,PRIOR_ARCHIVED)
        for record in source[:2]:
            p=reader.forecast(record["views"],record["row"])
            self.assertEqual(set(p),{
                "archive","live","gate","fixed_half","mispaired_gate","chance"})
            self.assertTrue(all(0<=v<=1 for probs in p.values() for v in probs))
            self.assertEqual(reader.observe(record["source_id"],
                            record["views"],record["row"]),p)
        self.assertEqual(reader.current.original.base.native.info()["count"],old_n+2)
        self.assertNotEqual(reader.current.original.base.native.checkpoint(),old_native)
        self.assertEqual(reader.archived.checkpoint(),archive)
        self.assertEqual(canonical({
            "sensory":reader.current.sensory.checkpoint(),
            "reward":reader.current.reward.checkpoint()}),old_future)
        state=reader.checkpoint()
        restored=ArchivedEvidenceReadout.restore(
            state,digest(state),archived_raw,live_raw)
        self.assertEqual(restored.checkpoint(),state)
        self.assertEqual(restored.archived.checkpoint(),archive)

    def test_duplicate_replay_conflict_and_invalid_source_are_atomic(self):
        a,b=inputs()
        reader=ArchivedEvidenceReadout(a,b)
        event=src().generate(97241,0)[0]
        reader.observe(event["source_id"],event["views"],event["row"])
        before=reader.checkpoint()
        self.assertIsNone(
            reader.observe(event["source_id"],event["views"],event["row"]))
        self.assertEqual(reader.checkpoint(),before)
        bad=dict(event["row"]);bad["y"]^=1
        with self.assertRaises(ValueError):
            reader.observe(event["source_id"],event["views"],bad)
        self.assertEqual(reader.checkpoint(),before)
        badview=((0,2),(0,1))
        with self.assertRaises(ValueError):
            reader.observe(event["source_id"],badview,event["row"])
        self.assertEqual(reader.checkpoint(),before)

    def test_historical_probe_is_public_recall_not_retraining(self):
        a,b=inputs()
        reader=ArchivedEvidenceReadout(a,b)
        old=reader.archived.base.native._ledger[-1]
        identifier,views,first,state,second,reward=old
        row={"s1":views[0][0],"x1":first,"s2":state,"x2":second,"y":reward}
        prior_native=reader.current.checkpoint()
        expected=reader.forecast(views,row)
        self.assertEqual(
            reader.observe(identifier,views,row,historical=True),expected)
        self.assertEqual(reader.current.checkpoint(),prior_native)
        self.assertEqual(len(reader.old_probe_events),1)
        with self.assertRaises(ValueError):
            reader.observe(identifier,views,row,historical=True)
        wrong=dict(row);wrong["s2"]^=1
        with self.assertRaises(ValueError):
            reader.observe(identifier,views,wrong,historical=True)
        state=reader.checkpoint()
        restored=ArchivedEvidenceReadout.restore(
            state,digest(state),a,b)
        self.assertEqual(restored.checkpoint(),state)

    def test_forged_posterior_rehashed_cold_replay_rejected(self):
        a,b=inputs()
        reader=ArchivedEvidenceReadout(a,b)
        e=src().generate(97241,0)[0]
        reader.observe(e["source_id"],e["views"],e["row"])
        state=reader.checkpoint()
        object_=json.loads(state)
        object_["posterior"]=0.999
        corrupt=canonical(object_)
        with self.assertRaises(ValueError):
            ArchivedEvidenceReadout.restore(corrupt,digest(corrupt),a,b)
        self.assertEqual(
            ArchivedEvidenceReadout.restore(state,digest(state),a,b).checkpoint(),
            state)

    def test_negative_gating_never_reads_hidden_regime(self):
        a,b=inputs()
        reader=ArchivedEvidenceReadout(a,b)
        e=src().generate(97241,1)[0]
        previous=reader.forecast(e["views"],e["row"])
        with_extra=dict(e["row"])
        self.assertEqual(previous,reader.forecast(e["views"],with_extra))
        reader.observe(e["source_id"],e["views"],e["row"])
        self.assertTrue(POSTERIOR_FLOOR<=reader.posterior<=POSTERIOR_CEIL)
        self.assertTrue(
            POSTERIOR_FLOOR<=reader.negative_posterior<=POSTERIOR_CEIL)


    def test_legacy_specialist_caps_follow_actual_native_1024_episode_contract(self):
        from yggdrasil.native_episode_experience import MAX_EPISODES as CAP_NATIVE
        from yggdrasil.native_jepa2_multilearner import (
            ActionLatentSpecialist, MAX_EPISODES as CAP_OLD, STEPS as OLD_STEPS)
        from yggdrasil.native_jepa_temporal import (
            TemporalLatentSpecialist, MAX_EPISODES as CAP_TEMP, STEPS as TEMP_STEPS)
        self.assertEqual(CAP_NATIVE,1024)
        self.assertEqual((CAP_OLD,CAP_TEMP),(CAP_NATIVE,CAP_NATIVE))
        for expert,steps in ((ActionLatentSpecialist("transition"),OLD_STEPS),
                             (TemporalLatentSpecialist("transition"),TEMP_STEPS)):
            expert.steps=1024*steps
            expert._validate()
            expert.steps+=1
            with self.assertRaises(ValueError):
                expert._validate()


if __name__=="__main__":
    unittest.main()


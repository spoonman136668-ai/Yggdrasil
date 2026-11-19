"""Focused source and original model fencing for JEPA2-05."""
import importlib.util
import pathlib
import unittest
import numpy as np
from yggdrasil.native_jepa_future import (
    HORIZON, observed_features, primary_truth, targets,
)
HERE=pathlib.Path(__file__).resolve().parent

def load(path, alias):
    spec=importlib.util.spec_from_file_location(alias,HERE/path)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

s=load("source.py","ygg_jepa205_test_source")
c=load("campaign.py","ygg_jepa205_test_campaign")

class JEPA205Tests(unittest.TestCase):
    def test_new_authentic_two_family_public_sources(self):
        for seed in s.SEEDS:
            events=s.generate(seed)
            self.assertEqual(len(events),16)
            self.assertEqual(len({e["source_id"] for e in events}),16)
            self.assertEqual(
                [sum(1 for e in events if e["phase"]==p)
                 for p in ("A","B","A_return")],[6,5,5])
            for i,e in enumerate(events):
                self.assertEqual(e["actions"],s.announced_plan(seed,i))
                self.assertEqual(e["post"][1],e["row"]["s2"])
                if i+1<len(events):
                    self.assertEqual(e["post"],(
                        events[i+1]["views"][0][0],
                        events[i+1]["views"][0][1],
                        events[i+1]["views"][1][1]))

    def test_fresh_source_is_deterministic(self):
        for seed in s.SEEDS:
            self.assertEqual(s.generate(seed),s.generate(seed))

    def test_no_unregistered_scientific_source(self):
        with self.assertRaisesRegex(ValueError,"FRESH_SEED"):
            s.generate(95413)
        with self.assertRaisesRegex(ValueError,"UNREGISTERED_PLAN"):
            s.announced_plan(99231,16)

    def test_future_only_visible_after_three_actual_events(self):
        events=s.generate(99231)
        with self.assertRaises(ValueError):
            targets(events[:2])
        sensory,reward=targets(events[:HORIZON])
        self.assertEqual((sensory.shape,reward.shape),((9,),(3,)))
        self.assertEqual(primary_truth(events[:HORIZON]).shape,(6,))

    def test_hidden_evaluation_labels_not_in_public_features(self):
        events=s.generate(99231)
        plans=tuple(s.announced_plan(99231,i) for i in range(3))
        first=events[0]
        x=observed_features(first["views"],plans,())
        redacted=dict(first,phase="UNKNOWN",family="UNKNOWN",seed="UNKNOWN")
        self.assertTrue(np.array_equal(x,observed_features(
            redacted["views"],plans,())))
        with self.assertRaises(ValueError):
            observed_features(first["views"],plans[:2],())

    def test_public_rehearsal_index_does_not_read_old_outcome(self):
        a=np.zeros(65,dtype=float)
        b=np.ones(65,dtype=float)
        sample=[(b, ({"post":(1,0,1),"row":{"y":1}},)),
                (a, ({"post":(0,1,0),"row":{"y":0}},))]
        idx,dist=c.matched_old(a,sample)
        self.assertEqual(idx,1)
        self.assertAlmostEqual(dist,0)
        sample[1]=(a,({"post":(1,1,1),"row":{"y":1}},))
        self.assertEqual(c.matched_old(a,sample),(1,0.0))

    def test_exact_prior_original_seven_component_models_cold_restore(self):
        for seed,expected in ((14071,1006),(14072,981)):
            model,raw=c.load_original(seed)
            self.assertEqual(len(model.original.base.native._ledger),expected)
            self.assertEqual(model.checkpoint(),raw)
            self.assertGreater(model.sensory.windows,0)
            self.assertGreater(model.reward.windows,0)

if __name__=="__main__":
    unittest.main()

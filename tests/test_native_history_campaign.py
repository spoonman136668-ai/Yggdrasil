"""Source-free mechanical qualification of the frozen consecutive campaign."""
import importlib.util
from fractions import Fraction
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("nkr20_mechanics",
    ROOT/"research/contrib/chatgpt/NKR-20/campaign.py")
c=importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

def fixture():
    rows=[]
    state=0
    for i in range(31):
        action=(state+i)%2
        reward=(i//4)%2
        after=state^(i&1)
        rows.append(dict(before=state,action=action,reward=reward,after=after,
                         terminated=False,truncated=i==30))
        state=after
    return {s:[dict(r) for r in rows] for s in c.source19.SEEDS}

class NativeHistoryCampaignTests(unittest.TestCase):
    def test_history_uses_previous_public_reward_and_validates_types(self):
        self.assertEqual(c.cue("history",1,0,0,1),1)
        self.assertEqual(c.cue("history",1,1,0,1),3)
        self.assertEqual(c.cue("state",1,1,0,1),1)
        with self.assertRaises(ValueError):
            c.cue("history",1,True,0,1)

    def test_native_and_batch_all_modes_every_query(self):
        data=fixture()
        for mode in c.MODES:
            native,retained=c.fit_native(data,mode)
            batch=c.batch_fit(data,mode)
            self.assertEqual(retained,96)
            for world in range(4):
                for before in (0,1):
                    for previous in (0,1):
                        for action in (0,1):
                            for index in (24,25):
                                self.assertEqual(native.predict(world,before,action,previous,index),
                                    c.batch_predict(batch,mode,world,before,action,previous,index))

    def test_pooled_parent_uses_no_additional_bank(self):
        data=fixture()
        baseline,_=c.fit_native(data,"state")
        for mode in ("history","sham"):
            model,_=c.fit_native(data,mode)
            self.assertEqual(len(model.snapshot()),328)
            self.assertEqual(len(model.banks),2)
            for world in range(4):
                for before in (0,1):
                    for action in (0,1):
                        self.assertEqual(model.parent_predict(world,before,action),
                                         baseline.predict(world,before,action,0,24))

    def test_two_bank_cold_integrity_and_tamper_rejection(self):
        model,_=c.fit_native(fixture(),"history")
        raw=model.snapshot()
        cold=c.NativeHistory.restore("history",raw)
        self.assertEqual(cold.snapshot(),raw)
        for bad in (raw[:-1],b"x"*328,bytearray(raw)):
            with self.assertRaises(ValueError):
                c.NativeHistory.restore("history",bad)

    def test_native_counters_count_each_training_event_once(self):
        model,_=c.fit_native(fixture(),"history")
        import struct
        total=sum(sum(struct.unpack(">"+"H"*64,b.snapshot()[4:-32])) for b in model.banks)
        self.assertEqual(total,4*23*2)

    def test_sham_is_source_outcome_independent(self):
        self.assertEqual(c.cue("sham",0,0,2,27),c.cue("sham",0,1,2,27))
        self.assertEqual(c.cue("state",0,0,2,27),c.cue("state",0,1,2,27))

    def test_zero_support_bounds_are_not_model_imputed(self):
        data=fixture()
        bounds=c.policy_bounds(data,range(31))
        self.assertEqual(bounds["behavior"]["unknown_rewards"],0)
        self.assertEqual(bounds["behavior"]["lower_bound"],bounds["behavior"]["upper_bound"])
        self.assertGreater(bounds["always0"]["unknown_rewards"],0)
        self.assertGreater(bounds["always1"]["unknown_rewards"],0)
        self.assertEqual(bounds["always0"]["matched_actions"]+bounds["always0"]["unknown_rewards"],124)

    def test_corrupted_original_behavior_detected(self):
        data=fixture()
        data[c.source19.SEEDS[0]][5]["action"]^=1
        with self.assertRaisesRegex(ValueError,"ORIGINAL_BEHAVIOR_POLICY_DRIFT"):
            c.policy_bounds(data,range(31))

    def test_hierarchical_arithmetic_fixed_strength_and_no_model_updates(self):
        model,_=c.fit_native(fixture(),"history")
        raw=model.snapshot()
        for world in range(4):
            child=model.counts(world,1,0,1,24)
            parent=model.parent_predict(world,1,0)
            p=[(s+4*parent[t])/(f+s+4) for t,(f,s) in enumerate(child)]
            self.assertTrue(all(Fraction(0)<=q<=Fraction(1) for q in p))
        self.assertEqual(model.snapshot(),raw)

    def test_bad_source_fixture_fails_before_model(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.json";p.write_text("{}")
            with self.assertRaises((KeyError,ValueError)):
                c.read_fixture(p)

if __name__=="__main__":
    unittest.main()

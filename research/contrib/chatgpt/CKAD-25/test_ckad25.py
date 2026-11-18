"""Frozen CKAD25 causal-surprise negative controls and independent parity."""
from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
campaign=load("ckad25_campaign_tests",HERE/"campaign.py")
audit=load("ckad25_audit_tests",HERE/"audit.py")
F=Fraction

class CKAD25AlarmTests(unittest.TestCase):
    def test_null_event_trace_has_no_alarm(self):
        p=F(1,2)
        for kind in campaign.ARMS:
            m=campaign.SurpriseAlarm(kind)
            trace=[]
            for i in range(192):
                id=f"{i:064x}"
                m.observe(id,449+i,p,p)
                trace.append({"event_id":id,"evidence_count":449+i,
                              "p_transition_observed":[1,2],
                              "p_reward_observed":[1,2]})
            self.assertEqual(m.alarms,[],kind)
            self.assertEqual(audit.alarms(trace,kind),[],kind)

    def test_transition_and_terminal_separate_surprise(self):
        for label,p,q,target in (
            ("transition",F(1,32),F(1,2),"transition"),
            ("reward",F(1,2),F(1,32),"reward")
        ):
            with self.subTest(label=label):
                trace=[]
                detectors={name:campaign.SurpriseAlarm(name) for name in campaign.ARMS}
                for i in range(10):
                    identity=f"{i:064x}"
                    for observer in detectors.values():
                        observer.observe(identity,449+i,p,q)
                    trace.append({"event_id":identity,"evidence_count":449+i,
                                  "p_transition_observed":[p.numerator,p.denominator],
                                  "p_reward_observed":[q.numerator,q.denominator]})
                self.assertTrue(detectors[target].alarms)
                self.assertTrue(detectors["factorized_or"].alarms)
                self.assertIn(target,detectors["factorized_or"].alarms[0]["causes"])
                for arm in campaign.ARMS:
                    self.assertEqual(detectors[arm].alarms,audit.alarms(trace,arm))

    def test_duplicate_detection_is_false_alarm(self):
        observations=[{"event_id":"a"*64,"evidence_count":448+49,"score":[16,1]},
                      {"event_id":"b"*64,"evidence_count":448+50,"score":[17,1]},
                      {"event_id":"c"*64,"evidence_count":448+97,"score":[18,1]},
                      {"event_id":"d"*64,"evidence_count":448+145,"score":[19,1]}]
        response=audit.classify(observations,[48,96,144])
        self.assertTrue(all(response["recognized"].values()))
        self.assertEqual(response["false_alarms"],1)
        self.assertEqual(response["detection_delays"],{"48":1,"96":1,"144":1})

    def test_stationary_null_and_missing_evidence_fail_closed(self):
        records=[{"event_id":"a"*64,"evidence_count":448+16,"score":[16,1]}]
        self.assertEqual(audit.classify(records,[])["false_alarms"],1)
        with self.assertRaisesRegex(ValueError,"NINE_CASES"):audit.aggregate([])
        with self.assertRaisesRegex(ValueError,"ALARM_SOURCE"):
            audit.classify([records[0],records[0]],[48])
        p=audit.protocols()
        self.assertEqual(p["checkpoint_parent_group_seeds"],[101,202,303])
        self.assertEqual(p["scientific_pass"],False)
        self.assertEqual(p["true_change_counts"]["stationary_null"],[])

    def test_semantic_sha_excludes_only_timing(self):
        a={"value":17,"wall_seconds":3,"scientific_pass":False}
        self.assertEqual(audit.semantic(a),audit.semantic({**a,"wall_seconds":7}))
        self.assertNotEqual(audit.semantic(a),audit.semantic({**a,"value":18}))

if __name__=="__main__":
    unittest.main()

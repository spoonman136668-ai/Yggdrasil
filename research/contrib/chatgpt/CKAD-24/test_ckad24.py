"""CKAD24 frozen shift timing, duplicate alarms and data-custody negatives."""
import importlib.util
from pathlib import Path
from fractions import Fraction
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad24_audit_test",HERE/"audit.py")
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
spec2=importlib.util.spec_from_file_location("ckad24_campaign_test",HERE/"campaign.py")
c=importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(c)


def det(number,label):
    return {"event_id":label*64,"evidence_count":448+number,"score":[17,1]}


class FrozenChangeTests(unittest.TestCase):
    def test_source_pins_and_new_phase_order_are_frozen(self):
        p,q=a.source_protocol()
        c.pin_source(p)
        self.assertEqual(p["seeds"],list(a.SEEDS))
        self.assertEqual(tuple(p["schedules"]),a.SCHEDULES)
        self.assertNotEqual(p["schedules"]["middle_swap"]["phase_worlds"],
                            p["schedules"]["double_flip"]["phase_worlds"])
        self.assertEqual(a.SHIFTS,(48,96,144))
        for name in a.SCHEDULES:
            self.assertEqual(p["schedules"][name]["phase_worlds"][-1],
                             {"family":"invariant","regime":0})
            self.assertNotEqual(p["schedules"][name]["source_seed_offset"],
                                q["source_seed_offset"])

    def test_three_timely_detections_and_one_spurious_alarm(self):
        out=a.classify([det(49,"a"),det(97,"b"),det(145,"c")])
        self.assertTrue(all(out["recognized"].values()))
        self.assertEqual(out["false_alarms"],0)
        self.assertEqual(out["delays"],{"48":1,"96":1,"144":1})
        out=a.classify([det(49,"a"),det(50,"b"),det(145,"c")])
        self.assertEqual(out["false_alarms"],1)
        self.assertEqual(out["recognized"]["96"],False)
        self.assertEqual(out["recognized"]["48"],True)
        self.assertEqual(out["recognized"]["144"],True)

    def test_first_alarm_before_boundary_or_after_sixteen_not_counted(self):
        out=a.classify([det(48,"a"),det(65,"b"),det(96,"c"),det(113,"d"),
                        det(144,"e"),det(161,"f")])
        self.assertEqual(out["false_alarms"],6)
        self.assertFalse(any(out["recognized"].values()))

    def test_replay_conflict_and_invalid_detection_rejected(self):
        with self.assertRaisesRegex(ValueError,"ALARM_ABSOLUTE_COUNT"):
            a.classify([det(50,"a"),det(50,"b")])
        with self.assertRaisesRegex(ValueError,"ALARM_PUBLIC_EVIDENCE"):
            a.classify([{"event_id":"x"*64,"evidence_count":498,"score":[15,1]}])
        with self.assertRaisesRegex(ValueError,"EXACT_CASE_COUNT"):
            a.aggregate([])
        self.assertEqual(c.stable_sha256({"n":3,"wall_seconds":1}),
                         c.stable_sha256({"n":3,"wall_seconds":20}))
        self.assertNotEqual(c.stable_sha256({"n":3}),c.stable_sha256({"n":4}))


if __name__=="__main__":unittest.main()

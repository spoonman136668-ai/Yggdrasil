"""NLD06: checks for delayed feedback, source integrity and bounded contexts."""
import unittest
from continuous_surprise import Detector, original_public_stream, run

class Zero:
    def choose(self, sensors, code): return 0

class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=run()

    def test_public_source_and_boundaries(self):
        events, receipts=original_public_stream()
        self.assertEqual(len(events),256)
        self.assertEqual(len({r["token"] for r in events}),256)
        self.assertEqual(events[128]["token"],"PUB-128")
        self.assertEqual([r["delayed_public_outcomes"] for r in receipts],[128,128])
        self.assertFalse(self.report["source_reset_visible_to_models"])
        self.assertFalse(self.report["protected_first_use"])

    def test_delayed_feedback_and_threshold(self):
        r=Detector()
        for tick in range(64):
            e={"token":f"PUB-{tick}","tick":tick,"feedback_tick":tick+2,
               "sensors":(False,False,False,False),"action":0,"success":False}
            r.observe(e["token"],e["sensors"],e["action"],tick,Zero())
            r.feedback(e)
        self.assertEqual(r.codes,[-1,1])
        self.assertEqual(r.feedback_count,64)
        self.assertEqual(r.transitions[0]["rolling_prediction_errors"],16)

    def test_no_creation_control(self):
        r=Detector(False)
        for t in range(64):
            e={"token":f"PUB-{t}","tick":t,"feedback_tick":t+2,
               "sensors":(False,False,False,False),"action":0,"success":False}
            r.observe(e["token"],e["sensors"],e["action"],t,Zero())
            r.feedback(e)
        self.assertEqual(r.codes,[-1])
        self.assertEqual(r.transitions,[])

    def test_checkpoint_exact(self):
        r=Detector()
        self.assertEqual(Detector.restore(r.save()).save(),r.save())
        with self.assertRaises(ValueError):
            Detector.restore(b"")

    def test_equal_information_and_readonly_score(self):
        v=self.report
        self.assertEqual(v["all_models_delayed_updates"],256)
        self.assertEqual(set(v["scoring"]),{"source_role_0","source_role_1"})
        for x in v["scoring"].values():
            self.assertEqual(x["diagnostic_probes"],8)
            self.assertEqual(x["scored"],56)
            self.assertEqual(len(x["inferred_slots"]),6)
            self.assertEqual(len(x["correct_of_56"]),7)

    def test_no_claim_of_first_use_or_unseen_transfer(self):
        v=self.report
        self.assertEqual(v["source_seed"],3)
        self.assertFalse(v["original_R9_science_seeds_reused"])
        self.assertEqual(v["ckb_admission"],"NOT_OBSERVED")
        self.assertEqual(v["causal_composition"],"NOT_TESTED")
        self.assertFalse(v["model_resource_cpu_rss_parity"])
        with self.assertRaises(ValueError):
            run(101)

if __name__=="__main__":
    unittest.main()

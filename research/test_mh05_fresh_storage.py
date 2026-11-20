"""MH05 pre-primary controls: no reward events or fresh-world training allowed."""
import unittest
from unittest import mock

from research import mh05_fresh_storage as m


class MH05FreshStoragePreprimaryTests(unittest.TestCase):
    def test_only_exact_frozen_public_source_allowed(self):
        m.source_guard()
        self.assertEqual(m.SEEDS, (503,509,521,523,541))
        self.assertEqual(m.MAPS, {"H":(0,2,1,0), "I":(2,0,0,0)})
        self.assertEqual(m.TRIAL,"MH05-SYNTH-HI-503-509-521-523-541-20261120")
        self.assertEqual(m.PHASES, (("a240","A",True),("x240","X",False)))

    def test_source_schedule_only_structure_no_reward_generation(self):
        for seed in m.SEEDS:
            for phase in ("A","X"):
                rows=m.schedule(seed,phase)
                self.assertEqual(len(rows),240)
                self.assertEqual(len(set(rows)),240)
                self.assertEqual(rows,m.schedule(seed,phase))
                for block in range(20):
                    sample=rows[block*12:block*12+12]
                    self.assertEqual({(c,a) for c,a,r in sample},
                        {(c,a) for c in range(4) for a in range(3)})
        for seed,phase in ((401,"A"),(503,"return"),(True,"X"),(541,"x")):
            with self.assertRaises(ValueError):
                m.schedule(seed,phase)

    def test_critical_phase_boolean_has_no_doubled_original_marker(self):
        self.assertEqual([x[0] for x in m.PHASES],["a240","x240"])
        self.assertEqual([x[1] for x in m.PHASES],["A","X"])
        self.assertEqual([x[2] for x in m.PHASES],[True,False])
        self.assertEqual(len(set(x[0] for x in m.PHASES)),2)

    def test_zero_event_dry_path_executes_both_phase_branches_and_cold_restore(self):
        # Proves no UnboundLocalError, duplicate A stage or missing X cold proof.
        # All schedules replaced with ZERO rows, hence no MH05 outcomes consumed.
        with mock.patch.object(m,"schedule",return_value=()):
            d=m.one_study(m.SEEDS[0],"H",m.MAPS["H"])
        self.assertEqual(set(d["stages"]),{"a240","x240"})
        self.assertTrue(d["frozen_x240_same_checkpoint"])
        self.assertEqual(len(bytes.fromhex(d["full_original_checkpoint_hex"]["a240"])),2264)
        self.assertEqual(len(bytes.fromhex(d["full_original_checkpoint_hex"]["x240"])),2264)
        self.assertEqual(d["resources"]["native_event_cpu_ns"],0)
        self.assertGreater(d["cold_x240"]["rss_bytes"],0)

    def test_conventional_score_not_oracle_bank(self):
        ctrl=m.old.FullHistory()
        ctrl.learn(0,0,-1.0)
        ctrl.learn(0,2,1.0)
        score=m.old.arm_readout(ctrl,m.MAPS["H"])
        self.assertEqual(score["x"],.25)
        self.assertGreater(score["bytes"],0)


if __name__=="__main__":
    unittest.main()

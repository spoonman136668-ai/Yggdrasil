"""KNOW32 source-only negative controls; NEVER produce frozen HELD outcomes."""
import unittest
from know32_balanced_access_dev import (
    protocol, public_tape, phase_coverage, b_law, b_family,
    private_witness, run_shared_prefix, require, PREFIX
)
from know30_blind_archive_reactivation_dev import Joint
from unknown_action_affordance_dev import ALL_MAPS


class Know32Controls(unittest.TestCase):
    def test_frozen_prereg_blob_and_scope(self):
        p=protocol()
        self.assertEqual(p["experiment_id"],"KNOW32")
        self.assertEqual(p["scope"]["merge"],False)
        self.assertEqual(p["scope"]["deployment"],"NONE")
        self.assertFalse(p["scope"]["original_first_use_issue_426"])

    def test_all_16_public_pairs_each_phase(self):
        for start in (0,16,32):
            pairs=[public_tape(t) for t in range(start,start+16)]
            self.assertEqual(len(set(pairs)),16)
            self.assertEqual(set(pairs),{(c,a) for c in range(4) for a in range(4)})

    def test_all_eight_physical_inputs_every_phase_all_maps(self):
        self.assertEqual(len(phase_coverage()),6)
        for mapping in ALL_MAPS:
            for start in (0,16,32):
                seen={public_tape(t)[0]^mapping[public_tape(t)[1]]
                      for t in range(start,start+16)}
                self.assertEqual(seen,set(range(8)))

    def test_original_fixed_schedule_missed_physical_4(self):
        for mapping in ALL_MAPS:
            old={c^mapping[c] for c in range(4)}
            self.assertNotIn(4,old)

    def test_new_family_split_and_unseen_law(self):
        self.assertEqual(b_law(17301),"H2")
        self.assertEqual(b_law(17351),"H1")
        self.assertEqual(b_family(17351),"unfamiliar_H1")
        with self.assertRaises(ValueError): b_law(16037)

    def test_no_held_source_read_in_focused_tests(self):
        with self.assertRaises(ValueError): private_witness(0,16037,0,0,"control_A")
        with self.assertRaises(ValueError): private_witness(0,17301,0,1,"control_A")
        with self.assertRaises(ValueError):
            private_witness(0,17301,0,0,"control_A",source_mode="original_world")

    def test_public_tape_typing_and_bounds(self):
        self.assertEqual(public_tape(15),(3,3))
        self.assertEqual(public_tape(16),(0,0))
        self.assertEqual(public_tape(32),(0,0))
        for bad in (-1,48,True,0.0):
            with self.assertRaises(ValueError): public_tape(bad)

    def test_mock_prefix_single_source_call_per_step_and_cold(self):
        prior=[1/6.]*6
        base=Joint(prior)
        fit=(prior,base,base,base,[])
        calls=[]
        def fake(mid,seed,t,a,branch):
            calls.append((mid,seed,t,a,branch))
            return int(t%2==0)
        models,n=run_shared_prefix(fit,0,17301,fake)
        self.assertEqual((n,len(calls)),(PREFIX,PREFIX))
        self.assertEqual([x[2] for x in calls],list(range(PREFIX)))
        self.assertTrue(all(x[-1]=="control_A" for x in calls))
        from know31_paired_interference_dev import cold_copy
        for m in models.values():
            old=[m.prob(c,0) for c in range(8)]
            self.assertEqual(old,[cold_copy(m).prob(c,0) for c in range(8)])
        self.assertEqual(models["archive"].received,PREFIX)

    def test_mock_bad_outcome_rejected(self):
        prior=[1/6.]*6
        base=Joint(prior)
        fit=(prior,base,base,base,[])
        def fake(*args): return 2
        with self.assertRaises(ValueError):
            run_shared_prefix(fit,0,17301,fake)


if __name__=="__main__":
    unittest.main()

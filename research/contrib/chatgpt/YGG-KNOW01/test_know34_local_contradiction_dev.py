"""KNOW34 mock-only tests: NEVER call frozen synthetic private_witness or proof."""
import json
import unittest
from know34_local_contradiction_dev import (
    ARMS, SEEDS, GuardedCells, canonical, cold, digest, family, paired_world,
    private_law_bit, private_witness, protocol, public_tape, public_prefix,
)


class Know34LocalContradiction(unittest.TestCase):
    def test_frozen_protocol_and_owner_isolation(self):
        p=protocol()
        self.assertEqual(p["experiment_id"],"KNOW34")
        self.assertEqual(p["budgets"]["paired_worlds"],24)
        self.assertEqual(p["source"]["seeds"],list(SEEDS))
        self.assertFalse(p["authority"]["protected_original_world_first_use"])
        self.assertFalse(p["authority"]["native_model_changed"])
        self.assertEqual(p["authority"]["deployment"],"NONE")

    def test_public_action_grid_is_fixed_source_blind(self):
        for start in range(0,192,16):
            a=[public_tape(t) for t in range(start,start+16)]
            self.assertEqual(len({(c,action) for c,action,_x in a}),16)
            self.assertEqual([sum(x==i for _,_,x in a) for i in range(8)],
                             [2]*8)

    def test_distinct_frozen_B_laws_without_model_input(self):
        bit={law:tuple(private_law_bit(law,x) for x in range(8))
             for law in ("A","B1","B2")}
        self.assertEqual(sum(a!=b for a,b in zip(bit["A"],bit["B1"])),4)
        self.assertEqual(sum(a!=b for a,b in zip(bit["A"],bit["B2"])),6)
        self.assertEqual((family(SEEDS[0]),family(SEEDS[-1])),("B1","B2"))
        self.assertEqual(len(set(SEEDS)),24)

    def test_source_denies_consumed_and_original(self):
        for s,t,b,mode in (
            (18101,0,"control_A","fresh_synthetic_local_cell_regimes_not_original"),
            (SEEDS[0],-1,"control_A","fresh_synthetic_local_cell_regimes_not_original"),
            (SEEDS[0],0,"protected","fresh_synthetic_local_cell_regimes_not_original"),
            (SEEDS[0],0,"control_A","original_world")
        ):
            with self.assertRaises(ValueError):
                private_witness(s,t,b,source_mode=mode)

    def test_tape_order_and_public_events_are_fail_closed(self):
        model=GuardedCells("local")
        with self.assertRaises(ValueError):
            model.observe(1,0,1)
        with self.assertRaises(ValueError):
            model.observe(0,0,True)
        with self.assertRaises(ValueError):
            model.observe(0,-1,1)
        with self.assertRaises(ValueError):
            model.observe(0,0,1,source_mode="private")
        model.observe(0,0,1)
        with self.assertRaises(ValueError):
            model.observe(0,0,1)
        self.assertEqual(model.received,1)

    def test_mock_contradiction_then_recovery_preserves_slow_A(self):
        for kind in ("local","rewired"):
            m=GuardedCells(kind)
            # Both members of one declared pair have 6 true observations.
            x0,x1=m.partners(0)
            for t in range(12):
                m.observe(t,x0 if t%2==0 else x1,1)
            slow_before=m.slow_sha()
            self.assertEqual(m.mode[0],"slow")
            for t in range(12,24):
                m.observe(t,x0 if t%2==0 else x1,0)
            self.assertEqual(m.mode[0],"fast")
            self.assertEqual(m.slow_sha(),slow_before)
            for t in range(24,36):
                m.observe(t,x0 if t%2==0 else x1,1)
            self.assertEqual(m.mode[0],"slow")
            self.assertEqual(m.slow_sha(),slow_before)
            self.assertGreaterEqual(m.fast_switches,1)
            self.assertGreaterEqual(m.slow_returns,1)
            self.assertEqual([m.prob(x) for x in range(8)],
                             [cold(m).prob(x) for x in range(8)])

    def test_stable_A_does_not_force_switch_in_mock(self):
        m=GuardedCells("local")
        for t in range(48):
            m.observe(t,t%8,1)
        self.assertEqual(m.mode,["slow"]*4)
        self.assertEqual(m.fast_switches,0)
        self.assertTrue(all(z==6 for z in m.n))

    def test_same_capacity_local_and_rewired_pair_assignment(self):
        local,rewired=GuardedCells("local"),GuardedCells("rewired")
        self.assertEqual([local.partners(i) for i in range(4)],
                         [(0,1),(2,3),(4,5),(6,7)])
        self.assertEqual([rewired.partners(i) for i in range(4)],
                         [(0,4),(1,5),(2,6),(3,7)])
        self.assertEqual(len(local.mode),len(rewired.mode))
        self.assertEqual(len(local.slow),len(rewired.slow))
        self.assertEqual(len(local.windows),len(rewired.windows))

    def test_checkpoint_rejects_tamper_duplicates_and_invalid_topology(self):
        m=GuardedCells("local")
        raw=m.checkpoint()
        with self.assertRaises(ValueError):
            GuardedCells.restore(raw,"0"*64)
        dup=b'{"kind":"local","kind":"local"}'
        with self.assertRaises(ValueError):
            GuardedCells.restore(dup,digest(dup))
        a=json.loads(raw.decode("ascii"))
        a["mode"][0]="hidden_phase"
        b=canonical(a)
        with self.assertRaises(ValueError):
            GuardedCells.restore(b,digest(b))
        a=json.loads(raw.decode("ascii"))
        a["n"][0]=1
        b=canonical(a)
        with self.assertRaises(ValueError):
            GuardedCells.restore(b,digest(b))

    def test_mock_prefix_source_single_fetch_and_all_arm_parity(self):
        calls=[]
        def toy(seed,t,branch):
            calls.append((seed,t,branch))
            return int(t%3==0)
        models,n=public_prefix(SEEDS[0],toy)
        self.assertEqual((n,len(calls)),(64,64))
        self.assertEqual([x[1] for x in calls],list(range(64)))
        self.assertEqual(set(models),set(ARMS))
        self.assertTrue(all(m.received==64 for m in models.values()))

    def test_mock_paired_cohort_cold_and_budget_without_held(self):
        calls=[]
        def toy(seed,t,branch):
            calls.append((seed,t,branch))
            return int((t%7)<3)
        r=paired_world(SEEDS[0],toy)
        self.assertEqual((r["source_calls"],len(calls)),(320,320))
        self.assertEqual(sum(t<64 for _,t,_ in calls),64)
        self.assertEqual(sum(t>=64 and b=="control_A" for _,t,b in calls),128)
        self.assertEqual(sum(t>=64 and b=="treatment_B" for _,t,b in calls),128)
        self.assertEqual(set(r["branches"]),{"control_A","treatment_B"})
        for b in r["branches"].values():
            self.assertEqual(set(b["return_A"]["local"]),{"16","32","48","64"})
        self.assertTrue(r["treatment_slow_A_unchanged"])


if __name__=="__main__":
    unittest.main()

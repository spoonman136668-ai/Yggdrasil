"""KNOW33 mock-only tests: NO frozen synthetic HELD outcome access."""
import copy
import json
import unittest

from know33_local_metaplastic_dev import (
    ARMS, SEEDS, Beta, Cells, canonical, cold, digest, family,
    law_bit, private_witness, protocol, public_tape, public_prefix, world
)


class Know33MetaplasticControls(unittest.TestCase):
    def test_prereg_blob_before_source_and_no_original(self):
        p=protocol()
        self.assertEqual(p["experiment_id"],"KNOW33")
        self.assertEqual(len(p["source"]["seeds"]),24)
        self.assertFalse(p["role"]["new_original_world_first_use"])
        self.assertFalse(p["role"]["accepted_checkpoint_change"])
        self.assertEqual(p["role"]["deployment"],"NONE")

    def test_tape_balanced_physical_inputs_at_all_phases(self):
        for start in (0,16,32,64,80,128,144):
            rows=[public_tape(t) for t in range(start,start+16)]
            self.assertEqual(len({(c,a) for c,a,_ in rows}),16)
            self.assertEqual([sum(x==k for _,_,x in rows) for k in range(8)],
                             [2]*8)

    def test_public_tape_invalid_types_and_bounds(self):
        for x in (True, -1, 192, 0.0, "1"):
            with self.assertRaises(ValueError): public_tape(x)

    def test_new_causal_laws_differ_without_outcome_access(self):
        tables={law:tuple(law_bit(law,x) for x in range(8))
                for law in ("A","B1","B2")}
        self.assertNotEqual(tables["A"],tables["B1"])
        self.assertNotEqual(tables["A"],tables["B2"])
        self.assertNotEqual(tables["B1"],tables["B2"])
        self.assertEqual(family(SEEDS[0]),"B1")
        self.assertEqual(family(SEEDS[-1]),"B2")

    def test_private_source_rejects_unfrozen_replay_original_mode(self):
        with self.assertRaises(ValueError): private_witness(17301,0,"control_A")
        with self.assertRaises(ValueError):
            private_witness(SEEDS[0],0,"control_A",source_mode="original_world")
        with self.assertRaises(ValueError):
            private_witness(SEEDS[0],0,"unqualified")
        with self.assertRaises(ValueError):
            private_witness(SEEDS[0],True,"control_A")

    def test_beta_and_same_exact_public_ledger(self):
        b=Beta()
        self.assertEqual(b.prob(),.5)
        b.update(1)
        self.assertEqual(b.prob(),2/3)
        with self.assertRaises(ValueError): b.update(True)
        for name in ARMS:
            m=Cells(name)
            self.assertEqual(m.received,0)
            for t in range(12):
                m.observe(t,t%8,t%2)
            self.assertEqual(m.received,12)
            self.assertEqual(sum(m.n),12)
            self.assertEqual([m.prob(x) for x in range(8)],
                             [cold(m).prob(x) for x in range(8)])

    def test_local_support_is_neighbor_only_and_ablation_is_independent(self):
        self.assertEqual(Cells("candidate").group(0),
                         Cells("candidate").group(1))
        self.assertNotEqual(Cells("candidate").group(0),
                            Cells("candidate").group(2))
        self.assertNotEqual(Cells("no_neighbor").group(0),
                            Cells("no_neighbor").group(1))
        models={name:Cells(name) for name in ("candidate","no_neighbor")}
        for t in range(9):
            for m in models.values(): m.observe(t,0,0)
        self.assertNotEqual(models["candidate"].support_score[0],2.0)
        self.assertEqual(models["no_neighbor"].support_score[1],2.0)
        self.assertGreater(models["candidate"].local_messages,0)
        self.assertEqual(models["no_neighbor"].local_messages,0)

    def test_order_tamper_duplicate_and_wrong_source_fail_closed(self):
        m=Cells("candidate")
        with self.assertRaises(ValueError): m.observe(1,0,1)
        with self.assertRaises(ValueError): m.observe(0,0,True)
        with self.assertRaises(ValueError): m.observe(0,-1,0)
        with self.assertRaises(ValueError):
            m.observe(0,0,1,source_mode="protected_original")
        m.observe(0,0,1)
        with self.assertRaises(ValueError): m.observe(0,0,1)

    def test_cold_rejects_wrong_checksum_and_duplicate_fields(self):
        m=Cells("candidate")
        raw=m.checkpoint()
        with self.assertRaises(ValueError): Cells.restore(raw,"0"*64)
        tampered=raw[:-1]+b' '
        with self.assertRaises(ValueError): Cells.restore(tampered,digest(raw))
        # Duplicate JSON keys, even when hashed exactly, fail closed.
        duplicate=b'{"kind":"candidate","kind":"candidate"}'
        with self.assertRaises(ValueError):
            Cells.restore(duplicate,digest(duplicate))

    def test_mock_prefix_has_one_source_call_per_actual_action(self):
        calls=[]
        def fake(seed,t,branch):
            calls.append((seed,t,branch))
            return int(t%3!=0)
        arms,n=public_prefix(SEEDS[0],fake)
        self.assertEqual((n,len(calls)),(64,64))
        self.assertEqual([t for _,t,_ in calls],list(range(64)))
        self.assertTrue(all(b=="control_A" for _,_,b in calls))
        self.assertTrue(all(m.received==64 for m in arms.values()))

    def test_mock_paired_world_uses_no_held_source_or_phase_input(self):
        calls=[]
        def fake(seed,t,branch):
            calls.append((seed,t,branch))
            return int((t%11)<5)
        d=world(SEEDS[0],fake)
        self.assertEqual((d["one_shot_source_calls"],len(calls)),(320,320))
        self.assertEqual(sum(1 for s,t,b in calls if t<64),64)
        self.assertEqual(len([t for s,t,b in calls if b=="treatment_B" and t>=64]),128)
        self.assertEqual(len([t for s,t,b in calls if b=="control_A" and t>=64]),128)
        self.assertEqual(set(d["branches"]),{"control_A","treatment_B"})
        for v in d["branches"].values():
            self.assertEqual(set(v["return_A_after_k"]["candidate"]),
                             {"8","16","32","64"})
        self.assertEqual(d["family"],"B1")


if __name__=="__main__":
    unittest.main()

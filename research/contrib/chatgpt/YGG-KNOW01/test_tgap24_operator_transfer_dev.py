"""TGAP24 novel Boolean law, source isolation and frozen budget checks."""
import json
import unittest

from tgap24_operator_transfer_dev import (
    FIT, HELD, PREREG, ARMS, SOURCE, ContextBank, ContextBeta,
    hidden_best, public, witnessed, fit, eval_world, proof, digest
)


class TGAP24Tests(unittest.TestCase):
    def test_operator_families_new_and_frozen(self):
        self.assertEqual(FIT,(10101,"fit",96))
        self.assertEqual(len(HELD),12)
        self.assertEqual(len(set(s for s,_ in HELD)),12)
        self.assertNotIn(FIT[0],set(s for s,_ in HELD))
        assert all(10000 < s < 11000 for s,_ in HELD)
        self.assertEqual(set(op for _,op in HELD),{
            "held_xor","held_and","held_xnor","held_nor"})
        for t in range(96):
            c,a=public(t)
            self.assertEqual((c,a),(t%4,(t//4)%2))
        for op in ("fit","held_xor","held_and","held_xnor","held_nor"):
            self.assertEqual(len([hidden_best(op,c) for c in range(4)]),4)
        self.assertNotEqual(tuple(hidden_best("fit",c) for c in range(4)),
                            tuple(hidden_best("held_xor",c) for c in range(4)))

    def test_witnessed_one_action_no_oracle_source(self):
        for s,op in HELD:
            for t in range(64):
                c,a=public(t)
                y=witnessed(s,op,t,c,a)
                self.assertEqual(y,witnessed(s,op,t,c,a))
                self.assertIn(y,(0,1))
        self.assertEqual(len({public(t) for t in range(8)}),8)

    def test_bank_exact_private_context_cursor_and_replay(self):
        b=ContextBank("quarantine")
        for t in range(8):
            c,a=public(t)
            b.observe(t,c,a,t%2)
        self.assertEqual(b.cursor,[2,2,2,2])
        with self.assertRaisesRegex(ValueError,"REPLAY_OR_SOURCE"):
            b.observe(7,3,1,1)
        with self.assertRaisesRegex(ValueError,"REPLAY_OR_SOURCE"):
            b.observe(8,0,0,1,source_mode="real_world")
        raw=b.state_bytes()
        self.assertEqual(ContextBank.cold_restore(raw,digest(raw)).state_bytes(),
                         raw)
        with self.assertRaises(ValueError):
            ContextBank.cold_restore(raw,b"invalid")
        with self.assertRaises(ValueError):
            ContextBank.cold_restore(raw+b"x",digest(raw+b"x"))
        self.assertEqual(SOURCE,"engineering_fixture_only")

    def test_controls_independent_fully_fitted_sources(self):
        b=ContextBeta()
        r=ContextBeta(rolling=True)
        for t in range(96):
            c,a=public(t)
            y=witnessed(*FIT[:2],t,c,a)
            b.observe(c,a,y)
            r.observe(c,a,y)
        self.assertTrue(all(len(b.cells[c][a])==12
                            for c in range(4) for a in (0,1)))
        self.assertTrue(all(len(r.cells[c][a])==8
                            for c in range(4) for a in (0,1)))

    def test_training_fit_retains_four_public_contexts(self):
        d=fit()
        self.assertEqual(d["q"].cursor,[24,24,24,24])
        self.assertEqual(d["o"].cursor,[24,24,24,24])
        self.assertEqual(len(d["old_slot0"]),8)
        self.assertEqual(len(d["old_all_slots"]),16)
        for b in (d["q"],d["o"]):
            cold=ContextBank.cold_restore(b.state_bytes(),digest(b.state_bytes()))
            self.assertEqual(b.state_bytes(),cold.state_bytes())
        s=eval_world(d,HELD[0])
        self.assertEqual(s["evaluated"],40)
        self.assertEqual(set(s["loss_sums"]),set(ARMS))
        self.assertEqual(s["operator"],HELD[0][1])

    def test_frozen_science_receipt(self):
        v=proof()
        self.assertEqual(v["prereg_commit"],PREREG)
        self.assertEqual(v["fit_witnessed"],96)
        self.assertEqual(v["held_warmup"],288)
        self.assertEqual(v["held_scored"],480)
        self.assertEqual(v["held_worlds"],12)
        self.assertEqual(set(v["held_brier"]),set(ARMS))
        self.assertEqual(len(v["frozen_hypotheses"]),4)
        self.assertEqual(v["held_brier"]["source_only"],.25)
        self.assertEqual(v["engineering_gate"],"PASS")
        self.assertEqual(v["scientific_gate"],"SCIENCE_NO_GO_SYNTHETIC")
        self.assertFalse(v["native_modified"])
        self.assertFalse(v["original_first_use"])
        self.assertEqual(v["deploy"],"NONE")
        print("YGG_TGAP24_FROZEN_RECEIPT="+json.dumps({
            "held_brier":v["held_brier"],
            "operator_brier":v["held_operator_brier"],
            "old_A_drift":v["old_FIT_context_slot0_drift_by_operator"],
            "hypotheses":v["frozen_hypotheses"],
            "verdict":v["development_verdict"],
        },sort_keys=True))


if __name__=="__main__":
    unittest.main()

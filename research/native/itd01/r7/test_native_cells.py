"""R7: REAL native cellular feedback learning and cold checkpoint tests."""
import copy
import hashlib
import json
import unittest
from native_cells import (Colony,LocalCell,PublicDevGenerator,
                          _examples,_score,study,gates)


class R7NativeYgg(unittest.TestCase):
    def test_feedback_cannot_arrive_before_public_consequence(self):
        colony=Colony()
        senses=(True,False,True,False)
        initial=colony.checkpoint()
        with self.assertRaisesRegex(ValueError,"EARLY_PRIVATE"):
            colony.learn_completed_public_feedback("A",senses,True,1)
        self.assertEqual(initial,colony.checkpoint())
        colony.learn_completed_public_feedback("A",senses,True,2)
        self.assertEqual(colony.feedback_updates,1)
        self.assertEqual(colony.neighbor_messages,8)
        with self.assertRaises(ValueError):
            colony.predict("H1",senses)

    def test_each_cell_plasticity_local_with_bounded_communication(self):
        model=Colony()
        before=model.checkpoint()
        for n in range(64):
            bits=(bool(n%2),bool(n%3),bool(n%5),bool(n%7))
            model.learn_completed_public_feedback("A",bits,bool(n%5),2)
        self.assertNotEqual(before,model.checkpoint())
        self.assertTrue(all(x.updates==64 for x in model.cells["A"]))
        self.assertTrue(all(x.updates==0 for x in model.cells["B"]))
        self.assertTrue(all(-512<=x.fast<=512 for x in model.cells["A"]))

    def test_native_prediction_improves_on_public_feedback(self):
        g=PublicDevGenerator(1447)
        train=_examples(g,"A",320)
        model=Colony()
        prior=_score(model,train)
        for c,x,y in train:
            model.learn_completed_public_feedback(c,x,y,2)
        later=_score(model,train)
        self.assertGreaterEqual(later-prior,.15,(prior,later))

    def test_cold_state_restart_exact_and_tamper_fails(self):
        model=Colony()
        for i in range(150):
            model.learn_completed_public_feedback("B",
                (bool(i%2),bool(i%3),bool(i%5),bool(i%7)),bool(i%3),2)
        raw=model.checkpoint()
        cold=Colony.restore(raw)
        self.assertEqual(raw,cold.checkpoint())
        for j in range(16):
            sensor=(bool(j&1),bool(j&2),bool(j&4),bool(j&8))
            self.assertEqual(model.predict("B",sensor),cold.predict("B",sensor))
        data=json.loads(raw)
        data["payload"]["cells"]["B"][0]["fast"]+=12
        with self.assertRaisesRegex(ValueError,"STATE_HASH"):
            Colony.restore(json.dumps(data,sort_keys=True).encode())

    def test_frozen_three_init_cohorts_keep_original_negatives(self):
        xs=[study(s) for s in (17,31,47)]
        for s in xs:
            print("YGGDRASIL_R7_NATIVE_DEV_SCORE="+json.dumps(s,sort_keys=True))
        self.assertTrue(gates(xs),xs)

    def test_repeated_run_seed_and_checksum_deterministic(self):
        for seed in (17,31,47):
            self.assertEqual(study(seed),study(seed))

    def test_prohibited_source_first_use_not_present(self):
        import native_cells
        import inspect
        text=inspect.getsource(native_cells)
        for token in ("minigrid.reset","mcp__GitHub__",
                      "broker.Runner","Coinbase","original_held_evaluator"):
            self.assertNotIn(token,text)


if __name__=="__main__":
    unittest.main()

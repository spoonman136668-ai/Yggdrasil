"""C29 focused source-free tests of original R1 cells and fitted comparator."""
import json
import unittest
from research.mass_r7c29.effects import (
    NativeCellEffect,ConventionalBeta,view,data_event,sealed,unseal,
    exploratory_proxy,make_arms,train,event_split
)


def event(a=1,before_blocked=False,after_blocked=True,seed=46101,step=0):
    return {"family":"MiniGrid-FourRooms-v0","seed":seed,"step":step,
      "before":{"x":1,"y":1,"direction":0,"goal_x":6,"goal_y":6,"front_blocked":before_blocked},
      "chosen_action":a,"information_turn":bool(a!=2),
      "returned_after":{"x":1,"y":1,"direction":3 if a==0 else (1 if a==1 else 0),
          "goal_x":6,"goal_y":6,"front_blocked":after_blocked},
      "returned_reward":0.,"terminated":False,"truncated":False}


class AuthenticFitModelUnit(unittest.TestCase):
    def test_native_train_selected_action_only_real_original_local_cells(self):
        x=view(event()["before"]);m=NativeCellEffect()
        p0=m.predict(x,1);m.observe(x,1,1)
        self.assertNotEqual(m.predict(x,1),p0)
        self.assertEqual(m.predict(x,0),p0)
        self.assertEqual(m.cells["1"][0].updates,1)
        self.assertEqual(m.cells["0"][0].updates,0)

    def test_native_can_relearn_after_changed_selected_effect(self):
        x=view(event()["before"]);m=NativeCellEffect()
        for _ in range(10):m.observe(x,1,1)
        a=m.predict(x,1)
        for _ in range(20):m.observe(x,1,0)
        b=m.predict(x,1)
        self.assertLess(b,a)
        for _ in range(40):m.observe(x,1,1)
        c=m.predict(x,1)
        self.assertGreater(c,b)

    def test_bayesian_stays_independent_of_native_code(self):
        x=view(event()["before"]);m=ConventionalBeta();n=NativeCellEffect()
        self.assertEqual(m.predict(x,1),0.5)
        m.observe(x,1,1);n.observe(x,1,1)
        self.assertNotEqual(m.predict(x,1),0.5)
        self.assertNotEqual(m.predict(x,1),n.predict(x,1))

    def test_time_only_control_ignores_selected_action(self):
        x=view(event()["before"]);m=ConventionalBeta(False)
        m.observe(x,0,1)
        self.assertEqual(m.predict(x,2),m.predict(x,0))

    def test_frozen_and_shuffled_affect_only_valid_surfaces(self):
        arms=make_arms()
        e=[event(a=0),event(a=1,step=1),event(a=2,step=2)]
        train(arms,e)
        self.assertEqual(arms["native"].updates,3)
        self.assertEqual(arms["shuffled_action"].updates,3)
        self.assertEqual(arms["frozen"].updates,0)
        self.assertEqual(arms["frozen"].predict(view(e[0]["before"]),0),0.5)

    def test_native_and_bayesian_sealed_cold_exact_parity(self):
        e=event();s,a,y=data_event(e)
        for m in (NativeCellEffect(),ConventionalBeta(),ConventionalBeta(False)):
            m.observe(s,a,y)
            checkpoint=sealed(m)
            restored=unseal(checkpoint)
            self.assertEqual(sealed(restored),checkpoint)
            self.assertAlmostEqual(m.predict(s,a),restored.predict(s,a),places=14)
            self.assertEqual(exploratory_proxy(m,s,a),exploratory_proxy(restored,s,a))

    def test_tamper_rejected_without_workaround(self):
        m=NativeCellEffect()
        original=json.loads(sealed(m))
        original["payload"]["model"]["cells"]["1"][0]["fast"]=8.
        with self.assertRaises(ValueError):
            unseal(json.dumps(original).encode())

    def test_hidden_data_and_malformed_selected_action_rejected(self):
        e=event();e["before"]["privileged_grid"]=9
        with self.assertRaisesRegex(ValueError,"EXTRA_OR_MISSING"):
            data_event(e)
        e=event();e["chosen_action"]=True
        with self.assertRaisesRegex(ValueError,"INVALID_ORIGINAL_SELECTED_ACTION"):
            data_event(e)

    def test_hand_defined_proxy_not_mislabeled_as_outcome(self):
        x=view(event()["before"]);m=NativeCellEffect()
        self.assertIsInstance(exploratory_proxy(m,x,1),bool)
        with self.assertRaisesRegex(ValueError,"INVALID_PROXY_COST"):
            exploratory_proxy(m,x,1,0)

    def test_invalid_native_checkpoint_counters_rejected(self):
        m=NativeCellEffect();wire=json.loads(sealed(m))
        wire["payload"]["model"]["cells"]["2"][0]["updates"]=99999
        import hashlib
        from research.native.itd02.r1.native_policy import canonical
        wire["sha256"]=hashlib.sha256(canonical(wire["payload"])).hexdigest()
        with self.assertRaisesRegex(ValueError,"CORRUPT"):
            unseal(canonical(wire))


if __name__=="__main__":
    unittest.main()

"""C31 source-free bounded validation of original R3 action-proposal boundary."""
import unittest
from research.native.itd02.r1.native_policy import PublicGrid
from research.native.itd02.r3.navigator import Navigator
from research.mass_r7c31.action_bridge import (
    decision,source_sensor_update,source_public_navigator,
    learned_source_motors,qualified_disposition
)


D={0:(1,0),1:(0,1),2:(-1,0),3:(0,-1)}


def nav_model(width=8):
    n=Navigator();n.reset_episode(width,width)
    n.motor={str(d):{f"{v[0]},{v[1]}":1} for d,v in D.items()}
    return n


class Pred:
    def __init__(self,p):self.probs=p
    def predict(self,s,a):return self.probs[a]


def event(d,a,move):
    dx,dy=D[d] if move else (0,0)
    return {"family":"MiniGrid-FourRooms-v0","seed":46101,"step":0,
      "before":{"x":2,"y":2,"goal_x":6,"goal_y":6,
                "direction":d,"front_blocked":False},
      "chosen_action":a,"information_turn":False,
      "returned_after":{"x":2+dx,"y":2+dy,"goal_x":6,"goal_y":6,
                        "direction":d,"front_blocked":False},
      "returned_reward":0.0,"terminated":False,"truncated":False}


class SourceOwnedChoice(unittest.TestCase):
    def test_r3_chosen_turn_changes_with_model_probability(self):
        n=nav_model()
        s=PublicGrid(2,2,4,2,2,False)
        b=n.choose(s)
        self.assertIn(b,(0,1))
        p=[.5,.5,.5];p[b]=.90;p[1-b]=.05
        original,chosen,details=decision(n,s,Pred(p))
        self.assertEqual(original,b)
        self.assertEqual(chosen,1-b)
        self.assertFalse(details["source_alt_selected_effect_observed"])

    def test_source_choice_does_not_change_when_model_frozen(self):
        n=nav_model()
        s=PublicGrid(2,2,4,2,2,False)
        b=n.choose(s)
        self.assertEqual(decision(n,s,Pred([.5,.5,.5]))[1],b)

    def test_original_r3_forward_choice_always_preserved(self):
        n=nav_model()
        s=PublicGrid(2,2,6,2,0,False)
        self.assertEqual(n.choose(s),2)
        self.assertEqual(decision(n,s,Pred([.99,.01,.99])),(2,2,None))

    def test_true_front_block_does_not_hide_or_override_forward(self):
        n=nav_model()
        s=PublicGrid(2,2,6,2,0,True)
        source_sensor_update(n,s)
        self.assertEqual((2,2,0) in n.blocked,True)
        b,a,_=decision(n,s,Pred([.5,.5,.5]))
        self.assertIn(b,(0,1))
        self.assertEqual(a,b)

    def test_non_public_or_missing_physical_motors_denied(self):
        n=nav_model()
        with self.assertRaises(ValueError):
            decision(n,{"x":2,"privileged":True},Pred([.5]*3))
        n.motor["3"]={}
        with self.assertRaisesRegex(ValueError,"INSUFFICIENT"):
            learned_source_motors([event(0,2,True)])

    def test_original_navigator_source_checkpoint_parity(self):
        n=nav_model()
        s=PublicGrid(2,2,4,2,2,False)
        before=decision(n,s,Pred([.9,.1,.5]))
        clone=Navigator.restore(n.snapshot())
        self.assertEqual(before,decision(clone,s,Pred([.9,.1,.5])))

    def test_only_real_selected_motor_forward_examples_count(self):
        rows=[event(d,2,True) for d in range(4)]
        motors=learned_source_motors(rows)
        self.assertEqual(set(motors),{"0","1","2","3"})
        n=source_public_navigator(motors,"MiniGrid-Dynamic-Obstacles-8x8-v0")
        self.assertEqual((n.width,n.height),(8,8))

    def test_gate_fails_for_all_static_predictions(self):
        def results(choices):
            return {"changed_from_r3":sum(x==1 for x in choices),
                    "decisions":[{"model_proposed_action_NOT_EXECUTED":x} for x in choices]}
        data={"native":results([0,0,0]),"frozen":results([0,0,0]),
              "shuffled_action":results([0,0,0])}
        self.assertIn("NO_GO",qualified_disposition(data))
        data["native"]=results([1,0,0])
        self.assertIn("FIT_ONLY_NATIVE",qualified_disposition(data))
        data["frozen"]=results([1,0,0])
        self.assertIn("NO_GO",qualified_disposition(data))


if __name__=="__main__":unittest.main()

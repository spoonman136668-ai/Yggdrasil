"""O22-U unit-only public source/action guard; no original simulator imports."""
import json
import subprocess
import sys
import unittest

from research.optimizer_o22u.cycle_veto import SelectedActionGuard


def frame(x=2,y=3,direction=0,blocked=False):
    return {"x":x,"y":y,"direction":direction,
            "goal_x":6,"goal_y":6,"front_blocked":blocked}


class TestOriginalPublicActionLoopBoundary(unittest.TestCase):
    def test_no_history_makes_no_unwitnessed_veto(self):
        g=SelectedActionGuard()
        self.assertEqual(g.decide(frame(),0,0,1),(1,False))
        self.assertEqual(g.decide(frame(),0,2,2),(2,False))
        self.assertEqual(g.decide(frame(),0,1,1),(1,False))

    def test_immediate_selected_opposite_turn_substitution_veto(self):
        g=SelectedActionGuard()
        g.observe_actual(0,frame(direction=0),1,frame(direction=1))
        # Candidate LEFT would undo actually selected RIGHT. R3 itself wanted RIGHT.
        self.assertEqual(g.decide(frame(direction=1,blocked=True),1,1,0),(1,True))
        self.assertEqual(g.seen,1)
        # Source history is never overwritten with the UNEXECUTED candidate.
        self.assertEqual(g.last_action,1)

    def test_source_original_r3_action_is_never_vetoed(self):
        g=SelectedActionGuard()
        g.observe_actual(0,frame(direction=0),1,frame(direction=1))
        self.assertEqual(g.decide(frame(direction=1),1,0,0),(0,False))
        self.assertEqual(g.decide(frame(direction=1),1,2,2),(2,False))
        with self.assertRaisesRegex(ValueError,"FORWARD"):
            g.decide(frame(direction=1),1,2,1)
        with self.assertRaisesRegex(ValueError,"FORWARD"):
            g.decide(frame(direction=1),1,1,2)

    def test_translated_source_pose_defeats_only_inverse_veto(self):
        g=SelectedActionGuard()
        g.observe_actual(0,frame(direction=0),0,frame(direction=3))
        self.assertEqual(g.decide(frame(x=3,direction=3),1,0,1),(1,False))

    def test_changed_front_alone_is_not_privileged_causal_evidence(self):
        g=SelectedActionGuard()
        g.observe_actual(0,frame(direction=0,blocked=False),1,
                         frame(direction=1,blocked=True))
        self.assertEqual(g.decide(frame(direction=1,blocked=False),1,1,0),
                         (1,True))

    def test_public_chain_guards_and_exact_source_turn_physics(self):
        g=SelectedActionGuard()
        with self.assertRaises(ValueError):
            g.observe_actual(1,frame(direction=0),0,frame(direction=3))
        with self.assertRaises(ValueError):
            g.observe_actual(0,frame(direction=0),0,frame(direction=0))
        with self.assertRaises(ValueError):
            g.observe_actual(0,frame(direction=0),0,frame(x=3,direction=3))
        g.observe_actual(0,frame(direction=0),0,frame(direction=3))
        with self.assertRaises(ValueError):
            g.observe_actual(0,frame(direction=3),2,frame(x=3,direction=3))
        with self.assertRaises(ValueError):
            g.observe_actual(1,frame(x=3,direction=3),0,frame(x=3,direction=2))
        # A genuinely changed current front at same heading may occur in a
        # moving original world. Do not require fake consecutive bit equality.
        g.observe_actual(1,frame(direction=3,blocked=True),0,
                         frame(direction=2,blocked=True))
        self.assertEqual(g.seen,2)

    def test_checkpoint_separate_python_process_and_tamper(self):
        g=SelectedActionGuard()
        g.observe_actual(0,frame(direction=0),1,frame(direction=1))
        raw=g.checkpoint()
        self.assertEqual(SelectedActionGuard.restore(raw).checkpoint(),raw)
        prog=(
            "import sys,json;"
            "from research.optimizer_o22u.cycle_veto import SelectedActionGuard;"
            "g=SelectedActionGuard.restore(sys.stdin.buffer.read());"
            "p={'x':2,'y':3,'direction':1,'goal_x':6,'goal_y':6,"
            "'front_blocked':False};"
            "a,blocked=g.decide(p,1,1,0);"
            "print(json.dumps({'a':a,'veto':blocked,'n':g.seen}))"
        )
        r=subprocess.run([sys.executable,"-B","-c",prog],
                         input=raw,capture_output=True,timeout=20)
        self.assertEqual(r.returncode,0,r.stderr.decode())
        self.assertEqual(json.loads(r.stdout),{"a":1,"veto":True,"n":1})
        tampered=json.loads(raw)
        tampered["state"]["last_action"]=0
        with self.assertRaises(ValueError):
            SelectedActionGuard.restore(json.dumps(tampered).encode())

if __name__=="__main__":
    unittest.main(verbosity=2)

"""Source-free opt-in R18 public mission boundary acceptance, no original env."""
import copy
import unittest

from research.native.itd02.r10.public_adapter import (
    MISSION as OLD_DOORKEY, public_observation as old_door_key_observation)
from research.native.itd02.r18.public_boundary import (
    PublicBoundary, canonical, digest, public_frame, public_digest)

def frame(mission=OLD_DOORKEY,direction=0,front=1):
    image=[[[1,0,0] for _ in range(7)] for _ in range(7)]
    image[3][5]=[front,0,0]
    return {"image":image,"direction":direction,"mission":mission}

class R18NativeBoundaryTests(unittest.TestCase):
    def test_original_door_key_exact_parity(self):
        p=frame()
        self.assertEqual(public_frame(p),old_door_key_observation(p))
        self.assertEqual(public_digest(p),digest(old_door_key_observation(p)))
        self.assertEqual(public_frame(p)["mission"],OLD_DOORKEY)
        p["image"][3][5][0]=4
        self.assertEqual(public_frame(p),old_door_key_observation(p))

    def test_genuine_public_mission_kept_exactly_without_oracle(self):
        a=frame("open the door")
        b=frame("get to the green goal square")
        c=frame("Bring the YELLOW Key Near the Door ")
        for x in (a,b,c):
            self.assertEqual(public_frame(x)["mission"],x["mission"])
            self.assertEqual(public_frame(x)["image"],x["image"])
        self.assertNotEqual(public_digest(a),public_digest(b))
        # Historical original refuses source-new Unlock public mission by design.
        with self.assertRaisesRegex(ValueError,"R10_PUBLIC_MISSION"):
            old_door_key_observation(a)

    def test_fail_closed_private_invalid_source_fields(self):
        p=frame("open the door")
        wrong=[
            dict(p,agent_pos=[1,2]),
            dict(p,hidden_stage="door"),{k:v for k,v in p.items() if k!="mission"},
            dict(p,direction=True),dict(p,direction=4),
            dict(p,mission=""),dict(p,mission="bad\nmission"),
            dict(p,mission="A"*257),dict(p,mission=None),
        ]
        for q in wrong:
            with self.subTest(q=str(q.keys())):
                with self.assertRaises(ValueError):public_frame(q)
        for x in (True,-1,11):
            q=copy.deepcopy(p);q["image"][1][2][0]=x
            with self.assertRaises(ValueError):public_frame(q)
        q=copy.deepcopy(p);q["image"][2][2]=[4,0,99]
        with self.assertRaises(ValueError):public_frame(q)

    def test_source_selected_two_stage_and_cold_restore(self):
        a=frame("open the door");b=frame("open the door",front=4)
        r=PublicBoundary()
        with self.assertRaisesRegex(ValueError,"R18_NO_PUBLIC_ACTION_CAPABILITY"):
            r.commit(0)
        r.begin(a)
        with self.assertRaisesRegex(ValueError,"R18_INVALID_SELECTED_SOURCE_ACTION"):
            r.commit(True)
        r.commit(5)
        with self.assertRaisesRegex(ValueError,"R18_WRONG_SELECTED_SOURCE_ACTION"):
            r.feedback(2,b,0.0)
        self.assertEqual(r.pending,5)
        with self.assertRaisesRegex(ValueError,"R18_ORIGINAL_PUBLIC_MISSION_CHANGED"):
            r.feedback(5,frame("get to the green goal square"),0.0)
        receipt=r.feedback(5,b,0,terminated=False)
        self.assertEqual(receipt["index"],1)
        self.assertEqual(receipt["before"],public_digest(a))
        self.assertEqual(receipt["after"],public_digest(b))
        self.assertEqual(receipt["action"],5)
        with self.assertRaisesRegex(ValueError,"R18_FEEDBACK_NOT_AUTHORIZED"):
            r.feedback(5,b,0)
        blob=r.checkpoint();cold=PublicBoundary.restore(blob)
        self.assertEqual(cold.checkpoint(),blob)
        cold.commit(2)
        pending=cold.checkpoint();again=PublicBoundary.restore(pending)
        self.assertEqual(again.checkpoint(),pending)
        again.feedback(2,b,1.0,terminated=True)
        self.assertTrue(again.finished)
        with self.assertRaisesRegex(ValueError,"R18_NO_PUBLIC_ACTION_CAPABILITY"):
            again.commit(2)
        with self.assertRaises(ValueError):PublicBoundary.restore(blob+b"0")

    def test_feedback_invalid_and_unmodified_public_payload(self):
        a=frame("open the door");x=copy.deepcopy(a)
        b=PublicBoundary();b.begin(a);b.commit(1)
        for reward in (True,float("nan"),float("inf"),-0.01,1.01):
            with self.assertRaisesRegex(ValueError,"R18_UNTRUSTED_SELECTED_SOURCE_RETURN"):
                b.feedback(1,a,reward)
        self.assertEqual(b.events,[])
        self.assertEqual(b.pending,1)
        x["mission"]="changed"
        with self.assertRaises(ValueError):b.feedback(1,x,0)
        b.feedback(1,a,0)
        self.assertEqual(b.current["mission"],"open the door")
        self.assertEqual(public_frame(a),a)

if __name__=="__main__":unittest.main()

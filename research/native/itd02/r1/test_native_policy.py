"""Native Yggdrasil independent three-way action policy source-only tests."""
import json
import os
import subprocess
import sys
import unittest

from research.native.itd02.r1.native_policy import (
    PublicGrid,GridColony,features,SCHEMA)

def scene():
    return PublicGrid(3,3,6,5,0,False)


class NativeYggR1(unittest.TestCase):
    def test_three_legitimate_decisions_are_reachable(self):
        p=GridColony();b=scene()
        self.assertEqual(p.choose(b),0)
        p.observe(b,1,b,1.,True)
        self.assertEqual(p.choose(b),1)
        old=p.cells["1"][0].fast
        for _ in range(5):
            p.observe(b,2,b,1.,True)
        self.assertEqual(p.choose(b),2)
        self.assertEqual(p.cells["1"][0].fast,old)
        self.assertEqual(p.feedback_updates,6)

    def test_public_feedback_is_selected_action_only(self):
        p=GridColony();b=scene()
        after=PublicGrid(4,3,6,5,0,False)
        before=p.save()
        p.observe(b,2,after,0.,False)
        self.assertNotEqual(p.save(),before)
        self.assertTrue(all(c.updates==1 for c in p.cells["2"]))
        self.assertTrue(all(c.updates==0 for a in ("0","1") for c in p.cells[a]))

    def test_invalid_events_transactionally_denied(self):
        p=GridColony();b=scene()
        old=p.save()
        invalid=[(3,0),(-1,0),(2,float("nan")),(2,float("inf")),(2,101)]
        for a,r in invalid:
            with self.assertRaises(ValueError):
                p.observe(b,a,b,r,False)
            self.assertEqual(old,p.save())
        with self.assertRaises(ValueError):
            p.observe(b,0,PublicGrid(-1,3,6,5,0,False),1,False)
        self.assertEqual(old,p.save())
        with self.assertRaises(ValueError):
            p.choose(PublicGrid(3,3,6,5,4,False))

    def test_checkpoint_immutability_integrity(self):
        p=GridColony();b=scene()
        p.observe(b,2,b,1.,True)
        original=p.save()
        another=GridColony.restore(original)
        self.assertEqual(another.save(),original)
        self.assertEqual([p.score(b,a) for a in range(3)],
                         [another.score(b,a) for a in range(3)])
        malformed=json.loads(original)
        malformed["payload"]["feedback_updates"]+=1
        with self.assertRaises(ValueError):
            GridColony.restore(json.dumps(malformed).encode())
        with self.assertRaises(ValueError):
            GridColony.restore(original+b"{}")

    def test_native_cold_process_restoration(self):
        p=GridColony();b=scene()
        for _ in range(4):
            p.observe(b,2,b,1.,True)
        script="""import sys
from research.native.itd02.r1.native_policy import PublicGrid,GridColony
p=GridColony.restore(sys.stdin.buffer.read())
b=PublicGrid(3,3,6,5,0,False)
print('COLD_ACTION='+str(p.choose(b)))
print('COLD_UPDATES='+str(p.feedback_updates))
"""
        result=subprocess.run([sys.executable,"-B","-c",script],input=p.save(),
                              capture_output=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1"),
                              timeout=20)
        self.assertEqual(result.returncode,0,result.stderr.decode())
        self.assertIn(f"COLD_ACTION={p.choose(b)}",result.stdout.decode())
        self.assertIn("COLD_UPDATES=4",result.stdout.decode())

    def test_all_features_public_no_oracle(self):
        phi=features(scene())
        self.assertEqual(len(phi),9)
        self.assertEqual(phi[0],1)
        self.assertEqual(phi[4],1)
        p=GridColony()
        self.assertEqual(set(p.cells),{"0","1","2"})
        self.assertEqual(SCHEMA,"yggdrasil.itd02.r1.public-grid-three-action-cellular-v1")

if __name__=="__main__":
    unittest.main()

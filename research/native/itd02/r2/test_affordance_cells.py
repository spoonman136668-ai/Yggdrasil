"""Yggdrasil R2 source-only real native plasticity and causal custody tests."""
import json
import os
import subprocess
import sys
import unittest
from research.native.itd02.r1.native_policy import PublicGrid
from research.native.itd02.r2.affordance_cells import AffordanceColony

def grid(blocked=True):
    return PublicGrid(3,4,6,7,0,blocked)

class R2OriginalTests(unittest.TestCase):
    def test_no_untrained_sensor_mask(self):
        p=AffordanceColony();s=grid()
        self.assertEqual(p.scores(s),[p.core.score(s,a) for a in range(3)])
        self.assertEqual(p.blocked_samples,0)
    def test_eight_public_failed_actions_establish_penalty(self):
        p=AffordanceColony();s=grid()
        for i in range(8):p.observe(s,2,s,0.,True)
        scores=p.scores(s)
        self.assertLess(scores[2],p.core.score(s,2)-3.)
        self.assertNotEqual(p.choose(s),2)
        u=grid(False)
        self.assertEqual(p.scores(u),[p.core.score(u,a) for a in range(3)])
        self.assertEqual(p.blocked_samples,8)
    def test_no_updating_other_action_credit(self):
        p=AffordanceColony();s=grid()
        for i in range(8):p.observe(s,1,s,0.,True)
        self.assertEqual(p.blocked_samples,0)
        self.assertEqual(p.blocked_fast,0.)
    def test_invalid_feedback_transactional(self):
        p=AffordanceColony();s=grid();old=p.save()
        for a,rew in ((3,0.),(-1,0.),(2,float("nan")),(2,101.)):
            with self.assertRaises(ValueError):
                p.observe(s,a,s,rew,False)
            self.assertEqual(p.save(),old)
    def test_authenticated_checkpoint_and_cold_OS(self):
        p=AffordanceColony();s=grid()
        for i in range(8):p.observe(s,2,s,0.,True)
        b=p.save()
        restored=AffordanceColony.restore(b)
        self.assertEqual(p.scores(s),restored.scores(s))
        w=json.loads(b);w["payload"]["samples"]+=1
        with self.assertRaises(ValueError):
            AffordanceColony.restore(json.dumps(w).encode())
        script="""import json,sys
from research.native.itd02.r1.native_policy import PublicGrid
from research.native.itd02.r2.affordance_cells import AffordanceColony
s=PublicGrid(3,4,6,7,0,True)
p=AffordanceColony.restore(sys.stdin.buffer.read())
print(json.dumps({"a":p.choose(s),"n":p.blocked_samples}))
"""
        q=subprocess.run([sys.executable,"-B","-c",script],input=b,capture_output=True,timeout=20,env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1"))
        self.assertEqual(q.returncode,0,q.stderr.decode())
        self.assertEqual(json.loads(q.stdout),{"a":p.choose(s),"n":8})
    def test_not_a_full_nav_proof(self):
        self.assertNotIn("world_seed",vars(AffordanceColony()))
if __name__=="__main__":unittest.main()

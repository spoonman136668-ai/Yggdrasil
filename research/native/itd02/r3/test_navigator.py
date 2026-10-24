"""Source-only Ygg R3 causal memory/planning and first-use guards."""
import json
import os
import subprocess
import sys
import unittest
from research.native.itd02.r2.affordance_cells import PublicGrid
from research.native.itd02.r3.navigator import Navigator

def g(x=3,y=3,d=0,b=False):return PublicGrid(x,y,6,3,d,b)

def trained():
 p=Navigator();p.reset_episode(8,8)
 deltas=((1,0),(0,1),(-1,0),(0,-1))
 for d,(dx,dy) in enumerate(deltas):
  a=g(3,3,d);b=g(3+dx,3+dy,d)
  p.observe(a,2,b,0.,False,True)
 return p

class R3PublicNative(unittest.TestCase):
 def test_four_source_motor_effects_learned_not_given(self):
  p=Navigator();p.reset_episode(8,8)
  self.assertTrue(all(p._motor(d) is None for d in range(4)))
  p=trained()
  self.assertEqual([p._motor(d) for d in range(4)],[(1,0),(0,1),(-1,0),(0,-1)])
 def test_blocked_forward_creates_only_actual_memory_edge(self):
  p=trained();p.reset_episode(8,8);s=g()
  self.assertEqual(p.choose(s),2)
  p.observe(s,2,s,0.,False,False)
  self.assertIn((3,3,0),p.blocked)
  self.assertNotEqual(p.choose(s),2)
  self.assertNotIn((4,3,0),p.blocked)
 def test_online_episode_memory_does_not_modify_native_R2(self):
  p=trained();p.reset_episode(8,8)
  previous=p.core.save()
  s=g();p.observe(s,2,s,0.,False,False)
  self.assertEqual(p.core.save(),previous)
  self.assertEqual(p.steps,1)
 def test_invalid_transaction_and_checkpoint_sha(self):
  p=trained();p.reset_episode(8,8)
  old=p.snapshot()
  with self.assertRaises(ValueError):
   p.observe(g(),3,g(),0.,False,False)
  self.assertEqual(p.snapshot(),old)
  p.observe(g(),2,g(),0.,False,False)
  restored=Navigator.restore(p.snapshot())
  self.assertEqual(p.choose(g()),restored.choose(g()))
  tamper=json.loads(p.snapshot())
  tamper["data"]["steps"]+=1
  with self.assertRaises(ValueError):
   Navigator.restore(json.dumps(tamper).encode())
 def test_real_cold_python_restart_retains_causal_graph(self):
  p=trained();p.reset_episode(8,8)
  p.observe(g(),2,g(),0.,False,False)
  program="""import sys,json
from research.native.itd02.r3.navigator import Navigator
from research.native.itd02.r2.affordance_cells import PublicGrid
p=Navigator.restore(sys.stdin.buffer.read())
s=PublicGrid(3,3,6,3,0,False)
print(json.dumps({"choice":p.choose(s),"blocked":len(p.blocked),"steps":p.steps}))
"""
  s=subprocess.run([sys.executable,"-B","-c",program],input=p.snapshot(),capture_output=True,timeout=25,env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1"))
  self.assertEqual(s.returncode,0,s.stderr.decode())
  self.assertEqual(json.loads(s.stdout),{"choice":p.choose(g()),"blocked":1,"steps":1})
 def test_unseen_family_transfer_not_claimed(self):
  p=trained();self.assertEqual(p.core.__class__.__name__,"AffordanceColony")
  self.assertFalse(hasattr(p,"unseen_map"))

if __name__=="__main__":unittest.main()

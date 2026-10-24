"""R7 source-only native nonlinear unknown-parent learning guards."""
import json,random,subprocess,sys,unittest
from research.native.itd02.r7.learner import NonlinearLocalLearner

def truth(seed,action,x):
 y=0
 for bit in range(8):
  p=(bit+action)%8;q=(bit+action+2)%8;r=(bit+action+5)%8
  val=(((x>>p)&1)&((x>>q)&1))^((x>>r)&1)^((seed+bit+action)&1)
  y|=val<<bit
 return y

def trained():
 m=NonlinearLocalLearner()
 for seed in (11,13):
  for state in random.Random(seed).sample(range(256),192):
   for action in range(3):m.observe(str(seed),action,state,truth(seed,action,state))
 m.fit()
 return m
class R7Tests(unittest.TestCase):
 def test_actual_nonlinear_unseen_composition(self):
  m=trained()
  for seed in (11,13):
   for x in (9,47,133,222):
    for ops in ((0,1,2),(2,0,0,1,2)):
     result=x
     for a in ops:result=truth(seed,a,result)
     self.assertEqual(m.predict(str(seed),x,ops),result)
 def test_cross_world_different(self):
  m=trained()
  self.assertNotEqual([m.predict("11",i,[0,1]) for i in range(20)],
                      [m.predict("13",i,[0,1]) for i in range(20)])
 def test_invalid_source_is_atomic(self):
  m=NonlinearLocalLearner();m.observe("w",0,7,3)
  for args in (("w",0,7,2),("w",4,1,3),("w",1,300,3)):
   with self.assertRaises(ValueError):m.observe(*args)
  self.assertEqual(m.events,1)
  with self.assertRaises(ValueError):m.fit()
 def test_checksum_and_cold_python_restart(self):
  m=trained();raw=m.checkpoint()
  script="""import json,sys
from research.native.itd02.r7.learner import NonlinearLocalLearner
m=NonlinearLocalLearner.restore(sys.stdin.buffer.read())
print(json.dumps({"events":m.events,"prediction":m.predict("11",177,[0,1,2])}))
"""
  p=subprocess.run([sys.executable,"-B","-c",script],input=raw,capture_output=True,timeout=25)
  self.assertEqual(p.returncode,0,p.stderr.decode())
  self.assertEqual(json.loads(p.stdout),{"events":1152,"prediction":m.predict("11",177,[0,1,2])})
  mod=json.loads(raw);mod["body"]["events"]-=1
  with self.assertRaises(ValueError):NonlinearLocalLearner.restore(json.dumps(mod).encode())
 def test_single_action_lookup_without_hidden_truth(self):
  m=trained()
  for action in range(3):
   for state in (0,63,109,255):
    self.assertEqual(m.step("11",action,state),truth(11,action,state))
  self.assertFalse(hasattr(m,"latent_parents"))
if __name__=="__main__":unittest.main()

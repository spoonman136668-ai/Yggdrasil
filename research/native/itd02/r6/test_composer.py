"""R6 native source qualification: local causal observation, exact composition,
isolated memories, invalid-event atomicity and authenticated cold OS restore."""
import json,os,subprocess,sys,unittest
from research.native.itd02.r6.composer import LocalCausalComposer,INPUTS

def t(world,op,x):
 if world=="w0":return ((x<<1)&63)|(x>>5) if op==0 else (x^13 if op==1 else x^45)
 return ((x>>1)|((x&1)<<5)) if op==0 else (x^22 if op==1 else x^51)

def fit():
 m=LocalCausalComposer()
 for x in INPUTS:
  for w in ("w0","w1"):
   for a in range(3):m.learn(w,a,x,t(w,a,x))
 return m

class NativeR6(unittest.TestCase):
 def test_honest_calibration_required(self):
  m=LocalCausalComposer()
  with self.assertRaises(ValueError):m.predict("w0",22,[0,1,2])
 def test_genuine_composed_unseen_input(self):
  m=fit()
  for world in ("w0","w1"):
   for x in (9,29,56,43):
    for acts in ((0,1,2),(2,2,0,1,0)):
     state=x
     for a in acts:state=t(world,a,state)
     self.assertEqual(m.predict(world,x,acts),state)
 def test_two_world_memories_remain_distinct(self):
  m=fit()
  self.assertNotEqual(m.predict("w0",22,[0,1]),m.predict("w1",22,[0,1]))
  self.assertEqual(m.observations,42)
 def test_invalid_source_is_atomic(self):
  m=fit();original=m.snapshot()
  for args in (("w0",0,0,0),("w0",3,0,2),("w0",0,3,2),("w0",1,1,255)):
   with self.assertRaises(ValueError):m.learn(*args)
   self.assertEqual(m.snapshot(),original)
 def test_cold_process_saved_native_composition(self):
  m=fit();raw=m.snapshot()
  script="""import json,sys
from research.native.itd02.r6.composer import LocalCausalComposer
m=LocalCausalComposer.restore(sys.stdin.buffer.read())
print(json.dumps({"events":m.observations,"w0":m.predict("w0",29,[1,2,0]),"w1":m.predict("w1",29,[1,2,0])}))
"""
  x=subprocess.run([sys.executable,"-B","-c",script],input=raw,capture_output=True,timeout=20,env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1"))
  self.assertEqual(x.returncode,0,x.stderr.decode())
  self.assertEqual(json.loads(x.stdout),{"events":42,"w0":m.predict("w0",29,[1,2,0]),"w1":m.predict("w1",29,[1,2,0])})
  altered=json.loads(raw);altered["payload"]["observations"]=41
  with self.assertRaises(ValueError):LocalCausalComposer.restore(json.dumps(altered).encode())
 def test_no_claim_world_secret_or_novelty(self):
  m=fit()
  self.assertFalse(hasattr(m,"latent_matrix"))
  self.assertFalse(hasattr(m,"physics_backend"))
if __name__=="__main__":unittest.main()

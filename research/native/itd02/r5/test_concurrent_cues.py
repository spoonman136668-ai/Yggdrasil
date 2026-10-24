"""R5 bounded source-only genuine concurrent cue retention and cold process tests."""
import json,os,subprocess,sys,unittest
from research.native.itd02.r5.concurrent_cues import ConcurrentCueMemory

class R5Tests(unittest.TestCase):
 def trained(self):
  x=ConcurrentCueMemory()
  for i in range(32):
   cue="key" if i%2 else "ball"
   x.fit(cue,cue,1.,True)
   x.fit(cue,"ball" if cue=="key" else "key",0.,True)
  return x
 def test_reward_conditional_fit_and_opaque_slot_binding(self):
  x=self.trained()
  for i in range(8):x.present(i,"ball" if i%2 else "key")
  for i in reversed(range(8)):
   self.assertEqual(x.choose(i,"key","ball"),i%2)
   x.release(i)
  self.assertEqual(x.slots,{})
 def test_genuine_independent_slot_interference(self):
  x=self.trained()
  x.present(0,"key");x.present(1,"ball");x.present(2,"key")
  self.assertEqual(x.choose(0,"key","ball"),0)
  self.assertEqual(x.choose(1,"key","ball"),1)
  self.assertEqual(x.choose(2,"key","ball"),0)
 def test_invalid_updates_and_duplicate_slots_atomic(self):
  x=self.trained();x.present(0,"key")
  before=x.snapshot()
  for slot,cue in ((0,"ball"),(9,"ball"),(1,"door")):
   with self.assertRaises(ValueError):x.present(slot,cue)
   self.assertEqual(x.snapshot(),before)
  with self.assertRaises(ValueError):x.choose(1,"key","ball")
 def test_authenticated_cold_OS_mid_concurrent_tasks(self):
  x=self.trained()
  x.present(0,"key");x.present(1,"ball")
  raw=x.snapshot()
  script="""import json,sys
from research.native.itd02.r5.concurrent_cues import ConcurrentCueMemory
x=ConcurrentCueMemory.restore(sys.stdin.buffer.read())
print(json.dumps({"left":x.choose(0,"key","ball"),"right":x.choose(1,"key","ball"),"slots":len(x.slots),"fit":x.training_events}))
"""
  y=subprocess.run([sys.executable,"-B","-c",script],input=raw,capture_output=True,timeout=30,env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1"))
  self.assertEqual(y.returncode,0,y.stderr.decode())
  self.assertEqual(json.loads(y.stdout),{"left":0,"right":1,"slots":2,"fit":64})
  modified=json.loads(raw);modified["data"]["slots"]["0"]="ball"
  with self.assertRaises(ValueError):ConcurrentCueMemory.restore(json.dumps(modified).encode())
 def test_slot_overflow_bounded(self):
  x=self.trained()
  for i in range(8):x.present(i,"key")
  with self.assertRaises(ValueError):x.present(8,"key")
 def test_explicit_not_autonomous_nav_or_novelty(self):
  self.assertFalse(hasattr(ConcurrentCueMemory,"navigate"))
if __name__=="__main__":unittest.main()

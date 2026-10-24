"""R4 cue-memory source-only retention and causal source guards."""
import json,os,subprocess,sys,unittest
from research.native.itd02.r4.cue_cells import CueCells

class R4Tests(unittest.TestCase):
 def test_without_cue_no_model_answer(self):
  x=CueCells()
  with self.assertRaises(ValueError):x.choose("key","ball")
 def test_local_real_reward_updates_actual_selected_option(self):
  x=CueCells()
  for i in range(12):
   x.begin("key")
   x.observe("key",1.,True)
   x.begin("ball")
   x.observe("key",0.,True)
  self.assertEqual(x.outcomes,24)
  x.begin("ball");self.assertEqual(x.choose("key","ball"),1)
  x.begin("key");self.assertEqual(x.choose("key","ball"),0)
 def test_invalid_feedback_atomic(self):
  x=CueCells();x.begin("ball");before=x.snapshot()
  for reward,done in ((float("nan"),True),(1.,False),(-1.,True)):
   with self.assertRaises(ValueError):x.observe("ball",reward,done)
   self.assertEqual(x.snapshot(),before)
 def test_cold_process_retains_episode_cue(self):
  x=CueCells()
  for i in range(8):
   x.begin("ball");x.observe("ball",1.,True)
   x.begin("key");x.observe("ball",0.,True)
  x.begin("ball");raw=x.snapshot()
  script="""import json,sys
from research.native.itd02.r4.cue_cells import CueCells
c=CueCells.restore(sys.stdin.buffer.read())
print(json.dumps({"action":c.choose("key","ball"),"cue":c.cue,"count":c.outcomes}))
"""
  z=subprocess.run([sys.executable,"-B","-c",script],input=raw,capture_output=True,timeout=25)
  self.assertEqual(z.returncode,0,z.stderr.decode())
  self.assertEqual(json.loads(z.stdout),{"action":1,"cue":"ball","count":16})
  o=json.loads(raw);o["data"]["cue"]="key"
  with self.assertRaises(ValueError):CueCells.restore(json.dumps(o).encode())
 def test_cue_removed_causes_inability(self):
  x=CueCells();x.begin("key");x.end()
  with self.assertRaises(ValueError):x.choose("key","ball")
 def test_no_navigation_claim(self):
  self.assertFalse(hasattr(CueCells,"navigate"))
if __name__=="__main__":unittest.main()

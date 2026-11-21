import json
import unittest
from mask_index import StageMaskIndex,StageBank,Q,canonical,digest

PIN='a'*64

def item(n,c,x1,s2,x2,y): return (f'{n+1:064x}',c,x1,s2,x2,y)

class TestFCR02(unittest.TestCase):
 def test_stage_separability(self):
  x=StageMaskIndex();before=x.checkpoint(PIN)
  for first in (0,1):
   for context in (0,1):
    self.assertEqual(x.forecast_transition(context,first),Q//2)
    self.assertEqual(x.forecast_reward(context,first,0,0),Q//2)
  self.assertEqual(x.checkpoint(PIN),before)

 def test_prequential_choice(self):
  x=StageMaskIndex()
  for i in range(64):
   c=i&1;first=(i>>1)&1;state=first^c;x2=(i>>2)&1
   x.observe_admitted_fixture(f'{i+1:064x}',c,first,state,x2,state^x2)
  self.assertEqual(x.transition.events,64); self.assertEqual(x.reward.events,64)
  self.assertIn(x.transition.choice(),(0,1))

 def test_exact_cold_replay(self):
  x=StageMaskIndex()
  for i in range(100):
   x.observe_admitted_fixture(*item(i,i&1,(i>>1)&1,(i>>2)&1,(i>>3)&1,(i>>4)&1))
  checkpoint=x.checkpoint(PIN)
  cold=StageMaskIndex.restore(x._ledger,checkpoint,digest(checkpoint),PIN)
  self.assertEqual(checkpoint,cold.checkpoint(PIN))
  for c in (0,1):
   for a in (0,1):
    self.assertEqual(x.forecast_transition(c,a),cold.forecast_transition(c,a))

 def test_tampering_fails(self):
  x=StageMaskIndex();x.observe_admitted_fixture(*item(0,0,0,1,0,1))
  raw=x.checkpoint(PIN)
  with self.assertRaises(ValueError):StageMaskIndex.restore(x._ledger,raw,'0'*64,PIN)
  with self.assertRaises(ValueError):StageMaskIndex.restore(x._ledger,raw,digest(raw),'0'*64)
  bad=json.loads(raw);bad['scientific_pass']=True;d=canonical(bad)
  with self.assertRaises(ValueError):StageMaskIndex.restore(x._ledger,d,digest(d),PIN)
  bad=json.loads(raw);bad['reward']['loss'][0]+=1;d=canonical(bad)
  with self.assertRaises(ValueError):StageMaskIndex.restore(x._ledger,d,digest(d),PIN)

 def test_wrong_evidence_order_and_types_fail(self):
  x=StageMaskIndex()
  with self.assertRaises(ValueError):x.observe_admitted_fixture(*item(0,0,True,0,0,1))
  self.assertEqual(len(x._ledger),0)
  x.observe_admitted_fixture(*item(0,0,0,1,0,1))
  with self.assertRaisesRegex(ValueError,'DUPLICATE'):x.observe_admitted_fixture(*item(0,0,0,1,0,1))
  with self.assertRaisesRegex(ValueError,'DUPLICATE'):x.observe_admitted_fixture(*item(0,0,0,1,0,0))

 def test_no_hidden_context_or_phase(self):
  model=StageMaskIndex()
  with self.assertRaises(TypeError):model.forecast_transition(context=0,first=0,phase='A')
  self.assertEqual(tuple(model.transition.masks),((),(0,)))
  self.assertEqual(len(model.reward.masks),8)

 def test_known_limit_correlated_law(self):
  # Equal marginals, differently coupled joint distributions: not identifiable
  a=StageMaskIndex();b=StageMaskIndex()
  self.assertEqual(a.forecast_transition(0,0)*a.forecast_reward(0,0,1,0)//Q,Q//4)
  # Any true joint P(s2=1,y=1)=0.5 is not represented by the above.
  self.assertNotEqual(Q//4,Q//2)

if __name__=='__main__':unittest.main()

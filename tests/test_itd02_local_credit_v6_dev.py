import json,unittest,hashlib
from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev,SCHEMA
class LocalCredit(unittest.TestCase):
 def test_selected_only(self):
  self.assertTrue(SCHEMA.endswith("source_only.v7"))
  m=NativeTaskRingBridgeDev()
  m.start_observation("LRV")
  m.accept_public_transition("Backup","Nothing",10,terminal=True)
  self.assertEqual(m.action_credit[0][:2],[0.,0.])
  self.assertNotEqual(m.action_credit[0][2],0.)
  cp=m.checkpoint()
  n=NativeTaskRingBridgeDev.restore(cp)
  self.assertEqual(n.action_credit,m.action_credit)
  n.start_observation("MRV")
  ids=n.model_identities()
  n.start_frozen_evaluation(ids["native"],ids["memory"]) if False else None
 def test_frozen_veto(self):
  m=NativeTaskRingBridgeDev();m.start_observation("LRV");m.accept_public_transition("Backup","Nothing",10,terminal=True)
  ids=m.model_identities();m.start_frozen_evaluation(ids["native"],ids["memory"])
  v=list(m.action_credit);m.start_observation("MRV")
  with self.assertRaisesRegex(ValueError,"FITTING_FORBIDDEN"):
   m.accept_public_transition("Backup","Nothing",10,learning=True)
  self.assertEqual(v,m.action_credit)
if __name__=="__main__":unittest.main()
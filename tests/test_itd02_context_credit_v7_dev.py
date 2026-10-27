import unittest
from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev,SCHEMA
class TestContextCredit(unittest.TestCase):
 def test_only_observed_context_and_action_credit_changes(self):
  self.assertTrue(SCHEMA.endswith("source_only.v7"))
  m=NativeTaskRingBridgeDev();m.start_observation("LRV")
  m.accept_public_transition("Backup","Nothing",10,terminal=True)
  self.assertNotEqual(m.action_credit[0][2],0)
  for i,row in enumerate(m.action_credit):
   for j,value in enumerate(row):
    if (i,j)!=(0,2):self.assertEqual(value,0)
  restored=NativeTaskRingBridgeDev.restore(m.checkpoint())
  self.assertEqual(restored.action_credit,m.action_credit)
 def test_protected_learning_cannot_update(self):
  m=NativeTaskRingBridgeDev();m.start_observation("LRV")
  m.accept_public_transition("Backup","Nothing",10,terminal=True)
  ids=m.model_identities();m.start_frozen_evaluation(ids["native"],ids["memory"])
  m.start_observation("MRV");start=[list(row) for row in m.action_credit]
  with self.assertRaisesRegex(ValueError,"FITTING_FORBIDDEN"):
   m.accept_public_transition("Backup","Nothing",10,learning=True)
  self.assertEqual(start,m.action_credit)
if __name__=="__main__":unittest.main()

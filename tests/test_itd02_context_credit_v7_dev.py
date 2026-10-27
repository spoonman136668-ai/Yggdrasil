import unittest
from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev,SCHEMA
class TestContextCredit(unittest.TestCase):
 def test_only_observed_context_and_action_credit_changes(self):
  self.assertTrue(SCHEMA.endswith("source_only.v8"))
  m=NativeTaskRingBridgeDev();m.start_observation("LRV")
  m.accept_public_transition("Backup","Nothing",10,terminal=True)
  from yggdrasil.itd02_native_task_bridge_dev import _local_ordered_word
  from yggdrasil.itd02_local_ring_memory_dev import ACTION_SITES
  self.assertEqual(len(m.action_credit),3)
  for i,row in enumerate(m.action_credit):
   active=_local_ordered_word("LRV","Backup",ACTION_SITES[i])
   self.assertNotEqual(row[active],0)
   self.assertTrue(all(v==0 for k,v in enumerate(row) if k!=active))
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

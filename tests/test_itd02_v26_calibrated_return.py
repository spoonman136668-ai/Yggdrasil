"""V26 public-only hysteretic-selector source-integrity tests."""
import json,unittest
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev
from yggdrasil.itd02_v26_calibrated_return_dev import CalibratedReturnRingDev
class V26Tests(unittest.TestCase):
 def source(self):
  s=SharedContextRingDev();s.start_observation("LRV");s.accept_first("Backup")
  s.accept_second("GoForward",1.0)
  return s.checkpoint()
 def test_public_only_source_frozen_and_roundtrip(self):
  m=CalibratedReturnRingDev(self.source())
  sha=m.bank.source_sha
  for i in range(6):
   m.start_observation("LRV");m.accept_first("Backup")
   m.accept_second("GoForward",2.0 if i%2 else -1.0)
   self.assertEqual(m.bank.slow.parameters_sha256(),sha)
   self.assertLessEqual(len(m.evidence),4)
   self.assertEqual(CalibratedReturnRingDev.restore(m.checkpoint()).checkpoint(),m.checkpoint())
  m.start_frozen_evaluation();before=m.checkpoint()
  m.start_observation("MRV");m.accept_first("GoForward")
  with self.assertRaises(ValueError):m.accept_second("Backup",1.,learning=True)
  m.accept_second("Backup",0.,learning=False)
  self.assertEqual(m.bank.slow.parameters_sha256(),sha)
 def test_no_hidden_regime_or_bad_checkpoint(self):
  m=CalibratedReturnRingDev(self.source())
  m.start_observation("LRV");m.accept_first("Backup")
  before=m.checkpoint()
  with self.assertRaises(TypeError):
   m.accept_second("Backup",1.0,source_return=True)
  with self.assertRaises(ValueError):
   m.accept_second("Backup",float("nan"))
  self.assertEqual(m.checkpoint(),before)
  packet=json.loads(before);packet["body"]["evidence"]=[1,1,1,1]
  with self.assertRaises(ValueError):
   CalibratedReturnRingDev.restore(json.dumps(packet).encode())
if __name__=="__main__":unittest.main()

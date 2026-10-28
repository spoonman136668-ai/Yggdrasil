"""V31 development-only checks: public reward, no hidden labels, source fixed."""
import unittest
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev
from yggdrasil.itd02_v31_public_history_dev import PublicHistoryGate
class Tests(unittest.TestCase):
 def make(self):
  source=SharedContextRingDev()
  source.start_observation("LRV");source.accept_first("Backup")
  source.accept_second("GoForward",0.5)
  return PublicHistoryGate(source.checkpoint())
 def test_source_and_public_history(self):
  m=self.make();original=m.bank.source_sha
  self.assertEqual(len(m.history),0)
  for i in range(8):
   m.start_observation("LRV");m.accept_first("Backup")
   m.accept_second("GoForward",0.1 if i%2 else -.1)
  self.assertEqual(m.bank.slow.parameters_sha256(),original)
  self.assertEqual(len(m.history),8)
  self.assertLessEqual(len(m.history),12)
 def test_reject_private_regime_and_counterfactual(self):
  m=self.make()
  m.start_observation("LRV");m.accept_first("Backup")
  with self.assertRaises(TypeError):
   m.accept_second("GoForward",0.1,regime="source")
  with self.assertRaises(ValueError):
   m.accept_second("GoForward",float("nan"))
  self.assertFalse(m.history)
  m.accept_second("GoForward",0.2)
  self.assertEqual(len(m.history),1)
 def test_frozen_eval_no_spurious_history(self):
  m=self.make();m.start_observation("LRV");m.accept_first("Backup")
  m.accept_second("GoForward",0.2,learning=False)
  self.assertFalse(m.history)
if __name__=="__main__":unittest.main()

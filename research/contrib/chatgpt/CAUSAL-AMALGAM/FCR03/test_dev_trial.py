import unittest
from dev_trial import (AffineHead,AffineModel,BetaModel,PHASE_LENGTHS,SEEDS,
                       draw,fixture,new_models)

class TrialContracts(unittest.TestCase):
 def test_no_phase_label_in_model_api(self):
  for model in new_models().values():
   with self.assertRaises(TypeError): model.transition_forecast(1,0,'A')
   with self.assertRaises(TypeError): model.admit_fixture('f'*64,0,0,0,0,0,'A')

 def test_fixed_seed_contract(self):
  self.assertEqual(len(SEEDS),8)
  self.assertEqual(len(tuple(fixture(SEEDS[0]))),368)
  self.assertEqual([p for p,_ in tuple(fixture(SEEDS[0]))[:1]],['A_familiar'])
  self.assertEqual(tuple(fixture(SEEDS[0]))[-1][0],'D_nonlinear_unknown')
  self.assertEqual(tuple(fixture(SEEDS[0])),tuple(fixture(SEEDS[0])))

 def test_controls_prequential(self):
  for model in (AffineModel(0),AffineModel(1/32),BetaModel(),BetaModel(32)):
   before=model.transition_forecast(0,0)
   self.assertAlmostEqual(before,0.5)
   model.admit_fixture('f'*64,0,0,1,0,1)
   self.assertGreater(model.transition_forecast(0,0),before)

 def test_hazard_posterior_normalized(self):
  h=AffineHead(4,1/32)
  for i in range(100):
   f=(i&1,(i>>1)&1,(i>>2)&1,(i>>3)&1)
   h.observe(f,f[0]^f[1]^f[3])
  self.assertAlmostEqual(sum(h.weights),1.0)

if __name__=='__main__':unittest.main()

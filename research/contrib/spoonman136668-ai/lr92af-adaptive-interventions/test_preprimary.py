"""Preprimary structural tests. Never instantiate the registered primary seeds."""
import json, pathlib, unittest
import numpy as np
import lr92af_run as m

class StructuralTests(unittest.TestCase):
 def test_hypothesis_identity(self):
  self.assertEqual(m.HYP.shape,(256,8))
  self.assertEqual(len({tuple(v) for v in m.HYP}),256)
 def test_known_context_pattern(self):
  for q in range(3):
   for base in (0,3,8,15):
    truth=m.ground_truth(base,q)
    np.testing.assert_array_equal(truth[4:]^truth[:4],m.Q_PATTERNS[q])
 def test_prior_normalized_and_unseen_independent(self):
  for q in range(3):
   p=m.posterior_prior(q)
   self.assertAlmostEqual(float(p.sum()),1,places=12)
   self.assertTrue(bool(np.all(p>0)))
  self.assertTrue(bool(np.all(m.posterior_prior(2)==1/256)))
 def test_action_blocks(self):
  for n in (4,16,64,112,256):
   seq=m.balanced(np.random.default_rng(31),n)
   self.assertEqual(len(seq),n)
   for i in range(0,n,4):self.assertEqual(set(seq[i:i+4]),{0,1,2,3})
 def test_observation_bayes(self):
  p=m.posterior_prior(0)
  logits=np.log(p)
  m.update_log(logits,0,2,1)
  z=m.normalize(logits)
  self.assertGreater(float(z[m.HYP[:,2]==1].sum()),float(p[m.HYP[:,2]==1].sum()))
 def test_information_gain_well_defined(self):
  p=np.ones(256)/256
  self.assertEqual(m.entropy_choice(p,np.zeros(4,dtype=int)),0)
  self.assertEqual(m.entropy_choice(p,np.array([2,0,0,0])),1)
 def test_preprimary_full_budget_all_policies(self):
  rng=np.random.default_rng(42)
  fit,fy,tape,val,vy,truth=m.make_world(rng,0,9)
  sched=m.balanced(np.random.default_rng(47),64)
  for i,policy in enumerate(m.POLICIES):
   out=m.run_policy(policy,m.posterior_prior(0),fit,fy,tape,val,vy,truth,sched,np.random.default_rng(i+10))
   self.assertEqual(sum(out['counts']),64)
   self.assertEqual(len(out['actions']),64)
   self.assertEqual(out['accepted'],out['confidence']>=.90 and out['fit_misfit_p']>.01)
 def test_validation_never_changes_selection(self):
  rng=np.random.default_rng(55)
  fit,fy,tape,val,vy,truth=m.make_world(rng,1,13)
  sched=m.balanced(np.random.default_rng(57),64)
  a=m.run_policy('eig',m.posterior_prior(1),fit,fy,tape,val,vy,truth,sched,np.random.default_rng(19))
  b=m.run_policy('eig',m.posterior_prior(1),fit,fy,tape,val,1-vy,truth,sched,np.random.default_rng(19))
  for key in ('actions','labels','map_index','confidence','accepted','fit_errors','fit_misfit_p'):
   self.assertEqual(a[key],b[key],key)
 def test_prior_persistence(self):
  d=np.asarray(json.loads(json.dumps(m.DELTA.tolist())),dtype=np.float64)
  np.testing.assert_array_equal(d.view(np.uint64),m.DELTA.view(np.uint64))

if __name__=='__main__':unittest.main(verbosity=2)

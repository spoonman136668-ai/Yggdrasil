"""TRAIN-only mode posterior and strict purchased-source contract tests."""
import importlib.util,pathlib,unittest,sys
P=pathlib.Path(__file__).with_name("train_only.py")
s=importlib.util.spec_from_file_location("yf36",P)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class SourceContract(unittest.TestCase):
  def test_reserved_original_ids_rejected(self):
    self.assertFalse(set(m.TRAIN)&set(m.EVAL))
    self.assertFalse(set(m.TRAIN)&set(m.RESERVED))
    self.assertFalse(set(m.EVAL_FAMILIES)&set(m.RESERVED_FAMILIES))
    with self.assertRaises(ValueError):m.source(253800,230,0,0,0,9)
  def test_public_anchor_distinct_from_target_mode(self):
    a=m.anchors(251800,220,0,0)
    self.assertEqual(len(a),16)
    self.assertTrue(all(len(x)==2 and len(x[1])==4 for x in a))
    public=m.public_reliability(a)
    _,mode,vals,polarity=m.source(251800,220,0,0,0,9000)
    self.assertIn(mode,(0,1))
    self.assertEqual(len(m.features(vals[0],polarity,public)),m.NFEATURES)
  def test_first_paid_read_before_action_and_no_duplicate(self):
    _,_,values,pol=m.source(251800,220,0,0,0,9000)
    bought=m.Bought()
    first=bought.take(values,0)
    with self.assertRaises(ValueError):bought.take(values,0)
    r=m.public_reliability(m.anchors(251800,220,0,0))
    weights=[0.]*m.NFEATURES
    q=[[.5]*3,[.5]*3]
    means=[-.5,.5];var=[.05,.05]
    choice=m.choose("polarity_Bayesian",first,pol,r,m.anchors(251800,220,0,0),weights,q,means,var)
    self.assertIn(choice,(1,2,3))
    bought.take(values,choice)
    with self.assertRaises(ValueError):bought.take(values,3 if choice!=3 else 1)
  def test_genuine_train_only_posterior_and_costs(self):
    weights,q,means,var,n=m.train()
    self.assertEqual(len(weights),6)
    self.assertGreater(n,1000)
    self.assertEqual(len(q),2)
    self.assertLess((6+6+4)*8,m.NATIVE_BYTES)
if __name__=="__main__":unittest.main()

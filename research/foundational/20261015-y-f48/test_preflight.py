import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("y_f48_preflight",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Preflight(unittest.TestCase):
 def test_frozen_seed_and_family_separation(self):
  self.assertFalse(set(m.FIT)&set(m.DIAGNOSTIC))
  self.assertFalse(set(m.DIAGNOSTIC)&set(m.RESERVED))
  self.assertFalse(set(m.DIAGNOSTIC)&set(m.OLD_RESERVED))
  for args in ((422000,624,0,2,0,70000),(401100,620,0,2,0,70000),
               (421100,620,0,0,0,70000)):
   with self.assertRaises(ValueError):m.source(*args)
 def test_public_pairs_truth_held_constant_across_intervention(self):
  a=m.parent.prior.public_pairs(421100,620,2,0)
  self.assertEqual(len(a),12)
  self.assertTrue(all(x[0]==y[0] for x,y in a))
  self.assertTrue(any(x[1][0]!=y[1][0] for x,y in a))
 def test_shift_mechanisms_public_not_secret(self):
  source=m.source(421100,620,0,2,0,97000,0)
  unchanged=m._parent_source(421100,620,0,2,0,97000,0)
  self.assertEqual(source[:2],unchanged[:2])
  self.assertNotEqual(source[2],unchanged[2])
 def test_task_mapping_not_invalid_default(self):
  for fam in m.FAMILIES:
   self.assertEqual(m.parent.prior.task((True,True,False),fam),
     m.parent.old_task((True,True,False),480+fam-620))
 def test_two_channel_no_reuse(self):
  port=m.parent.prior.Port((.1,.2,.3,.4))
  port.buy(0);port.buy(1)
  with self.assertRaises(ValueError):port.buy(2)
if __name__=="__main__":unittest.main()

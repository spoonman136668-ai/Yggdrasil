import importlib.util,json,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
sp=importlib.util.spec_from_file_location("y_f54b",p)
m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m)
pr=json.loads(pathlib.Path(__file__).with_name("prereg.json").read_text())
class Tests(unittest.TestCase):
 def test_complete_frozen_controls_and_disjoint_source(self):
  self.assertEqual(tuple(pr["controls"]),m.ARMS)
  self.assertEqual((m.FIT.start,m.FIT.stop),tuple(pr["fit_seeds"]))
  self.assertEqual((m.DIAG.start,m.DIAG.stop),tuple(pr["diagnostic_seeds"]))
  for sf in ((622000,1248),(591100,1124),(621100,1240)):
   with self.assertRaises(ValueError):m.source(*sf)
 def test_online_query_is_not_an_argument(self):
  events,q,paths=m.source(621000,1240)
  self.assertEqual(len(events),64)
  w,n=m.fit();self.assertEqual(len(w),8)
  for arm in m.ARMS[:-1]:
   records=m.ingest(events,arm,w)
   self.assertLessEqual(len(records),12)
   self.assertTrue(all(len(z[1])<=3 for z in records))
   self.assertIsInstance(m.solve_records(records,dict(start=q["start"],chain=q["chain"],answer=q["answer"])),bool)
 def test_exact_two_hop_composition(self):
  a=m.rawrecord((1,0,2,0),0);b=m.rawrecord((2,1,3,1),1)
  z=m.expand(a,b,2)
  self.assertEqual((z[0],z[1],z[2]),(1,((0,1),(1,1)),3))
  self.assertTrue(m.solve_records([z],dict(start=1,chain=[[0,1],[1,1]],answer=3)))
 def test_witness_index_chain_from_new_fit_only(self):
  # FIT-only audit fixture: every persisted record must reconstruct from
  # publicly observed original edges in the exact role/direction order.
  import math
  events,q,paths=m.source(621000,1240)
  w,n=m.fit()
  for arm in m.ARMS[:-1]:
   for z in m.ingest(events,arm,w):
    at=z[0];self.assertEqual(len(z[1]),len(z[3]))
    for (role,d),ix in zip(z[1],z[3]):
     a,r,b,t=events[ix];self.assertEqual(r,role)
     self.assertEqual((a if d==1 else b),at)
     at=b if d==1 else a
    self.assertEqual(at,z[2])
 def test_inverted_composite_record_reverses_source_edge_indices(self):
  a=m.rawrecord((1,0,2,0),2)
  b=m.rawrecord((2,1,3,1),5)
  z=m.expand(a,b,2)
  rev=m.inverted(z)
  self.assertEqual(rev[3],(5,2))
  self.assertEqual(rev[1],((1,-1),(0,-1)))
 def test_independent_audit_compiles(self):
  compile(pathlib.Path(__file__).with_name("audit_result.py").read_text(),"audit","exec")
if __name__=="__main__":unittest.main()

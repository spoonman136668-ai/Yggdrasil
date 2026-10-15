"""Y-F54 FIT-only: source provenance, balanced tags and native codec."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("y54_fitonly",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_identity_disjoint(self):
  self.assertFalse(set(m.FIT)&set(m.DIAG))
  self.assertFalse(set(m.FIT_FAM)&set(m.DIAG_FAM))
  with self.assertRaises(ValueError):m.source(592000,1068)
  with self.assertRaises(ValueError):m.source(591100,1060)
 def test_balanced_public_tags_and_hidden_query(self):
  public,query,paths,motifs,tags=m.source(591000,1060)
  self.assertEqual(len(public),72)
  self.assertEqual(len(tags),72)
  self.assertIn(len(query["ops"]),(4,6,8))
  core={edge for p in paths for edge in p["edges"]}
  self.assertEqual(sum(bit for e,bit in zip(public,tags) if e in core),16)
  self.assertEqual(sum(bit for e,bit in zip(public,tags) if e not in core),20)
  selected=next(x for x in paths if x["start"]==query["start"])
  self.assertEqual(m.codec.solve([m.codec.edge_record(e) for e in selected["edges"][:len(query["ops"])]],query),query["answer"])
 def test_global_train_and_equal_bytes(self):
  weights,n,packed=m.train()
  self.assertEqual(len(weights),12)
  self.assertEqual(len(packed),12)
  self.assertGreater(n,64*150)
  public,query,paths,motifs,tags=m.source(591000,1061)
  for arm in m.ARMS[:-1]:
   if arm=="F53_frozen_learned_chunker":
    historical,_,_=m.prev.train()
    held=m.prev.retain(public,"learned_future_value_consolidation",historical)
   else:held=m.retain(public,arm,weights)
   self.assertLessEqual(len(held),12)
   self.assertLessEqual(sum(len(m.codec.pack(*e)) for e in held),144)
 def test_offline_public_reference_without_query(self):
  public,q,paths,motifs,tags=m.source(591000,1062)
  memory,work=m.public_offline_reference(public)
  self.assertLessEqual(len(memory),12)
  self.assertLessEqual(work,6001)
  self.assertTrue(all(len(m.codec.pack(*x))==12 for x in memory))
if __name__=="__main__":unittest.main()

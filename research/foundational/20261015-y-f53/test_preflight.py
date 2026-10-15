import importlib.util,json,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
sp=importlib.util.spec_from_file_location("y_f53",p)
m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m)
pr=json.loads(pathlib.Path(__file__).with_name("prereg.json").read_text())
class Qualification(unittest.TestCase):
 def test_exact_cohort_and_control_registry(self):
  self.assertEqual(m.ARMS,(pr["candidate"],*pr["controls"],pr["unfair_control"]))
  self.assertEqual((m.FIT.start,m.FIT.stop),tuple(pr["fit_seeds"]))
  self.assertEqual((m.DIAG.start,m.DIAG.stop),tuple(pr["diagnostic_seeds"]))
  self.assertFalse(set(m.FIT)&set(m.DIAG));self.assertFalse(set(m.DIAG)&set(m.RESERVED))
  for seed,family in ((592000,1128),(571100,1024),(591100,1120)):
   with self.assertRaises(ValueError):m.source(seed,family)
 def test_PUBLIC_memory_path_feature_never_sees_future_question(self):
  events,question,paths=m.source(591000,1120)
  self.assertEqual(len(events),64);self.assertEqual(len(paths),4)
  self.assertEqual(len(question["chain"]),4)
  self.assertEqual(m.solve(question["edges"],question),question["answer"])
  assert len(m.public_features(events[0],events[:13],0))==9
  for arm in m.ARMS[:-1]:
   held,_=m.held_after_ingestion(events,arm,[0.]*9)
   self.assertEqual(len(held),12)
 def test_new_motif_is_not_earlier_heldout_star(self):
  events,question,paths=m.source(591100,1124)
  distractors=[x for x in events if x[:3] not in {e for p in paths for e in p["edges"]}]
  self.assertEqual(len(distractors),48)
  self.assertEqual(sum(x[3] for x in events),32)
 def test_frozen_auditor_compiles_before_DIAG(self):
  q=pathlib.Path(__file__).with_name("audit_result.py")
  compile(q.read_text(),str(q),"exec")
if __name__=="__main__":unittest.main()

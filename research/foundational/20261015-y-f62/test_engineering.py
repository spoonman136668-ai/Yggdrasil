"""Y-F62 source engineering checks: synthetic-only, never FIT/DIAG/original."""
import importlib.util,pathlib,sys,unittest
P=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("y62_source_engineering",P)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
A=P.with_name("audit_public.py")
asp=importlib.util.spec_from_file_location("y62_independent_public_auditor",A)
audit=importlib.util.module_from_spec(asp);asp.loader.exec_module(audit)
class FrozenSourceTests(unittest.TestCase):
 def test_cohort_denial_and_exact_contract(self):
  self.assertEqual((m.TRAIN.start,m.TRAIN.stop),(761000,761008))
  self.assertEqual((m.VALIDATE.start,m.VALIDATE.stop),(761008,761016))
  self.assertEqual(m.FAMILIES,(1460,1461,1462,1463))
  self.assertEqual(m.CAP*m.RECORD_BYTES,144)
  self.assertEqual(len(m.F61_WEIGHTS),12)
  for seed,family in ((741000,1420),(741100,1424),(742000,1428),
                      (761100,1464),(762000,1468)):
   with self.assertRaises(ValueError):m.source(seed,family)
 def test_public_synthetic_causality_and_exact_receipts(self):
  packing=m.codec()
  for seed,family,regime in ((-71,-2,"delayed_public_joins"),
                             (-72,-1,"rolling_interleaved_hubs")):
   tagged,question,paths,observed=m._construct(seed,family)
   self.assertEqual(observed,regime)
   self.assertEqual(len(tagged),72)
   self.assertEqual(len(set(tuple(row[:3]) for row in tagged)),72)
   self.assertEqual(sum(row[3] for row in tagged),36)
   self.assertEqual(len(paths),4)
   public=tuple(row[:3] for row in tagged)
   degrees={}
   for a,_role,b in public:
    degrees[a]=degrees.get(a,0)+1
    degrees[b]=degrees.get(b,0)+1
   hubs=sum(v>=3 for v in degrees.values())
   self.assertEqual(hubs,8 if regime=="rolling_interleaved_hubs" else 0)
   self.assertTrue(m.assert_F60_step_parity(public,packing))
   historical=m.historical_controls_public(public,packing)
   self.assertEqual(set(historical),{
    "F60_exact_source_fixed_online","F59_exact_source_deferred",
    "F58_exact_source_frontier","F61_frozen_learned_policy_no_refit",
    "fixed_public_pair_triple_DAG","fixed_public_FIFO_hash",
    "offline_full_public_graph_extra_work_noncompetitive"})
   for name,records in historical.items():
    m._valid_memory(records,packing)
    self.assertLessEqual(len(records)*12,144,name)
   offline=m.controls()[0].offline_public_witness(public)
   self.assertEqual(offline,historical["offline_full_public_graph_extra_work_noncompetitive"])
   self.assertEqual(packing.solve(offline,question),question["answer"])
   learned,actions,trace=m.learned_online(public,(0,)*12,packing,trace=True)
   claim=audit.verify(public,question,trace)
   self.assertEqual(claim["prefixes"],72)
   self.assertEqual(claim["max_payload_bytes"],12*len(learned) if
                    max(len(z) for z in trace)==len(learned) else
                    12*max(len(z) for z in trace))
   self.assertTrue(claim["publicly_grounded_question"])
   self.assertFalse(claim["source_independent_F3"])
   self.assertEqual(tuple(trace[-1]),tuple(packing.pack(*r).hex() for r in learned))
   # Reject claimed one-step future memory, malformed codec, and private tags.
   future=tuple(packing.pack(*r).hex() for r in (packing.edge_record(public[1]),))
   forged=list(trace);forged[0]=future
   with self.assertRaises(AssertionError):audit.verify(public,question,forged)
   corrupted=list(trace);corrupted[0]=tuple("00"*12 for _ in corrupted[0])
   with self.assertRaises(AssertionError):audit.verify(public,question,corrupted)
   with self.assertRaises(AssertionError):audit.verify(tagged,question,trace)
   self.assertEqual(len(actions),72)
   m._valid_memory(learned,packing)
   self.assertLessEqual(12*len(learned),144)
   with self.assertRaises(AssertionError):m.actions(learned,tagged[0],0,packing)
 def test_counterfactual_label_derivation_on_unregistered_synthetic_only(self):
  packing=m.codec()
  for seed,family in ((-71,-2),(-72,-1)):
   tagged,question,_paths,_regime=m._construct(seed,family)
   public=tuple(row[:3] for row in tagged)
   examples,count=m.counterfactual_labels(public,question,packing)
   self.assertTrue(examples)
   self.assertEqual(sum(count.values()),len(examples))
   self.assertEqual(set(count),{-1,0,1})
   self.assertTrue(all(len(features)==12 and delta in (-1,0,1)
                       for features,delta in examples))
   self.assertTrue(any(delta==0 for _features,delta in examples))
  # The online entrypoint cannot receive offline future-task truth.
  import inspect
  self.assertEqual(tuple(inspect.signature(m.learned_online).parameters),
                   ("public","weights","packing","trace","allow_composition"))

 def test_frozen_no_composition_ablation_on_synthetic_public_only(self):
  packing=m.codec()
  for seed,family in ((-71,-2),(-72,-1)):
   tagged,question,_paths,_regime=m._construct(seed,family)
   public=tuple(x[:3] for x in tagged)
   normal,normal_choices,normal_trace=m.learned_online(
     public,(0,)*12,packing,trace=True,allow_composition=True)
   without,ablation_choices,ablation_trace=m.learned_online(
     public,(0,)*12,packing,trace=True,allow_composition=False)
   self.assertEqual(len(normal_choices),len(ablation_choices))
   self.assertEqual(len(ablation_choices),72)
   self.assertTrue(all(choice[0]!="merge" for choice in ablation_choices))
   self.assertEqual(len(normal_trace),len(ablation_trace))
   self.assertEqual(audit.verify(public,question,normal_trace)["prefixes"],72)
   self.assertEqual(audit.verify(public,question,ablation_trace)["prefixes"],72)
   m._valid_memory(normal,packing)
   m._valid_memory(without,packing)
   self.assertEqual(len(audit.proposals((),public[0])),1)


 def test_exact_historical_source_witnesses(self):
  f60,f59,f58,f61=m.controls()
  self.assertEqual(f60.online_fixed.__name__,"online_fixed")
  self.assertEqual(f59.fixed_deferred_component_buffer.__name__,
                   "fixed_deferred_component_buffer")
  self.assertEqual(f58.frontier_online.__name__,"frontier_online")
  self.assertEqual(f61.PARAMS,12)
 def test_no_execution_authority(self):
  d=m.source_only_manifest()
  self.assertTrue(d["train_not_executed"])
  self.assertTrue(d["validation_not_executed"])
  self.assertTrue(d["diagnostic_not_executed"])
  self.assertTrue(d["original_not_executed"])
  self.assertFalse(d["independent_F3"])
  self.assertFalse(d["policy_promotion"])
if __name__=="__main__":unittest.main()

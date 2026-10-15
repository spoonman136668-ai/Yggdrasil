"""Y-F53 independent byte-exact relation-chunk audit; source cohort not rerun."""
import importlib.util,json,math,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("y53_pinned_source",ROOT/"source_pilot.py")
m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m)
def audit(path,prereg):
 d=json.load(open(path));p=json.load(open(prereg))
 t=p["fit"];v=p["diagnostic"];arms=p["controls"];st=p["stream"];g=p["thresholds"]
 assert d["schema"]=="yggdrasil.f53.future-value-chain-memory.trainonly.v1"
 assert d["stage"]=="TRAIN_ONLY_UNSEEN_GRAPH_AND_QUESTION_NO_ORIGINAL"
 assert d["fit_seeds"]==t["seeds"] and d["fit_families"]==t["families"]
 assert d["diagnostic_seeds"]==v["seeds"] and d["diagnostic_families"]==v["families"]
 assert set(t["families"]).isdisjoint(v["families"])
 assert d["cases"]==len(d["rows"])==v["expected_streams"]==64
 assert d["max_records"]==st["records_max"]==12
 assert d["serialized_record_bytes"]==st["record_bytes"]==12
 assert d["serialized_payload_budget"]==st["memory_payload_bytes_max"]==144
 assert d["decoder_metadata_in_record"] and d["native_576B_total_unverified"]
 assert d["future_question_hidden_during_retention"]
 assert not d["independent_F3"] and not d["original_executed"]
 assert not d["accepted_ref_mutation"] and d["paid_api_calls"]==0
 assert d["proposed_original_NOT_RESERVED"]==[m.RESERVED.start,m.RESERVED.stop]
 # The frozen Y-F53 prereg does not define a future original seed range; this
 # explicit source-only exclusion is not retroactively treated as a prereg gate.
 weights,n,packed=m.train()
 assert d["train_examples"]==n and d["learned_weight_int8"]==packed
 seen=set();actual={a:0 for a in arms};ablation=0
 for row in d["rows"]:
  seed,fam=row["seed"],row["family"]
  assert (seed,fam) not in seen;seen.add((seed,fam))
  assert seed in m.DIAG and fam in m.DIAG_FAM
  events,future,paths,motifs=m.source(seed,fam)
  assert row["public_events"]==[list(z) for z in events]
  assert row["question"]==dict(start=future["start"],ops=[list(x) for x in future["ops"]],answer=future["answer"])
  assert len(row["public_events"])==st["public_events"]==72
  assert len(future["ops"]) in st["query_hops"]
  assert set(row["answers"])==set(arms)
  assert set(row["receipts"])==set(arms[:-1])
  for arm in arms[:-1]:
   records=[m.codec.unpack(bytes.fromhex(v)) for v in row["receipts"][arm]]
   assert len(records)<=12
   assert sum(len(m.codec.pack(*r)) for r in records)<=144
   assert all(m.codec.pack(*r).hex()==hexvalue for r,hexvalue in zip(records,row["receipts"][arm]))
   # The encoded path is not permitted to hallucinate any edge absent in the
   # public source, including every intermediate composed relation.
   for rec in records:
    # The public graph may contain legitimately ambiguous branch-role edges.
    # Verify *existence* of the exact composed public path, not uniqueness.
    reachable={rec[0]}
    for code in rec[2]:
     role=code//2;direction=-1 if code&1 else 1
     reachable={e[2] if direction==1 else e[0]
                for at in reachable for e in events if e[1]==role and
                (e[0] if direction==1 else e[2])==at}
     assert reachable
    assert rec[1] in reachable
   recomputed=m.codec.solve(records,future)
   assert row["answers"][arm]==int(recomputed==future["answer"])
   if arm==arms[0]:
    stripped=[r for r in records if len(r[2])==1]
    no_composition=int(m.codec.solve(stripped,future)==future["answer"])
    assert no_composition==row["retrieval_without_composed_chunks"]
    ablation+=no_composition
   actual[arm]+=row["answers"][arm]
  assert row["answers"][arms[-1]]==1
  actual[arms[-1]]+=1
 assert len(seen)==64
 for arm in arms:
  assert d["scores"][arm]["correct"]==actual[arm]
  assert d["scores"][arm]["total"]==64
  assert math.isclose(d["scores"][arm]["accuracy"],actual[arm]/64,abs_tol=1e-12)
 for fam in v["families"]:
  rows=[r for r in d["rows"] if r["family"]==fam]
  assert len(rows)==16
  for arm in arms:
   assert d["by_family"][str(fam)][arm]==sum(r["answers"][arm] for r in rows)
 fair=arms[1:-1]
 best=max(fair,key=lambda a:actual[a])
 gain=(actual[arms[0]]-actual[best])/64
 retrieval=(actual[arms[0]]-ablation)/64
 guard=all(d["by_family"][str(f)][arms[0]]>=max(
   d["by_family"][str(f)][a] for a in fair) for f in v["families"])
 passed=gain>=g["gain_vs_strongest_equal_byte_fair_min"] and retrieval>0 and guard
 assert d["strongest_equal_byte_fair"]==best
 assert math.isclose(d["candidate_gain"],gain,abs_tol=1e-12)
 assert math.isclose(d["retrieval_ablation_gain"],retrieval,abs_tol=1e-12)
 assert d["per_family_nondegradation"]==guard and d["frozen_gate_met"]==passed
 assert d["verdict"]==("TRAIN_ONLY_CHAIN_VALUE_SUPPORTED" if passed else "TRAIN_ONLY_CHAIN_VALUE_NEGATIVE")
 print("Y_F53",d["verdict"],"correct",actual,"gain",gain,"retrieval_gain",retrieval,"family_guard",guard)
if __name__=="__main__":
 if len(sys.argv)!=3:raise SystemExit("expected RESULT_JSON FROZEN_PREREG_JSON")
 audit(*sys.argv[1:])

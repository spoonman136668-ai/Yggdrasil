"""Y-F52 independent exact 12-byte record and question-visibility audit.

No candidate retraining, no source experiment replay. Rebuild semantic
question answers exclusively from archived serialized memory payloads.
"""
import importlib.util,json,math,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("yf52_audit_source",ROOT/"source_pilot.py")
m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m)
def audit(path,prereg):
 d=json.load(open(path));p=json.load(open(prereg))
 t=p["train"];v=p["diagnostic"];arms=p["controls"];st=p["stream"];g=p["thresholds"]
 assert d["schema"]=="yggdrasil.f52.online-relation-chunks.trainonly.v1"
 assert d["stage"]=="TRAIN_ONLY_DISJOINT_TOPOLOGY_AND_MEMORY_NOT_ORIGINAL"
 assert d["fit_seeds"]==t["seeds"] and d["fit_families"]==t["families"]
 assert d["diagnostic_seeds"]==v["seeds"] and d["diagnostic_families"]==v["families"]
 assert set(d["fit_families"]).isdisjoint(d["diagnostic_families"])
 assert d["cases"]==len(d["rows"])==v["expected_streams"]==64
 assert d["train_examples"]==t["expected_train_streams"]*st["events_per_stream"]==4608
 assert d["records_max"]==st["max_records"]==12 and d["record_bytes"]==st["stored_record_bytes"]==12
 assert d["total_payload_max_bytes"]==st["memory_payload_budget_bytes"]==144
 assert d["query_hidden_until_memory_frozen"]
 assert d["original_seeds_NOT_RESERVED"]==p["future_original_NOT_RESERVED"]["seeds"]
 assert not d["independent_F3"] and not d["primary_original_executed"]
 assert d["native_576B_total_unverified"] and not d["accepted_ref_mutation"]
 assert d["paid_api_calls"]==0
 assert len(d["weights"])==7
 seen=set();scores={a:0 for a in arms}
 for row in d["rows"]:
  key=row["seed"],row["family"]
  assert key not in seen;seen.add(key)
  assert 551100<=row["seed"]<551116 and row["family"] in v["families"]
  assert len(row["public_events"])==72
  assert len(row["query"]["ops"]) in st["query_lengths"]
  assert set(row["results"])==set(arms)
  assert set(row["receipts"])==set(arms)-{"private_future_question_oracle_unfair"}
  public=[tuple(x) for x in row["public_events"]]
  future=dict(start=row["query"]["start"],ops=[tuple(x) for x in row["query"]["ops"]],answer=row["query"]["answer"])
  for arm,records in row["receipts"].items():
   assert len(records)<=12
   serialized=[bytes.fromhex(x) for x in records]
   assert all(len(item)==12 for item in serialized)
   assert sum(len(item) for item in serialized)<=144
   decoded=[m.unpack(x) for x in serialized]
   assert all(m.pack(*r)==x for r,x in zip(decoded,serialized))
   for entry in decoded:
    # Every encoded composition must correspond to one actual observable
    # path through the frozen public graph, without private hidden graph use.
    at=entry[0]
    for code in entry[2]:
     role=code//2;direction=-1 if code&1 else 1
     choices=[e for e in public if e[1]==role and
              (e[0] if direction==1 else e[2])==at]
     assert len(choices)==1
     e=choices[0];at=e[2] if direction==1 else e[0]
    assert at==entry[1]
   value=int(m.solve(decoded,future)==future["answer"])
   assert row["results"][arm]==value
  assert row["results"]["private_future_question_oracle_unfair"]==1
  for arm in arms:
   assert row["results"][arm] in (0,1)
   scores[arm]+=row["results"][arm]
 assert len(seen)==64
 for arm in arms:
  assert d["scores"][arm]["correct"]==scores[arm]
  assert d["scores"][arm]["total"]==64
  assert math.isclose(d["scores"][arm]["accuracy"],scores[arm]/64,abs_tol=1e-12)
 for f in v["families"]:
  sub=[row for row in d["rows"] if row["family"]==f]
  assert len(sub)==16
  for arm in arms:
   assert d["by_family"][str(f)][arm]==sum(row["results"][arm] for row in sub)
 fair=arms[1:-1]
 best=max(fair,key=lambda a:scores[a])
 gain=(scores["learned_relation_chunking"]-scores[best])/64
 nonreg=all(d["by_family"][str(f)]["learned_relation_chunking"]>=
       max(d["by_family"][str(f)][arm] for arm in fair) for f in v["families"])
 passed=gain>=g["gain_over_strongest_equal_byte_fair_min"] and nonreg
 assert d["strongest_equal_byte_fair_control"]==best
 assert math.isclose(d["candidate_gain"],gain,abs_tol=1e-12)
 assert d["family_nondegradation"]==nonreg and d["frozen_gate_met"]==passed
 assert d["verdict"]==("TRAIN_ONLY_RELATION_CHUNKING_SUPPORTED" if passed else "TRAIN_ONLY_RELATION_CHUNKING_NEGATIVE")
 print("Y_F52",d["verdict"],"correct",scores,"gain",gain,"family_guard",nonreg)
if __name__=="__main__":
 if len(sys.argv)!=3:raise SystemExit("expected RESULT_JSON PREREG_JSON")
 audit(*sys.argv[1:])

"""Y-F54 independent, source-free synthetic result audit.

Reads only frozen preregistration and immutable experiment JSON. It does not
import the source generator/model or run another experiment. All retained
paths must be real paths through public events; original first uses untouched.
"""
import json,math,sys
from pathlib import Path
def check(d,p):
 assert p["schema"]=="yggdrasil.f54.public-identifiability-and-learned-global-memory.prereg.v1"
 assert d["schema"]=="yggdrasil.f54.global-public-memory.trainonly.v1"
 assert d["stage"]=="TRAIN_ONLY_NEW_GLOBAL_QUERY_BLIND_MEMORY_NOT_ORIGINAL"
 for field,cohort in (("fit","fit"),("diagnostic","diagnostic")):
  assert d[field+"_seeds"]==p[cohort]["seeds"]
  assert d[field+"_families"]==p[cohort]["families"]
 assert set(d["fit_families"]).isdisjoint(d["diagnostic_families"])
 assert d["original_seeds_NOT_RESERVED"]==p["future_original_NOT_RESERVED"]["seeds"]
 assert d["cases"]==len(d["rows"])==p["diagnostic"]["expected_streams"]==64
 assert d["max_records"]==p["stream"]["records_max"]==12
 assert d["record_bytes"]==p["stream"]["record_bytes"]==12
 assert d["serialized_payload_budget_bytes"]==p["stream"]["memory_payload_max_bytes"]==144
 assert d["public_tag_core_rate"]==d["public_tag_distractor_rate"]==.5
 assert d["future_question_hidden_until_retention_complete"]
 assert d["reference_extra_work_noncompetitive"]
 assert not d["physically_measured_native_total_576B"]
 assert d["independent_F3"] is False and d["original_executed"] is False
 assert d["accepted_ref_mutation"] is False and d["paid_api_calls"]==0
 assert len(d["learned_weight_int8"])==12
 arms=p["controls"]
 assert set(d["scores"])==set(arms)
 seen=set();count={a:0 for a in arms};by={str(f):{a:0 for a in arms} for f in p["diagnostic"]["families"]}
 reference_correct=reference_work=ablation=0
 for row in d["rows"]:
  key=row["seed"],row["family"]
  assert key not in seen;seen.add(key)
  assert p["diagnostic"]["seeds"][0]<=key[0]<p["diagnostic"]["seeds"][1]
  assert key[1] in p["diagnostic"]["families"]
  assert len(row["public_events"])==p["stream"]["public_edges_per_stream"]==72
  assert len(row["public_tags"])==72
  assert sum(row["public_tags"])==36
  assert all(v in (0,1) for v in row["public_tags"])
  q=row["question"];assert len(q["ops"]) in p["stream"]["future_question_path_lengths"]
  assert set(row["answers"])==set(arms)
  assert set(row["receipts"])==set(arms[:-1])
  public=[tuple(e) for e in row["public_events"]]
  assert len(set(public))==72
  for arm in arms[:-1]:
   payloads=[bytes.fromhex(h) for h in row["receipts"][arm]]
   assert len(payloads)<=12
   assert all(len(h)==12 for h in payloads)
   assert len(payloads)*12<=144
   chunks=[]
   for raw in payloads:
    a=int.from_bytes(raw[:4],"little");b=int.from_bytes(raw[4:8],"little")
    bits=int.from_bytes(raw[8:11],"little");length=raw[11]
    assert 1<=length<=6 and bits>>(3*length)==0
    codes=tuple((bits>>(3*i))&7 for i in range(length))
    chunks.append((a,b,codes))
    reachable={a}
    for code in codes:
     role=code//2;direct=-1 if code&1 else 1
     reachable={e[2] if direct==1 else e[0]
         for at in reachable for e in public
         if e[1]==role and (e[0] if direct==1 else e[2])==at}
     assert reachable
    assert b in reachable
   # Independent deterministic decoder of retained compact path records.
   at=q["start"];remaining=tuple(2*r+(direction==-1) for r,direction in q["ops"])
   while remaining:
    choices=set()
    for a,b,c in chunks:
     for start,end,code in ((a,b,c),(b,a,tuple(x^1 for x in reversed(c)))):
      if start==at and remaining[:len(code)]==code:choices.add((start,end,code))
    if len(choices)!=1:break
    start,end,code=next(iter(choices))
    at=end;remaining=remaining[len(code):]
   answer=int(not remaining and at==q["answer"])
   assert row["answers"][arm]==answer
   count[arm]+=answer;by[str(row["family"])][arm]+=answer
   if arm==arms[0]:
    compact=[c for c in chunks if len(c[2])==1]
    state=q["start"];left=tuple(2*r+(d==-1) for r,d in q["ops"])
    while left:
     choices=set()
     for a,b,c in compact:
      for start,end,code in ((a,b,c),(b,a,tuple(x^1 for x in reversed(c)))):
       if start==state and left[:len(code)]==code:choices.add((start,end,code))
     if len(choices)!=1:break
     _,end,code=next(iter(choices));state=end;left=left[len(code):]
    result=int(not left and state==q["answer"])
    assert result==row["retrieval_without_composed_chunks"]
    ablation+=result
  assert row["answers"][arms[-1]]==1
  count[arms[-1]]+=1;by[str(row["family"])][arms[-1]]+=1
  reference_correct+=row["bounded_offline_public_reference_correct"]
  expansions=row["bounded_offline_public_reference_expansions"]
  assert 0<=expansions<=6001
  reference_work+=expansions
 assert len(seen)==64 and by==d["by_family"]
 for arm in arms:
  assert d["scores"][arm]["correct"]==count[arm] and d["scores"][arm]["total"]==64
  assert math.isclose(d["scores"][arm]["accuracy"],count[arm]/64,abs_tol=1e-12)
 assert d["bounded_offline_public_reference_correct"]==reference_correct
 assert d["bounded_offline_public_reference_expansions"]==reference_work
 fair=arms[1:-1];best=max(fair,key=lambda a:count[a])
 gain=(count[arms[0]]-count[best])/64
 retrieval=(count[arms[0]]-ablation)/64
 no_reg=all(by[str(f)][arms[0]]>=max(by[str(f)][a] for a in fair) for f in p["diagnostic"]["families"])
 passed=gain>=p["thresholds"]["gain_vs_strongest_equal_byte_fair_min"] and retrieval>0 and no_reg
 assert d["strongest_equal_byte_fair"]==best
 assert math.isclose(d["candidate_gain"],gain,abs_tol=1e-12)
 assert math.isclose(d["retrieval_ablation_gain"],retrieval,abs_tol=1e-12)
 assert d["per_family_nondegradation"]==no_reg and d["frozen_gate_met"]==passed
 assert d["verdict"]==("TRAIN_ONLY_GLOBAL_MEMORY_SUPPORTED" if passed else "TRAIN_ONLY_GLOBAL_MEMORY_NEGATIVE")
 return dict(result=d["verdict"],candidate_correct=count[arms[0]],
    strongest_fair=best,strongest_fair_correct=count[best],gain=gain,
    retrieval_gain=retrieval,per_family_nondegradation=no_reg,
    reference_correct=reference_correct,reference_work=reference_work,
    source_train_only=True,accepted_original=False)
if __name__=="__main__":
 assert len(sys.argv)==3
 print(json.dumps(check(json.loads(Path(sys.argv[1]).read_text()),
                        json.loads(Path(sys.argv[2]).read_text())),sort_keys=True))

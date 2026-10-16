"""Independent source-free Y-F57 FIT validation artifact and byte receipts.

Does NOT import policy/model/source or recompute any sealed original.
Each encoded record must reproduce a publicly witnessed role chain.
Answers are decoded independently with ambiguity rejection, from archived
public graph and fixed query. Recount prespecified fair and family gates.
"""
import json,math,sys
from pathlib import Path
def decode(records,query):
 remaining=tuple(2*r+(d==-1) for r,d in query["ops"])
 at=query["start"];seen=set()
 while remaining:
  options=set()
  for a,b,codes in records:
   for start,end,ops in ((a,b,codes),(b,a,tuple(v^1 for v in reversed(codes)))):
    if start==at and remaining[:len(ops)]==ops:options.add((start,end,ops))
  if len(options)!=1:return None
  start,end,ops=next(iter(options));at=end;remaining=remaining[len(ops):]
  state=(at,remaining)
  if state in seen:return None
  seen.add(state)
 return at
def audit(result,pre):
 d=json.loads(Path(result).read_text())
 p=json.loads(Path(pre).read_text())
 assert d["schema"]=="yggdrasil.f57.trainable-causal-component.within-FIT.v1"
 assert d["stage"]=="F57_NEW_FIT_SPLIT_ONLY_NO_DIAGNOSTIC"
 assert d["parent_F57_frozen_source_head"]==p["parent_f57_source_head"]
 assert d["training_seeds"]==p["fit_training"]["seeds"]
 assert d["validation_seeds"]==p["fit_validation"]["seeds"]
 assert d["FIT_families"]==p["fit_validation"]["families"]
 assert set(range(*d["training_seeds"])).isdisjoint(range(*d["validation_seeds"]))
 assert d["validation_cases"]==len(d["rows"])==32
 assert d["training_cases"]==32
 assert len(d["learned_int8_policy_parameters"])==p["policy"]["trainable_integer_parameter_count"]==6
 assert all(isinstance(x,int) and -8<=x<=8 for x in d["learned_int8_policy_parameters"])
 assert 4<=d["candidates_examined"]<=p["policy"]["max_fit_only_candidates"]==64
 assert d["records_max"]==12 and d["record_bytes"]==12
 assert d["persistent_record_budget_bytes"]==144
 assert d["learned_parameter_bytes"]==6
 assert d["model_params_not_in_144B_record_count"]
 assert d["query_and_core_membership_hidden_during_policy"]
 assert d["future_DIAG_untouched"] and d["originals_untouched"]
 assert not d["independent_F3"] and d["native_total_576B_unverified"]
 assert not d["accepted_ref_mutation"] and d["paid_API_calls"]==0
 # Frozen protocol and archived result use different labels for three
 # *existing* arms. This is a reporting alias, not a scientific control
 # change: source, comparisons, gates and original receipt remain immutable.
 canonical={
  "learned_train_FIT_only":"learned_causal_component",
  "frozen_F57_causal_online":"frozen_F57_online",
  "fixed_pair_chunk":"fixed_pair_chunk",
  "fixed_triple_chunk":"fixed_triple_chunk",
  "public_component_priority":"public_component_priority",
  "public_FIFO":"public_FIFO",
  "public_hash":"public_hash",
  "public_offline_full_graph_noncompetitive":"offline_full_public_noncompetitive",
  "future_query_oracle_unfair":"future_query_oracle_unfair"}
 assert set(p["controls"])==set(canonical)
 arms=tuple(canonical[a] for a in p["controls"])
 assert set(arms)==set(d["correct"])
 assert set(d["by_family"])==set(str(f) for f in d["FIT_families"])
 totals={a:0 for a in arms};by={str(f):{a:0 for a in arms} for f in d["FIT_families"]}
 seen=set();ablate=0
 for row in d["rows"]:
  seed,fam=row["seed"],row["family"]
  assert (seed,fam) not in seen;seen.add((seed,fam))
  assert d["validation_seeds"][0]<=seed<d["validation_seeds"][1]
  assert fam in d["FIT_families"]
  assert row["regime"] in ("clustered","bounded_interleave")
  events=[tuple(z) for z in row["public_events"]]
  assert len(events)==72 and len(set(events))==72
  q=row["question"]
  assert len(q["ops"]) in (4,6,8)
  assert set(row["answers"])==set(arms)
  assert set(row["receipts"])==set(arms[:-2])
  for arm in arms[:-2]:
   chunks=[]
   raw=row["receipts"][arm]
   assert len(raw)<=12
   for hex_record in raw:
    item=bytes.fromhex(hex_record)
    assert len(item)==12
    a=int.from_bytes(item[:4],"little");b=int.from_bytes(item[4:8],"little")
    packed=int.from_bytes(item[8:11],"little");n=item[11]
    assert 1<=n<=6 and packed>>(3*n)==0
    codes=tuple((packed>>(3*i))&7 for i in range(n))
    rec=(a,b,codes)
    # Public path proof must account for branching, not require a unique
    # member edge at each step of a losslessly combined record.
    reachable={a}
    for v in codes:
     r=v//2;direction=-1 if v&1 else 1
     reachable={e[2] if direction==1 else e[0]
           for at in reachable for e in events
           if e[1]==r and (e[0] if direction==1 else e[2])==at}
     assert reachable
    assert b in reachable
    chunks.append(rec)
   score=int(decode(chunks,q)==q["answer"])
   assert score==row["answers"][arm]
   if arm==arms[0]:
    v=int(decode([chunk for chunk in chunks if len(chunk[2])==1],q)==q["answer"])
    assert v==row["learned_without_chunks"]
    ablate+=v
  assert row["answers"][arms[-1]]==1
  # Offline noncompetitive reference is allowed in the evidence only as
  # a distinct non-fair comparison; never a selectable policy.
  for arm in arms:
   assert row["answers"][arm] in (0,1)
   totals[arm]+=row["answers"][arm]
   by[str(fam)][arm]+=row["answers"][arm]
 assert len(seen)==32
 assert totals==d["correct"] and by==d["by_family"]
 online_fair=arms[1:-2]
 strongest=max(online_fair,key=lambda a:totals[a])
 gain=(totals[arms[0]]-totals[strongest])/32
 comp=(totals[arms[0]]-ablate)/32
 safe=all(by[str(f)][arms[0]]>=max(by[str(f)][arm] for arm in online_fair) for f in d["FIT_families"])
 accepted=gain>=p["acceptance"]["gain_over_strongest_same_144B_online_min_absolute"] and comp>0 and safe
 assert strongest==d["strongest_same_byte_online_fair"]
 assert math.isclose(d["learned_gain_vs_fair"],gain,abs_tol=1e-12)
 assert math.isclose(d["learned_composition_ablation_gain"],comp,abs_tol=1e-12)
 assert d["per_family_nondegradation"]==safe and d["frozen_gate_met"]==accepted
 assert d["verdict"]==("FIT_ONLY_LEARNED_CAUSAL_CONSOLIDATION_SUPPORTED" if accepted else "FIT_ONLY_LEARNED_CAUSAL_CONSOLIDATION_NEGATIVE")
 print("Y_F57_LEARNED_FIT_AUDIT",json.dumps(dict(scores=totals,strongest_fair=strongest,gain=gain,composition=comp,family_guard=safe,qualified=accepted),sort_keys=True))
if __name__=="__main__":
 assert len(sys.argv)==3
 audit(sys.argv[1],sys.argv[2])

"""Y-F60 source-free public-path / 144-byte memory / FIT result audit.

Independently checks that every encoded retained relationship can be built
from the 72 public observations. No project source/model imported and no
diagnostic/original identities are executed.
"""
import json,sys
def solve(chunks,q):
 want=tuple(2*r+(d==-1) for r,d in q["ops"])
 states={(q["start"],0)}
 for _ in range(len(want)):
  next_states=set(states)
  for at,i in states:
   for a,b,c in chunks:
    for u,v,ops in ((a,b,c),(b,a,tuple(k^1 for k in reversed(c)))):
     if at==u and want[i:i+len(ops)]==ops:next_states.add((v,i+len(ops)))
  if next_states==states:break
  states=next_states
 return int((q["answer"],len(want)) in states)
def decode(hexrec,public):
 raw=bytes.fromhex(hexrec);assert len(raw)==12
 a=int.from_bytes(raw[:4],"little");b=int.from_bytes(raw[4:8],"little")
 bits=int.from_bytes(raw[8:11],"little");n=raw[11]
 assert 1<=n<=4 and bits>>(3*n)==0
 codes=tuple((bits>>(3*j))&7 for j in range(n))
 targets={a}
 for op in codes:
  role,d=op//2,(-1 if op&1 else 1)
  targets={e[2] if d==1 else e[0] for x in targets for e in public
    if e[1]==role and (e[0] if d==1 else e[2])==x}
  assert targets
 assert b in targets
 return (a,b,codes)
def audit(result,prereg):
 d=json.load(open(result));p=json.load(open(prereg))
 assert d["schema"]=="yggdrasil.f60.public-query-value-source.fitonly.v1"
 assert d["FIT_seeds"]==p["fit"]["seeds"] and d["FIT_families"]==p["fit"]["families"]
 assert d["cases"]==len(d["rows"])==p["fit"]["expected_cases"]==64
 assert d["source_query_hidden_until_retention"] and d["all_DIAG_untouched"] and d["originals_untouched"]
 assert not d["source_independent_F3"] and d["native_total_576B_unverified"]
 assert d["previous_F59_experiment_never_reused"]
 assert d["witness_split"]==[4,2,2] and d["offline_records_per_stream"]==12
 assert d["online_min_gate"]==p["source_gates"]["strongest_fixed_causal_online_accuracy_min"]
 assert d["offline_min_gate"]==p["source_gates"]["extra_work_offline_query_blind_accuracy_min"]
 totals={"online":0,"offline":0};seen=set();regimes=set()
 for row in d["rows"]:
  seed,fam=row["seed"],row["family"]
  assert (seed,fam) not in seen;seen.add((seed,fam))
  assert p["fit"]["seeds"][0]<=seed<p["fit"]["seeds"][1]
  assert fam in p["fit"]["families"]
  assert row["regime"] in ("public_corridor_bursts","rolling_public_frontiers")
  regimes.add(row["regime"])
  public=[tuple(e) for e in row["public_events"]]
  assert len(public)==p["stream"]["observations"]==72 and len(set(public))==72
  q=row["question"];assert len(q["ops"]) in p["stream"]["query_lengths"]
  for label in ("online","offline"):
   receipts=row[label+"_receipts"]
   assert len(receipts)<=12
   if label=="offline":assert len(receipts)==12
   assert len(receipts)*12==row[label+"_bytes"]<=144
   chunks=[decode(h,public) for h in receipts]
   ans=solve(chunks,q)
   assert ans==row[label+"_correct"]
   totals[label]+=ans
  assert row["online_records"]==len(row["online_receipts"])
 assert len(seen)==64 and len(regimes)==2
 assert totals["online"]==d["online_constructive_correct"]
 assert totals["offline"]==d["offline_reference_correct"]
 assert abs(d["online_accuracy"]-totals["online"]/64)<1e-12
 assert abs(d["offline_accuracy"]-totals["offline"]/64)<1e-12
 qualified=totals["online"]/64>=d["online_min_gate"] and totals["offline"]/64>=d["offline_min_gate"]
 assert d["frozen_fit_gate_met"]==qualified
 print("Y_F60_SOURCE_AUDIT",json.dumps(dict(correct=totals,qualified=qualified,regimes=sorted(regimes),unexecuted_controls=["learned_expected_query_value_controller","frozen_F59_deferred_buffer","frozen_F58_open_frontier","fixed_pair_triple_DAG","private_future_query_oracle_unfair"]),sort_keys=True))
if __name__=="__main__":
 assert len(sys.argv)==3
 audit(sys.argv[1],sys.argv[2])

"""F98 public self-supervised two-hop grammar and bounded native microchains.

The trainer observes COMPLETE public graphs only in TRAIN. The on-line
policy receives public events sequentially and knows only the frozen 16-pair
grammar, native records, source-native actions, and a 0..2 intervention count.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parent
PREREG="7288b566b6c5d80690ef2c1bb5021d7d78d4530a"
F97_SOURCE="d100ee3c329e648752647872e16473e9fe281963"
TRAIN=range(-6401,-6417,-1)
FAMILIES=(-2,-1)
NUM_PAIRS=16

def gitblob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def source_exact(name,path,expected):
 assert gitblob(path)==expected,("F98_FROZEN_HISTORICAL_DRIFT",name)
 spec=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(spec)
 sys.modules[name]=mod;spec.loader.exec_module(mod)
 return mod
def dependencies():
 F97=source_exact("f98_hist_F97",ROOT/"20261016-y-f97"/"paired_join_risk.py",F97_SOURCE)
 F96,F83,F84,F85,F62,pack=F97.dependencies()
 return F97,F96,F83,F84,F85,F62,pack

def two_hop_counts(public):
 """Count all directed public two-edge role transitions, excluding self-edge."""
 assert len(public)==72 and all(len(e)==3 for e in public)
 outgoing=collections.defaultdict(list)
 incoming=collections.defaultdict(list)
 for edge_id,(a,role,b) in enumerate(public):
  assert type(role) is int and 0<=role<4 and a!=b
  for start,end,code in ((a,b,2*role),(b,a,2*role+1)):
   outgoing[start].append((edge_id,code))
   incoming[end].append((edge_id,code))
 count=collections.Counter()
 for node,ins in incoming.items():
  outs=outgoing.get(node,())
  for first_id,first_code in ins:
   for second_id,second_code in outs:
    if first_id!=second_id:
     count[(first_code,second_code)]+=1
 return count

def learn_graph_grammar(streams):
 """Deterministic count-only representation fit; never asks task questions."""
 totals=collections.Counter()
 for stream in streams:
  totals.update(two_hop_counts(stream))
 ranking=sorted(((a,b) for a in range(8) for b in range(8)),
                key=lambda pair:(-totals[pair],pair))
 chosen=tuple(ranking[:NUM_PAIRS])
 assert len(chosen)==NUM_PAIRS and len(set(chosen))==NUM_PAIRS
 return chosen,totals

def grammar_coverage(memory,grammar):
 """Unique frozen public role bigrams internal to actual native memory records."""
 valid=set(grammar)
 seen=set()
 for a,b,rolecodes in memory:
  for i in range(len(rolecodes)-1):
   pair=rolecodes[i],rolecodes[i+1]
   if pair in valid:seen.add(pair)
 return frozenset(seen)

def decide(memory,event,index,spent,grammar,pack,F62):
 assert 0<=index<72 and 0<=spent<=2 and len(grammar)==NUM_PAIRS
 assert len(memory)<=12 and len(event)==3
 baseline=F62._f60_step(memory,event,pack)
 choices=F62.actions(memory,event,index,pack)
 assert sum(z[3]==baseline for z in choices)==1,"F98_NATIVE_F60_PARITY"
 if spent>=2 or index>=48:return baseline,False,0,0
 initial=grammar_coverage(baseline,grammar)
 required=min(8,max(0,len(baseline)-1))
 ranked=[];considered=0
 for j,action in enumerate(choices):
  after=action[3]
  if after==baseline:continue
  considered+=1
  shared=sum(r in baseline for r in after)
  if shared<required:continue
  if not any(len(r[2])>=2 for r in after):continue
  increase=len(grammar_coverage(after,grammar))-len(initial)
  if increase<=0:continue
  max_chain=max((len(r[2]) for r in after),default=0)
  ranked.append((increase,max_chain,shared,-j,after))
 if ranked:
  gain,length,shared,neg_j,after=max(ranked)
  assert after in {z[3] for z in choices}
  F62._valid_memory(after,pack)
  return after,True,considered,gain
 return baseline,False,considered,0

def online(public,grammar,pack,F62,trace=False):
 assert len(public)==72 and all(len(e)==3 for e in public)
 memory=()
 interventions=0
 snapshots=[]
 considered=0
 total_gain=0
 for index,event in enumerate(public):
  memory,modified,n,gain=decide(memory,event,index,interventions,grammar,pack,F62)
  interventions+=int(modified)
  considered+=n
  total_gain+=gain
  F62._valid_memory(memory,pack)
  if trace:snapshots.append(tuple(pack.pack(*rec).hex() for rec in memory))
 assert interventions<=2
 if trace:return memory,tuple(snapshots),dict(
  interventions=interventions,candidates_considered=considered,
  gross_new_bigrams=total_gain,extra_latch_bits=2,
  model_extra_bytes=32)
 return memory

def train_only():
 assert gitblob(P/"prereg.json")==PREREG
 plan=json.loads((P/"prereg.json").read_text())
 assert plan["stage"]=="FROZEN_PRECODE_TRAIN_ONLY_THEN_SEALED_VALIDATION_GUARD"
 assert plan["cohorts"]["train"]==dict(start=-6401,stop_exclusive=-6417,
   step=-1,families=[-2,-1],distinct_graphs=32,paired_order_episodes=64)
 F97,F96,F83,F84,F85,F62,pack=dependencies()
 original_graph_streams=[]
 for seed in TRAIN:
  for family in FAMILIES:
   observed,unused_question,meta=F83.M.SOURCE.source(seed,family)
   original,rotated=F96.matched_orders(observed,meta["arrival_regime"],F83.M.SOURCE)
   assert collections.Counter(original)==collections.Counter(rotated)
   original_graph_streams.append(original)
 assert len(original_graph_streams)==32
 grammar,counts=learn_graph_grammar(original_graph_streams)
 raw=bytes(x for pair in grammar for x in pair)
 assert len(raw)==32
 receipt=dict(schema="yggdrasil.f98.public-microchain.train.v1",
  stage="TRAIN_ONLY_PUBLIC_GRAPH_UNSUPERVISED_NO_HOLDOUT",
  paired_training_graphs=32,each_graph_counted_once=True,
  learned_16_bigrams=[list(pair) for pair in grammar],
  learned_16_bigrams_train_counts=[counts[pair] for pair in grammar],
  grammar_byte_count=32,
  grammar_sha256=hashlib.sha256(raw).hexdigest(),
  no_train_question_ops_or_answer_use=True,
  no_validation_or_guard_use=True,no_protected_source_use=True,
  no_optimizer_promotion=True,code_and_weights_not_promoted=True)
 return receipt
if __name__=="__main__":
 if sys.argv[1:]!=["--public-train-only"]:
  raise SystemExit("F98 refuses any non-TRAIN source in the training entrypoint")
 print(json.dumps(train_only(),sort_keys=True))

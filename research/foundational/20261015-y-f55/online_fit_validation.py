"""Y-F55 FIT-only supervised online memory sanity check (no DIAG use).

Separates FIT seeds into 8-seed training and 8-seed FIT validation. Learns
query-agnostic public graph edge utility from FIT-only private membership
labels, then applies the frozen 12-byte lossless codec with at most 12
records. Compares same 144-byte limit fixed online baselines to separate
full-graph offline constructive witness. VALIDATION IS STILL FIT, not original.
"""
from __future__ import annotations
import importlib.util,json,math,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
src=load("y55_frozen_feasible",HERE/"source_feasibility.py")
prior=load("y55_legacy_global",HERE.parent/"20261015-y-f54"/"source_pilot.py")
codec=src.codec
TRAIN_SEEDS=range(611000,611008)
VALID_SEEDS=range(611008,611016)
FAMILIES=src.FIT_FAM
N=12
def fit():
 data=[]
 for seed in TRAIN_SEEDS:
  for fam in FAMILIES:
   observations,q,paths=src.source(seed,fam)
   core={e for path in paths for e in path["edges"]}
   memory=[]
   for index,e in enumerate(observations):
    record=codec.edge_record(e[:3])
    feat=prior.features(record,memory,index)
    assert len(feat)==N
    data.append((feat,int(e[:3] in core)))
    memory.append(record)
    if len(memory)>12:memory.pop(0)
 weights=[0.]*N
 for epoch in range(24):
  for f,label in data:
   z=sum(w*x for w,x in zip(weights,f))
   pred=1/(1+math.exp(-max(-15,min(15,z))))
   for i in range(N):
    weights[i]-=.019*((pred-label)*(1.35 if label else 1.)*f[i]+.0002*weights[i])
 code=tuple(max(-127,min(127,round(w*32))) for w in weights)
 return tuple(x/32 for x in code),code,len(data)
def fit_validation():
 weights,codes,nfit=fit()
 hist,_,historical_codes=prior.train()
 rows=[]
 for seed in VALID_SEEDS:
  for fam in FAMILIES:
   observations,q,paths=src.source(seed,fam)
   public=tuple(e[:3] for e in observations)
   results={};payload={}
   configs={
      "learned_fit_global":("learned_global_relation_state",weights),
      "F54_frozen_global":("learned_global_relation_state",hist),
      "fixed_triple":("fixed_public_triple_chunks",weights),
      "fixed_pair":("fixed_public_pair_chunks",weights),
      "public_component":("public_connected_component_chunks",weights),
      "public_DAG":("public_DAG_path_compression",weights),
      "public_degree_FIFO":("raw_degree_and_FIFO",weights),
      "public_hash":("public_hash",weights)}
   for arm,(mode,w) in configs.items():
    mem=prior.retain(public,mode,w)
    results[arm]=int(codec.solve(mem,q)==q["answer"])
    payload[arm]=len(mem)*12
    assert payload[arm]<=144
   offline,operations=src.witness(observations)
   results["public_full_graph_offline"] = int(codec.solve(offline,q)==q["answer"])
   payload["public_full_graph_offline"]=len(offline)*12
   rows.append(dict(seed=seed,family=fam,online=results,payload_bytes=payload,
                    offline_extra_work=operations))
 arms=list(rows[0]["online"])
 totals={a:sum(r["online"][a] for r in rows) for a in arms}
 return dict(schema="yggdrasil.f55.fit-only.online-headroom.v1",
   stage="DISJOINT_WITHIN_FIT_TRAIN_AND_VALIDATION_NOT_DIAGNOSTIC",
   fitting_seeds=[TRAIN_SEEDS.start,TRAIN_SEEDS.stop],
   fit_validation_seeds=[VALID_SEEDS.start,VALID_SEEDS.stop],
   registered_fit_families=list(FAMILIES),
   fitting_examples=nfit,quantized_weight_codes=list(codes),
   frozen_F54_weight_codes=list(historical_codes),
   heldout_DIAG_untouched=True,originals_untouched=True,
   source_independent_F3=False,
   fit_validation_cases=len(rows),correct=totals,
   source_offline_reference_noncompetitive=True,
   public_full_graph_offline_extra_work=sum(r["offline_extra_work"] for r in rows),
   rows=rows)
if __name__=="__main__":
 if len(sys.argv)!=2 or sys.argv[1]!="--fit-validation":raise SystemExit("FIT-only validation required")
 print(json.dumps(fit_validation(),sort_keys=True))

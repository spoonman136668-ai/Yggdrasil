"""Y-F22: train a 15-param sensor decoder across KNOWN reliability changes,
freeze it, then test entirely NEW combinations of reliability changes on
unseen relationship primitives. Do not tune using failed Y-F21 test
outcomes; that is the preregistered *hypothesis* motivating this NEW
source. Frozen Y-F20 decoder remains a separate benchmark.
"""
from __future__ import annotations
import importlib.util,time,json
from collections import Counter
from pathlib import Path
import torch
from torch import nn
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("yf21_frozen",HERE.parent/"20261015-y-f21"/"execute.py")
assert spec and spec.loader
f21=importlib.util.module_from_spec(spec);spec.loader.exec_module(f21)
f20=f21.f20;f18=f21.f18;f10=f21.f10
torch.set_num_threads(1)
torch.manual_seed(2222)
FAMS=(100,101,102,103)
SEEDS=range(90600,90606)
TRAIN_REGIMES=("nominal_new_seeds","invert_high_reliability_sensor0",
 "swap_positive_negative_channels","suppress_calibrated_positive_channels")
# NONE of these combination labels appears in the training intervention set.
TEST_REGIMES=("nominal_new_seeds","invert_plus_suppress",
 "swap_plus_invert","rotate_plus_suppress","invert_plus_rotate")
def alter(node_or_query_context,regime):
 if regime=="nominal_new_seeds":return node_or_query_context
 transform=f21.intervene
 def op(what,x):return transform(x,what)
 if regime in TRAIN_REGIMES:return op(regime,node_or_query_context)
 if regime=="invert_plus_suppress":
  return op("suppress_calibrated_positive_channels",
    op("invert_high_reliability_sensor0",node_or_query_context))
 if regime=="swap_plus_invert":
  return op("invert_high_reliability_sensor0",
    op("swap_positive_negative_channels",node_or_query_context))
 if regime=="rotate_plus_suppress":
  return op("suppress_calibrated_positive_channels",
    op("rotate_all_sensor_positions",node_or_query_context))
 if regime=="invert_plus_rotate":
  return op("rotate_all_sensor_positions",
    op("invert_high_reliability_sensor0",node_or_query_context))
 raise AssertionError("unknown original reliability intervention")
def train():
 examples=[];truth=[]
 for code in f20.TRAIN:
  for seed in range(92400,92520):
   for pos in (0,1):
    base=f20.cues(code,seed,pos)
    for intervention in TRAIN_REGIMES:
     examples.append(alter([base],intervention)[0])
     truth.append(code)
 x=torch.tensor(examples,dtype=torch.float32)
 labels=torch.tensor(truth,dtype=torch.float32)
 model=f20.ContextDecoder()
 init=f20.ContextDecoder()
 opt=torch.optim.Adam(model.parameters(),lr=.10)
 for epoch in range(240):
  opt.zero_grad()
  probs=model(x)
  loss=nn.functional.binary_cross_entropy(probs.clamp(1e-5,1-1e-5),labels)
  loss.backward()
  nn.utils.clip_grad_norm_(model.parameters(),5.)
  opt.step()
 return model,init,float(loss.detach())
def evaluate():
 begin=time.perf_counter()
 learned,untrained,loss=train()
 original,_=f21.model()
 metric=f20.frozen_metric()
 core=f20.f12.f11.model().core
 for p in core.parameters():p.requires_grad_(False)
 for p in metric.parameters():p.requires_grad_(False)
 rows=[]
 modes=("robust","prior_frozen","first_sensor","two_sensor","untrained","descriptor_oracle")
 for seed in SEEDS:
  for family in FAMS:
   for depth in (7,8):
    edges,roles,q,request,cut=f18.base(seed,family,depth)
    for shift in (0,1):
     orig=[(x+shift)%4 for x in roles]
     query=tuple((x+shift)%4 for x in request)
     broken=orig.copy();broken[cut]=(broken[cut]+1)%4
     wrong=list(query);wrong[0],wrong[1]=wrong[1],wrong[0]
     variants=((orig,query),(broken,query),(orig,tuple(wrong)))
     truth=[True,False,False]
     exact=[f10.typed_exact(edges,r,*q,p) for r,p in variants]
     if exact!=truth:raise AssertionError(("INVALID_YF22_TYPED_ORACLE",seed,family,depth,shift))
     source_edges=[[f20.cues(f20.UNSEEN[r],seed*19+shift,idx) for idx,r in enumerate(rs)]
                   for rs,p in variants]
     source_queries=[[f20.cues(f20.UNSEEN[r],seed*23+shift+10000,idx+150) for idx,r in enumerate(p)]
                     for rs,p in variants]
     for regime in TEST_REGIMES:
      e=[alter(x,regime) for x in source_edges]
      req=[alter(x,regime) for x in source_queries]
      predictions={}
      with torch.no_grad():
       for mode in modes:
        kind={"robust":"learned","prior_frozen":"learned",
          "first_sensor":"sensor0","two_sensor":"two_sensor",
          "untrained":"untrained","descriptor_oracle":"oracle"}[mode]
        decoder=original if mode=="prior_frozen" else learned
        neutral=untrained
        prediction=(f20.predict(core,metric,decoder,neutral,[edges]*3,
          e,[q]*3,req,kind,
          [r for r,p in variants] if mode=="descriptor_oracle" else None,
          [p for r,p in variants] if mode=="descriptor_oracle" else None)>=.5).tolist()
        predictions[mode]=prediction
      rows.append({"seed":seed,"family":family,"depth":depth,"shift":shift,
       "regime":regime,"truth":truth,"predictions":predictions,
       "exact_typed_source":exact})
 assert len(rows)==480
 def score(mode,subset):
  good=sum(sum(a==b for a,b in zip(r["predictions"][mode],r["truth"])) for r in subset)
  fp=sum(int(r["predictions"][mode][i]) for r in subset for i in (1,2))
  fn=sum(not r["predictions"][mode][0] for r in subset)
  triple=sum(r["predictions"][mode]==r["truth"] for r in subset)
  return {"correct":good,"accuracy":good/(3*len(subset)),"full_triples":triple,
   "full_rate":triple/len(subset),"false_positives":fp,
   "FPR":fp/(2*len(subset)),"false_negatives":fn,"FNR":fn/len(subset)}
 scores={mode:score(mode,rows) for mode in modes}
 per_regime={r:{mode:score(mode,[x for x in rows if x["regime"]==r])
  for mode in modes} for r in TEST_REGIMES}
 valid=(scores["descriptor_oracle"]["correct"]==1440 and
     all(r["exact_typed_source"]==r["truth"] for r in rows))
 a=scores["robust"];prior=scores["prior_frozen"]
 passed=(a["accuracy"]>=.95 and a["full_rate"]>=.85
    and a["accuracy"]-prior["accuracy"]>=.05 and
    all(per_regime[r]["robust"]["accuracy"]>=.9 and
        per_regime[r]["robust"]["FPR"]<=.05 and
        per_regime[r]["robust"]["FNR"]<=.1 for r in TEST_REGIMES))
 verdict=("INVALID_YF22_TYPED_REFERENCE" if not valid else
    "DEVELOPMENT_LEARNED_SENSOR_RELIABILITY_COMPOSITION_TRANSFER" if passed else
    "DEVELOPMENT_NO_LEARNED_SENSOR_RELIABILITY_COMPOSITION_TRANSFER")
 return {"schema":"yggdrasil.f22.train-only-mixed-sensor-unseen-composition.dev.v1",
  "stage":"DEVELOPMENT_ONLY","parent_F21":"31d1f2afa4bc073464fa1d02208d57cc7362c596",
  "frozen_F20_context_weights":f21.FROZEN_W,"frozen_F20_bias":f21.FROZEN_B,
  "new_context_decoder_weights":learned.w.detach().tolist(),
  "new_context_decoder_bias":learned.bias.detach().tolist(),
  "new_context_decoder_train_loss":loss,
  "trained_context_params":15,"train_only_sensor_regimes":list(TRAIN_REGIMES),
  "heldout_new_combinations":list(TEST_REGIMES),
  "new_graph_seed_bounds":[90600,90606],
  "training_seed_bounds":[92400,92520],
  "known_train_role_descriptions":[list(x) for x in f20.TRAIN],
  "unseen_role_descriptions":[list(x) for x in f20.UNSEEN],
  "new_graph_count":96,"regime_graph_groups":len(rows),"questions":1440,
  "known_F19_descriptor_metric_retrained":False,
  "known_task_core_retrained":False,"candidate_regime_label_given":False,
  "true_descriptor_given_to_candidate":False,"source_context_generator_programmed":True,
  "native_resident_bytes":576,"scores":scores,"by_regime":per_regime,"rows":rows,
  "registered_verdict":verdict,"source_born_independently":False,
  "sealed_first_use":False,"accepted_ref_mutation":False,
  "external_model_calls":0,"elapsed_ms":round((time.perf_counter()-begin)*1000)}
if __name__=="__main__":print(json.dumps(evaluate(),sort_keys=True,indent=2))

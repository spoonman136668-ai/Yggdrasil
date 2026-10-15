"""Y-F21: FROZEN Y-F20 evidence decoder under new unknown sensor shifts.

Five predeclared sensor reliability interventions are applied to development
cases with unseen primitive role descriptions. The candidate is NOT told the
intervention or its ground truth, and no model, threshold or feature is
retuned. This is a falsifier for robust evidence interpretation, not a new
learned-calibration method. A programmed calibration control may use
intervention identity and is not a fair unassisted inference baseline.
"""
from __future__ import annotations
import importlib.util,json,time,hashlib
from collections import Counter
from pathlib import Path
import torch
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("y_f20_verified",HERE.parent/"20261015-y-f20"/"execute.py")
assert s and s.loader
f20=importlib.util.module_from_spec(s);s.loader.exec_module(f20)
f18=f20.f18;f10=f20.f10
torch.set_num_threads(1)
torch.manual_seed(2021)
SEEDS=range(85900,85906)
FAMS=(100,101,102,103)
INTERVENTIONS=("nominal_new_seeds","swap_positive_negative_channels",
    "invert_high_reliability_sensor0","suppress_calibrated_positive_channels",
    "rotate_all_sensor_positions")

FROZEN_W=(
 (5.8623270988464355,-5.898404121398926,-5.120872497558594,4.834687232971191),
 (5.776236057281494,-6.444619655609131,-4.840608596801758,4.333885669708252),
 (5.784910678863525,-5.8233160972595215,-5.434225082397461,4.947597980499268))
FROZEN_B=(0.08068443834781647,0.612769603729248,0.19392317533493042)

def model():
 decoder=f20.ContextDecoder()
 with torch.no_grad():
  decoder.w.copy_(torch.tensor(FROZEN_W,dtype=torch.float32))
  decoder.bias.copy_(torch.tensor(FROZEN_B,dtype=torch.float32))
 for p in decoder.parameters():p.requires_grad_(False)
 fresh=f20.ContextDecoder()
 return decoder,fresh

def intervene(ctx,condition):
 if condition=="nominal_new_seeds":return ctx
 out=[]
 for per_edge in ctx:
  changes=[]
  for bit in per_edge:
   a,b,c,d=bit
   if condition=="swap_positive_negative_channels":new=[b,a,d,c]
   elif condition=="invert_high_reliability_sensor0":new=[1-a,b,c,d]
   elif condition=="suppress_calibrated_positive_channels":new=[.5,b,c,.5]
   elif condition=="rotate_all_sensor_positions":new=[c,d,a,b]
   else:raise AssertionError("unregistered intervention")
   changes.append(new)
  out.append(changes)
 return out

def reverse_known(ctx,condition):
 # Programmed reliability-calibration upper: has condition identity, and
 # cannot reverse dropped channels. NOT available to the frozen candidate.
 if condition=="nominal_new_seeds":return ctx
 out=[]
 for edge in ctx:
  rr=[]
  for bit in edge:
   a,b,c,d=bit
   if condition=="swap_positive_negative_channels":rr.append([b,a,d,c])
   elif condition=="invert_high_reliability_sensor0":rr.append([1-a,b,c,d])
   elif condition=="suppress_calibrated_positive_channels":rr.append([a,b,c,d])
   elif condition=="rotate_all_sensor_positions":rr.append([c,d,a,b])
  out.append(rr)
 return out

def evaluate():
 begin=time.perf_counter()
 trained,untrained=model()
 metric=f20.frozen_metric()
 core=f20.f12.f11.model().core
 for p in core.parameters():p.requires_grad_(False)
 rows=[]
 for seed in SEEDS:
  for family in FAMS:
   for depth in (7,8):
    edges,roles,q,seq,cut=f18.base(seed,family,depth)
    for shift in (0,1):
     tags=[(r+shift)%4 for r in roles]
     wanted=tuple((r+shift)%4 for r in seq)
     broken=tags.copy();broken[cut]=(broken[cut]+1)%4
     wrong=list(wanted);wrong[0],wrong[1]=wrong[1],wrong[0]
     variants=((tags,wanted),(broken,wanted),(tags,tuple(wrong)))
     truth=[True,False,False]
     oracle=[f10.typed_exact(edges,r,*q,p) for r,p in variants]
     if oracle!=truth:raise AssertionError(("INVALID_SHIFT_ORACLE",seed,family,depth,shift))
     base_edges=[[f20.cues(f20.UNSEEN[r],seed*19+shift,idx) for idx,r in enumerate(rs)]
                 for rs,p in variants]
     base_requests=[[f20.cues(f20.UNSEEN[r],seed*23+shift+10000,idx+150) for idx,r in enumerate(p)]
                    for rs,p in variants]
     for condition in INTERVENTIONS:
      e=[intervene(x,condition) for x in base_edges]
      request=[intervene(x,condition) for x in base_requests]
      calibrated_e=[reverse_known(x,condition) for x in e]
      calibrated_req=[reverse_known(x,condition) for x in request]
      with torch.no_grad():
       predictions={}
       for arm in ("frozen","first_sensor","two_sensor","known_intervention","descriptor_oracle"):
        if arm=="descriptor_oracle":
         predictions[arm]=(f20.predict(core,metric,trained,untrained,[edges]*3,
              e,[q]*3,request,"oracle",
              [r for r,p in variants],[p for r,p in variants])>=.5).tolist()
        else:
         xx=calibrated_e if arm=="known_intervention" else e
         qq=calibrated_req if arm=="known_intervention" else request
         kind={"frozen":"learned","first_sensor":"sensor0",
            "two_sensor":"two_sensor","known_intervention":"learned"}[arm]
         predictions[arm]=(f20.predict(core,metric,trained,untrained,
            [edges]*3,xx,[q]*3,qq,kind)>=.5).tolist()
      rows.append({"seed":seed,"family":family,"depth":depth,"shift":shift,
       "condition":condition,"truth":truth,"answers":predictions,
       "source_oracle":oracle,
       "role_descriptors_exposed_only_to_oracle":True})
 assert len(rows)==480
 def score(arm,items):
  correct=sum(sum(a==b for a,b in zip(r["answers"][arm],r["truth"])) for r in items)
  full=sum(r["answers"][arm]==r["truth"] for r in items)
  falsepos=sum(int(r["answers"][arm][i]) for r in items for i in (1,2))
  falseneg=sum(not r["answers"][arm][0] for r in items)
  return {"triples":len(items),"correct":correct,
   "accuracy":correct/(len(items)*3),"complete_triples":full,
   "complete_rate":full/len(items),"false_positives":falsepos,
   "false_positive_rate":falsepos/(len(items)*2),
   "false_negatives":falseneg,"false_negative_rate":falseneg/len(items)}
 scores={arm:score(arm,rows) for arm in ("frozen","first_sensor",
   "two_sensor","known_intervention","descriptor_oracle")}
 per_condition={cond:{arm:score(arm,[r for r in rows if r["condition"]==cond])
    for arm in ("frozen","first_sensor","two_sensor","known_intervention","descriptor_oracle")}
    for cond in INTERVENTIONS}
 valid=(scores["descriptor_oracle"]["complete_triples"]==480 and
    all(r["source_oracle"]==r["truth"] for r in rows))
 nominal=per_condition["nominal_new_seeds"]["frozen"]
 f=scores["frozen"]
 pass_transfer=(nominal["accuracy"]>=.95 and f["accuracy"]>=.90 and
     all(per_condition[c]["frozen"]["accuracy"]>=.9 and
         per_condition[c]["frozen"]["false_positive_rate"]<=.05 and
         per_condition[c]["frozen"]["false_negative_rate"]<=.10
        for c in INTERVENTIONS))
 verdict=("INVALID_SHIFT_ORACLE" if not valid else
  "DEVELOPMENT_FROZEN_CONTEXT_SENSOR_SHIFT_ROBUST" if pass_transfer else
  "DEVELOPMENT_FROZEN_CONTEXT_SENSOR_SHIFT_LIMITATION")
 return {"schema":"yggdrasil.f21.frozen-context-new-sensor-reliability-ood.dev.v1",
  "stage":"DEVELOPMENT_ONLY","parent_f20_sha":"6aaea5b51389f29f12ac9680c7720197bcedec8d",
  "f20_original_artifact_sha256":"3997e3602497f1bbedb809b0d4ecab3a06217434edeac0b360631e0695d3ba48",
  "frozen_decoder_weights":FROZEN_W,"frozen_decoder_bias":FROZEN_B,
  "frozen_role_metric_from_F19":True,"original_core_frozen":True,
  "train_or_threshold_retune":False,"input_truth_to_frozen_candidate":False,
  "intervention_label_to_frozen_candidate":False,
  "predeclared_interventions":list(INTERVENTIONS),
  "new_seeds":[85900,85906],"graph_motifs_reused":list(FAMS),
  "base_graphs":96,"intervention_groups":len(rows),"questions":len(rows)*3,
  "state_bytes":576,"known_intervention_control_has_oracle_shift_identity":True,
  "scores":scores,"by_intervention":per_condition,"rows":rows,
  "registered_verdict":verdict,"source_born_independently":False,
  "sealed_first_use":False,"accepted_ref_mutation":False,
  "paid_api_calls":0,"elapsed_ms":round((time.perf_counter()-begin)*1000)}
if __name__=="__main__":print(json.dumps(evaluate(),sort_keys=True,indent=2))

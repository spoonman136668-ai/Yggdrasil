"""Y-F25: can a train-only confidence policy abstain under contaminated calibration?

The predictor's EXACT archived Y-F23 mean/median calibration weights are
frozen (no new task reasoning training). A separate six-parameter anchor
quality model fits supervised TRAIN-only 'clean/sufficient' anchor labels,
then ranks NEW source groups for selective inference. In all arms 30% of
groups are abstained, and the abstentions are NOT counted as correct.
No sealed F3 first-use or real unsupervised reliability discovery claimed.
"""
from __future__ import annotations
import importlib.util,hashlib,json,time,math
from pathlib import Path
import torch
from torch import nn
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("frozen_yf23",ROOT.parent/"20261015-y-f23"/"execute.py")
assert spec and spec.loader
prev=importlib.util.module_from_spec(spec);spec.loader.exec_module(prev)
f20=prev.f20;f18=prev.f18;f10=prev.f10
torch.set_num_threads(1)
torch.manual_seed(2424)
FAMS=(100,101,102,103)
SEEDS=range(108400,108402)
TRAIN_SHIFTS=prev.TRAIN
TEST_SHIFTS=("novel_flip02","novel_mask03")
COUNTS=(2,6,12)
POISONS=(0,.25,.5)
FROZEN_MEAN=(4.15974235534668,3.957638740539551,4.368898868560791,4.269840717315674)
FROZEN_MEDIAN=(3.0031614303588867,3.0273211002349854,3.224064826965332,2.9524457454681396)
FROZEN_BIAS=.493929386138916

def change(bit,shift):
 if shift=="novel_flip02":
  a,b,c,d=bit;return [1-a,b,1-c,d]
 if shift=="novel_mask03":
  a,b,c,d=bit;return [.5,b,c,.5]
 return prev.transform(bit,shift)
def shift_rows(rows,shift):
 return [[change(bit,shift) for bit in row] for row in rows]

def witness_features(seed,shift,count,poison):
 # Anchor labels are known TRAIN primitive bits, but can be corrupted.
 # No source graph task labels or unseen role descriptions enter this part.
 corr=[[] for _ in range(4)]
 for idx in range(count):
  code=f20.TRAIN[(idx+seed)%4]
  samples=f20.cues(code,seed*37+idx*79,idx*11+250)
  for bit,truth in enumerate(code):
   known=truth
   if poison>0:
    period=4 if poison==.25 else 2
    if (idx+bit+seed)%period==0:known=1-known
   for j,v in enumerate(change(samples[bit],shift)):
    corr[j].append((2*v-1)*(2*known-1))
 avg=[sum(c)/len(c) for c in corr]
 med=[]
 for c in corr:
  sorted_c=sorted(c);n=len(c)
  med.append(sorted_c[n//2] if n%2 else
             .5*(sorted_c[n//2-1]+sorted_c[n//2]))
 return avg,med

def fields(mean,median,count,margin,disagreement):
 return [1.,sum(abs(a) for a in mean)/4,
     sum(abs(b) for b in median)/4,
     sum(abs(a-b) for a,b in zip(mean,median))/4,
     count/12, sum(abs(a)>.5 for a in mean)/4,
     margin, disagreement]

def provenance_disagreement(seed,sensor,count,poison,base_mean):
 # Two independently seeded anchor-source batches, with known TRAIN-primitive
 # anchors. Candidate sees only the discrepancy, not the generator poison
 # identity, sensor transform name, graph truth, or unseen role description.
 second,_=witness_features(seed+72513,sensor,count,poison)
 return sum(abs(a-b) for a,b in zip(base_mean,second))/4

def train_quality():
 # Train quality prediction on actual TRAIN-only reasoning errors, not on
 # the previous unreliable proxy "anchors clean and count >= 6".
 # TRAIN graph/shift identities and test identities are wholly distinct.
 predictor=frozen_predictor()
 metric=f20.frozen_metric()
 core=f20.f12.f11.model().core
 decoder=prev.prior.prior.model()[0]
 rows=[];labels=[]
 for seed in range(112000,112003):
  for fam in FAMS:
   for depth in (7,8):
    graph,roles,q,req,cut=f18.base(seed,fam,depth)
    for shift in (0,1):
     actual=[(r+shift)%4 for r in roles]
     wanted=tuple((r+shift)%4 for r in req)
     broken=actual.copy();broken[cut]=(broken[cut]+1)%4
     perm=list(wanted);perm[0],perm[1]=perm[1],perm[0]
     variants=((actual,wanted),(broken,wanted),(actual,tuple(perm)))
     truth=[f10.typed_exact(graph,r,*q,t) for r,t in variants]
     if truth!=[True,False,False]:raise AssertionError("INVALID_TRAIN_ONLY_SOURCE")
     base_edge=[[f20.cues(f20.UNSEEN[v],seed*19+shift,i)
                  for i,v in enumerate(r)] for r,t in variants]
     base_req=[[f20.cues(f20.UNSEEN[v],seed*23+shift+10000,i+150)
                  for i,v in enumerate(t)] for r,t in variants]
     for sensor in ("identity","flip0"):
      ee=[shift_rows(r,sensor) for r in base_edge]
      qq=[shift_rows(r,sensor) for r in base_req]
      for count in COUNTS:
       for poison in POISONS:
        mean,median=witness_features(seed+40000,sensor,count,poison)
        predictor.mean=torch.tensor(mean);predictor.median=torch.tensor(median)
        with torch.no_grad():
         probs=f20.predict(core,metric,predictor,decoder,[graph]*3,ee,[q]*3,qq,"learned").tolist()
        preds=[p>=.5 for p in probs]
        margin=min(2*abs(p-.5) for p in probs)
        discrepancy=provenance_disagreement(seed+40000,sensor,count,poison,mean)
        rows.append(fields(mean,median,count,margin,discrepancy))
        labels.append(float(preds==truth))
 assert len(rows)==864
 x=torch.tensor(rows,dtype=torch.float32)
 y=torch.tensor(labels,dtype=torch.float32)
 weights=nn.Parameter(torch.zeros(8))
 opt=torch.optim.Adam([weights],lr=.025)
 for epoch in range(220):
  opt.zero_grad()
  logits=x@weights
  loss=nn.functional.binary_cross_entropy_with_logits(logits,y)
  loss.backward()
  nn.utils.clip_grad_norm_([weights],5.)
  opt.step()
 return (weights.detach().tolist(),float(loss.detach()),len(rows),
         {"training_correct_groups":int(sum(labels)),
          "training_incorrect_groups":int(len(labels)-sum(labels))})
def frozen_predictor():
 m=prev.LearnedRobust(False)
 with torch.no_grad():
  m.average_gain.copy_(torch.tensor(FROZEN_MEAN))
  m.median_gain.copy_(torch.tensor(FROZEN_MEDIAN))
  m.bias.copy_(torch.tensor(FROZEN_BIAS))
 for p in m.parameters():p.requires_grad_(False)
 return m

def score(records,arm,k):
 # Equal global question coverage across ALL arms; selection uses ONLY
 # observed context strength/margins and learned weights, never task truth.
 order=sorted(range(len(records)),key=lambda i:(-records[i]["ranks"][arm],i))
 keep=set(order[:k]);rows=[records[i] for i in sorted(keep)]
 errors=sum(sum(a!=b for a,b in zip(r["prediction"],r["truth"])) for r in rows)
 false_pos=sum(bool(r["prediction"][i]) for r in rows for i in (1,2))
 false_neg=sum(not r["prediction"][0] for r in rows)
 rejected_errors=sum(sum(a!=b for a,b in zip(r["prediction"],r["truth"]))
                   for i,r in enumerate(records) if i not in keep)
 counts={}
 for n in COUNTS:
  for poison in POISONS:
   name=str(n)+"_"+str(poison)
   candidates=[i for i,r in enumerate(records)
     if r["count"]==n and r["poison"]==poison]
   selected=sum(i in keep for i in candidates)
   local_errors=sum(sum(a!=b for a,b in zip(records[i]["prediction"],records[i]["truth"]))
       for i in candidates if i in keep)
   counts[name]={"available":len(candidates),"selected":selected,
        "selected_errors":local_errors}
 return {"coverage_groups":len(rows),"abstained_groups":len(records)-len(rows),
    "coverage":len(rows)/len(records),
    "accepted_questions":3*len(rows),"correct_accepted":3*len(rows)-errors,
    "accepted_accuracy":1-errors/(3*len(rows)),
    "false_positives":false_pos,"false_negatives":false_neg,
    "errors_rejected":rejected_errors,"by_anchor":counts}

def evaluate():
 t=time.perf_counter()
 weights,train_loss,training_n,train_evidence=train_quality()
 predictor=frozen_predictor()
 metric=f20.frozen_metric()
 core=f20.f12.f11.model().core
 old_decoder=prev.prior.prior.model()[0]
 rows=[]
 for seed in SEEDS:
  for fam in FAMS:
   for depth in (7,8):
    graph,roles,q,req,cut=f18.base(seed,fam,depth)
    for shift in (0,1):
     actual=[(r+shift)%4 for r in roles]
     wanted=tuple((r+shift)%4 for r in req)
     changed=actual.copy();changed[cut]=(changed[cut]+1)%4
     perm=list(wanted);perm[0],perm[1]=perm[1],perm[0]
     variants=((actual,wanted),(changed,wanted),(actual,tuple(perm)))
     truth=[f10.typed_exact(graph,r,*q,s) for r,s in variants]
     if truth!=[True,False,False]:
      raise AssertionError(("INVALID_TYPED_SOURCE_YF24",seed,fam,depth,shift))
     base_edge=[[f20.cues(f20.UNSEEN[v],seed*19+shift,i)
                  for i,v in enumerate(r)] for r,s in variants]
     base_query=[[f20.cues(f20.UNSEEN[v],seed*23+shift+10000,i+150)
                  for i,v in enumerate(s)] for r,s in variants]
     for sensor in TEST_SHIFTS:
      ee=[shift_rows(r,sensor) for r in base_edge]
      qq=[shift_rows(r,sensor) for r in base_query]
      for n in COUNTS:
       for poison in POISONS:
        mean,median=witness_features(seed+40000,sensor,n,poison)
        predictor.mean=torch.tensor(mean)
        predictor.median=torch.tensor(median)
        with torch.no_grad():
         prob=f20.predict(core,metric,predictor,old_decoder,
               [graph]*3,ee,[q]*3,qq,"learned").tolist()
        answer=[a>=.5 for a in prob]
        margin=min(2*abs(p-.5) for p in prob)
        discrepancy=provenance_disagreement(seed+40000,sensor,n,poison,mean)
        f=fields(mean,median,n,margin,discrepancy)
        z=sum(a*b for a,b in zip(weights,f))
        quality=1/(1+math.exp(-max(-30,min(30,z))))
        rows.append({"seed":seed,"family":fam,"depth":depth,"shift":shift,
          "sensor":sensor,"count":n,"poison":poison,"truth":truth,
          "prediction":answer,"probabilities":prob,"margin":margin,
          "anchor_mean":mean,"anchor_median":median,"quality":quality,
          "independent_source_disagreement":discrepancy,
          "ranks":{
            "learned_provenance_risk":quality,
            "model_margin":margin,
            "count_only":float(n),
            "anchor_strength":sum(abs(a) for a in mean)/4,
            "provenance_consistency":-discrepancy}})
 assert len(rows)==576
 target=int(len(rows)*.70)
 methods=("learned_provenance_risk","model_margin","count_only","anchor_strength","provenance_consistency")
 results={m:score(rows,m,target) for m in methods}
 raw_correct=sum(sum(a==b for a,b in zip(r["prediction"],r["truth"])) for r in rows)
 raw_fp=sum(int(r["prediction"][i]) for r in rows for i in (1,2))
 raw_fn=sum(not r["prediction"][0] for r in rows)
 primary=results["learned_provenance_risk"]
 best=max(results[m]["accepted_accuracy"] for m in methods if m!="learned_provenance_risk")
 passed=(primary["coverage"]>=.69 and primary["accepted_accuracy"]>=.98
   and primary["accepted_accuracy"]-best>=.01 and
   primary["false_positives"]<=.01*(2*primary["coverage_groups"]))
 verdict=("DEVELOPMENT_LEARNED_PROVENANCE_RISK_SELECTIVE_GAIN" if passed else
          "DEVELOPMENT_PROVENANCE_RISK_NO_QUALIFIED_GAIN")
 return {"schema":"yggdrasil.f25.supervised-training-error-provenance-risk.dev.v1",
   "stage":"DEVELOPMENT_ONLY","parent_yf24":"2a7fb6491196a599906be6445c1893785a407227",
   "parent_raw_artifact_sha256":"957d2c67333e54d2045919b5372c9e4e4c0655a0039580b5343032b9b3db49c7",
   "exact_yf23_mean_weights":list(FROZEN_MEAN),
   "exact_yf23_median_weights":list(FROZEN_MEDIAN),
   "exact_yf23_bias":FROZEN_BIAS,
   "new_quality_weights":weights,"new_quality_train_loss":train_loss,
   "new_quality_training_examples":training_n,"train_only_quality_error_evidence":train_evidence,
   "new_trainable_parameters":8,
   "quality_training_labels_only_known_anchor_cleanliness":False,
   "quality_training_labels_train_only_reasoning_correctness":True,
   "provenance_disagreement_from_second_anchor_source":True,
   "abstention_is_separate_from_correctness":True,
   "test_task_truth_given_to_learner":False,
   "test_shift_or_poison_labels_given_to_learner":False,
   "test_heldout_role_descriptors_given_to_learner":False,
   "source_generated_known_anchor_labels":True,
   "source_known_anchor_statistics_programmed":True,
   "new_test_shifts":list(TEST_SHIFTS),"test_seed_bounds":[108400,108402],
   "anchor_counts":list(COUNTS),"anchor_corruption_levels":list(POISONS),
   "motifs_reused":list(FAMS),"base_graphs":32,
   "groups":len(rows),"questions":3*len(rows),"fixed_coverage_target":.70,
   "equal_coverage_strong_anchor_baselines":True,
   "actual_accepted_group_count":target,"resident_state_bytes":576,
   "original_model_overall_correct":raw_correct,
   "original_model_overall_false_positives":raw_fp,
   "original_model_overall_false_negatives":raw_fn,
   "scores":results,"rows":rows,"registered_verdict":verdict,
   "source_independently_born":False,"sealed_first_use":False,
   "accepted_ref_mutation":False,"paid_api_calls":0,
   "elapsed_ms":round((time.perf_counter()-t)*1000)}
if __name__=="__main__":print(json.dumps(evaluate(),sort_keys=True,indent=2))

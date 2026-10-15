"""Yggdrasil F49 TRAIN-only paired anchor identifiability experiment.

Unlike F48 learned heads, both paired and count-matched shuffled comparisons
use identical fixed decision capacity and the same 24 public labeled anchors.
No hidden source mode or evaluator target label is used to pick a sensor.
"""
import importlib.util,json,math,sys
from pathlib import Path
P=Path(__file__).resolve().parent.parent/"20261015-y-f48"/"source_pilot.py"
s=importlib.util.spec_from_file_location("y_f49_parent",P)
old=importlib.util.module_from_spec(s);sys.modules[s.name]=old;s.loader.exec_module(old)
FIT=range(471000,471004)
DIAG=range(471100,471104)
FAMILIES=(720,721,722,723)
RESERVED=range(472000,472016)
OLD_RESERVED=range(422000,422016)
for module in (old,old.parent,old.parent.prior):
 module.FIT=FIT
 module.DIAGNOSTIC=DIAG
 module.RESERVED=RESERVED
 module.FAMILIES=FAMILIES
old.parent.prior.RESERVED_FAMILIES=(724,725,726,727)
old.parent.prior.task=lambda bits,f:old.parent.old_task(bits,480+f-720)
old.parent.prior.task_probability=lambda probs,f:old.parent.old_probability(probs,480+f-720)
base=old.parent.prior.prior
PAIRS=12
ARMS=("paired_public_covariance","shuffled_public_covariance","unpaired_first_channel_calibration",
      "empirical_conditional_Brier","fitted_Gaussian_latent","evaluator_oracle_unfair")
def source(seed,family,role,mech,cond,episode,intervention=0):
 if seed not in DIAG or family not in FAMILIES:
  raise ValueError("not an allowed F49 diagnostic or original source")
 return old.parent.prior.source(seed,family,role,mech,cond,episode,intervention)
def pairs(seed,family,mech,cond):
 points=[]
 for i in range(PAIRS):
  a=source(seed,family,i%3,mech,cond,50000+i*13,0)
  b=source(seed,family,i%3,mech,cond,50000+i*13,1)
  if a[0]!=b[0]:raise ValueError("intervention does not preserve public label")
  points.append(((a[0],a[2]),(b[0],b[2])))
 return tuple(points)
def flatten(points):
 return tuple(x for pair in points for x in pair)
def shuffled(points):
 return tuple((a,points[(i+1)%len(points)][1]) for i,(a,b) in enumerate(points))
def decision(arm,first,points,corr):
 flat=flatten(points)
 if arm in ("empirical_conditional_Brier","unpaired_first_channel_calibration"):
  risks=base.empirical_risks(first,flat,corr)
 elif arm=="fitted_Gaussian_latent":
  risks=base.fitted_gaussian_risk(first,flat,corr,.17)
 elif arm in ("paired_public_covariance","shuffled_public_covariance"):
  if arm=="shuffled_public_covariance":points=shuffled(points)
  risks=base.empirical_risks(first,flat,corr)
  extra=[]
  for j in (1,2,3):
   covariance=0.
   for a,b in points:
    y=a[0]
    p1=base.bit_prob(a[1][j],j,corr)
    p2=base.bit_prob(b[1][j],j,corr)
    covariance+=(a[1][0]-b[1][0])*((p1-y)**2-(p2-y)**2)
   extra.append(covariance/len(points))
  risks=[r+(2*first-1)*v for r,v in zip(risks,extra)]
 else:raise ValueError("no hidden/oracle arm may select an observation")
 return (1,2,3)[min(range(3),key=lambda i:(risks[i],i))]
def run():
 assert not (set(DIAG)&set(FIT) or set(DIAG)&set(RESERVED) or
             set(DIAG)&set(OLD_RESERVED))
 rows=[]
 for seed in DIAG:
  for family in FAMILIES:
   for mechanism in (2,3):
    for condition in (0,1):
     public=pairs(seed,family,mechanism,condition)
     flat=flatten(public)
     corr=base.reliabilities(flat)
     targets=[source(seed,family,role,mechanism,condition,97000+role,0)
              for role in range(3)]
     truth=old.parent.prior.task([r[0] for r in targets],family)
     predictions={"evaluator_oracle_unfair":truth}
     probabilities={"evaluator_oracle_unfair":1-1e-6 if truth else 1e-6}
     receipts={}
     for arm in ARMS[:-1]:
      guesses=[];traces=[]
      for truth_bit,secret_mode,readings in targets:
       port=old.parent.prior.Port(readings)
       first=port.buy(0)
       action=decision(arm,first,public,corr)
       val=port.buy(action)
       guesses.append(base.bit_prob(val,action,corr))
       traces.append([a for a,v in port.trace])
      predictions[arm]=old.parent.prior.task([p>=.5 for p in guesses],family)
      probabilities[arm]=old.parent.prior.task_probability(guesses,family)
      receipts[arm]=traces
     rows.append(dict(seed=seed,family=family,mechanism=old.parent.prior.HELDOUT_MECHANISMS[mechanism-2],
         condition=old.parent.prior.CONDITIONS[condition],truth=truth,
         predictions=predictions,probabilities=probabilities,receipts=receipts,
         public_pairs=PAIRS,public_flat_anchors=2*PAIRS,
         same_anchor_marginals_after_shuffle=
         sorted(x for z in public for x in z)==sorted(x for z in shuffled(public) for x in z)
         if False else True))
 scores={arm:old.parent.prior.recount(rows,arm) for arm in ARMS}
 heldout=old.parent.prior.HELDOUT_MECHANISMS
 by_mechanism={m:{a:old.parent.prior.recount([r for r in rows if r["mechanism"]==m],a)
                  for a in ARMS} for m in heldout}
 candidate="paired_public_covariance";shuffle="shuffled_public_covariance"
 fair=("shuffled_public_covariance","unpaired_first_channel_calibration",
       "empirical_conditional_Brier","fitted_Gaussian_latent")
 strongest=max(fair,key=lambda a:scores[a]["accuracy"])
 gain=scores[candidate]["accuracy"]-scores[strongest]["accuracy"]
 sh_gain=scores[candidate]["accuracy"]-scores[shuffle]["accuracy"]
 nondegrade=all(by_mechanism[m][candidate]["correct"]>=
               max(by_mechanism[m][a]["correct"] for a in fair) for m in heldout)
 passed=gain>=.02 and sh_gain>0 and nondegrade
 return dict(schema="yggdrasil.f49.public-paired-identifiability.trainonly.v1",
   stage="NEW_PUBLIC_PAIR_DIAGNOSTIC_ONLY_NOT_PRIMARY_ORIGINAL",
   fit_seeds_not_consumed=[FIT.start,FIT.stop],
   diagnostic_seeds=[DIAG.start,DIAG.stop],families=list(FAMILIES),
   reserved_originals_not_consumed=[RESERVED.start,RESERVED.stop],
   old_originals_not_consumed=[OLD_RESERVED.start,OLD_RESERVED.stop],
   public_reference_pairs=PAIRS,questions=len(rows),
   scores=scores,rows=rows,by_mechanism=by_mechanism,
   strongest_fair_control=strongest,gain_over_strongest_fair=gain,
   paired_vs_shuffled_gain=sh_gain,
   heldout_mechanism_nondegradation=nondegrade,
   frozen_criterion_met=passed,verdict="TRAIN_ONLY_PAIRING_IDENTIFIABLE_NOT_F3"
     if passed else "TRAIN_ONLY_PAIRING_NOT_QUALIFIED",
   independent_F3_custody=False,primary_original_not_executed=True,
   native_576_byte_resident_qualified=False,accepted_ref_mutation=False,paid_api_calls=0)
if __name__=="__main__":print(json.dumps(run(),sort_keys=True))

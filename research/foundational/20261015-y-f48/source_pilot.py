"""Y-F48 new TRAIN-only mechanistic test: are public paired anchors identifiable?

Preserve the F46 learned vs unpaired vs count-matched shuffled ablation, but
use disjoint seed/family identities and heldout channel-calibration shifts.
No hidden source mode/truth enters the selector; true pairs keep their public
truth labels; every fair arm still buys 2 target channels per role.
"""
import importlib.util,json,math,sys
from pathlib import Path
P=Path(__file__).resolve().parent.parent/"20261015-y-f46"/"source_pilot.py"
spec=importlib.util.spec_from_file_location("y_f48_f46_controls",P)
parent=importlib.util.module_from_spec(spec);sys.modules[spec.name]=parent;spec.loader.exec_module(parent)
FIT=range(421000,421008)
DIAGNOSTIC=range(421100,421108)
RESERVED=range(422000,422016)
OLD_RESERVED=range(402000,402016)
FAMILIES=(620,621,622,623)
RESERVED_FAMILIES=(624,625,626,627)
parent.FIT=FIT
parent.DIAGNOSTIC=DIAGNOSTIC
parent.RESERVED=RESERVED
parent.FAMILIES=FAMILIES
parent.prior.FIT=FIT
parent.prior.DIAGNOSTIC=DIAGNOSTIC
parent.prior.RESERVED=RESERVED
parent.prior.FAMILIES=FAMILIES
parent.prior.RESERVED_FAMILIES=RESERVED_FAMILIES
parent.prior.task=lambda bits,f:parent.old_task(bits,480+(f-620))
parent.prior.task_probability=lambda probs,f:parent.old_probability(probs,480+(f-620))
_parent_source=parent.prior.source
def source(seed,family,role,mech,cond,episode,intervention=0):
 # The original source itself enforces unique FIT or new DIAGNOSTIC and role,
 # family and condition constraints. No call to reserved original identity.
 truth,mode,observed=_parent_source(seed,family,role,mech,cond,episode,intervention)
 if seed not in DIAGNOSTIC:return truth,mode,observed
 readings=list(observed)
 # Two new public sensor mechanisms, each applied across BOTH intervention
 # sides of 12 public anchor pairs and the target. Same deterministic
 # transform for each sensor, never conditioned on evaluator-private truth.
 if mech==2: # shifted nonlinear/hysteretic calibration
  readings[0]=max(0.,min(1.,.5+1.15*(readings[0]-.5)))
  readings[1]=max(0.,min(1.,readings[1]+.06*math.sin(episode*.17+role)))
  readings[2]=max(0.,min(1.,readings[2]-.045*math.cos(episode*.11+family)))
 elif mech==3: # channel-specific asymmetric public calibration response
  readings[0]=max(0.,min(1.,readings[0]**1.2))
  readings[1]=max(0.,min(1.,readings[1]**.83))
  readings[2]=max(0.,min(1.,readings[2]**1.4))
  readings[3]=max(0.,min(1.,.5+.85*(readings[3]-.5)))
 return truth,mode,tuple(readings)
parent.prior.source=source
def run():
 assert not (set(FIT)&set(DIAGNOSTIC) or set(DIAGNOSTIC)&set(RESERVED)
             or set(DIAGNOSTIC)&set(OLD_RESERVED) or set(FAMILIES)&set(RESERVED_FAMILIES))
 result=parent.run()
 rows=result["rows"]
 assert len(rows)==128
 assert all(r["seed"] in DIAGNOSTIC and r["family"] in FAMILIES
            and r["public_pairs"]==12 and r["public_flat_anchors"]==24 for r in rows)
 # Prevent family-name substitution from artificially inflating relevance;
 # all four original typed task families 480..483 are remapped exactly.
 for f in FAMILIES:
  mapped=480+(f-620)
  for bits in ((True,False,True),(False,True,False),(True,True,False)):
   assert parent.prior.task(bits,f)==parent.old_task(bits,mapped)
 pairs="learned_intervention_invariant"
 shuffled="count_matched_shuffled_intervention_pairs"
 unpaired="learned_unpaired_ablation"
 scores=result["scores"]
 fair=("fitted_Gaussian_latent","empirical_conditional_Brier","Gaussian_kernel",
       "public_global_static","source_variance",shuffled,unpaired)
 strongest=max(fair,key=lambda arm:scores[arm]["accuracy"])
 gain=scores[pairs]["accuracy"]-scores[strongest]["accuracy"]
 shuffled_gain=scores[pairs]["accuracy"]-scores[shuffled]["accuracy"]
 unpaired_gain=scores[pairs]["accuracy"]-scores[unpaired]["accuracy"]
 no_regress=all(result["by_mechanism"][m][pairs]["correct"]>=
                max(result["by_mechanism"][m][a]["correct"] for a in fair)
                for m in parent.prior.HELDOUT_MECHANISMS)
 supported=gain>=.02 and shuffled_gain>0 and unpaired_gain>0 and no_regress
 result.update(schema="yggdrasil.f48.shifted-anchor-identifiability.trainonly.v1",
  stage="NEW_SHIFTED_SENSING_TRAIN_ONLY_NO_ORIGINAL",
  diagnostic_seeds=[DIAGNOSTIC.start,DIAGNOSTIC.stop],
  fit_seeds=[FIT.start,FIT.stop],families=list(FAMILIES),
  reserved_seeds=[RESERVED.start,RESERVED.stop],
  reserved_families=list(RESERVED_FAMILIES),
  prior_originals_not_consumed=[OLD_RESERVED.start,OLD_RESERVED.stop],
  shifted_heldout_mechanisms=["nonlinear_hysteresis_shifted","cross_channel_flip_asymmetric"],
  strongest_fair_control=strongest,gain_over_strongest_fair=gain,
  shuffled_pairs_ablation_gain=shuffled_gain,unpaired_ablation_gain=unpaired_gain,
  heldout_mechanism_nondegradation=no_regress,frozen_criterion_met=supported,
  verdict="TRAIN_ONLY_SUPPORTED_NOT_F3" if supported else "TRAIN_ONLY_NEGATIVE",
  primary_original_not_executed=True,independent_F3_custody=False,
  accepted_ref_mutation=False,native_576_byte_resident_qualified=False,
  paid_api_calls=0)
 return result
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

"""Y-F46: new TRAIN-only paired-vs-shuffled causal anchor study.

F45's previously frozen architecture/control implementations remain unchanged.
Run them on entirely NEW FIT/diagnostic seeds and task families. Add a public
count-matched shuffled-pair intervention control to test whether pairing causes
the benefit, not simply learned calibration capacity. No F3/original claim.
"""
import importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent.parent/"20261015-y-f45"/"source_pilot.py"
spec=importlib.util.spec_from_file_location("y_f46_f45_prior",P)
prior=importlib.util.module_from_spec(spec);sys.modules[spec.name]=prior;spec.loader.exec_module(prior)
FIT=range(401000,401008)
DIAGNOSTIC=range(401100,401108)
RESERVED=range(402000,402016)
OLD_RESERVED=range(382000,382016)
FAMILIES=(520,521,522,523)
prior.FIT=FIT
prior.DIAGNOSTIC=DIAGNOSTIC
prior.RESERVED=RESERVED
prior.FAMILIES=FAMILIES
prior.RESERVED_FAMILIES=(524,525,526,527)
old_task=prior.task
old_probability=prior.task_probability
prior.task=lambda bits,family: old_task(bits,480+family-520)
prior.task_probability=lambda probs,family: old_probability(probs,480+family-520)
old_select=prior.select
def select(arm,first,role,pairs,corr,model,bandwidth):
 if arm=="count_matched_shuffled_intervention_pairs":
  # Exactly the same PUBLIC 12 anchor pairs and trained model. Only break
  # intervention pairing by rotating the second side; no private labels
  # or diagnostic outcome enters this causal ablation.
  shuffled=tuple((pair[0],pairs[(i+1)%len(pairs)][1]) for i,pair in enumerate(pairs))
  return old_select("learned_intervention_invariant",first,role,shuffled,corr,model,bandwidth)
 return old_select(arm,first,role,pairs,corr,model,bandwidth)
prior.select=select
prior.ARMS=prior.ARMS[:-1]+("count_matched_shuffled_intervention_pairs","evaluator_oracle_unfair")
def fit_bandwidth():
 errors={b:0. for b in (.12,.17,.25)}
 for seed in (FIT.start,FIT.start+1):
  for family in FAMILIES:
   for mech in (0,1):
    for cond in (0,1):
     ref=prior.flat(prior.public_pairs(seed,family,mech,cond))
     corr=prior.prior.reliabilities(ref)
     for role in range(3):
      truth,mode,values=prior.source(seed,family,role,mech,cond,90000+role)
      for b in errors:
       risk=prior.prior.fitted_gaussian_risk(values[0],ref,corr,b)
       for j,prob in zip((1,2,3),risk):
        target=(prior.prior.bit_prob(values[j],j,corr)-truth)**2
        errors[b]+=(prob-target)**2
 return min(errors,key=lambda b:(errors[b],b))
prior.fit_bandwidth=fit_bandwidth
def run():
 assert set(FIT).isdisjoint(DIAGNOSTIC)
 assert set(DIAGNOSTIC).isdisjoint(RESERVED)
 assert set(DIAGNOSTIC).isdisjoint(OLD_RESERVED)
 report=prior.run()
 assert report["questions"]==128
 arms=report["scores"]
 cand="learned_intervention_invariant"; shuffled="count_matched_shuffled_intervention_pairs"
 unpaired="learned_unpaired_ablation"
 fair=("fitted_Gaussian_latent","empirical_conditional_Brier","Gaussian_kernel",
       "public_global_static","source_variance",unpaired,shuffled)
 strongest=max(fair,key=lambda a:arms[a]["accuracy"])
 gain=arms[cand]["accuracy"]-arms[strongest]["accuracy"]
 shuffled_gain=arms[cand]["accuracy"]-arms[shuffled]["accuracy"]
 unpaired_gain=arms[cand]["accuracy"]-arms[unpaired]["accuracy"]
 by_mech=report["by_mechanism"]
 no_regress=all(by_mech[m][cand]["correct"]>=max(by_mech[m][a]["correct"] for a in fair)
                for m in prior.HELDOUT_MECHANISMS)
 accepted=gain>=.02 and shuffled_gain>0 and unpaired_gain>0 and no_regress
 report.update(schema="yggdrasil.f46.paired-vs-shuffled-anchor.trainonly.v1",
  stage="TRAIN_ONLY_CAUSAL_ABLATION_NOT_PRIMARY_ORIGINAL",
  original_source_cohorts_not_reused=True,diagnostic_seeds=[DIAGNOSTIC.start,DIAGNOSTIC.stop],
  fit_seeds=[FIT.start,FIT.stop],reserved_seeds=[RESERVED.start,RESERVED.stop],
  old_original_reserved_not_touched=[OLD_RESERVED.start,OLD_RESERVED.stop],
  families=list(FAMILIES),reserved_families=list(prior.RESERVED_FAMILIES),
  strongest_fair_control=strongest,gain_over_strongest_fair=gain,
  shuffled_pairs_ablation_gain=shuffled_gain,unpaired_ablation_gain=unpaired_gain,
  heldout_mechanism_nondegradation=no_regress,frozen_criterion_met=accepted,
  verdict="TRAIN_ONLY_CAUSAL_INTERVENTION_SUPPORTED_NOT_F3" if accepted else
          "TRAIN_ONLY_CAUSAL_INTERVENTION_NEGATIVE",
  primary_original_not_executed=True,independent_F3_custody=False,
  native_576_byte_resident_qualified=False,accepted_ref_mutation=False,paid_api_calls=0)
 return report
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

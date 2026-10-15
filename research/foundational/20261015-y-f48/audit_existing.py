"""Independent row/receipt audit of a PREEXISTING Y-F48 TRAIN artifact.

Never runs source_pilot.run, the learner fit, or a new source experiment.
Reconstructs paid-channel values and typed-task predictions using recorded
receipt indices and the frozen deterministically registered diagnostic source.
"""
import importlib.util,json,math,pathlib,sys
base=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("y48_existing_frozen_source",base/"source_pilot.py")
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
ARMS=m.parent.prior.ARMS
def metric(rows,arm):
 n=len(rows)
 correct=sum(row["predictions"][arm]==row["truth"] for row in rows)
 fp=sum(bool(row["predictions"][arm]) and not row["truth"] for row in rows)
 fn=sum(not bool(row["predictions"][arm]) and row["truth"] for row in rows)
 brier=sum((row["probabilities"][arm]-float(row["truth"]))**2 for row in rows)/n
 logloss=-sum(math.log(row["probabilities"][arm] if row["truth"] else
     1-row["probabilities"][arm]) for row in rows)/n
 return dict(total=n,correct=correct,accuracy=correct/n,fp=fp,fn=fn,Brier=brier,logloss=logloss)
def matching(x,y):
 assert x.keys()==y.keys()
 for key,value in y.items():
  if isinstance(value,float):assert math.isclose(x[key],value,abs_tol=1e-11,rel_tol=1e-11)
  else:assert x[key]==value
def audit(path):
 d=json.loads(pathlib.Path(path).read_text())
 assert d["schema"]=="yggdrasil.f48.shifted-anchor-identifiability.trainonly.v1"
 assert d["stage"]=="NEW_SHIFTED_SENSING_TRAIN_ONLY_NO_ORIGINAL"
 assert d["questions"]==128 and len(d["rows"])==128
 assert d["fit_seeds"]==[421000,421008] and d["diagnostic_seeds"]==[421100,421108]
 assert d["families"]==list(m.FAMILIES)
 assert d["reserved_seeds"]==[422000,422016]
 assert d["reserved_families"]==list(m.RESERVED_FAMILIES)
 assert d["prior_originals_not_consumed"]==[402000,402016]
 assert d["shifted_heldout_mechanisms"]==["nonlinear_hysteresis_shifted","cross_channel_flip_asymmetric"]
 assert d["public_reference_pairs"]==12 and d["train_examples"]>0
 assert d["diagnostic_labels_not_used_in_fit"] and d["private_modes_never_in_action_inputs"]
 assert not d["independent_F3_custody"] and d["primary_original_not_executed"]
 assert not d["native_576_byte_resident_qualified"] and not d["accepted_ref_mutation"]
 assert d["paid_api_calls"]==0
 assert set(d["scores"])==set(ARMS)
 rows=d["rows"];seen=set()
 for row in rows:
  seed,family=row["seed"],row["family"]
  assert seed in m.DIAGNOSTIC and family in m.FAMILIES
  assert row["mechanism"] in m.parent.prior.HELDOUT_MECHANISMS
  assert row["condition"] in m.parent.prior.CONDITIONS
  key=seed,family,row["mechanism"],row["condition"]
  assert key not in seen;seen.add(key)
  mech=2+m.parent.prior.HELDOUT_MECHANISMS.index(row["mechanism"])
  cond=m.parent.prior.CONDITIONS.index(row["condition"])
  public=m.parent.prior.public_pairs(seed,family,mech,cond)
  assert len(public)==12 and all(p[0][0]==p[1][0] for p in public)
  ref=m.parent.prior.flat(public)
  reliability=m.parent.prior.prior.reliabilities(ref)
  hidden=[m.source(seed,family,role,mech,cond,97000+role,0) for role in range(3)]
  truth=m.parent.prior.task([v[0] for v in hidden],family)
  assert truth==row["truth"]
  assert row["public_pairs"]==12 and row["public_flat_anchors"]==24
  assert set(row["predictions"])==set(ARMS)
  assert set(row["probabilities"])==set(ARMS)
  assert set(row["receipts"])==set(ARMS)-{"evaluator_oracle_unfair"}
  assert row["predictions"]["evaluator_oracle_unfair"]==truth
  for arm,trace in row["receipts"].items():
   assert len(trace)==3
   prob=[]
   for role,channels in enumerate(trace):
    assert len(channels)==2 and channels[0]==0 and channels[1] in (1,2,3)
    j=channels[1];readings=hidden[role][2]
    prob.append(m.parent.prior.prior.bit_prob(readings[j],j,reliability))
   expected=m.parent.prior.task([x>=.5 for x in prob],family)
   p=m.parent.prior.task_probability(prob,family)
   assert row["predictions"][arm]==expected
   assert math.isclose(row["probabilities"][arm],p,rel_tol=1e-11,abs_tol=1e-11)
 assert len(seen)==128
 for arm in ARMS:matching(d["scores"][arm],metric(rows,arm))
 for field,key,values in (
  ("by_mechanism","mechanism",m.parent.prior.HELDOUT_MECHANISMS),
  ("by_condition","condition",m.parent.prior.CONDITIONS)):
  for value in values:
   cohort=[row for row in rows if row[key]==value]
   assert len(cohort)==64
   for arm in ARMS:matching(d[field][value][arm],metric(cohort,arm))
 candidate="learned_intervention_invariant"
 fair=("fitted_Gaussian_latent","empirical_conditional_Brier","Gaussian_kernel",
       "public_global_static","source_variance","count_matched_shuffled_intervention_pairs",
       "learned_unpaired_ablation")
 best=max(fair,key=lambda a:d["scores"][a]["accuracy"])
 correct={a:d["scores"][a]["correct"] for a in ARMS}
 gain=(correct[candidate]-correct[best])/128
 shuffled=(correct[candidate]-correct["count_matched_shuffled_intervention_pairs"])/128
 unpaired=(correct[candidate]-correct["learned_unpaired_ablation"])/128
 nonreg=all(d["by_mechanism"][mech][candidate]["correct"]>=max(
   d["by_mechanism"][mech][a]["correct"] for a in fair)
   for mech in m.parent.prior.HELDOUT_MECHANISMS)
 passed=gain>=.02 and shuffled>0 and unpaired>0 and nonreg
 assert d["strongest_fair_control"]==best
 assert math.isclose(d["gain_over_strongest_fair"],gain,abs_tol=1e-12)
 assert math.isclose(d["shuffled_pairs_ablation_gain"],shuffled,abs_tol=1e-12)
 assert math.isclose(d["unpaired_ablation_gain"],unpaired,abs_tol=1e-12)
 assert d["heldout_mechanism_nondegradation"]==nonreg
 assert d["frozen_criterion_met"]==passed
 assert d["verdict"]==("TRAIN_ONLY_SUPPORTED_NOT_F3" if passed else "TRAIN_ONLY_NEGATIVE")
 out=dict(schema="yggdrasil.f48.independent-existing-train-audit.v1",source_run=38805887306,
     cases=128,scores_correct=correct,strongest_fair=best,gain=gain,
     shuffled_pair_gain=shuffled,unpaired_gain=unpaired,
     heldout_mechanism_nonregression=nonreg,frozen_gate_pass=passed,
     source_independent_F3=False,primary_original_executed=False)
 print(json.dumps(out,indent=2,sort_keys=True))
 return out
if __name__=="__main__":
 if len(sys.argv)!=2:raise SystemExit("usage: audit_existing.py RESULT_JSON")
 audit(sys.argv[1])

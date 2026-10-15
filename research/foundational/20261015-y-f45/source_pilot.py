"""Y-F45 public-paired-intervention reliability transfer diagnostic.

A paired intervention changes the *observable* first reading while preserving the
paired truth label. Public calibration pairs expose neither latent mode nor
condition. Training fits exclusively on source/method classes disjoint from
diagnostic classes. No independent F3 or physically measured native 576B claim.
"""
from __future__ import annotations
import importlib.util,json,math,random,struct,sys,time
from itertools import product
from pathlib import Path

HERE=Path(__file__).resolve().parent
P=HERE.parent/"20261015-y-f43"/"source_pilot.py"
spec=importlib.util.spec_from_file_location("y_f45_f43_public_controls",P)
prior=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=prior
spec.loader.exec_module(prior)
FIT=range(381000,381008)
DIAGNOSTIC=range(381100,381108)
RESERVED=range(382000,382016)
FAMILIES=(480,481,482,483)
RESERVED_FAMILIES=(484,485,486,487)
TRAIN_MECHANISMS=("alternating_context","role_phase")
HELDOUT_MECHANISMS=("nonlinear_hysteresis","cross_channel_flip")
CONDITIONS=("coupled","decoupled")
PAIRS=12
ARMS=("learned_intervention_invariant","fitted_Gaussian_latent",
      "empirical_conditional_Brier","Gaussian_kernel","public_global_static",
      "learned_unpaired_ablation","source_variance","evaluator_oracle_unfair")
FEATURE_DIM=11

def source(seed,family,role,mech,cond,episode,intervention=0):
    if family not in FAMILIES:raise ValueError("invalid family")
    if not ((seed in FIT and mech in (0,1)) or
            (seed in DIAGNOSTIC and mech in (2,3))):
        raise ValueError("invalid source or heldout mechanism")
    if role not in (0,1,2) or cond not in (0,1) or intervention not in (0,1):
        raise ValueError("invalid role, condition or intervention")
    common=random.Random(seed*19117+family*2833+role*647+mech*239+episode*41+45037)
    truth=common.randrange(2)
    hint=common.randrange(2)^intervention
    first=max(0.,min(1.,.5+.31*(2*hint-1)+common.gauss(0,.09)))
    other=random.Random(seed*19117+family*2833+role*647+mech*239+episode*41+45037+cond*1013+intervention*1409+7717)
    if mech==0:mode=hint^(episode%2)
    elif mech==1:mode=hint^(role%2)
    elif mech==2:mode=hint^int(first>.69)
    else:mode=hint^int(role!=0)
    if cond==1:mode=other.randrange(2)
    values=[first]
    for j in (1,2,3):
        accurate=(j==1 and mode==0) or (j==2 and mode==1)
        amplitude=.41 if accurate else .032
        noise=.12 if accurate else .24
        if j==3:amplitude,noise=.22,.17
        if mech==3 and j==2:amplitude=-amplitude
        if mech==2 and j==3:amplitude,noise=.27,.16
        x=.5+(2*truth-1)*amplitude+other.gauss(0,noise)
        values.append(max(0.,min(1.,x)))
    return truth,mode,tuple(values)

def public_pairs(seed,family,mech,cond):
    pairs=[]
    for i in range(PAIRS):
        a=source(seed,family,i%3,mech,cond,50000+i*13,0)
        b=source(seed,family,i%3,mech,cond,50000+i*13,1)
        assert a[0]==b[0]
        pairs.append(((a[0],a[2]),(b[0],b[2])))
    return tuple(pairs)

def flat(pairs):
    return tuple(item for pair in pairs for item in pair)

def task(bits,family):
    bits=tuple(bool(x) for x in bits)
    if family==480:return bits[0]^bits[1]^bits[2]
    if family==481:return sum(bits)>=2
    if family==482:return bits[2] or not (bits[0] and bits[1])
    return bits[0]==bits[1]==bits[2]

def task_probability(probs,family):
    total=0.
    for bits in product((False,True),repeat=3):
        p=1.
        for b,x in zip(bits,probs):p*=x if b else 1-x
        if task(bits,family):total+=p
    return max(1e-6,min(1-1e-6,total))

def anchor_features(first,role,j,pairs,corr):
    ref=flat(pairs)
    plain=prior.empirical_risks(first,ref,corr)[j-1]
    per_pair=[]
    for pair in pairs:
        e=[]
        for y,readings in pair:
            prob=prior.bit_prob(readings[j],j,corr)
            e.append((prob-y)**2)
        per_pair.append(e)
    means=[sum(x)/2 for x in per_pair]
    variation=sum(abs(x[0]-x[1]) for x in per_pair)/len(per_pair)
    worst=sum(max(x) for x in per_pair)/len(per_pair)
    pooled=sum(means)/len(means)
    covariance=sum((pair[0][1][0]-pair[1][1][0])*(v[0]-v[1])
                   for pair,v in zip(pairs,per_pair))/len(pairs)
    strength=corr[j]
    z=2*first-1
    # Each feature is derived entirely from public paired calibration and bought first.
    return (1.,plain,pooled,worst,variation,covariance,
            z,z*z,abs(strength),strength,plain*variation)

class InvariantRisk:
    def __init__(self):
        self.weights={j:[0.]*FEATURE_DIM for j in (1,2,3)}
        self.fit_count=0
    def estimate(self,first,role,j,pairs,corr,unpaired=False):
        f=list(anchor_features(first,role,j,pairs,corr))
        if unpaired:
            # Eliminate the pair-specific intervention contrast and covariance.
            f[3]=f[2];f[4]=0.;f[5]=0.;f[10]=0.
        z=sum(w*x for w,x in zip(self.weights[j],f))
        return 1/(1+math.exp(-max(-15,min(15,z))))
    def fit(self, examples,epochs=6,rate=.05):
        rows=list(examples)
        for _ in range(epochs):
            for first,role,j,pairs,corr,label in rows:
                f=anchor_features(first,role,j,pairs,corr)
                p=self.estimate(first,role,j,pairs,corr)
                grad=(p-label)*p*(1-p)
                for k,x in enumerate(f):
                    self.weights[j][k]-=rate*(grad*x+.0001*self.weights[j][k])
        self.fit_count=len(rows)
        return self
    def packed(self):
        return struct.pack("<"+str(FEATURE_DIM*3)+"f",*(
           x for j in (1,2,3) for x in self.weights[j]))

def select(arm,first,role,pairs,corr,model,bandwidth):
    ref=flat(pairs)
    if arm in ("learned_intervention_invariant","learned_unpaired_ablation"):
        losses=[model.estimate(first,role,j,pairs,corr,
                    unpaired=arm=="learned_unpaired_ablation") for j in (1,2,3)]
    elif arm=="empirical_conditional_Brier":
        losses=prior.empirical_risks(first,ref,corr)
    elif arm=="Gaussian_kernel":
        losses=prior.empirical_risks(first,ref,corr,bandwidth)
    elif arm=="fitted_Gaussian_latent":
        losses=prior.fitted_gaussian_risk(first,ref,corr,bandwidth)
    elif arm=="public_global_static":
        return max((1,2,3),key=lambda j:(abs(corr[j]),-j))
    elif arm=="source_variance":
        means=[sum(v[j] for y,v in ref)/len(ref) for j in (1,2,3)]
        var=[sum((v[j]-means[j-1])**2 for y,v in ref)/len(ref) for j in (1,2,3)]
        return max((1,2,3),key=lambda j:(var[j-1],-j))
    else:raise ValueError("unknown selector")
    return (1,2,3)[min(range(3),key=lambda i:(losses[i],i))]

def training_examples():
    for seed in FIT:
      for family in FAMILIES:
       for mech in (0,1):
        for cond in (0,1):
          pairs=public_pairs(seed,family,mech,cond)
          corr=prior.reliabilities(flat(pairs))
          static=max((1,2,3),key=lambda j:(abs(corr[j]),-j))
          for episode in range(12):
            roles=[source(seed,family,role,mech,cond,70000+episode*17,0) for role in range(3)]
            answer=task([r[0] for r in roles],family)
            for role in range(3):
              for j in (1,2,3):
                guessed=[prior.bit_prob(r[2][j if k==role else static],
                    j if k==role else static,corr)>=.5 for k,r in enumerate(roles)]
                label=float(task(guessed,family)!=answer)
                yield (roles[role][2][0],role,j,pairs,corr,label)

def fit_bandwidth():
    errors={b:0. for b in (.12,.17,.25)}
    for seed in (381000,381001):
      for family in FAMILIES:
       for mech in (0,1):
        for cond in (0,1):
          refs=flat(public_pairs(seed,family,mech,cond))
          corr=prior.reliabilities(refs)
          for role in range(3):
            true,mode,values=source(seed,family,role,mech,cond,90000+role)
            for b in errors:
                est=prior.fitted_gaussian_risk(values[0],refs,corr,b)
                for j,p in zip((1,2,3),est):
                    target=(prior.bit_prob(values[j],j,corr)-true)**2
                    errors[b]+=(p-target)**2
    return min(errors,key=lambda b:(errors[b],b))

class Port:
    def __init__(self,values):
        self.__values=values;self.trace=[]
    def buy(self,j):
        if j not in (0,1,2,3) or any(x[0]==j for x in self.trace) or len(self.trace)>=2:
            raise ValueError("duplicate/third/invalid paid read")
        val=self.__values[j];self.trace.append((j,val));return val

def recount(rows,arm):
    n=len(rows)
    correct=sum(r["predictions"][arm]==r["truth"] for r in rows)
    fp=sum(bool(r["predictions"][arm]) and not r["truth"] for r in rows)
    fn=sum(not bool(r["predictions"][arm]) and r["truth"] for r in rows)
    brier=sum((r["probabilities"][arm]-float(r["truth"]))**2 for r in rows)/n
    logloss=-sum(math.log(r["probabilities"][arm] if r["truth"]
                        else 1-r["probabilities"][arm]) for r in rows)/n
    return dict(total=n,correct=correct,accuracy=correct/n,fp=fp,fn=fn,Brier=brier,logloss=logloss)

def run():
    assert not set(FIT)&set(DIAGNOSTIC) and not set(DIAGNOSTIC)&set(RESERVED)
    assert not set(FAMILIES)&set(RESERVED_FAMILIES)
    start=time.perf_counter()
    model=InvariantRisk().fit(training_examples())
    bandwidth=fit_bandwidth()
    rows=[]
    for seed in DIAGNOSTIC:
      for family in FAMILIES:
       for mech in (2,3):
        for cond in (0,1):
          pairs=public_pairs(seed,family,mech,cond)
          corr=prior.reliabilities(flat(pairs))
          targets=[source(seed,family,role,mech,cond,97000+role,0) for role in range(3)]
          truth=task([t[0] for t in targets],family)
          answers={"evaluator_oracle_unfair":truth}
          probabilities={"evaluator_oracle_unfair":1-1e-6 if truth else 1e-6}
          receipts={}
          for arm in ARMS[:-1]:
            probs=[];trace=[]
            for role,(_,hidden_mode,values) in enumerate(targets):
                port=Port(values)
                first=port.buy(0)
                second_idx=select(arm,first,role,pairs,corr,model,bandwidth)
                second=port.buy(second_idx)
                probs.append(prior.bit_prob(second,second_idx,corr))
                trace.append([v[0] for v in port.trace])
            answers[arm]=task([x>=.5 for x in probs],family)
            probabilities[arm]=task_probability(probs,family)
            receipts[arm]=trace
          rows.append(dict(seed=seed,family=family,mechanism=HELDOUT_MECHANISMS[mech-2],
            condition=CONDITIONS[cond],truth=truth,
            predictions=answers,probabilities=probabilities,receipts=receipts,
            public_pairs=len(pairs),public_flat_anchors=len(flat(pairs))))
    scores={a:recount(rows,a) for a in ARMS}
    by_mech={m:{a:recount([r for r in rows if r["mechanism"]==m],a)
                for a in ARMS} for m in HELDOUT_MECHANISMS}
    by_cond={c:{a:recount([r for r in rows if r["condition"]==c],a)
                for a in ARMS} for c in CONDITIONS}
    fair=("fitted_Gaussian_latent","empirical_conditional_Brier",
          "Gaussian_kernel","public_global_static","source_variance")
    strongest=max(fair,key=lambda a:scores[a]["accuracy"])
    gain=scores["learned_intervention_invariant"]["accuracy"]-scores[strongest]["accuracy"]
    ablate=scores["learned_intervention_invariant"]["accuracy"]-scores["learned_unpaired_ablation"]["accuracy"]
    no_regress=all(by_mech[m]["learned_intervention_invariant"]["correct"]>=
                   max(by_mech[m][a]["correct"] for a in fair) for m in HELDOUT_MECHANISMS)
    qualified=gain>=.02 and ablate>0 and no_regress
    return dict(schema="yggdrasil.f45.paired-intervention-invariance.trainonly.v1",
      stage="FRESH_TRAIN_ONLY_UNSEEN_MECHANISMS_NOT_ORIGINAL",
      fit_seeds=[FIT.start,FIT.stop],diagnostic_seeds=[DIAGNOSTIC.start,DIAGNOSTIC.stop],
      reserved_seeds=[RESERVED.start,RESERVED.stop],families=list(FAMILIES),
      reserved_families=list(RESERVED_FAMILIES),
      train_mechanisms=list(TRAIN_MECHANISMS),heldout_mechanisms=list(HELDOUT_MECHANISMS),
      questions=len(rows),public_reference_pairs=PAIRS,
      train_examples=model.fit_count,packed_parameter_bytes=len(model.packed()),
      packed_bytes_not_native_residency=True,fit_bandwidth=bandwidth,
      strongest_fair_control=strongest,gain_over_strongest_fair=gain,
      paired_intervention_ablation_gain=ablate,heldout_mechanism_nondegradation=no_regress,
      scores=scores,by_mechanism=by_mech,by_condition=by_cond,
      elapsed_seconds=time.perf_counter()-start,rows=rows,
      verdict="TRAIN_ONLY_INTERVENTION_INVARIANCE_QUALIFIED" if qualified else "TRAIN_ONLY_INTERVENTION_INVARIANCE_NOT_QUALIFIED",
      diagnostic_labels_not_used_in_fit=True,private_modes_never_in_action_inputs=True,
      independent_F3_custody=False,primary_original_not_executed=True,
      native_576_byte_resident_qualified=False,accepted_ref_mutation=False,paid_api_calls=0)

if __name__=="__main__":print(json.dumps(run(),indent=2,sort_keys=True))

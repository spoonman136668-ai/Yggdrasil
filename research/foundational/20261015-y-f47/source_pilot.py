"""Yggdrasil F47 trainable group-robust downstream-task calibration.

The grouped learner uses public sensor reference channels and TRAIN task-loss
labels, preserving fully disjoint source families and unseen mechanism classes.
The same features and labels train a pooled ERM control. No source family,
mechanism or condition ID is passed to a diagnostic selector, and no F3/
original/native <=576B claim is made.
"""
from __future__ import annotations
import importlib.util,json,math,random,struct,sys,time
from itertools import product
from pathlib import Path
HERE=Path(__file__).resolve().parent
P=HERE.parent/"20261015-y-f45"/"source_pilot.py"
s=importlib.util.spec_from_file_location("y47_f45_public_baselines",P)
prior=importlib.util.module_from_spec(s);sys.modules[s.name]=prior;s.loader.exec_module(prior)

FIT=range(431000,431008)
DIAG=range(431100,431108)
FIT_FAM=(580,581,582,583)
DIAG_FAM=(584,585,586,587)
RESERVED=range(432000,432016)
RESERVED_FAM=(588,589,590,591)
FIT_MECH=("alternating_noise","role_phase_shift")
DIAG_MECH=("sparse_channel_dropout","delayed_sign_flip")
CONDITIONS=("coupled","decoupled")
ANCHORS=24
FEATURE_DIM=12
ARMS=("groupDRO_task_selector","equal_data_ERM_task_selector",
      "fitted_Gaussian_risk","empirical_conditional_Brier","public_static",
      "variance_control","first_read_masked_groupDRO","private_oracle_unfair")

def source(seed,family,role,mech,cond,episode):
    if not ((seed in FIT and family in FIT_FAM and mech in (0,1)) or
            (seed in DIAG and family in DIAG_FAM and mech in (2,3))):
        raise ValueError("unregistered source, original or cross-fold mechanism")
    if role not in (0,1,2) or cond not in (0,1):raise ValueError("invalid source")
    base=random.Random(seed*18121+family*2089+role*389+mech*173+episode*53+47001)
    truth=base.randrange(2);hint=base.randrange(2)
    first=max(0.,min(1.,.5+.29*(2*hint-1)+base.gauss(0,.085)))
    private=random.Random(seed*18121+family*2089+role*389+mech*173+
                          episode*53+47001+cond*1009+8819)
    if mech==0:mode=hint^(episode%2)
    elif mech==1:mode=hint^int(role>0)^int((episode//3)%2)
    elif mech==2:mode=hint^int(first>.6)
    else:mode=hint^int((episode//2)%2)
    if cond==1:mode=private.randrange(2)
    readings=[first]
    for j in (1,2,3):
        reliable=(j==1 and mode==0) or (j==2 and mode==1)
        amplitude=.44 if reliable else .02
        noise=.115 if reliable else .26
        if j==3:amplitude,noise=.24,.18
        if mech==2 and (episode%5==0) and j in (1,2):
            amplitude,noise=0.,.30
        if mech==3 and j==2:
            amplitude*=(-1 if (episode//2)%2 else 1)
        x=.5+(2*truth-1)*amplitude+private.gauss(0,noise)
        readings.append(max(0.,min(1.,x)))
    return truth,mode,tuple(readings)

def references(seed,fam,mech,cond):
    return tuple((y,channels) for i in range(ANCHORS)
        for y,mode,channels in [source(seed,fam,i%3,mech,cond,50000+i*17)])

def task(bits,family):
    x=tuple(bool(v) for v in bits)
    pattern=family%4
    if pattern==0:return x[0]^x[1]^x[2]
    if pattern==1:return sum(x)>=2
    if pattern==2:return x[2] or not (x[0] and x[1])
    return x[0]==x[1]==x[2]

def task_prob(probs,family):
    result=0.
    for bits in product((False,True),repeat=3):
        p=1.
        for b,q in zip(bits,probs):p*=q if b else 1-q
        if task(bits,family):result+=p
    return max(1e-6,min(1-1e-6,result))

def channel_prob(x,j,corr):
    return prior.prior.bit_prob(x,j,corr)

def features(first,role,j,reference,corr):
    t=2*first-1
    pooled=[];weights=[];local=[]
    for y,channels in reference:
        err=(channel_prob(channels[j],j,corr)-y)**2
        w=math.exp(-8*abs(channels[0]-first))
        pooled.append(err);weights.append(w);local.append(channels[0])
    aggregate=sum(pooled)/len(pooled)
    conditional=sum(x*w for x,w in zip(pooled,weights))/max(sum(weights),1e-12)
    lo=[x for x,q in zip(pooled,local) if q<.5]
    hi=[x for x,q in zip(pooled,local) if q>=.5]
    low=sum(lo)/len(lo) if lo else aggregate
    high=sum(hi)/len(hi) if hi else aggregate
    variance=sum((x-aggregate)**2 for x in pooled)/len(pooled)
    slope=sum((u-.5)*(x-aggregate) for u,x in zip(local,pooled))/len(pooled)
    sign=corr[j]
    return (1.,t,t*t,sign,abs(sign),conditional,aggregate,
            high-low,variance,slope,role%2,conditional*t)

def sigmoid(z):return 1/(1+math.exp(-max(-15.,min(15.,z))))

class RiskModel:
    def __init__(self):
        self.weights={j:[0.]*FEATURE_DIM for j in (1,2,3)}
        self.training_count=0
        self.group_weights=[.5,.5]
    def predict(self,first,role,j,reference,corr):
        f=features(first,role,j,reference,corr)
        return sigmoid(sum(x*y for x,y in zip(f,self.weights[j])))
    def fit(self,rows,robust=False,epochs=8,rate=.075):
        training=list(rows)
        if not training:raise ValueError("no training")
        # Both ERM and groupDRO receive identical rows/labels, feature size,
        # epochs, rate and regularization; only group weighting changes.
        weights=[.5,.5]
        for epoch in range(epochs):
            if robust:
                group_loss=[0.,0.];group_count=[0,0]
                for group,first,role,j,ref,corr,outcome in training:
                    pred=self.predict(first,role,j,ref,corr)
                    group_loss[group]+=(pred-outcome)**2
                    group_count[group]+=1
                for k in (0,1):
                    group_loss[k]/=max(1,group_count[k])
                a=math.exp(min(5.,max(-5.,12*(group_loss[0]-group_loss[1]))))
                weights=[a/(a+1),1/(a+1)]
            for group,first,role,j,ref,corr,outcome in training:
                f=features(first,role,j,ref,corr)
                pred=sigmoid(sum(a*b for a,b in zip(f,self.weights[j])))
                group_factor=weights[group]*2 if robust else 1.
                grad=(pred-outcome)*pred*(1-pred)*group_factor
                w=self.weights[j]
                for k in range(FEATURE_DIM):
                    w[k]-=rate*(grad*f[k]+.00005*w[k])
        self.training_count=len(training);self.group_weights=weights
        return self
    def packed_weights(self):
        return struct.pack("<"+str(3*FEATURE_DIM)+"f",
            *(w for j in (1,2,3) for w in self.weights[j]))

def training_examples():
    for seed in FIT:
      for family in FIT_FAM:
       for mech in (0,1):
        for cond in (0,1):
          ref=references(seed,family,mech,cond)
          corr=prior.prior.reliabilities(ref)
          static=max((1,2,3),key=lambda j:(abs(corr[j]),-j))
          for ep in range(10):
            src=[source(seed,family,role,mech,cond,70000+17*ep)
                 for role in range(3)]
            actual=task([item[0] for item in src],family)
            for role in range(3):
              for j in (1,2,3):
                choices=[j if k==role else static for k in range(3)]
                probs=[channel_prob(item[2][choice],choice,corr)
                       for item,choice in zip(src,choices)]
                error=float(task([p>=.5 for p in probs],family)!=actual)
                yield mech,src[role][2][0],role,j,ref,corr,error

def calibrate_gaussian_bandwidth():
    losses={b:0. for b in (.12,.17,.25)}
    for seed in (FIT.start,FIT.start+1):
      for fam in FIT_FAM:
       for mech in (0,1):
        for cond in (0,1):
          ref=references(seed,fam,mech,cond)
          corr=prior.prior.reliabilities(ref)
          for role in range(3):
            y,hidden,readings=source(seed,fam,role,mech,cond,92000+role)
            for b in losses:
                risks=prior.prior.fitted_gaussian_risk(readings[0],ref,corr,b)
                for j,risk in zip((1,2,3),risks):
                    err=(channel_prob(readings[j],j,corr)-y)**2
                    losses[b]+=(risk-err)**2
    return min(losses,key=lambda b:(losses[b],b))

def select(arm,first,role,ref,corr,robust,erm,bandwidth):
    if arm in ("groupDRO_task_selector","first_read_masked_groupDRO"):
        use_first=.5 if arm=="first_read_masked_groupDRO" else first
        losses=[robust.predict(use_first,role,j,ref,corr) for j in (1,2,3)]
    elif arm=="equal_data_ERM_task_selector":
        losses=[erm.predict(first,role,j,ref,corr) for j in (1,2,3)]
    elif arm=="fitted_Gaussian_risk":
        losses=prior.prior.fitted_gaussian_risk(first,ref,corr,bandwidth)
    elif arm=="empirical_conditional_Brier":
        losses=prior.prior.empirical_risks(first,ref,corr)
    elif arm=="public_static":
        return max((1,2,3),key=lambda j:(abs(corr[j]),-j))
    elif arm=="variance_control":
        means=[sum(v[j] for y,v in ref)/len(ref) for j in (1,2,3)]
        variance=[sum((v[j]-means[j-1])**2 for y,v in ref)/len(ref) for j in (1,2,3)]
        return max((1,2,3),key=lambda j:(variance[j-1],-j))
    else:raise ValueError("unknown arm")
    return (1,2,3)[min(range(3),key=lambda k:(losses[k],k))]

class Port:
    def __init__(self,channels):
        self.__channels=channels;self.receipts=[]
    def buy(self,j):
        if j not in (0,1,2,3) or any(a==j for a,b in self.receipts) or len(self.receipts)>=2:
            raise ValueError("invalid/duplicate/third sensor")
        v=self.__channels[j];self.receipts.append((j,v));return v

def recount(rows,arm):
    n=len(rows)
    correct=sum(r["predictions"][arm]==r["truth"] for r in rows)
    fp=sum(bool(r["predictions"][arm]) and not r["truth"] for r in rows)
    fn=sum(not bool(r["predictions"][arm]) and r["truth"] for r in rows)
    brier=sum((r["task_probabilities"][arm]-float(r["truth"]))**2 for r in rows)/n
    logloss=-sum(math.log(r["task_probabilities"][arm] if r["truth"]
                        else 1-r["task_probabilities"][arm]) for r in rows)/n
    return dict(correct=correct,total=n,accuracy=correct/n,fp=fp,fn=fn,Brier=brier,logloss=logloss)

def run():
    assert not set(FIT)&set(DIAG) and not set(FIT_FAM)&set(DIAG_FAM)
    assert not set(DIAG)&set(RESERVED) and not set(DIAG_FAM)&set(RESERVED_FAM)
    start=time.perf_counter()
    training=list(training_examples())
    robust=RiskModel().fit(training,robust=True)
    erm=RiskModel().fit(training,robust=False)
    assert robust.training_count==erm.training_count==len(training)
    bandwidth=calibrate_gaussian_bandwidth()
    rows=[]
    for seed in DIAG:
      for family in DIAG_FAM:
       for mech in (2,3):
        for cond in (0,1):
          ref=references(seed,family,mech,cond)
          corr=prior.prior.reliabilities(ref)
          hidden=[source(seed,family,role,mech,cond,97000+role)
                  for role in range(3)]
          truth=task([v[0] for v in hidden],family)
          preds={"private_oracle_unfair":truth}
          probabilities={"private_oracle_unfair":.999999 if truth else .000001}
          receipts={}
          for arm in ARMS[:-1]:
            probs=[];bought=[]
            for role,(_,hidden_mode,channels) in enumerate(hidden):
                port=Port(channels);first=port.buy(0)
                second=select(arm,first,role,ref,corr,robust,erm,bandwidth)
                val=port.buy(second)
                probs.append(channel_prob(val,second,corr))
                bought.append([a for a,b in port.receipts])
            preds[arm]=task([p>=.5 for p in probs],family)
            probabilities[arm]=task_prob(probs,family)
            receipts[arm]=bought
          rows.append(dict(seed=seed,family=family,mechanism=DIAG_MECH[mech-2],
             condition=CONDITIONS[cond],truth=truth,predictions=preds,
             task_probabilities=probabilities,receipts=receipts,
             public_anchor_count=len(ref)))
    scores={arm:recount(rows,arm) for arm in ARMS}
    by_mech={m:{a:recount([r for r in rows if r["mechanism"]==m],a)
                 for a in ARMS} for m in DIAG_MECH}
    fair=("equal_data_ERM_task_selector","fitted_Gaussian_risk",
          "empirical_conditional_Brier","public_static","variance_control")
    strong=max(fair,key=lambda a:scores[a]["accuracy"])
    gain=scores["groupDRO_task_selector"]["accuracy"]-scores[strong]["accuracy"]
    ablation=scores["groupDRO_task_selector"]["accuracy"]-scores["first_read_masked_groupDRO"]["accuracy"]
    nonregress=all(by_mech[m]["groupDRO_task_selector"]["correct"]>=
        max(by_mech[m][a]["correct"] for a in fair) for m in DIAG_MECH)
    qualified=gain>=.02 and ablation>0 and nonregress
    return dict(schema="yggdrasil.f47.groupDRO-typed-task.trainonly.v1",
      stage="TRAIN_ONLY_UNSEEN_MECHANISM_NO_PRIMARY_ORIGINAL",
      fit_seeds=[FIT.start,FIT.stop],diagnostic_seeds=[DIAG.start,DIAG.stop],
      fit_families=list(FIT_FAM),diagnostic_families=list(DIAG_FAM),
      train_mechanisms=list(FIT_MECH),heldout_mechanisms=list(DIAG_MECH),
      proposed_original_seeds_NOT_RESERVED=[RESERVED.start,RESERVED.stop],
      public_anchor_count=ANCHORS,paid_channels_per_role=2,questions=len(rows),
      training_examples=len(training),packed_parameter_bytes=len(robust.packed_weights()),
      robust_group_weights=robust.group_weights,
      parameter_bytes_not_total_native_residency=True,
      fitted_baseline_bandwidth=bandwidth,
      scores=scores,by_mechanism=by_mech,rows=rows,
      strongest_fair_control=strong,candidate_gain=gain,
      first_read_ablation_gain=ablation,per_mechanism_nondegradation=nonregress,
      elapsed_seconds=time.perf_counter()-start,frozen_criterion_met=qualified,
      verdict="TRAIN_ONLY_GROUP_ROBUST_CALIBRATION_SUPPORTED" if qualified else
        "TRAIN_ONLY_GROUP_ROBUST_CALIBRATION_NEGATIVE",
      diagnostic_labels_not_used_in_fit=True,private_mode_never_selector_feature=True,
      source_independent_F3_custody=False,original_executed=False,
      native_576_bytes_residency_qualified=False,
      accepted_ref_mutation=False,paid_api_calls=0)

if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

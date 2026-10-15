"""Y-F44 public-anchor learned reliability transfer onto heldout mechanism classes.

Train identities/mechanisms and diagnostic identities/mechanisms are disjoint.
Train labels never reach an action. All observed anchors are public labeled
calibration, and every policy uses exactly one first plus one target purchase.
Python heap, anchor RAM and model parameters are NOT native <=576B qualification.
"""
from __future__ import annotations
import json,math,random,struct,sys,time
from itertools import product
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
UPSTREAM=HERE.parent/"20261015-y-f43"/"source_pilot.py"
spec=importlib.util.spec_from_file_location("y_f44_fair_controls",UPSTREAM)
prior=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=prior
spec.loader.exec_module(prior)

FIT=range(361000,361008)
DIAGNOSTIC=range(361100,361108)
RESERVED=range(362000,362016)
FAMILIES=(440,441,442,443)
RESERVED_FAMILIES=(444,445,446,447)
TRAIN_MECHANISMS=("lagged_hint","periodic_inversion")
HELDOUT_MECHANISMS=("threshold_context","cross_channel_swap")
CONDITIONS=("coupled","decoupled")
ANCHORS=24
FEATURE_DIM=14
ARMS=("learned_anchor_latent","empirical_conditional_Brier","Gaussian_kernel",
      "fitted_Gaussian_latent","global_static","source_variance",
      "learned_first_masked","private_oracle_unfair")

def source(seed,family,role,mechanism,condition,episode):
    if family not in FAMILIES:
        raise ValueError("reserved or unknown family")
    if seed in FIT and mechanism in (0,1):pass
    elif seed in DIAGNOSTIC and mechanism in (2,3):pass
    else:raise ValueError("identity/mechanism split forbids source")
    if role not in (0,1,2) or condition not in (0,1):
        raise ValueError("invalid source role/condition")
    shared=random.Random(seed*19001+family*1069+role*193+mechanism*173+episode*41+44071)
    truth=shared.randrange(2)
    hint=shared.randrange(2)
    first=max(0.,min(1.,.5+.31*(2*hint-1)+shared.gauss(0,.08)))
    other=random.Random(seed*19001+family*1069+role*193+mechanism*173+
                        episode*41+44071+condition*1013+70003)
    if mechanism==0:
        mode=hint ^ (role%2)
    elif mechanism==1:
        mode=hint ^ (episode%2)
    elif mechanism==2:
        mode=hint ^ int(first>.71)
    else:
        mode=hint ^ int(role!=0)
    if condition==1:
        mode=other.randrange(2)
    readings=[first]
    for j in (1,2,3):
        reliable=(j==1 and mode==0) or (j==2 and mode==1)
        amp=.43 if reliable else .025
        noise=.1 if reliable else .25
        if j==3:amp,noise=.22,.19
        if mechanism==3 and j==2:amp=-amp
        if mechanism==2 and j==3:amp,noise=.27,.16
        v=.5+(2*truth-1)*amp+other.gauss(0,noise)
        readings.append(max(0.,min(1.,v)))
    return truth,mode,tuple(readings)

def references(seed,family,mechanism,condition):
    return tuple((truth,readings) for i in range(ANCHORS) for truth,mode,readings
        in [source(seed,family,i%3,mechanism,condition,50000+i*13)])

def task(bits,family):
    bits=tuple(bool(b) for b in bits)
    if family==440:return bits[0]^bits[1]^bits[2]
    if family==441:return sum(bits)>=2
    if family==442:return bits[2] or not (bits[0] and bits[1])
    return bits[0]==bits[1]==bits[2]

def bit_prob(x,j,corr):
    return prior.bit_prob(x,j,corr)

def feature(first,role,j,ref,corr):
    """Structured public-anchor conditional reliability, no family or mech ID."""
    risks=[]
    errors=[]
    weights=[]
    for truth,channels in ref:
        e=(bit_prob(channels[j],j,corr)-truth)**2
        w=math.exp(-abs(first-channels[0])*9)
        errors.append(e)
        weights.append(w)
    n=len(ref)
    cond=sum(w*e for w,e in zip(weights,errors))/max(sum(weights),1e-12)
    global_=sum(errors)/n
    lo=[e for e,(y,ch) in zip(errors,ref) if ch[0]<.5]
    hi=[e for e,(y,ch) in zip(errors,ref) if ch[0]>=.5]
    lo_avg=sum(lo)/len(lo) if lo else global_
    hi_avg=sum(hi)/len(hi) if hi else global_
    corr_first=sum((ch[0]-.5)*(e-global_) for e,(y,ch) in zip(errors,ref))/n
    eff=sum(weights)**2/max(sum(w*w for w in weights),1e-12)
    r=corr[j]
    z=2*first-1
    parity=1. if role%2 else -1.
    return (1.,cond,global_,lo_avg,hi_avg,hi_avg-lo_avg,
            corr_first,eff/n,r,abs(r),z,z*z,z*parity,cond*z)

def loss_to_logit(x):
    x=max(1e-5,min(1-1e-5,x))
    return math.log(x/(1-x))

class LatentRisk:
    def __init__(self):
        self.weights={j:[0.]*FEATURE_DIM for j in (1,2,3)}
        self.num_examples=0
    def score(self,first,role,j,ref,corr):
        f=feature(first,role,j,ref,corr)
        z=sum(w*x for w,x in zip(self.weights[j],f))
        return 1/(1+math.exp(-max(-16.,min(16.,z))))
    def fit(self,examples,epochs=10,rate=.055):
        rows=list(examples)
        for epoch in range(epochs):
            for first,role,j,ref,corr,outcome_error in rows:
                features=feature(first,role,j,ref,corr)
                pred=self.score(first,role,j,ref,corr)
                grad=(pred-outcome_error)*pred*(1-pred)
                for k,value in enumerate(features):
                    self.weights[j][k]-=rate*(grad*value+1e-5*self.weights[j][k])
        self.num_examples=len(rows)
        return self
    def packed_bytes(self):
        return struct.pack("<"+str(FEATURE_DIM*3)+"f",*(
            w for j in (1,2,3) for w in self.weights[j]))

def select(method,first,role,ref,corr,learner,bandwidth):
    if method in ("learned_anchor_latent","learned_first_masked"):
        used_first=.5 if method=="learned_first_masked" else first
        risks=[learner.score(used_first,role,j,ref,corr) for j in (1,2,3)]
    elif method=="empirical_conditional_Brier":
        risks=prior.empirical_risks(first,ref,corr)
    elif method=="Gaussian_kernel":
        risks=prior.empirical_risks(first,ref,corr,bandwidth)
    elif method=="fitted_Gaussian_latent":
        risks=prior.fitted_gaussian_risk(first,ref,corr,bandwidth)
    elif method=="global_static":
        return max((1,2,3),key=lambda j:(abs(corr[j]),-j))
    elif method=="source_variance":
        means=[sum(v[j] for y,v in ref)/len(ref) for j in (1,2,3)]
        variances=[sum((v[j]-means[j-1])**2 for y,v in ref)/len(ref) for j in (1,2,3)]
        return max((1,2,3),key=lambda j:(variances[j-1],-j))
    else:raise ValueError("unknown selector")
    return (1,2,3)[min(range(3),key=lambda k:(risks[k],k))]

def training_examples():
    for seed in FIT:
      for family in FAMILIES:
       for mech in (0,1):
        for cond in (0,1):
          ref=references(seed,family,mech,cond)
          corr=prior.reliabilities(ref)
          static=max((1,2,3),key=lambda j:(abs(corr[j]),-j))
          for episode in range(8):
            units=[source(seed,family,role,mech,cond,70000+17*episode) for role in range(3)]
            truth=task([v[0] for v in units],family)
            for role in range(3):
              for j in (1,2,3):
                guesses=[bit_prob(v[2][j if r==role else static],
                             j if r==role else static,corr)>=.5
                             for r,v in enumerate(units)]
                target=float(task(guesses,family)!=truth)
                yield (units[role][2][0],role,j,ref,corr,target)

def choose_bandwidth_on_fit():
    # All hyperparameter choices use training labels only, never unseen mechanisms.
    errors={b:0. for b in (.12,.17,.25)}
    for seed in (361000,361001):
      for fam in FAMILIES:
       for mech in (0,1):
        for cond in (0,1):
          ref=references(seed,fam,mech,cond)
          corr=prior.reliabilities(ref)
          for role in range(3):
            truth,hidden,channels=source(seed,fam,role,mech,cond,80000+role)
            for b in errors:
                for j,e in zip((1,2,3),prior.fitted_gaussian_risk(channels[0],ref,corr,b)):
                    actual=(bit_prob(channels[j],j,corr)-truth)**2
                    errors[b]+=(e-actual)**2
    return min(errors,key=lambda b:(errors[b],b))

def predicted_task_probability(role_probs,family):
    total=0.
    for bits in product((False,True),repeat=3):
        likelihood=1.
        for bit,p in zip(bits,role_probs):
            likelihood*=p if bit else 1-p
        if task(bits,family):total+=likelihood
    return max(1e-6,min(1-1e-6,total))

class Port:
    def __init__(self,values):
        self.__values=values;self.receipts=[]
    def buy(self,j):
        if j not in (0,1,2,3) or j in [v[0] for v in self.receipts] or len(self.receipts)>=2:
            raise ValueError("duplicate/third/unapproved sensor read")
        x=self.__values[j];self.receipts.append((j,x));return x

def recount(rows,arm):
    n=len(rows)
    correct=sum(r["predictions"][arm]==r["truth"] for r in rows)
    fp=sum(bool(r["predictions"][arm]) and not r["truth"] for r in rows)
    fn=sum(not bool(r["predictions"][arm]) and r["truth"] for r in rows)
    return dict(total=n,correct=correct,accuracy=correct/n,fp=fp,fn=fn,
      Brier=sum((r["task_probabilities"][arm]-float(r["truth"]))**2 for r in rows)/n,
      logloss=-sum(math.log(r["task_probabilities"][arm] if r["truth"]
                      else 1-r["task_probabilities"][arm]) for r in rows)/n)

def run():
    assert not set(FIT)&set(DIAGNOSTIC)
    assert not set(FIT)&set(RESERVED)
    assert not set(DIAGNOSTIC)&set(RESERVED)
    assert not set(FAMILIES)&set(RESERVED_FAMILIES)
    start=time.perf_counter()
    model=LatentRisk().fit(training_examples())
    bandwidth=choose_bandwidth_on_fit()
    rows=[]
    for seed in DIAGNOSTIC:
      for family in FAMILIES:
       for mech in (2,3):
        for cond in (0,1):
          ref=references(seed,family,mech,cond)
          corr=prior.reliabilities(ref)
          hidden=[source(seed,family,role,mech,cond,90000+role) for role in range(3)]
          truth=task([v[0] for v in hidden],family)
          answers={"private_oracle_unfair":truth}
          probabilities={"private_oracle_unfair":.999999 if truth else .000001}
          receipts={}
          for method in ARMS[:-1]:
            estimated_bits=[];paid=[]
            for role,(_,hidden_mode,values) in enumerate(hidden):
                port=Port(values);first=port.buy(0)
                second_idx=select(method,first,role,ref,corr,model,bandwidth)
                acquired=port.buy(second_idx)
                estimated_bits.append(bit_prob(acquired,second_idx,corr))
                paid.append([entry[0] for entry in port.receipts])
            p=predicted_task_probability(estimated_bits,family)
            probabilities[method]=p
            answers[method]=task([x>=.5 for x in estimated_bits],family)
            receipts[method]=paid
          rows.append(dict(seed=seed,family=family,
             mechanism=HELDOUT_MECHANISMS[mech-2],condition=CONDITIONS[cond],
             truth=truth,predictions=answers,task_probabilities=probabilities,
             receipts=receipts,public_calibration_anchor_count=len(ref)))
    score={a:recount(rows,a) for a in ARMS}
    by_mech={m:{a:recount([r for r in rows if r["mechanism"]==m],a)
                 for a in ARMS} for m in HELDOUT_MECHANISMS}
    by_cond={c:{a:recount([r for r in rows if r["condition"]==c],a)
                 for a in ARMS} for c in CONDITIONS}
    fair=ARMS[1:6]
    best=max(score[a]["accuracy"] for a in fair)
    gain=score["learned_anchor_latent"]["accuracy"]-best
    ablation=score["learned_anchor_latent"]["accuracy"]-score["learned_first_masked"]["accuracy"]
    no_mech_regression=all(by_mech[m]["learned_anchor_latent"]["correct"]>=
       max(by_mech[m][a]["correct"] for a in fair) for m in HELDOUT_MECHANISMS)
    qualified=gain>=.02 and ablation>0 and no_mech_regression
    return dict(schema="yggdrasil.f44.public-anchor-transfer.trainonly.v1",
      stage="FRESH_TRAIN_ONLY_HELDOUT_MECHANISMS_NOT_PRIMARY_ORIGINAL",
      fit_seeds=[FIT.start,FIT.stop],diagnostic_seeds=[DIAGNOSTIC.start,DIAGNOSTIC.stop],
      reserved_seeds=[RESERVED.start,RESERVED.stop],families=list(FAMILIES),
      reserved_families=list(RESERVED_FAMILIES),
      train_mechanisms=list(TRAIN_MECHANISMS),heldout_mechanisms=list(HELDOUT_MECHANISMS),
      questions=len(rows),train_examples=model.num_examples,
      packed_coefficient_bytes=len(model.packed_bytes()),
      packed_bytes_do_not_measure_native_heap=True,fit_bandwidth=bandwidth,
      scores=score,by_mechanism=by_mech,by_condition=by_cond,
      gain_over_strongest_fair=gain,masked_first_gain=ablation,
      no_heldout_mechanism_regression=no_mech_regression,
      elapsed_seconds=time.perf_counter()-start,rows=rows,
      verdict="TRAIN_ONLY_HELDOUT_TRANSFER_QUALIFIED" if qualified else "TRAIN_ONLY_HELDOUT_TRANSFER_NOT_QUALIFIED",
      diagnostic_labels_never_used_for_fit=True,
      latent_condition_not_passed_to_action=True,
      independent_F3_custody=False,primary_original_not_executed=True,
      native_576_byte_residency_qualified=False,accepted_ref_mutation=False,paid_api_calls=0)

if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

"""Y-F40: train a task-conditional credibility policy when first-channel marginal
variance is deliberately matched across reliable and misleading regimes.

Source-private truth/mode/regime are evaluator-only. Inference sees PUBLIC
labeled calibration readings and the first bought target value. Train-only
supervision selects which of two matched-budget acquisition choices produces
a lower final bit-prediction loss. Fresh unseen family IDs; no F3 authority.
"""
from __future__ import annotations
import json,math,random
from collections import Counter
TRAIN=range(301800,301824);TRAIN_FAMILIES=(330,331,332)
EVAL=range(302800,302816);EVAL_FAMILIES=(334,335,336,337)
RESERVED=range(303800,303816);RESERVED_FAMILIES=(340,341,342,343)
CONDITIONS=("mode_coupled","mode_decoupled")
MECHANISMS=("normal","anticorrelated_channel")
ARMS=("learned_contextual_credibility","conditional_empirical_Brier",
      "fitted_Gaussian_Bayesian","fixed_public_crosscovariance",
      "fixed_variance","static","first_masked","privileged_oracle_unfair")
ANCHORS=24;WEIGHTS=8;PAID=2
def sigmoid(z):return 1/(1+math.exp(-max(-25,min(25,z))))
def rand(seed,family,role,mechanism,condition,episode):
    if not ((seed in TRAIN and family in TRAIN_FAMILIES) or
            (seed in EVAL and family in EVAL_FAMILIES)):
        raise ValueError("reserved source ID denied")
    return random.Random(91007+seed*101093+family*27817+role*601+mechanism*193+condition*711+episode*47)
def source(seed,family,role,mechanism,condition,episode):
    r=rand(seed,family,role,mechanism,condition,episode)
    truth=r.randrange(2);mode=r.randrange(2)
    pol=1 if (family+mechanism)%2 else -1
    # Same bimodal first-sensor *marginal* in both conditions.
    first_sign=(2*mode-1) if condition==0 else r.choice((-1,1))
    first=min(1.,max(0.,.5+pol*first_sign*.30+r.gauss(0,.075)))
    values=[first]
    for j in (1,2,3):
        useful=(j==1 and mode==0) or (j==2 and mode==1)
        amplitude=.385 if useful else .035
        noise=.105 if useful else .225
        if j==3:amplitude=.19;noise=.18
        if mechanism==1 and j==2:
            amplitude=-amplitude;noise=.15 if useful else .23
        if mechanism==1 and j==3:
            amplitude=.24;noise=.15
        v=min(1,max(0,.5+(2*truth-1)*amplitude+r.gauss(0,noise)))
        values.append(v)
    return truth,mode,tuple(values),pol
def refs(seed,family,mechanism,condition):
    return tuple((truth,values) for i in range(ANCHORS)
        for truth,mode,values,pol in [source(seed,family,i%3,mechanism,condition,50000+i*13)])
def correlations(references):
    return tuple(sum((2*y-1)*(2*v[j]-1) for y,v in references)/len(references) for j in range(4))
def bit_probability(value,j,corr):
    strength=(2*value-1)*corr[j]/(abs(corr[j])+.05)
    return sigmoid(5*strength)
def calc_brier(first,refs,corr):
    losses=[]
    for j in (1,2,3):
        numerator=den=0.
        for truth,values in refs:
            w=math.exp(-9*abs(values[0]-first))
            p=bit_probability(values[j],j,corr)
            numerator+=w*(p-truth)**2;den+=w
        losses.append(numerator/max(den,1e-12))
    return tuple(losses)
def public_features(first,pol,refs,corr):
    sign=(first-.5)*pol
    firsts=[v[0] for truth,v in refs]
    mu=sum(firsts)/len(firsts)
    variance=sum((f-mu)**2 for f in firsts)/len(firsts)
    errors1=[];errors2=[];groups=[]
    for truth,values in refs:
        p1=bit_probability(values[1],1,corr);p2=bit_probability(values[2],2,corr)
        e1=(p1-truth)**2;e2=(p2-truth)**2
        errors1.append(e1);errors2.append(e2)
        groups.append(((values[0]-.5)*pol,e1-e2))
    cross=sum(g[0]*g[1] for g in groups)/len(groups)
    brier=calc_brier(first,refs,corr)
    return (1.,cross*5,variance*10,sign*2,abs(sign)*2,
            brier[1]-brier[0],abs(corr[1])-abs(corr[2]),corr[3])
def bayes_params(samples):
    modes=[[],[]]
    for mode,z in samples:modes[mode].append(z)
    means=[sum(a)/len(a) for a in modes]
    vars_=[max(.004,sum((v-means[i])**2 for v in modes[i])/len(modes[i])) for i in (0,1)]
    return means,vars_
def gaussian_choice(first,pol,params):
    means,vars_=params;v=(first-.5)*pol*2
    terms=[-.5*math.log(vars_[j])-(v-means[j])**2/(2*vars_[j]) for j in (0,1)]
    return 1 if terms[0]>=terms[1] else 2
def choose(method,first,pol,refs,corr,weights,gaussian):
    if method=="static" or method=="first_masked":
        return max((1,2,3),key=lambda j:(abs(corr[j]),-j))
    if method=="conditional_empirical_Brier":
        loss=calc_brier(first,refs,corr)
        return (1,2,3)[min(range(3),key=lambda i:(loss[i],i))]
    if method=="fitted_Gaussian_Bayesian":
        return gaussian_choice(first,pol,gaussian)
    if method=="fixed_variance":
        a=[v[0] for y,v in refs]
        mu=sum(a)/len(a);var=sum((v-mu)**2 for v in a)/len(a)
        return gaussian_choice(first,pol,gaussian) if var>.07 else choose("conditional_empirical_Brier",first,pol,refs,corr,weights,gaussian)
    feats=public_features(first,pol,refs,corr)
    if method=="fixed_public_crosscovariance":
        trust=abs(feats[1])>.1
    elif method=="learned_contextual_credibility":
        trust=sigmoid(sum(w*x for w,x in zip(weights,feats)))>=.5
    else:raise ValueError("unknown policy")
    return gaussian_choice(first,pol,gaussian) if trust else choose("conditional_empirical_Brier",first,pol,refs,corr,weights,gaussian)
def train():
    samples=[];gaussian_rows=[]
    for seed in TRAIN:
      for family in TRAIN_FAMILIES:
       for mech in range(2):
        for condition in range(2):
            r=refs(seed,family,mech,condition);corr=correlations(r)
            for role in range(3):
                truth,mode,v,pol=source(seed,family,role,mech,condition,9000+role)
                gaussian_rows.append((mode,(v[0]-.5)*pol*2))
    gaussian=bayes_params(gaussian_rows)
    for seed in TRAIN:
      for family in TRAIN_FAMILIES:
       for mech in range(2):
        for condition in range(2):
            r=refs(seed,family,mech,condition);corr=correlations(r)
            for role in range(3):
                truth,mode,v,pol=source(seed,family,role,mech,condition,9000+role)
                b=choose("conditional_empirical_Brier",v[0],pol,r,corr,[],gaussian)
                g=choose("fitted_Gaussian_Bayesian",v[0],pol,r,corr,[],gaussian)
                if b==g:continue
                err_b=(bit_probability(v[b],b,corr)-truth)**2
                err_g=(bit_probability(v[g],g,corr)-truth)**2
                if abs(err_b-err_g)<1e-8:continue
                # TRAIN ONLY: label posterior preference by downstream bit loss.
                samples.append((public_features(v[0],pol,r,corr),float(err_g<err_b)))
    w=[0.]*WEIGHTS
    for _ in range(200):
        gradients=[0.]*WEIGHTS
        for x,label in samples:
            err=sigmoid(sum(a*b for a,b in zip(w,x)))-label
            for j in range(WEIGHTS):gradients[j]+=err*x[j]
        for j in range(WEIGHTS):
            w[j]-=.17*(gradients[j]/max(1,len(samples))+.005*w[j])
    return w,gaussian,len(samples),len(gaussian_rows)
class Port:
    def __init__(self,vals):self._vals=vals;self.trace=[]
    def buy(self,j):
        if len(self.trace)>=PAID or any(k==j for k,val in self.trace):
            raise ValueError("duplicate/third purchase denied")
        v=self._vals[j];self.trace.append((j,v));return v
def task(bits,family):
    return bool(bits[0]^bits[1]^bits[2]) if family%2==0 else sum(bool(x) for x in bits)>=2
def scores(rows,a):
    n=len(rows)
    correct=sum(row["answers"][a]==row["truth"] for row in rows)
    fp=sum(bool(row["answers"][a]) and not row["truth"] for row in rows)
    fn=sum(not bool(row["answers"][a]) and row["truth"] for row in rows)
    return dict(total=n,correct=correct,accuracy=correct/n,fp=fp,fn=fn)
def run():
    assert not set(TRAIN)&set(EVAL) and not set(EVAL)&set(RESERVED)
    assert not set(TRAIN_FAMILIES)&set(EVAL_FAMILIES)
    assert not set(EVAL_FAMILIES)&set(RESERVED_FAMILIES)
    w,gaussian,ntrained,ngaussian=train()
    rows=[];first_switch=first_interventions=0
    for seed in EVAL:
      for family in EVAL_FAMILIES:
       for mech in range(2):
        for condition in range(2):
            r=refs(seed,family,mech,condition);corr=correlations(r)
            targets=[source(seed,family,role,mech,condition,9000+role) for role in range(3)]
            truth=task([y for y,mode,v,pol in targets],family)
            answers={"privileged_oracle_unfair":truth};receipts={}
            for method in ARMS[:-1]:
                bits=[];traces=[]
                for true_bit,latent,values,pol in targets:
                    port=Port(values);first=port.buy(0)
                    j=choose(method,first,pol,r,corr,w,gaussian)
                    value=port.buy(j)
                    if port.trace[0][0]!=0 or len(port.trace)!=2:raise ValueError("physical custody")
                    bits.append(bit_probability(value,j,corr)>=.5)
                    traces.append(tuple(j for j,v in port.trace))
                answers[method]=task(bits,family);receipts[method]=traces
            pol=targets[0][3]
            for a,b in ((.2,.8),(.35,.65)):
                first_switch+=choose("learned_contextual_credibility",a,pol,r,corr,w,gaussian)!=choose("learned_contextual_credibility",b,pol,r,corr,w,gaussian)
                first_interventions+=1
            rows.append(dict(seed=seed,family=family,mechanism=MECHANISMS[mech],
                condition=CONDITIONS[condition],truth=truth,answers=answers,receipts=receipts,
                public_anchors=len(r),reference_first_variance=sum((v[0]-sum(vv[0] for y,vv in r)/len(r))**2 for y,v in r)/len(r)))
    summary={a:scores(rows,a) for a in ARMS}
    strata={name:{a:scores([r for r in rows if r["mechanism"]==name],a) for a in ARMS} for name in MECHANISMS}
    conditions={name:{a:scores([r for r in rows if r["condition"]==name],a) for a in ARMS} for name in CONDITIONS}
    fair=("conditional_empirical_Brier","fitted_Gaussian_Bayesian","fixed_public_crosscovariance","fixed_variance","static","first_masked")
    gap=summary["learned_contextual_credibility"]["accuracy"]-max(summary[a]["accuracy"] for a in fair)
    robust=all(strata[m]["learned_contextual_credibility"]["accuracy"]>=max(strata[m][a]["accuracy"] for a in fair) for m in MECHANISMS)
    qualifies=gap>=.02 and robust and first_switch>0 and summary["learned_contextual_credibility"]["correct"]>summary["first_masked"]["correct"]
    return dict(schema="yggdrasil.f40.decision-conditioned-trust.trainonly.v1",
        phase="FRESH_TRAIN_ONLY_EVALUATION_NOT_PRIMARY_ORIGINAL",
        train_seeds=[TRAIN.start,TRAIN.stop],train_families=TRAIN_FAMILIES,
        eval_seeds=[EVAL.start,EVAL.stop],eval_families=EVAL_FAMILIES,
        reserved_original_seeds=[RESERVED.start,RESERVED.stop],reserved_original_families=RESERVED_FAMILIES,
        training_preference_examples=ntrained,training_gaussian_examples=ngaussian,
        learned_weights=w,learned_weights_bytes=WEIGHTS*8,physical_reads_per_role=2,
        native_core_memory_not_independently_measured=True,public_calibration_bytes_per_case=ANCHORS*5*8,
        first_read_action_switch_rate=first_switch/first_interventions,questions=len(rows),
        scores=summary,by_mechanism=strata,by_condition=conditions,rows=rows,
        hidden_source_condition_or_mode_not_given_to_policy=True,source_independent_F3=False,
        original_not_executed=True,accepted_ref_mutation=False,paid_api_calls=0,
        verdict="TRAIN_ONLY_DECISION_TRUST_GAIN" if qualifies else "TRAIN_ONLY_DECISION_TRUST_NO_QUALIFIED_GAIN")
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

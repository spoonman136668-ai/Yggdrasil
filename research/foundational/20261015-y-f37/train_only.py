"""Y-F37: train-only decision-calibrated latent reliability posterior.

Learn the latent mode posterior from public-calibration descriptors and the first
paid reading. Unlike Y-F36, optimize a differentiable expected *downstream
bit-decision loss* in addition to latent mode CE. Gaussian Bayesian receives
the same TRAIN latent labels; no evaluation modes/truth/unpurchased channels are
available to acquisition. Synthetic development, NOT independent F3 custody.
"""
from __future__ import annotations
import json,math,random
from collections import Counter
TRAIN=range(271800,271840);TRAIN_FAMILIES=(250,251,252)
EVAL=range(272800,272816);EVAL_FAMILIES=(254,255,256,257)
RESERVED=range(273800,273816);RESERVED_FAMILIES=(260,261,262,263)
CONDITIONS=("normal","reversed_polarity","weak_hint","uninformative_hint")
MECHANISMS=("mode_shift","anti_correlated_aux")
METHODS=("learned_decision","gaussian_Bayesian","public_polarity_Bayesian","conditional_empirical_Brier","calibrated_static","masked_first","privileged_oracle")
ANCHORS=16;NFEATURES=6;READS=2;NATIVE_CAP=576
def sig(z):
    return 1/(1+math.exp(-max(-25,min(25,z))))
def rng(seed,fam,role,condition,mechanism,episode):
    if not ((seed in TRAIN and fam in TRAIN_FAMILIES) or (seed in EVAL and fam in EVAL_FAMILIES)):
        raise ValueError("source ID denied (including reserved first-use)")
    return random.Random(51039+seed*107011+fam*17123+role*719+condition*947+mechanism*271+episode*47)
def source(seed,fam,role,condition,mechanism,episode):
    r=rng(seed,fam,role,condition,mechanism,episode)
    truth=r.randrange(2);mode=r.randrange(2);bit=2*truth-1
    polarity=(-1 if (fam+condition+mechanism)%2 else 1)*(-1 if condition==1 else 1)
    strength=.31 if condition in (0,1) else .14 if condition==2 else .006
    first=min(1,max(0,.5+strength*polarity*(2*mode-1)+r.gauss(0,.105 if condition<2 else .175)))
    vals=[first]
    for j in (1,2,3):
        good=(j==1 and mode==0) or (j==2 and mode==1)
        efficacy=.39 if good else .035
        noise=.12 if good else .21
        if j==3:efficacy=.18;noise=.16
        if mechanism==1 and j==2:efficacy=-efficacy;noise=.17 if good else .23
        if mechanism==1 and j==3:efficacy=.25;noise=.145
        if condition==2 and j==1:noise+=.055
        vals.append(min(1,max(0,.5+bit*efficacy+r.gauss(0,noise))))
    return truth,mode,tuple(vals),polarity
def anchors(seed,fam,cond,mechanism):
    return tuple((truth,vals) for i in range(ANCHORS)
        for truth,mode,vals,pol in [source(seed,fam,i%3,cond,mechanism,50000+i*7)])
def reliability(a):
    return tuple(sum((2*y-1)*(2,v[j]-1)[1] for y,v in a)/len(a) for j in range(4))
def public_reliability(a):
    return tuple(sum((2*y-1)*(2*v[j]-1) for y,v in a)/len(a) for j in range(4))
def bit_probability(value,j,corr):
    z=(2*value-1)*corr[j]/(abs(corr[j])+.05)
    return sig(5*z)
def features(first,polarity,corr):
    z=polarity*(2*first-1)
    return (1.,z,abs(z),z*abs(z),abs(corr[1])-abs(corr[2]),corr[3])
def train():
    records=[];mode_reliability=[[0,0] for _ in range(6)];mode_samples=[[],[]]
    for seed in TRAIN:
      for fam in TRAIN_FAMILIES:
       for cond in range(4):
        for mechanism in range(2):
          refs=anchors(seed,fam,cond,mechanism);corr=public_reliability(refs)
          for role in range(3):
            truth,mode,vals,pol=source(seed,fam,role,cond,mechanism,9000+role)
            x=features(vals[0],pol,corr)
            mode_samples[mode].append((2*vals[0]-1)*pol)
            losses=[]
            for j in (1,2,3):
                p=bit_probability(vals[j],j,corr)
                losses.append(-truth*math.log(max(1e-7,p))-(1-truth)*math.log(max(1e-7,1-p)))
                index=mode*3+j-1
                mode_reliability[index][0]+=(p>=.5)==bool(truth)
                mode_reliability[index][1]+=1
            records.append((x,mode,losses))
    quality=[[((mode_reliability[mode*3+j][0]+1)/(mode_reliability[mode*3+j][1]+2))
             for j in range(3)] for mode in (0,1)]
    means=[sum(t)/len(t) for t in mode_samples]
    variances=[max(.006,sum((x-means[i])**2 for x in mode_samples[i])/len(mode_samples[i])) for i in (0,1)]
    weights=[0.]*NFEATURES
    # A differentiable objective: mode cross entropy + expected future bit
    # logloss of a soft sensor choice according to mode-conditioned utilities.
    for epoch in range(90):
        gradient=[0.]*NFEATURES
        for x,mode,losses in records:
            z=sum(a*b for a,b in zip(weights,x))
            p=sig(z)
            value=[(1-p)*quality[0][j]+p*quality[1][j] for j in range(3)]
            temperature=6.
            m=max(value);e=[math.exp(temperature*(v-m)) for v in value];den=sum(e)
            probs=[v/den for v in e]
            expected=sum(pi*li for pi,li in zip(probs,losses))
            derivative=sum(probs[j]*(losses[j]-expected)*temperature*(quality[1][j]-quality[0][j]) for j in range(3))
            dz=(p-mode)*.15 + derivative*p*(1-p)
            for i in range(NFEATURES):gradient[i]+=dz*x[i]
        for i in range(NFEATURES):
            weights[i]-=.18*(gradient[i]/len(records)+.0007*weights[i])
    return weights,quality,means,variances,len(records)
def posterior(method,first,pol,corr,weights,means,variances):
    z=(2*first-1)*pol
    if method in ("learned_decision","masked_first"):
        x=features(.5 if method=="masked_first" else first,pol,corr)
        return sig(sum(a*b for a,b in zip(weights,x)))
    if method=="gaussian_Bayesian":
        terms=[-.5*math.log(variances[i])-(z-means[i])**2/(2*variances[i]) for i in (0,1)]
        return sig(terms[1]-terms[0])
    if method=="public_polarity_Bayesian":return float(z>=0)
    raise ValueError("unregistered posterior method")
def choose(method,first,pol,corr,refs,weights,quality,means,variances):
    if method=="calibrated_static":return max((1,2,3),key=lambda j:(abs(corr[j]),-j))
    if method=="conditional_empirical_Brier":
        losses=[]
        for j in (1,2,3):
            weighted=mass=0.
            for y,src in refs:
                w=math.exp(-9*abs(src[0]-first))
                p=bit_probability(src[j],j,corr)
                weighted+=w*(p-y)**2;mass+=w
            losses.append(weighted/max(mass,1e-12))
        return (1,2,3)[min(range(3),key=lambda i:(losses[i],i))]
    p=posterior(method,first,pol,corr,weights,means,variances)
    utility=[(1-p)*quality[0][j]+p*quality[1][j]+.04*abs(corr[j+1]) for j in range(3)]
    return (1,2,3)[max(range(3),key=lambda i:(utility[i],-i))]
class Port:
    def __init__(self,values):self._values=values;self.trace=[]
    def buy(self,j):
        if j in [v[0] for v in self.trace] or len(self.trace)>=READS:raise ValueError("read-budget violation")
        value=self._values[j];self.trace.append((j,value));return value
def task(bits,fam):
    return bool(bits[0]^bits[1]^bits[2]) if fam%2==0 else sum(bool(z) for z in bits)>=2
def tally(rows,name):
    n=len(rows);correct=sum(r["answers"][name]==r["truth"] for r in rows)
    fp=sum(bool(r["answers"][name]) and not r["truth"] for r in rows)
    fn=sum(not bool(r["answers"][name]) and r["truth"] for r in rows)
    return dict(correct=correct,total=n,accuracy=correct/n,fp=fp,fn=fn)
def run():
    if (set(TRAIN)&set(EVAL) or set(EVAL)&set(RESERVED) or
        set(TRAIN_FAMILIES)&set(EVAL_FAMILIES) or set(EVAL_FAMILIES)&set(RESERVED_FAMILIES)):
        raise ValueError("source identity collision")
    weights,quality,means,variances,train_count=train()
    rows=[];calibration={a:0. for a in ("learned_decision","gaussian_Bayesian","public_polarity_Bayesian")};log_n=0
    switch=total_switch=0
    for seed in EVAL:
      for fam in EVAL_FAMILIES:
       for cond in range(4):
        for mechanism in range(2):
            refs=anchors(seed,fam,cond,mechanism);corr=public_reliability(refs)
            targets=[source(seed,fam,role,cond,mechanism,9000+role) for role in range(3)]
            true=task([y for y,mode,src,pol in targets],fam)
            answers={"privileged_oracle":true};receipts={}
            for method in METHODS[:-1]:
                bits=[];trace=[]
                for bit,mode,values,pol in targets:
                    port=Port(values);first=port.buy(0)
                    j=choose(method,first,pol,corr,refs,weights,quality,means,variances)
                    second=port.buy(j)
                    if len(port.trace)!=2 or port.trace[0][0]!=0:raise ValueError("not two sequential purchases")
                    bits.append(bit_probability(second,j,corr)>=.5)
                    trace.append([port.trace[0][0],port.trace[1][0]])
                    if method in calibration:
                        p=max(1e-8,min(1-1e-8,posterior(method,first,pol,corr,weights,means,variances)))
                        calibration[method]-=mode*math.log(p)+(1-mode)*math.log(1-p)
                        if method=="learned_decision":log_n+=1
                answers[method]=task(bits,fam);receipts[method]=trace
            pol=targets[0][3]
            for low,high in ((.2,.8),(.35,.65)):
                switch+=choose("learned_decision",low,pol,corr,refs,weights,quality,means,variances)!=choose("learned_decision",high,pol,corr,refs,weights,quality,means,variances)
                total_switch+=1
            rows.append(dict(seed=seed,family=fam,condition=CONDITIONS[cond],mechanism=MECHANISMS[mechanism],
                truth=true,answers=answers,purchased_sensors=receipts,public_anchors=len(refs)))
    summary={name:tally(rows,name) for name in METHODS}
    by_mechanism={m:{name:tally([r for r in rows if r["mechanism"]==m],name) for name in METHODS} for m in MECHANISMS}
    fair=("gaussian_Bayesian","public_polarity_Bayesian","conditional_empirical_Brier","calibrated_static")
    gain=summary["learned_decision"]["accuracy"]-max(summary[a]["accuracy"] for a in fair)
    robust=all(by_mechanism[m]["learned_decision"]["accuracy"]>=max(by_mechanism[m][a]["accuracy"] for a in fair) for m in MECHANISMS)
    passed=gain>=.02 and robust and switch>0 and summary["learned_decision"]["correct"]>summary["masked_first"]["correct"]
    return dict(schema="yggdrasil.f37.decision-calibrated.trainonly.v1",
        stage="DEVELOPMENT_TRAIN_ONLY_NO_PRIMARY_ORIGINAL",
        train_seeds=[TRAIN.start,TRAIN.stop],train_families=TRAIN_FAMILIES,
        eval_seeds=[EVAL.start,EVAL.stop],eval_families=EVAL_FAMILIES,
        reserved_original_seeds=[RESERVED.start,RESERVED.stop],reserved_original_families=RESERVED_FAMILIES,
        train_count=train_count,learned_weights=weights,mode_source_quality=quality,
        gaussian_control_means=means,gaussian_control_variances=variances,
        latent_mode_heldout_logloss={a:v/log_n for a,v in calibration.items()},
        native_coefficients_bytes=(NFEATURES+6+4)*8,native_core_budget=576,
        calibration_external_bytes_per_case=ANCHORS*5*8,physical_paid_reads_per_role=2,
        first_read_causal_action_switch_rate=switch/total_switch,questions=len(rows),
        scores=summary,by_mechanism=by_mechanism,rows=rows,
        source_independently_born_F3=False,primary_original_not_executed=True,accepted_ref_mutation=False,
        verdict="TRAIN_ONLY_DECISION_CALIBRATED_LEARNED_GAIN" if passed else "TRAIN_ONLY_DECISION_CALIBRATED_NO_QUALIFIED_GAIN")
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

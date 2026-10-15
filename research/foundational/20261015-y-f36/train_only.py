"""Y-F36 TRAIN-only latent reliability posterior over sensor mechanisms.

Train a genuine logistic posterior P(hidden source mode | public calibration,
public polarity, FIRST physically purchased reading), plus expected per-mode
source predictive correctness. At evaluation mode/truth are evaluator-only.
All fair policies buy the same two target channels; strong Gaussian Bayesian
posterior is fitted on exactly the same TRAIN mode examples. Project-authored
synthetic development is NOT independent F3 custody.
"""
import json,math,random
from collections import defaultdict

TRAIN=range(251800,251824);TRAIN_FAMILIES=(220,221,222)
EVAL=range(252800,252816);EVAL_FAMILIES=(224,225,226,227)
RESERVED=range(253800,253816);RESERVED_FAMILIES=(230,231,232,233)
CONDITIONS=("normal","reversed_polarity","weak_hint","uninformative_hint")
MECHANISMS=("mode_switched","anticorrelated_auxiliary")
ARMS=("learned_posterior","gaussian_Bayesian","polarity_Bayesian","conditional_empirical_Brier","calibrated_static","fixed","masked_first","privileged_oracle")
ANCHORS=16; NFEATURES=6; NATIVE_BYTES=576; READS=2

def rng(seed,fam,role,condition,mechanism,episode):
    if not ((seed in TRAIN and fam in TRAIN_FAMILIES) or
            (seed in EVAL and fam in EVAL_FAMILIES)):
        raise ValueError("unauthorized seed and family, including reserved originals")
    return random.Random(seed*101071+fam*17113+role*827+condition*743+mechanism*199+episode*47+3311)

def source(seed,fam,role,condition,mechanism,episode):
    r=rng(seed,fam,role,condition,mechanism,episode)
    truth=r.randrange(2);mode=r.randrange(2)
    sign=2*truth-1
    polarity=-1 if (fam+condition+mechanism)%2 else 1
    if condition==1:polarity*=-1
    amp=.30 if condition in (0,1) else .16 if condition==2 else .005
    first=min(1.,max(0.,.5+amp*polarity*(2*mode-1)+r.gauss(0,.11 if condition<2 else .18)))
    vals=[first]
    for j in (1,2,3):
        selected=(j==1 and mode==0) or (j==2 and mode==1)
        strength=.38 if selected else .04
        noise=.13 if selected else .21
        if j==3:strength=.20;noise=.16
        if mechanism==1 and j==2:strength=-strength;noise=.17 if selected else .24
        if mechanism==1 and j==3:strength=.24;noise=.14
        if condition==2 and j==1:noise+=.05
        vals.append(min(1.,max(0.,.5+sign*strength+r.gauss(0,noise))))
    return truth,mode,tuple(vals),polarity

def anchors(seed,fam,condition,mechanism):
    # Public reference has known truth, no target modes. Both learned and
    # control policies receive exactly the same anchor labels/measurements.
    return tuple((truth,vals) for i in range(ANCHORS)
            for truth,mode,vals,polarity in [source(seed+0,fam,i%3,condition,mechanism,50000+i*7)])

def public_reliability(reference):
    return [sum((2*y-1)*(2*v[j]-1) for y,v in reference)/len(reference) for j in range(4)]

def bit_estimate(reading,j,reliability):
    correlation=reliability[j]
    z=(2*reading-1)*correlation/(abs(correlation)+.05)
    return 1/(1+math.exp(-max(-20,min(20,5*z))))

def features(first,polarity,reference_reliability):
    z=(2*first-1)*polarity
    return (1.,z,abs(z),z*abs(z),abs(reference_reliability[1])-abs(reference_reliability[2]),reference_reliability[3])

def sigmoid(x):
    return 1/(1+math.exp(-max(-25,min(25,x))))

def train():
    training=[];qualities=[[0.,0.] for _ in range(6)]; gaussian=[[],[]]
    for seed in TRAIN:
      for fam in TRAIN_FAMILIES:
       for cond in range(4):
        for mechanism in range(2):
            reference=anchors(seed,fam,cond,mechanism)
            r=public_reliability(reference)
            for role in range(3):
                truth,mode,vals,pol=source(seed,fam,role,cond,mechanism,9000+role)
                training.append((features(vals[0],pol,r),mode))
                gaussian[mode].append((2*vals[0]-1)*pol)
                for j in (1,2,3):
                    p=bit_estimate(vals[j],j,r)
                    # train expected downstream bit correctness, not hardcoded
                    # channel utility; private mode appears in TRAIN only.
                    correctly=(p>=.5)==bool(truth)
                    index=mode*3+j-1
                    qualities[index][0]+=int(correctly)
                    qualities[index][1]+=1
    weights=[0.]*NFEATURES
    for epoch in range(140):
        grad=[0.]*NFEATURES
        for x,y in training:
            e=sigmoid(sum(a*b for a,b in zip(weights,x)))-y
            for i in range(NFEATURES):grad[i]+=e*x[i]
        for i in range(NFEATURES):weights[i]-=.24*(grad[i]/len(training)+.0005*weights[i])
    q=[[((qualities[mode*3+j][0]+1)/(qualities[mode*3+j][1]+2)) for j in range(3)] for mode in (0,1)]
    means=[sum(v)/len(v) for v in gaussian]
    variances=[max(.005,sum((v-means[mode])**2 for v in gaussian[mode])/len(gaussian[mode])) for mode in (0,1)]
    return weights,q,means,variances,len(training)

def posterior(first,polarity,r,weights,means,variances,method):
    z=(2*first-1)*polarity
    if method in ("learned_posterior","masked_first"):
        x=features(.5 if method=="masked_first" else first,polarity,r)
        return sigmoid(sum(a*b for a,b in zip(weights,x)))
    if method=="gaussian_Bayesian":
        scores=[-.5*math.log(variances[i])-(z-means[i])**2/(2*variances[i]) for i in (0,1)]
        return sigmoid(scores[1]-scores[0])
    if method=="polarity_Bayesian":
        return 1. if z>=0 else 0.
    raise ValueError(method)

def choose(method,first,polarity,r,reference,weights,q,means,variances):
    candidates=(1,2,3)
    if method=="fixed":return 3
    if method=="calibrated_static":return max(candidates,key=lambda j:(abs(r[j]),-j))
    if method=="conditional_empirical_Brier":
        risk=[]
        for j in candidates:
            error=weight=0.
            for truth,measurements in reference:
                w=math.exp(-9*abs(measurements[0]-first))
                p=bit_estimate(measurements[j],j,r)
                error+=w*(p-truth)**2
                weight+=w
            risk.append(error/max(1e-12,weight))
        return candidates[min(range(3),key=lambda idx:(risk[idx],idx))]
    p=posterior(first,polarity,r,weights,means,variances,method)
    scores=[]
    for j in candidates:
        # Train-only expected downstream reliability for each latent mode,
        # adjusted by current publicly calibrated sensor's reliability.
        value=(1-p)*q[0][j-1]+p*q[1][j-1]
        scores.append(value+.04*abs(r[j]))
    return candidates[max(range(3),key=lambda idx:(scores[idx],-idx))]

class Bought:
    def __init__(self):
        self.observations=[]
    def take(self,channels,j):
        if j in [r[0] for r in self.observations]:raise ValueError("duplicate purchase")
        if len(self.observations)>=READS:raise ValueError("over budget")
        self.observations.append((j,channels[j]))
        return channels[j]

def task(bits,fam):
    return bool(bits[0]^bits[1]^bits[2]) if fam%2==0 else sum(bool(v) for v in bits)>=2

def metrics(rows,arm):
    n=len(rows);correct=sum(r["answers"][arm]==r["truth"] for r in rows)
    fp=sum(bool(r["answers"][arm]) and not r["truth"] for r in rows)
    fn=sum(not bool(r["answers"][arm]) and r["truth"] for r in rows)
    return dict(correct=correct,total=n,accuracy=correct/n,fp=fp,fn=fn)

def run():
    if set(TRAIN)&set(EVAL) or set(TRAIN)&set(RESERVED) or set(EVAL)&set(RESERVED):
        raise ValueError("consumed source identities")
    weights,q,means,variances,ntrain=train()
    rows=[];mode_logloss={"learned_posterior":0.,"gaussian_Bayesian":0.,"polarity_Bayesian":0.};mode_n=0
    switch_count=switch_total=0
    for seed in EVAL:
      for fam in EVAL_FAMILIES:
       for cond in range(4):
        for mechanism in range(2):
            ref=anchors(seed,fam,cond,mechanism)
            r=public_reliability(ref)
            targets=[source(seed,fam,role,cond,mechanism,9000+role) for role in range(3)]
            oracle=task([truth for truth,mode,channels,pol in targets],fam)
            predictions={"privileged_oracle":oracle};receipts={}
            for method in ARMS[:-1]:
                bits=[];traces=[]
                for truth,mode,channels,polarity in targets:
                    bought=Bought();first=bought.take(channels,0)
                    j=choose(method,first,polarity,r,ref,weights,q,means,variances)
                    second=bought.take(channels,j)
                    assert len(bought.observations)==2 and bought.observations[0][0]==0
                    bits.append(bit_estimate(second,j,r)>=.5)
                    traces.append([v[0] for v in bought.observations])
                    if method in mode_logloss:
                        prob=posterior(first,polarity,r,weights,means,variances,method)
                        prob=max(1e-7,min(1-1e-7,prob))
                        mode_logloss[method]-=mode*math.log(prob)+(1-mode)*math.log(1-prob)
                        if method=="learned_posterior":mode_n+=1
                predictions[method]=task(bits,fam)
                receipts[method]=traces
            pol=targets[0][3]
            for low,high in ((.2,.8),(.35,.65)):
                switch_count+=choose("learned_posterior",low,pol,r,ref,weights,q,means,variances)!=choose("learned_posterior",high,pol,r,ref,weights,q,means,variances)
                switch_total+=1
            rows.append(dict(seed=seed,family=fam,condition=CONDITIONS[cond],mechanism=MECHANISMS[mechanism],
                truth=oracle,answers=predictions,purchased_sensor_receipts=receipts,public_anchor_count=len(ref)))
    scores={a:metrics(rows,a) for a in ARMS}
    mechanism_scores={name:{a:metrics([row for row in rows if row["mechanism"]==name],a) for a in ARMS} for name in MECHANISMS}
    fair=("gaussian_Bayesian","polarity_Bayesian","conditional_empirical_Brier","calibrated_static","fixed")
    best=max(scores[a]["accuracy"] for a in fair)
    gain=scores["learned_posterior"]["accuracy"]-best
    sturdy=all(mechanism_scores[m]["learned_posterior"]["accuracy"]>=max(mechanism_scores[m][a]["accuracy"] for a in fair) for m in MECHANISMS)
    switches=switch_count/switch_total
    advance=gain>=.02 and sturdy and switches>0 and scores["learned_posterior"]["correct"]>scores["masked_first"]["correct"]
    return dict(schema="yggdrasil.f36.latent-mode-posterior.trainonly.v1",
        stage="NEW_TRAIN_ONLY_NOT_PRIMARY_ORIGINAL",
        train_seeds=[TRAIN.start,TRAIN.stop],train_families=TRAIN_FAMILIES,
        eval_seeds=[EVAL.start,EVAL.stop],eval_families=EVAL_FAMILIES,
        reserved_primary_seeds=[RESERVED.start,RESERVED.stop],
        reserved_primary_families=RESERVED_FAMILIES,
        learned_posterior_weights=weights,train_derived_mode_source_utilities=q,
        gaussian_control_means=means,gaussian_control_variances=variances,
        train_source_examples=ntrain,source_mode_predictive_logloss={k:v/mode_n for k,v in mode_logloss.items()},
        native_coefficient_bytes=(NFEATURES+2*3+2*2)*8,native_core_limit_bytes=NATIVE_BYTES,
        Python_runtime_heap_not_bounded=True,external_calibration_bytes_per_question=ANCHORS*5*8,
        physical_target_reads_per_role=READS,questions=len(rows),
        first_read_counterfactual_action_switch_rate=switches,
        hidden_mode_not_exposed_to_action=True,source_independently_born_F3=False,
        primary_original_not_executed=True,accepted_ref_mutation=False,scores=scores,
        mechanism_scores=mechanism_scores,rows=rows,
        verdict="TRAIN_ONLY_LATENT_RELIABILITY_QUALIFIED" if advance else "TRAIN_ONLY_LATENT_RELIABILITY_NO_GAIN")
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

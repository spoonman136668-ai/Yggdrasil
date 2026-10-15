"""Y-F35 train-only conditional posterior acquisition policy; no primary original.

The 24 trainable weights learn expected *future bit-loss* from public
calibration, known instrument polarity and the FIRST purchased target channel.
Reference anchors and latent target modes remain separate; no private truth,
unbought target channel, or evaluation family enters an action callback.
"""
from __future__ import annotations
import importlib.util,math,random,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("yf35_sensor_custody",H.parent/"20261015-y-f28"/"sensor_custody.py")
custody=importlib.util.module_from_spec(spec);sys.modules[spec.name]=custody;spec.loader.exec_module(custody)

TRAIN=range(221800,221840)
TRAIN_FAMILIES=(210,211,212)
EVAL=range(222800,222816)
EVAL_FAMILIES=(214,215,216,217)
RESERVED=range(212800,212816)
RESERVED_FAMILIES=(194,195,196,197)
CONDITIONS=("ordinary","polarity_reversal","weak_marker","uninformative_marker")
MECHANISMS=("mode_switch","anti_correlated_noisy")
METHODS=("learned","polarity_bayes","empirical_brier","calibrated_static","fixed","masked_first","privileged_oracle")
ANCHORS=16;NFEATURES=8;NATIVE_CAP=576
PAID_READS=2
def guarded(seed,family):
    if not ((seed in TRAIN and family in TRAIN_FAMILIES) or
            (seed in EVAL and family in EVAL_FAMILIES)):
        raise ValueError("reserved source or consumed identity denied")

def physical(seed,role,family,condition,mechanism,episode):
    guarded(seed,family)
    g=random.Random(997+seed*131071+role*617+family*19009+condition*7103+mechanism*311+episode*37)
    truth=g.randrange(2);mode=g.randrange(2);signed=2*truth-1
    orientation=-1 if (family+condition+mechanism)%2 else 1
    if condition==1:orientation=-orientation
    amplitude=(.30 if condition<2 else .15 if condition==2 else 0.)
    first=max(0.,min(1.,.5+orientation*(2*mode-1)*amplitude+g.gauss(0,.095 if condition<2 else .15)))
    values=[first]
    for j in (1,2,3):
        selected=(j==1 and mode==0) or (j==2 and mode==1)
        mag=.39 if selected else .035
        if j==3:mag=.17
        noise=.12 if selected else .22
        if mechanism==1:
            if j==2:mag=-mag;noise=.15 if selected else .22
            if j==3:mag=.23;noise=.16
        if condition==2 and j==1:noise+=.07
        if condition==3 and j==3:mag=.18
        values.append(max(0.,min(1.,.5+signed*mag+g.gauss(0,noise))))
    return truth,mode,tuple(values),orientation

def source_reference(seed,family,condition,mechanism):
    return tuple((truth,measurements) for i in range(ANCHORS) for truth,_,measurements,_ in
                 [physical(seed,i%3,family,condition,mechanism,50000+i*19)])

def public_calibration(anchors):
    corr=[sum((2*y-1)*(2*v[j]-1) for y,v in anchors)/len(anchors) for j in range(4)]
    missing=[sum(v[j]==.5 for y,v in anchors)/len(anchors) for j in range(4)]
    return custody.PublicSensorInfo(tuple(corr),tuple(missing))

def posterior_bit(value,j,public):
    # Shared fixed decoder across all fair acquisition algorithms.
    r=public.reliability[j]
    z=(2*value-1)*r/(abs(r)+.05)
    return 1/(1+math.exp(-max(-20,min(20,5*z))))

def features(j,first,polarity,public):
    v=2*first-1
    cor=public.reliability[j]
    return (1.,abs(cor),cor,polarity*v,abs(v),
            (polarity*v)*(1 if j==1 else -1 if j==2 else 0),
            public.missingness[j],1. if j==3 else 0.)

def public_choice(method,first,polarity,anchors,public,weights):
    candidates=(1,2,3)
    if method in ("learned","masked_first"):
        reading=.5 if method=="masked_first" else first
        vals=[sum(weights[k][i]*v for i,v in enumerate(features(k+1,reading,polarity,public))) for k in range(3)]
        return candidates[max(range(3),key=lambda i:(vals[i],-i))]
    if method=="polarity_bayes":
        mode_guess=int((first-.5)*polarity>=0)
        return 1 if mode_guess==0 else 2
    if method=="empirical_brier":
        risk=[]
        for j in candidates:
            sumloss=weight_sum=0.
            for truth,src in anchors:
                weight=math.exp(-9*abs(src[0]-first))
                p=posterior_bit(src[j],j,public)
                sumloss+=weight*(p-truth)**2;weight_sum+=weight
            risk.append(sumloss/(weight_sum+1e-12))
        return candidates[min(range(3),key=lambda i:(risk[i],i))]
    if method=="calibrated_static":return max(candidates,key=lambda j:(abs(public.reliability[j]),-j))
    if method=="fixed":return 3
    raise ValueError(method)

def train():
    samples=[]
    for seed in TRAIN:
      for fam in TRAIN_FAMILIES:
       for cond in range(4):
        for mechanism in range(2):
            anchors=source_reference(seed,fam,cond,mechanism)
            pub=public_calibration(anchors)
            for role in range(3):
                truth,mode,channels,polarity=physical(seed,role,fam,cond,mechanism,9000+role)
                options=[features(j,channels[0],polarity,pub) for j in (1,2,3)]
                errors=[]
                for j in (1,2,3):
                    p=posterior_bit(channels[j],j,pub)
                    errors.append(-truth*math.log(max(1e-6,p))-(1-truth)*math.log(max(1e-6,1-p)))
                samples.append((options,errors))
    weights=[[0.]*NFEATURES for _ in range(3)]
    for epoch in range(95):
        gradient=[[0.]*NFEATURES for _ in range(3)]
        for xs,losses in samples:
            logits=[sum(a*b for a,b in zip(weights[j],xs[j])) for j in range(3)]
            biggest=max(logits)
            exps=[math.exp(v-biggest) for v in logits]
            z=sum(exps);probs=[v/z for v in exps]
            avg_loss=sum(p*y for p,y in zip(probs,losses))
            for j in range(3):
                delta=probs[j]*(losses[j]-avg_loss)
                for i in range(NFEATURES):gradient[j][i]+=delta*xs[j][i]
        lr=.15
        for j in range(3):
            for i in range(NFEATURES):
                weights[j][i]-=lr*(gradient[j][i]/len(samples)+.001*weights[j][i])
    return weights,len(samples)

def composite(bits,family):
    if family%2==0:return bool(bits[0]^bits[1]^bits[2])
    return sum(bool(v) for v in bits)>=2

def summary(rows,name):
    n=len(rows);correct=fp=fn=0
    for r in rows:
        v=r["answers"][name];true=r["truth"]
        correct+=v==true;fp+=bool(v) and not true;fn+=not bool(v) and true
    return dict(total=n,correct=correct,accuracy=correct/n,fp=fp,fn=fn)

def run():
    assert set(TRAIN).isdisjoint(EVAL) and set(TRAIN_FAMILIES).isdisjoint(EVAL_FAMILIES)
    assert set(EVAL).isdisjoint(RESERVED) and set(EVAL_FAMILIES).isdisjoint(RESERVED_FAMILIES)
    weights,count=train()
    rows=[];switch=total_switch=0
    for seed in EVAL:
      for fam in EVAL_FAMILIES:
       for cond in range(4):
        for mechanism in range(2):
            anchors=source_reference(seed,fam,cond,mechanism)
            pub=public_calibration(anchors)
            source=[physical(seed,r,fam,cond,mechanism,9000+r) for r in range(3)]
            truth=composite([v[0] for v in source],fam)
            answers={"privileged_oracle":truth};receipts={}
            for method in METHODS[:-1]:
                bits=[];purchases=[]
                for target_truth,hidden_mode,channels,polarity in source:
                    receipt=custody.evaluate_policy(
                        channels,pub,lambda _:0,
                        lambda public,first,mode=method,ori=polarity:public_choice(
                            mode,first.value,ori,anchors,public,weights),
                        NATIVE_CAP,ANCHORS*5*8)
                    if receipt.physical_reads!=PAID_READS:raise ValueError("read budget drift")
                    first,second=receipt.trace
                    if first.sensor!=0 or second.sensor==0:raise ValueError("not sequential")
                    bits.append(posterior_bit(second.value,second.sensor,pub)>=.5)
                    purchases.append((first.sensor,second.sensor))
                answers[method]=composite(bits,fam)
                receipts[method]=purchases
            orientation=source[0][3]
            for low,high in ((.2,.8),(.35,.65)):
                switch+=public_choice("learned",low,orientation,anchors,pub,weights)!=public_choice("learned",high,orientation,anchors,pub,weights)
                total_switch+=1
            rows.append(dict(seed=seed,family=fam,condition=CONDITIONS[cond],mechanism=MECHANISMS[mechanism],
                truth=truth,answers=answers,receipts=receipts,public_anchor_count=len(anchors)))
    scores={name:summary(rows,name) for name in METHODS}
    strata={m:{name:summary([r for r in rows if r["mechanism"]==m],name) for name in METHODS}
            for m in MECHANISMS}
    controls=METHODS[1:5]
    best=max(scores[c]["accuracy"] for c in controls)
    gain=scores["learned"]["accuracy"]-best
    pass_gate=(gain>=.02 and scores["learned"]["accuracy"]>scores["masked_first"]["accuracy"]
          and switch>0 and all(strata[m]["learned"]["accuracy"]>=max(strata[m][c]["accuracy"] for c in controls)
          for m in MECHANISMS))
    return dict(schema="yggdrasil.f35.learned-conditional-posterior.trainonly.v1",
        stage="FRESH_TRAIN_ONLY_EVALUATION_NOT_PRIMARY_ORIGINAL",
        train_seed_range=[TRAIN.start,TRAIN.stop],train_families=TRAIN_FAMILIES,
        eval_seed_range=[EVAL.start,EVAL.stop],eval_families=EVAL_FAMILIES,
        reserved_original_seeds=[RESERVED.start,RESERVED.stop],reserved_original_families=RESERVED_FAMILIES,
        train_examples=count,weights=weights,trainable_coefficients=3*NFEATURES,
        native_policy_weights_bytes=3*NFEATURES*8,native_core_cap=576,
        external_calibration_bytes_per_role=ANCHORS*5*8,physical_target_reads_per_role=PAID_READS,
        conditional_switch_rate=switch/total_switch,questions=len(rows),scores=scores,
        by_mechanism=strata,rows=rows,
        source_hidden_modes_unavailable_to_policy=True,independent_F3_source_custody=False,
        primary_original_not_executed=True,accepted_ref_mutation=False,paid_api_calls=0,
        verdict="TRAIN_ONLY_LEARNED_POSTERIOR_QUALIFIED" if pass_gate else "TRAIN_ONLY_LEARNED_POSTERIOR_NO_GAIN")
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

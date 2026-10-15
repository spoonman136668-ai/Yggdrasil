"""Y-F29: train expected downstream utility under unknown sensor shifts.

Development-only synthetic experiment. Evaluation policies get the same public
labeled calibration anchors and the first paid reading, NOT the true generator
mechanism, hidden role bit, unpurchased source values, or held-out answers.
"""
from __future__ import annotations
import json
import math
import random
from dataclasses import asdict
import torch
from pathlib import Path
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("yf28custody",str(HERE.parent/"20261015-y-f28"/"sensor_custody.py"))
custody=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=custody
spec.loader.exec_module(custody)

TRAIN_SEEDS=range(151000,151079)
TEST_SEEDS=range(152800,152816)
TRAIN_REGIMES=(0,1,2)
TEST_REGIMES=(3,4)
CONDITIONS=("missing","noise","anchor-corruption")
TEST_FAMILIES=(108,109,110,111)
METHODS=("learned","empirical_adaptive","conditional_greedy","static","fixed","masked_first","privileged_oracle")
COEFFS=8
NATIVE_BYTES=576
CALIBRATION_COUNT=48
CALIBRATION_EXTERNAL_BYTES=48*4*8+48*8

torch.manual_seed(2929)
torch.set_num_threads(1)

def rng_for(seed,role,regime,condition,episode):
    return random.Random(seed*1000003+role*23741+regime*10007+condition*991+episode*43)

def measurements(seed,role,regime,condition,episode):
    rng=rng_for(seed,role,regime,condition,episode)
    truth=rng.randrange(2);mode=rng.randrange(2);signal=1 if truth else -1
    readings=[]
    for j in range(4):
        # Public calibration can characterize these mechanisms, but the
        # policy is never handed regime, mode, or hidden truth directly.
        if regime==0:strength=(.26,.31 if mode==0 else .03,.31 if mode==1 else .03,.18)[j]
        elif regime==1:strength=(.22,.27 if mode==0 else .08,.27 if mode==1 else .08,.17)[j]
        elif regime==2:strength=(.25,.29 if mode==0 else -.10,.29 if mode==1 else -.10,.07)[j]
        elif regime==3:strength=(.17,.04 if mode==0 else .28,.28 if mode==0 else .04,.26)[j]
        else:strength=(.18,-.23 if mode==0 else .12,.23 if mode==1 else -.12,.22)[j]
        if condition==1 and j==2:strength*=.70
        if condition==2 and j==1:strength*=-1
        noise=(.15,.20,.20,.23)[j]
        if regime in (1,4) and j==3:noise=.13
        value=max(0.,min(1.,.5+strength*signal+rng.gauss(0,noise)))
        if condition==0 and j==2 and rng.random()<.20:value=.5
        readings.append(value)
    return truth,tuple(readings)

def calibrate(seed,regime,condition):
    # A public labeled reference bank, disjoint from target entity episodes.
    samples=[measurements(seed+99991+i*7,i%3,regime,condition,200+i) for i in range(CALIBRATION_COUNT)]
    reliability=[]
    missing=[]
    for j in range(4):
        vals=[((2*value[j]-1)*(2*truth-1)) for truth,value in samples]
        reliability.append(sum(vals)/len(vals))
        missing.append(sum(value[j]==.5 for _,value in samples)/len(samples))
    return custody.PublicSensorInfo(tuple(reliability),tuple(missing)),samples

def features(pub,first,j,override=None):
    v=first.value if override is None else override
    corr=pub.reliability[j];first_corr=pub.reliability[first.sensor]
    uncertainty=1-abs(2*v-1)
    return (1.,abs(corr),pub.missingness[j],(2*v-1)*first_corr,
            uncertainty,abs(corr)*uncertainty,corr*(2*v-1),j/3.)

def first_choice(pub):
    return max(range(4),key=lambda j:(abs(pub.reliability[j])-.12*pub.missingness[j],-j))

def decode(first,second,pub):
    a=pub.reliability[first.sensor];b=pub.reliability[second.sensor]
    z=((2*first.value-1)*a+(2*second.value-1)*b)/(abs(a)+abs(b)+.04)
    return 1/(1+math.exp(-max(-20,min(20,5*z))))

def empirical_choice(pub,first,anchors):
    # Strong adaptive control sees exactly the same 48 public anchor pairs,
    # never a hidden evaluation truth or actual mechanism identity.
    options=[j for j in range(4) if j!=first.sensor]
    chosen=None;best=math.inf
    for j in options:
        weighted=mass=0.
        for truth,source in anchors:
            w=math.exp(-abs(source[first.sensor]-first.value)*10)
            proxy=custody.PurchasedReading(first.sensor,source[first.sensor])
            second=custody.PurchasedReading(j,source[j])
            prediction=decode(proxy,second,pub)
            weighted+=w*(prediction-truth)**2
            mass+=w
        error=weighted/max(1e-12,mass)
        if error<best:best=error;chosen=j
    return chosen

def train():
    examples=[];losses=[];biases=[];options=[]
    for seed in TRAIN_SEEDS:
        for regime in TRAIN_REGIMES:
            for condition in range(3):
                pub,anchors=calibrate(seed,regime,condition)
                for role in range(3):
                    truth,values=measurements(seed,role,regime,condition,90+role)
                    first=first_choice(pub)
                    observed=custody.PurchasedReading(first,values[first])
                    alternatives=[j for j in range(4) if j!=first]
                    examples.append([features(pub,observed,j) for j in alternatives])
                    biases.append(alternatives)
                    losses.append([-(truth*math.log(max(1e-6,decode(observed,custody.PurchasedReading(j,values[j]),pub)))+
                                    (1-truth)*math.log(max(1e-6,1-decode(observed,custody.PurchasedReading(j,values[j]),pub))))
                                   for j in alternatives])
    x=torch.tensor(examples,dtype=torch.float32)
    target=torch.tensor(losses,dtype=torch.float32)
    ids=torch.tensor(biases,dtype=torch.long)
    w=torch.nn.Parameter(torch.zeros(COEFFS))
    b=torch.nn.Parameter(torch.zeros(4))
    optimizer=torch.optim.Adam([w,b],lr=.055)
    for _ in range(120):
        optimizer.zero_grad()
        logits=(x*w).sum(-1)+b[ids]
        probabilities=torch.softmax(logits,dim=1)
        loss=(probabilities*target).sum(-1).mean()
        loss.backward()
        torch.nn.utils.clip_grad_norm_([w,b],5)
        optimizer.step()
    return tuple(float(v) for v in w.detach()),tuple(float(v) for v in b.detach()),len(examples),float(loss.detach())

def second_choice(mode,pub,first,anchors,w,b):
    options=[j for j in range(4) if j!=first.sensor]
    if mode in ("learned","masked_first"):
        masked=.5 if mode=="masked_first" else None
        return max(options,key=lambda j:(sum(p*q for p,q in zip(w,features(pub,first,j,masked)))+b[j],-j))
    if mode=="empirical_adaptive":return empirical_choice(pub,first,anchors)
    if mode=="conditional_greedy":
        return max(options,key=lambda j:(abs(pub.reliability[j])*(1+.12*(first.value>.5)*(pub.reliability[j]>0))-.12*pub.missingness[j],-j))
    if mode=="static":return max(options,key=lambda j:(abs(pub.reliability[j])-.12*pub.missingness[j],-j))
    if mode=="fixed":return 3 if first.sensor!=3 else 0
    raise ValueError("unknown arm")

def relation(bits,fam):
    if fam%2==0:return bool(bits[0]^bits[1]^bits[2])
    return sum(bool(x) for x in bits)>=2

def score(rows,arm):
    n=len(rows)
    pred=[r["predictions"][arm] for r in rows]
    correct=sum(p==r["truth"] for p,r in zip(pred,rows))
    return dict(correct=correct,total=n,accuracy=correct/n,
                false_positives=sum(bool(p) and not r["truth"] for p,r in zip(pred,rows)),
                false_negatives=sum(not bool(p) and r["truth"] for p,r in zip(pred,rows)))

def original():
    custody.validate_disjoint(
        dict(seeds=set(TRAIN_SEEDS),entities={v+100000 for v in TRAIN_SEEDS},families={200,201,202,203}),
        dict(seeds=set(TEST_SEEDS),entities={v+300000 for v in TEST_SEEDS},families=set(TEST_FAMILIES)))
    w,b,records,loss=train()
    rows=[]
    for seed in TEST_SEEDS:
        for fam in TEST_FAMILIES:
            for regime in TEST_REGIMES:
                for cond in range(3):
                    pub,anchors=calibrate(seed,regime,cond)
                    truthbits=[];observations=[]
                    for role in range(3):
                        truth,values=measurements(seed,role,regime,cond,400+role)
                        truthbits.append(truth);observations.append(values)
                    truth=relation(truthbits,fam)
                    predictions={"privileged_oracle":truth};receipts={}
                    for method in METHODS[:-1]:
                        bits=[];traces=[]
                        for vals in observations:
                            receipt=custody.evaluate_policy(vals,pub,first_choice,
                              lambda public,first,m=method:second_choice(m,public,first,anchors,w,b),
                              NATIVE_BYTES,CALIBRATION_EXTERNAL_BYTES)
                            if receipt.physical_reads!=2:raise AssertionError("budget drift")
                            first,second=receipt.trace
                            bits.append(decode(first,second,pub)>=.5)
                            traces.append([[v.sensor,round(v.value,7)] for v in receipt.trace])
                        predictions[method]=relation(bits,fam)
                        receipts[method]=traces
                    rows.append(dict(seed=seed,family=fam,regime=regime,condition=CONDITIONS[cond],
                                     truth=truth,predictions=predictions,receipts=receipts,
                                     public_reliabilities=pub.reliability,
                                     calibration_anchor_count=len(anchors)))
    scores={arm:score(rows,arm) for arm in METHODS}
    strata={str(regime)+":"+cond:{arm:score([r for r in rows if r["regime"]==regime and r["condition"]==cond],arm)
         for arm in METHODS} for regime in TEST_REGIMES for cond in CONDITIONS}
    # Switch rate is tested using matched first-value interventions, never
    # held-out truth-based training or adjusted thresholds.
    switches=0;total=0
    for seed in TEST_SEEDS:
        for regime in TEST_REGIMES:
            pub,anchors=calibrate(seed,regime,0)
            a=first_choice(pub)
            for lo,hi in ((.2,.8),(.4,.6)):
                f0=custody.PurchasedReading(a,lo);f1=custody.PurchasedReading(a,hi)
                switches+=second_choice("learned",pub,f0,anchors,w,b)!=second_choice("learned",pub,f1,anchors,w,b)
                total+=1
    switch_rate=switches/max(1,total)
    best=max(scores[a]["accuracy"] for a in METHODS[1:5])
    nondegrading=all(strata[k]["learned"]["accuracy"]>=max(strata[k][a]["accuracy"] for a in METHODS[1:5]) for k in strata)
    passed=(scores["learned"]["accuracy"]-best>=.02 and nondegrading and switch_rate>0)
    return dict(schema="yggdrasil.f29.unknown-shift-development.v1",stage="DEVELOPMENT_ONLY",
      parent="2d1a339782d56b403c3afb1cc1a11035f9d5c57b",train_seed_range=[151000,151079],
      test_seed_range=[152800,152816],train_regimes=TRAIN_REGIMES,test_regimes=TEST_REGIMES,
      test_families=TEST_FAMILIES,conditions=CONDITIONS,trained_policy_weights=w,
      trained_policy_bias=b,train_examples=records,train_loss=loss,read_budget=2,
      native_state_bytes=NATIVE_BYTES,public_calibration_anchors=CALIBRATION_COUNT,
      calibration_bytes_external=CALIBRATION_EXTERNAL_BYTES,source_mode_unavailable_at_inference=True,
      training_access_to_all_training_sources=True,learned_first_value_switch_rate=switch_rate,
      questions=len(rows),scores=scores,strata=strata,rows=rows,
      verdict="DEVELOPMENT_UNKNOWN_SHIFT_LEARNED_GAIN" if passed else "DEVELOPMENT_UNKNOWN_SHIFT_NO_QUALIFIED_GAIN",
      independently_born_F3_source=False,sealed_first_use=False,accepted_ref_mutation=False,paid_api_calls=0)

if __name__=="__main__":print(json.dumps(original(),sort_keys=True,indent=2))

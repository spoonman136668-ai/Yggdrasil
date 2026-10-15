"""Y-F30: train-only learned posterior expected value of second observation.

DEVELOPMENT ONLY, source generated here (not independently born F3).
Calibration anchors are public/labeled and separate from evaluation identities;
the scorer has only those anchors and its first *purchased* reading. Other
target channels and the hidden regime/bit remain behind a two-read port.
"""
from __future__ import annotations

import importlib.util
import json
import math
import random
import sys
from pathlib import Path

import torch

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("yf30_custody",HERE.parent/"20261015-y-f28"/"sensor_custody.py")
custody=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=custody
spec.loader.exec_module(custody)
torch.set_num_threads(1)
torch.manual_seed(3030)

TRAIN_SEEDS=range(161200,161248)
TEST_SEEDS=range(162700,162716)
TRAIN_REGIMES=(0,1,2)
TEST_REGIMES=(3,4)
FAMILIES=(112,113,114,115)
CONDITIONS=("ordinary","missingness","anticorrelated-source")
ARMS=("learned","adaptive_calibration","calibrated_static","conditional_greedy","fixed","masked_first","oracle")
N_ANCHORS=64
CORE_BYTES=576
CALIB_BYTES=N_ANCHORS*(4*8+8)
FEATURE_DIM=10
OPTIONS=(1,2,3)

def clip(v):
    return min(1.,max(0.,v))

def physics(seed,role,regime,condition,episode):
    randomizer=random.Random(seed*1000003+role*17431+regime*7717+condition*971+episode*173)
    truth=randomizer.randrange(2)
    mode=randomizer.randrange(2)
    y=2*truth-1
    # The first target channel is a source-mode hint, not the true role bit.
    # A test regime changes both marker orientation and sensor physics.
    marker_sign=-1 if regime in (1,3) else 1
    mode_value=marker_sign*(2*mode-1)
    marker_noise={0:.08,1:.09,2:.17,3:.11,4:.22}[regime]
    marker=clip(.5+.30*mode_value+randomizer.gauss(0,marker_noise))
    sensors=[marker]
    for j in OPTIONS:
        if regime==0:
            strength=(.37 if mode==0 else .02) if j==1 else (.37 if mode==1 else .02) if j==2 else .15
        elif regime==1:
            strength=(.31 if mode==0 else .05) if j==1 else (.31 if mode==1 else .05) if j==2 else .19
        elif regime==2:
            strength=(.30 if mode==0 else -.10) if j==1 else (.30 if mode==1 else -.10) if j==2 else .14
        elif regime==3:
            strength=(.06 if mode==0 else .36) if j==1 else (.36 if mode==0 else .06) if j==2 else .18
        else:
            strength=(.32 if mode==0 else -.07) if j==1 else (-.07 if mode==0 else .32) if j==2 else .22
        noise=(.14 if j==1 else .17 if j==2 else .19)
        if regime==4 and j==3:noise=.12
        if condition==1 and j==1 and randomizer.random()<.22:
            sensors.append(.5)
            continue
        if condition==2 and j==2: strength=-strength
        sensors.append(clip(.5+strength*y+randomizer.gauss(0,noise)))
    return truth,tuple(sensors)

def public_anchors(seed,regime,condition):
    # Labeled source calibration is available equally to ALL fair arms.
    return tuple((truth,readings) for i in range(N_ANCHORS)
          for truth,readings in [physics(seed+50000+i*11,i%4,regime,condition,1000+i)])

def calibration(anchors):
    correlation=[]
    missing=[]
    for j in range(4):
        correlation.append(sum((2*v[j]-1)*(2*y-1) for y,v in anchors)/N_ANCHORS)
        missing.append(sum(v[j]==.5 for _,v in anchors)/N_ANCHORS)
    return custody.PublicSensorInfo(tuple(correlation),tuple(missing))

def conditional_corr(anchors,first,j):
    # Soft posterior mixture derived only from public labeled references and
    # the first paid reading. This estimator is shared by all fair decoders.
    weighted=0.;mass=0.
    for truth,vals in anchors:
        w=math.exp(-10*abs(first-vals[0]))
        weighted+=w*(2*vals[j]-1)*(2*truth-1)
        mass+=w
    return weighted/(mass+1.e-12)

def features(pub,anchors,first,j):
    cc=conditional_corr(anchors,first,j)
    unc=pub.reliability[j]
    v=2*first-1
    return (1.,abs(cc),cc,abs(unc),pub.missingness[j],
            v,abs(v),1. if j==3 else 0.,cc-unc,v*cc)

def predict_bit(first,second,j,anchors):
    cc=conditional_corr(anchors,first,j)
    z=(2*second-1)*cc/(abs(cc)+.05)
    return 1/(1+math.exp(-max(-20,min(20,5*z))))

def adaptive_choice(first,anchors):
    # Equal-budget empirical Bayesian proxy, trained only on public
    # calibration examples: conditional Brier risk for each next sensor.
    risk=[]
    for j in OPTIONS:
        total=mass=0.
        for truth,values in anchors:
            weight=math.exp(-10*abs(values[0]-first))
            guess=predict_bit(values[0],values[j],j,anchors)
            total+=weight*(guess-truth)**2
            mass+=weight
        risk.append(total/(mass+1.e-12))
    return OPTIONS[min(range(3),key=lambda i:(risk[i],i))]

def train():
    xs=[];risks=[]
    for seed in TRAIN_SEEDS:
        for regime in TRAIN_REGIMES:
            for cond in range(3):
                anchors=public_anchors(seed,regime,cond)
                pub=calibration(anchors)
                for role in range(4):
                    truth,values=physics(seed,role,regime,cond,500+role)
                    xs.append([features(pub,anchors,values[0],j) for j in OPTIONS])
                    risks.append([
                        -truth*math.log(max(1e-6,predict_bit(values[0],values[j],j,anchors)))
                        -(1-truth)*math.log(max(1e-6,1-predict_bit(values[0],values[j],j,anchors)))
                        for j in OPTIONS])
    x=torch.tensor(xs,dtype=torch.float32)
    target=torch.tensor(risks,dtype=torch.float32)
    w=torch.nn.Parameter(torch.zeros(FEATURE_DIM))
    optimizer=torch.optim.Adam([w],lr=.055)
    for _ in range(140):
        optimizer.zero_grad()
        decision=torch.softmax((x*w).sum(-1),dim=1)
        expected=(decision*target).sum(-1).mean()
        expected.backward()
        torch.nn.utils.clip_grad_norm_([w],5.)
        optimizer.step()
    return tuple(float(v) for v in w.detach().tolist()),len(xs),float(expected.detach())

def second(mode,pub,anchors,first,w):
    v=.5 if mode=="masked_first" else first.value
    if mode in ("learned","masked_first"):
        scores=[sum(a*b for a,b in zip(w,features(pub,anchors,v,j))) for j in OPTIONS]
        return OPTIONS[max(range(3),key=lambda i:(scores[i],-i))]
    if mode=="adaptive_calibration":
        return adaptive_choice(first.value,anchors)
    if mode=="calibrated_static":
        return max(OPTIONS,key=lambda j:(abs(pub.reliability[j]),-j))
    if mode=="conditional_greedy":
        return max(OPTIONS,key=lambda j:(abs(conditional_corr(anchors,v,j)),-j))
    if mode=="fixed":
        return 1
    raise ValueError("unregistered policy")

def composite(bits,family):
    if family%2==0:return bool(bits[0]^bits[1]^bits[2])
    return sum(bool(v) for v in bits)>=2

def summarize(rows,name):
    n=len(rows);correct=fp=fn=0
    for r in rows:
        value=r["answers"][name]
        truth=r["truth"]
        correct+=value==truth
        fp+=bool(value) and not truth
        fn+=not bool(value) and truth
    return dict(total=n,correct=correct,accuracy=correct/n if n else 0.,
                fp=fp,fn=fn)

def original():
    custody.validate_disjoint(
        dict(seeds=set(TRAIN_SEEDS),entities={100000+s for s in TRAIN_SEEDS},families={120,121,122}),
        dict(seeds=set(TEST_SEEDS),entities={200000+s for s in TEST_SEEDS},families=set(FAMILIES)))
    w,train_n,train_loss=train()
    rows=[]
    for seed in TEST_SEEDS:
        for family in FAMILIES:
            for regime in TEST_REGIMES:
                for condition in range(len(CONDITIONS)):
                    anchors=public_anchors(seed,regime,condition)
                    pub=calibration(anchors)
                    labels=[];source_values=[]
                    for role in range(3):
                        label,vals=physics(seed,role,regime,condition,9000+role)
                        labels.append(label);source_values.append(vals)
                    truth=composite(labels,family)
                    answers={"oracle":truth}
                    receipts={}
                    for arm in ARMS[:-1]:
                        decisions=[];trace=[]
                        for vals in source_values:
                            observed=custody.evaluate_policy(
                                vals,pub,lambda _public:0,
                                lambda _public,first,a=arm:second(a,_public,anchors,first,w),
                                CORE_BYTES,CALIB_BYTES)
                            assert observed.physical_reads==2 and observed.trace[0].sensor==0
                            t0,t1=observed.trace
                            decisions.append(predict_bit(t0.value,t1.value,t1.sensor,anchors)>=.5)
                            trace.append([[v.sensor,round(v.value,8)] for v in observed.trace])
                        answers[arm]=composite(decisions,family)
                        receipts[arm]=trace
                    rows.append(dict(seed=seed,family=family,regime=regime,condition=CONDITIONS[condition],
                                     answers=answers,truth=truth,receipts=receipts,
                                     public_correlation=pub.reliability,calibration_anchors=N_ANCHORS))
    summary={a:summarize(rows,a) for a in ARMS}
    per_regime={str(r):{a:summarize([v for v in rows if v["regime"]==r],a) for a in ARMS}
                for r in TEST_REGIMES}
    # Causal action probe, not label-dependent decision tuning.
    switches=0;total=0
    for seed in TEST_SEEDS:
        for regime in TEST_REGIMES:
            anchors=public_anchors(seed,regime,0)
            pub=calibration(anchors)
            for low,high in ((.15,.85),(.3,.7),(.4,.6)):
                a=custody.PurchasedReading(0,low)
                b=custody.PurchasedReading(0,high)
                switches+=second("learned",pub,anchors,a,w)!=second("learned",pub,anchors,b,w)
                total+=1
    switch_rate=switches/total
    fair=max(summary[a]["accuracy"] for a in ("adaptive_calibration","calibrated_static","conditional_greedy","fixed"))
    pass_gate=(summary["learned"]["accuracy"]-fair>=.02 and
        summary["learned"]["correct"]>summary["masked_first"]["correct"] and switch_rate>0 and
        all(per_regime[str(r)]["learned"]["accuracy"] >= max(per_regime[str(r)][a]["accuracy"]
            for a in ("adaptive_calibration","calibrated_static","conditional_greedy","fixed"))
            for r in TEST_REGIMES))
    return dict(schema="yggdrasil.f30.learned-posterior-sensing.dev.v1",stage="DEVELOPMENT_ONLY",
       parent="21ebe0696474638048123f15f7799cd76d11be3c",trained_weights=w,
       train_examples=train_n,train_loss=train_loss,train_seeds=[161200,161248],
       test_seeds=[162700,162716],test_families=FAMILIES,test_regimes=TEST_REGIMES,
       conditions=CONDITIONS,questions=len(rows),actual_target_reads_per_role=2,
       native_state_bytes=CORE_BYTES,learned_coefficient_bytes=len(w)*8,
       public_reference_anchor_count=N_ANCHORS,external_calibration_bytes=CALIB_BYTES,
       first_read_only_second_action=True,train_uses_only_training_labels=True,
       test_labels_unavailable_to_action=True,unseen_regime_ids_not_passed_to_action=True,
       action_switch_rate=switch_rate,scores=summary,per_regime=per_regime,rows=rows,
       verdict="DEVELOPMENT_POSTERIOR_LEARNED_GAIN" if pass_gate else "DEVELOPMENT_POSTERIOR_NO_QUALIFIED_GAIN",
       independent_F3_source_custody=False,sealed_first_use=False,accepted_ref_mutation=False,
       paid_api_calls=0)

if __name__=="__main__":
    print(json.dumps(original(),sort_keys=True,indent=2))

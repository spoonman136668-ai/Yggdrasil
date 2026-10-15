"""Y-F32: train-only conditional-information feasibility, not primary original.

The polarities of the public calibration settings are observable metadata.
A hidden per-case source mode remains PRIVATE. Sensor acquisition is through
the prior 2-read custody port; oracle bits and unpurchased values are never
passed into action selection. Reserved Y-F32 test seeds are never generated.
"""
from __future__ import annotations
import importlib.util, json, math, random, sys
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("yf32_custody",P.parent/"20261015-y-f28"/"sensor_custody.py")
custody=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=custody
spec.loader.exec_module(custody)

SEEDS=range(191800,191832)
RESERVED_SEEDS=range(192800,192812)
FAMILIES=(170,171,172,173)
RESERVED_FAMILIES=(174,175,176,177)
CONDITIONS=("marker_normal","marker_reversed","marker_corrupted","marker_noninformative")
ANCHORS=8
ARMS=("conditional_empirical","bayesian_posterior","static","fixed","privileged_oracle")

def obs(seed,role,family,condition,episode):
    gen=random.Random(seed*1000003+role*761+family*2939+condition*199+episode*87)
    truth=gen.randrange(2)
    mode=gen.randrange(2)
    orientation=(1 if (family+condition)%2==0 else -1)
    if condition==1:orientation*=-1
    amplitude=.28 if condition!=3 else .008
    marker=max(0.,min(1.,.5+amplitude*orientation*(2*mode-1)+gen.gauss(0,.11 if condition<2 else .20)))
    senses=[marker]
    for j in (1,2,3):
        strong=(j==1 and mode==0) or (j==2 and mode==1)
        magnitude=.38 if strong else .045
        if j==3:magnitude=.21
        if condition==2 and j==2:magnitude=-magnitude
        error=.15 if strong else .23
        v=max(0.,min(1.,.5+magnitude*(2*truth-1)+gen.gauss(0,error)))
        senses.append(v)
    return truth,mode,tuple(senses),orientation

def anchors(seed,family,condition):
    return tuple((truth,values) for i in range(ANCHORS)
                 for truth,mode,values,orientation in [obs(seed+50000+i*19,i%3,family,condition,100+i)])

def calibration(sample):
    corr=[];miss=[]
    for j in range(4):
        corr.append(sum((2*truth-1)*(2*values[j]-1) for truth,values in sample)/ANCHORS)
        miss.append(sum(values[j]==.5 for _,values in sample)/ANCHORS)
    return custody.PublicSensorInfo(tuple(corr),tuple(miss))

def estimate_bit(first,second,j,pub):
    r=pub.reliability[j]
    z=(2*second-1)*r/(abs(r)+.05)
    return 1/(1+math.exp(-max(-20,min(20,5*z))))

def choose(first,metadata,sample,pub,arm):
    if arm=="fixed":return 3
    if arm=="static":return max((1,2,3),key=lambda j:(abs(pub.reliability[j]),-j))
    if arm=="bayesian_posterior":
        # Public physical polarity, not hidden evaluation mode.
        inferred_mode=0 if (first-.5)*metadata < 0 else 1
        return 1 if inferred_mode==0 else 2
    if arm=="conditional_empirical":
        risks=[]
        for j in (1,2,3):
            numerator=denominator=0.
            for truth,values in sample:
                weight=math.exp(-9*abs(values[0]-first))
                p=estimate_bit(values[0],values[j],j,pub)
                numerator+=weight*(p-truth)**2
                denominator+=weight
            risks.append(numerator/(denominator+1.e-12))
        return (1,2,3)[min(range(3),key=lambda k:(risks[k],k))]
    raise ValueError(arm)

def relation(bits,family):
    if family%2==0:return bool(bits[0]^bits[1]^bits[2])
    return sum(bool(v) for v in bits)>=2

def score(rows,arm):
    right=sum(r["answers"][arm]==r["truth"] for r in rows)
    return dict(total=len(rows),correct=right,accuracy=right/len(rows))

def mutual_info(data,conditional):
    # Data tuples (hidden mode, first-sign, public polarity), evaluated only
    # in independent audit, after all choices. Nothing passed to selector.
    def mi(group):
        n=len(group)
        if not n:return 0.
        joint=Counter((m,s) for m,s,_ in group)
        mcount=Counter(m for m,s,c in group)
        scount=Counter(s for m,s,c in group)
        return sum((v/n)*math.log2((v*n)/(mcount[m]*scount[s]))
                    for (m,s),v in joint.items() if v>0)
    if not conditional:return mi(data)
    orientations={p for m,s,p in data}
    return sum(sum(p0==p for m,s,p0 in data)/len(data)*mi([x for x in data if x[2]==p])
               for p in orientations)

def cv_gain(data):
    # Heldout log-loss on alternating train-only pilot rows; no future source.
    left=data[::2];right=data[1::2]
    def fit_predict(reference,validation,conditional):
        counts=Counter()
        for m,s,p in reference:
            counts[(p,s,m)]+=1
            counts[(p,s,None)]+=1
            counts[(p,None,m)]+=1
            counts[(p,None,None)]+=1
        total=0.
        for m,s,p in validation:
            if conditional:
                numerator=counts[(p,s,m)]+1.
                denominator=counts[(p,s,None)]+2.
            else:
                numerator=counts[(p,None,m)]+1.
                denominator=counts[(p,None,None)]+2.
            total-=math.log(numerator/denominator)
        return total/len(validation)
    return .5*((fit_predict(left,right,False)-fit_predict(left,right,True))+
               (fit_predict(right,left,False)-fit_predict(right,left,True)))

def pilot():
    assert not set(SEEDS)&set(RESERVED_SEEDS)
    assert not set(FAMILIES)&set(RESERVED_FAMILIES)
    rows=[];information=[];switch=total_switch=0
    for seed in SEEDS:
        for family in FAMILIES:
            for ci in range(4):
                sample=anchors(seed,family,ci)
                public=calibration(sample)
                generated=[obs(seed,role,family,ci,9000+role) for role in range(3)]
                truth=relation([r[0] for r in generated],family)
                orientation=generated[0][3]
                answer={"privileged_oracle":truth};trace={}
                for t,mode,measurements,o in generated:
                    information.append((mode,int(measurements[0]>=.5),o))
                for arm in ARMS[:-1]:
                    outputs=[];reads=[]
                    for _truth,_mode,values,_orientation in generated:
                        receipt=custody.evaluate_policy(values,public,lambda _:0,
                            lambda _pub,first,name=arm:choose(first.value,orientation,sample,_pub,name),
                            576,ANCHORS*5*8)
                        assert receipt.physical_reads==2 and receipt.trace[0].sensor==0
                        first,second=receipt.trace
                        outputs.append(estimate_bit(first.value,second.value,second.sensor,public)>=.5)
                        reads.append((first.sensor,second.sensor))
                    answer[arm]=relation(outputs,family);trace[arm]=reads
                rows.append(dict(seed=seed,family=family,condition=CONDITIONS[ci],
                                 orientation=orientation,truth=truth,
                                 answers=answer,read_receipts=trace,
                                 external_calibration_bytes=ANCHORS*5*8))
                if ci!=3:
                    for low,high in ((.2,.8),(.35,.65)):
                        a=choose(low,orientation,sample,public,"conditional_empirical")
                        b=choose(high,orientation,sample,public,"conditional_empirical")
                        switch+=a!=b;total_switch+=1
    scores={a:score(rows,a) for a in ARMS}
    pooled=mutual_info(information,False)
    conditioned=mutual_info(information,True)
    gain=cv_gain(information)
    fair=max(scores[a]["accuracy"] for a in ARMS[:-1])
    headroom=1-fair
    sr=switch/total_switch
    eligible=conditioned>=.02 and gain>=.01 and headroom>=.04 and sr>=.05
    return dict(schema="yggdrasil.f32.calibrated-conditional-info-pilot.v1",
       status="PRE_ORIGINAL_TRAIN_ONLY",parent="7426dc977c49ea33deff809e43fef3310ff6f0fc",
       pilot_seeds=[191800,191832],reserved_test_seeds=[192800,192812],
       families=FAMILIES,reserved_families=RESERVED_FAMILIES,
       conditions=CONDITIONS,questions=len(rows),rows=rows,scores=scores,
       first_mode_information_pooled_bits=pooled,
       first_mode_information_conditioned_on_public_polarity_bits=conditioned,
       heldout_conditional_predictive_logloss_gain_nats=gain,
       empirical_action_switch_rate=sr,headroom_vs_best_fair=headroom,
       public_orientation_is_metadata_not_hidden_mode=True,
       policy_cannot_view_hidden_mode_or_unpurchased_target_channels=True,
       target_reads_per_role=2,native_state_limit_bytes=576,
       external_calibration_bytes_per_query=ANCHORS*5*8,
       independently_born_F3_source=False,
       primary_original_not_executed=True,accepted_ref_mutation=False,paid_api_calls=0,
       verdict="PILOT_CONDITIONAL_INFORMATION_HEADROOM_ELIGIBLE_FOR_NEXT_SCIENTIFIC_GATE"
         if eligible else "PILOT_CONDITIONAL_INFORMATION_NOT_QUALIFIED_NO_ORIGINAL")

if __name__=="__main__":print(json.dumps(pilot(),indent=2,sort_keys=True))

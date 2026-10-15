"""Y-F38 TRAIN-only source-value diagnostic, not a learned-policy original.

Train-seed evaluator estimates how often the FIRST physical reading reveals a
latent sensor-reliability mode. On disjoint validation seeds it computes
predictive log-loss gains separately for informative and noninformative first
channels. All fair task policies acquire EXACTLY TWO target channels per role;
hindsight and truth upper bounds use private evaluator values only.
"""
from __future__ import annotations
import json,math,random
from collections import Counter
SEEDS=range(281800,281816)
TRAIN=range(281800,281808)
VALIDATION=range(281808,281816)
FAMILIES=(270,271,272,273)
MECHANISMS=("mode_dependent_reliability","anticorrelated_auxiliary")
CONDITIONS=("informative_first","uninformative_first")
RESERVED_SEEDS=range(282800,282816)
RESERVED_FAMILIES=(274,275,276,277)
ANCHORS=24
ARMS=("empirical_Brier","public_polarity","static_reference","evaluator_hindsight_unfair","privileged_truth_oracle")
def rng(seed,family,role,mechanism,condition,episode):
    if seed not in SEEDS or family not in FAMILIES:
        raise ValueError("unauthorized source IDs including reserved originals")
    return random.Random(47131+seed*100073+family*3727+role*313+mechanism*919+condition*97+episode*41)
def source(seed,family,role,mechanism,condition,episode):
    r=rng(seed,family,role,mechanism,condition,episode)
    truth=r.randrange(2);mode=r.randrange(2)
    polarity=1 if (family+mechanism)%2 else -1
    hint_strength=.34 if condition==0 else 0.
    first=max(0.,min(1.,.5+hint_strength*polarity*(2*mode-1)+r.gauss(0,.09)))
    channels=[first]
    for j in (1,2,3):
        preferred=(j==1 and mode==0) or (j==2 and mode==1)
        signal=.38 if preferred else .025
        noise=.11 if preferred else .23
        if j==3:signal=.18;noise=.18
        if mechanism==1 and j==2:signal=-signal;noise=.15 if preferred else .24
        if mechanism==1 and j==3:signal=.23;noise=.16
        value=max(0.,min(1.,.5+(2*truth-1)*signal+r.gauss(0,noise)))
        channels.append(value)
    return truth,mode,tuple(channels),polarity
def refs(seed,family,mechanism,condition):
    # Anchors publish truth and source observations, NOT source-private mode.
    return tuple((truth,values) for i in range(ANCHORS) for truth,mode,values,pol in
                 [source(seed,family,i%3,mechanism,condition,50000+i*17)])
def correlations(anchors):
    return tuple(sum((2*y-1)*(2*v[j]-1) for y,v in anchors)/len(anchors) for j in range(4))
def bit_prob(value,j,corr):
    signal=(2*value-1)*corr[j]/(abs(corr[j])+.05)
    return 1/(1+math.exp(-max(-20,min(20,5*signal))))
def choose(method,first,polarity,anchors,corr):
    if method=="public_polarity":
        return 1 if ((first-.5)*polarity)<0 else 2
    if method=="static_reference":
        return max((1,2,3),key=lambda j:(abs(corr[j]),-j))
    if method=="empirical_Brier":
        losses=[]
        for j in (1,2,3):
            loss=mass=0.
            for y,v in anchors:
                w=math.exp(-10*abs(v[0]-first))
                p=bit_prob(v[j],j,corr)
                loss+=w*(p-y)**2;mass+=w
            losses.append(loss/max(1e-10,mass))
        return (1,2,3)[min(range(3),key=lambda i:(losses[i],i))]
    raise ValueError(method)
class Port:
    def __init__(self,values):self._values=values;self.trace=[]
    def buy(self,j):
        if len(self.trace)>=2 or any(prev==j for prev,v in self.trace):
            raise ValueError("duplicate or third target purchase")
        value=self._values[j]
        self.trace.append((j,value))
        return value
def truth_task(bits,family):
    if family%2==0:return bool(bits[0]^bits[1]^bits[2])
    return sum(bool(z) for z in bits)>=2
def fraction_good(rows,arm):
    correct=sum(r["answers"][arm]==r["truth"] for r in rows)
    return dict(correct=correct,total=len(rows),accuracy=correct/len(rows))
def mode_statistics(samples):
    # out-of-fold evaluator-only population statistics, never policy training
    # source-private mode: 1 if the more reliable sensor is channel 2.
    counts=Counter()
    for mode,sign,condition in samples:
        counts[(condition,mode,sign)]+=1
    return counts
def conditional_information(records):
    # I(mode; public-signed first-bin | instrument condition) in bits.
    groups={}
    for mode,sign,condition in records:
        groups.setdefault(condition,[]).append((mode,sign))
    info={}
    for condition,values in groups.items():
        joint=Counter(values);mode=Counter(x for x,y in values);sign=Counter(y for x,y in values)
        n=len(values)
        info[condition]=sum(v/n*math.log2(v*n/(mode[k[0]]*sign[k[1]])) for k,v in joint.items() if v)
    return info
def holdout_logloss(training,validation):
    # Fixed two-level smoothed empirical evaluator trained on disjoint SEEDS.
    count=Counter(training)
    results={}
    for condition in range(2):
        sub=[(mode,sign) for mode,sign,c in validation if c==condition]
        baseline=conditional=0.
        for mode,sign in sub:
            positives=sum(count[(m,s,c)] for m in (1,) for s in (0,1) for c in (0,1))
            all_count=sum(count[(m,s,c)] for m in (0,1) for s in (0,1) for c in (0,1))
            p0=(positives+1)/(all_count+2)
            cond_positive=sum(count[(1,sign,c)] for c in (0,1))
            cond_total=sum(count[(m,sign,c)] for m in (0,1) for c in (0,1))
            p1=(cond_positive+1)/(cond_total+2)
            baseline-=math.log(p0 if mode else (1-p0))
            conditional-=math.log(p1 if mode else (1-p1))
        results[CONDITIONS[condition]]=dict(rows=len(sub),baseline=baseline/len(sub),
          conditional=conditional/len(sub),gain=(baseline-conditional)/len(sub))
    return results
def run():
    if not set(TRAIN).isdisjoint(VALIDATION) or not set(SEEDS).isdisjoint(RESERVED_SEEDS):
        raise ValueError("disjoint identity source violated")
    rows=[];private_train=[];private_validation=[]
    for seed in SEEDS:
      for family in FAMILIES:
       for mechanism in range(2):
        for condition in range(2):
            anchors=refs(seed,family,mechanism,condition)
            corr=correlations(anchors)
            samples=[source(seed,family,role,mechanism,condition,9000+role) for role in range(3)]
            for y,mode,channel,pol in samples:
                signed=int((channel[0]-.5)*pol>=0)
                (private_train if seed in TRAIN else private_validation).append((mode,signed,condition))
            target=truth_task([y for y,mode,channel,pol in samples],family)
            answers={"privileged_truth_oracle":target}
            receipts={}
            for method in ("empirical_Brier","public_polarity","static_reference"):
                chosen_bits=[];traces=[]
                for y,mode,channels,polarity in samples:
                    port=Port(channels);first=port.buy(0)
                    j=choose(method,first,polarity,anchors,corr)
                    second=port.buy(j)
                    assert len(port.trace)==2 and port.trace[0][0]==0 and port.trace[1][0]!=0
                    chosen_bits.append(bit_prob(second,j,corr)>=.5)
                    traces.append([port.trace[0][0],port.trace[1][0]])
                answers[method]=truth_task(chosen_bits,family)
                receipts[method]=traces
            # HINDSIGHT IS PRIVILEGED AND UNATTAINABLE: direct evaluator
            # inspection of all unpurchased target values and true bit.
            hindsight_bits=[]
            for y,mode,channels,polarity in samples:
                best=next((j for j in (1,2,3) if (bit_prob(channels[j],j,corr)>=.5)==bool(y)),3)
                hindsight_bits.append(bit_prob(channels[best],best,corr)>=.5)
            answers["evaluator_hindsight_unfair"]=truth_task(hindsight_bits,family)
            rows.append(dict(seed=seed,family=family,mechanism=MECHANISMS[mechanism],
                condition=CONDITIONS[condition],truth=target,answers=answers,
                fair_two_paid_read_receipts=receipts,public_reference_anchors=len(anchors)))
    test_loss=holdout_logloss(private_train,private_validation)
    information=conditional_information(private_validation)
    all_scores={a:fraction_good(rows,a) for a in ARMS}
    condition_scores={c:{a:fraction_good([r for r in rows if r["condition"]==c],a) for a in ARMS} for c in CONDITIONS}
    base_best=max(all_scores[a]["accuracy"] for a in ("empirical_Brier","public_polarity","static_reference"))
    hindsight_headroom=all_scores["evaluator_hindsight_unfair"]["accuracy"]-base_best
    # A switch under a causal first-value intervention is only evidence that
    # a policy reacts; heldout logloss separately tests whether it reacts well.
    informative_switch=0;interventions=0
    for seed in SEEDS:
      for family in FAMILIES:
        for mechanism in range(2):
            anchors=refs(seed,family,mechanism,0);corr=correlations(anchors)
            pol=source(seed,family,0,mechanism,0,9000)[3]
            informative_switch+=choose("public_polarity",.2,pol,anchors,corr)!=choose("public_polarity",.8,pol,anchors,corr)
            interventions+=1
    passed=(test_loss["informative_first"]["gain"]>=.04 and information[1 if False else 0]>=.10
            and hindsight_headroom>=.04 and informative_switch/interventions>=.10)
    return dict(schema="yggdrasil.f38.sensor-information-source.trainonly.v1",
        stage="SOURCE_DIAGNOSTIC_NOT_LEARNED_ORIGINAL",
        seeds=[SEEDS.start,SEEDS.stop],training_seeds=[TRAIN.start,TRAIN.stop],
        validation_seeds=[VALIDATION.start,VALIDATION.stop],families=FAMILIES,
        conditions=CONDITIONS,mechanisms=MECHANISMS,
        reserved_original_seeds=[RESERVED_SEEDS.start,RESERVED_SEEDS.stop],
        reserved_original_families=RESERVED_FAMILIES,
        questions=len(rows),validation_private_records=len(private_validation),
        heldout_mode_logloss=test_loss,validation_mode_conditional_MI_bits={CONDITIONS[c]:v for c,v in information.items()},
        hindsight_upper_bound_headroom=hindsight_headroom,causal_polarity_switch_rate=informative_switch/interventions,
        scores=all_scores,by_condition=condition_scores,rows=rows,
        fair_policy_paid_reads_per_role=2,evaluator_only_privileged_hindsight_not_reachable_by_policy=True,
        source_independently_born_F3=False,primary_original_not_executed=True,
        verdict="TRAIN_ONLY_SENSOR_INFORMATION_FEASIBLE" if passed else "TRAIN_ONLY_SENSOR_INFORMATION_NOT_QUALIFIED",
        accepted_ref_mutation=False,paid_api_calls=0)
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

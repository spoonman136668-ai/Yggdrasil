"""Y-F39: train observation-credibility gate from PUBLIC reference features.

A six-weight logistic gate learns from training-only examples which first
source readings carry latent-mode information. At evaluation the gate receives
only public labeled reference readings, public polarity and the FIRST paid
target reading. Hidden source type, truth, latent mode and unpurchased channels
are never sent to the action callback. All fair arms get exactly two purchases.
This is synthetic development, not independently sourced F3 evidence.
"""
import json,math,random

TRAIN=range(291800,291816)
TRAIN_FAMILIES=(280,281,282)
EVAL=range(291816,291832)
EVAL_FAMILIES=(284,285,286,287)
RESERVED=range(292800,292816)
RESERVED_FAMILIES=(288,289,290,291)
MECHANISMS=("conditional_source","anticorrelated_source")
CONDITIONS=("informative","noninformative")
ARMS=("learned_trust_gate","conditional_empirical_Brier","public_polarity","variance_threshold_gate","static_reference","first_masked_ablation","privileged_truth_oracle")
ANCHORS=24
WEIGHTS=6
READS=2

def rng(seed,family,role,mechanism,condition,episode):
    if not ((seed in TRAIN and family in TRAIN_FAMILIES) or
            (seed in EVAL and family in EVAL_FAMILIES)):
        raise ValueError("reserved source identity forbidden")
    return random.Random(seed*101071+family*9877+role*313+mechanism*199+condition*821+episode*41+39017)

def source(seed,family,role,mechanism,condition,episode):
    r=rng(seed,family,role,mechanism,condition,episode)
    truth=r.randrange(2)
    latent=r.randrange(2)
    polarity=1 if (family+mechanism)%2 else -1
    # Inferrable calibration signature: bimodal latent mixture versus
    # unimodal first-source noise; truth and mode remain unobserved.
    strength=.33 if condition==0 else 0.0
    first=min(1,max(0,.5+polarity*(2*latent-1)*strength+r.gauss(0,.095)))
    channels=[first]
    for j in (1,2,3):
        preferred=(j==1 and latent==0) or (j==2 and latent==1)
        signal=.38 if preferred else .025
        noise=.11 if preferred else .23
        if j==3:signal=.18;noise=.18
        if mechanism==1 and j==2:signal=-signal;noise=.15 if preferred else .24
        if mechanism==1 and j==3:signal=.23;noise=.16
        channels.append(min(1,max(0,.5+(2*truth-1)*signal+r.gauss(0,noise))))
    return truth,latent,tuple(channels),polarity

def public_refs(seed,family,mechanism,condition):
    return tuple((y,values) for i in range(ANCHORS)
         for y,latent,values,pol in [source(seed,family,i%3,mechanism,condition,50000+i*17)])

def correlations(refs):
    return tuple(sum((2*y-1)*(2*values[j]-1) for y,values in refs)/len(refs) for j in range(4))

def public_features(refs,corr,first,polarity):
    a=[v[0] for _,v in refs]
    mean=sum(a)/len(a)
    variance=sum((v-mean)**2 for v in a)/len(a)
    # Bimodal first channel strongly separates a useful latent-mode hint
    # from uninformative unimodal noise, without true mode/condition labels.
    proportion_outer=sum(abs(v-.5)>.21 for v in a)/len(a)
    signed=(first-.5)*polarity
    return (1.,variance*10.,proportion_outer,abs(signed),
            abs(corr[1])-abs(corr[2]),abs(corr[3]))

def sigmoid(z):
    return 1/(1+math.exp(-max(-24,min(24,z))))

def train_gate():
    rows=[]
    for seed in TRAIN:
      for family in TRAIN_FAMILIES:
       for mech in range(2):
        for condition in range(2):
            refs=public_refs(seed,family,mech,condition)
            corr=correlations(refs)
            for role in range(3):
                truth,latent,values,pol=source(seed,family,role,mech,condition,9000+role)
                features=public_features(refs,corr,values[0],pol)
                # TRAIN-only source truth may supervise the gate, but it is
                # never a runtime feature and is hidden for all EVAL cases.
                rows.append((features,float(condition==0)))
    w=[0.]*WEIGHTS
    for _ in range(220):
        gradient=[0.]*WEIGHTS
        for x,y in rows:
            error=sigmoid(sum(v*z for v,z in zip(w,x)))-y
            for j,val in enumerate(x):gradient[j]+=error*val
        for j in range(WEIGHTS):w[j]-=.22*(gradient[j]/len(rows)+.0004*w[j])
    return w,len(rows)

def bit_prob(reading,sensor,corr):
    s=(2*reading-1)*corr[sensor]/(abs(corr[sensor])+.05)
    return sigmoid(5*s)

def brier_choice(first,refs,corr):
    errors=[]
    for j in (1,2,3):
        loss=mass=0.
        for truth,v in refs:
            weight=math.exp(-10*abs(v[0]-first))
            p=bit_prob(v[j],j,corr)
            loss+=weight*(p-truth)**2;mass+=weight
        errors.append(loss/max(mass,1e-10))
    return (1,2,3)[min(range(3),key=lambda i:(errors[i],i))]

def choose(method,first,polarity,refs,corr,w):
    if method=="static_reference" or method=="first_masked_ablation":
        return max((1,2,3),key=lambda j:(abs(corr[j]),-j))
    if method=="conditional_empirical_Brier":
        return brier_choice(first,refs,corr)
    if method=="public_polarity":
        return 1 if ((first-.5)*polarity)<0 else 2
    if method=="variance_threshold_gate":
        features=public_features(refs,corr,first,polarity)
        trust=features[1]>.55
        return (1 if ((first-.5)*polarity)<0 else 2) if trust else brier_choice(first,refs,corr)
    if method=="learned_trust_gate":
        x=public_features(refs,corr,first,polarity)
        trust=sigmoid(sum(a*b for a,b in zip(w,x)))>=.5
        return (1 if ((first-.5)*polarity)<0 else 2) if trust else brier_choice(first,refs,corr)
    raise ValueError("unregistered fair method")

class PaidPort:
    def __init__(self,channels):self._channels=channels;self.trace=[]
    def buy(self,j):
        if len(self.trace)>=READS or any(i==j for i,v in self.trace):
            raise ValueError("third or duplicate sensor purchase")
        value=self._channels[j]
        self.trace.append((j,value))
        return value

def typed(bits,family):
    return bool(bits[0]^bits[1]^bits[2]) if family%2==0 else sum(bool(v) for v in bits)>=2

def score(rows,arm):
    n=len(rows)
    cor=sum(r["predictions"][arm]==r["truth"] for r in rows)
    fp=sum(bool(r["predictions"][arm]) and not r["truth"] for r in rows)
    fn=sum(not bool(r["predictions"][arm]) and r["truth"] for r in rows)
    return dict(correct=cor,total=n,accuracy=cor/n,fp=fp,fn=fn)

def run():
    assert not set(TRAIN)&set(EVAL)
    assert not set(EVAL)&set(RESERVED)
    w,ntrain=train_gate()
    rows=[]
    interventions=changes=0
    trust_correct=trust_total=0
    for seed in EVAL:
      for family in EVAL_FAMILIES:
       for mech in range(2):
        for condition in range(2):
            refs=public_refs(seed,family,mech,condition)
            corr=correlations(refs)
            targets=[source(seed,family,role,mech,condition,9000+role) for role in range(3)]
            truth=typed([t[0] for t in targets],family)
            predictions={"privileged_truth_oracle":truth}
            receipts={}
            for method in ARMS[:-1]:
                guesses=[]
                trace=[]
                for y,latent,channels,polarity in targets:
                    port=PaidPort(channels)
                    first=port.buy(0)
                    second_index=choose(method,first,polarity,refs,corr,w)
                    read=port.buy(second_index)
                    if len(port.trace)!=2 or port.trace[0][0]!=0 or second_index not in (1,2,3):
                        raise ValueError("purchase custody violation")
                    guesses.append(bit_prob(read,second_index,corr)>=.5)
                    trace.append([port.trace[0][0],port.trace[1][0]])
                    if method=="learned_trust_gate":
                        x=public_features(refs,corr,first,polarity)
                        estimate=sigmoid(sum(a*b for a,b in zip(w,x)))
                        trust_correct+=(estimate>=.5)==(condition==0)
                        trust_total+=1
                predictions[method]=typed(guesses,family)
                receipts[method]=trace
            pol=targets[0][3]
            for low,high in ((.2,.8),(.35,.65)):
                a=choose("learned_trust_gate",low,pol,refs,corr,w)
                b=choose("learned_trust_gate",high,pol,refs,corr,w)
                changes+=a!=b;interventions+=1
            rows.append(dict(seed=seed,family=family,mechanism=MECHANISMS[mech],
                condition=CONDITIONS[condition],truth=truth,predictions=predictions,
                purchases=receipts,public_reference_anchors=len(refs)))
    scores={arm:score(rows,arm) for arm in ARMS}
    by_condition={c:{a:score([r for r in rows if r["condition"]==c],a) for a in ARMS}
                  for c in CONDITIONS}
    fair=("conditional_empirical_Brier","public_polarity","variance_threshold_gate","static_reference","first_masked_ablation")
    gain=scores["learned_trust_gate"]["accuracy"]-max(scores[a]["accuracy"] for a in fair)
    nondegrade=all(by_condition[c]["learned_trust_gate"]["accuracy"]>=max(by_condition[c][a]["accuracy"] for a in fair) for c in CONDITIONS)
    passed=(gain>=.02 and nondegrade and changes>0 and
            scores["learned_trust_gate"]["correct"]>scores["first_masked_ablation"]["correct"])
    return dict(schema="yggdrasil.f39.observation-trust.trainonly.v1",
        stage="NEW_TRAIN_ONLY_LEARNED_TRUST_NO_PRIMARY_ORIGINAL",
        train_seeds=[TRAIN.start,TRAIN.stop],train_families=TRAIN_FAMILIES,
        eval_seeds=[EVAL.start,EVAL.stop],eval_families=EVAL_FAMILIES,
        reserved_original_seeds=[RESERVED.start,RESERVED.stop],
        reserved_original_families=RESERVED_FAMILIES,
        public_anchors_per_case=ANCHORS,train_examples=ntrain,
        learned_trust_weights=w,learned_coefficient_bytes=WEIGHTS*8,
        native_core_limit_bytes=576,external_reference_bytes_per_case=ANCHORS*5*8,
        native_interpreter_heap_independently_unverified=True,
        purchased_target_reads_per_role=2,questions=len(rows),
        trusted_condition_label_hidden_at_inference=True,
        source_private_truth_and_mode_hidden_at_inference=True,
        trust_classification_accuracy=trust_correct/trust_total,
        first_read_intervention_action_switch_rate=changes/interventions,
        scores=scores,by_condition=by_condition,rows=rows,
        verdict="TRAIN_ONLY_TRUST_GATE_LEARNED_GAIN" if passed else "TRAIN_ONLY_TRUST_GATE_NO_QUALIFIED_GAIN",
        same_repo_synthetic_source_not_F3=True,primary_original_not_executed=True,
        accepted_ref_mutation=False,paid_api_calls=0)
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

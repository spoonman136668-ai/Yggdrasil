"""Y-F41: causal first-observation decision-value source diagnostic.

Fresh disjoint sensor mechanisms; the first-channel marginal is matched between
coupled and decoupled modes. Fair policies can see only public labeled
calibration and values physically purchased via the two-read port. Evaluator
may compare private hindsight; it is NOT a deployable policy or F3 evidence.
"""
import json,random,math
from collections import Counter

SEEDS=range(312800,312816)
FAMILIES=(364,365,366,367)
RESERVED=range(313800,313816)
RESERVED_FAMILIES=(368,369,370,371)
CONDITIONS=("coupled","decoupled");MECHANISMS=("standard","anticorrelated")
ANCHORS=24;READS=2
ARMS=("conditional_empirical_Brier","public_conditional_expected_bit_error",
      "best_static","first_value_masked","private_hindsight_oracle_unfair")
def rng(seed,family,role,mech,condition,episode):
    if seed not in SEEDS or family not in FAMILIES:raise ValueError("reserved source denied")
    return random.Random(seed*17749+family*11731+role*541+mech*313+condition*59+episode*29+47011)
def source(seed,family,role,mech,condition,episode):
    r=rng(seed,family,role,mech,condition,episode)
    truth=r.randrange(2);mode=r.randrange(2)
    polarity=1 if (family+mech)%2 else -1
    sign=(2*mode-1) if condition==0 else r.choice((-1,1))
    first=max(0.,min(1.,.5+.30*polarity*sign+r.gauss(0,.09)))
    values=[first]
    for j in (1,2,3):
        selected=(j==1 and mode==0) or (j==2 and mode==1)
        amplitude=.40 if selected else .04
        noise=.12 if selected else .24
        if j==3:amplitude=.19;noise=.18
        if mech==1 and j==2:amplitude=-amplitude;noise=.16 if selected else .25
        if mech==1 and j==3:amplitude=.24;noise=.16
        value=max(0.,min(1.,.5+(2*truth-1)*amplitude+r.gauss(0,noise)))
        values.append(value)
    return truth,mode,tuple(values),polarity
def calibration(seed,family,mech,condition):
    # Same public reference anchor count across all arms; no hidden
    # condition/mode is included in reference records.
    return tuple((truth,vals) for i in range(ANCHORS)
      for truth,mode,vals,pol in [source(seed,family,i%3,mech,condition,50000+i*13)])
def reliabilities(references):
    return tuple(sum((2*y-1)*(2*v[j]-1) for y,v in references)/len(references) for j in range(4))
def sigmoid(x):return 1/(1+math.exp(-max(-20,min(20,x))))
def bit_prob(v,j,corr):
    return sigmoid(5*(2*v-1)*corr[j]/(abs(corr[j])+.05))
def empirical_loss(first,ref,corr):
    risks=[]
    for j in (1,2,3):
        num=den=0.
        for y,v in ref:
            weight=math.exp(-10*abs(v[0]-first))
            p=bit_prob(v[j],j,corr)
            num+=weight*(p-y)**2;den+=weight
        risks.append(num/max(den,1e-12))
    return risks
def posterior_expected_error(first,ref,corr):
    # Leave-one-reference-out shrinkage protects source sparsity.
    # Computes expected future bit *error*, rather than matching labels
    # or revealing mode. This can be estimated solely from public anchors.
    vals=empirical_loss(first,ref,corr)
    prior=[]
    for j in (1,2,3):
        prior.append(sum((bit_prob(v[j],j,corr)-y)**2 for y,v in ref)/len(ref))
    # Adaptive mixing by effective sample mass near bought first value.
    weights=[math.exp(-10*abs(v[0]-first)) for y,v in ref]
    eff=(sum(weights)**2)/(sum(w*w for w in weights)+1e-12)
    blend=eff/(eff+12.)
    return [blend*conditional+(1-blend)*global_ for conditional,global_ in zip(vals,prior)]
def choose(method,first,ref,corr):
    if method=="best_static" or method=="first_value_masked":
        return max((1,2,3),key=lambda j:(abs(corr[j]),-j))
    if method=="conditional_empirical_Brier":
        risk=empirical_loss(first,ref,corr)
    elif method=="public_conditional_expected_bit_error":
        risk=posterior_expected_error(first,ref,corr)
    else:raise ValueError("unsupported policy")
    return (1,2,3)[min(range(3),key=lambda i:(risk[i],i))]
class Port:
    def __init__(self,channels):
        self.__channels=channels;self.trace=[]
    def buy(self,j):
        if len(self.trace)>=READS or any(k==j for k,v in self.trace):
            raise ValueError("third/duplicate paid target denied")
        val=self.__channels[j];self.trace.append((j,val));return val
def task(bits,fam):
    return bool(bits[0]^bits[1]^bits[2]) if fam%2==0 else sum(bool(x) for x in bits)>=2
def count(rows,arm):
    n=len(rows)
    c=sum(r["predictions"][arm]==r["truth"] for r in rows)
    fp=sum(bool(r["predictions"][arm]) and not r["truth"] for r in rows)
    fn=sum(not bool(r["predictions"][arm]) and r["truth"] for r in rows)
    return dict(total=n,correct=c,accuracy=c/n,fp=fp,fn=fn)
def run():
    assert not set(SEEDS)&set(RESERVED)
    assert not set(FAMILIES)&set(RESERVED_FAMILIES)
    rows=[];switch=total_switch=0
    first_stats={condition:[] for condition in CONDITIONS}
    for seed in SEEDS:
      for family in FAMILIES:
       for mech in range(2):
        for cond in range(2):
            ref=calibration(seed,family,mech,cond);corr=reliabilities(ref)
            target=[source(seed,family,r,mech,cond,9000+r) for r in range(3)]
            first_stats[CONDITIONS[cond]].extend(v[0] for truth,mode,v,pol in target)
            actual=task([truth for truth,mode,v,pol in target],family)
            predictions={};receipts={}
            # Private hindsight answer ceiling is evaluator-only; not a real
            # two-purchase decision policy and is not counted as a fair arm.
            predictions["private_hindsight_oracle_unfair"]=actual
            for arm in ARMS[:-1]:
                bits=[];trace=[]
                for truth,mode,vals,pol in target:
                    port=Port(vals);first=port.buy(0)
                    j=choose(arm,first,ref,corr)
                    second=port.buy(j)
                    bits.append(bit_prob(second,j,corr)>=.5)
                    trace.append((port.trace[0][0],port.trace[1][0]))
                predictions[arm]=task(bits,family)
                receipts[arm]=trace
            for low,high in ((.2,.8),(.35,.65)):
                switch+=choose("public_conditional_expected_bit_error",low,ref,corr)!=choose("public_conditional_expected_bit_error",high,ref,corr)
                total_switch+=1
            rows.append(dict(seed=seed,family=family,mechanism=MECHANISMS[mech],
                condition=CONDITIONS[cond],truth=actual,predictions=predictions,
                receipts=receipts,public_anchor_count=ANCHORS,
                public_first_variance=sum((v[0]-sum(w[0] for y,w in ref)/len(ref))**2 for y,v in ref)/len(ref)))
    scores={a:count(rows,a) for a in ARMS}
    by_condition={condition:{a:count([r for r in rows if r["condition"]==condition],a) for a in ARMS} for condition in CONDITIONS}
    by_mechanism={m:{a:count([r for r in rows if r["mechanism"]==m],a) for a in ARMS} for m in MECHANISMS}
    marginal_stats={name:dict(mean=sum(v)/len(v),variance=sum((x-sum(v)/len(v))**2 for x in v)/len(v))
        for name,v in first_stats.items()}
    # This diagnostic is only eligible when the fair conditional-information
    # score provides enough genuine gain over the best static control.
    strongest=max(scores[a]["accuracy"] for a in ARMS[:2])
    gain=strongest-scores["best_static"]["accuracy"]
    ready=gain>=.02 and scores["private_hindsight_oracle_unfair"]["correct"]==len(rows)
    return dict(schema="yggdrasil.f41.causal-observation-regret.trainonly.v1",
        stage="FRESH_SOURCE_DIAGNOSTIC_NOT_LEARNED_ORIGINAL",
        seeds=[SEEDS.start,SEEDS.stop],families=FAMILIES,
        reserved_original_seeds=[RESERVED.start,RESERVED.stop],
        reserved_original_families=RESERVED_FAMILIES,
        questions=len(rows),source_conditions=CONDITIONS,source_mechanisms=MECHANISMS,
        reference_anchors=ANCHORS,physical_paid_reads_per_role=READS,
        external_reference_bytes_per_case=ANCHORS*5*8,
        first_observation_action_switch_rate=switch/total_switch,
        observed_first_channel_marginal_stats=marginal_stats,
        scores=scores,by_condition=by_condition,by_mechanism=by_mechanism,rows=rows,
        verdict="TRAIN_ONLY_ACTIONABLE_OBSERVATION_HEADROOM" if ready else "TRAIN_ONLY_NO_ACTIONABLE_OBSERVATION_HEADROOM",
        evaluator_private_source_modes_and_truth_not_passed_to_policy=True,
        native_core_576_bytes_not_runtime_measured=True,
        same_repository_source_not_F3=True,primary_original_not_executed=True,
        accepted_ref_mutation=False,paid_api_calls=0)
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

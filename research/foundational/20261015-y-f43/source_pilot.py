"""Y-F43 source-only structured reliability learner, with train/diagnostic split.

A bounded learned interaction basis predicts the downstream typed-task squared
error of acquiring each sensor, trained on disjoint labeled public training
sources. Actual diagnostic truth and latent source condition never enter choice.
This is a synthetic train-only proxy, NOT a native <=576B resident proof or F3.
"""
from __future__ import annotations
import json, math, random, struct, time
from collections import defaultdict

FIT_SEEDS = range(342000, 342008)
DIAGNOSTIC_SEEDS = range(342100, 342108)
RESERVED_SEEDS = range(343000, 343016)
FAMILIES = (400,401,402,403)
RESERVED_FAMILIES = (404,405,406,407)
MECHANISMS = ("phase_reversal","context_delay")
CONDITIONS = ("coupled","decoupled")
ANCHORS = 24
PAID_READS = 2
ARMS = ("learned_interaction_reliability","conditional_empirical_Brier",
        "public_Gaussian_kernel","fitted_Gaussian_latent_Bayes",
        "static_reference","source_variance_control","first_read_masked",
        "private_truth_oracle_unfair")
FEATURE_DIM = 12

def rng(seed, family, role, mech, cond, episode, first=False):
    if seed not in FIT_SEEDS and seed not in DIAGNOSTIC_SEEDS:
        raise ValueError("train/diagnostic/held-out identity isolation")
    if family not in FAMILIES:
        raise ValueError("nonadmitted source family")
    salt = 0 if first else 1777*cond
    return random.Random(seed*14033 + family*1109 + role*733 + mech*227 + episode*71 + salt + 431)

def source(seed, family, role, mech, cond, episode):
    common = rng(seed, family, role, mech, cond, episode, True)
    truth = common.randrange(2)
    hint = common.randrange(2)
    first = max(0., min(1., .5+.29*(2*hint-1)+common.gauss(0,.085)))
    if cond == 0:
        mode = hint ^ (role%2 if mech==0 else (episode%3==0))
    else:
        mode = rng(seed,family,role,mech,cond,episode).randrange(2)
    noise = rng(seed,family,role,mech,cond,episode+1311)
    values=[first]
    for j in (1,2,3):
        good = (j == 1 and mode == 0) or (j == 2 and mode == 1)
        amplitude = .39 if good else .035
        sigma = .12 if good else .25
        if j == 3: amplitude,sigma = (.23,.17)
        if mech == 1 and j == 2: amplitude = -amplitude
        if mech == 1 and j == 3: amplitude,sigma = (.26,.16)
        values.append(max(0.,min(1.,.5+(2*truth-1)*amplitude+noise.gauss(0,sigma))))
    return truth, mode, tuple(values)

def references(seed,family,mech,cond):
    return tuple((y,values) for i in range(ANCHORS)
                 for y,mode,values in [source(seed,family,i%3,mech,cond,50000+i*13)])

def task(bits,family):
    if family==400: return bool(bool(bits[0]) ^ bool(bits[1]) ^ bool(bits[2]))
    if family==401: return sum(bool(v) for v in bits)>=2
    if family==402: return not (bool(bits[0]) and bool(bits[1])) or bool(bits[2])
    return all(bool(v)==bool(bits[0]) for v in bits)

def reliabilities(ref):
    return tuple(sum((2*y-1)*(2*v[j]-1) for y,v in ref)/len(ref) for j in range(4))

def bit_prob(x,j,corr):
    score = max(-20.,min(20.,5*(2*x-1)*corr[j]/(abs(corr[j])+.05)))
    return 1/(1+math.exp(-score))

def feature(first,role,j,corr):
    # No source family, mechanism, condition, label, or future truth feature.
    t = 2*first-1
    c = corr[j]
    p = 1. if role%2 else -1.
    return (1.,t,t*t,t*t*t,p,p*t,p*t*t,c,c*t,c*p,abs(c),c*t*p)

def clamp(x):
    return max(0.00001,min(0.99999,x))

class LearnedTaskRisk:
    def __init__(self):
        self.weights = {j:[0.]*FEATURE_DIM for j in (1,2,3)}
        self.fit_count = 0
    def predict_risk(self,first,role,j,corr):
        f=feature(first,role,j,corr)
        z=sum(w*x for w,x in zip(self.weights[j],f))
        return 1/(1+math.exp(-max(-15.,min(15.,z))))
    def fit(self, training, epochs=12, rate=.035):
        # Inputs are public labeled TRAIN identities only, never diagnostic.
        ordered=list(training)
        for epoch in range(epochs):
            for first,role,j,corr,downstream_error in ordered:
                f=feature(first,role,j,corr)
                pred=self.predict_risk(first,role,j,corr)
                grad=(pred-downstream_error)*pred*(1-pred)
                ws=self.weights[j]
                for k in range(FEATURE_DIM):
                    ws[k]-=rate*(grad*f[k]+.00005*ws[k])
        self.fit_count=len(ordered)
        return self
    def packed_parameter_bytes(self):
        return struct.pack("<"+str(3*FEATURE_DIM)+"f", *(x for j in (1,2,3) for x in self.weights[j]))

class PurchasePort:
    def __init__(self,channels):
        self.__channels=channels
        self.trace=[]
    def buy(self,j):
        if len(self.trace)>=PAID_READS or j in [q for q,_ in self.trace]:
            raise ValueError("third or duplicate physical read denied")
        if j not in (0,1,2,3):
            raise ValueError("invalid channel")
        x=self.__channels[j]
        self.trace.append((j,x))
        return x

def empirical_risks(first,ref,corr,bandwidth=None):
    errors=[]
    for j in (1,2,3):
        n=d=0.
        for y,values in ref:
            dist=abs(values[0]-first)
            weight=math.exp(-10*dist) if bandwidth is None else math.exp(-.5*(dist/bandwidth)**2)
            n+=weight*(bit_prob(values[j],j,corr)-y)**2
            d+=weight
        errors.append(n/max(d,1.e-12))
    return errors

def fitted_gaussian_risk(first,ref,corr,bandwidth):
    # Gaussian latent calibration control with the same train-derived bandwidth
    # and public local label count; shrink conditional to pooled error.
    risks=empirical_risks(first,ref,corr,bandwidth)
    pooled=[sum((bit_prob(values[j],j,corr)-y)**2 for y,values in ref)/len(ref) for j in (1,2,3)]
    eff=sum(math.exp(-.5*((values[0]-first)/bandwidth)**2) for y,values in ref)
    blend=eff/(eff+8)
    return [blend*r+(1-blend)*p for r,p in zip(risks,pooled)]

def select(arm,first,role,ref,corr,learner,bandwidth):
    if arm=="learned_interaction_reliability":
        losses=[learner.predict_risk(first,role,j,corr) for j in (1,2,3)]
    elif arm=="conditional_empirical_Brier":
        losses=empirical_risks(first,ref,corr)
    elif arm=="public_Gaussian_kernel":
        losses=empirical_risks(first,ref,corr,.17)
    elif arm=="fitted_Gaussian_latent_Bayes":
        losses=fitted_gaussian_risk(first,ref,corr,bandwidth)
    elif arm in ("static_reference","first_read_masked"):
        return max((1,2,3),key=lambda j:(abs(corr[j]),-j))
    elif arm=="source_variance_control":
        means=[sum(v[j] for y,v in ref)/len(ref) for j in (1,2,3)]
        variances=[sum((v[j]-means[j-1])**2 for y,v in ref)/len(ref) for j in (1,2,3)]
        return max((1,2,3),key=lambda j:(variances[j-1],-j))
    else:
        raise ValueError("unapproved selector")
    return (1,2,3)[min(range(3),key=lambda i:(losses[i],i))]

def training_examples(seed_subset=FIT_SEEDS, family_subset=FAMILIES):
    # Downstream supervised target: squared task-outcome error after buying j
    # for one role while other roles use the public static reference choice.
    for seed in seed_subset:
      if seed not in FIT_SEEDS: raise ValueError("training only on fit sources")
      for family in family_subset:
       for mech in range(2):
        for cond in range(2):
          ref=references(seed,family,mech,cond)
          corr=reliabilities(ref)
          static=max((1,2,3),key=lambda j:(abs(corr[j]),-j))
          for episode in range(24):
            target=[source(seed,family,role,mech,cond,70000+episode*17) for role in range(3)]
            true_task=task([q[0] for q in target],family)
            for role in range(3):
              for j in (1,2,3):
                predicted=[]
                for r,(truth,mode,vals) in enumerate(target):
                    selected=j if r==role else static
                    predicted.append(bit_prob(vals[selected],selected,corr)>=.5)
                pred_task=task(predicted,family)
                err=float(pred_task!=true_task)
                yield target[role][2][0], role, j, corr, err

def fit_bandwidth(training_refs):
    # Fit only on fit-cohort labeled public references; not diagnostic cases.
    scored=[]
    for bandwidth in (.12,.17,.25):
        total=0.
        for first,ref,corr,truth,channels in training_refs:
            for j,loss in zip((1,2,3),fitted_gaussian_risk(first,ref,corr,bandwidth)):
                total+=(loss-(bit_prob(channels[j],j,corr)-truth)**2)**2
        scored.append((total,bandwidth))
    return min(scored)[1]

def public_bandwidth_training(seed_subset=(342000,342001)):
    for seed in seed_subset:
      for family in FAMILIES:
       for mech in range(2):
        for cond in range(2):
          ref=references(seed,family,mech,cond)
          corr=reliabilities(ref)
          for role in range(3):
            y,mode,v=source(seed,family,role,mech,cond,90000+role)
            yield v[0],ref,corr,y,v

def recount(rows,arm):
    n=len(rows)
    correct=sum(r["predictions"][arm]==r["truth"] for r in rows)
    fp=sum(bool(r["predictions"][arm]) and not r["truth"] for r in rows)
    fn=sum(not bool(r["predictions"][arm]) and r["truth"] for r in rows)
    return dict(correct=correct,total=n,accuracy=correct/n,fp=fp,fn=fn)

def run():
    assert not set(FIT_SEEDS)&set(DIAGNOSTIC_SEEDS)
    assert not set(FIT_SEEDS)&set(RESERVED_SEEDS)
    assert not set(DIAGNOSTIC_SEEDS)&set(RESERVED_SEEDS)
    assert not set(FAMILIES)&set(RESERVED_FAMILIES)
    start=time.perf_counter()
    learner=LearnedTaskRisk().fit(training_examples())
    bandwidth=fit_bandwidth(tuple(public_bandwidth_training()))
    rows=[]
    for seed in DIAGNOSTIC_SEEDS:
      for family in FAMILIES:
       for mech in range(2):
        for cond in range(2):
          ref=references(seed,family,mech,cond)
          corr=reliabilities(ref)
          targets=[source(seed,family,role,mech,cond,95000+role) for role in range(3)]
          truth=task([t[0] for t in targets],family)
          preds={"private_truth_oracle_unfair":truth}
          receipts={}
          for arm in ARMS[:-1]:
            bits=[];bought=[]
            for role,(hidden_true,hidden_mode,values) in enumerate(targets):
                port=PurchasePort(values)
                first=port.buy(0)
                j=select(arm,first,role,ref,corr,learner,bandwidth)
                measured=port.buy(j)
                bits.append(bit_prob(measured,j,corr)>=.5)
                bought.append([int(t[0]) for t in port.trace])
            preds[arm]=task(bits,family)
            receipts[arm]=bought
          rows.append(dict(seed=seed,family=family,mechanism=MECHANISMS[mech],
                           condition=CONDITIONS[cond],truth=truth,
                           predictions=preds,receipts=receipts,
                           public_anchor_count=len(ref)))
    scores={a:recount(rows,a) for a in ARMS}
    by_mechanism={m:{a:recount([r for r in rows if r["mechanism"]==m],a)
                       for a in ARMS} for m in MECHANISMS}
    by_condition={c:{a:recount([r for r in rows if r["condition"]==c],a)
                       for a in ARMS} for c in CONDITIONS}
    fair=ARMS[1:-1]
    best=max(scores[a]["accuracy"] for a in fair)
    gain=scores["learned_interaction_reliability"]["accuracy"]-best
    masked_gain=scores["learned_interaction_reliability"]["accuracy"]-scores["first_read_masked"]["accuracy"]
    no_mechanism_degrade=all(by_mechanism[m]["learned_interaction_reliability"]["correct"] >=
         max(by_mechanism[m][a]["correct"] for a in fair) for m in MECHANISMS)
    passed=gain>=.02 and masked_gain>0 and no_mechanism_degrade
    return dict(schema="yggdrasil.f43.learned-typed-task-reliability.trainonly.v1",
       stage="TRAIN_ONLY_LEARNED_PROXY_NOT_NATIVE_OR_F3",
       fit_seeds=[FIT_SEEDS.start,FIT_SEEDS.stop],
       diagnostic_seeds=[DIAGNOSTIC_SEEDS.start,DIAGNOSTIC_SEEDS.stop],
       reserved_original_seeds=[RESERVED_SEEDS.start,RESERVED_SEEDS.stop],
       families=list(FAMILIES),reserved_original_families=list(RESERVED_FAMILIES),
       questions=len(rows),public_reference_anchors=ANCHORS,physical_reads_per_role=PAID_READS,
       train_examples=learner.fit_count,parameter_payload_bytes=len(learner.packed_parameter_bytes()),
       parameter_payload_is_not_native_resident_measurement=True,
       fitted_gaussian_bandwidth=bandwidth,elapsed_seconds=time.perf_counter()-start,
       scores=scores,by_mechanism=by_mechanism,by_condition=by_condition,rows=rows,
       gain_over_strongest_fair=gain,masked_first_ablation_gain=masked_gain,
       no_unseen_mechanism_degradation=no_mechanism_degrade,
       verdict="TRAIN_ONLY_LEARNED_RELIABILITY_HEADROOM" if passed else "TRAIN_ONLY_LEARNED_RELIABILITY_NOT_QUALIFIED",
       diagnostic_labels_never_fit=True,private_modes_and_truth_evaluator_only=True,
       independent_F3_custody=False,primary_original_not_executed=True,
       native_576_byte_resident_physically_qualified=False,accepted_ref_mutation=False,paid_api_calls=0)

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))

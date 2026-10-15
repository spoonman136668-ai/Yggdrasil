"""Y-F42: matched-first-marginal observable-decision source diagnostic.

Both source conditions share EXACT same first-channel draws per matched
seed/family/mechanism/role/episode. Only the coupling from its public hint to
the private reliability mode differs. Thus mean/variance shortcuts have no
information about condition; private modes and unpurchased source values are
evaluator-only. No learned F42 policy or independently born F3 source.
"""
from __future__ import annotations
import importlib.util,random,math,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent
p=H.parent/"20261015-y-f41"/"source_pilot.py"
s=importlib.util.spec_from_file_location("yf42_prior_evaluator",p)
prior=importlib.util.module_from_spec(s);sys.modules[s.name]=prior;s.loader.exec_module(prior)
SEEDS=range(322800,322816)
FAMILIES=(380,381,382,383)
RESERVED=range(323800,323816)
RESERVED_FAMILIES=(384,385,386,387)
CONDITIONS=("coupled","decoupled")
MECHANISMS=("normal","anticorrelated")
ANCHORS=24;READS=2
ARMS=("conditional_empirical_Brier","public_Gaussian_mode_posterior",
      "static_reference","first_masked","private_condition_oracle_unfair")
def rng(seed,family,role,mech,condition,episode,first=False):
    if seed not in SEEDS or family not in FAMILIES:
        raise ValueError("reserved source not authorized")
    # Absolutely identical first-channel draws across paired conditions.
    salt=0 if first else condition*633
    return random.Random(971+seed*17137+family*2207+role*547+mech*131+episode*41+salt)
def source(seed,family,role,mech,cond,episode):
    common=rng(seed,family,role,mech,cond,episode,True)
    truth=common.randrange(2)
    hint=common.randrange(2)
    polarity=1 if (family+mech)%2 else -1
    first=max(0.,min(1.,.5+.3*polarity*(2*hint-1)+common.gauss(0,.085)))
    # Condition alters *causal coupling* only, not the marginal first stream.
    mode=hint if cond==0 else rng(seed,family,role,mech,cond,episode).randrange(2)
    noise=rng(seed,family,role,mech,cond,episode+991)
    values=[first]
    for j in (1,2,3):
        good=(j==1 and mode==0) or (j==2 and mode==1)
        amp=.4 if good else .03
        sigma=.12 if good else .23
        if j==3:amp=.21;sigma=.17
        if mech==1 and j==2:amp=-amp;sigma=.17 if good else .245
        if mech==1 and j==3:amp=.255;sigma=.15
        values.append(max(0.,min(1.,.5+(2*truth-1)*amp+noise.gauss(0,sigma))))
    return truth,mode,tuple(values),polarity
def reference(seed,family,mech,cond):
    return tuple((truth,vals) for i in range(ANCHORS)
        for truth,mode,vals,pol in [source(seed,family,i%3,mech,cond,50000+i*13)])
def choose(method,first,ref,corr,polarity):
    if method in ("static_reference","first_masked"):
        return max((1,2,3),key=lambda j:(abs(corr[j]),-j))
    if method=="conditional_empirical_Brier":
        risks=prior.empirical_loss(first,ref,corr)
        return (1,2,3)[min(range(3),key=lambda k:(risks[k],k))]
    if method=="public_Gaussian_mode_posterior":
        # Calibration contains only observable first readings and labeled
        # channel prediction errors; it never carries source condition/mode.
        # A Gaussian kernel estimates empirical conditional expected error.
        risks=[]
        for j in (1,2,3):
            weighted=total=0.
            for truth,values in ref:
                w=math.exp(-((values[0]-first)/.17)**2/2)
                p=prior.bit_prob(values[j],j,corr)
                weighted+=w*(p-truth)**2;total+=w
            risks.append(weighted/max(total,1e-12))
        return (1,2,3)[min(range(3),key=lambda k:(risks[k],k))]
    raise ValueError(method)
def fair_incremental_gain(scored):
    # Conditional empirical Brier is a matched fair control, not candidate credit.
    baseline=max(scored[a]["accuracy"] for a in
        ("conditional_empirical_Brier","static_reference","first_masked"))
    candidate=scored["public_Gaussian_mode_posterior"]["accuracy"]
    return candidate-baseline,baseline

def run():
    assert set(SEEDS).isdisjoint(RESERVED)
    assert set(FAMILIES).isdisjoint(RESERVED_FAMILIES)
    rows=[];first_pair_values={c:[] for c in CONDITIONS}
    public_reference_first={c:[] for c in CONDITIONS}
    for seed in SEEDS:
      for family in FAMILIES:
       for mech in range(2):
        refs=[reference(seed,family,mech,cond) for cond in range(2)]
        assert all(a[1][0]==b[1][0] for a,b in zip(refs[0],refs[1]))
        assert all(a[0]==b[0] for a,b in zip(refs[0],refs[1]))
        for cond in range(2):
            ref=refs[cond]
            public_reference_first[CONDITIONS[cond]].extend(v[0] for truth,v in ref)
            corr=prior.reliabilities(ref)
            targets=[source(seed,family,role,mech,cond,9000+role) for role in range(3)]
            other=[source(seed,family,role,mech,1-cond,9000+role) for role in range(3)]
            assert all(targets[i][2][0]==other[i][2][0] for i in range(3))
            first_pair_values[CONDITIONS[cond]].extend(t[2][0] for t in targets)
            truth=prior.task([t[0] for t in targets],family)
            answers={"private_condition_oracle_unfair":truth};receipts={}
            for arm in ARMS[:-1]:
                bits=[];paid=[]
                for true_bit,mode,channels,polarity in targets:
                    port=prior.Port(channels)
                    first=port.buy(0)
                    idx=choose(arm,first,ref,corr,polarity)
                    second=port.buy(idx)
                    assert len(port.trace)==2 and port.trace[0][0]==0
                    bits.append(prior.bit_prob(second,idx,corr)>=.5)
                    paid.append((0,idx))
                answers[arm]=prior.task(bits,family)
                receipts[arm]=paid
            rows.append(dict(seed=seed,family=family,mechanism=MECHANISMS[mech],
                 condition=CONDITIONS[cond],truth=truth,predictions=answers,
                 receipts=receipts,reference_anchors=ANCHORS))
    def stats(vals):
        mu=sum(vals)/len(vals)
        return dict(mean=mu,variance=sum((v-mu)**2 for v in vals)/len(vals))
    marginal={c:stats(vals) for c,vals in first_pair_values.items()}
    reference_marginal={c:stats(vals) for c,vals in public_reference_first.items()}
    assert first_pair_values["coupled"]==first_pair_values["decoupled"]
    assert public_reference_first["coupled"]==public_reference_first["decoupled"]
    scored={a:prior.count([dict(truth=r["truth"],predictions=r["predictions"]) for r in rows],a) for a in ARMS}
    by_condition={condition:{arm:prior.count([dict(truth=r["truth"],predictions=r["predictions"])
      for r in rows if r["condition"]==condition],arm) for arm in ARMS} for condition in CONDITIONS}
    by_mechanism={mechanism:{arm:prior.count([dict(truth=r["truth"],predictions=r["predictions"])
      for r in rows if r["mechanism"]==mechanism],arm) for arm in ARMS} for mechanism in MECHANISMS}
    fair=("conditional_empirical_Brier","public_Gaussian_mode_posterior","static_reference","first_masked")
    best=max(scored[a]["accuracy"] for a in fair[:2])
    conditional_source_headroom=best-max(scored[a]["accuracy"] for a in fair[2:])
    gain,strongest_matched_fair_control=fair_incremental_gain(scored)
    # This is *source feasibility*, not a learned advancement.
    verdict=("TRAIN_ONLY_CONDITIONAL_SOURCE_FEASIBLE" if gain>=.02 and
      scored["private_condition_oracle_unfair"]["correct"]==len(rows)
      else "TRAIN_ONLY_CONDITIONAL_SOURCE_NOT_FEASIBLE")
    return dict(schema="yggdrasil.f42.matched-marginal-observation.trainonly.v1",
      stage="FRESH_TRAIN_ONLY_SOURCE_DIAGNOSTIC_NO_LEARNED_ORIGINAL",
      seeds=[SEEDS.start,SEEDS.stop],families=list(FAMILIES),
      reserved_original_seeds=[RESERVED.start,RESERVED.stop],reserved_original_families=list(RESERVED_FAMILIES),
      questions=len(rows),public_reference_anchors=ANCHORS,physical_paid_reads_per_role=READS,
      paired_first_marginals_identical=True,paired_public_reference_first_marginals_identical=True,
      observed_first_marginal_stats=marginal,reference_first_marginal_stats=reference_marginal,
      external_calibration_bytes_per_query=ANCHORS*5*8,scores=scored,by_condition=by_condition,
      by_mechanism=by_mechanism,rows=rows,verdict=verdict,
      conditional_source_headroom=conditional_source_headroom,
      candidate_over_strongest_matched_fair_gain=gain,
      strongest_matched_fair_control_accuracy=strongest_matched_fair_control,
      evaluator_private_modes_and_conditions_not_given_to_policy=True,
      native_576_byte_resident_not_physically_verified=True,independent_F3_custody=False,
      primary_original_not_executed=True,accepted_ref_mutation=False,paid_api_calls=0)
if __name__=="__main__":print(json.dumps(run(),sort_keys=True,indent=2))

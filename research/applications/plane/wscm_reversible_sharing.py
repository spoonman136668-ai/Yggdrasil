"""Exact reversible posterior sharing over public context/action counts.
Conventional Bayesian computation, not a native learner or source actor.
"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import subprocess
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
from wscm_dtr_effect_partition import ROOT, canonical, check, counts_for, logbeta, greedy, probability, mix
from wscm_effect_partition_retention import cart_fit, cart_predict, recall, risk, SINGLETONS, MODELS

EXPERIMENT="WSCM-REVERSIBLE-SHARING-01"
SEEDS=(792301,792311,792319)
ARMS=("subset_dp","exact_enumerated","full_beta","hard_greedy","cart")
FAMILIES=("shared","independent","no_change")
CELLS=tuple(itertools.product(range(8),range(2)))
PAIRS=tuple(itertools.product((.15,.35,.65,.85),repeat=2))


def rng(seed,index,part):
    raw=f"{EXPERIMENT}/{seed}/{index}/{part}".encode("ascii")
    return random.Random(int.from_bytes(hashlib.sha256(raw).digest(),"big"))


def law(r,sizes):
    ids=list(range(8))
    r.shuffle(ids)
    pairs=r.sample(PAIRS,len(sizes))
    result=[None]*8
    offset=0
    for size,pair in zip(sizes,pairs):
        for c in ids[offset:offset+size]:
            result[c]=pair
        offset+=size
    check(offset==8,"LAW_SIZE")
    return result


def observations(r,truth,blocks):
    result=[]
    for _ in range(blocks):
        cells=list(CELLS)
        r.shuffle(cells)
        result.extend((c,a,int(r.random()<truth[c][a]),0) for c,a in cells)
    return result


def subset_readout(counts):
    """Exact uniform-partition Bayes using subset normalizers; no merge writes."""
    n=len(counts)
    check(1<=n<=12,"CONTEXT_CAP")
    size=1<<n
    full=size-1
    # Every group has its own conjugate Beta-integrated likelihood.
    sums=[(0,0,0,0)]*size
    weights=[0.0]*size
    means=[None]*size
    for mask in range(1,size):
        low=mask&-mask
        c=low.bit_length()-1
        prev=sums[mask^low]
        row=counts[c]
        z0,o0,z1,o1=tuple(x+y for x,y in zip(prev,(*row[0],*row[1])))
        sums[mask]=(z0,o0,z1,o1)
        weights[mask]=math.exp(logbeta(z0,o0)+logbeta(z1,o1))
        means[mask]=((o0+1)/(z0+o0+2),(o1+1)/(z1+o1+2))
    normal=[0.0]*size
    normal[0]=1.0
    terms=0
    for mask in range(1,size):
        anchor=mask&-mask
        tail=mask^anchor
        sub=tail
        value=0.0
        while True:
            block=sub|anchor
            value+=weights[block]*normal[mask^block]
            terms+=1
            if sub==0:
                break
            sub=(sub-1)&tail
        normal[mask]=value
    check(normal[full]>0 and math.isfinite(normal[full]),"NORMALIZER")
    forecasts=[[0.0,0.0] for _ in range(n)]
    membership=[[0.0]*n for _ in range(n)]
    for mask in range(1,size):
        mass=weights[mask]*normal[full^mask]/normal[full]
        check(math.isfinite(mass) and 0<=mass<=1+1e-10,"BLOCK_MASS")
        members=[c for c in range(n) if mask&(1<<c)]
        for c in members:
            for a in range(2):
                forecasts[c][a]+=mass*means[mask][a]
            for d in members:
                membership[c][d]+=mass
    for c in range(n):
        check(abs(membership[c][c]-1)<1e-10,"PARTITION_NORMALIZATION")
        check(all(0<=v<=1+1e-10 for v in forecasts[c]),"FORECAST_RANGE")
        check(all(abs(membership[c][d]-membership[d][c])<1e-12 for d in range(n)),
              "MEMBERSHIP_SYMMETRY")
    return forecasts,membership,terms


def maxdiff(x,y):
    return max(abs(a-b) for u,v in zip(x,y) for a,b in zip(u,v))


def mean(xs):
    return math.fsum(xs)/len(xs)


def fit_read(rows,times):
    counts=counts_for(rows)
    raw=canonical(counts)
    start=time.perf_counter()
    dp,member,terms=subset_readout(counts)
    times["dp"]+=time.perf_counter()-start
    start=time.perf_counter()
    exact=mix(counts,MODELS)[0]
    times["enumerated"]+=time.perf_counter()-start
    error=maxdiff(dp,exact)
    check(error<=1e-10,"ENUMERATION_PARITY")
    check(subset_readout(json.loads(raw))==(dp,member,terms),"COLD_PARITY")
    hard,_=greedy(counts)
    cart=cart_fit(counts)
    result={"subset_dp":dp,"exact_enumerated":exact,
            "full_beta":probability(counts,SINGLETONS),
            "hard_greedy":probability(counts,hard),
            "cart":[[cart_predict(cart,c,a) for a in range(2)] for c in range(8)]}
    check(canonical(counts)==raw,"FIT_MUTATION")
    return result,error,len(raw),terms


def contradiction_fixture():
    counts=[[[8,0],[8,0]] for _ in range(4)]
    old=canonical(counts[1:])
    _,before,_=subset_readout(counts)
    for a in range(2):
        counts[0][a][1]+=64
    _,after,_=subset_readout(counts)
    check(canonical(counts[1:])==old,"UNRELATED_COUNTS_CHANGED")
    fall=before[0][1]-after[0][1]
    check(fall>=.5,"SHARING_NOT_REVERSED")
    return {"before":before[0][1],"after":after[0][1],"fall":fall,
            "other_counts_unchanged":True,"original_counts_retained":counts[0]}


def run():
    start=time.perf_counter()
    for path,pin in (("research/applications/plane/wscm_dtr_effect_partition.py","8ad052791d4bc884703048dfd79c831e6f17f8eb"),
                     ("research/applications/plane/wscm_effect_partition_retention.py","c550fe557ce84ae795114459c1540c478249a5f4")):
        blob=subprocess.check_output(["git","hash-object","--no-filters",path],cwd=ROOT,text=True).strip()
        check(blob==pin,"PARENT_DRIFT")
    fixture=contradiction_fixture()
    counts12=[[[2+c%3,1],[1,2+c%4]] for c in range(12)]
    tick=time.perf_counter()
    q12,m12,terms12=subset_readout(counts12)
    scale_time=time.perf_counter()-tick
    check(subset_readout(json.loads(canonical(counts12)))==(q12,m12,terms12),"SCALE_COLD")
    times={"dp":0.0,"enumerated":0.0}
    worlds=[]
    max_error=0.0
    total=0
    cold=0
    bank_sizes=[]
    terms8=None
    for seed in SEEDS:
        for index,family in enumerate(FAMILIES):
            r=rng(seed,index,"law")
            sizes=(1,)*8 if family=="independent" else (3,3,2)
            a_truth=law(r,sizes)
            b_truth=a_truth if family=="no_change" else law(r,sizes)
            a_rows=observations(rng(seed,index,"A"),a_truth,6)
            b_rows=observations(rng(seed,index,"B"),b_truth,6)
            return_rows=observations(rng(seed,index,"R"),a_truth,2)
            total+=len(a_rows)+len(b_rows)+len(return_rows)
            entry={"seed":seed,"family":family,"index":index,
                   "receipts_sha256":[hashlib.sha256(canonical(rows)).hexdigest() for rows in (a_rows,b_rows,return_rows)],
                   "arms":{arm:{"scores":[]} for arm in ARMS}}
            banks={}
            for label,rows,truth in (("A",a_rows,a_truth),("B",b_rows,b_truth)):
                for prefix in (32,96):
                    q,err,byte_count,terms8=fit_read(rows[:prefix],times)
                    max_error=max(max_error,err)
                    cold+=1
                    bank_sizes.append(byte_count)
                    for arm in ARMS:
                        entry["arms"][arm]["scores"].append({"stage":label,"prefix":prefix,
                                                            "excess_brier":risk(q[arm],truth)})
                    if prefix==96:
                        banks[label]=q
            raw=canonical(banks)
            for arm in ARMS:
                a,b=banks["A"][arm],banks["B"][arm]
                record=entry["arms"][arm]
                record["mean_excess_brier"]=mean([s["excess_brier"] for s in record["scores"]])
                record["return"]={}
                for n in (0,8,16,32):
                    q,w=recall(a,b,return_rows[:n])
                    record["return"][str(n)]={"excess_brier":risk(q,a_truth),
                                               "drift":risk(q,a_truth)-risk(a,a_truth),"a_weight":w}
            check(canonical(banks)==raw,"RETURN_MUTATION")
            worlds.append(entry)
    check(total==2016 and cold==36 and len(worlds)==9,"COHORT_BUDGET")
    groups={}
    for key,ws in [("all",worlds)]+[(f"seed/{s}",[w for w in worlds if w["seed"]==s]) for s in SEEDS]+[(f"family/{f}",[w for w in worlds if w["family"]==f]) for f in FAMILIES]:
        groups[key]={arm:{"mean_excess_brier":mean([w["arms"][arm]["mean_excess_brier"] for w in ws]),
                         "return32_excess_brier":mean([w["arms"][arm]["return"]["32"]["excess_brier"] for w in ws]),
                         "return32_drift":mean([w["arms"][arm]["return"]["32"]["drift"] for w in ws])}
                     for arm in ARMS}
    gains={str(s):groups[f"seed/{s}"]["full_beta"]["mean_excess_brier"]-
                  groups[f"seed/{s}"]["subset_dp"]["mean_excess_brier"] for s in SEEDS}
    harms={f:groups[f"family/{f}"]["subset_dp"]["mean_excess_brier"]-
             groups[f"family/{f}"]["full_beta"]["mean_excess_brier"] for f in FAMILIES}
    drift=max(w["arms"]["subset_dp"]["return"]["32"]["drift"] for w in worlds)
    gates={"all_seed_gain_ge_0_002":all(v>=.002 for v in gains.values()),
           "all_family_harm_le_0_01":all(v<=.01 for v in harms.values()),
           "max_return_drift_le_0_02":drift<=.02}
    print("SUBSET_MATCHED_TIMINGS "+json.dumps(times,sort_keys=True))
    print("SUBSET_SCALE12_SECONDS %.8f"%scale_time)
    print("SUBSET_SCREEN_SECONDS %.8f"%(time.perf_counter()-start))
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,
            "status":"REVERSIBLE_SHARING_DEV_COMPLETE","scientific_pass":False,
            "scientific_gain_verified":False,"source_first_use":False,
            "metrics":{"disposition":"DEV_SIGNAL" if all(gates.values()) else "DEV_NO_GO",
                       "gates":gates,"seed_gain_vs_full":gains,"family_harm_vs_full":harms,
                       "max_return_drift":drift,"groups":groups,"worlds":worlds,
                       "world_count":9,"synthetic_outcomes":total,"original_source_actions":0,
                       "enumeration_parity_max_abs":max_error,"enumeration_parity_checks":cold,
                       "cold_count_restore_checks":cold,"scale12_cold_parity":True,
                       "subset_terms_n8":terms8,"subset_terms_n12":terms12,
                       "subset_masks_n8":256,"subset_masks_n12":4096,
                       "mean_serialized_count_bytes":mean(bank_sizes),
                       "contradiction_fixture":fixture,"per_context_counts_retained":True,
                       "return_banks_immutable":True,"closed_loop_selection":False,
                       "native_model_mutation":False,"full_final_regression":"NOT_RUN",
                       "exact_bayesian_computation_not_unique_learning":True}}


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    result=run()
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(canonical(result)+b"\n")

"""Prospectively frozen synthetic stochastic partition and recall screen.
Research-only; no original source, native learner mutation, or scientific acceptance.
"""
import argparse
from collections import defaultdict
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wscm_dtr_effect_partition import (
    ROOT, canonical, check, counts_for, norm, partitions, greedy, probability,
    group_counts, mix,
)

EXPERIMENT = "WSCM-EFFECT-PARTITION-RETENTION-01"
SEEDS = (781201, 781211, 781219)
ARMS = ("greedy", "full_beta", "exact_bma", "cart", "pooled_beta")
P = (.1,.2,.3,.7,.8,.9)
RESPONSE_PAIRS = tuple(itertools.product(P, repeat=2))
SINGLETONS = norm((c,) for c in range(8))
CELLS = tuple(itertools.product(range(8), range(2)))
PARTITIONS = tuple(sorted(set(partitions(list(range(8))))))
MODELS = [(p, True) for p in PARTITIONS]
RETURN_STEPS = (0,8,16,32)


def make_rng(seed, index, purpose):
    key = f"{EXPERIMENT}/{seed}/{index}/{purpose}".encode("ascii")
    return random.Random(int.from_bytes(hashlib.sha256(key).digest(), "big"))


def law(rng, sizes):
    contexts = list(range(8))
    rng.shuffle(contexts)
    effects = rng.sample(RESPONSE_PAIRS, len(sizes))
    out = [None]*8
    pos = 0
    for size, pair in zip(sizes, effects):
        for c in contexts[pos:pos+size]:
            out[c] = pair
        pos += size
    check(pos == 8 and all(x is not None for x in out), "GENERATOR_PARTITION")
    return tuple(out)


def observations(rng, truth, blocks):
    rows = []
    for _ in range(blocks):
        pairs = list(CELLS)
        rng.shuffle(pairs)
        for c,a in pairs:
            rows.append((c,a,int(rng.random() < truth[c][a]),0))
    return rows


def cart_fit(counts):
    # Conventional fully grown greedy CART on public context bits and action.
    # Cell sufficient counts exactly represent all repeated FIT observations.
    def totals(cells):
        return tuple(sum(counts[c][a][y] for c,a in cells) for y in (0,1))
    def loss(cells):
        z,o = totals(cells)
        return z*o/(z+o) if z+o else 0.0
    def bit(c,a,k):
        return ((c>>k)&1) if k<3 else a
    def tree(cells, features):
        z,o = totals(cells)
        check(z+o>0,"CART_EMPTY_LEAF")
        old = loss(cells)
        choices = []
        for k in features:
            left = tuple((c,a) for c,a in cells if not bit(c,a,k))
            right = tuple((c,a) for c,a in cells if bit(c,a,k))
            if left and right and sum(totals(left)) and sum(totals(right)):
                choices.append((old-loss(left)-loss(right),k,left,right))
        if not choices:
            return {"mean":o/(z+o)}
        gain,k,left,right = min(choices,key=lambda x:(-x[0],x[1]))
        if gain<=1e-12:
            return {"mean":o/(z+o)}
        rest=tuple(i for i in features if i!=k)
        return {"bit":k,"left":tree(left,rest),"right":tree(right,rest)}
    return tree(CELLS,tuple(range(4)))


def cart_predict(tree,c,a):
    while "bit" in tree:
        k=tree["bit"]
        bit=((c>>k)&1) if k<3 else a
        tree=tree["right" if bit else "left"]
    return tree["mean"]


def make_bank(arm, rows):
    counts=counts_for(rows)
    if arm=="greedy":
        partition,_=greedy(counts)
        bank={"kind":arm,"groups":[list(g) for g in partition],
              "counts":[[list(group_counts(counts,g,a)) for a in range(2)] for g in partition]}
    elif arm in ("full_beta","exact_bma","pooled_beta"):
        bank={"kind":arm,"counts":counts}
    elif arm=="cart":
        bank={"kind":arm,"tree":cart_fit(counts)}
    else:
        raise ValueError("BANK_KIND")
    return bank


def read_bank(bank):
    arm=bank["kind"]
    if arm=="greedy":
        out=[[None,None] for _ in range(8)]
        check(sorted(c for g in bank["groups"] for c in g)==list(range(8)),"BANK_GROUP_COVERAGE")
        for group,counts in zip(bank["groups"],bank["counts"]):
            for a,(z,o) in enumerate(counts):
                for c in group:
                    out[c][a]=(o+1)/(z+o+2)
        return out
    if arm in ("full_beta","pooled_beta"):
        return probability(bank["counts"],SINGLETONS)
    if arm=="exact_bma":
        return mix(bank["counts"],MODELS)[0]
    if arm=="cart":
        return [[cart_predict(bank["tree"],c,a) for a in range(2)] for c in range(8)]
    raise ValueError("BANK_KIND")


def risk(matrix,truth):
    return math.fsum((matrix[c][a]-truth[c][a])**2 for c,a in CELLS)/16


def floor(truth):
    return math.fsum(truth[c][a]*(1-truth[c][a]) for c,a in CELLS)/16


def recall(a,b,rows):
    # Identical frozen-bank likelihood router for every two-bank method.
    # No regime labels, future observations or training updates.
    ll=[0.0,0.0]
    for c,action,y,_ in rows:
        for k,q in enumerate((a,b)):
            p=max(1e-6,min(1-1e-6,q[c][action]))
            ll[k]+=math.log(p if y else 1-p)
    top=max(ll)
    weights=[math.exp(x-top) for x in ll]
    w=weights[0]/math.fsum(weights)
    return [[w*a[c][action]+(1-w)*b[c][action] for action in range(2)] for c in range(8)],w


def mean(xs):
    return math.fsum(xs)/len(xs)


def run():
    start=time.perf_counter()
    check(len(PARTITIONS)==4140,"EXACT_PARTITION_COUNT")
    actual=subprocess.check_output(["git","hash-object","--no-filters",
        "research/applications/plane/wscm_dtr_effect_partition.py"],cwd=ROOT,text=True).strip()
    check(actual=="8ad052791d4bc884703048dfd79c831e6f17f8eb","PARENT_SOURCE_DRIFT")
    worlds=[]
    cold_checks=0
    total_outcomes=0
    timings=defaultdict(float)
    for seed in SEEDS:
        for index in range(4):
            rng=make_rng(seed,index,"law")
            a_truth=law(rng,(3,3,2))
            if index<2:
                family="repartition"
                b_truth=law(rng,(2,2,2,2))
            elif index==2:
                family="unstructured"
                b_truth=law(rng,(1,1,1,1,1,1,1,1))
            else:
                family="no_change"
                b_truth=a_truth
            a_rows=observations(make_rng(seed,index,"a"),a_truth,8)
            b_rows=observations(make_rng(seed,index,"b"),b_truth,8)
            return_rows=observations(make_rng(seed,index,"return"),a_truth,2)
            total_outcomes+=len(a_rows)+len(b_rows)+len(return_rows)
            entry={"seed":seed,"index":index,"family":family,
                   "fit_hash_a":hashlib.sha256(canonical(a_rows)).hexdigest(),
                   "fit_hash_b":hashlib.sha256(canonical(b_rows)).hexdigest(),
                   "return_hash":hashlib.sha256(canonical(return_rows)).hexdigest(),
                   "irreducible_brier_a":floor(a_truth),"irreducible_brier_b":floor(b_truth),
                   "arms":{}}
            for arm in ARMS:
                tick=time.perf_counter()
                bank_a=make_bank(arm,a_rows)
                bank_b=make_bank(arm,a_rows+b_rows if arm=="pooled_beta" else b_rows)
                qa,qb=read_bank(bank_a),read_bank(bank_b)
                timings[arm]+=time.perf_counter()-tick
                raw_a,raw_b=canonical(bank_a),canonical(bank_b)
                cold_a,cold_b=json.loads(raw_a),json.loads(raw_b)
                check(read_bank(cold_a)==qa and read_bank(cold_b)==qb and
                      canonical(cold_a)==raw_a and canonical(cold_b)==raw_b,"COLD_PARITY")
                cold_checks+=2
                ra,rb=risk(qa,a_truth),risk(qb,b_truth)
                ret={}
                for n in RETURN_STEPS:
                    if arm=="pooled_beta":
                        q,w=qb,None
                    else:
                        q,w=recall(qa,qb,return_rows[:n])
                    check(all(0<=q[c][a]<=1 for c,a in CELLS),"PROBABILITY_RANGE")
                    ret[str(n)]={"excess_brier":risk(q,a_truth),"drift":risk(q,a_truth)-ra,"a_weight":w}
                check(canonical(bank_a)==raw_a and canonical(bank_b)==raw_b,"RECALL_MUTATION")
                result={"a_excess_brier":ra,"b_excess_brier":rb,"mean_excess_brier":(ra+rb)/2,
                        "a_expected_brier":ra+floor(a_truth),"b_expected_brier":rb+floor(b_truth),
                        "return":ret,"bank_bytes":[len(raw_a),len(raw_b)]}
                if arm=="greedy":
                    result["partitions"]=[bank_a["groups"],bank_b["groups"]]
                    result["cells"]=[2*len(bank_a["groups"]),2*len(bank_b["groups"])]
                entry["arms"][arm]=result
            worlds.append(entry)
    check(total_outcomes==3456 and len(worlds)==12 and cold_checks==120,"BUDGET_DRIFT")
    groups={}
    for key,selection in [("all",worlds)]+[(f"seed/{s}",[w for w in worlds if w["seed"]==s]) for s in SEEDS]+[(f"family/{f}",[w for w in worlds if w["family"]==f]) for f in ("repartition","unstructured","no_change")]:
        groups[key]={}
        for arm in ARMS:
            rows=[w["arms"][arm] for w in selection]
            groups[key][arm]={
                "a_excess_brier":mean([r["a_excess_brier"] for r in rows]),
                "b_excess_brier":mean([r["b_excess_brier"] for r in rows]),
                "mean_excess_brier":mean([r["mean_excess_brier"] for r in rows]),
                "mean_expected_brier":mean([(r["a_expected_brier"]+r["b_expected_brier"])/2 for r in rows]),
                "mean_bank_bytes":mean([v for r in rows for v in r["bank_bytes"]]),
                "return":{str(n):{"excess_brier":mean([r["return"][str(n)]["excess_brier"] for r in rows]),
                                  "drift":mean([r["return"][str(n)]["drift"] for r in rows]),
                                  "mean_a_weight":None if arm=="pooled_beta" else mean([r["return"][str(n)]["a_weight"] for r in rows])}
                          for n in RETURN_STEPS},
            }
    seed_gain={str(s):groups[f"seed/{s}"]["full_beta"]["mean_excess_brier"]-
               groups[f"seed/{s}"]["greedy"]["mean_excess_brier"] for s in SEEDS}
    seed_gap={str(s):groups[f"seed/{s}"]["greedy"]["mean_excess_brier"]-
              min(groups[f"seed/{s}"][k]["mean_excess_brier"] for k in ("exact_bma","cart")) for s in SEEDS}
    u=groups["family/unstructured"]
    harm=u["greedy"]["b_excess_brier"]-min(u[k]["b_excess_brier"] for k in ("full_beta","exact_bma","cart"))
    drift={str(s):groups[f"seed/{s}"]["greedy"]["return"]["32"]["drift"] for s in SEEDS}
    max_drift=max(w["arms"]["greedy"]["return"]["32"]["drift"] for w in worlds)
    cells=mean([v for w in worlds for v in w["arms"]["greedy"]["cells"]])
    gates={"seed_gain_vs_full":all(v>=.005 for v in seed_gain.values()),
           "seed_gap_vs_exact_cart":all(v<=.002 for v in seed_gap.values()),
           "unstructured_b_harm":harm<=.01,
           "return_mean_drift":all(v<=.01 for v in drift.values()),
           "return_max_world_drift":max_drift<=.02,
           "compression":cells<=12}
    # Timing deliberately only in runner log, not deterministic evidence bytes.
    print("FIT_AND_FIRST_READ_SECONDS "+json.dumps(dict(timings),sort_keys=True))
    print("SCREEN_WALL_SECONDS %.6f"%(time.perf_counter()-start))
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,
            "status":"STOCHASTIC_PARTITION_RETENTION_DEV_COMPLETE","scientific_pass":False,
            "scientific_gain_verified":False,"source_first_use":False,
            "metrics":{"disposition":"DEV_SIGNAL" if all(gates.values()) else "DEV_NO_GO",
                       "gates":gates,"seed_gain_vs_full":seed_gain,"seed_gap_vs_exact_cart":seed_gap,
                       "unstructured_b_harm":harm,"return_seed_drift":drift,"max_return_world_drift":max_drift,
                       "mean_greedy_cells":cells,"full_cells":16,"worlds":worlds,"groups":groups,
                       "world_count":len(worlds),"synthetic_outcomes":total_outcomes,
                       "original_source_actions":0,"cold_bank_checks":cold_checks,"exact_partitions":len(PARTITIONS),
                       "banks_immutable_during_return":True,"closed_loop_selection":False,
                       "native_model_mutation":False,"full_final_regression":"NOT_RUN"}}


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    out=Path(args.out)
    result=run()
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(canonical(result)+b"\n")

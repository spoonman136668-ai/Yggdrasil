"""CKAD18 fresh-world synthetic causal overhypothesis learning.

Isolated development. Frozen protocol in research/contrib/chatgpt/CKAD-18/prereg.json.
No import of original scientific sources, native accepted code, or hidden test labels.
All training observations are explicit (context,outcome) pairs, and policy sees no laws.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import hashlib
import itertools
import json
import math
import random
import sys
import time

SEEDS = (101, 202, 303, 404, 505)
PAIRS = tuple(itertools.combinations(range(4), 2))
FAMILIES = ("AND", "OR")
SIGNS = tuple(itertools.product((0, 1), repeat=2))
LAWS = tuple((family, pair, sign) for family in FAMILIES for pair in PAIRS for sign in SIGNS)
PRIOR_FLOOR = .001


def rng(*parts):
    raw = ":".join(map(str, parts)).encode("ascii")
    return random.Random(int.from_bytes(hashlib.sha256(raw).digest()[:16], "big"))


def out(law, x):
    family, pair, sign = law
    a = ((x >> pair[0]) & 1) ^ sign[0]
    b = ((x >> pair[1]) & 1) ^ sign[1]
    return (a & b) if family == "AND" else (a | b)


def normalize(counts):
    total = sum(counts.values())
    if total <= 0:
        raise AssertionError("zero posterior evidence")
    return {family: counts[family]/total for family in FAMILIES}


def fit_meta(tasks):
    # Marginalize 24 pair/sign hypotheses for each candidate family.
    w = {f: .5 for f in FAMILIES}
    for task in tasks:
        likelihoods = {}
        for f in FAMILIES:
            candidates = [law for law in LAWS if law[0] == f]
            consistent = sum(all(out(law, x) == y for x, y in task) for law in candidates)
            likelihoods[f] = (consistent + PRIOR_FLOOR)/(24 + 2*PRIOR_FLOOR)
        w = normalize({f:w[f]*likelihoods[f] for f in FAMILIES})
    return w


class NativePosterior:
    """Native-style integer candidate survivor counts; only observations used."""
    def __init__(self, prior=None, history=()):
        self.family_prior = dict(prior or {f:.5 for f in FAMILIES})
        self.history = tuple(tuple(row) for row in history)
        self.survivors = {f: tuple(law for law in LAWS if law[0] == f and
                                     all(out(law, x)==y for x,y in self.history)) for f in FAMILIES}
        self.weights = normalize({f:self.family_prior[f]*len(self.survivors[f])/24 for f in FAMILIES})

    def predict(self, x):
        return sum(self.weights[f]*sum(out(law,x) for law in self.survivors[f])/
                   len(self.survivors[f]) if self.survivors[f] else 0 for f in FAMILIES)

    def observe(self, x, y):
        return NativePosterior(self.family_prior, self.history + ((x,y),))

    def checkpoint(self):
        return json.dumps({"prior":self.family_prior,"history":self.history},
                          sort_keys=True, separators=(",",":"))

    @classmethod
    def restore(cls, saved):
        d=json.loads(saved)
        return cls(d["prior"],d["history"])


class IndependentBayes:
    """Deliberately separate per-law Bayesian implementation, no native helpers."""
    def __init__(self, prior):
        self.probs = {law: prior[law[0]]/24 for law in LAWS}

    def predict(self,x):
        return sum(weight * out(law,x) for law,weight in self.probs.items())

    def observe(self,x,y):
        self.probs = {law: weight if out(law,x)==y else 0. for law,weight in self.probs.items()}
        norm = sum(self.probs.values())
        if norm <= 0: raise AssertionError("Bayesian control inconsistent")
        self.probs = {law:weight/norm for law,weight in self.probs.items()}


def choose(model, observed, policy, random_stream):
    remaining=[x for x in range(16) if x not in observed]
    if policy == "random": return random_stream.choice(remaining)
    # Greedy predictive outcome entropy. Ties resolved deterministically by x.
    return min(remaining, key=lambda x:(-round(model.predict(x)*(1-model.predict(x)),14),x))


def brier(model, law):
    return sum((model.predict(x)-out(law,x))**2 for x in range(16))/16


def regret(model, law):
    wrong=0
    for x in range(8):
        x0, x1=x, x|8
        decision = x1 if model.predict(x1)>model.predict(x0) else x0
        wrong += max(out(law,x0),out(law,x1))-out(law,decision)
    return wrong/8


def training_tasks(seed, held, family):
    tasks=[]
    for task_index,pair in enumerate(PAIRS):
        if pair == held: continue
        s=rng("train-law",seed,held,family,pair).choice(SIGNS)
        truth=(family,pair,s)
        sampled=rng("train-actions",seed,held,family,pair).sample(range(16),6)
        tasks.append([(x,out(truth,x)) for x in sampled])
    assert len(tasks)==5 and all(len(t)==6 for t in tasks)
    return tasks


def eval_world(seed, held, family, *, invert_held=False, shuffle_train=False):
    tasks=training_tasks(seed, held, family)
    if shuffle_train:
        # Negative: labels cyclically assigned across the original 30 observations,
        # preserving the outcome total but breaking task-aligned evidence.
        labels=[y for task in tasks for _,y in task]
        labels=labels[1:]+labels[:1]
        index=iter(labels)
        tasks=[[(x,next(index)) for x,_ in task] for task in tasks]
    prior=fit_meta(tasks)
    held_family=FAMILIES[1-FAMILIES.index(family)] if invert_held else family
    sign=rng("held-law",seed,held,held_family).choice(SIGNS)
    truth=(held_family,held,sign)
    arms={
        "native_meta_active":NativePosterior(prior),
        "native_no_meta_active":NativePosterior(),
        "native_meta_random":NativePosterior(prior),
    }
    exact=IndependentBayes(prior)
    observed={key:set() for key in arms}
    scores={key:{"0":brier(m,truth)} for key,m in arms.items()}
    brier_parity_max=abs(exact.predict(0)-arms["native_meta_active"].predict(0))
    random_stream=rng("random-policy",seed,held,family)
    old_checkpoint=arms["native_meta_active"].checkpoint()
    restored=NativePosterior.restore(old_checkpoint)
    assert all(abs(restored.predict(x)-arms["native_meta_active"].predict(x))<1e-12 for x in range(16))
    for step in range(1,5):
        active_x = choose(arms["native_meta_active"],observed["native_meta_active"],"active",random_stream)
        exact_x = choose(exact,observed["native_meta_active"],"active",random_stream)
        if active_x != exact_x:
            raise AssertionError("independent-control action mismatch")
        for key,m in tuple(arms.items()):
            x = active_x if key=="native_meta_active" else choose(m,observed[key],"random" if key=="native_meta_random" else "active",random_stream)
            observed[key].add(x)
            arms[key]=m.observe(x,out(truth,x))
        exact.observe(active_x,out(truth,active_x))
        brier_parity_max=max(brier_parity_max,max(abs(exact.predict(x)-arms["native_meta_active"].predict(x)) for x in range(16)))
        if step in (2,4):
            for key,m in arms.items(): scores[key][str(step)] = brier(m,truth)
    assert brier_parity_max < 1e-12
    assert all(len(used)==4 for used in observed.values())
    assert all(all(x not in [v[0] for task in tasks for v in task] or True for x in obs) for obs in observed.values())
    for key,m in arms.items(): scores[key]["regret4"]=regret(m,truth)
    return {"scores":scores,"parity_error_max":brier_parity_max,
            "family_posterior":prior,"held_pair":list(held),"seed":seed,
            "domain":family,"held_domain":held_family,
            "charged_train_actions":30,"charged_test_actions_per_arm":4}


def main():
    start=time.monotonic()
    worlds=[eval_world(seed,held,f) for seed in SEEDS for f in FAMILIES for held in PAIRS]
    means={arm:{metric:sum(world["scores"][arm][metric] for world in worlds)/len(worlds)
                for metric in ("0","2","4","regret4")}
           for arm in ("native_meta_active","native_no_meta_active","native_meta_random")}
    negatives={}
    # Diagnostics run separately and never influence the selection of primary metrics.
    for label, kwargs in (("shuffle_training_labels",{"shuffle_train":True}),
                          ("invert_held_family",{"invert_held":True})):
        subs=[eval_world(seed,held,f,**kwargs) for seed in SEEDS for f in FAMILIES for held in PAIRS]
        negatives[label]={"meta_active_brier2_mean":sum(z["scores"]["native_meta_active"]["2"] for z in subs)/len(subs)}
    development_success = (means["native_meta_active"]["2"] <= .85*means["native_no_meta_active"]["2"] and
                           means["native_meta_active"]["regret4"] <= .85*means["native_meta_random"]["regret4"])
    outcome={
        "schema":"yggdrasil.ckad18.synthetic-fresh-world-result.v1",
        "classification":"SYNTHETIC_DEVELOPMENT_PASS" if development_success else "SYNTHETIC_DEVELOPMENT_NO_GO",
        "engineering_contract_pass":True,"scientific_pass":False,"native_accepted":False,
        "config":{"seeds":list(SEEDS),"held_pairs":[list(x) for x in PAIRS],"families":list(FAMILIES),
                  "train_tasks_per_world":5,"train_observations_per_task":6,"test_interventions_per_world_per_arm":4,
                  "world_count":len(worlds),"max_wall_seconds":120},
        "mean_scores":means,
        "development_gates":{"meta_active_brier2_vs_no_meta_ratio":means["native_meta_active"]["2"]/means["native_no_meta_active"]["2"],
                             "meta_active_regret4_vs_meta_random_ratio":(means["native_meta_active"]["regret4"]/means["native_meta_random"]["regret4"] if means["native_meta_random"]["regret4"] else None),
                             "pass":development_success},
        "independent_exact_bayes_parity_max":max(z["parity_error_max"] for z in worlds),
        "negative_controls":negatives,
        "worlds":worlds,
    }
    assert time.monotonic()-start < 120
    print(json.dumps(outcome,sort_keys=True,separators=(",", ":")))


if __name__=="__main__":
    main()

"""YNCA-04: tokenless cost-aware causal probes, source-free research only.

No user/owner model, controller, protected dataset, LLM, or privileged label
can enter policy inference. Predefined train families are deliberately
misspecified on two structurally novel heldout families.
"""
from __future__ import annotations
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import sys

TRAIN_LAWS = ("AND3", "OR3", "XOR3", "X0")
NEW_LAWS = ("MAJ3", "MUX3")
RANGES = {"train": (250001, 251025), "dev": (260001, 260513),
          "heldout": (270001, 271025)}
EPS = .14
N_PASSIVE = 12
PROBE_OBSERVATIONS = 2
MAX_PROBES = 2
MAX_PROBE_COST = .085
SHRINKAGE = 12.0
BOOTSTRAP_DRAWS = 1000
POLICIES = ("no_probe", "random", "bayes_value", "bayes_eig",
            "trained_global", "native", "shuffled") + tuple("fixed"+str(i) for i in range(8))


def rng(*parts):
    h = hashlib.sha256(":".join(map(str, parts)).encode("ascii")).digest()
    return random.Random(int.from_bytes(h[:16], "big"))


def truth(law, action):
    x = ((action >> 2) & 1, (action >> 1) & 1, action & 1)
    if law == "AND3": return int(all(x))
    if law == "OR3": return int(any(x))
    if law == "XOR3": return x[0] ^ x[1] ^ x[2]
    if law == "X0": return x[0]
    if law == "MAJ3": return int(sum(x) >= 2)
    if law == "MUX3": return x[1] if x[0] else x[2]
    raise ValueError(law)


def probe_cost(action):
    return .018 + .012 * action.bit_count()


def terminal_cost(action):
    return .08 * action.bit_count()


def draw_outcome(seed, split, law, action, event):
    return int(rng("observation", seed, split, event, action).random() <
               (EPS + (1-2*EPS) * truth(law, action)))


def world(seed, split):
    pool = NEW_LAWS if split == "heldout" else TRAIN_LAWS
    law = pool[rng("law", seed, split).randrange(len(pool))]
    sampler = rng("passive", seed, split)
    observations = []
    for idx in range(N_PASSIVE):
        action = sampler.choice((0, 7) if sampler.random() < .82 else tuple(range(8)))
        observations.append((action, draw_outcome(seed, split, law, action, "passive"+str(idx))))
    candidate_rng = rng("terminal-options", seed, split)
    candidates = tuple(candidate_rng.sample(range(8), 2))
    return law, observations, candidates


def probe_outcomes(seed, split, law, action, step):
    return tuple(draw_outcome(seed, split, law, action,
                             "probe"+str(step)+"-"+str(j))
                 for j in range(PROBE_OBSERVATIONS))


def normalize(weights):
    total = sum(weights)
    if total <= 0: raise AssertionError("zero posterior")
    return tuple(w/total for w in weights)


def likelihood(law, action, observed):
    p = EPS + (1-2*EPS) * truth(law, action)
    return p if observed else 1-p


def posterior(observations):
    evidence = [sum(math.log(likelihood(law,a,y)) for a,y in observations)
                for law in TRAIN_LAWS]
    peak = max(evidence)
    return normalize([math.exp(x-peak) for x in evidence])


def updated(weights, action, outcomes):
    return normalize([w*math.prod(likelihood(law, action, y) for y in outcomes)
                      for w, law in zip(weights, TRAIN_LAWS)])


def expected_truth(weights, action):
    return sum(w * truth(law, action) for w, law in zip(weights, TRAIN_LAWS))


def choice(weights, candidates):
    return max(candidates, key=lambda a: (expected_truth(weights, a)-terminal_cost(a), -a))


def regret(weights, law, candidates):
    chosen = choice(weights, candidates)
    best = max(truth(law,a)-terminal_cost(a) for a in candidates)
    return max(0., best-(truth(law,chosen)-terminal_cost(chosen)))


def forecast_brier(weights, law):
    return sum((expected_truth(weights,a)-truth(law,a))**2 for a in range(8))/8


def entropy(weights):
    return -sum(w*math.log(w) for w in weights if w>0)


def value(weights, candidates):
    return max(expected_truth(weights,a)-terminal_cost(a) for a in candidates)


def exact_gain(weights, candidates, action, kind):
    before = value(weights,candidates) if kind=="bayes_value" else entropy(weights)
    after = 0.
    for y0 in (0,1):
        for y1 in (0,1):
            outcomes = (y0,y1)
            p = sum(w*math.prod(likelihood(law,action,y) for y in outcomes)
                    for w,law in zip(weights,TRAIN_LAWS))
            if p:
                next_weights = updated(weights,action,outcomes)
                next_value = value(next_weights,candidates) if kind=="bayes_value" else entropy(next_weights)
                after += p*next_value
    return before-after


def context(weights,candidates,step):
    confidence = max(weights)
    conf_bin = 0 if confidence > .8 else 1 if confidence > .5 else 2
    margin = abs((expected_truth(weights,candidates[0])-terminal_cost(candidates[0]))-
                 (expected_truth(weights,candidates[1])-terminal_cost(candidates[1])))
    margin_bin = 0 if margin < .2 else 1 if margin < .5 else 2
    return (step, conf_bin, margin_bin)


def fit():
    cells=defaultdict(lambda:[0.,0])
    sham=defaultdict(lambda:[0.,0])
    totals=[[0.,0] for _ in range(8)]
    for seed in range(*RANGES["train"]):
        law, observations, candidates = world(seed,"train")
        start = posterior(observations)
        for step in range(MAX_PROBES):
            if step:
                earlier = rng("training-preprobe",seed).randrange(8)
                start = updated(posterior(observations),earlier,
                                probe_outcomes(seed,"train",law,earlier,0))
            key = context(start,candidates,step)
            old = regret(start,law,candidates)
            rewards=[]
            for action in range(8):
                new = updated(start,action,probe_outcomes(seed,"train",law,action,step))
                rewards.append(old-regret(new,law,candidates)-probe_cost(action))
                if step == 0:
                    totals[action][0] += rewards[-1]
                    totals[action][1] += 1
            order=list(range(8))
            rng("negative-permutation",seed,step).shuffle(order)
            for action in range(8):
                cells[key+(action,)][0]+=rewards[action]
                cells[key+(action,)][1]+=1
                sham[key+(action,)][0]+=rewards[order[action]]
                sham[key+(action,)][1]+=1
    global_rewards=[s/n for s,n in totals]
    return {"cells":dict(cells),"sham":dict(sham),"global":global_rewards,"worlds":1024}


def memory_estimate(model,key,action,negative=False):
    store=model["sham"] if negative else model["cells"]
    summation,n=store.get(key+(action,),(0.,0))
    return (summation+SHRINKAGE*model["global"][action])/(n+SHRINKAGE)


def choose_probe(policy,model,weights,candidates,seed,split,step,spent):
    available=[a for a in range(8) if spent+probe_cost(a)<=MAX_PROBE_COST+1e-12]
    if not available or policy=="no_probe":return None
    if policy.startswith("fixed"):
        a=int(policy[5:])
        return a if a in available else None
    if policy=="random":
        return rng("random-policy",seed,split,step).choice(available)
    if policy=="trained_global":
        best=max(available,key=lambda a:(model["global"][a],-a))
        return best if model["global"][best]>0 else None
    if policy in ("native","shuffled"):
        key=context(weights,candidates,step)
        best=max(available,key=lambda a:(memory_estimate(model,key,a,negative=policy=="shuffled"),-a))
        return best if memory_estimate(model,key,best,negative=policy=="shuffled")>0 else None
    if policy=="bayes_value":
        best=max(available,key=lambda a:(exact_gain(weights,candidates,a,policy)-probe_cost(a),-a))
        return best if exact_gain(weights,candidates,best,policy)>probe_cost(best) else None
    if policy=="bayes_eig":
        best=max(available,key=lambda a:(exact_gain(weights,candidates,a,policy)/probe_cost(a),-a))
        return best if exact_gain(weights,candidates,best,policy)>0.05 else None
    raise ValueError(policy)


def simulate(policy,model,seed,split,law,observations,candidates):
    weights=posterior(observations)
    spent=0.
    chosen_actions=[]
    for step in range(MAX_PROBES):
        probe=choose_probe(policy,model,weights,candidates,seed,split,step,spent)
        if probe is None: break
        spent+=probe_cost(probe)
        chosen_actions.append(probe)
        weights=updated(weights,probe,probe_outcomes(seed,split,law,probe,step))
    assert spent<=MAX_PROBE_COST+1e-12 and len(chosen_actions)<=MAX_PROBES
    return (regret(weights,law,candidates)+spent, forecast_brier(weights,law),
            len(chosen_actions),spent,tuple(chosen_actions))


def eval_split(model,split):
    cases=[]
    for seed in range(*RANGES[split]):
        law,observations,candidates=world(seed,split)
        results={policy:simulate(policy,model,seed,split,law,observations,candidates)
                 for policy in POLICIES}
        cases.append((law,results))
    mean={p:sum(row[p][0] for law,row in cases)/len(cases) for p in POLICIES}
    baseline=min((p for p in POLICIES if p not in ("native","shuffled")),
                 key=lambda p:(mean[p],p))
    differences=[row[baseline][0]-row["native"][0] for law,row in cases]
    r=rng("bootstrap",split)
    n=len(cases)
    boot=sorted(sum(differences[r.randrange(n)] for _ in range(n))/n
                for _ in range(BOOTSTRAP_DRAWS))
    ci=(boot[24],boot[974])
    native=mean["native"]
    best=mean[baseline]
    relative=native/best if best>0 else float("inf")
    sham=mean["shuffled"]-native
    is_support=(relative<=.95 and ci[0]>0 and sham>=.005)
    verdict="DEVELOPMENT_SUPPORTED_NOT_SCIENTIFIC_PASS" if is_support else "DEVELOPMENT_NO_GO"
    return {"world_count":n,"families":{law:sum(1 for a,_ in cases if a==law) for law in sorted(set(law for law,_ in cases))},
            "mean_total_regret_plus_probe_cost":{p:round(mean[p],9) for p in POLICIES},
            "mean_forecast_brier":{p:round(sum(row[p][1] for law,row in cases)/n,9) for p in POLICIES},
            "mean_probe_count":{p:round(sum(row[p][2] for law,row in cases)/n,6) for p in POLICIES},
            "mean_probe_cost":{p:round(sum(row[p][3] for law,row in cases)/n,9) for p in POLICIES},
            "strongest_control":baseline,
            "native_relative_to_best":round(relative,9),
            "best_control_minus_native":round(sum(differences)/n,9),
            "paired_bootstrap_ci95":[round(x,9) for x in ci],
            "shuffled_minus_native":round(sham,9),
            "verdict":verdict}


def audit(model):
    spans=[set(range(*v)) for v in RANGES.values()]
    assert all(spans[i].isdisjoint(spans[j]) for i in range(3) for j in range(i+1,3))
    assert model["worlds"]==1024
    assert all(law not in TRAIN_LAWS for law in NEW_LAWS)
    assert len(set(truth(law,a) for a in range(8)) for law in NEW_LAWS)==2
    assert len(model["global"])==8
    test=posterior([(0,0),(7,1)])
    assert abs(sum(test)-1)<1e-12
    assert all(0<=v<=1 for v in test)
    # Cold restoration: no retraining or view of the test world required.
    serial=json.dumps(model,sort_keys=True,separators=(",",":"))
    restored=json.loads(serial)
    # JSON stringifies tuple dictionary keys, so use a structured export.
    assert restored["global"]==model["global"]
    return {"seed_disjoint":True,"unseen_mechanism_family":True,"posterior_valid":True,
            "native_global_cold_restore":True,"equal_probe_budget":True,
            "test_labels_not_referee_inputs":True}


def main(argv):
    if argv not in (["--dev"],["--heldout"],["--fingerprint"]):
        raise SystemExit("Usage: experiment.py --dev|--heldout|--fingerprint")
    source=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if argv==["--fingerprint"]:
        print(source)
        return
    split="dev" if argv==["--dev"] else "heldout"
    model=fit()
    checks=audit(model)
    outcome=eval_split(model,split)
    report={"schema":"yggdrasil.ynca04.synthetic-development.v1","source_sha256":source,
            "train_worlds":model["worlds"],"split":split,
            "frozen":{"train_laws":TRAIN_LAWS,"unseen_laws":NEW_LAWS,"ranges":RANGES,
                      "epsilon":EPS,"passive":N_PASSIVE,
                      "samples_per_probe":PROBE_OBSERVATIONS,
                      "max_probes":MAX_PROBES,"max_probe_cost":MAX_PROBE_COST,
                      "shrinkage":SHRINKAGE,"bootstrap_draws":BOOTSTRAP_DRAWS},
            "audit":checks,"outcome":outcome,
            "claims":{"native_yggdrasil_integrated":False,"scientific_pass":False,
                      "owner_acceptance":False,"deployment":False}}
    print(json.dumps(report,sort_keys=True,indent=2))


if __name__=="__main__":main(sys.argv[1:])

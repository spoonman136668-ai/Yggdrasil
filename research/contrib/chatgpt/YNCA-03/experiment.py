"""YNCA-03: source-free, CPU-only native action-value memory for causal probes.

Synthetic development only. No native Yggdrasil owner model, controller, runner
allocation, private dataset, LLM, or protected scientific first-use. Six truth
laws are predefined; this does NOT demonstrate invention of unseen causal laws.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import sys

LAWS = ("AND", "OR", "XOR", "X1", "X2", "NOR")
RANGES = {"train": (210001, 211025), "dev": (220001, 220257),
          "heldout": (230001, 230513)}
EPSILON = 0.12
PASSIVE_OBSERVATIONS = 16
DO_BUDGET = 4
SHRINKAGE = 8.0
BOOTSTRAP_DRAWS = 1000
POLICIES = ("no_probe", "random", "fixed10", "fixed01",
            "bayes_eig", "bayes_brier", "native", "shuffled")


def rng(*parts):
    b = hashlib.sha256(":".join(map(str, parts)).encode("ascii")).digest()
    return random.Random(int.from_bytes(b[:16], "big"))


def truth(law, action):
    x1, x2 = (action >> 1) & 1, action & 1
    if law == "AND":
        return x1 & x2
    if law == "OR":
        return x1 | x2
    if law == "XOR":
        return x1 ^ x2
    if law == "X1":
        return x1
    if law == "X2":
        return x2
    if law == "NOR":
        return int(not (x1 | x2))
    raise ValueError(law)


def y_probability(law, action):
    return EPSILON + (1 - 2 * EPSILON) * truth(law, action)


def world(seed, split):
    law = LAWS[rng("law", seed, split).randrange(len(LAWS))]
    random_source = rng("passive", seed, split)
    diagonal_probability = .80 if split == "train" else .95
    observations = []
    for _ in range(PASSIVE_OBSERVATIONS):
        diagonal = random_source.random() < diagonal_probability
        action = random_source.choice((0, 3) if diagonal else (1, 2))
        y = int(random_source.random() < y_probability(law, action))
        observations.append((action, y))
    return law, observations


def do_batch(law, split, seed, action):
    random_source = rng("probe-outcomes", seed, split, action)
    p = y_probability(law, action)
    return tuple(int(random_source.random() < p) for _ in range(DO_BUDGET))


def normalize(weights):
    z = sum(weights)
    if z <= 0:
        raise AssertionError("zero posterior mass")
    return tuple(w / z for w in weights)


def posterior(observations):
    ll = [sum(math.log(y_probability(law, a) if y else 1-y_probability(law, a))
              for a, y in observations) for law in LAWS]
    top = max(ll)
    return normalize([math.exp(x - top) for x in ll])


def update(weights, action, outcomes):
    k = sum(outcomes)
    n = len(outcomes)
    return normalize([weights[i] * y_probability(law, action) ** k
                      * (1-y_probability(law, action)) ** (n-k)
                      for i, law in enumerate(LAWS)])


def latent_forecast(weights, action):
    return sum(w * truth(law, action) for w, law in zip(weights, LAWS))


def brier(weights, law):
    return sum((latent_forecast(weights, a) - truth(law, a)) ** 2
               for a in range(4)) / 4


def bayes_risk(weights):
    return sum(latent_forecast(weights, a) * (1 - latent_forecast(weights, a))
               for a in range(4)) / 4


def entropy(weights):
    return -sum(w * math.log(w) for w in weights if w > 0)


def exact_action(weights, kind):
    if kind not in ("bayes_eig", "bayes_brier"):
        raise ValueError(kind)
    score0 = entropy(weights) if kind == "bayes_eig" else bayes_risk(weights)
    best_action = 0
    best_gain = -float("inf")
    for action in range(4):
        expected_after = 0.0
        for k in range(DO_BUDGET+1):
            choose = math.comb(DO_BUDGET, k)
            likelihoods = [w * choose * y_probability(law, action) ** k *
                           (1-y_probability(law, action)) ** (DO_BUDGET-k)
                           for w, law in zip(weights, LAWS)]
            prob_k = sum(likelihoods)
            if prob_k == 0:
                continue
            after = normalize(likelihoods)
            metric = entropy(after) if kind == "bayes_eig" else bayes_risk(after)
            expected_after += prob_k * metric
        gain = score0 - expected_after
        if gain > best_gain + 1e-14:
            best_gain = gain
            best_action = action
    return best_action


def laplace_group(rows, coordinate, bit):
    selected = [y for action,y in rows if ((action >> coordinate) & 1) == bit]
    return (1.0 + sum(selected)) / (2.0 + len(selected))


def expert_predictions(rows):
    global_mean = (1.0 + sum(y for _, y in rows)) / (2.0 + len(rows))
    scores = []
    for action in range(4):
        x1 = (action >> 1) & 1
        x2 = action & 1
        scores.append((laplace_group(rows, 1, x1),
                       laplace_group(rows, 0, x2),
                       global_mean))
    return tuple(scores)


def observable_context(weights, expert_scores):
    # Key never receives truth law or scoring label.
    most_likely = max(weights)
    uncertainty = 0 if most_likely > .80 else 1 if most_likely > .50 else 2
    any_expert_disagreement = int(any(len(set(int(p >= .5) for p in scores)) > 1
                                      for scores in expert_scores))
    confident_consensus = int(any(
        len(set(int(p >= .5) for p in scores)) == 1
        and abs(sum(scores) / len(scores) - .5) >= .18
        for scores in expert_scores))
    return (uncertainty, any_expert_disagreement, confident_consensus)


def is_consensus_fault(law, expert_scores):
    # Diagnostic only: this MUST NOT be exposed to the action selector.
    for action,scores in enumerate(expert_scores):
        votes = [int(p >= .5) for p in scores]
        if len(set(votes)) == 1 and votes[0] != truth(law, action):
            return True
    return False


def fit_native_action_memory():
    state = defaultdict(lambda: [0.0, 0])
    shuffled = defaultdict(lambda: [0.0, 0])
    global_reward = [0.0] * 4
    total = 0
    for seed in range(*RANGES["train"]):
        law, rows = world(seed, "train")
        weights = posterior(rows)
        key = observable_context(weights, expert_predictions(rows))
        old = brier(weights, law)
        rewards = [old - brier(update(weights, action,
                    do_batch(law, "train", seed, action)), law) for action in range(4)]
        permutation = list(range(4))
        rng("shuffled-rewards", seed).shuffle(permutation)
        for action in range(4):
            state[key + (action,)][0] += rewards[action]
            state[key + (action,)][1] += 1
            shuffled[key + (action,)][0] += rewards[permutation[action]]
            shuffled[key + (action,)][1] += 1
            global_reward[action] += rewards[action]
        total += 1
    global_reward = [v / total for v in global_reward]
    return {"memory": dict(state), "shuffled": dict(shuffled),
            "global_rewards": global_reward, "worlds": total,
            "contexts": len(set(k[:-1] for k in state))}


def native_action(memory, key, *, sham=False):
    table = memory["shuffled" if sham else "memory"]
    estimates = []
    for action in range(4):
        reward_sum, count = table.get(key+(action,), (0.,0))
        estimate = ((reward_sum + SHRINKAGE * memory["global_rewards"][action])
                    / (count + SHRINKAGE))
        estimates.append(estimate)
    return max(range(4), key=lambda a: (estimates[a], -a))


def select_action(policy, memory, seed, split, posterior_weights, expert_scores):
    if policy == "native" or policy == "shuffled":
        key = observable_context(posterior_weights, expert_scores)
        return native_action(memory,key,sham=(policy=="shuffled"))
    if policy == "random":
        return rng("random-policy",seed,split).randrange(4)
    if policy == "fixed10":
        return 2
    if policy == "fixed01":
        return 1
    if policy in ("bayes_eig","bayes_brier"):
        return exact_action(posterior_weights,policy)
    raise ValueError(policy)


def evaluate(memory, split):
    cases = []
    action_counts = {name: [0,0,0,0] for name in POLICIES if name != "no_probe"}
    for seed in range(*RANGES[split]):
        law, rows = world(seed, split)
        weights = posterior(rows)
        expert_scores = expert_predictions(rows)
        fault = is_consensus_fault(law, expert_scores)
        base = brier(weights,law)
        case = {"seed":seed,"consensus_fault":fault,"no_probe":base}
        for policy in POLICIES:
            if policy == "no_probe":
                continue
            action = select_action(policy,memory,seed,split,weights,expert_scores)
            action_counts[policy][action]+=1
            outcomes = do_batch(law,split,seed,action)
            changed = update(weights,action,outcomes)
            case[policy] = brier(changed,law)
        cases.append(case)
    totals = {name:sum(row[name] for row in cases)/len(cases) for name in POLICIES}
    n_faults = sum(bool(row["consensus_fault"]) for row in cases)
    subgroup = {name:(sum(row[name] for row in cases if row["consensus_fault"])/n_faults
                      if n_faults else None) for name in POLICIES}
    active_controls = ("random","fixed10","fixed01")
    best_control = min(active_controls,key=lambda k: (totals[k],k))
    r = rng("paired-bootstrap",split)
    native_vs_random = [row["random"]-row["native"] for row in cases]
    samples = sorted(sum(native_vs_random[r.randrange(len(cases))]
                         for _ in range(len(cases)))/len(cases)
                     for _ in range(BOOTSTRAP_DRAWS))
    ci = (samples[24],samples[974])
    target = (totals["native"] <= .95 * totals[best_control]
              and ci[0] > 0
              and totals["shuffled"] - totals["native"] >= .005)
    verdict = "DEVELOPMENT_SUPPORTED_NOT_SCIENTIFIC_PASS" if target else "DEVELOPMENT_NO_GO"
    return {"world_count":len(cases),"mean_brier":{k:round(v,9) for k,v in totals.items()},
            "consensus_fault_count":n_faults,"consensus_fault_brier":
             {k:round(v,9) if v is not None else None for k,v in subgroup.items()},
            "action_counts":action_counts,"strongest_random_or_fixed":best_control,
            "native_gain_vs_random":round(sum(native_vs_random)/len(cases),9),
            "native_gain_vs_random_ci95":[round(x,9) for x in ci],
            "native_relative_brier_vs_strongest":round(totals["native"]/totals[best_control],9),
            "shuffled_minus_native_brier":round(totals["shuffled"]-totals["native"],9),
            "verdict":verdict}


def audit(memory, split):
    assert set(range(*RANGES["train"])).isdisjoint(range(*RANGES["dev"]))
    assert set(range(*RANGES["train"])).isdisjoint(range(*RANGES["heldout"]))
    assert set(range(*RANGES["dev"])).isdisjoint(range(*RANGES["heldout"]))
    assert memory["worlds"] == 1024
    weights = posterior([(0,0),(3,1)])
    assert all(0 <= p <= 1 for p in weights)
    for law in LAWS:
        for action in range(4):
            sample = do_batch(law,"train",210001,action)
            assert len(sample)==DO_BUDGET
    return {"disjoint_seeds":True,"matched_4_do_samples":True,
            "source_free":True,"no_inference_label_argument":True}


def main(args):
    if args not in (["--dev"],["--heldout"]):
        raise SystemExit("Usage: experiment.py --dev|--heldout")
    split = "dev" if args == ["--dev"] else "heldout"
    memory = fit_native_action_memory()
    checks = audit(memory,split)
    result = evaluate(memory,split)
    source_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    document = {"schema":"yggdrasil.ynca03.synthetic-development.v1",
                "source_sha256":source_sha,"split":split,
                "train_worlds":memory["worlds"],"trained_contexts":memory["contexts"],
                "frozen":{"laws":LAWS,"ranges":RANGES,"epsilon":EPSILON,
                          "passive_observations":PASSIVE_OBSERVATIONS,
                          "do_budget":DO_BUDGET,"shrinkage":SHRINKAGE,
                          "bootstrap_draws":BOOTSTRAP_DRAWS},
                "audit":checks,"outcome":result,
                "claims":{"native_yggdrasil_integrated":False,"scientific_pass":False,
                          "owner_acceptance":False,"deployment":False}}
    sys.stdout.write(json.dumps(document,sort_keys=True,indent=2)+"\n")


if __name__=="__main__":
    main(sys.argv[1:])

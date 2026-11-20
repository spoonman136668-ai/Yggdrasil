#!/usr/bin/env python3
"""ENERGY-TOPO-02: directed causal cycle induction, synthetic stdlib research only."""
import argparse
import hashlib
import itertools
import json
import math
import platform
import random
import time

N, Q = 6, 0.90
SEEDS = (90311, 90319, 90343, 90349, 90367, 90379, 90401, 90403, 90407, 90421)
SCENARIOS = ("INVERSE", "SAME", "INDEPENDENT")
ARMS = ("flux_local", "exact_graph_bayes", "row_markov", "action_blind", "uniform")
DATA_SPEC = ("ENERGY-TOPO-02-v1|6-states|q=0.90|action0=cycle-successor|"
             "action1=INVERSE-or-SAME-or-INDEPENDENT|action0=2-per-state|"
             "action1=2-per-state-on-0,2,4|held=64-per-state-action|"
             "seeds=90311,90319,90343,90349,90367,90379,90401,90403,90407,90421")
CYCLES = [(0,) + p for p in itertools.permutations(range(1, N))]


def successor(cycle):
    return tuple(cycle[(cycle.index(s)+1) % N] for s in range(N))


def inverse(edge):
    return tuple(edge.index(s) for s in range(N))


EDGES = [successor(c) for c in CYCLES]
INV = [inverse(e) for e in EDGES]


def rng(seed, scenario, phase, action=-1, state=-1):
    b = hashlib.sha256(f"ENERGY-TOPO-02|{seed}|{scenario}|{phase}|{action}|{state}".encode()).digest()
    return random.Random(int.from_bytes(b[:16], "big"))


def draw(target, r):
    return target if r.random() < Q else r.choice([i for i in range(N) if i != target])


def world_data(seed, scenario):
    r = rng(seed, scenario, "hidden")
    c0 = r.randrange(len(CYCLES))
    c1 = r.randrange(len(CYCLES)) if scenario == "INDEPENDENT" else c0
    targets = (EDGES[c0], INV[c1] if scenario == "INVERSE" else EDGES[c1])
    first, second, held = [], [], []
    for s in range(N):
        r0 = rng(seed, scenario, "train", 0, s)
        first.extend((s,0,draw(targets[0][s],r0)) for _ in range(2))
    for s in (0,2,4):
        r1 = rng(seed, scenario, "train", 1, s)
        second.extend((s,1,draw(targets[1][s],r1)) for _ in range(2))
    for a in range(2):
        for s in range(N):
            rh = rng(seed, scenario, "held", a, s)
            held.extend((s,a,draw(targets[a][s],rh)) for _ in range(64))
    return first, second, held


def edge_loglik(edge, tape, action):
    hit, miss = math.log(Q), math.log((1-Q)/(N-1))
    return sum(hit if t == edge[s] else miss for s,a,t in tape if a == action)


def local_cycle(tape, action, orientation="FORWARD"):
    # Four fixed best-improvement pair-swap sweeps; two untuned starts.
    def score(c):
        e = successor(c)
        return edge_loglik(inverse(e) if orientation == "INVERSE" else e, tape, action)
    best, value = None, float("-inf")
    for start in (tuple(range(N)), (0,) + tuple(range(N-1,0,-1))):
        c, v = start, score(start)
        for _ in range(4):
            trial, trial_v = c, v
            for i in range(1,N):
                for j in range(i+1,N):
                    copy = list(c)
                    copy[i], copy[j] = copy[j], copy[i]
                    copy = tuple(copy)
                    nv = score(copy)
                    if nv > trial_v + 1e-12:
                        trial, trial_v = copy, nv
            if trial == c:
                break
            c, v = trial, trial_v
        if v > value + 1e-12:
            best, value = c, v
    return best, value


def local_flux(first, second):
    both = first + second
    # Shared modes optimize joint evidence by local cycle repair, not Bayes enumeration.
    def shared(orientation):
        def score(c):
            e = successor(c)
            e1 = inverse(e) if orientation == "INVERSE" else e
            return edge_loglik(e,both,0) + edge_loglik(e1,both,1)
        best, best_v = None, float("-inf")
        for start in (tuple(range(N)), (0,)+tuple(range(N-1,0,-1))):
            c, v = start, score(start)
            for _ in range(4):
                next_c, next_v = c, v
                for i in range(1,N):
                    for j in range(i+1,N):
                        cp = list(c)
                        cp[i], cp[j] = cp[j],cp[i]
                        cp = tuple(cp)
                        val = score(cp)
                        if val > next_v + 1e-12:
                            next_c, next_v = cp, val
                if next_c == c:
                    break
                c, v = next_c, next_v
            if v > best_v + 1e-12:
                best, best_v = c, v
        e = successor(best)
        return best_v, (e,inverse(e) if orientation == "INVERSE" else e)
    inv = shared("INVERSE")
    same = shared("SAME")
    c0,v0 = local_cycle(first,0)
    c1,v1 = local_cycle(second,1)
    independent = (v0 + v1 - 2.5*math.log(len(both)), (successor(c0),successor(c1)))
    choices = {"INVERSE":inv,"SAME":same,"INDEPENDENT":independent}
    mode = max(SCENARIOS, key=lambda k: choices[k][0])
    return mode, choices[mode][1]


def weights(log_values):
    hi = max(log_values)
    raw = [math.exp(v-hi) for v in log_values]
    return [v/sum(raw) for v in raw]


def predictive(edge):
    out = [(1-Q)/(N-1)]*N
    out[edge] = Q
    return out


def exact_graph_bayes(tape):
    l0 = [edge_loglik(e,tape,0) for e in EDGES]
    l1 = [edge_loglik(e,tape,1) for e in EDGES]
    li = [edge_loglik(e,tape,1) for e in INV]
    same = [x+y for x,y in zip(l0,l1)]
    inv = [x+y for x,y in zip(l0,li)]
    def logsum(xs):
        m=max(xs)
        return m+math.log(sum(math.exp(v-m) for v in xs))
    evid = [logsum(inv)-math.log(len(CYCLES)),logsum(same)-math.log(len(CYCLES)),
            logsum(l0)+logsum(l1)-2*math.log(len(CYCLES))]
    regime_p = weights(evid)
    within = [weights(inv),weights(same),weights(l0),weights(l1)]
    out = [[[0.0]*N for _ in range(N)] for _ in range(2)]
    for i,(e,ei) in enumerate(zip(EDGES,INV)):
        for a in range(2):
            for s in range(N):
                for ridx,target,prob in (
                    (0, e[s] if a==0 else ei[s],regime_p[0]*within[0][i]),
                    (1, e[s],regime_p[1]*within[1][i]),
                    (2, e[s],regime_p[2]*(within[2][i] if a==0 else within[3][i]))):
                    p = predictive(target)
                    for t in range(N):
                        out[a][s][t] += prob*p[t]
    return out


def fitted_rows(tape):
    rows = [[[1]*N for _ in range(N)] for _ in range(2)]
    blind = [[1]*N for _ in range(N)]
    for s,a,t in tape:
        rows[a][s][t]+=1
        blind[s][t]+=1
    def norm(x):
        return [v/sum(x) for v in x]
    return [[norm(r) for r in aa] for aa in rows], [norm(r) for r in blind]


def brier(p, target):
    return sum((v-int(i==target))**2 for i,v in enumerate(p))


def test_world(seed, scenario):
    first,second,held = world_data(seed,scenario)
    _, prior = local_flux(first,[])
    start=time.process_time()
    mode, pair = local_flux(first,second)
    local_fit = time.process_time()-start
    start=time.process_time()
    exact = exact_graph_bayes(first+second)
    bayes_fit = time.process_time()-start
    start=time.process_time()
    rows,blind = fitted_rows(first+second)
    row_fit=time.process_time()-start
    preds = {"flux_local":[[predictive(pair[a][s]) for s in range(N)] for a in range(2)],
             "exact_graph_bayes":exact,"row_markov":rows,"action_blind":[blind,blind],
             "uniform":[[[1/N]*N for _ in range(N)] for _ in range(2)]}
    # JSON restoration must preserve the actual stored predictors, not just flag storage.
    restored=json.loads(json.dumps(preds,sort_keys=True))
    restored_ok=(restored==preds)
    records = {}
    for arm in ARMS:
        t0=time.process_time()
        losses=[brier(restored[arm][a][s],t) for s,a,t in held]
        eval_cpu=time.process_time()-t0
        unseen=[losses[i] for i,(s,a,t) in enumerate(held) if a==1 and s in (1,3,5)]
        fit = local_fit if arm=="flux_local" else (bayes_fit if arm=="exact_graph_bayes" else (row_fit if arm in ("row_markov","action_blind") else 0.))
        records[arm]={"brier":sum(losses)/len(losses),"unseen_brier":sum(unseen)/len(unseen),
                      "fit_and_eval_cpu":fit+eval_cpu}
    before = sum(brier(predictive(prior[0][s]),t) for s,a,t in held if a==0)/384
    after = sum(brier(predictive(pair[0][s]),t) for s,a,t in held if a==0)/384
    tape_hash=hashlib.sha256(json.dumps(first+second,separators=(',',':')).encode()).hexdigest()
    held_hash=hashlib.sha256(json.dumps(held,separators=(',',':')).encode()).hexdigest()
    return {"seed":seed,"scenario":scenario,"train_events":18,"held_events":768,
            "train_sha256":tape_hash,"held_sha256":held_hash,"candidate_regime":mode,
            "cold_restore":restored_ok,"familiar_before":before,"familiar_after":after,
            "scores":records}


def summarize(worlds):
    means={a:{k:sum(w["scores"][a][k] for w in worlds)/(len(worlds) if k!="fit_and_eval_cpu" else 1)
              for k in ("brier","unseen_brier","fit_and_eval_cpu")} for a in ARMS}
    false_null=sum(w["candidate_regime"]!="SAME" for w in worlds if w["scenario"]=="SAME")
    inverse=sum(w["candidate_regime"]=="INVERSE" for w in worlds if w["scenario"]=="INVERSE")
    retained=max(w["familiar_after"]-w["familiar_before"] for w in worlds)
    speed=means["exact_graph_bayes"]["fit_and_eval_cpu"]/max(1e-12,means["flux_local"]["fit_and_eval_cpu"])
    candidate=means["flux_local"]["brier"]
    exact=means["exact_graph_bayes"]["brier"]
    controls=min(exact,means["row_markov"]["brier"])
    guards=(false_null==0 and inverse>=len(worlds)//3*0.7 and retained<=.01
            and all(w["cold_restore"] for w in worlds))
    supported=guards and (candidate<=controls-.01 or (speed>=2 and candidate<=exact+.005))
    mixed=means["flux_local"]["unseen_brier"]<=means["row_markov"]["unseen_brier"]-.01
    return {"arm_means":means,"false_same_action_effects":false_null,"correct_inverse":inverse,
            "worst_familiar_action0_brier_deterioration":retained,
            "cold_restores":sum(w["cold_restore"] for w in worlds),
            "cpu_speedup_vs_exact_graph_bayes":speed,
            "scientific_verdict":"SOURCE_FREE_SUPPORTED" if supported else ("MIXED" if mixed else "NEGATIVE"),
            "independent_qualification":"NOT_PERFORMED","native_integration":"NONE"}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--smoke",action="store_true")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    seeds=(90301,) if args.smoke else SEEDS
    start=time.process_time()
    records=[test_world(seed,scenario) for seed in seeds for scenario in SCENARIOS]
    result={"experiment_id":"ENERGY-TOPO-02","phase":"SMOKE" if args.smoke else "PRIMARY",
            "data_spec_sha256":hashlib.sha256(DATA_SPEC.encode()).hexdigest(),
            "seeds":seeds,"worlds":records,"summary":summarize(records),
            "environment":{"python":platform.python_version(),"platform":platform.platform()},
            "process_cpu_seconds":time.process_time()-start}
    with open(args.out,"w",encoding="utf-8") as f:
        json.dump(result,f,sort_keys=True,indent=2)
        f.write("\n")
    print(json.dumps({"phase":result["phase"],"summary":result["summary"],
                      "process_cpu_seconds":result["process_cpu_seconds"]},sort_keys=True))


if __name__ == "__main__":
    main()

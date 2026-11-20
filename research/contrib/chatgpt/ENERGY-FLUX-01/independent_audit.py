#!/usr/bin/env python3
"""Post-score independent numeric reproduction of ENERGY-FLUX-01.
Separate from frozen experiment.py. Not preregistered scorer; does not
rerun original-world protected first use or promote a scientific result.
"""
import hashlib
import json
import random
import math
import time
from pathlib import Path

SEEDS = (721101, 721127, 721147, 721169, 721181, 721199)
SCENARIOS = {"DRIFT": (.8, .2), "REVERSIBLE": (.5, .5),
             "ACTION_NULL": (.8, .8)}
ARMS = ("conservative", "flux", "row_markov", "exact_flux_bayes",
        "action_blind", "no_learning")

def rng(seed, scenario, act, phase, state=-1):
    data = f"energy-flux01|{seed}|{scenario}|{act}|{phase}|{state}"
    return random.Random(int.from_bytes(hashlib.sha256(
        data.encode("ascii")).digest()[:16], "big"))

def run():
    start = time.perf_counter()
    cpu = time.process_time()
    worlds = []
    for seed in SEEDS:
        for scenario, probs in SCENARIOS.items():
            witness = []
            for act in range(2):
                g = rng(seed, scenario, act, "train")
                for _ in range(8):
                    state = g.randrange(4)
                    cw = int(g.random() < probs[act])
                    nxt = (state + (1 if cw else -1)) % 4
                    witness.append((state, act, nxt))
            counts = [0, 0]
            rows = [[0]*4 for _ in range(2)]
            row_total = [[0]*4 for _ in range(2)]
            for state, act, nxt in witness:
                y = int(nxt == (state+1)%4)
                counts[act] += y
                rows[act][state] += y
                row_total[act][state] += 1
            means = [(1+counts[a])/10 for a in range(2)]
            blind = (1+sum(counts))/18
            row = [[(1+rows[a][s])/(2+row_total[a][s])
                    for s in range(4)] for a in range(2)]
            scores = {arm: {"brier_sum":0., "correct":0, "n":0}
                      for arm in ARMS}
            held_sha = hashlib.sha256()
            for act in range(2):
                for state in range(4):
                    g = rng(seed, scenario, act, "held", state)
                    for _ in range(256):
                        y = int(g.random() < probs[act])
                        nxt = (state+(1 if y else -1))%4
                        held_sha.update(bytes((state,act,nxt)))
                        ps = {
                            "conservative": .5, "flux": means[act],
                            "row_markov": row[act][state],
                            "exact_flux_bayes": means[act],
                            "action_blind": blind, "no_learning": .5}
                        for arm,p in ps.items():
                            d = scores[arm]
                            d["brier_sum"] += (p-y)**2
                            d["correct"] += int((p>.5)==bool(y))
                            d["n"] += 1
            worlds.append({
                "seed":seed, "scenario":scenario,
                "counts":counts, "p":means,
                "held_sha256":held_sha.hexdigest(),
                "action_gap":means[0]-means[1],
                "declares":abs(means[0]-means[1])>=.30,
                "scores":scores,
            })
    summary = {}
    for scenario in SCENARIOS:
        subset = [w for w in worlds if w["scenario"]==scenario]
        arms = {}
        for arm in ARMS:
            n = sum(w["scores"][arm]["n"] for w in subset)
            arms[arm] = {
                "brier":sum(w["scores"][arm]["brier_sum"] for w in subset)/n,
                "accuracy":sum(w["scores"][arm]["correct"] for w in subset)/n,
                "n":n}
        summary[scenario] = {
            "arms": arms,
            "action_gap_declarations":sum(w["declares"] for w in subset),
            "clockwise_0_choices":sum(w["action_gap"]>=0 for w in subset)}
    return {
        "protocol":"ENERGY-FLUX-01",
        "execution":"postscore_independent_reimplementation",
        "seeds":SEEDS, "worlds":worlds, "summary":summary,
        "witnesses":len(worlds)*16, "held_events":len(worlds)*2048,
        "cycle_affinity":4*math.log(4),
        "wall_seconds":time.perf_counter()-start,
        "cpu_seconds":time.process_time()-cpu}

if __name__=="__main__":
    result=run()
    path=Path(__file__).with_name("independent_result.json")
    path.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",
                    encoding="utf-8")
    for family,sc in result["summary"].items():
        print(family, {a:round(sc["arms"][a]["brier"],8) for a in ARMS},
              "false_declarations",sc["action_gap_declarations"])
    print("witnesses",result["witnesses"],
          "held_events",result["held_events"])

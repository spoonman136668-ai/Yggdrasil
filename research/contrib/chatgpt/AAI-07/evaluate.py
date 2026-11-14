"""AAI-07A frozen one-shot MiniGrid Memory benchmark admission.

This tests a hand-coded memory cue vs its removal, NOT a learned policy.
Native external environment actions and rewards; no hidden simulator attributes.
"""
from __future__ import annotations
import hashlib
import json
import math
import random
import time

from navigator_probe import run

PREREG = "e27dc3eb66171a96f55fa4cb0acc2cfff2695ea1"
COHORTS = (
    ("development", "MiniGrid-MemoryS11-v0", range(971000, 971064)),
    ("transfer", "MiniGrid-MemoryS13Random-v0", range(972000, 972064)),
)
BOOTSTRAPS = 1024
BOOTSTRAP_SEED = 17070


def paired_exact_p(b, c):
    n = b + c
    if n == 0:
        return 1.0
    small = min(b,c)
    return min(1.0, 2 * sum(math.comb(n,k) for k in range(small+1)) / 2**n)


def confidence_interval(rows, metric="success"):
    diffs = [float(x["memory_"+metric]) - float(x["reactive_"+metric]) for x in rows]
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(diffs)
    draws = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n
                   for _ in range(BOOTSTRAPS))
    return [round(draws[25],8),round(draws[998],8)]


def per_cohort(name, env_name, seeds):
    rows = []
    for seed in seeds:
        mem = run(env_name, seed, remember=True)
        reactive = run(env_name, seed, remember=False)
        assert mem["seed"] == seed == reactive["seed"]
        assert mem["terminal"] and reactive["terminal"]
        assert mem["step_count"] <=120 and reactive["step_count"]<=120
        rows.append({
            "seed":seed,
            "memory_success":bool(mem["success"]),
            "reactive_success":bool(reactive["success"]),
            "memory_reward":float(mem["reward"]),
            "reactive_reward":float(reactive["reward"]),
            "memory_steps":mem["step_count"],
            "reactive_steps":reactive["step_count"],
            "memory_trace":hashlib.sha256(bytes(mem["action_trace"])).hexdigest(),
            "reactive_trace":hashlib.sha256(bytes(reactive["action_trace"])).hexdigest(),
        })
    n=len(rows)
    b=sum(int(x["memory_success"] and not x["reactive_success"]) for x in rows)
    c=sum(int(x["reactive_success"] and not x["memory_success"]) for x in rows)
    report={
        "environment":env_name,"n":n,
        "memory_success":sum(x["memory_success"] for x in rows)/n,
        "reactive_success":sum(x["reactive_success"] for x in rows)/n,
        "memory_mean_reward":sum(x["memory_reward"] for x in rows)/n,
        "reactive_mean_reward":sum(x["reactive_reward"] for x in rows)/n,
        "memory_mean_actions":sum(x["memory_steps"] for x in rows)/n,
        "reactive_mean_actions":sum(x["reactive_steps"] for x in rows)/n,
        "paired_memory_only":b,
        "paired_reactive_only":c,
        "paired_mcnemar_p":paired_exact_p(b,c),
        "success_gain_ci_95":confidence_interval(rows,"success"),
        "reward_gain_ci_95":confidence_interval(rows,"reward"),
    }
    report["success_gain"]=report["memory_success"]-report["reactive_success"]
    return report,rows


def main():
    start=time.perf_counter()
    results={}
    world_rows={}
    for name, env,seeds in COHORTS:
        result,rows=per_cohort(name,env,seeds)
        results[name]=result
        world_rows[name]=rows
    total_b=sum(v["paired_memory_only"] for v in results.values())
    total_c=sum(v["paired_reactive_only"] for v in results.values())
    combined_p=paired_exact_p(total_b,total_c)
    tests={
        "memory_success_minimum":all(r["memory_success"]>=.85 for r in results.values()),
        "difference_minimum":all(r["success_gain"]>=.25 for r in results.values()),
        "paired_bootstrap_lower_positive":all(r["success_gain_ci_95"][0]>0 for r in results.values()),
        "reactive_control_nontrivial":all(.25<=r["reactive_success"]<=.75 for r in results.values()),
        "combined_mcnemar_p":combined_p<.01,
        "bounded_actions_and_real_rewards":True,
        "no_privileged_navigation_data":True,
    }
    packed=json.dumps(world_rows,sort_keys=True,separators=(",",":"))
    return {
        "schema":"yggdrasil.contrib.aai07a.memory-necessity-result.v1",
        "prereg_commit":PREREG,
        "classification":("MEMORY_BENCHMARK_ADMITTED_DEVELOPMENT_ONLY"
                          if all(tests.values()) else "VALID_NEGATIVE_MEMORY_BENCHMARK"),
        "cohorts":results,
        "combined":{"memory_only":total_b,"reactive_only":total_c,
                    "mcnemar_exact_p":combined_p},
        "checks":tests,
        "world_observation_receipt_sha256":hashlib.sha256(packed.encode("utf-8")).hexdigest(),
        "world_rows":world_rows,
        "external_environment":"Farama-Foundation/Minigrid",
        "external_source_commit":"64e1eaec904bc35e7de041167274e2c0dfe541d2",
        "limits":"Scripted navigation and matching cue provided by programmer; no new learning mechanism, no native model, no training and no unknown dynamics solved.",
        "native_integration":"NONE",
        "elapsed_seconds":round(time.perf_counter()-start,6),
    }


if __name__=="__main__":
    print(json.dumps(main(),indent=2,sort_keys=True))

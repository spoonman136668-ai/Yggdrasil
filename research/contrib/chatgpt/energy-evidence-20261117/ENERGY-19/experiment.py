#!/usr/bin/env python3
"""ENERGY-19: deterministic counterexample to path-MAP decision-making.

This is a *mathematical safety test*, not a trained classical energy learner,
not a CRAM reproduction, and not native Yggdrasil scientific first-use.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
from itertools import product
import json
from pathlib import Path

ACTIONS = (0, 1)
STATES = (0, 1)
GRID = (Fraction(0), Fraction(1,5), Fraction(2,5), Fraction(3,5), Fraction(4,5), Fraction(1))
# Primary binary-state, two-stage witnessed world: exact, predeclared probabilities.
PRIMARY = ((Fraction(3,5), Fraction(3,5)), (Fraction(9,10), Fraction(0)))

def values(success):
    """p(state|a)=1/2, maximize second-stage success in each state."""
    expectation = tuple(sum((success[a][s] for s in STATES), Fraction(0))/2 for a in ACTIONS)
    max_success_path = tuple(max(success[a])/2 for a in ACTIONS)
    return expectation, max_success_path

def choose(v):
    # When tied, return action 0; ties are not counted in grid mismatch cohorts.
    return int(v[1] > v[0])

def plan(success):
    expectation, max_path = values(success)
    return {"expected_action":choose(expectation),
            "single_witness_action":choose(max_path),
            "marginalized_energy_action":choose(expectation),
            "expected_values":[str(x) for x in expectation],
            "best_successful_path_probabilities":[str(x) for x in max_path],
            "single_witness_regret":str(expectation[choose(expectation)]-expectation[choose(max_path)])}

def score():
    primary = plan(PRIMARY)
    grid_cases = 0
    strict_cases = 0
    wrong_witness = 0
    corrected_mismatches = 0
    max_regret = Fraction(0)
    total_regret = Fraction(0)
    # 6^4 factorial enumeration, not a train/test benchmark.
    for p in product(GRID, repeat=4):
        world = (p[:2], p[2:])
        expected, path = values(world)
        grid_cases += 1
        if expected[0] == expected[1] or path[0] == path[1]:
            continue
        strict_cases += 1
        exp_action, path_action = choose(expected), choose(path)
        marg_action = choose(expected)
        corrected_mismatches += int(exp_action != marg_action)
        if exp_action != path_action:
            wrong_witness += 1
            regret = expected[exp_action]-expected[path_action]
            total_regret += regret
            max_regret = max(max_regret,regret)
    return {"gate":"ENERGY-19","classification":"EXACT_MATHEMATICAL_SAFETY_COUNTEREXAMPLE_ONLY",
            "predeclared_primary":primary,"grid":{"value_set":[str(v) for v in GRID],
            "evaluated":grid_cases,"strict_decisions":strict_cases,
            "wrong_single_witness":wrong_witness,
            "marginalized_energy_mismatches":corrected_mismatches,
            "max_regret":str(max_regret),"sum_regret":str(total_regret)},
            "training":"NONE","native_Yggdrasil":"NOT_EXECUTED",
            "scientific_pass":False,"source":"standalone finite two-action/two-state world"}

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();out=score();args.out.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps(out))
if __name__ == "__main__":main()

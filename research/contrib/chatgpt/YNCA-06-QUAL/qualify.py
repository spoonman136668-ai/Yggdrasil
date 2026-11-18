"""YNCA-06-QUAL: minimal falsification gates for four proposed frontier mechanisms.

Only source-free analytic/probe tests. Not implementations of full sheaf cohomology,
chemical reaction networks, Popperian co-evolution or thermodynamic hardware.
No original-science first-use, CKAD learner modification or hidden evaluation data.
"""
from __future__ import annotations
from itertools import combinations
import hashlib
import json
import math
from pathlib import Path
import sys

RULE_COUNT = 64
ACTIONS = tuple(range(1, 7))
SENSOR_FLIP = 0.05
NOISE_PAIRS = 100
NULL_FALSE_POSITIVE_CAP = 0.05
CHANGED_BITS = 20
TOTAL_BITS = 100


def laws():
    return tuple(tuple(0 if a == 0 else 1 if a == 7 else
                       (mask >> (a - 1)) & 1 for a in range(8))
                 for mask in range(RULE_COUNT))


LAWS = laws()


def entropy_binary(p):
    if p == 0 or p == 1:
        return 0.0
    return -p * math.log2(p) - (1-p) * math.log2(1-p)


def ipfc_scores(compatible):
    """Falsifier disagreement vs exact one-step EIG for noiseless Boolean bits."""
    n = len(compatible)
    return {action: {
        "disagreement": 2 * (sum(rule[action] for rule in compatible) / n) *
                          (1 - sum(rule[action] for rule in compatible) / n),
        "expected_information_gain_bits":
            entropy_binary(sum(rule[action] for rule in compatible) / n),
    } for action in ACTIONS}


def select_by(compatible, metric):
    values = ipfc_scores(compatible)
    return max(ACTIONS, key=lambda action: (values[action][metric], -action))


def ipfc_gate():
    identical_paths = 0
    residual_class_sizes = set()
    final_paths = set()
    for actual_law in LAWS:
        ipfc = list(LAWS)
        eig = list(LAWS)
        steps_ipfc, steps_eig = [], []
        for _ in range(2):
            proposed = select_by(ipfc, "disagreement")
            expected = select_by(eig, "expected_information_gain_bits")
            steps_ipfc.append(proposed)
            steps_eig.append(expected)
            ipfc = [candidate for candidate in ipfc if
                    candidate[proposed] == actual_law[proposed]]
            eig = [candidate for candidate in eig if
                   candidate[expected] == actual_law[expected]]
        identical_paths += int(steps_ipfc == steps_eig and ipfc == eig)
        residual_class_sizes.add(len(ipfc))
        final_paths.add(tuple(steps_ipfc))
    uniform = ipfc_scores(list(LAWS))
    assert len(LAWS) == RULE_COUNT
    assert identical_paths == RULE_COUNT
    assert residual_class_sizes == {16}
    assert final_paths == {(1, 2)}
    assert all(abs(uniform[action]["disagreement"]-0.5) < 1e-12
               and abs(uniform[action]["expected_information_gain_bits"]-1.0) < 1e-12
               for action in ACTIONS)
    return {
        "scope": "exact YNCA05 64 independent off-diagonal Boolean bits, noiseless probes",
        "laws": RULE_COUNT,
        "paths_compared": RULE_COUNT,
        "identical_IPFC_disagreement_and_EIG_paths": identical_paths,
        "distinct_paths": [list(x) for x in sorted(final_paths)],
        "remaining_laws_after_two_probes": sorted(residual_class_sizes),
        "max_first_action_disagreement": 0.5,
        "max_first_action_EIG_bits": 1.0,
        "original_fixture_gate": "NO_UNIQUE_ADVANTAGE_OVER_EIG",
        "next_allowed": "Only a separately frozen structured-world coevolution experiment with an independent generator and stronger EIG/Bayes baseline.",
    }


def binomial_tail(n, cutoff, p):
    return math.fsum(math.comb(n, k) * p**k * (1-p)**(n-k)
                     for k in range(cutoff, n+1))


def scdr_gate():
    # Graph cycle rank H1(underlying graph), not sheaf cohomology.
    # A deterministic, fully observable 3-node Markov cycle needs no latent bit.
    transition = {"A": "B", "B": "C", "C": "A"}
    assert transition["C"] == "A"
    graph_betti_1 = 3 - 3 + 1  # E-V+connected_components
    false_conflict_pair = 2 * SENSOR_FLIP * (1-SENSOR_FLIP)
    naive_false_alarm = 1 - (1 - false_conflict_pair)**NOISE_PAIRS
    threshold = next(k for k in range(NOISE_PAIRS+1)
                     if binomial_tail(NOISE_PAIRS, k, false_conflict_pair)
                     <= NULL_FALSE_POSITIVE_CAP)
    calibrated_null_alarm = binomial_tail(NOISE_PAIRS, threshold,
                                           false_conflict_pair)
    # Alternating true hidden parity in each paired read, independently flipped:
    true_contrast_pair = (1-SENSOR_FLIP)**2 + SENSOR_FLIP**2
    parity_detection = binomial_tail(NOISE_PAIRS, threshold,
                                      true_contrast_pair)
    assert graph_betti_1 == 1
    assert naive_false_alarm > 0.05
    assert calibrated_null_alarm <= 0.05
    assert parity_detection >= 0.95
    return {
        "scope": "topological graph-cycle screening + exact independent sensor-flip null; NOT computed sheaf H1",
        "visible_markov_cycle_nodes": len(transition),
        "visible_markov_cycle_edges": len(transition),
        "graph_cycle_rank": graph_betti_1,
        "hidden_state_needed_for_visible_cycle": False,
        "sensor_flip_probability": SENSOR_FLIP,
        "paired_revisits": NOISE_PAIRS,
        "noise_only_pair_disagreement_probability": round(false_conflict_pair, 12),
        "naive_ever_disagree_false_alarm": round(naive_false_alarm, 12),
        "calibrated_conflict_count_threshold": threshold,
        "calibrated_noise_null_false_alarm": round(calibrated_null_alarm, 12),
        "calibrated_alternating_parity_detection": round(parity_detection, 12),
        "original_fixture_gate": "CYCLE_NOT_PROOF_OF_LATENT_AND_NAIVE_NOISE_ALARM_FAILS",
        "next_allowed": "Specify a genuine cellular sheaf and restriction maps; independently compare with calibrated binomial and fully fitted HMM/POMDP under noisy heldout, otherwise stop.",
    }


def bayesian_context_update(weights, observations):
    contexts = tuple(range(3))
    prior = tuple(weights)
    for observed in observations:
        likelihood = [0.9 if observed == context else 0.05
                      for context in contexts]
        evidence = sum(prior[i]*likelihood[i] for i in contexts)
        prior = tuple(prior[i]*likelihood[i]/evidence for i in contexts)
    return prior


def replicator_context_update(weights, observations):
    # Minimal "kinetic" multiplicative selector = exactly Bayesian evidence.
    concentrations = list(weights)
    for observed in observations:
        for context in range(3):
            concentrations[context] *= 0.9 if observed == context else 0.05
        total = sum(concentrations)
        concentrations = [x/total for x in concentrations]
    return tuple(concentrations)


def crn_gate():
    initial = (1/3, 1/3, 1/3)
    if_no_context_cue = max(initial)
    trajectories = (
        (), (0,), (0, 0, 0, 0, 0, 1, 1, 1, 1, 1),
        (2, 2, 2, 2, 1, 1, 1, 1, 0, 0),
        (0, 1, 2, 0, 1, 2, 0, 1, 2),
    )
    maximum_diff = max(
        max(abs(a-b) for a,b in zip(bayesian_context_update(initial, path),
                                    replicator_context_update(initial, path)))
        for path in trajectories)
    assert maximum_diff < 1e-12
    assert abs(if_no_context_cue - 1/3) < 1e-12
    return {
        "scope": "three uniformly likely hidden contexts, no discriminating context cue; a simple multiplicative chemical selector",
        "context_count": 3,
        "best_possible_expected_context_accuracy_before_observation":
            round(if_no_context_cue, 12),
        "bayes_vs_replicator_max_probability_deviation":
            round(maximum_diff, 12),
        "tested_evidence_trajectories": len(trajectories),
        "original_fixture_gate": "NO_CUE_IDENTIFIABILITY_CEILING_AND_MULTIPLICATIVE_SELECTOR_IS_BAYES",
        "next_allowed": "Specify true mass-action rates, irreversible composition rewiring, stable kinetics, and a fresh information/compute-matched switch task; stop if only reparameterized Bayes.",
    }


def ltm_gate():
    # Strongest simple no-forgetting control for direct-address deterministic
    # feedback. The independent author-provided thermal proposal is not built.
    old = [i & 1 for i in range(TOTAL_BITS)]
    updated_truth = list(old)
    changed = tuple(range(0, TOTAL_BITS, 5))
    for i in changed:
        updated_truth[i] ^= 1
    simple = list(old)
    writes = 0
    for i in changed:
        if simple[i] != updated_truth[i]:
            simple[i] = updated_truth[i]
            writes += 1
    untouched = [i for i in range(TOTAL_BITS) if i not in changed]
    unchanged_errors = sum(simple[i] != old[i] for i in untouched)
    changed_errors = sum(simple[i] != updated_truth[i] for i in changed)
    assert len(changed) == CHANGED_BITS
    assert writes == CHANGED_BITS
    assert unchanged_errors == 0 and changed_errors == 0
    return {
        "scope": "100 independent directly addressed deterministic binary rules, exactly 20 changed, feedback identifies each changed address",
        "total_rule_bits": TOTAL_BITS,
        "changed_rule_bits": CHANGED_BITS,
        "retained_untouched_rule_bits": len(untouched),
        "simple_sparse_direct_edit_count": writes,
        "untouched_rule_error_after_direct_update": unchanged_errors,
        "changed_rule_error_after_direct_update": changed_errors,
        "measured_physical_energy": False,
        "original_fixture_gate": "SPARSE_DIRECT_EDIT_ALREADY_PERFECT_NO_THERMAL_GAIN_SHOWN",
        "next_allowed": "Move to genuinely coupled, uncertain, partially addressed multiworld feedback with exact sparse-update/EWC/forgetting controls and measured compute/energy.",
    }


def qualify():
    return {
        "schema": "yggdrasil.ynca06.four-frontier-early-stop.v1",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "input_ideas": ["IPFC", "SCDR", "CRN", "LTM"],
        "scope": "Stage0 source-free falsification screens only; no full mechanisms, model training or owner action",
        "gates": {
            "IPFC": ipfc_gate(),
            "SCDR": scdr_gate(),
            "CRN": crn_gate(),
            "LTM": ltm_gate(),
        },
        "qualification": {
            "all_four_original_fixture_superiority_claims": "NOT_ESTABLISHED",
            "expensive_training_tuning_permitted_without_new_frozen_mechanism": False,
            "next_executable_mechanism": "Separately preregistered IPFC structured-equivalence test with truly novel counterexample generation, Bayesian EIG controls and independent worlds; not the YNCA05 fixture.",
        },
        "claims": {"scientific_pass": False, "native_yggdrasil_trained": False,
                   "accepted_ref_changed": False, "deployed": False},
    }


if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--run"], ["--check"]):
        raise SystemExit("usage: qualify.py [--run|--check]")
    result = qualify()
    if sys.argv[1:] == ["--check"]:
        print("YNCA06_FOUR_MECHANISM_EARLY_STOP_CHECK_PASS")
    else:
        print(json.dumps(result,sort_keys=True,indent=2))

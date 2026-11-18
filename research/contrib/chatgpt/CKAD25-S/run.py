"""CKAD25-S: first prospective synthetic unfamiliar-family test of real CKAD native slots.

Runs the existing cumulative learner with actual observe/repaired checkpoint paths.
Preserve source-owned original CKAD25 checkpoint, original results, accepted main,
and all science first-use fences. Four procedural laws are evaluator-side ONLY.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import time
from collections import defaultdict
from pathlib import Path

from yggdrasil.native_ckad_dev_campaign import FILES as ORIGINAL_FILES
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

ROOT = Path(__file__).resolve().parents[4]
ORIGINAL = ROOT / "research/contrib/chatgpt/CKAD-25/qualified-development-runs/44331408493"
ORIGINAL_CHECKPOINT = "c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f"
SEEDS = (1103, 2207, 3301)
LAWS = ("parity3", "majority3", "conditional-mux", "mixed4")
METHODS = ("native_sparse", "native_degree", "uniform", "frequency", "cart", "forest",
           "logistic", "exact_sparse3")


def require(ok, msg):
    if not ok:
        raise ValueError("CKAD25S_" + msg)


def inputs(mask):
    return ((mask >> 0) & 1, (mask >> 1) & 1,
            (mask >> 2) & 1, (mask >> 3) & 1)


def law_outcome(law, mask):
    c0, c1, c2, action = inputs(mask)
    # Distinct unseen generator rules; NEVER passed to native learner or controls.
    if law == "parity3":
        return c0 ^ c1 ^ action
    if law == "majority3":
        return int(c0 + c1 + action >= 2)
    if law == "conditional-mux":
        return c2 if action else c0
    if law == "mixed4":
        return (c1 & (c2 | action)) ^ c0
    raise ValueError("invalid evaluator law")


def split(law, seed):
    generator_seed = int.from_bytes(hashlib.sha256(
        canonical(["CKAD25-S-input-order", law, seed])).digest()[:8], "big")
    order = list(range(16))
    random.Random(generator_seed).shuffle(order)
    revealed = [[m & 7, m >> 3, law_outcome(law, m)] for m in order[:12]]
    held = [[m & 7, m >> 3, law_outcome(law, m)] for m in order[12:]]
    require(len(set((c, a) for c, a, _ in revealed + held)) == 16, "SPLIT_OVERLAP")
    return revealed, held


def snapshot():
    linux = (ORIGINAL/"linux/stage-02.native.json").read_bytes()
    windows = (ORIGINAL/"windows/stage-02.native.json").read_bytes()
    require(linux == windows and digest(linux) == ORIGINAL_CHECKPOINT,
            "CKAD25_SOURCE_CHECKPOINT_NOT_PINNED")
    for platform in ("linux", "windows"):
        record = json.loads((ORIGINAL/platform/"campaign-result.json").read_bytes())
        require(record["final_checkpoint_sha256"] == ORIGINAL_CHECKPOINT and
                record["stages_completed"] == 2 and record["observations"] == 12 and
                record["scientific_first_use"] is False and
                record["scientific_pass"] is False, "CKAD25_ORIGINAL_CUSTODY")
    original = NativeCumulativeLearner.restore(linux, ORIGINAL_CHECKPOINT)
    require(original.info()["observed_inputs"][0] == 12 and
            original.info()["events"] == 2, "CKAD25_ORIGINAL_NATIVE_SOURCE")
    return original


def vector(c, a):
    return [*[(c >> bit) & 1 for bit in range(3)], a]


def terms(c, a):
    bits = c | (a << 3)
    return [int((bits & monomial) == monomial) for monomial in range(16)]


def two_class_probability(model, xs):
    return [float(row[list(model.classes_).index(1)]) if 1 in model.classes_
            else 0.0 for row in model.predict_proba(xs)]


def sparse3_exact(revealed, held):
    # Symmetric exact posterior over all GF(2) ANF expressions using <=3
    # of the 16 four-input monomials. This is a strong fixed small prior,
    # although not a universal causal-operator oracle.
    solutions = []
    train_rows = [(terms(c,a), y) for c,a,y in revealed]
    for degree in range(4):
        for active in itertools.combinations(range(16), degree):
            if all((sum(features[j] for j in active) & 1) == y
                   for features,y in train_rows):
                solutions.append(active)
    if not solutions:
        return [0.5] * len(held), False
    probabilities = []
    for c,a,_ in held:
        features = terms(c,a)
        probabilities.append(sum((sum(features[j] for j in active) & 1)
                                 for active in solutions) / len(solutions))
    return probabilities, True


def conventional(revealed, held, seed):
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression

    x_train = [vector(c,a) for c,a,_ in revealed]
    x_test = [vector(c,a) for c,a,_ in held]
    ys = [int(y) for _,_,y in revealed]
    p_frequency = (1 + sum(ys)) / (len(ys) + 2)
    results = {
        "uniform": [0.5] * len(held),
        "frequency": [p_frequency] * len(held),
    }
    cart = DecisionTreeClassifier(max_depth=4, random_state=seed).fit(x_train,ys)
    forest = RandomForestClassifier(n_estimators=64,max_depth=4,n_jobs=1,
                                    random_state=seed).fit(x_train,ys)
    results["cart"] = two_class_probability(cart,x_test)
    results["forest"] = two_class_probability(forest,x_test)
    if len(set(ys)) > 1:
        x_anf = [terms(c,a) for c,a,_ in revealed]
        t_anf = [terms(c,a) for c,a,_ in held]
        logistic = LogisticRegression(C=1.0,max_iter=1000,solver="lbfgs",
                                      random_state=seed).fit(x_anf,ys)
        results["logistic"] = two_class_probability(logistic,t_anf)
    else:
        results["logistic"] = [float(ys[0])] * len(held)
    results["exact_sparse3"], supported = sparse3_exact(revealed,held)
    return results, supported


def score(predictions, held):
    require(len(predictions) == len(held) == 4, "PREDICTION_COUNT")
    answers = [None if x is None else float(x) for x in predictions]
    probabilities = [0.5 if x is None else x for x in answers]
    require(all(0 <= p <= 1 for p in probabilities), "INVALID_PROBABILITY")
    truths = [y for _,_,y in held]
    return {
        "brier": round(sum((p-y)**2 for p,y in zip(probabilities,truths))/4,9),
        "answered": sum(x is not None for x in answers),
        "correct_answered": sum(x is not None and x == y for x,y in zip(answers,truths)),
        "incorrect_answered": sum(x is not None and x != y for x,y in zip(answers,truths)),
    }


def prospective():
    start = time.monotonic()
    parent = snapshot()
    parent_checkpoint = parent.checkpoint()
    old_slot_predictions = [parent.predict(0,c,a) for a in (0,1) for c in range(8)]
    rows = []
    for seed in SEEDS:
        working = NativeCumulativeLearner.restore(parent_checkpoint, ORIGINAL_CHECKPOINT)
        revealed_by_slot = {}
        held_by_slot = {}
        for slot,law in enumerate(LAWS, start=1):
            train, held = split(law,seed)
            ref = digest(canonical(["CKAD25-S-public-developer-source",seed,slot]))
            for batch in (train[:8], train[8:]):
                working = working.observe(slot,batch,digest(canonical(batch)),source_ref=ref)
            revealed_by_slot[slot] = train
            held_by_slot[slot] = held
        pre_repair = NativeCumulativeLearner.restore(working.checkpoint(),digest(working.checkpoint()))
        repaired = working
        modes = {}
        for slot in range(1,5):
            h = repaired._hypotheses[slot]
            require(h is not None, "HYPOTHESIS_ABSENT")
            if h.eligible:
                modes[slot] = "preexisting_eligible_degree"
            else:
                next_model, sparse, _cost = repaired.repair_sparse(slot)
                modes[slot] = ("eligible_sparse_repair" if next_model is not repaired
                               and sparse.eligible else "sparse_repair_declined")
                repaired = next_model
        repaired_raw = repaired.checkpoint()
        cold = NativeCumulativeLearner.restore(repaired_raw,digest(repaired_raw))
        # Preserve original 12-observation knowledge, provenance ledger and prior
        # native predictions, while adding four distinct laws to this SAME model.
        retained = (cold._properties.checkpoint() == parent._properties.checkpoint() and
                    cold._source._seen[0] == parent._source._seen[0] and
                    cold._events[:len(parent._events)] == parent._events and
                    cold._hypotheses[0].checkpoint() == parent._hypotheses[0].checkpoint() and
                    [cold.predict(0,c,a) for a in (0,1) for c in range(8)] ==
                    old_slot_predictions and
                    cold.checkpoint() == repaired_raw and
                    all(cold.info()["observed_inputs"][slot] == 12
                        for slot in range(1,5)) and
                    not any(cold.info()["quarantined"][:5]))
        require(retained, "RETENTION_OR_COLD_RESTORE")
        for slot,law in enumerate(LAWS, start=1):
            train,held = revealed_by_slot[slot],held_by_slot[slot]
            controls,sparse_supported = conventional(train,held,seed)
            controls["native_degree"] = [pre_repair.predict(slot,c,a) for c,a,_ in held]
            controls["native_sparse"] = [cold.predict(slot,c,a) for c,a,_ in held]
            values = {method:score(controls[method],held) for method in METHODS}
            rows.append({
                "seed":seed, "law":law, "slot":slot,
                "train_source_sha256":digest(canonical(train)),
                "held_inputs_sha256":digest(canonical([[c,a] for c,a,_ in held])),
                "held_truth_sha256":digest(canonical([y for _,_,y in held])),
                "mode":modes[slot], "exact_sparse3_model_supported":sparse_supported,
                "metrics":values, "old_slot_retained":retained,
            })
    require(len(rows) == 12, "COHORT_COUNT")
    means = {method:round(sum(r["metrics"][method]["brier"] for r in rows)/12,9)
             for method in METHODS}
    candidate_correct = sum(r["metrics"]["native_sparse"]["correct_answered"] for r in rows)
    candidate_answered = sum(r["metrics"]["native_sparse"]["answered"] for r in rows)
    best_control = min(means[m] for m in ("cart","forest","logistic","exact_sparse3"))
    gates = {
        "retained_previous_native_knowledge":all(r["old_slot_retained"] for r in rows),
        "native_answered_at_least_36_of_48":candidate_answered >= 36,
        "native_correct_at_least_36_of_48":candidate_correct >= 36,
        "native_brier_at_least_0_03_below_uniform":means["native_sparse"] <= 0.22,
        "native_within_0_02_of_best_strong_control":means["native_sparse"] <= best_control+0.02,
    }
    verdict = "DEVELOPMENT_SIGNAL" if all(gates.values()) else "DEVELOPMENT_MIXED_NO_GO"
    return {
        "schema":"yggdrasil.ckad25s.prospective-native-development.v1",
        "source_script_sha256":digest(Path(__file__).read_bytes()),
        "parent_checkpoint_sha256":ORIGINAL_CHECKPOINT,
        "seeds":list(SEEDS), "law_families":list(LAWS),
        "native_state_count":1, "prior_native_events":2,
        "new_synthetic_training_observations_per_seed":48,
        "new_synthetic_held_observations_per_seed":16,
        "protected_original_world_actions":0,
        "source_first_use":False,
        "native_learner_source_edited":False,
        "full_native_training_observation_count_per_slot":12,
        "candidate_correct_answered":candidate_correct,
        "candidate_answered":candidate_answered,
        "candidate_total":48,
        "brier_means":means,
        "best_strong_control_brier":best_control,
        "per_family_seed":rows,
        "gates":gates,
        "disposition":verdict,
        "scientific_pass":False,
        "accepted_model":False,
        "merge_authorized":False,
        "forge_dispatch_authorized":False,
        "promotion_authorized":False,
        "deployment_authorized":False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    doc = prospective()
    raw=canonical(doc)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(raw)
    print("CKAD25S_NATIVE_DEVELOPMENT=" + doc["disposition"])
    print("CKAD25S_ANSWERED=" + str(doc["candidate_answered"]) + "/48")
    print("CKAD25S_CORRECT=" + str(doc["candidate_correct_answered"]) + "/48")
    print("CKAD25S_BRIER=" + json.dumps(doc["brier_means"],sort_keys=True))
    print("CKAD25S_GATES=" + json.dumps(doc["gates"],sort_keys=True))
    print("CKAD25S_RESULT_SHA256=" + digest(raw))


if __name__=="__main__":
    main()

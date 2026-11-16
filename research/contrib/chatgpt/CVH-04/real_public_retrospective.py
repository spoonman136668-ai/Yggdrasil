"""CVH-04: retrospective real-source public-return learning, NO source-first-use.

Source data are 124 previously consumed native CausalGym MDPPCH.do public
actions from FKP26. No source import, reset, network access, seed reuse or
counterfactual generation. This is NOT a prospective scientific test.
"""
from __future__ import annotations

import argparse
from collections import namedtuple
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "CVH-01"
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))
from earned_memory import EarnedReturnMemory, FIELDS, _slot
from strong_conventional import batch_public_returns, immediate_only_public_returns

SOURCE_SHA = "c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
ARTIFACT_SHA = "4c877a6df5685516cc7ba445b2b90c90afb3674537ab741fb67adb5453e5c9ef"
ORIGINAL_SUMMARY_SHA = "bdad1c832fd008746d7eb9ae2bc248e30ffa4be4a3e667209c6bfc33a0a93c22"
SEEDS = (996100, 996101, 996102, 996103)
TRAIN = SEEDS[:2]
HELD = SEEDS[2:]
OBSERVATIONS_PER_WORLD = 31
MIN_SUPPORT = 2
HORIZON = 4
BAYES_STRENGTH = 2
PublicConsequence = namedtuple("PublicConsequence", FIELDS)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def hash_json(value):
    return sha256(canonical(value)).hexdigest()


def load_original_public(fixture=None):
    """Verify exact original FKP26 public receipts; no source simulator."""
    path = Path(fixture) if fixture is not None else HERE / "consumed_public_fixture.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    if (type(doc) is not dict
            or doc.get("schema") != "yggdrasil.cvh04.consumed-source-compact-public-fixture.v1"
            or doc.get("source_sha") != SOURCE_SHA):
        raise ValueError("CVH04_ORIGINAL_PUBLIC_FIXTURE_SCHEMA_OR_SOURCE_DRIFT")
    source = doc.get("fkp26")
    if (type(source) is not dict
            or source.get("pr") != 1158
            or source.get("run") != 43930489602
            or source.get("head") != "f99552f29947767eb8764c68ba72518327c3d25c"
            or source.get("artifact_id") != 14257634107
            or source.get("artifact_zip_sha256") != ARTIFACT_SHA
            or source.get("artifact_summary_sha256") != ORIGINAL_SUMMARY_SHA
            or source.get("source_real_first_use_previously_consumed") is not True):
        raise ValueError("CVH04_CONSUMED_SOURCE_CUSTODY_DRIFT")
    encoding = doc.get("encoding")
    if (type(encoding) is not dict or encoding.get("rows_per_seed") != OBSERVATIONS_PER_WORLD
            or encoding.get("bit_positions") != {
                "before":5,"action":4,"reward":3,"after":2,
                "terminated":1,"truncated":0}):
        raise ValueError("CVH04_PUBLIC_COMPACTION_CONTRACT_DRIFT")
    entries = doc.get("episodes")
    if type(entries) is not list or len(entries) != len(SEEDS):
        raise ValueError("CVH04_ORIGINAL_EPISODE_COUNT_DRIFT")
    worlds = {}
    for expected_seed, item in zip(SEEDS, entries):
        if (type(item) is not dict or item.get("seed") != expected_seed
                or type(item.get("rows_hex")) is not str):
            raise ValueError("CVH04_SOURCE_SEED_ORDER_OR_HEX_INVALID")
        try:
            values = bytes.fromhex(item["rows_hex"])
        except ValueError as exc:
            raise ValueError("CVH04_BAD_ORIGINAL_PUBLIC_HEX") from exc
        if len(values) != OBSERVATIONS_PER_WORLD or any(v >= 64 for v in values):
            raise ValueError("CVH04_SOURCE_PUBLIC_ACTION_COUNT_OR_RANGE")
        public = []
        events = []
        prev_after = None
        for index, v in enumerate(values):
            b, a, r, n, terminal, trunc = (
                (v >> 5) & 1, (v >> 4) & 1, (v >> 3) & 1,
                (v >> 2) & 1, bool(v & 2), bool(v & 1))
            if (terminal or trunc) != (index == len(values)-1) or terminal:
                raise ValueError("CVH04_ORIGINAL_TERMINAL_SEQUENCE_DRIFT")
            if prev_after is not None and b != prev_after:
                raise ValueError("CVH04_ORIGINAL_PUBLIC_STATE_CONTINUITY_DRIFT")
            # FKP26 mechanically used this exact original *untrained*
            # fixed public policy; no hidden evaluation choices existed.
            if a != ((b + index) % 2):
                raise ValueError("CVH04_ORIGINAL_PUBLIC_ACTION_POLICY_DRIFT")
            row = PublicConsequence(b, a, r, n, terminal, trunc)
            events.append(row)
            public.append(dict(before=b, action=a, reward=r, after=n,
                               terminated=terminal, truncated=trunc))
            prev_after = n
        trans_hash = hash_json(public)
        if trans_hash != item.get("public_transitions_sha256"):
            raise ValueError("CVH04_ORIGINAL_TRANSITIONS_SHA256_MISMATCH")
        receipt = dict(schema="fkp24.native-public-mdp-transcript.v1",
                       upstream_sha=SOURCE_SHA,
                       public_seed=expected_seed,
                       physical_do_actions=len(public),
                       ended_by_source=True,
                       budget_exhausted=False,
                       public_transitions_sha256=trans_hash,
                       public_transitions=public,
                       forbidden_info_passed_to_policy=False,
                       counterfactuals_used=False)
        if hash_json(receipt) != item.get("original_public_receipt_sha256"):
            raise ValueError("CVH04_FKP26_FULL_PUBLIC_RECEIPT_SHA_MISMATCH")
        if sum(x.reward for x in events) != item.get("earned_rewards"):
            raise ValueError("CVH04_SOURCE_EARNED_REWARD_COUNT_DRIFT")
        worlds[expected_seed] = tuple(events)
    return worlds


def four_step_targets(rows):
    """Evaluator-only actual observed-policy returns; NOT source oracle."""
    return tuple(
        sum(rows[t+lag].reward * (1 / (1 << lag))
            for lag in range(min(HORIZON, len(rows)-t)))
        for t in range(len(rows)))


def context_keys(rows):
    pa = pr = 2
    keys = []
    for event in rows:
        keys.append(_slot(pa, pr, event.before, event.action))
        if event.terminated or event.truncated:
            pa = pr = 2
        else:
            pa, pr = event.action, event.reward
    return tuple(keys)


def permuted_train_worlds(worlds):
    """Training-only negative corruption, NEVER genuine causal source replay."""
    result = []
    for seed in TRAIN:
        original = worlds[seed]
        rewards = [row.reward for row in original]
        shifted = rewards[7:] + rewards[:7]
        result.extend(PublicConsequence(
            row.before, row.action, shifted[i], row.after,
            row.terminated, row.truncated) for i, row in enumerate(original))
    return tuple(result)


def mean_square(predictions, actuals):
    if not predictions or len(predictions) != len(actuals):
        return None
    return sum((x-y)**2 for x,y in zip(predictions,actuals)) / len(actuals)


def canonicalize_report_precision(value):
    """Report-only 12-decimal normalization across CPU/Python float order.

    No model predictions, training, held labels, losses, or thresholds change.
    Applied strictly AFTER all frozen raw metric comparisons have finished.
    """
    if type(value) is float:
        return float(format(value, ".12f"))
    if type(value) is list:
        return [canonicalize_report_precision(x) for x in value]
    if type(value) is dict:
        return {k: canonicalize_report_precision(v)
                for k, v in value.items()}
    return value


def run_retrospective(fixture=None):
    """Source-open count ZERO. Exact frozen TRAIN then retrospective HELD."""
    worlds = load_original_public(fixture)
    training = tuple(row for seed in TRAIN for row in worlds[seed])
    if len(training) != 62 or len(worlds[HELD[0]])+len(worlds[HELD[1]])!=62:
        raise ValueError("CVH04_FROZEN_SPLIT_COUNT_DRIFT")
    # Train once, sequential, original public actions only.
    native = EarnedReturnMemory()
    for row in training:
        native.observe(row)
    snapshot = native.snapshot()
    cold = EarnedReturnMemory.restore(snapshot)
    if cold.snapshot() != snapshot or native.receipt() != sha256(snapshot).hexdigest():
        raise AssertionError("CVH04_ORIGINAL_NATIVE_COLD_CHECKPOINT_NOT_IDENTICAL")
    full_batch = batch_public_returns(training)
    if (native.count != full_batch[0] or native.total != full_batch[1]
            or sum(native.count) != 62 or native.seen != 62):
        raise AssertionError("CVH04_INDEPENDENT_EXACT_CONVENTIONAL_TRAIN_PARITY_FAIL")
    immediate = immediate_only_public_returns(training)
    train_return = tuple(x for seed in TRAIN
                         for x in four_step_targets(worlds[seed]))
    prior = sum(train_return) / len(train_return)
    shuff = EarnedReturnMemory()
    for row in permuted_train_worlds(worlds):
        shuff.observe(row)
    perm_count = tuple(shuff.count)
    perm_total = tuple(shuff.total)

    # For every prospective public (state,chosen_action) context, seal ALL
    # model and control predictions before reading any held return labels.
    all_predictions = []
    per_world = []
    for seed in HELD:
        episode = worlds[seed]
        keys = context_keys(episode)
        predictions = []
        for key, row in zip(keys,episode):
            n = native.count[key]
            fitted_native = (native.estimate(row.before,
                             (key // 4) // 3, (key // 4) % 3, row.action)
                             if n >= MIN_SUPPORT else None)
            exact = (full_batch[1][key] / (8*full_batch[0][key])
                     if full_batch[0][key] >= MIN_SUPPORT else None)
            bayes = ((full_batch[1][key] / 8 + BAYES_STRENGTH * prior) /
                     (full_batch[0][key] + BAYES_STRENGTH))
            immediate_p = (immediate[1][key] / (8 * immediate[0][key])
                           if immediate[0][key] >= MIN_SUPPORT else None)
            shifted_p = (perm_total[key] / (8 * perm_count[key])
                         if perm_count[key] >= MIN_SUPPORT else None)
            predictions.append({
                "source_seed":seed,
                "key":key,
                "native":fitted_native,
                "exact":exact,
                "bayes":bayes,
                "immediate":immediate_p,
                "shifted":shifted_p,
                "train_global":prior,
                "source_actions_to_learn":0,
            })
        # Only AFTER sealing candidate/control predictions for the entire
        # independent historical episode may evaluator read future rewards.
        labels = four_step_targets(episode)
        per_world.append({"seed":seed,"rows":len(episode),
                          "supported":sum(p["native"] is not None
                                          for p in predictions)})
        all_predictions.extend(zip(predictions,labels))

    supported = [(p,y) for p,y in all_predictions if p["native"] is not None]
    if any(p["native"] != p["exact"] for p,y in supported):
        raise AssertionError("CVH04_STRONG_EXACT_FITTED_CONTROL_DISAGREES")
    if any(p["native"] is not None and native.count[p["key"]] < MIN_SUPPORT
           for p,y in all_predictions):
        raise AssertionError("CVH04_UNSUPPORTED_NATIVE_RETURN_CLAIM")
    shift_overlap = [(p,y) for p,y in supported if p["shifted"] is not None]
    active = tuple(p["native"] for p,y in supported)
    truth = tuple(y for p,y in supported)
    global_supported = tuple(p["train_global"] for p,y in supported)
    every_truth = tuple(y for p,y in all_predictions)
    native_fallback = tuple(
        p["native"] if p["native"] is not None else p["train_global"]
        for p,y in all_predictions)
    prior_all = tuple(p["train_global"] for p,y in all_predictions)
    bayes_all = tuple(p["bayes"] for p,y in all_predictions)

    # Separate post-evaluation adaptation diagnostic replays only the already
    # consumed public tuples, into a NEW copy of training memory.
    continuing = EarnedReturnMemory.restore(snapshot)
    for seed in HELD:
        for row in worlds[seed]:
            continuing.observe(row)
    combined = training + tuple(row for seed in HELD for row in worlds[seed])
    final_batch = batch_public_returns(combined)
    preservation = (
        all(a>=b for a,b in zip(continuing.count,native.count))
        and all(a>=b for a,b in zip(continuing.total,native.total))
        and continuing.count == final_batch[0]
        and continuing.total == final_batch[1]
        and continuing.seen == 124
        and EarnedReturnMemory.restore(continuing.snapshot()).snapshot()
           == continuing.snapshot()
        and cold.snapshot() == snapshot
    )
    total_supported = len(supported)
    native_mse = mean_square(active,truth)
    prior_supported_mse = mean_square(global_supported,truth)
    signal = (total_supported >= 16 and native_mse is not None
              and prior_supported_mse - native_mse >= 0.01
              and preservation)
    metrics = {
        "source_physical_do_actions_reused":124,
        "source_new_do_actions":0,
        "train_original_source_actions":62,
        "retro_held_original_source_actions":62,
        "held_coverage_supported_n":total_supported,
        "held_unsupported_n":62-total_supported,
        "held_worlds":per_world,
        "native_supported_mse":native_mse,
        "global_prior_mse_on_native_supported":prior_supported_mse,
        "native_mse_advantage_over_train_global_supported":
            None if native_mse is None else prior_supported_mse-native_mse,
        "independent_exact_batch_agreements":total_supported,
        "independent_exact_batch_disagreements":0,
        "native_global_fallback_all_row_mse":
            mean_square(native_fallback,every_truth),
        "train_global_all_row_mse":mean_square(prior_all,every_truth),
        "bayesian_2_pseudocount_all_row_mse":
            mean_square(bayes_all,every_truth),
        "immediate_ablation_supported_mse":
            mean_square(tuple(p["immediate"] for p,y in supported),truth)
            if all(p["immediate"] is not None for p,y in supported) and supported
            else None,
        "negative_shifted_overlap_rows":len(shift_overlap),
        "negative_shifted_overlap_mse":mean_square(
            tuple(p["shifted"] for p,y in shift_overlap),
            tuple(y for p,y in shift_overlap)),
        "source_train_global_four_step_return":prior,
        "train_checkpoint_bytes":len(snapshot),
        "train_checkpoint_sha256":sha256(snapshot).hexdigest(),
        "continual_checkpoint_bytes":len(continuing.snapshot()),
        "continual_checkpoint_sha256":sha256(continuing.snapshot()).hexdigest(),
        "train_original_rows_preserved_in_posteval_memory":preservation,
    }
    if not preservation:
        raise AssertionError("CVH04_REAL_PUBLIC_CUMULATIVE_RETENTION_FAIL")
    # Frozen raw development comparison above is unchanged. Serialize
    # identical 12-decimal scientific reporting across Python 3.11/3.12.
    metrics = canonicalize_report_precision(metrics)
    result = {
        "schema":"yggdrasil.cvh04.real-source-consumed-public-return-development.v1",
        "parent_cvh03_sha":"0975c5d83aa9b0357735139cae3457338ec67027",
        "frozen_prereg_first": "d35ff1eb7afca66b586352eab988fcdbbd657569",
        "source_sha":SOURCE_SHA,
        "fkp26_original_run":43930489602,
        "fkp26_original_artifact":14257634107,
        "fkp26_zip_sha256":ARTIFACT_SHA,
        "training_seeds":list(TRAIN),
        "historically_consumed_held_seeds":list(HELD),
        "original_source_first_use":False,
        "actual_source_original_but_previously_consumed":True,
        "held_was_prospectively_blind":False,
        "hidden_private_source_info_seen":False,
        "source_reset_or_do_calls":0,
        "candidate":"unchanged CVH01 EarnedReturnMemory",
        "strongest_equal_information_control":"independent CVH01 batch_public_returns exact tie",
        "classification":"RETROSPECTIVE_SOURCE_PREDICTIVE_DEVELOPMENT_SIGNAL"
                         if signal else
                         "RETROSPECTIVE_SOURCE_PREDICTIVE_DEVELOPMENT_NO_GO",
        "frozen_development_signal":signal,
        "scientific_pass":False,
        "native_accepted":False,
        "deployment":False,
        "not_a_causal_off_policy_estimate":True,
        "metrics":metrics,
    }
    result["metric_receipt_sha256"] = hash_json(result)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--fixture",default=None)
    parser.add_argument("--output-json",required=True)
    args=parser.parse_args()
    value=run_retrospective(args.fixture)
    path=Path(args.output_json)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("CVH04_REAL_SOURCE_RETROSPECTIVE="+json.dumps({
        "classification":value["classification"],
        "metrics":value["metrics"],
        "receipt_sha256":value["metric_receipt_sha256"],
        "scientific_pass":False,
    },sort_keys=True,separators=(",",":")),flush=True)


if __name__=="__main__":
    main()

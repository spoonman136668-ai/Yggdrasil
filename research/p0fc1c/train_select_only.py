"""P0F-C1C: matched-capacity genuine-original TRAIN/SELECT history intervention.

Zero DEV/TEST/H1/H2 source episodes. The source-generated current/history features are
lawful original public observations only; sealed source private state is excluded.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import sys
import time

import numpy as np

from research.mr34e.public_alias import ENGINES, source, peak_rss, canon
from research.p0fc1b.full_public_controls import (
    FullFrameCategorical, TRAIN, SELECT, EPOCHS, BATCH, arrays,
    acquire, check_config, original_digest,
)

SCHEMA = "mass.p0fc1c.train-select-only.matched-history.v1"
FIRST_PROTOCOL = "005629efceea2542159eb6cd4968e1614e8559ab"
EXPECTED = {
    "DeepMindPycolabApprehend": {
        "train_sha": "5d34e2edf2dc02c63dba988b59037b825e4d5079b0eb4b4edf498710e230abb4",
        "select_sha": "428f075a21af5d09a15aaf0e530bf28cd9a5105d8559f71ae2e0a72d88d34391",
        "train_actions": 215, "select_actions": 53, "seed": 17,
    },
    "FaramaMiniGridDoorKey8": {
        "train_sha": "7e8e8cab70c5ffd8574233f78b9cf3e7e67ee41d328fd2efc2d96577263fe443",
        "select_sha": "0072822de54cd655e016e3661eb86088ca02af9b2eff97d4d80c38230a128408",
        "train_actions": 2304, "select_actions": 576, "seed": 31,
    }
}
RATE = 0.02
UNITS = 32
BOOT_SEED = 2901
BOOT_DRAWS = 1000


def mask_history(x, nact, frame_length):
    """Same 3-block tensor shape, only both historical input blocks set to zero."""
    block = frame_length + nact
    assert x.ndim == 2 and x.shape[1] == block*3
    out = x.copy()
    out[:, block:] = 0.
    if not np.array_equal(out[:, :block], x[:, :block]):
        raise ValueError("ORIGINAL_CURRENT_PUBLIC_INPUT_DRIFT")
    return out


def means_by_reset(s, scores):
    return [float(np.mean(scores[s == t])) for t in SELECT]


def boot_interval(delta):
    if len(delta) != len(SELECT) or any(not math.isfinite(x) for x in delta):
        raise ValueError("MATCHED_HISTORY_INVALID_CLUSTER")
    rng = random.Random(BOOT_SEED)
    draws = sorted(sum(delta[rng.randrange(len(delta))] for _ in delta)/len(delta)
                   for _ in range(BOOT_DRAWS))
    return [draws[24], draws[974]]


def classification(train_delta, select_delta, ci):
    # Deltas are masked loss minus visible loss; positive favors visible history.
    if train_delta > 1e-8 and select_delta < -1e-8:
        return "HISTORY_EXTRA_FEATURES_OVERFIT_OR_GENERALIZE_POORLY"
    if train_delta < -1e-8 and select_delta < -1e-8:
        return "HISTORY_INPUT_NOT_EFFECTIVELY_FITTED_UNDER_FIXED_BUDGET"
    if train_delta > 1e-8 and ci[0] > 0:
        return "TRAIN_SELECTION_HISTORY_SIGNAL_WITH_MATCHED_CAPACITY"
    return "MATCHED_CAPACITY_HISTORY_BENEFIT_INCONCLUSIVE"


def evaluate_source(name):
    expected = EXPECTED[name]
    train_rows, train_receipts = acquire(name, TRAIN)
    selection_rows, selection_receipts = acquire(name, SELECT)
    if (original_digest(train_receipts) != expected["train_sha"] or
        original_digest(selection_receipts) != expected["select_sha"] or
        len(train_rows) != expected["train_actions"] or
        len(selection_rows) != expected["select_actions"]):
        raise ValueError("ORIGINAL_P0FC1B_TRAIN_SELECTION_SOURCE_IDENTITY_DRIFT")
    actions = ENGINES[name]["actions"]
    xfit, yfit, train_seeds = arrays(train_rows, actions, True)
    xsel, ysel, select_seeds = arrays(selection_rows, actions, True)
    xmask_fit = mask_history(xfit, actions, yfit.shape[1])
    xmask_sel = mask_history(xsel, actions, yfit.shape[1])
    if not np.array_equal(xfit[:, :yfit.shape[1]+actions],
                          xmask_fit[:, :yfit.shape[1]+actions]):
        raise ValueError("CURRENT_INPUT_DRIFT")
    if (sorted(set(train_seeds.tolist())) != list(TRAIN) or
        sorted(set(select_seeds.tolist())) != list(SELECT) or
        set(TRAIN) & set(SELECT)):
        raise ValueError("ORIGINAL_TRAIN_SELECT_ROLE_DRIFT")

    model_reports = {}
    losses = {}
    for arm, xf, xs in (
        ("history_visible", xfit, xsel),
        ("history_masked", xmask_fit, xmask_sel),
    ):
        model = FullFrameCategorical(xf.shape[1], yfit, UNITS, expected["seed"])
        started = time.process_time_ns()
        model.train(xf, yfit, RATE, EPOCHS, expected["seed"])
        train_cpu_ns = time.process_time_ns() - started
        train_scores = model.score(xf, yfit)
        selection_scores = model.score(xs, ysel)
        if not all(np.isfinite(x).all() for x in (train_scores, selection_scores)):
            raise ValueError("NONFINITE_ORIGINAL_PUBLIC_TRAIN_SELECT_LOG_SCORE")
        losses[arm] = {"train": float(np.mean(train_scores)),
                       "select": float(np.mean(selection_scores))}
        model_reports[arm] = {
            "train_loss_nats_full_frame": losses[arm]["train"],
            "select_loss_nats_full_frame": losses[arm]["select"],
            "select_per_reset_cluster": means_by_reset(select_seeds, selection_scores),
            "training_cpu_ns": train_cpu_ns,
            "frozen_fit_updates": model.steps,
            "train_examples":len(yfit),
            "selection_examples":len(ysel),
            "trainable_parameters":sum(p.size for p in model.p),
            "checkpoint_bytes":model.checkpoint_bytes(),
            "trained_checkpoint_sha256":model.checkpoint_sha()
        }
    v = model_reports["history_visible"]
    m = model_reports["history_masked"]
    if (v["trainable_parameters"] != m["trainable_parameters"] or
        v["frozen_fit_updates"] != m["frozen_fit_updates"] or
        v["checkpoint_bytes"] != m["checkpoint_bytes"]):
        raise ValueError("MATCHED_CAPACITY_AND_FIT_BUDGET_DRIFT")
    by_cluster = [a-b for a,b in zip(m["select_per_reset_cluster"],
                                   v["select_per_reset_cluster"])]
    interval = boot_interval(by_cluster)
    dfit = m["train_loss_nats_full_frame"]-v["train_loss_nats_full_frame"]
    dsel = sum(by_cluster)/len(by_cluster)
    return {
        "original_source_sha":ENGINES[name]["sha"],
        "original_train_episode_digest":expected["train_sha"],
        "original_selection_episode_digest":expected["select_sha"],
        "original_train_reset_clusters":len(TRAIN),
        "original_selection_reset_clusters":len(SELECT),
        "original_train_native_action_steps":len(train_rows),
        "original_selection_native_action_steps":len(selection_rows),
        "frozen_train_epoch_count":EPOCHS, "frozen_batch_size":BATCH,
        "frozen_learning_rate":RATE,
        "frozen_train_only_selected_initial_seed":expected["seed"],
        "same_model_parameter_count":v["trainable_parameters"],
        "same_model_train_updates":v["frozen_fit_updates"],
        "arms":model_reports,
        "visible_history_train_gain_masked_minus_visible_nats":dfit,
        "visible_history_selection_cluster_gain_masked_minus_visible_nats":dsel,
        "paired_six_cluster_95pct_bootstrap":interval,
        "per_original_selection_seed_masked_minus_visible_nats":by_cluster,
        "selection_history_winning_source_resets":sum(z>0 for z in by_cluster),
        "development_diagnostic_disposition":classification(dfit,dsel,interval),
        "protected_or_former_DEV_seeds_reacquired":False
    }


def main(farama, pycolab):
    original_cfg = check_config()
    roots = {k:source(farama if k=="FaramaMiniGridDoorKey8" else pycolab,k)
             for k in ENGINES}
    for k,root in roots.items():
        if k == "FaramaMiniGridDoorKey8":
            sys.path.insert(0,str(root))
        else:
            sys.path.insert(0,str(root))
    from research.mr27.natural_memory import source_guard
    source_guard(roots["FaramaMiniGridDoorKey8"])
    started = time.process_time_ns()
    result = {name:evaluate_source(name) for name in ENGINES}
    for name in ENGINES:
        source(roots[name],name)
    receipt = {
        "schema":SCHEMA, "frozen_first_only_protocol_commit":FIRST_PROTOCOL,
        "original_parent_C1B_candidate":"2add84058d5c5466562a6a6c00e99ac4d90389b8",
        "original_C1B_contract_sha256":__import__("hashlib").sha256(
            __import__("pathlib").Path(__import__("research.p0fc1b.full_public_controls",
                                                  fromlist=["FROZEN"]).FROZEN).read_bytes()).hexdigest(),
        "source_reports":result,
        "source_role_types_used":["TRAIN","TRAIN_ONLY_SELECT"],
        "source_real_DEV_samples_generated":0,
        "scientific_first_use_consumed":False,
        "external_independent_custody":False,
        "native_cognition_demonstrated":False,
        "full_process_cpu_ns":time.process_time_ns()-started,
        "full_process_peak_rss_bytes":peak_rss(),
        "energy_measured":False,
        "scientific_admission":"NOT_QUALIFIED"
    }
    print("P0FC1C_MATCHED_TRAIN_SELECT="+canon(receipt))


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: python -m research.p0fc1c.train_select_only FARAMA PYCOLAB")
    main(sys.argv[1],sys.argv[2])

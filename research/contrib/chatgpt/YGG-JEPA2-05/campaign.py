"""YGG-JEPA2-05: ACTUAL cumulative Yggdrasil native + six-head continuation.

Source-bound isolated synthetic development. Fresh interventions score before
outcome revelation; original model is never restarted or accepted into main.
One learned future-state candidate practices public-history-matched rehearsal,
while equally updated new-only and mispaired controls start at exact same
original fitted weights. Original native + four prior heads are shared.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_jepa_future import (
    NativeFutureStateLearner, DirectLogistic, FutureStateHead,
    HORIZON, UPDATES, targets, observed_features, public_observed,
    primary_truth, primary_probabilities,
)
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "YGG-RET01"
OLD_CAMPAIGN = HERE.parent / "YGG-JEPA2-04" / "campaign.py"
PINS = {
    14071: {
        "new_seed": 99231, "episodes": 1006,
        "git_blob": "e2912ca930ad99ed23bfee4ce18d1e3945f6780a",
        "native_full_sha": "c9bd78d4636d9b71e5bca42a3cf52afcfb9a58267d83c3e7727deceab667e690",
    },
    14072: {
        "new_seed": 99247, "episodes": 981,
        "git_blob": "3f076a393a15911769c0a40d37ccafc06dfaf2b7",
        "native_full_sha": "724cc155863d2ac88265ddb3006a90702049ed54a53e52881939f063c002a31b",
    },
}
PREREG_SHA = "d0fa25aad2c6dc270eb0f863b6e93cbb89092f23"
BASE_SHA = "84bb01dc6b8cfe0a729db30f8637265aa38fd97e"
OLD_CAMPAIGN_BLOB = "dcb5ae2a4bd75ce1c99bc071de96cb23d2cd1455"
BETA_ARMS = ("beta_full", "beta_window24", "beta_window48", "beta_discount95")
ARMS = ("rehearsal", "matched_new", "plain_new", "mispaired", "frozen",
        "native", "direct", "chance", "no_action_input", *BETA_ARMS)
LATE_STARTS = tuple(range(6, 14))
CPU_LIMIT = 180.

def check(cond, label):
    if not cond:
        raise ValueError("YGG_JEPA2_05_" + label)

def git_blob(path):
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD:" + path.relative_to(ROOT).as_posix()],
        cwd=ROOT, text=True, timeout=20).strip()

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def score(p, y):
    a, b = np.asarray(p, dtype=np.float64), np.asarray(y, dtype=np.float64)
    check(a.shape == b.shape == (6,) and bool(np.isfinite(a).all())
          and bool(((a >= 0) & (a <= 1)).all()), "PREQUENTIAL_SCORE")
    return float(np.mean((a-b)**2))

def heads_pair(model):
    return (FutureStateHead.restore(model.sensory.checkpoint()),
            FutureStateHead.restore(model.reward.checkpoint()))

def predict(pair, x):
    return primary_probabilities(pair[0].predict(x), pair[1].predict(x))

def learn(pair, x, window):
    a, b = targets(window)
    pair[0].learn(x, a)
    pair[1].learn(x, b)

def old_memory(ledger, helpers):
    """Fit strong controls on ALL prior authentic source; never old-native refit.

    Original future weights are restored, not reconstructed. Retrospective
    old windows here train controls and provide witnessed replay exemplars.
    """
    direct = DirectLogistic()
    betas = helpers.Counts()
    memory = []
    for i in range(len(ledger)-HORIZON+1):
        root = ledger[i]
        view = root[1]
        plan = tuple((e[2], e[4]) for e in ledger[i:i+HORIZON])
        x = observed_features(view, plan, ledger[:i])
        window = helpers.old_window(ledger, i)
        s, r = targets(window)
        direct.learn(x, np.concatenate((s, r)))
        betas.update(public_observed(view), plan, primary_truth(window))
        memory.append((x, window))
    check(len(memory) == len(ledger)-2 and
          direct.steps == len(memory)*UPDATES and
          len(betas.windows) == len(memory), "CONTROL_PRETRAIN_EXPOSURE")
    return direct, betas, memory

def matched_old(x, memory):
    """One fixed context-addressed REHEARSAL from prior witnessed knowledge.

    Query and keys use ONLY public preintervention observations, publicly
    announced action plans, and historical observations preceding query.
    Previously witnessed source outcomes are accessed only AFTER match.
    """
    best_idx, best = None, None
    for i, (old_x, _) in enumerate(memory):
        d = float(np.dot((x[:9]-old_x[:9]), (x[:9]-old_x[:9])) +
                  .005*np.dot((x[9:]-old_x[9:]), (x[9:]-old_x[9:])))
        if best is None or d < best:
            best_idx, best = i, d
    check(best_idx is not None, "NO_RETRIEVABLE_OLD_WITNESS")
    return best_idx, best

def load_original(old_seed):
    pin = PINS[old_seed]
    original = PARENT / ("seed-%s-state.json" % old_seed)
    check(git_blob(original) == pin["git_blob"], "ORIGINAL_MODEL_BLOB")
    d = json.loads(original.read_bytes())
    reader_raw = d["reader_ascii"].encode("ascii")
    check(digest(reader_raw) == d["reader_sha256"], "ORIGINAL_READER_SHA")
    reader = json.loads(reader_raw)
    check(reader["current_sha256"] == pin["native_full_sha"] ==
          d["new_model_cold_sha256"], "ORIGINAL_FUTURE_SHA")
    raw = reader["current_ascii"].encode("ascii")
    check(digest(raw) == pin["native_full_sha"], "ORIGINAL_FUTURE_PIN")
    original_model = NativeFutureStateLearner.restore(raw, digest(raw))
    check(original_model.checkpoint() == raw and
          len(original_model.original.base.native._ledger) == pin["episodes"],
          "ORIGINAL_CUMULATIVE_RESTORE")
    return original_model, raw

def old_readout(model, prior_ledger, helpers):
    """Read-only old-training diagnostic; not held future science."""
    sample = [helpers.old_window(prior_ledger, i)
              for i in range(len(prior_ledger)-34,
                             len(prior_ledger)-2)]
    check(len(sample) == 32, "OLD_WITNESS_COUNT")
    features = [
        observed_features(prior_ledger[i][1],
                          tuple((e[2], e[4])
                                for e in prior_ledger[i:i+HORIZON]),
                          prior_ledger[:i])
        for i in range(len(prior_ledger)-34, len(prior_ledger)-2)
    ]
    labels = [primary_truth(w) for w in sample]
    pair = (model.sensory, model.reward)
    return features, labels, [score(predict(pair, x), y)
                              for x, y in zip(features, labels)]

def native_old(model, ledger):
    """Native one-step old-context readout; read-only, consumed diagnostic."""
    out = []
    native = model.original.base.native
    for _, views, a, s, b, r in ledger[-32:]:
        view = views[0]
        x1 = float(native.context_forecast(view, a))
        x2 = float(native.context_forecast(view, a, s, b))
        out.append(((x1-s)**2+(x2-r)**2)/2)
    return float(np.mean(out))

def run_seed(old_seed, source, helpers):
    began, cpu = time.perf_counter(), time.process_time()
    seed = PINS[old_seed]["new_seed"]
    model, old_raw = load_original(old_seed)
    old_ledger = tuple(model.original.base.native._ledger)
    old_native_sha = digest(model.original.base.native.checkpoint())
    old_head_sha = digest(canonical({
        "sensors": model.sensory.checkpoint(),
        "reward": model.reward.checkpoint(),
    }))
    current_pair = (model.sensory, model.reward)
    matched = heads_pair(model)
    plain = heads_pair(model)
    mispaired = heads_pair(model)
    frozen = heads_pair(model)
    original_counts = (model.sensory.windows, model.reward.windows)
    old_features, old_targets, before_losses = old_readout(
        model, old_ledger, helpers)
    before_old = float(np.mean(before_losses))
    before_native_old = native_old(model, old_ledger)

    direct, beta, memory = old_memory(old_ledger, helpers)
    events = source.generate(seed)
    seen = {x[0] for x in old_ledger}
    output = []
    pending = {}
    replay_choices = []
    for t, event in enumerate(events):
        check(event["index"] == t and event["seed"] == seed and
              event["source_id"] not in seen and
              event["actions"] == (event["row"]["x1"], event["row"]["x2"]),
              "FRESH_PUBLIC_SOURCE")
        seen.add(event["source_id"])
        # Forecast at the START of a known three-action intervention
        # sequence: not a single future outcome is available yet.
        if t <= len(events)-HORIZON:
            views = event["views"]
            plans = tuple(source.announced_plan(seed, t+i)
                          for i in range(HORIZON))
            check(plans[0] == event["actions"],
                  "PUBLIC_ANNOUNCED_PLAN")
            x = observed_features(views, plans,
                                  model.original.base.native._ledger)
            unacted = observed_features(views, plans,
                                        model.original.base.native._ledger,
                                        no_actions=True)
            current = {
                "rehearsal": predict(current_pair, x),
                "matched_new": predict(matched, x),
                "plain_new": predict(plain, x),
                "mispaired": predict(mispaired, x),
                "frozen": predict(frozen, x),
                "native": helpers.native_forecast(model.original, views,
                                                  plans),
                "direct": helpers.primary12(direct.predict(x)),
                "no_action_input": predict(current_pair, unacted),
                "chance": np.full((6,), .5, dtype=np.float64),
            }
            for arm in BETA_ARMS:
                current[arm] = beta.probabilities(
                    public_observed(views), plans, arm)
            check(set(current) == set(ARMS), "CONTROL_ARMS")
            pending[t] = {"x": x, "plans": plans,
                          "source_id": event["source_id"],
                          "forecasts": current, "phase": event["phase"]}
        # Exactly one new native + FOUR previous JEPA heads' original
        # intervention update, preserving the complete cumulative ledger.
        prior_count = len(model.original.base.native._ledger)
        model.observe_native(event["source_id"], event["views"],
                             event["row"])
        check(len(model.original.base.native._ledger) == prior_count+1,
              "ACTUAL_NATIVE_WITNESS_UPDATE")
        start = t-(HORIZON-1)
        if start in pending:
            p = pending.pop(start)
            window = events[start:t+1]
            truth = primary_truth(window)
            s, r = targets(window)
            labeled = np.concatenate((s, r))
            losses = {name:score(prob, truth)
                      for name, prob in p["forecasts"].items()}
            output.append({
                "seed": seed, "old_seed": old_seed,
                "start": start, "phase": p["phase"],
                "source_id": p["source_id"],
                "announced_plan": [list(x) for x in p["plans"]],
                "target": truth.astype(int).tolist(),
                "forecasts": {k:p["forecasts"][k].tolist()
                              for k in ARMS},
                "brier": losses,
            })
            idx, distance = matched_old(p["x"], memory)
            # The original cumulative model's existing two future-state
            # heads receive one newly observed future plus one HISTORICAL
            # already-witnessed causal future. No original head is reset.
            learn(current_pair, p["x"], window)
            learn(current_pair, memory[idx][0], memory[idx][1])
            learn(matched, p["x"], window)
            learn(matched, p["x"], window)
            learn(plain, p["x"], window)
            learn(mispaired, p["x"], window)
            shuffled_idx = (idx + 137) % len(memory)
            negative = (
                {"post": tuple(int(y) for y in memory[shuffled_idx][1][j]["post"]),
                 "row": dict(memory[shuffled_idx][1][j]["row"])}
                for j in range(HORIZON)
            )
            learn(mispaired, memory[idx][0], tuple(negative))
            direct.learn(p["x"], labeled)
            beta.update(public_observed(events[start]["views"]),
                        p["plans"], truth)
            replay_choices.append({
                "start": start, "matched_old_window_index": idx,
                "public_feature_distance": distance,
                "negative_old_target_index": shuffled_idx,
            })
    check(not pending and len(output) == 14 and len(replay_choices) == 14,
          "COMPLETE_THREE_STEP_FUTURES")
    final_ledger = tuple(model.original.base.native._ledger)
    check(final_ledger[:len(old_ledger)] == old_ledger and
          len(final_ledger) == len(old_ledger)+16 <= 1024,
          "EXACT_NATIVE_OLD_PREFIX_AND_CAPACITY")
    check(model.sensory.windows == original_counts[0]+28 and
          model.reward.windows == original_counts[1]+28 and
          matched[0].windows == original_counts[0]+28 and
          matched[1].windows == original_counts[1]+28 and
          plain[0].windows == original_counts[0]+14 and
          plain[1].windows == original_counts[1]+14 and
          mispaired[0].windows == original_counts[0]+28 and
          mispaired[1].windows == original_counts[1]+28 and
          frozen[0].checkpoint() == FutureStateHead.restore(
              json.loads(old_raw)["sensory"]).checkpoint() and
          frozen[1].checkpoint() == FutureStateHead.restore(
              json.loads(old_raw)["reward"]).checkpoint(),
          "JEPA_TRAINED_HEADS_MATCHED_UPDATES")
    final_raw = model.checkpoint()
    check(NativeFutureStateLearner.restore(
        final_raw, digest(final_raw)).checkpoint() == final_raw,
        "ACTUAL_NATIVE_SIX_HEAD_COLD_RESTORE")
    hist = {name: float(np.mean([
        score(predict(pair, x), y)
        for x, y in zip(old_features, old_targets)]))
        for name, pair in
        (("rehearsal", current_pair), ("matched_new", matched),
         ("plain_new", plain), ("mispaired", mispaired),
         ("frozen", frozen))}
    native_historical_after = native_old(model, old_ledger)
    late = [row for row in output if row["start"] in LATE_STARTS]
    check(len(late) == 8 and
          {row["start"] for row in late} == set(LATE_STARTS),
          "LATE_COHORT")
    pooled = {name:float(np.mean([row["brier"][name] for row in late]))
              for name in ARMS}
    conventional = min(pooled[name]
                       for name in ("direct", *BETA_ARMS))
    conditions = {
        "better_than_matched_new": pooled["rehearsal"] <=
                                   pooled["matched_new"] - .005,
        "better_than_best_conventional": pooled["rehearsal"] <=
                                         conventional - .005,
        "better_than_mispaired": pooled["rehearsal"] <=
                                 pooled["mispaired"] - .01,
        "old_horizon_retention": hist["rehearsal"] <= before_old+.03,
        "old_horizon_better_than_matched": hist["rehearsal"] <=
                                            hist["matched_new"]-.005,
        "native_historical_retention": native_historical_after <=
                                        before_native_old+.03,
    }
    check(math.isfinite(conventional) and all(math.isfinite(x)
          for x in hist.values()), "MEASURE_FINITE")
    final_heads_sha = digest(canonical({
        "sensors": model.sensory.checkpoint(),
        "reward": model.reward.checkpoint(),
    }))
    check(final_heads_sha != old_head_sha, "HEAD_PARAMETERS_ACTUALLY_UPDATED")
    cpu_elapsed = time.process_time() - cpu
    check(cpu_elapsed <= CPU_LIMIT, "CPU_BUDGET")
    result = {
        "seed": seed, "old_seed": old_seed,
        "old_native_episodes": len(old_ledger),
        "new_native_episodes": len(final_ledger)-len(old_ledger),
        "total_native_episodes": len(final_ledger),
        "original_native_sha256": old_native_sha,
        "original_model_sha256": digest(old_raw),
        "updated_model_sha256": digest(final_raw),
        "initial_future_heads_sha256": old_head_sha,
        "final_future_heads_sha256": final_heads_sha,
        "old_future_windows_before": list(original_counts),
        "old_future_windows_after": [model.sensory.windows,
                                      model.reward.windows],
        "historic_readonly_horizon_before": before_old,
        "historic_readonly_horizon_after": hist,
        "historic_readonly_native_before": before_native_old,
        "historic_readonly_native_after": native_historical_after,
        "new_late": pooled,
        "best_conventional": conventional,
        "new_horizon_starts": len(output),
        "late_horizon_starts": len(late),
        "new_original_public_witnesses": len(events),
        "conditions": conditions,
        "development_go": all(conditions.values()),
        "science_pass": False,
    }
    state = {
        "seed": seed, "old_seed": old_seed,
        "model_sha256": digest(final_raw),
        "model_ascii": final_raw.decode("ascii"),
        "matched_new_heads": [z.checkpoint() for z in matched],
        "plain_new_heads": [z.checkpoint() for z in plain],
        "mispaired_heads": [z.checkpoint() for z in mispaired],
        "frozen_heads": [z.checkpoint() for z in frozen],
        "old_model_sha256": digest(old_raw),
    }
    runtime = {"seed": seed, "cpu_seconds": cpu_elapsed,
               "wall_seconds": time.perf_counter()-began}
    return result, state, output, replay_choices, runtime

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    expected_prereg = subprocess.check_output([
        "git", "rev-parse",
        PREREG_SHA+":research/contrib/chatgpt/YGG-JEPA2-05/prereg.json"
    ], cwd=ROOT, text=True).strip()
    check(git_blob(HERE/"prereg.json") == expected_prereg,
          "FROZEN_PREREGISTRATION")
    check(git_blob(OLD_CAMPAIGN) == OLD_CAMPAIGN_BLOB,
          "CONVENTIONAL_CONTROL_SOURCE")
    source = load(HERE/"source.py", "ygg_jepa2_05_source")
    helpers = load(OLD_CAMPAIGN, "ygg_jepa2_04_controls")
    args.output.mkdir(parents=True, exist_ok=True)
    reports, runtimes = [], []
    for oldseed in sorted(PINS):
        report, state, trace, choices, timing = run_seed(
            oldseed, source, helpers)
        reports.append(report)
        runtimes.append(timing)
        for name, obj in (
            (f"seed-{oldseed}-state.json", state),
            (f"seed-{oldseed}-trace.json", trace),
            (f"seed-{oldseed}-replay.json", choices),
        ):
            (args.output/name).write_bytes(canonical(obj))
        print("YGG_JEPA2_05_ORIGINAL_NATIVE_CONTINUED",oldseed,
              "new_events",report["new_native_episodes"],
              "future_windows",report["new_horizon_starts"],
              "dev_go",report["development_go"],flush=True)
    summary = {
        "schema": "yggdrasil.jepa2-05.actual-cumulative-rehearsal-development.v1",
        "parent_sha":BASE_SHA,
        "prereg_first_sha":PREREG_SHA,
        "source_blob":git_blob(HERE/"source.py"),
        "controls_blob":OLD_CAMPAIGN_BLOB,
        "replicas":reports,
        "development_go":all(x["development_go"] for x in reports),
        "science_pass":False, "accepted_native":False,
        "training_provenance":"actual single original 7-component model per cohort",
        "historical_probes_are_already_consumed":True,
        "new_source_is_synthetic_development":True,
        "deployment":"NONE",
    }
    (args.output/"result.json").write_bytes(canonical(summary))
    (args.output/"timings.json").write_bytes(canonical(runtimes))
    print("YGG_JEPA2_05_"+("DEVELOPMENT_GO" if summary["development_go"]
                             else "DEVELOPMENT_NO_GO")+
          " SCIENCE_NOT_PASS",flush=True)

if __name__ == "__main__":
    main()

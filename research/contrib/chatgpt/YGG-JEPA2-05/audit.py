"""Independent original-receipt and score auditor for JEPA2-05.

Does not import campaign or rerun training; rebuilds the fresh public source,
checks exact witnessed native suffix and original prefix, independently
calculates every prequential metric and predeclared verdict from saved forecasts.
Previously observed historical metrics remain read-only diagnostics.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_jepa_future import (
    NativeFutureStateLearner, FutureStateHead, HORIZON, UPDATES,
    observed_features, public_observed, primary_truth,
    primary_probabilities,
)
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "YGG-RET01"
PINNED = {
    14071: (99231, 1006, "e2912ca930ad99ed23bfee4ce18d1e3945f6780a",
            "c9bd78d4636d9b71e5bca42a3cf52afcfb9a58267d83c3e7727deceab667e690"),
    14072: (99247, 981, "3f076a393a15911769c0a40d37ccafc06dfaf2b7",
            "724cc155863d2ac88265ddb3006a90702049ed54a53e52881939f063c002a31b"),
}
SOURCE_BLOB = "ee809ef04859d94f7e96f50d757635b6827d1f7c"
ARMS = ("rehearsal", "matched_new", "plain_new", "mispaired", "frozen",
        "native", "direct", "chance", "no_action_input", "beta_full",
        "beta_window24", "beta_window48", "beta_discount95")
LATE = set(range(6, 14))

def check(cond, code):
    if not cond:
        raise ValueError("YGG_JEPA2_05_AUDIT_" + code)

def git_blob(path):
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD:" + path.relative_to(ROOT).as_posix()],
        cwd=ROOT, text=True, timeout=20).strip()

def source_module():
    path = HERE/"source.py"
    check(git_blob(path) == SOURCE_BLOB, "FROZEN_NEW_SOURCE")
    spec = importlib.util.spec_from_file_location("jepa205_source",path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def score(prob, expected):
    p = np.asarray(prob, dtype=float)
    y = np.asarray(expected, dtype=float)
    check(p.shape == y.shape == (6,) and bool(np.isfinite(p).all()) and
          bool(((0 <= p)&(p <= 1)).all()), "SCORE_RANGE")
    return float(np.mean((p-y)**2))

def near(a,b, tolerance=1e-9):
    return type(a) in (float,int) and type(b) in (float,int) and \
        math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tolerance

def old_windows(ledger):
    # Mirror the published observation interpretation independently.
    out = []
    for i in range(len(ledger)-34,len(ledger)-2):
        events = []
        for record in ledger[i:i+3]:
            _, views, first, s2, second, reward = record
            u, _, w = public_observed(views)
            events.append({"post":(u,s2,w),
                           "row":{"s1":u,"x1":first,"s2":s2,
                                  "x2":second,"y":reward}})
        plans = tuple((x[2], x[4]) for x in ledger[i:i+3])
        f = observed_features(ledger[i][1],plans,ledger[:i])
        out.append((f,primary_truth(events)))
    return out

def predict_from_pair(pair, x):
    return primary_probabilities(pair[0].predict(x),pair[1].predict(x))

def old_brier(pair, windows):
    return sum(score(predict_from_pair(pair, x),y)
               for x,y in windows)/len(windows)

def audit(data_dir:Path):
    source = source_module()
    report_file = data_dir/"result.json"
    report = json.loads(report_file.read_bytes())
    check(report["schema"] ==
          "yggdrasil.jepa2-05.actual-cumulative-rehearsal-development.v1"
          and report["prereg_first_sha"] ==
          "d0fa25aad2c6dc270eb0f863b6e93cbb89092f23" and
          report["source_blob"] == SOURCE_BLOB and
          report["science_pass"] is False and
          report["accepted_native"] is False and
          report["deployment"] == "NONE", "ORIGINAL_RESULT_FIELDS")
    check(len(report["replicas"]) == 2, "TWO_PRESET_REPLICAS")
    verdict = []
    results = []
    for i, old_seed in enumerate(sorted(PINNED)):
        seed, n_old, blob, starting_sha = PINNED[old_seed]
        r = report["replicas"][i]
        check((r["old_seed"],r["seed"]) == (old_seed, seed) and
              r["old_native_episodes"]==n_old and
              r["new_native_episodes"]==16 and
              r["total_native_episodes"]==n_old+16 and
              r["new_horizon_starts"]==14 and
              r["late_horizon_starts"]==8 and
              r["original_model_sha256"]==starting_sha and
              r["science_pass"] is False, "CONTINUATION_RECEIPT")

        parent_path = PARENT/f"seed-{old_seed}-state.json"
        check(git_blob(parent_path)==blob, "ORIGINAL_CHECKPOINT_BLOB")
        parent = json.loads(parent_path.read_bytes())
        saved = json.loads(parent["reader_ascii"])
        initial_raw = saved["current_ascii"].encode("ascii")
        check(digest(initial_raw)==starting_sha, "INITIAL_SOURCE_SHA")
        initial = NativeFutureStateLearner.restore(initial_raw,starting_sha)
        old = tuple(initial.original.base.native._ledger)
        check(len(old)==n_old and
              digest(initial.original.base.native.checkpoint()) ==
              r["original_native_sha256"], "ORIGINAL_TRAINED_SOURCE")

        artifact = json.loads((data_dir/f"seed-{old_seed}-state.json").read_bytes())
        final_raw = artifact["model_ascii"].encode("ascii")
        check(digest(final_raw)==r["updated_model_sha256"] ==
              artifact["model_sha256"] and
              artifact["old_model_sha256"]==starting_sha,
              "SEALED_COLD_MODEL_SHA")
        model = NativeFutureStateLearner.restore(
            final_raw,r["updated_model_sha256"])
        check(model.checkpoint() == final_raw, "FINAL_COLD_BYTE_RESTORE")
        final = tuple(model.original.base.native._ledger)
        check(len(final)==n_old+16 and final[:n_old]==old,
              "ORIGINAL_NATIVE_LEDGER_PREFIX")
        new_events = source.generate(seed)
        for t,event in enumerate(new_events):
            native = final[n_old+t]
            check(native[0]==event["source_id"] and
                  native[1]==event["views"] and
                  native[2:]==(event["row"]["x1"],
                              event["row"]["s2"],
                              event["row"]["x2"],
                              event["row"]["y"]),
                  "AUTHENTIC_NEW_NATIVE_WITNESS")
        check(model.sensory.windows ==
              initial.sensory.windows +28 and
              model.reward.windows ==
              initial.reward.windows+28 and
              r["old_future_windows_after"] ==
              [model.sensory.windows,model.reward.windows] and
              r["old_future_windows_before"] ==
              [initial.sensory.windows,initial.reward.windows] and
              r["final_future_heads_sha256"] == digest(canonical({
                  "sensors":model.sensory.checkpoint(),
                  "reward":model.reward.checkpoint(),
              })) and
              r["initial_future_heads_sha256"] == digest(canonical({
                  "sensors":initial.sensory.checkpoint(),
                  "reward":initial.reward.checkpoint(),
              })), "ORIGINAL_SIX_HEAD_CONTINUATION")

        copies = {}
        for arm, field, update_count in (
            ("matched_new","matched_new_heads",28),
            ("plain_new","plain_new_heads",14),
            ("mispaired","mispaired_heads",28),
            ("frozen","frozen_heads",0),
        ):
            pairs = [FutureStateHead.restore(v)
                     for v in artifact[field]]
            check(len(pairs)==2 and pairs[0].kind=="sensors" and
                  pairs[1].kind=="reward" and
                  pairs[0].windows==initial.sensory.windows+update_count and
                  pairs[1].windows==initial.reward.windows+update_count,
                  "MATCHED_ORIGINAL_UPDATE_BUDGET")
            copies[arm] = pairs
        check(copies["frozen"][0].checkpoint()==initial.sensory.checkpoint()
              and copies["frozen"][1].checkpoint()==initial.reward.checkpoint(),
              "UNMODIFIED_OLD_HEADS")

        traces = json.loads((data_dir/f"seed-{old_seed}-trace.json").read_bytes())
        choices = json.loads((data_dir/f"seed-{old_seed}-replay.json").read_bytes())
        check(len(traces)==len(choices)==14, "COMPLETE_NEW_TARGETS")
        scores = {arm:[] for arm in ARMS}
        old_ids = {item[0] for item in old}
        for t, (record, chosen) in enumerate(zip(traces,choices)):
            start = new_events[t]
            window = new_events[t:t+3]
            expected = primary_truth(window).tolist()
            check(record["start"]==t and record["seed"]==seed and
                  record["old_seed"]==old_seed and
                  record["source_id"]==start["source_id"] and
                  record["phase"]==start["phase"] and
                  record["source_id"] not in old_ids and
                  record["announced_plan"]==
                     [list(source.announced_plan(seed,t+j)) for j in range(3)] and
                  record["target"]==expected and
                  set(record["forecasts"])==set(ARMS) and
                  set(record["brier"])==set(ARMS),
                  "INDEPENDENT_PUBLIC_WINDOW_AND_TARGET")
            for arm in ARMS:
                loss = score(record["forecasts"][arm],expected)
                check(near(loss,record["brier"][arm],1e-12),
                      "INDEPENDENT_NUMERIC_SCORE")
                if t in LATE:
                    scores[arm].append(loss)
            check(chosen["start"]==t and
                  0 <= chosen["matched_old_window_index"] < n_old-2 and
                  chosen["negative_old_target_index"] ==
                  (chosen["matched_old_window_index"]+137)%(n_old-2) and
                  math.isfinite(chosen["public_feature_distance"]) and
                  chosen["public_feature_distance"]>=0,
                  "DETERMINISTIC_REHEARSAL_EVIDENCE")
        mean = {arm:sum(values)/8 for arm,values in scores.items()}
        check(all(near(mean[arm],r["new_late"][arm],1e-10)
                  for arm in ARMS), "PRIMARY_DEVELOPMENT_LOSS_PARITY")
        best = min(mean[arm] for arm in
                   ("direct","beta_full","beta_window24",
                    "beta_window48","beta_discount95"))
        check(near(best,r["best_conventional"],1e-10),
              "STRONG_CONVENTIONAL_BENCHMARK")
        old_tasks = old_windows(old)
        before=old_brier((initial.sensory,initial.reward),old_tasks)
        after={
            "rehearsal":old_brier((model.sensory,model.reward),old_tasks),
            **{key:old_brier(pair,old_tasks) for key,pair in copies.items()},
        }
        check(near(before,r["historic_readonly_horizon_before"],1e-9)
              and all(near(after[key],
                           r["historic_readonly_horizon_after"][key],1e-9)
                      for key in after),
              "OLD_READONLY_RECALL_METRIC")
        qualified={
            "better_than_matched_new":mean["rehearsal"] <= mean["matched_new"]-.005,
            "better_than_best_conventional":mean["rehearsal"]<=best-.005,
            "better_than_mispaired":mean["rehearsal"]<=mean["mispaired"]-.01,
            "old_horizon_retention":after["rehearsal"]<=before+.03,
            "old_horizon_better_than_matched":after["rehearsal"]<=
                                                after["matched_new"]-.005,
            "native_historical_retention":
                r["historic_readonly_native_after"] <=
                r["historic_readonly_native_before"]+.03,
        }
        check(r["conditions"]==qualified and
              r["development_go"]==all(qualified.values()),
              "FROZEN_QUALIFIER_RECOMPUTED")
        verdict.append(all(qualified.values()))
        results.append({"old_seed":old_seed,"seed":seed,
                        "late":mean,"historic":after,
                        "prior_historic":before,"conditions":qualified,
                        "development_go":all(qualified.values()),
                        "updated_native_sha256":r["updated_model_sha256"]})
    check(report["development_go"]==all(verdict) and
          report["science_pass"] is False and
          report["historical_probes_are_already_consumed"] is True and
          report["new_source_is_synthetic_development"] is True,
          "OVERALL_SCIENCE_FENCE")
    return {"schema":"yggdrasil.jepa2-05.independent-original-audit.v1",
            "source_sha":SOURCE_BLOB,"replicas":results,
            "engineering_audit":True,"development_go":all(verdict),
            "science_pass":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("artifact",type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    audited=audit(args.artifact)
    if args.output:
        args.output.write_bytes(canonical(audited))
    print("YGG_JEPA2_05_INDEPENDENT_SOURCE_AUDIT_PASS",
          "DEVELOPMENT_"+("GO" if audited["development_go"] else "NO_GO"),
          "SCIENCE_NOT_PASS",flush=True)

if __name__=="__main__":
    main()

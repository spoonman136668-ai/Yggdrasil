"""Independently reconstruct CKAD24 controls, receipts and native state bytes.

This module imports source-side fixtures and earlier independent reference
implementations, never the native learner or the training campaign.
"""
import argparse
import copy
from fractions import Fraction
from hashlib import sha256
import importlib.util
from itertools import product
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PREVIOUS = HERE.parent / "CKAD-23"
SOURCE = HERE.parent / "CKAD-20" / "synthetic_world.py"
sys.path.insert(0, str(SOURCE.parent))
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
spec = importlib.util.spec_from_file_location("ckad24_independent_previous", PREVIOUS / "independent_audit.py")
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
canonical, sha, ratio = previous.canonical, previous.sha, previous.ratio
Monitor, Mixture = previous.Monitor, previous.Mixture
reference = previous.reference
make_episode, public_views, rollout = previous.make_episode, previous.public_views, previous.rollout
BITS = (0, 1)
ACQUISITION = ("coverage_active", "original_active", "uniform_random", "coverage_random")
ARMS = (*ACQUISITION, "pooled_replay", "trailing_mle", "exact_mixture", "frozen_ckad23")


def require(condition, label):
    if not condition:
        raise RuntimeError("CKAD24_INDEPENDENT_" + label)


def stable(value):
    """Remove only declared provenance and measured-resource fields."""
    if type(value) is dict:
        return {key: stable(item) for key, item in value.items()
                if key not in ("source_candidate_sha", "stable_sha256", "resource_accounting")
                and not key.endswith(("_seconds", "_rss_bytes"))}
    if type(value) is list:
        return [stable(item) for item in value]
    return value


def verify_training_source(candidate):
    """Verify frozen training bytes when immutable Git objects are available."""
    require(type(candidate) is str and re.fullmatch(r"[0-9a-f]{40}",candidate), "SOURCE_COMMIT_FORMAT")
    if not (ROOT / ".git").exists():
        require(not os.environ.get("GITHUB_ACTIONS"), "CI_GIT_CUSTODY_REQUIRED")
        return False
    paths = [path.relative_to(ROOT).as_posix() for path in sorted((ROOT / "yggdrasil").glob("*.py"))]
    paths += ["research/contrib/chatgpt/CKAD-24/campaign.py",
              "research/contrib/chatgpt/CKAD-24/prereg.json",
              "research/contrib/chatgpt/CKAD-20/synthetic_world.py"]
    paths += [f"research/contrib/chatgpt/CKAD-{era}/{name}.py"
              for era,names in ((19,("independent_audit",)),
                                (20,("campaign","independent_audit")),
                                (21,("campaign","independent_audit")),
                                (22,("campaign","independent_audit")),
                                (23,("independent_audit",))) for name in names]
    for relative in paths:
        try:
            frozen = subprocess.check_output(["git","show",f"{candidate}:{relative}"],cwd=ROOT)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError("CKAD24_INDEPENDENT_SOURCE_GIT_OBJECT") from exc
        require(frozen == (ROOT / relative).read_bytes(), "FROZEN_TRAINING_BYTES_"+relative)
    return True


def random_actions(cohort, kind, seed, index):
    data = sha256(f"ckad24/actions-v1/{cohort}/{kind}/{seed}/{index}".encode("ascii")).digest()
    return data[0] & 1, data[1] & 1


def learned_projection(events):
    """The fixed public-view projection uses only the first eight witnesses."""
    if len(events) < 8:
        return None
    mismatch = [sum(event[1][0][bit] != event[1][1][bit] for event in events[:8])
                for bit in BITS]
    return None if mismatch[0] == mismatch[1] else mismatch.index(min(mismatch))


def coverage_counts(events, projection, view, first=None, state=None):
    require((first is None) == (state is None), "COVERAGE_HISTORY")
    context = None if projection is None else view[projection]
    counts = [0, 0]
    # Select the total-row window BEFORE filtering by public context/history.
    for _, views, x1, s2, x2, _ in events[-32:]:
        recorded = (None if projection is None or views[0][projection] != views[1][projection]
                    else views[0][projection])
        if recorded != context:
            continue
        if first is None:
            counts[x1] += 1
        elif (x1, s2) == (first, state):
            counts[x2] += 1
    return counts


def coverage_action(monitor, projection, view, first=None, state=None, *, tie=None):
    counts = coverage_counts(monitor.events, projection, view, first, state)
    if counts[0] == counts[1]:
        return monitor.mixture.explore(view, first, state) if tie is None else tie
    return int(counts[1] < counts[0])


def restore_monitor(events):
    require(len(events) >= 448, "MONITOR_INHERITED_PREFIX")
    monitor = Monitor(events[:448])
    for event in events[448:]:
        monitor.add(event)
    return monitor


def acquire(source_pin, fixture, seed, index, arm, monitor, projection):
    views = public_views(fixture)
    view = views[0]
    if arm == "uniform_random":
        first, second = random_actions("ckad24-stream", "probe-random", seed, index)
        row = rollout(fixture, lambda _: first, lambda *_: second)
    elif index % 4 == 3:
        plan = monitor.mixture.plan(view)
        row = rollout(fixture, lambda _: plan["first_action"],
                      lambda _, first, state: plan["second_actions"][first][state])
    elif arm == "original_active":
        row = rollout(fixture, lambda _: monitor.mixture.explore(view),
                      lambda _, first, state: monitor.mixture.explore(view, first, state))
    else:
        ties = (None, None) if arm == "coverage_active" else random_actions(
            "ckad24-stream", "probe-coverage-random", seed, index)
        row = rollout(fixture,
            lambda _: coverage_action(monitor, projection, view, tie=ties[0]),
            lambda _, first, state: coverage_action(monitor, projection, view, first, state, tie=ties[1]))
    identifier = sha(canonical(["ckad24", source_pin, "ckad24-stream", seed, index, arm]))
    return [identifier, [list(v) for v in views], *[row[k] for k in ("x1", "s2", "x2", "y")]]


def evaluate(forecast, seed, count, world, held_count):
    cohort = f"ckad24-held-{count}"
    views = list(product(BITS, repeat=2))
    plans = {view: previous.prior.prior.plan(forecast, view) for view in views}
    transitions = {(view, action): forecast(view, action) for view in views for action in BITS}
    terminals = {(view, *history): forecast(view, *history) for view in views
                 for history in product(BITS, repeat=3)}
    reward = disagreements = distinct = 0
    losses = [Fraction(), Fraction()]
    for index in range(held_count):
        fixture = make_episode(cohort=cohort, seed=seed, index=index, **world)
        view, alternate = public_views(fixture)
        distinct += view != alternate
        plan = plans[view]
        reward += rollout(fixture, lambda _: plan["first_action"],
                          lambda _, first, state: plan["second_actions"][first][state])["y"]
        first, second = random_actions(cohort, "held-matched", seed, index)
        row = rollout(fixture, lambda _: first, lambda *_: second)
        for target, (table, history, outcome) in enumerate((
                (transitions, (first,), row["s2"]),
                (terminals, (first, row["s2"], second), row["y"]))):
            probability = table[(view, *history)]
            losses[target] += (probability-outcome)**2
            disagreements += probability != table[(alternate, *history)]
    return {"episodes": held_count, "reward_sum": reward,
            "transition_brier": ratio(losses[0]/held_count),
            "terminal_brier": ratio(losses[1]/held_count),
            "pooled_brier": ratio(sum(losses)/(2*held_count)),
            "view_disagreements": disagreements, "view_comparisons": 2*held_count,
            "distinct_view_episodes": distinct}


def action_coverage(events, projection):
    first, histories = [0, 0], [0]*16
    for _, views, x1, state, x2, _ in events:
        require(projection is not None and views[0][projection] == views[1][projection],
                "COVERAGE_DIAGNOSTIC_CONTEXT")
        first[x1] += 1
        histories[8*views[0][projection]+4*x1+2*state+x2] += 1
    return {"first_action_counts": first, "terminal_history_action_counts": histories}


def detection(monitor):
    alarms = [entry["evidence_count"]-640 for entry in monitor.detections if entry["evidence_count"]>640]
    return {"alarm_steps":alarms,
            "inherited_detection_count":sum(entry["evidence_count"]<=640 for entry in monitor.detections),
            "false_alarm_steps":[n for n in alarms if not any(change<n<=change+16 for change in (48,96,144))],
            "boundaries":[{"change":change,
                "first_alarm":next((n for n in alarms if change<n<=change+16),None),
                "delay":next((n-change for n in alarms if change<n<=change+16),None)}
                for change in (48,96,144)]}


def held_mean(seeds, arm, counts=(64, 112, 160), field="reward_sum"):
    rows = [row["evaluation"][arm] for case in seeds for row in case["stream"]
            if row["count"] in counts]
    denominator = sum(row["episodes"] for row in rows)
    numerator = (sum(row[field] for row in rows) if field == "reward_sum" else
                 sum(Fraction(*row[field])*row["episodes"] for row in rows))
    return Fraction(numerator, denominator)


def development(seeds):
    active, original, uniform, balanced, mle = (
        held_mean(seeds, arm) for arm in (*ACQUISITION[:2], "uniform_random", "coverage_random", "trailing_mle"))
    active_brier = held_mean(seeds, "coverage_active", field="pooled_brier")
    original_brier = held_mean(seeds, "original_active", field="pooled_brier")
    returning = held_mean(seeds, "coverage_active", (192,))
    original_returning = held_mean(seeds, "original_active", (192,))
    per_seed = {str(case["seed"]): held_mean([case], "coverage_active") - held_mean([case], "original_active")
                for case in seeds}
    gates = {
        "held_gain_vs_original": active-original >= Fraction(3, 100),
        "held_vs_uniform_random": active >= uniform,
        "held_vs_coverage_random": active >= balanced,
        "held_vs_trailing_mle": active >= mle,
        "held_brier_vs_original": active_brier <= original_brier,
        "per_seed_no_reward_loss": all(value >= 0 for value in per_seed.values()),
        "final_returning_invariant": returning >= Fraction(4, 5),
        "final_retention_vs_original": returning >= original_returning-Fraction(1, 20),
    }
    metrics = {
        "held_reward": {arm:ratio(held_mean(seeds,arm)) for arm in ARMS},
        "held_pooled_brier": {arm:ratio(held_mean(seeds,arm,field="pooled_brier")) for arm in ARMS},
        "gain_vs_original": ratio(active-original),
        "per_seed_reward_delta": {seed:ratio(value) for seed,value in per_seed.items()},
        "final_reward": {arm:ratio(held_mean(seeds,arm,(192,))) for arm in ARMS},
    }
    return gates, metrics


def verify_gates(result):
    gates, metrics = development(result["seeds"])
    require(result["development_gates"] == gates and result["development_metrics"] == metrics,
            "FROZEN_METRICS_GATES")
    passed = all(gates.values())
    require(result["development_pass"] is passed and result["classification"] ==
            ("DEVELOPMENT_GO" if passed else "DEVELOPMENT_NO_GO"), "CLASSIFICATION")


def audit(root=HERE):
    start = time.monotonic()
    require(not any(name == "yggdrasil" or name.startswith("yggdrasil.") for name in sys.modules),
            "NATIVE_IMPORT_FENCE")
    protocol = json.loads((HERE / "prereg.json").read_bytes())
    result = json.loads((root / "campaign-result.json").read_bytes())
    source = sha(SOURCE.read_bytes())
    require(source == protocol["source_sha256"] == result["source_sha256"], "SOURCE_PIN")
    require(result["schema"] == "yggdrasil.ckad24.coverage-continuation-development.result.v1"
            and result["stable_sha256"] == sha(canonical(stable(result))), "RESULT_HASH")
    source_custody = verify_training_source(result["source_candidate_sha"])
    require(result["scientific_pass"] is False and result["accepted_native"] is False
            and result["deployment"] == "NONE", "AUTHORITY")
    require([row["seed"] for row in result["seeds"]] == protocol["seeds"], "SEEDS")
    budget = protocol["budgets"]
    require(budget["checkpoints"] == list(range(0,193,16)) and budget["coverage_total_rows"] == 32
            and budget["stream_episodes_per_seed_per_acquisition_arm"] == 192
            and budget["phase_episodes"] == 48 and budget["acquisition_arms"] == 4, "SCHEDULE")
    require(0 <= result["whole_wall_seconds"] <= budget["max_wall_seconds"], "WALL_BUDGET")
    parity = {"forecasts":9216, "decisions":7680, "coverage_choices":3840, "mismatches":0}
    identities, rollouts, diagnostics = set(), 0, []
    for case in result["seeds"]:
        seed = case["seed"]
        source_seed = seed+protocol["source_seed_offset"]
        require(case["source_seed"] == source_seed, "SOURCE_SEED")
        parent_raw = (PREVIOUS / f"seed-{seed}-stream-native.json").read_bytes()
        require(sha(parent_raw) == case["parent_checkpoint_sha256"] == protocol["parent_pins"][str(seed)], "PARENT_PIN")
        parent = json.loads(parent_raw)
        inherited = json.loads(parent["experience_ascii"])
        prefix = inherited["episodes"]
        require(inherited["stream_start"] == 448 and len(prefix) == 640
                and canonical(parent) == parent_raw, "PARENT_SCHEMA")
        projection = learned_projection(prefix)
        replay = previous.prior.prior.replay(prefix, True)
        require(replay.projection == projection, "PUBLIC_PROJECTION")
        monitors = {arm:restore_monitor(prefix) for arm in ACQUISITION}
        active = monitors["coverage_active"]
        require(previous.stream_checkpoint(replay, parent, active) == parent_raw, "PARENT_EXACT_REPLAY")
        frozen = copy.deepcopy(active.mixture)
        name = f"seed-{seed}-coverage-native.json"
        require(case["final_checkpoint_name"] == name, "STATE_NAME")
        raw = (root / name).read_bytes()
        require(sha(raw) == case["final_checkpoint_sha256"] and len(raw) == case["final_checkpoint_bytes"], "STATE_PIN")
        final = json.loads(raw)
        experience = json.loads(final["experience_ascii"])
        ledger = experience["episodes"]
        require({**final,"experience_ascii":parent["experience_ascii"]} == parent
                and ledger[:640] == prefix and len(ledger) == 832
                and len({event[0] for event in ledger}) == 832, "RETENTION")
        reports = case["stream"]
        require([row["count"] for row in reports] == budget["checkpoints"], "HELD_SCHEDULE")
        rewards = {arm:0 for arm in ACQUISITION}
        midstream = None
        for count in range(193):
            if count == 81:
                checkpoint = previous.stream_checkpoint(replay,parent,active)
                require(midstream is not None, "MIDSTREAM_PARENT_RECEIPT")
                midstream.update({"method":"fresh_process_actual_receipt_update_then_continue",
                    "continued_count":81,"continued_event_id":active.events[-1][0],
                    "continued_sha256":sha(checkpoint),
                    "continued_readout_sha256":previous.prior.prior.readout_pin(active.mixture)})
            if count in budget["checkpoints"]:
                row = reports[budget["checkpoints"].index(count)]
                world = protocol["phases"][0 if count == 0 else (count-1)//48]
                mle = reference.FullHistoryControl(replay.events, projection, mle=True)
                experts = {arm:monitors[arm].mixture.forecast for arm in ACQUISITION}
                experts.update(pooled_replay=replay.predict, trailing_mle=mle.predict,
                               exact_mixture=active.mixture.forecast, frozen_ckad23=frozen.forecast)
                require(set(row["evaluation"]) == set(ARMS), "HELD_ARMS")
                for arm, forecast in experts.items():
                    require(row["evaluation"][arm] == evaluate(forecast, source_seed, count, world,
                            budget["held_episodes_per_checkpoint"]), f"HELD_{seed}_{count}_{arm}")
                    rollouts += budget["held_episodes_per_checkpoint"]
                require(row["monitors"] == {arm:monitor.info() for arm,monitor in monitors.items()}, "MONITOR_TRACE")
                require(row["context_starts"] == {arm:monitor.mixture.start for arm,monitor in monitors.items()}, "CONTEXT_TRACE")
                require(row["acquisition_reward"] == rewards, "ACQUISITION_REWARD_TRACE")
                coverage = {arm:action_coverage(monitor.events[640:],projection) for arm,monitor in monitors.items()}
                require(row["action_coverage"] == coverage, "ACTION_COVERAGE_TRACE")
                checkpoint = previous.stream_checkpoint(replay,parent,active)
                require(row["checkpoint_sha256"] == sha(checkpoint), f"CHECKPOINT_REPLAY_{seed}_{count}")
                if count == 80:
                    midstream = {"count":80, "sha256":sha(checkpoint),
                                 "readout_sha256":previous.prior.prior.readout_pin(active.mixture)}
            if count == 192:
                break
            fixture = make_episode(cohort="ckad24-stream", seed=source_seed, index=count,
                                   **protocol["phases"][count//48])
            for arm, monitor in monitors.items():
                event = acquire(source,fixture,source_seed,count,arm,monitor,projection)
                if arm == "coverage_active":
                    require(ledger[640+count] == event, f"SELECTED_RECEIPT_{seed}_{count}")
                    replay.add(event)
                require(event[0] not in identities, "ACQUISITION_IDENTITY")
                identities.add(event[0]); monitor.add(event); rewards[arm] += event[-1]
        require(raw == previous.stream_checkpoint(replay,parent,active), "FULL_EXACT_STATE_REPLAY")
        require(case["monitors"] == {arm:monitor.info() for arm,monitor in monitors.items()}, "FINAL_MONITORS")
        require(case["acquisition_reward"] == rewards and case["action_coverage"] ==
                {arm:action_coverage(monitor.events[640:],projection) for arm,monitor in monitors.items()}, "FINAL_DIAGNOSTICS")
        require(case["change_detection"] == {arm:detection(monitor) for arm,monitor in monitors.items()},
                "CHANGE_DETECTION_DIAGNOSTICS")
        readout = previous.prior.prior.readout_pin(active.mixture)
        require(case["midstream_restore"] == midstream, "MIDSTREAM_CONTINUATION_RECEIPT")
        require(case["cold"] == {"sha256":sha(raw), "readout_sha256":readout}
                and case["final_context_sha256"] == readout, "COLD_RECEIPT")
        require(case["parity"] == parity, "PARITY_COUNTS")
        children = case["resource_accounting"]["cold_children"]
        require([child["count"] for child in children] == [81,192]
                and all(child["cpu_seconds"] >= 0 and child["wall_seconds"] >= 0
                        and child["peak_rss_bytes"] > 0 for child in children), "CHILD_RESOURCE_SCOPE")
        detections = {}
        for arm, monitor in monitors.items():
            alarms = [event["evidence_count"]-640 for event in monitor.detections if event["evidence_count"]>640]
            detections[arm] = {"alarms":alarms,
                "boundaries":[{"change":change,
                    "delay":next((n-change for n in alarms if change < n <= change+16),None)}
                    for change in (48,96,144)],
                "false_alarms":[n for n in alarms if not any(change<n<=change+16 for change in (48,96,144))]}
        diagnostics.append({"seed":seed,"acquisition_reward":rewards,"detection":detections})
    require(len(identities) == 2304 and rollouts == 29952, "REPLAY_SCOPE")
    require(result["scope"] == {"acquisition_episodes":2304,"synthetic_actions":4608,
            "held_source_episodes":3744,"held_policy_rollouts":29952,
            "held_updates":0,"original_source_actions":0,"protected_first_use":0}, "RECORDED_SCOPE")
    require(result["parity"] == {key:value*3 for key,value in parity.items()}, "TOTAL_PARITY")
    resources = result["resource_accounting"]
    require(result["parent_cpu_seconds"] >= 0 and result["parent_peak_rss_bytes"] > 0
            and resources["parent_cpu_seconds"] == result["parent_cpu_seconds"]
            and resources["parent_peak_rss_bytes"] == result["parent_peak_rss_bytes"]
            and resources["whole_process_peak_rss_bytes"] is None, "PARENT_RESOURCE_SCOPE")
    child_cpu = sum(child["cpu_seconds"] for case in result["seeds"]
                    for child in case["resource_accounting"]["cold_children"])
    require(abs(resources["measured_child_cpu_seconds"]-child_cpu) < 1e-7
            and abs(resources["parent_plus_measured_child_cpu_seconds"]-
                    result["parent_cpu_seconds"]-child_cpu) < 1e-7, "CPU_ACCOUNTING")
    verify_gates(result)
    held_summary = {arm:{"reward":ratio(held_mean(result["seeds"],arm)),
        "pooled_brier_decimal":format(float(held_mean(result["seeds"],arm,field="pooled_brier")),".12f")}
        for arm in ARMS}
    return {"independent_all_arm_audit":"PASS","native_imports":0,"new_primary_observations":0,
            "git_training_source_custody_checked":source_custody,
            "verified_seeds":3,"verified_checkpoints":39,"verified_training_episodes":len(identities),
            "verified_held_policy_rollouts":rollouts,"full_state_bytes_replayed":True,
            "stable_sha256":result["stable_sha256"],"held_summary":held_summary,
            "diagnostics":diagnostics,"wall_seconds":time.monotonic()-start}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path, default=HERE)
    arguments = parser.parse_args()
    print(json.dumps(audit(arguments.directory),sort_keys=True))

"""Frozen cumulative intervention-coverage ablation in one native learner."""
import argparse
import copy
from fractions import Fraction
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

PROCESS_STARTED = time.monotonic()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PARENT = HERE.parent / "CKAD-23"
SOURCE = HERE.parent / "CKAD-20" / "synthetic_world.py"
sys.path.insert(0, str(ROOT))
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

PREVIOUS = load("ckad24_existing_campaign_helpers", HERE.parent / "CKAD-22" / "campaign.py")
REFERENCE = load("ckad24_existing_exact_monitor", PARENT / "independent_audit.py")
BASE, LEGACY = PREVIOUS.BASE, PREVIOUS.LEGACY
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE, NativeCumulativeLearner

ACQUISITION_ARMS = ("coverage_active", "original_active", "uniform_random", "coverage_random")
ARMS = (*ACQUISITION_ARMS, "pooled_replay", "trailing_mle", "exact_mixture", "frozen_ckad23")
STREAM = "ckad24-stream"

def check(condition, label):
    if not condition:
        raise RuntimeError("CKAD24_" + label)

def ratio(value):
    return [value.numerator, value.denominator]

def _semantic(value):
    if isinstance(value, dict):
        return {key: _semantic(item) for key, item in value.items()
                if key not in {"source_candidate_sha", "stable_sha256", "resource_accounting"}
                and not key.endswith("_seconds") and not key.endswith("_rss_bytes")}
    if isinstance(value, list):
        return [_semantic(item) for item in value]
    return value

def stable(result):
    return canonical(_semantic(result))

def peak_rss():
    if sys.platform != "win32":
        import resource
        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return value if sys.platform == "darwin" else value * 1024
    import ctypes
    from ctypes import wintypes
    class MemoryCounters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                    *[(name, ctypes.c_size_t) for name in
                      ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                       "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
                       "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]]
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(MemoryCounters), wintypes.DWORD]
    counters = MemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    check(psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb),
          "WINDOWS_PROCESS_PEAK")
    return counters.PeakWorkingSetSize

def random_actions(cohort, kind, seed, index):
    key = f"ckad24/actions-v1/{cohort}/{kind}/{seed}/{index}".encode("ascii")
    raw = bytes.fromhex(digest(key))
    return raw[0] & 1, raw[1] & 1

def event_id(seed, index, arm):
    return digest(canonical(["ckad24", EXPERIENCE_SOURCE, STREAM, seed, index, arm]))

def restore_monitor(events, stream_start):
    monitor = REFERENCE.Monitor(events[:stream_start])
    for event in events[stream_start:]:
        monitor.add(event)
    return monitor

def coverage_choice(monitor, projection, view, first=None, state=None, *, tie=None):
    counts = [0, 0]
    context = view[projection]
    for _, views, x1, s2, x2, _ in monitor.events[-32:]:
        if views[0][projection] != views[1][projection] or views[0][projection] != context:
            continue
        if first is None:
            counts[x1] += 1
        elif (x1, s2) == (first, state):
            counts[x2] += 1
    if counts[0] != counts[1]:
        return int(counts[1] < counts[0])
    return monitor.mixture.explore(view, first, state) if tie is None else tie

def action_coverage(events, projection):
    first, terminal = [0, 0], [0] * 16
    for _, views, x1, s2, x2, _ in events[640:]:
        context = views[0][projection]
        check(context == views[1][projection] and context in BASE.BITS, "PUBLIC_PROJECTED_CONTEXT")
        first[x1] += 1
        terminal[8 * context + 4 * x1 + 2 * s2 + x2] += 1
    return {"first_action_counts": first, "terminal_history_action_counts": terminal}

def assert_monitor(model, monitor):
    info = model.info()["episode_experience"]
    check(info["stream"] == monitor.info(), "MONITOR_TRACE")
    check(info["context"] == monitor.mixture.info(), "CONTEXT_TRACE")

def exact_parity(model, monitor, projection, counts):
    BASE.require_parity(model, monitor.mixture, counts)
    for view in BASE.VIEWS:
        for first, state in ((None, None), *((x1, s2) for x1 in BASE.BITS for s2 in BASE.BITS)):
            check(model.experience_coverage_explore(view, first, state) ==
                  coverage_choice(monitor, projection, view, first, state), "COVERAGE_CHOICE_PARITY")
            counts["coverage_choices"] += 1

def estimates(models, monitors, parent):
    active = models["coverage_active"]
    mle = LEGACY.ConventionalControl(BASE.receipts_from_events(monitors["coverage_active"].events), mle=True)
    methods = {arm: (model.experience_context_plan, model.experience_context_forecast)
               for arm, model in models.items()}
    methods.update({"pooled_replay": (active.experience_plan, active.experience_forecast),
                    "trailing_mle": (mle.plan, mle.forecast),
                    "exact_mixture": (monitors["coverage_active"].mixture.plan,
                                      monitors["coverage_active"].mixture.forecast),
                    "frozen_ckad23": (parent.experience_context_plan, parent.experience_context_forecast)})
    return {arm: ({v: plan(v) for v in BASE.VIEWS},
                  {(v, first): forecast(v, first) for v in BASE.VIEWS for first in BASE.BITS},
                  {(v, *history): forecast(v, *history) for v in BASE.VIEWS for history in BASE.TERMINAL_HISTORIES})
            for arm, (plan, forecast) in methods.items()}

def evaluate(models, monitors, parent, source_seed, count, world, held_count):
    before = {arm: digest(model.checkpoint()) for arm, model in models.items()}
    before_parent = digest(parent.checkpoint())
    before_monitors = canonical({arm: monitor.info() for arm, monitor in monitors.items()})
    tables = estimates(models, monitors, parent)
    sums = {arm: [0, Fraction(), Fraction(), 0] for arm in ARMS}
    distinct = 0
    cohort = f"ckad24-held-{count}"
    for index in range(held_count):
        fixture = BASE.make_episode(cohort=cohort, seed=source_seed, index=index, **world)
        view, other = BASE.public_views(fixture)
        distinct += view != other
        observed = LEGACY.fixed_rollout(fixture, random_actions(cohort, "held-matched", source_seed, index))
        first, state, second, reward = (observed[key] for key in ("x1", "s2", "x2", "y"))
        for arm, (plans, transition, terminal) in tables.items():
            scores = sums[arm]
            scores[0] += LEGACY.planned_rollout(fixture, plans[view])["y"]
            p, q = transition[view, first], terminal[view, first, state, second]
            scores[1] += (p-state) ** 2
            scores[2] += (q-reward) ** 2
            scores[3] += int(p != transition[other, first]) + int(q != terminal[other, first, state, second])
    result = {arm: {"episodes": held_count, "reward_sum": row[0],
                    "transition_brier": ratio(row[1]/held_count),
                    "terminal_brier": ratio(row[2]/held_count),
                    "pooled_brier": ratio((row[1]+row[2])/(2*held_count)),
                    "view_disagreements": row[3], "view_comparisons": 2*held_count,
                    "distinct_view_episodes": distinct} for arm, row in sums.items()}
    check(result["coverage_active"] == result["exact_mixture"], "HELD_EXACT_REFERENCE")
    check(before == {arm: digest(model.checkpoint()) for arm, model in models.items()}
          and before_parent == digest(parent.checkpoint())
          and before_monitors == canonical({arm: m.info() for arm, m in monitors.items()}), "HELD_UPDATES")
    return result

def cold_child(arguments):
    path, pin, readout = arguments
    raw = Path(path).read_bytes()
    model = NativeCumulativeLearner.restore(raw, pin)
    check(model.checkpoint() == raw and BASE.context_readout_pin(model) == readout, "COLD_RESTORE")
    print(json.dumps({"sha256": pin, "readout_sha256": readout,
                      "episode_count": model.info()["episode_experience"]["count"],
                      "resource_accounting": {"cpu_seconds": time.process_time(),
                          "wall_seconds": time.monotonic()-PROCESS_STARTED, "peak_rss_bytes": peak_rss()}}, sort_keys=True))

def cold_proof(path, pin, readout, count):
    report = json.loads(subprocess.check_output([sys.executable, "-B", str(HERE / "campaign.py"),
                        "--cold-check", str(path), pin, readout], cwd=ROOT, timeout=180, text=True))
    check(report["sha256"] == pin and report["readout_sha256"] == readout
          and report["episode_count"] == count, "COLD_REPORT")
    return {"sha256": pin, "readout_sha256": readout}, report["resource_accounting"]

def cold_update_child(arguments):
    path, pin, readout, packet_path, output_path = arguments
    raw = Path(path).read_bytes()
    model = NativeCumulativeLearner.restore(raw, pin)
    check(model.checkpoint() == raw and BASE.context_readout_pin(model) == readout, "COLD_UPDATE_PARENT")
    packet = json.loads(Path(packet_path).read_bytes())
    check(set(packet) == {"identifier", "views", "row"}, "COLD_PUBLIC_PACKET_KEYS")
    views = tuple(tuple(view) for view in packet["views"])
    updated = BASE.admit(model, packet["identifier"], views, packet["row"])
    payload = updated.checkpoint()
    Path(output_path).write_bytes(payload)
    print(json.dumps({"parent_sha256": pin, "parent_readout_sha256": readout,
        "event_id": packet["identifier"], "sha256": digest(payload),
        "readout_sha256": BASE.context_readout_pin(updated),
        "episode_count": updated.info()["episode_experience"]["count"],
        "resource_accounting": {"cpu_seconds": time.process_time(),
            "wall_seconds": time.monotonic()-PROCESS_STARTED, "peak_rss_bytes": peak_rss()}}, sort_keys=True))

def cold_update_proof(raw, pin, readout, identifier, views, row, expected):
    with tempfile.TemporaryDirectory(prefix="ckad24-cold-update-") as directory:
        temporary = Path(directory)
        checkpoint, packet, output = (temporary/name for name in ("parent.json", "packet.json", "continued.json"))
        checkpoint.write_bytes(raw)
        packet.write_bytes(canonical({"identifier": identifier, "views": views, "row": row}))
        report = json.loads(subprocess.check_output([sys.executable, "-B", str(HERE / "campaign.py"),
            "--cold-update", str(checkpoint), pin, readout, str(packet), str(output)],
            cwd=ROOT, timeout=180, text=True))
        payload = output.read_bytes()
    check(payload == expected and report["parent_sha256"] == pin
          and report["parent_readout_sha256"] == readout and report["event_id"] == identifier
          and report["sha256"] == digest(payload) and report["episode_count"] == 721,
          "ACTUAL_COLD_RECEIPT_CONTINUATION")
    restored = NativeCumulativeLearner.restore(payload, report["sha256"])
    check(restored.checkpoint() == payload and BASE.context_readout_pin(restored) == report["readout_sha256"],
          "ACTUAL_COLD_CONTINUED_READOUT")
    return restored, report

def detection(monitor):
    alarms = [entry["evidence_count"]-640 for entry in monitor.detections if entry["evidence_count"] > 640]
    return {"alarm_steps": alarms,
            "inherited_detection_count": sum(entry["evidence_count"] <= 640 for entry in monitor.detections),
            "false_alarm_steps": [step for step in alarms if not any(c < step <= c+16 for c in (48,96,144))],
            "boundaries": [{"change": c, "first_alarm": next((a for a in alarms if c < a <= c+16), None),
                            "delay": next((a-c for a in alarms if c < a <= c+16), None)} for c in (48,96,144)]}

def run_seed(seed, protocol, output):
    raw = (PARENT / f"seed-{seed}-stream-native.json").read_bytes()
    pin = protocol["parent_pins"][str(seed)]
    parent = NativeCumulativeLearner.restore(raw, pin)
    check(parent.checkpoint() == raw, "EXACT_QUALIFIED_PARENT")
    legacy, inherited = BASE.legacy_and_experience(raw)
    prefix = inherited["episodes"]
    check(len(prefix) == 640 and inherited["stream_start"] == 448, "PARENT_STREAM_CONTINUATION")
    projection = parent.info()["episode_experience"]["projection"]
    check(projection in BASE.BITS, "QUALIFIED_PARENT_PROJECTION")
    initial_monitor = restore_monitor(prefix, inherited["stream_start"])
    assert_monitor(parent, initial_monitor)
    models = {arm: parent for arm in ACQUISITION_ARMS}
    monitors = {arm: copy.deepcopy(initial_monitor) for arm in ACQUISITION_ARMS}
    rewards = dict.fromkeys(ACQUISITION_ARMS, 0)
    parity = {"forecasts": 0, "decisions": 0, "coverage_choices": 0, "mismatches": 0}
    snapshots, child_costs = [], []
    source_seed = seed + protocol["source_seed_offset"]
    budget = protocol["budgets"]
    midstream = midstream_raw = None
    for count in range(193):
        if count in budget["checkpoints"]:
            world = protocol["phases"][0 if count == 0 else (count-1)//48]
            scores = evaluate(models, monitors, parent, source_seed, count, world,
                              budget["held_episodes_per_checkpoint"])
            for arm, model in models.items():
                header, episode = BASE.legacy_and_experience(model.checkpoint())
                check(header == legacy and episode["episodes"][:640] == prefix
                      and episode["episodes"] == monitors[arm].events
                      and len(episode["episodes"]) == 640+count
                      and episode["stream_start"] == 448, "RETAINED_EVIDENCE")
                assert_monitor(model, monitors[arm])
            state = models["coverage_active"].checkpoint()
            snapshots.append({"count": count, "evaluation": scores, "checkpoint_sha256": digest(state),
                "monitors": {arm: monitor.info() for arm, monitor in monitors.items()},
                "context_starts": {arm: monitor.mixture.start for arm, monitor in monitors.items()},
                "acquisition_reward": rewards.copy(),
                "action_coverage": {arm: action_coverage(m.events, projection) for arm, m in monitors.items()}})
            if count == 80:
                state_pin = digest(state)
                readout = BASE.context_readout_pin(models["coverage_active"])
                models["coverage_active"] = NativeCumulativeLearner.restore(state, state_pin)
                check(models["coverage_active"].checkpoint() == state, "MIDSTREAM_RESTORE")
                midstream = {"count": 80, "sha256": state_pin, "readout_sha256": readout}
                midstream_raw = state
        if count == 192:
            break
        exact_parity(models["coverage_active"], monitors["coverage_active"], projection, parity)
        world = protocol["phases"][count//48]
        fixture = BASE.make_episode(cohort=STREAM, seed=source_seed, index=count, **world)
        views = BASE.public_views(fixture)
        view = views[0]
        for arm in ACQUISITION_ARMS:
            model, monitor = models[arm], monitors[arm]
            if arm == "uniform_random":
                row = LEGACY.fixed_rollout(fixture, random_actions(STREAM, "probe-random", source_seed, count))
            elif count % 4 == 3:
                row = LEGACY.planned_rollout(fixture, model.experience_context_plan(view))
            else:
                ties = random_actions(STREAM, "probe-coverage-random", source_seed, count)
                if arm == "coverage_active":
                    choose = model.experience_coverage_explore
                elif arm == "original_active":
                    choose = model.experience_context_explore
                else:
                    def choose(v, first=None, state=None):
                        return coverage_choice(monitor, projection, v, first, state,
                                               tie=ties[0 if first is None else 1])
                row = BASE.rollout(fixture, lambda _: choose(view),
                                   lambda _, first, state: choose(view, first, state))
            identifier = event_id(source_seed, count, arm)
            models[arm] = BASE.admit(model, identifier, views, row)
            if arm == "coverage_active" and count == 80:
                models[arm], cold_report = cold_update_proof(midstream_raw, midstream["sha256"],
                    midstream["readout_sha256"], identifier, views, row, models[arm].checkpoint())
                midstream.update({"method": "fresh_process_actual_receipt_update_then_continue",
                    "continued_count": 81, "continued_event_id": identifier,
                    "continued_sha256": cold_report["sha256"],
                    "continued_readout_sha256": cold_report["readout_sha256"]})
                child_costs.append({"count": 81, **cold_report["resource_accounting"]})
            monitor.add(BASE.retain_event(identifier, views, row))
            rewards[arm] += row["y"]
            assert_monitor(models[arm], monitor)
    active = models["coverage_active"].consolidate_experience()
    payload = active.checkpoint()
    name = f"seed-{seed}-coverage-native.json"
    destination = output / name
    destination.write_bytes(payload)
    readout = BASE.context_readout_pin(active)
    cold, cost = cold_proof(destination, digest(payload), readout, 832)
    child_costs.append({"count": 192, **cost})
    check(midstream is not None and len(monitors["coverage_active"].events) == 832, "CONTINUED_AFTER_RESTART")
    return {"seed": seed, "source_seed": source_seed, "parent_checkpoint_sha256": pin,
            "stream": snapshots, "parity": parity, "midstream_restore": midstream,
            "monitors": {arm: monitor.info() for arm, monitor in monitors.items()},
            "change_detection": {arm: detection(monitor) for arm, monitor in monitors.items()},
            "acquisition_reward": rewards,
            "action_coverage": {arm: action_coverage(m.events, projection) for arm, m in monitors.items()},
            "final_checkpoint_name": name, "final_checkpoint_sha256": digest(payload),
            "final_checkpoint_bytes": len(payload), "final_context_sha256": readout, "cold": cold,
            "resource_accounting": {"cold_children": child_costs}}

def development(seeds):
    def mean(arm, *, counts=(64,112,160), subset=None, metric="reward"):
        rows = [row["evaluation"][arm] for case in (seeds if subset is None else subset)
                for row in case["stream"] if row["count"] in counts]
        if metric == "reward":
            return Fraction(sum(row["reward_sum"] for row in rows), sum(row["episodes"] for row in rows))
        return sum((Fraction(*row["pooled_brier"]) for row in rows), Fraction())/len(rows)
    reward = {arm: mean(arm) for arm in ARMS}
    brier = {arm: mean(arm, metric="brier") for arm in ARMS}
    final = {arm: mean(arm, counts=(192,)) for arm in ARMS}
    deltas = {str(case["seed"]): mean("coverage_active", subset=[case])-mean("original_active", subset=[case])
              for case in seeds}
    active, original = reward["coverage_active"], reward["original_active"]
    gates = {"held_gain_vs_original": active-original >= Fraction(3,100),
             "held_vs_uniform_random": active >= reward["uniform_random"],
             "held_vs_coverage_random": active >= reward["coverage_random"],
             "held_vs_trailing_mle": active >= reward["trailing_mle"],
             "held_brier_vs_original": brier["coverage_active"] <= brier["original_active"],
             "per_seed_no_reward_loss": all(value >= 0 for value in deltas.values()),
             "final_returning_invariant": final["coverage_active"] >= Fraction(4,5),
             "final_retention_vs_original": final["coverage_active"] >= final["original_active"]-Fraction(1,20)}
    metrics = {"held_reward": {arm: ratio(value) for arm, value in reward.items()},
               "held_pooled_brier": {arm: ratio(value) for arm, value in brier.items()},
               "gain_vs_original": ratio(active-original),
               "per_seed_reward_delta": {seed: ratio(value) for seed, value in deltas.items()},
               "final_reward": {arm: ratio(value) for arm, value in final.items()}}
    return gates, metrics

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--verify-env", action="store_true")
    parser.add_argument("--cold-check", nargs=3)
    parser.add_argument("--cold-update", nargs=5)
    args = parser.parse_args()
    if args.cold_check:
        cold_child(args.cold_check)
        return
    if args.cold_update:
        cold_update_child(args.cold_update)
        return
    if args.output_directory is None:
        parser.error("--output-directory required")
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    protocol = json.loads((HERE / "prereg.json").read_bytes())
    check(digest(SOURCE.read_bytes()) == protocol["source_sha256"] == EXPERIENCE_SOURCE, "SOURCE_PIN")
    check(protocol["seeds"] == [101,202,303]
          and protocol["budgets"]["checkpoints"] == list(range(0,193,16))
          and protocol["budgets"]["acquisition_arms"] == len(ACQUISITION_ARMS), "FROZEN_SCOPE")
    seeds = [run_seed(seed, protocol, output) for seed in protocol["seeds"]]
    gates, metrics = development(seeds)
    passed = all(gates.values())
    cpu, peak = time.process_time(), peak_rss()
    child_costs = [child for case in seeds for child in case["resource_accounting"]["cold_children"]]
    result = {"schema": "yggdrasil.ckad24.coverage-continuation-development.result.v1",
              "classification": "DEVELOPMENT_GO" if passed else "DEVELOPMENT_NO_GO",
              "development_pass": passed, "development_gates": gates, "development_metrics": metrics,
              "source_candidate_sha": subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip(),
              "source_sha256": EXPERIENCE_SOURCE, "scientific_pass": False,
              "accepted_native": False, "deployment": "NONE", "seeds": seeds,
              "parity": {key: sum(case["parity"][key] for case in seeds)
                         for key in ("forecasts","decisions","coverage_choices","mismatches")},
              "scope": {"acquisition_episodes": 2304, "synthetic_actions": 4608,
                        "held_source_episodes": 3744, "held_policy_rollouts": 29952,
                        "held_updates": 0, "original_source_actions": 0, "protected_first_use": 0},
              "whole_wall_seconds": time.monotonic()-PROCESS_STARTED,
              "parent_cpu_seconds": cpu, "parent_peak_rss_bytes": peak,
              "resource_accounting": {"parent_cpu_seconds": cpu, "parent_peak_rss_bytes": peak,
                  "measured_child_cpu_seconds": sum(child["cpu_seconds"] for child in child_costs),
                  "parent_plus_measured_child_cpu_seconds": cpu+sum(child["cpu_seconds"] for child in child_costs),
                  "whole_process_peak_rss_bytes": None,
                  "scope_note": "Separate parent/child process peaks measured; aggregate process-tree peak and interpreter startup wall not separately measured. CI/setup/authoring/audit additional."}}
    check(result["whole_wall_seconds"] <= protocol["budgets"]["max_wall_seconds"], "WALL_BUDGET")
    result["stable_sha256"] = digest(stable(result))
    (output / "campaign-result.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="ascii")
    print(json.dumps({"classification": result["classification"], "stable_sha256": result["stable_sha256"]}, sort_keys=True))
    if args.verify_env:
        check(os.environ["CKAD24_EXPECTED_HASH"] == result["stable_sha256"], "CROSS_PLATFORM_RESULT")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="ascii") as stream:
            stream.write("stable="+result["stable_sha256"]+"\n")

if __name__ == "__main__":
    main()

"""Frozen matched-receipt native context refresh without new training actions."""
import argparse
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
PARENT = HERE.parent / "CKAD-24"
SOURCE = HERE.parent / "CKAD-20" / "synthetic_world.py"
sys.path.insert(0, str(ROOT))
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

PREVIOUS = load("ckad26_existing_campaign_helpers", HERE.parent / "CKAD-22" / "campaign.py")
REFERENCE = load("ckad26_existing_exact_monitor", HERE / "independent_audit.py")
BASE, LEGACY = PREVIOUS.BASE, PREVIOUS.LEGACY
QUALIFIED = load("ckad26_qualified24_helpers", PARENT / "campaign.py")
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE, NativeCumulativeLearner

RECEIPTS = HERE.parent / "CKAD-25"
NATIVE_ARMS = ("native_refresh", "native_product")
CONTROL_ARMS = ("exact_refresh", "refresh_no_alarm", "product_no_alarm", "prior_only")
ARMS = (*NATIVE_ARMS, *CONTROL_ARMS, "pooled_replay", "trailing_mle", "frozen_ckad24")


def check(condition, label):
    if not condition:
        raise RuntimeError("CKAD26_" + label)


def ratio(value):
    return [value.numerator, value.denominator]


stable, peak_rss = QUALIFIED.stable, QUALIFIED.peak_rss


def wall_budget(protocol):
    check(time.monotonic()-PROCESS_STARTED <= protocol["budgets"]["max_wall_seconds"], "WALL_BUDGET")


def random_actions(cohort, kind, seed, index):
    data = bytes.fromhex(digest(f"ckad26/actions-v1/{cohort}/{kind}/{seed}/{index}".encode("ascii")))
    return data[0] & 1, data[1] & 1


def assert_monitor(model, monitor):
    QUALIFIED.assert_monitor(model, monitor)
    if getattr(monitor, "refresh_start", None) is not None:
        check(model.info()["episode_experience"]["refresh"] ==
              {"refresh_start": monitor.refresh_start, "rate": [1, 32]}, "REFRESH_TRACE")


def estimates(models, monitors, parent):
    active = models["native_refresh"]
    mle = LEGACY.ConventionalControl(BASE.receipts_from_events(monitors["exact_refresh"].events), mle=True)
    methods = {arm: (model.experience_context_plan, model.experience_context_forecast)
               for arm, model in models.items()}
    methods.update({arm: (monitor.mixture.plan, monitor.mixture.forecast)
                    for arm, monitor in monitors.items() if arm in CONTROL_ARMS})
    methods.update({"pooled_replay": (active.experience_plan, active.experience_forecast),
                    "trailing_mle": (mle.plan, mle.forecast),
                    "frozen_ckad24": (parent.experience_context_plan, parent.experience_context_forecast)})
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
    cohort = f"ckad26-held-{count}"
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
    check(result["native_refresh"] == result["exact_refresh"], "HELD_EXACT_REFERENCE")
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
    with tempfile.TemporaryDirectory(prefix="ckad26-cold-update-") as directory:
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
          and report["sha256"] == digest(payload) and report["episode_count"] == 913,
          "ACTUAL_COLD_RECEIPT_CONTINUATION")
    restored = NativeCumulativeLearner.restore(payload, report["sha256"])
    check(restored.checkpoint() == payload and BASE.context_readout_pin(restored) == report["readout_sha256"],
          "ACTUAL_COLD_CONTINUED_READOUT")
    return restored, report

def detection(monitor):
    alarms = [entry["evidence_count"]-832 for entry in monitor.detections if entry["evidence_count"] > 832]
    return {"alarm_steps": alarms,
            "inherited_detection_count": sum(entry["evidence_count"] <= 832 for entry in monitor.detections),
            "false_alarm_steps": [step for step in alarms if not any(c < step <= c+16 for c in (48,80,144))],
            "boundaries": [{"change": c, "first_alarm": next((a for a in alarms if c < a <= c+16), None),
                            "delay": next((a-c for a in alarms if c < a <= c+16), None)} for c in (48,80,144)]}

def world_at(protocol, index):
    """Evaluator-side equation schedule; never passed into the learner."""
    check(type(index) is int and 0 <= index < 192, "SOURCE_INDEX")
    offset = 0
    for phase in protocol["phases"]:
        offset += phase["episodes"]
        if index < offset:
            return {"family":phase["family"], "regime":phase["regime"]}
    raise RuntimeError("CKAD26_SOURCE_PHASE_BUDGET")


def capacity_probe(model, seed):
    """Invalid unit admission at capacity, not a new observed consequence."""
    before = model.checkpoint()
    episode = json.loads(json.loads(before)["experience_ascii"])
    check(len(episode["episodes"]) == 1024, "CAPACITY_PROBE_COUNT")
    _, views, first, state, second, reward = episode["episodes"][-1]
    views = tuple(tuple(view) for view in views)
    projection = model.info()["episode_experience"]["projection"]
    check(projection in BASE.BITS, "CAPACITY_PUBLIC_PROJECTION")
    row = {"s1":views[0][projection], "x1":first, "s2":state, "x2":second, "y":reward}
    identifier = digest(canonical(["ckad26-capacity-unit", seed]))
    packet_pin = digest(canonical([identifier, views, row]))
    try:
        BASE.admit(model, identifier, views, row)
    except ValueError as exc:
        check(str(exc) == "CKAD_NATIVE_EPISODE_CAPACITY", "CAPACITY_GUARD_REASON")
    else:
        raise RuntimeError("CKAD26_CAPACITY_ADMISSION_ACCEPTED")
    check(model.checkpoint() == before, "CAPACITY_REJECTION_CHANGED_STATE")
    return {"count":1024, "unit_event_id":identifier, "packet_sha256":packet_pin,
            "rejection":"CKAD_NATIVE_EPISODE_CAPACITY", "before_sha256":digest(before),
            "after_sha256":digest(model.checkpoint()), "source_actions":0, "admitted":False}


def retained_packet(event, projection):
    identifier, public, first, state, second, reward = event
    views = tuple(tuple(view) for view in public)
    check(views[0][projection] == views[1][projection], "RECEIPT_PUBLIC_CONTEXT")
    row = {"s1": views[0][projection], "x1": first, "s2": state, "x2": second, "y": reward}
    check(BASE.retain_event(identifier, views, row) == event, "EXACT_RETAINED_PACKET")
    return identifier, views, row


def run_seed(seed, protocol, output, original_case):
    wall_budget(protocol)
    print(f"CKAD26 seed={seed} start elapsed={time.monotonic()-PROCESS_STARTED:.1f}s", flush=True)
    raw = (PARENT / f"seed-{seed}-coverage-native.json").read_bytes()
    pin = protocol["initial_pins"][str(seed)]
    parent = NativeCumulativeLearner.restore(raw, pin)
    check(parent.checkpoint() == raw, "EXACT_QUALIFIED_PARENT")
    legacy, inherited = BASE.legacy_and_experience(raw)
    prefix = inherited["episodes"]
    check(len(prefix) == 832 and inherited["stream_start"] == 448, "PARENT_STREAM_CONTINUATION")
    projection = parent.info()["episode_experience"]["projection"]
    check(projection in BASE.BITS, "QUALIFIED_PARENT_PROJECTION")
    receipts_raw = (RECEIPTS / f"seed-{seed}-capacity-native.json").read_bytes()
    receipt_pin = protocol["receipt_state_pins"][str(seed)]
    check(digest(receipts_raw) == receipt_pin, "AUTHENTICATED_RECEIPT_STATE_PIN")
    receipt_header, receipt_episode = BASE.legacy_and_experience(receipts_raw)
    events = receipt_episode["episodes"]
    check(receipt_header == legacy and len(events) == 1024 and events[:832] == prefix
          and receipt_episode["stream_start"] == 448, "MATCHED_RECEIPT_CUSTODY")
    original_pins = {row["count"]: row["checkpoint_sha256"] for row in original_case["stream"]}
    check(set(original_pins) == set(protocol["budgets"]["checkpoints"])
          and original_pins[0] == pin and original_pins[192] == receipt_pin
          and original_case["parent_checkpoint_sha256"] == pin
          and original_case["final_checkpoint_sha256"] == receipt_pin, "ORIGINAL25_STREAM_PINS")
    product_monitor = QUALIFIED.restore_monitor(prefix, inherited["stream_start"])
    assert_monitor(parent, product_monitor)
    models = {"native_refresh": parent.enable_experience_refresh(), "native_product": parent}
    monitors = {"native_refresh": REFERENCE.restore_monitor(prefix),
                "native_product": product_monitor,
                "refresh_no_alarm": REFERENCE.restore_monitor(prefix, alarm=False),
                "product_no_alarm": REFERENCE.restore_monitor(prefix, rate=Fraction(), alarm=False),
                "prior_only": REFERENCE.restore_monitor(prefix, rate=Fraction(1))}
    # The exact refresh arm shares this independent reference with native parity;
    # the learner never reads control predictions or receives evaluator labels.
    monitors["exact_refresh"] = monitors["native_refresh"]
    assert_monitor(models["native_refresh"], monitors["native_refresh"])
    check(BASE.context_readout_pin(models["native_refresh"]) == BASE.context_readout_pin(parent),
          "ACTIVATION_PRESERVES_READOUT")
    parity = {"forecasts": 0, "decisions": 0, "mismatches": 0}
    snapshots, child_costs = [], []
    source_seed = seed + protocol["held_source_seed_offset"]
    budget = protocol["budgets"]
    midstream = midstream_raw = None
    retained_reward = 0
    for count in range(193):
        if count in budget["checkpoints"]:
            wall_budget(protocol)
            print(f"CKAD26 seed={seed} count={count} elapsed={time.monotonic()-PROCESS_STARTED:.1f}s", flush=True)
            for arm in NATIVE_ARMS:
                BASE.require_parity(models[arm], monitors[arm].mixture, parity)
                state = models[arm].checkpoint()
                header, episode = BASE.legacy_and_experience(state)
                check(header == legacy and episode["episodes"] == events[:832+count]
                      and episode["episodes"] == monitors[arm].events
                      and episode["stream_start"] == 448, "RETAINED_EVIDENCE")
                assert_monitor(models[arm], monitors[arm])
                if arm == "native_product":
                    check(digest(state) == original_pins[count], "ALL_POINT_PRODUCT25_BYTE_PARITY")
            world = world_at(protocol, 0 if count == 0 else count-1)
            scores = evaluate(models, monitors, parent, source_seed, count, world,
                              budget["held_episodes_per_checkpoint"])
            state = models["native_refresh"].checkpoint()
            snapshots.append({"count": count, "evaluation": scores, "checkpoint_sha256": digest(state),
                "product_checkpoint_sha256": digest(models["native_product"].checkpoint()),
                "monitors": {arm: monitor.info() for arm, monitor in monitors.items() if arm != "exact_refresh"},
                "context_starts": {arm: monitor.mixture.start for arm, monitor in monitors.items() if arm != "exact_refresh"},
                "retained_receipt_reward": retained_reward})
            if count == 80:
                state_pin = digest(state)
                readout = BASE.context_readout_pin(models["native_refresh"])
                models["native_refresh"] = NativeCumulativeLearner.restore(state, state_pin)
                check(models["native_refresh"].checkpoint() == state, "MIDSTREAM_RESTORE")
                midstream = {"count": 80, "sha256": state_pin, "readout_sha256": readout}
                midstream_raw = state
            wall_budget(protocol)
        if count == 192:
            break
        BASE.require_parity(models["native_refresh"], monitors["native_refresh"].mixture, parity)
        identifier, views, row = retained_packet(events[832+count], projection)
        for arm in NATIVE_ARMS:
            models[arm] = BASE.admit(models[arm], identifier, views, row)
            if arm == "native_refresh" and count == 80:
                models[arm], cold_report = cold_update_proof(midstream_raw, midstream["sha256"],
                    midstream["readout_sha256"], identifier, views, row, models[arm].checkpoint())
                midstream.update({"method": "fresh_process_actual_retained_receipt_update_then_continue",
                    "continued_count": 81, "continued_event_id": identifier,
                    "continued_sha256": cold_report["sha256"],
                    "continued_readout_sha256": cold_report["readout_sha256"]})
                child_costs.append({"count": 81, **cold_report["resource_accounting"]})
        for arm, monitor in monitors.items():
            if arm != "exact_refresh":
                monitor.add(events[832+count])
        retained_reward += row["y"]
        for arm in NATIVE_ARMS:
            assert_monitor(models[arm], monitors[arm])
    before_consolidation = models["native_refresh"].checkpoint()
    active = models["native_refresh"].consolidate_experience()
    payload = active.checkpoint()
    check(payload == before_consolidation, "EXACT_CONSOLIDATION")
    check(models["native_product"].checkpoint() == receipts_raw, "EXACT_ORIGINAL25_FINAL_BYTES")
    capacity = capacity_probe(active, seed)
    name = f"seed-{seed}-refresh-native.json"
    destination = output / name
    destination.write_bytes(payload)
    readout = BASE.context_readout_pin(active)
    cold, cost = cold_proof(destination, digest(payload), readout, 1024)
    child_costs.append({"count": 192, **cost})
    check(midstream is not None and len(monitors["native_refresh"].events) == 1024, "CONTINUED_AFTER_RESTART")
    wall_budget(protocol)
    return {"seed": seed, "source_seed": source_seed, "parent_checkpoint_sha256": pin,
            "receipt_state_sha256": receipt_pin, "stream": snapshots, "parity": parity,
            "midstream_restore": midstream, "capacity_probe": capacity,
            "monitors": {arm: monitor.info() for arm, monitor in monitors.items() if arm != "exact_refresh"},
            "change_detection": {arm: detection(monitor) for arm, monitor in monitors.items() if arm != "exact_refresh"},
            "retained_receipt_reward": retained_reward,
            "final_checkpoint_name": name, "final_checkpoint_sha256": digest(payload),
            "final_checkpoint_bytes": len(payload), "final_context_sha256": readout, "cold": cold,
            "resource_accounting": {"cold_children": child_costs}}


def development(seeds):
    def mean(arm, *, counts=tuple(range(0,193,16)), subset=None, metric="reward"):
        rows = [row["evaluation"][arm] for case in (seeds if subset is None else subset)
                for row in case["stream"] if row["count"] in counts]
        if metric == "reward":
            return Fraction(sum(row["reward_sum"] for row in rows), sum(row["episodes"] for row in rows))
        return sum((Fraction(*row["pooled_brier"]) for row in rows), Fraction())/len(rows)
    reward = {arm: mean(arm) for arm in ARMS}
    brier = {arm: mean(arm, metric="brier") for arm in ARMS}
    post = {arm: mean(arm, counts=(16,64,96,160)) for arm in ARMS}
    final = {arm: mean(arm, counts=(192,)) for arm in ARMS}
    per_seed = {str(case["seed"]): mean("native_refresh", subset=[case])-mean("native_product", subset=[case])
                for case in seeds}
    active = reward["native_refresh"]
    gates = {"whole_curve_gain_vs_product": active-reward["native_product"] >= Fraction(3,100),
             "whole_curve_vs_trailing_mle": active >= reward["trailing_mle"],
             "per_seed_whole_curve_no_loss": all(value >= 0 for value in per_seed.values()),
             "seed101_gain_vs_product": per_seed["101"] >= Fraction(1,20),
             "post16_gain_vs_frozen": post["native_refresh"]-post["frozen_ckad24"] >= Fraction(1,20),
             "final_returning_invariant": final["native_refresh"] >= Fraction(4,5),
             "final_retention_vs_product": final["native_refresh"] >= final["native_product"]-Fraction(1,20),
             "final_retention_vs_frozen": final["native_refresh"] >= final["frozen_ckad24"]-Fraction(1,20),
             "whole_curve_brier_vs_product": brier["native_refresh"] <= brier["native_product"]}
    metrics = {"whole_curve_reward": {arm:ratio(value) for arm,value in reward.items()},
               "whole_curve_pooled_brier": {arm:ratio(value) for arm,value in brier.items()},
               "per_seed_reward_delta": {seed:ratio(value) for seed,value in per_seed.items()},
               "post16_reward": {arm:ratio(value) for arm,value in post.items()},
               "post16_gain_vs_frozen": ratio(post["native_refresh"]-post["frozen_ckad24"]),
               "final_reward": {arm:ratio(value) for arm,value in final.items()}}
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
          and protocol["budgets"]["initial_episodes"] == 832
          and protocol["budgets"]["final_episodes"] == 1024
          and protocol["budgets"]["retained_receipts_per_seed"] == 192
          and protocol["budgets"]["refresh_rate"] == [1,32]
          and protocol["held_source_seed_offset"] == 112000
          and [phase["episodes"] for phase in protocol["phases"]] == [48,32,64,48]
          and protocol["budgets"]["boundaries"] == [48,80,144]
          and protocol["budgets"]["post16_checkpoints"] == [16,64,96,160], "FROZEN_SCOPE")
    original = json.loads((RECEIPTS / "campaign-result.json").read_bytes())
    check(original["stable_sha256"] == digest(stable(original))
          == "9d918ca7574c516cab6860eaf6e6db6eb177762033bf77384adbe596e6191ba2"
          and original["source_candidate_sha"] == "dac8685ac4d4b8e045e2c164600ac38f1221b3ac",
          "QUALIFIED25_RESULT_CUSTODY")
    original_cases = {case["seed"]: case for case in original["seeds"]}
    check(set(original_cases) == set(protocol["seeds"]), "QUALIFIED25_SEEDS")
    seeds = [run_seed(seed, protocol, output, original_cases[seed]) for seed in protocol["seeds"]]
    gates, metrics = development(seeds)
    passed = all(gates.values())
    cpu, peak = time.process_time(), peak_rss()
    child_costs = [child for case in seeds for child in case["resource_accounting"]["cold_children"]]
    result = {"schema": "yggdrasil.ckad26.retained-context-refresh.result.v1",
              "classification": "DEVELOPMENT_GO" if passed else "DEVELOPMENT_NO_GO",
              "development_pass": passed, "development_gates": gates, "development_metrics": metrics,
              "source_candidate_sha": subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip(),
              "source_sha256": EXPERIENCE_SOURCE, "scientific_pass": False,
              "accepted_native": False, "deployment": "NONE", "seeds": seeds,
              "parity": {key: sum(case["parity"][key] for case in seeds)
                         for key in ("forecasts","decisions","mismatches")},
              "scope": {"retained_unique_receipts": 576, "native_replayed_admissions": 1152,
                        "new_training_source_episodes": 0, "new_training_source_actions": 0,
                        "held_source_episodes": 3744, "held_policy_rollouts": 33696,
                        "held_matched_brier_trajectories": 3744, "evaluation_action_callbacks": 74880,
                        "held_updates": 0, "original_source_actions": 0, "protected_first_use": 0,
                        "capacity_unit_probes": 3},
              "whole_wall_seconds": time.monotonic()-PROCESS_STARTED,
              "parent_cpu_seconds": cpu, "parent_peak_rss_bytes": peak,
              "resource_accounting": {"parent_cpu_seconds": cpu, "parent_peak_rss_bytes": peak,
                  "measured_child_cpu_seconds": sum(child["cpu_seconds"] for child in child_costs),
                  "parent_plus_measured_child_cpu_seconds": cpu+sum(child["cpu_seconds"] for child in child_costs),
                  "whole_process_peak_rss_bytes": None,
                  "scope_note": "Offline replay of previously witnessed public receipts; no training policy/world execution. Separate parent/child process peaks measured; aggregate process-tree peak and interpreter startup wall not separately measured. CI/setup/authoring/audit additional."}}
    wall_budget(protocol)
    result["stable_sha256"] = digest(stable(result))
    (output / "campaign-result.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="ascii")
    wall_budget(protocol)
    print(json.dumps({"classification": result["classification"], "stable_sha256": result["stable_sha256"]}, sort_keys=True))
    if args.verify_env:
        check(os.environ["CKAD26_EXPECTED_HASH"] == result["stable_sha256"], "CROSS_PLATFORM_RESULT")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="ascii") as stream:
            stream.write("stable="+result["stable_sha256"]+"\n")

if __name__ == "__main__":
    main()

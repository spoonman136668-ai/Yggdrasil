"""Verify the sealed probe comparison without generating or training on new outcomes."""

from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import monotonic

from outcome_probe_trial import FIELDS, POLICIES, SCALE, SCENARIOS, SUPPORTED, admit
from selection_trial import restore
from yggdrasil.native_context_basis import canonical, digest

HERE = Path(__file__).resolve().parent


def audit(checkpoints, plan_path, evidence):
    wall = monotonic()
    plan_raw = plan_path.read_bytes()
    plan = json.loads(plan_raw)
    protocol = json.loads((HERE / plan["input_contract"]).read_bytes())
    report = json.loads((evidence / "result.json").read_bytes())
    expected = [(seed, scenario) for seed in plan["seeds"] for scenario in SCENARIOS]
    cases = [(case["seed"],case["scenario"]) for case in report["cases"]]
    if (report["protocol_sha256"] != digest(plan_raw) or expected != cases or
            report["parent_checkpoint_sha256"] != protocol["joint_sha256"]):
        raise ValueError("Frozen protocol, checkpoint or case roster differs")
    anchor = restore(checkpoints, protocol)
    prefix = anchor.native._episode_reader()._ledger
    raw_cost = []
    recall = []
    safety = []
    held_quality = []
    restored = {}
    source_actions = held_actions = 0
    for case in report["cases"]:
        seed, scenario = case["seed"], case["scenario"]
        case_key = f"{scenario}-{seed}"
        trace_raw = (evidence/f"{case_key}-trace.json").read_bytes()
        if digest(trace_raw) != case["trace_sha256"]:
            raise ValueError("Trace bytes differ")
        trace = json.loads(trace_raw)
        held = trace["shared_held_rows"]
        if len(held) != plan["held_episodes"] or len(held)*2 != case["held_actions"]:
            raise ValueError("Common held action budget differs")
        held_actions += case["held_actions"]
        for name in POLICIES:
            events = trace[name]["training"]
            predictions = trace[name]["held_predictions"]
            recorded = case["policies"][name]
            if len(events)*2 != recorded["action_count"] or len(events) != plan["episodes"]:
                raise ValueError("Acquisition action budget differs")
            counts = Counter(declaration is not None for *_, declaration in events)
            declaration = events[-1][-1]
            if declaration != recorded["declaration"]:
                raise ValueError("Changed declaration receipt")
            if declaration is not None:
                first = next(i for i,event in enumerate(events,1) if event[-1] is not None)
                if declaration[1] != 2*first or any(event[-1] != declaration for event in events[first-1:]):
                    raise ValueError("First declaration timing differs")
            elif counts[True]:
                raise ValueError("A declaration disappeared")
            paid = 2*len(events)+2
            if scenario in SUPPORTED and declaration is not None and declaration[0] == SUPPORTED[scenario]:
                paid = declaration[1]
            held_error = sum((forecast - row[3]*SCALE)**2 for forecast,row in
                             zip(predictions,held,strict=True))
            sequential_error = sum((forecast-row[3]*SCALE)**2 for _,row,forecast,_ in events)
            if (recorded["held_brier_numerator"] != held_error or
                    recorded["brier_numerator"] != sequential_error or
                    recorded["cost_to_correct_declaration"] != paid):
                raise ValueError("Independent Brier or cost accounting differs")
            source_actions += recorded["action_count"]
        models = case["policies"]
        active = models["native_probe"]
        if scenario == "unsupported":
            safety.append(active["declaration"] is None)
        else:
            safety.append(active["declaration"] is None or active["declaration"][0] == SUPPORTED[scenario])
            best = min(m["held_brier_numerator"] for name,m in models.items() if name != "native_probe")
            held_quality.append(Fraction(active["held_brier_numerator"]-best,len(held)*SCALE**2)
                                <= Fraction(plan["max_brier_loss"]))
        if scenario == "supported_shift":
            best, name = min((m["cost_to_correct_declaration"],k) for k,m in models.items()
                             if k!="native_probe")
            gain = best-active["cost_to_correct_declaration"]
            raw_cost.append(gain)
            action_differences = {}
            for arm in POLICIES[1:]:
                stop = min(models[arm]["cost_to_correct_declaration"],
                           active["cost_to_correct_declaration"])//2
                left = trace[arm]["training"][:stop]
                right = trace["native_probe"]["training"][:stop]
                action_differences[arm] = sum(a[1][1]!=b[1][1] for a,b in zip(left,right,strict=True))
            if action_differences != case["different_first_actions"]:
                raise ValueError("Matched action schedule accounting differs")
            recall.append(gain > 0 and action_differences[name] > 0)
        trained = anchor
        observed = []
        for index,(views,row,_,_) in enumerate(trace["native_probe"]["training"]):
            identifier = digest(canonical([plan["id"]+"-"+scenario,seed,"native_probe",index]))
            views = tuple(tuple(view) for view in views)
            packet = dict(zip(FIELDS,row,strict=True))
            trained = admit(trained,identifier,views,packet)
            observed.append((identifier,views,*(packet[k] for k in ("x1","s2","x2","y"))))
        state = trained.checkpoint()
        if digest(state) != case["candidate_sha256"]:
            raise ValueError("Recorded descendant deviated from receipt-only replay")
        with TemporaryDirectory(prefix="amalgam-probe-replay-") as directory:
            path = Path(directory)/"replayed.json"
            path.write_bytes(state)
            cold = restore(checkpoints,protocol,path,case["candidate_sha256"])
        if cold.native._episode_reader()._ledger != prefix+tuple(observed):
            raise ValueError("Cold witness ledger did not retain all admitted data")
        restored[case_key] = case["candidate_sha256"]
    gates = dict(
        action_savings=sum(raw_cost)>=len(raw_cost)*plan["min_mean_actions_saved"],
        most_shift_seeds_gain=sum(recall)>=plan["min_shift_seeds_advantaged"],
        unsupported_abstention_and_no_wrong_declarations=all(safety),
        preserve_brier_quality=all(held_quality),
    )
    if (gates != report["gates"] or raw_cost != report["supported_shift_gains"] or
            source_actions != report["actual_actions"] or held_actions != report["actual_held_actions"] or
            report["development"] != ("DEV_GO" if all(gates.values()) else "DEV_NO_GO")):
        raise ValueError("Independent classification or global action accounting differs")
    return dict(exact_audit=True, cold_descendants=restored,
                recomputed_acquisition_actions=source_actions, recomputed_held_actions=held_actions,
                new_source_actions=0,wall_seconds=monotonic()-wall)


if __name__=="__main__":
    print(json.dumps(audit(*map(Path,sys.argv[1:])),indent=2,sort_keys=True))

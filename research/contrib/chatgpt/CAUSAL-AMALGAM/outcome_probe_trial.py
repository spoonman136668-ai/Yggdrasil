"""Development action-cost comparison on fresh, matched synthetic worlds."""

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from resource import RUSAGE_SELF, getrusage
import sys
from time import monotonic, process_time

from outcome_probe import OutcomeProbe, reversal_quarters
from selection_trial import SCALE, restore, source_module
from staged_retention import admit
from yggdrasil.native_context_basis import canonical, digest

HERE = Path(__file__).resolve().parent
POLICIES = ("native_probe", "native_balanced", "beta_probe", "recent_beta_probe")
SCENARIOS = ("unchanged", "supported_shift", "unsupported")
SUPPORTED = {"unchanged":0, "supported_shift":1}
FIELDS = ("s1", "x1", "x2", "s2", "y")


def native_start(model):
    return {(c,a):float(model.native.experience_context_forecast((c,0),a))
            for c in (0,1) for a in (0,1)}


def conventional_start(history):
    def fit(events):
        counts = defaultdict(lambda:[0,0])
        for _, views, action, outcome, _, _ in events:
            counts[views[0][0],action][outcome] += 1
        return {(c,a):(ones+0.5)/(zeros+ones+1)
                for c in (0,1) for a in (0,1) for zeros,ones in [counts[c,a]]}
    return fit(history), fit(history[-128:])


def cohort_episode(source, manifest, scenario, seed, index):
    domain = manifest["id"]+"-"+scenario
    fixture = source.make_episode(cohort=domain, seed=seed, index=index,
                                  family="invariant", regime=0)
    return domain, fixture


def intervention(fixture, scenario, context, action, previous_action, second, draw):
    outcome = fixture.transition(action)
    if scenario == "supported_shift":
        outcome ^= int(draw < reversal_quarters(context,action))
    elif scenario == "unsupported":
        outcome ^= previous_action
    return dict(s1=context,x1=action,x2=second,s2=outcome,y=fixture._reward(action,outcome,second))


def run_case(seed, scenario, source, anchor, manifest, target, deadline):
    history = anchor.native._episode_reader()._ledger
    prior = native_start(anchor)
    fitted, recent = conventional_start(history)
    budget = manifest["episodes"]
    controls = manifest["declaration"]
    held = []
    preceding = 0
    for index in range(manifest["held_episodes"]):
        domain = manifest["id"]+"-held-"+scenario
        fixture = source.make_episode(cohort=domain, seed=seed, index=index,
                                      family="invariant", regime=0)
        context = source.public_views(fixture)[0][0]
        action, second = [value & 1 for value in sha256(canonical([domain,seed,index])).digest()[:2]]
        draw = sha256(canonical([domain,seed,index,"effect"])).digest()[0] & 3
        row = intervention(fixture,scenario,context,action,preceding,second,draw)
        held.append(row)
        preceding = action
    traces, checkpoints, results = {}, {}, {}
    for name, table in zip(POLICIES,(prior,prior,fitted,recent),strict=True):
        model = anchor
        reader = OutcomeProbe(lambda c,a:table[c,a],active=name != "native_balanced")
        prior_action = 0
        declared = None
        events = []
        numerator = 0
        for index in range(budget):
            if monotonic() > deadline:
                raise TimeoutError("Frozen prospective budget expired")
            domain, fixture = cohort_episode(source,manifest,scenario,seed,index)
            views = source.public_views(fixture)
            context = views[0][0]
            action, hypotheses, forecast = reader.choose(context)
            second = sha256(canonical([domain,seed,index])).digest()[0] & 1
            draw = sha256(canonical([domain,seed,index,"effect"])).digest()[0] & 3
            row = intervention(fixture,scenario,context,action,prior_action,second,draw)
            next_state = row["s2"]
            point = round(forecast*SCALE)
            numerator += (point-next_state*SCALE)**2
            identifier = digest(canonical([domain,seed,name,index]))
            prior_action = action
            reader.observe(context,action,hypotheses,next_state)
            if declared is None and (first := reader.declaration(**controls)) is not None:
                declared = [first,2*(index+1)]
            if name == "native_probe":
                model = admit(model,identifier,views,row)
            events.append([views,[row[field] for field in FIELDS],point,declared])
        held_points = []
        for row in held:
            pair = reader.hypotheses(row["s1"],row["x1"])
            forecast = sum(w*p for w,p in zip(reader.mass,pair,strict=True))
            held_points.append(round(forecast*SCALE))
        results[name] = dict(
            action_count=2*budget, declaration=declared, brier_numerator=numerator,
            held_brier_numerator=sum((point-row["s2"]*SCALE)**2
                                     for point,row in zip(held_points,held,strict=True)),
            confidence_without_calibration=reader.mass,
            cost_to_correct_declaration=(declared[1] if scenario in SUPPORTED and declared is not None
                                         and declared[0] == SUPPORTED[scenario] else 2*budget+2),
        )
        if name == "native_probe":
            raw = model.checkpoint()
            checkpoints[name] = digest(raw)
            (target / f"{scenario}-{seed}-native-probe.json").write_bytes(raw)
            next_ledger = model.native._episode_reader()._ledger
            if next_ledger[:len(history)] != history or len(next_ledger) != len(history)+budget:
                raise RuntimeError("Native witness continuity failure")
            if [b.steps-a.steps for a,b in zip(anchor._heads,model._heads,strict=True)] != [3*budget]*4:
                raise RuntimeError("Specialist witness continuity failure")
        traces[name] = dict(training=events, held_predictions=held_points)
    traces["shared_held_rows"] = [[row[field] for field in FIELDS] for row in held]
    counts = {}
    for name in POLICIES[1:]:
        cutoff = min(results[arm]["cost_to_correct_declaration"] for arm in (name,"native_probe"))//2
        left = traces[name]["training"][:cutoff]
        right = traces["native_probe"]["training"][:cutoff]
        counts[name] = sum(a[1][1]!=b[1][1] for a,b in zip(left,right,strict=True))
    payload = canonical(traces)
    (target / f"{scenario}-{seed}-trace.json").write_bytes(payload)
    return dict(seed=seed, scenario=scenario, policies=results, held_actions=2*len(held),
                candidate_sha256=checkpoints["native_probe"], trace_sha256=digest(payload),
                different_first_actions=counts)


def evaluate(records, manifest):
    advantage = []
    gains = []
    safety = []
    calibration = []
    total = manifest["held_episodes"] * SCALE**2
    for case in records:
        rows = case["policies"]
        candidate = rows["native_probe"]
        if case["scenario"] == "unsupported":
            safety.append(candidate["declaration"] is None)
            continue
        if case["scenario"] == "supported_shift":
            best, control = min((v["cost_to_correct_declaration"],k) for k,v in rows.items()
                                if k!="native_probe")
            improvement = best - candidate["cost_to_correct_declaration"]
            gains.append(improvement)
            advantage.append(improvement > 0 and case["different_first_actions"][control] > 0)
        correct = candidate["declaration"]
        if correct is not None and correct[0] != SUPPORTED[case["scenario"]]:
            safety.append(False)
        best = min(v["held_brier_numerator"] for k,v in rows.items() if k!="native_probe")
        calibration.append(Fraction(candidate["held_brier_numerator"]-best,total)
                           <= Fraction(manifest["max_brier_loss"]))
    gates = {
        "action_savings": sum(gains) >= len(gains)*manifest["min_mean_actions_saved"],
        "most_shift_seeds_gain": sum(advantage) >= manifest["min_shift_seeds_advantaged"],
        "unsupported_abstention_and_no_wrong_declarations": all(safety),
        "preserve_brier_quality": all(calibration),
    }
    return gates, gains


def run(checkpoints, plan_path, output):
    start,cpu=monotonic(),process_time()
    raw=plan_path.read_bytes()
    manifest=json.loads(raw)
    for n,pin in manifest["sources"].items():
        if digest((HERE/n).read_bytes()) != pin:
            raise ValueError("Code digest differs from frozen protocol")
    proof=json.loads((HERE/"selection_protocol_dev.json").read_bytes())
    source=source_module(proof["world_sha256"])
    anchor=restore(checkpoints,proof)
    reader=anchor.native._episode_reader()
    if len(reader._ledger)+manifest["episodes"]>reader._episode_limit:
        raise ValueError("Budget exceeds exact native capacity")
    output.mkdir(exist_ok=False)
    deadline=start+manifest["wall_cap_seconds"]
    results=[run_case(seed,case,source,anchor,manifest,output,deadline)
             for seed in manifest["seeds"] for case in SCENARIOS]
    gates,gains=evaluate(results,manifest)
    return dict(development="DEV_GO" if all(gates.values()) else "DEV_NO_GO",
                protocol_sha256=digest(raw),parent_checkpoint_sha256=proof["joint_sha256"],
                actual_actions=sum(p["action_count"] for r in results for p in r["policies"].values()),
                actual_held_actions=sum(r["held_actions"] for r in results),
                cases=results, gates=gates, supported_shift_gains=gains,
                wall_seconds=monotonic()-start,cpu_seconds=process_time()-cpu,
                max_rss_kib=getrusage(RUSAGE_SELF).ru_maxrss)


if __name__=="__main__":
    print(json.dumps(run(*map(Path,sys.argv[1:])),indent=2,sort_keys=True))

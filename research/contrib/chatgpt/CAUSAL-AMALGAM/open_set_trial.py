"""One bounded, disjoint structural improvement trial with an explicit open set."""

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from resource import RUSAGE_SELF, getrusage
import sys
from time import monotonic, process_time

from open_set_readout import OpenSetReadout
from selection_trial import SCALE, TransitionControls, restore, source_module
from staged_retention import admit
from yggdrasil.native_context_basis import canonical, digest

HERE = Path(__file__).resolve().parent
ARMS = ("candidate", "pinned", "native_live", "fitted_gate", "native_template",
        "history_change_point")


def events(source, cohort, seed, phase):
    previous = 0
    for index in range(phase["count"]):
        fixture = source.make_episode(cohort=cohort, seed=seed, index=index,
                                      family="invariant", regime=0)
        views = source.public_views(fixture)
        action, second = (n & 1 for n in sha256(canonical([cohort,seed,index])).digest()[:2])
        executed = 0 if phase["mask"] & (1 << views[0][0]) else action ^ phase["swap"]
        state = fixture.transition(executed) ^ (previous if phase["lag"] else 0)
        yield views, dict(s1=views[0][0], x1=action, x2=second, s2=state,
                          y=fixture._reward(executed,state,second))
        previous = action


def comparison(seed, source, protocol, anchor, output):
    start, cpu = monotonic(),process_time()
    trained = anchor
    ledger = anchor.native._episode_reader()._ledger
    previous = [(views[0], a, s) for _, views, a, s, _, _ in ledger]
    prior_counts = defaultdict(lambda:[0,0])
    for v,a,state in previous:
        prior_counts[v[0],a][state] += 1

    def native_prior(v,a):
        return float(anchor.native.experience_context_forecast(v,a))

    def fitted_prior(v,a):
        zero, one = prior_counts[v[0],a]
        return (one+0.5)/(zero+one+1)

    trace, scores = [], []
    for stage, phase in enumerate(protocol["phases"]):
        reader = OpenSetReadout(native_prior, previous, TransitionControls(32, 1 / 32))
        fitted = OpenSetReadout(fitted_prior, previous, TransitionControls(32, 1 / 32))
        counts = dict.fromkeys(ARMS,0)
        accepted_modes = [0,0,0,0]
        n = 0
        cohort = protocol["id"]+"-"+phase["name"]
        for i,(views,row) in enumerate(events(source,cohort,seed,phase)):
            if monotonic()-start >= protocol["wall_seconds_per_seed"]:
                raise TimeoutError("Open-set template development wall cap reached")
            view = views[0]
            action,state = row["x1"],row["s2"]
            probabilities = reader.evidence_predictions(view,action)
            control = fitted.evidence_predictions(view,action)
            selected, mode = reader.forecast(probabilities)
            paired = (selected,probabilities[0],trained.native.experience_context_forecast(view,action),
                      fitted.forecast(control)[0], probabilities[1], probabilities[2])
            predictions = {k:round(v*SCALE) for k,v in zip(ARMS,paired,strict=True)}
            if i >= protocol["warmup"]:
                n += 1
                accepted_modes[mode if mode is not None else 3] += 1
                for k,p in predictions.items():
                    counts[k] += (p-state*SCALE)**2
            identifier = digest(canonical([cohort,seed,i]))
            trace.append(dict(stage=stage,identifier=identifier,views=views,row=row,
                              forecasts=predictions,mode=mode,scored=i>=protocol["warmup"]))
            reader.observe(view,action,state,probabilities)
            fitted.observe(view,action,state,control)
            trained = admit(trained,identifier,views,row)
        scores.append(dict(phase=phase["name"],n=n,squared_errors=counts,modes=accepted_modes))
    raw = trained.checkpoint()
    final = trained.native._episode_reader()._ledger
    if final[:len(ledger)] != ledger or len(final) != len(ledger)+len(trace):
        raise RuntimeError("Native training continuity failed")
    target = output/f"seed-{seed}"
    target.mkdir()
    (target/"joint.json").write_bytes(raw)
    (target/"trace.json").write_bytes(canonical(trace))
    return dict(seed=seed,checkpoints=dict(final_sha256=digest(raw),trace_sha256=digest(canonical(trace))),
                scores=scores,head_steps=[new.steps-old.steps for old,new in zip(anchor._heads,trained._heads,strict=True)],
                actions=2*len(trace),wall_seconds=monotonic()-start,cpu_seconds=process_time()-cpu)


def evaluate(replicas, protocol):
    results = {}
    for replica in replicas:
        for stage in replica["scores"]:
            loss = {k:Fraction(v,stage["n"]*SCALE**2) for k,v in stage["squared_errors"].items()}
            delta = loss["candidate"]
            name = stage["phase"]
            if name == "paired_new":
                best = min(v for k,v in loss.items() if k != "candidate")
                ok = best-delta >= Fraction(protocol["gain"])
            elif name == "familiar":
                best = loss["pinned"]
                ok = delta-best <= Fraction(protocol["old_and_unsupported_loss"])
            else:
                best = min(loss[k] for k in ("native_live","fitted_gate","history_change_point"))
                ok = delta-best <= Fraction(protocol["old_and_unsupported_loss"])
            results[f"{replica['seed']}:{name}"]=dict(pass_gate=ok,candidate_brier=float(delta),
                                                    comparator_brier=float(best))
    return results


def run(checkpoints, manifest_path, output):
    started,cpu=monotonic(),process_time()
    raw=manifest_path.read_bytes()
    manifest=json.loads(raw)
    for path,pin in manifest["sources"].items():
        if digest((HERE/path).read_bytes()) != pin:
            raise ValueError("Open-set source hash mismatch")
    protocol=json.loads((HERE/"selection_protocol_dev.json").read_bytes())
    source=source_module(protocol["world_sha256"])
    anchor=restore(checkpoints,protocol)
    original=anchor.native._episode_reader()
    if sum(p["count"] for p in manifest["phases"])+len(original._ledger)>original._episode_limit:
        raise ValueError("Run would exceed the current witness capacity")
    output.mkdir(exist_ok=False)
    replicas=[comparison(seed,source,manifest,anchor,output) for seed in manifest["seeds"]]
    gates=evaluate(replicas,manifest)
    return dict(development="DEV_GO" if all(g["pass_gate"] for g in gates.values()) else "DEV_NO_GO",
                protocol_sha256=digest(raw),input_sha256=protocol["joint_sha256"],replicas=replicas,
                gates=gates,wall_seconds=monotonic()-started,cpu_seconds=process_time()-cpu,
                max_rss_kib=getrusage(RUSAGE_SELF).ru_maxrss)


if __name__=="__main__":
    print(json.dumps(run(*map(Path,sys.argv[1:])),indent=2,sort_keys=True))

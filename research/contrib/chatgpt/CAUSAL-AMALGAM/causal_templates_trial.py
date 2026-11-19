"""Bounded test of learned native action transformations on matched interventions."""

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from resource import RUSAGE_SELF, getrusage
import sys
from time import monotonic, process_time

from causal_templates import CausalTemplates
from selection_trial import SCALE, TransitionControls, restore, source_module
from staged_retention import admit
from yggdrasil.native_context_basis import canonical, digest

HERE = Path(__file__).resolve().parent
ARMS = ("pinned", "live", "native_structure", "fitted_structure", "recent_beta",
        "change_point", "randomized_structure")


def cases(source, cohort, seed, phase):
    """Apply causal transforms only on the evaluator side of the public interface."""
    for index in range(phase["count"]):
        fixture = source.make_episode(cohort=cohort, seed=seed, index=index,
                                      family="invariant", regime=0)
        views = source.public_views(fixture)
        a, b = index % 2, (index // 2) % 2
        context = views[0][0]
        command = 0 if phase["inhibit_mask"] & (1 << context) else a ^ phase["swap"]
        state = fixture.transition(command) ^ int(bool(phase["context_flip"] & (1 << context)))
        yield views, dict(s1=context, x1=a, x2=b, s2=state, y=fixture._reward(command, state, b))


def one_seed(seed, anchor, source, manifest, output):
    wall, cpu = monotonic(), process_time()
    model = anchor
    counts = defaultdict(lambda: [0, 0])
    historical = anchor.native._episode_reader()._ledger
    for _, v, first, state, _, _ in historical:
        counts[(v[0][0], first)][state] += 1

    def fitted_prior(view, action):
        zero, one = counts[view[0], action]
        return (one + 0.5) / (zero + one + 1)

    def native_prior(view, action):
        return float(anchor.native.experience_context_forecast(view, action))

    model_scores = []
    traces = []
    for phase_idx, phase in enumerate(manifest["phases"]):
        # Each arm is given the same stream boundary; the causal law is hidden.
        native = CausalTemplates(native_prior)
        conventional = CausalTemplates(fitted_prior)
        randomized = CausalTemplates(native_prior)
        recent = TransitionControls(32, 1 / 32)
        for _, views, first, state, _, _ in historical:
            recent.update((views[0][0], first), state)
        totals = dict.fromkeys(ARMS, 0)
        n = 0
        cohort = manifest["id"] + "-" + phase["name"]
        for i, (views, row) in enumerate(cases(source, cohort, seed, phase)):
            if monotonic() - wall > manifest["wall_seconds_per_seed"]:
                raise TimeoutError("Causal templates trial reached its wall cap")
            view = views[0]
            action, observed = row["x1"], row["s2"]
            beta, change = recent.forecast((view[0], action))
            candidate = native.marginal(view, action)
            forecasts = (native_prior(view, action),
                         model.native.experience_context_forecast(view, action),
                         candidate, conventional.marginal(view, action), beta,
                         change, randomized.marginal(view, action))
            rounded = {name: round(p * SCALE) for name,p in zip(ARMS, forecasts, strict=True)}
            if i >= manifest["warmup"]:
                n += 1
                for name, p in rounded.items():
                    totals[name] += (p - observed*SCALE)**2
            identifier = digest(canonical([cohort,seed,i]))
            traces.append(dict(stage=phase_idx, identifier=identifier, views=views, row=row,
                               forecasts=rounded, scored=i>=manifest["warmup"]))
            native.advance(view, action, observed)
            conventional.advance(view, action, observed)
            randomized.advance((view[0]^1,view[1]), action^1, observed)
            recent.update((view[0], action), observed)
            model = admit(model, identifier, views, row)
        model_scores.append(dict(phase=phase["name"], n=n, squared_errors=totals,
                                 final_native_template_masses=native.mass))
    raw = model.checkpoint()
    native = model.native._episode_reader()._ledger
    if native[:len(historical)] != historical or len(native) != len(historical)+len(traces):
        raise RuntimeError("Template trial witness accounting")
    seed_folder = output / f"seed-{seed}"
    seed_folder.mkdir()
    (seed_folder/"trace.json").write_bytes(canonical(traces))
    (seed_folder/"joint.json").write_bytes(raw)
    return dict(seed=seed, checkpoints=dict(final_sha256=digest(raw), trace_sha256=digest(canonical(traces))),
                seen=len(traces), scores=model_scores, actions=2*len(traces),
                head_steps=[new.steps-old.steps for old,new in zip(anchor._heads,model._heads,strict=True)],
                wall_seconds=monotonic()-wall, cpu_seconds=process_time()-cpu)


def decide(replicas, manifest):
    margin = Fraction(manifest["gain"])
    limit = Fraction(manifest["old_and_unsupported_loss"])
    required = {}
    for replica in replicas:
        for stage in replica["scores"]:
            loss = {name: Fraction(value,stage["n"]*SCALE**2)
                    for name,value in stage["squared_errors"].items()}
            current = loss["native_structure"]
            if stage["phase"] == "paired_new":
                baseline = min(loss[name] for name in ARMS if name != "native_structure")
                passed = baseline-current >= margin
            elif stage["phase"] == "familiar":
                baseline = loss["pinned"]
                passed = current-baseline <= limit
            else:
                baseline = min(loss["live"],loss["change_point"],loss["fitted_structure"])
                passed = current-baseline <= limit
            required[f"{replica['seed']}:{stage['phase']}"] = dict(
                pass_gate=passed, comparator_brier=float(baseline), candidate_brier=float(current))
    return required


def run(checkpoints, plan, output):
    begin, cpu = monotonic(),process_time()
    raw = plan.read_bytes()
    manifest = json.loads(raw)
    for relative, sha in manifest["sources"].items():
        if sha256((HERE/relative).read_bytes()).hexdigest() != sha:
            raise ValueError("Causal template code differs from frozen source")
    protocol = json.loads((HERE/"selection_protocol_dev.json").read_bytes())
    source = source_module(protocol["world_sha256"])
    anchor = restore(checkpoints, protocol)
    reader = anchor.native._episode_reader()
    if sum(p["count"] for p in manifest["phases"])+len(reader._ledger)>reader._episode_limit:
        raise ValueError("Trial would exceed the existing witness capacity")
    output.mkdir(exist_ok=False)
    results = [one_seed(seed,anchor,source,manifest,output) for seed in manifest["seeds"]]
    required = decide(results,manifest)
    return dict(development="DEV_GO" if all(g["pass_gate"] for g in required.values()) else "DEV_NO_GO",
                protocol_sha256=digest(raw), input_sha256=protocol["joint_sha256"],
                replicas=results, gates=required, wall_seconds=monotonic()-begin,
                cpu_seconds=process_time()-cpu, max_rss_kib=getrusage(RUSAGE_SELF).ru_maxrss)


if __name__ == "__main__":
    print(json.dumps(run(*map(Path,sys.argv[1:])),indent=2,sort_keys=True))

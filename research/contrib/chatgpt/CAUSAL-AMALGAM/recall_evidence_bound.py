"""Expected transition loss under a bounded public regime-evidence budget."""

import json
from pathlib import Path
import sys

from retention_identifiability import target
from selection_trial import restore
from shadow_preflight import checked_bytes
from transfer_curve import error
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE

HERE = Path(__file__).resolve().parent
CELLS = ((0, 0), (0, 1), (1, 0), (1, 1))
BUDGETS = (0, 1, 2, 4, 8)


def probability_table(family, orientation):
    phase = dict(family=family, regime=orientation, swap=0, mask_by_context=False)
    return tuple(float(target(*cell, phase)) for cell in CELLS)


def observations(old, new, anchor, trained):
    """Keep a likelihood for each regime under both evaluator and native models."""
    probabilities = [(1.0, 1.0, 1.0, 1.0)]
    for n in range(BUDGETS[-1] + 1):
        if n in BUDGETS:
            yield n, probabilities
        if n == BUDGETS[-1]:
            break
        cell = n % len(CELLS)
        row = (old[cell], new[cell], anchor[cell], trained[cell])
        probabilities = [tuple(w * (p if bit else 1 - p) for w, p in
                               zip(prior, row, strict=True))
                         for prior in probabilities for bit in (0, 1)]


def bound(old, new, anchor, trained, held):
    result = []
    for budget, sequences in observations(old, new, anchor, trained):
        cells = {
            "familiar": tuple(range(len(CELLS))),
            "familiar_held_cell": (held,),
            "novel_held_cell": (held,),
        }
        losses = {}
        for name, selected in cells.items():
            regime = int(name == "novel_held_cell")
            actual = (old, new)[regime]
            totals = dict.fromkeys(("fixed_anchor", "fixed_continuation", "known_regime_readout",
                                    "native_likelihood_readout", "exact_likelihood_readout",
                                    "bayes_floor"), 0.0)
            for old_weight, new_weight, native_old, native_new in sequences:
                posterior = new_weight / (old_weight + new_weight)
                native_posterior = (native_new / (native_old + native_new)
                                    if native_old + native_new else 0.5)
                for cell in selected:
                    p = actual[cell]
                    a, b = anchor[cell], trained[cell]
                    readings = (
                        a, b, (a, b)[regime],
                        a + native_posterior * (b - a), a + posterior * (b - a),
                        old[cell] + posterior * (new[cell] - old[cell]),
                    )
                    weight = (old_weight, new_weight)[regime] / len(selected)
                    for arm, q in zip(totals, readings, strict=True):
                        totals[arm] += weight * (p * (1 - p) + (p - q) ** 2)
            losses[name] = {arm: round(loss, 10) for arm, loss in totals.items()}
        correct = sum(max(a, b) for a, b, _, _ in sequences) / 2
        result.append(dict(public_witnesses=budget, bayes_regime_accuracy=round(correct, 10),
                           expected_transition_brier=losses))
    return result


def forecast_table(native):
    values = tuple(native.experience_context_forecast((c, 0), a) for c, a in CELLS)
    if values != tuple(native.experience_context_forecast((c, 1), a) for c, a in CELLS):
        raise ValueError("Uniform context-action table requires nuisance invariance")
    return values


def run(checkpoints):
    evidence = HERE / "transfer-curve-dev-01"
    protocol_raw = (HERE / "transfer_curve_protocol.json").read_bytes()
    result_raw = (evidence / "result.json").read_bytes()
    plan, sealed = json.loads(protocol_raw), json.loads(result_raw)
    if sealed["protocol_sha256"] != digest(protocol_raw):
        raise ValueError("Frozen protocol digest differs")
    proof = json.loads((HERE / "selection_protocol_dev.json").read_bytes())
    if proof["joint_sha256"] != sealed["parent_sha256"]:
        raise ValueError("Archived starting checkpoint differs")
    anchor = restore(checkpoints, proof).native
    prefix = anchor._episode_reader()._ledger
    anchor_table = forecast_table(anchor)
    old = probability_table("invariant", 0)
    output = []
    for case, report in zip(plan["cases"], sealed["replicas"], strict=True):
        seed = case["seed"]
        if seed != report["seed"]:
            raise ValueError("Case roster changed")
        trace = json.loads(checked_bytes(evidence / f"trace-{seed}.json", report["trace_sha256"]))
        current = anchor
        for identifier, views, row in trace["train"]:
            views = tuple(tuple(v) for v in views)
            current = current.observe_experience(
                identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
                packet_sha256=digest(canonical([identifier, views, row])),
            )
        ledger = current._episode_reader()._ledger
        if ledger[:len(prefix)] != prefix or len(ledger) != report["final_witnesses"]:
            raise ValueError("Reconstructed native witness continuity differs")
        trained_table = forecast_table(current)
        final = report["milestones"][-1]
        for split, group, key in (("transfer", "transfer", "native"),
                                  ("retention", "retention", "native_transition")):
            loss = sum(error(trained_table[CELLS.index((row["s1"], row["x1"]))], row["s2"])
                       for _, _, row in trace[split])
            if loss != final[group][key]:
                raise ValueError("Native reconstruction differs from the sealed scoring receipt")
        output.append(dict(seed=seed, omitted=case["omitted"], trace_sha256=report["trace_sha256"],
                           predicted_anchor=list(map(float, anchor_table)),
                           predicted_continuation=list(map(float, trained_table)),
                           curve=bound(old, probability_table("context_switch", case["orientation"]),
                                       tuple(map(float, anchor_table)), tuple(map(float, trained_table)),
                                       CELLS.index(tuple(case["omitted"])))))
    return dict(scope="Analytic diagnostic of sealed development evidence",
                source_actions=0, result_sha256=digest(result_raw),
                protocol_sha256=digest(protocol_raw), cases=output)


if __name__ == "__main__":
    print(json.dumps(run(Path(sys.argv[1])), indent=2, sort_keys=True))

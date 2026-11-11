"""WSP16 frozen contradiction/retention DEV and information-bound negative."""
import hashlib
import importlib.util
import json
import math
import platform
import sys
import time
from pathlib import Path
from neutral import (NeutralNand, OBSERVED, PlasticNand, PUBLIC, SEEDS,
                     TRIALS, context, mismatch)


def original_examples(signature):
    return tuple((context(i), (signature >> j) & 1) for j, i in enumerate(PUBLIC))


def trained_six(obs):
    """Genuine conventional full-batch Adam, identical six observations."""
    weights, moment, velocity = [0.]*8, [0.]*8, [0.]*8
    for step in range(1, 2049):
        loss = sum(math.log1p(math.exp(-weights[i])) if y else math.log1p(math.exp(weights[i]))
                   for i, (_x, y) in zip(OBSERVED, obs))/6
        if loss <= .02:
            return tuple(int(w > 0) for w in weights), step-1, loss
        for i, (_x, y) in zip(OBSERVED, obs):
            grad = (1/(1+math.exp(-weights[i]))-y)/6
            moment[i] = .9*moment[i]+.1*grad
            velocity[i] = .999*velocity[i]+.001*grad*grad
            weights[i] -= .1*(moment[i]/(1-.9**step))/(math.sqrt(velocity[i]/(1-.999**step))+1e-8)
    return tuple(int(w > 0) for w in weights), 2048, loss


def symbolic_reference():
    path = Path(__file__).resolve().parents[1]/"WSP-14"/"nand_program.py"
    spec = importlib.util.spec_from_file_location("wsp16_wsp14_reference", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run():
    start = time.perf_counter()
    tick = time.perf_counter()
    ref = symbolic_reference()
    catalog = ref.catalog()
    setup = time.perf_counter()-tick
    scores = {mode: {"witness_correct": 0, "observed_correct": 0, "exact_tasks": 0,
                      "old_valid_retained": 0, "old_valid_lost": 0, "hidden_correct": 0}
              for mode in ("neutral", "strict", "random", "disabled", "symbolic", "precompiled", "trained")}
    operations = {m: {"proposals": 0, "nand_evaluations": 0, "accepted": 0,
                      "neutral_accepts": 0, "improving_accepts": 0, "noise_draws": 0, "scalar_ops": 0}
                  for m in ("neutral", "strict", "random", "disabled")}
    times = {m: 0. for m in ("initial_acquisition", "neutral", "strict", "random", "disabled", "symbolic", "trained")}
    old_valid = restores = converged = steps = 0
    state_bytes = []
    replay = 0
    for seed in SEEDS:
        for sig in range(32):
            original = original_examples(sig)
            tick = time.perf_counter()
            initial = PlasticNand().learn(original, seed)
            raw = initial.snapshot()
            times["initial_acquisition"] += time.perf_counter()-tick
            initial_predictions = tuple(initial.predict(context(i)) for i in range(8))
            obs = original+((context(3), 1-initial_predictions[3]),)
            valid = [initial_predictions[i] == y for i, (_x, y) in zip(PUBLIC, original)]
            old_valid += sum(valid)
            predictions = {}
            for mode in ("neutral", "strict", "random", "disabled"):
                tick = time.perf_counter()
                model = NeutralNand(raw).adapt(obs, seed, mode)
                predictions[mode] = tuple(model.predict(context(i)) for i in range(8))
                times[mode] += time.perf_counter()-tick
                for name in operations[mode]:
                    operations[mode][name] += getattr(model, name)
                if mode == "disabled" and model.rows != initial.rows:
                    raise AssertionError("WSP16_NO_WITNESS_STATE_CHANGED")
                if mode == "neutral":
                    checkpoint = model.snapshot()
                    cold = NeutralNand.restore(checkpoint)
                    if checkpoint != cold.snapshot() or predictions[mode] != tuple(cold.predict(context(i)) for i in range(8)):
                        raise AssertionError("WSP16_COLD_MISMATCH")
                    restores += 1
                    state_bytes.append(checkpoint)
                    if sig == 19:
                        replay += NeutralNand(raw).adapt(obs, seed).snapshot() == checkpoint
            tick = time.perf_counter()
            choices = [(cost, mask, program) for mask, (cost, program) in catalog.items()
                       if all(ref.symbolic_eval(program, x) == y for x, y in obs)]
            _cost, _mask, tree = min(choices, key=lambda t: (t[0], t[1]))
            predictions["symbolic"] = tuple(ref.symbolic_eval(tree, context(i)) for i in range(8))
            circuit = ref.NumericNand.from_program(tree)
            predictions["precompiled"] = tuple(circuit.predict(context(i)) for i in range(8))
            times["symbolic"] += time.perf_counter()-tick
            tick = time.perf_counter()
            trained, n, bce = trained_six(obs)
            times["trained"] += time.perf_counter()-tick
            if bce > .02 or n > 2048:
                raise AssertionError("WSP16_TRAINED_NOT_CONVERGED")
            converged += 1
            steps += n
            predictions["trained"] = trained
            for mode, pred in predictions.items():
                row = scores[mode]
                row["witness_correct"] += pred[3] == obs[-1][1]
                fit = sum(pred[i] == y for i, (_x, y) in zip(OBSERVED, obs))
                row["observed_correct"] += fit
                row["exact_tasks"] += fit == 6
                for j, (i, (_x, y)) in enumerate(zip(PUBLIC, original)):
                    row["old_valid_retained"] += valid[j] and pred[i] == y
                    row["old_valid_lost"] += valid[j] and pred[i] != y
                for assignment in range(4):
                    for j, i in enumerate((5, 6)):
                        row["hidden_correct"] += pred[i] == ((assignment >> j) & 1)
    supported = (scores["neutral"]["witness_correct"] >= 122
                 and scores["neutral"]["observed_correct"] >= 730
                 and scores["neutral"]["old_valid_lost"] == 0 and restores == 128)
    required = (restores == converged == 128 and replay == 4
                and all(row["hidden_correct"] == 512 for row in scores.values())
                and all(scores[m]["observed_correct"] == 768 for m in ("symbolic", "precompiled", "trained"))
                and scores["disabled"]["witness_correct"] == 0
                and all(op["proposals"] == 128*TRIALS for op in operations.values()))
    report = {"schema": "wsp16.public-dev.v1", "engineering": "PASS" if required else "FAIL",
              "frozen_hypothesis": "DEV_SUPPORTED" if supported else "SCIENTIFIC_NEGATIVE",
              "scientific_superiority": "UNVERIFIED; authorship/public DEV; strongest symbolic fits all observations",
              "tasks": 128, "observed_total": 768, "hidden_total": 1024,
              "initial_old_correct_of640": old_valid, "initial_witness_correct": 0,
              "scores": scores, "operations": operations, "cold_restores": restores,
              "seed_replays": replay, "trained_converged": converged, "trained_steps": steps,
              "state_digest_sha256": hashlib.sha256(b"".join(state_bytes)).hexdigest(),
              "checkpoint_bytes": len(state_bytes[0]), "binary_synapses": 75,
              "external_replay_examples_per_task": 6, "gradient_steps_candidate": 0,
              "external_logic": "Generic simulator, independent noise and evidence custody. Numeric non-worsening reward controls updates; search policy remains manually designed. Symbolic selection is CONTROL ONLY.",
              "seconds": {**{k: round(v, 6) for k, v in times.items()}, "symbolic_cold_catalog_setup": round(setup, 6)},
              "total_seconds": round(time.perf_counter()-start, 6),
              "environment": {"python": sys.version, "platform": platform.platform()},
              "limits": "Witness chosen adversarially from initial prediction. Six public examples retained externally for replay. No native novel primitive or unfamiliar-family transfer; no compute/capacity-matched strongest neural comparator. All overhead included only in end-to-end time."}
    print(json.dumps(report, sort_keys=True, indent=2))
    if not required:
        raise SystemExit(1)
    return report


if __name__ == "__main__":
    run()

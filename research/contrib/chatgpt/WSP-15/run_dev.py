"""Frozen WSP15 complete public DEV assay; failed hypothesis is valid output."""
import hashlib
import importlib.util
import json
import platform
import sys
import time
import tracemalloc
from pathlib import Path
from structural import (PlasticNand, PUBLIC, HIDDEN, SEEDS, TRIALS, GATES,
                        LENGTHS, context, mismatch)


def baseline_module():
    path = Path(__file__).resolve().parents[1]/"WSP-14"/"nand_program.py"
    spec = importlib.util.spec_from_file_location("wsp15_frozen_wsp14", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def examples(signature):
    return tuple((context(i), (signature >> j) & 1) for j, i in enumerate(PUBLIC))


def run():
    start = time.perf_counter()
    states = {}
    times = {}
    scores = {}
    restored_count = 0
    counts = {}
    for mode in ("plastic", "random", "disabled"):
        tick = time.perf_counter()
        score = exact = accepted = proposals = gates = scalar_ops = draws = 0
        for seed in SEEDS:
            for signature in range(32):
                obs = examples(signature)
                model = PlasticNand().learn(obs, seed, mode)
                score += 5-mismatch(model.rows, obs)
                exact += mismatch(model.rows, obs) == 0
                raw = model.snapshot()
                restored = PlasticNand.restore(raw)
                if restored.snapshot() != raw or any(restored.predict(context(i)) != model.predict(context(i)) for i in range(8)):
                    raise AssertionError("WSP15_COLD_MISMATCH")
                restored_count += mode == "plastic"
                states[mode, seed, signature] = raw
                accepted += model.accepted
                proposals += model.proposals
                gates += model.gate_evaluations
                scalar_ops += model.scalar_ops
                draws += model.noise_draws
        times[mode] = round(time.perf_counter()-tick, 6)
        scores[mode] = {"public_correct": score, "public_total": 640, "exact_signatures": exact, "signatures_total": 128}
        counts[mode] = {"accepted": accepted, "proposals": proposals, "nand_evaluations": gates, "analytical_scalar_ops": scalar_ops, "external_noise_draws": draws}
    # Independent symbolic and converged trained references. Cache setup is
    # part of measured baseline time; repeated logical worlds are not retrained.
    tick = time.perf_counter()
    ref = baseline_module()
    compiled = {}
    trained = {}
    symbolic = {}
    steps = 0
    for sig in range(32):
        obs = examples(sig)
        _, _, tree = ref.synthesize(obs)
        numeric = ref.NumericNand.from_program(tree)
        symbolic[sig] = tuple(ref.symbolic_eval(tree, context(i)) for i in range(8))
        compiled[sig] = tuple(numeric.predict(context(i)) for i in range(8))
        weights, epochs, bce = ref.fully_train_8hot(obs)
        if bce > .02 or epochs > 2048:
            raise AssertionError("WSP15_BASELINE_NOT_CONVERGED")
        trained[sig] = tuple(ref.trained_predict(weights, i) for i in range(8))
        steps += epochs
    times["symbolic_compilation_and_trained_cold_setup"] = round(time.perf_counter()-tick, 6)
    hidden = {k: 0 for k in ("plastic", "random", "disabled", "symbolic", "precompiled", "trained")}
    numeric_predictions = {}
    public_ref = {k: 0 for k in ("symbolic", "precompiled", "trained")}
    for sig in range(32):
        for i in PUBLIC:
            y = (sig >> PUBLIC.index(i)) & 1
            for name, lookup in (("symbolic", symbolic), ("precompiled", compiled), ("trained", trained)):
                public_ref[name] += lookup[sig][i] == y
    for seed in SEEDS:
        for mask in range(256):
            sig = sum(((mask >> i) & 1) << j for j, i in enumerate(PUBLIC))
            for mode in ("plastic", "random", "disabled"):
                model = PlasticNand.restore(states[mode, seed, sig])
                for i in HIDDEN:
                    hidden[mode] += model.predict(context(i)) == ((mask >> i) & 1)
            for name, lookup in (("symbolic", symbolic), ("precompiled", compiled), ("trained", trained)):
                for i in HIDDEN:
                    hidden[name] += lookup[sig][i] == ((mask >> i) & 1)
    # Byte reproducibility on one frozen signature per seed. Full independent
    # repeat is the exact-source dual-OS qualification, not this small control.
    replay = sum(PlasticNand().learn(examples(19), seed).snapshot() == states["plastic", seed, 19] for seed in SEEDS)
    mechanism = (scores["plastic"]["public_correct"] >= 608
                 and scores["plastic"]["public_correct"]-scores["random"]["public_correct"] >= 64
                 and scores["plastic"]["public_correct"]-scores["disabled"]["public_correct"] >= 64)
    required = (restored_count == 128 and replay == 4 and all(v == 1536 for v in hidden.values())
                and all(v == 160 for v in public_ref.values())
                and all(v["proposals"] == 128*TRIALS for v in counts.values())
                and sum(LENGTHS) == 75)
    digest = hashlib.sha256(b"".join(states[k] for k in sorted(states))).hexdigest()
    report = {
        "schema": "wsp15.public-dev.v1", "engineering": "PASS" if required else "FAIL",
        "frozen_mechanism_hypothesis": "DEV_SUPPORTED" if mechanism else "SCIENTIFIC_NEGATIVE",
        "scientific_superiority": "UNVERIFIED; exact symbolic public fit is an upper bound; hidden cohort is unidentifiable",
        "scores": scores, "reference_public_correct_of160": public_ref,
        "hidden_correct_of3072": hidden, "cold_restores": restored_count,
        "independent_seed_replays": replay, "state_digest_sha256": digest,
        "operations": counts, "trained_unique_signatures": 32, "trained_optimizer_steps": steps,
        "synaptic_binary_scalars": sum(LENGTHS), "checkpoint_bytes": len(next(iter(states.values()))),
        "gradient_steps_candidate": 0, "candidate_uses_external_symbolic_selection": False,
        "external_logic": "generic simulator, independent RNG proposals, validation/checkpoint/evaluator; structural search policy and NAND primitive are preprogrammed",
        "timings_seconds": times, "total_seconds": round(time.perf_counter()-start, 6),
        "environment": {"python": sys.version, "platform": platform.platform()},
        "cost_limits": "pure Python implementations and hardware dependent wall time; analytical scalar operations not hardware FLOPs; no strongest capacity/compute-matched neural control or efficiency claim",
        "first_use": "authored public DEV only"
    }
    print(json.dumps(report, sort_keys=True, indent=2))
    if not required:
        raise SystemExit(1)
    return report


if __name__ == "__main__":
    run()

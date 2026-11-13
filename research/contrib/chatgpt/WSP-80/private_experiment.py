"""WSP80 private evaluator boundary and paid-row experiment preparation.

DEVELOPMENT ONLY. No automatic registered source discovery or scientific first
use. The private source oracle is touched only by score_after_prelabel_freeze,
after the candidate and every comparator have been frozen to a SHA256 receipt.
The source-blind learners and controls never import this module.
"""
from __future__ import annotations

from hashlib import sha256
from random import Random
from time import process_time_ns
import json
import tracemalloc

import acquisition
import source
from controls import (
    ConventionalAdam384, PaidMemorization, SparsePublicControl, paid_rows,
)
from frozen_scoring import freeze_public_outputs, score_frozen
from independent_symbolic import IndependentConditionalSymbolic
from numerical_controls import FixedSparseNumeric
from structural_weights import PaidStructuralWeightEditor

DEVELOPER_ONLY = 9001


def collect_developer_sessions(world, seed=DEVELOPER_ONLY):
    """Two *independently paid* no-reset developer sessions. Never registered."""
    if (type(seed) is not int or seed != DEVELOPER_ONLY or
            type(world) is not source.World or world.seed != seed):
        raise PermissionError("registered scientific source execution not admitted")
    copies = {"candidate": world.training_session(),
              "random": world.training_session()}
    candidate = acquisition.InterventionPolicy()
    random = acquisition.UniformRandomPolicy(seed)
    editors = {key: PaidStructuralWeightEditor() for key in copies}
    stage_a_snapshot = None
    policy_cpu_ns = 0
    for i in range(source.CHARGES):
        before = copies["candidate"].current
        if i < source.STAGE_A:
            action = acquisition.stage_a_action(seed, i)
            actions = {"candidate": action, "random": action}
        else:
            t = process_time_ns()
            actions = {"candidate": candidate.choose(before),
                       "random": random.choose(copies["random"].current)}
            policy_cpu_ns += process_time_ns() - t
        observations = {name: copies[name].step(actions[name])
                        for name in copies}
        if i < source.STAGE_A and observations["candidate"] != observations["random"]:
            raise AssertionError("independently charged common StageA diverged")
        candidate.observe(observations["candidate"])
        random.observe(observations["random"])
        for name, event in observations.items():
            editors[name].charge(event.before, event.action,
                                 event.after, event.action_cost)
        if i + 1 == source.STAGE_A:
            editors["candidate"].compile()
            stage_a_snapshot = editors["candidate"].snapshot()
    if stage_a_snapshot is None or any(len(v.ledger) != 384 for v in copies.values()):
        raise AssertionError("incomplete independently paid source copies")
    return {
        "candidate_ledger": tuple(copies["candidate"].ledger),
        "random_ledger": tuple(copies["random"].ledger),
        "stage_a_snapshot": stage_a_snapshot,
        "candidate_editor": editors["candidate"],
        "random_editor": editors["random"],
        "candidate_policy_cpu_ns": policy_cpu_ns,
        "source_private_receipt": world.receipt(),
    }


def freeze_developer_models(paid, seed=DEVELOPER_ONLY, *, train_conventional=True):
    """Prelabel snapshot: only charged public rows and deterministic predictors.

    Real neural Adam fit mandatory to generate a completed scientific-quality
    comparator; caller cannot silently supply fabricated convergence claims.
    """
    if seed != DEVELOPER_ONLY:
        raise PermissionError("registered source run not admitted")
    if train_conventional is not True:
        raise ValueError("real fully trained Adam comparator required for freeze")
    ledger = paid["candidate_ledger"]
    random_ledger = paid["random_ledger"]
    paid_rows(ledger)
    paid_rows(random_ledger)
    candidate = paid["candidate_editor"]
    random_editor = paid["random_editor"]
    t = process_time_ns()
    cdiag = candidate.compile()
    rdiag = random_editor.compile()
    candidate = PaidStructuralWeightEditor.restore(candidate.snapshot())
    random = PaidStructuralWeightEditor.restore(random_editor.snapshot())
    stage_a = PaidStructuralWeightEditor.restore(paid["stage_a_snapshot"])
    fixed = FixedSparseNumeric("fixed_degree3")
    fdiag = fixed.fit(ledger)
    fixed = FixedSparseNumeric.restore(fixed.snapshot())
    always = FixedSparseNumeric("always_degree4")
    adiag = always.fit(ledger)
    always = FixedSparseNumeric.restore(always.snapshot())
    stage_a_fixed = FixedSparseNumeric("fixed_degree3")
    stage_a_fixed.fit(ledger[:144])
    stage_a_fixed = FixedSparseNumeric.restore(stage_a_fixed.snapshot())
    independent = IndependentConditionalSymbolic.from_paid_ledger(ledger)
    memory = PaidMemorization(ledger)
    sham = SparsePublicControl(ledger, mode="sham_novelty")
    compile_cpu_ns = process_time_ns() - t
    mlp = ConventionalAdam384(seed)
    t = process_time_ns()
    mlp_receipt = mlp.fit(ledger)
    mlp_train_cpu_ns = process_time_ns() - t
    stats = {"candidate_policy_cpu_ns": paid["candidate_policy_cpu_ns"],
             "candidate_train_cpu_ns": compile_cpu_ns + paid["candidate_policy_cpu_ns"],
             "candidate_infer_cpu_ns": 0,
             "MLP_train_cpu_ns": mlp_train_cpu_ns,
             "MLP_infer_cpu_ns": 0,
             "candidate_numeric_parameters": cdiag["numeric_parameters"],
             "fixed_numeric_parameters": fdiag["numeric_parameters"],
             "always_numeric_parameters": adiag["numeric_parameters"],
             "random_numeric_parameters": rdiag["numeric_parameters"],
             "MLP_numeric_parameters": 614,
             "MLP_fully_trained": mlp_receipt["fully_trained"],
             "MLP_train_exact": mlp_receipt["best_train_exact"],
             "MLP_gradient_updates_total": mlp_receipt["gradient_updates_total"],
             "MLP_restarts": mlp_receipt["restarts"],
             "MLP_trials": mlp_receipt["trials"],
             "candidate_paid_actions": 384, "random_paid_actions": 384}
    if not mlp.fully_trained:
        stats["MLP_incomplete"] = True
    predictors = {
        "candidate": candidate.predict,
        "stage_a": stage_a.predict,
        "fixed_degree3": fixed.predict,
        "always_degree4": always.predict,
        "symbolic": independent.predict,
        "paid_memory": memory.predict,
        "sham_novelty": sham.predict,
        "frozen_readout": stage_a_fixed.predict,
        "random_candidate": random.predict,
        "mlp_forced": lambda s, a: mlp.predict(s, a, confidence=False),
        "mlp_native": lambda s, a: mlp.predict(s, a, confidence=True),
    }
    def timed(name, func):
        def wrapped(s, a):
            start = process_time_ns()
            result = func(s, a)
            stats[name] += process_time_ns() - start
            return result
        return wrapped
    predictors["candidate"] = timed("candidate_infer_cpu_ns", predictors["candidate"])
    predictors["mlp_forced"] = timed("MLP_infer_cpu_ns", predictors["mlp_forced"])
    predictors["mlp_native"] = timed("MLP_infer_cpu_ns", predictors["mlp_native"])
    started = tracemalloc.is_tracing()
    if not started:
        tracemalloc.start()
    try:
        prelabel = freeze_public_outputs(ledger, predictors, mlp.winner.probability,
                                        stats)
        current, peak = tracemalloc.get_traced_memory()
        # Peak allocation is diagnostic, not a substitute for peak process RSS.
    finally:
        if not started:
            tracemalloc.stop()
    return {"prelabel": prelabel,
            "prelabel_sha256": sha256(prelabel.encode("ascii")).hexdigest(),
            "memory_peak_traced_bytes_diagnostic": peak,
            "source_private_receipt": paid["source_private_receipt"]}


def score_after_prelabel_freeze(world, frozen, seed=DEVELOPER_ONLY):
    """Private 64x6 transition and 32 compositions; callable after freeze only.

    No model, solver, or training action selector is accessed here.
    """
    if (type(world) is not source.World or world.seed != seed or
            seed != DEVELOPER_ONLY):
        raise PermissionError("protected experiment not admitted")
    envelope = frozen["prelabel"]
    if sha256(envelope.encode("ascii")).hexdigest() != frozen["prelabel_sha256"]:
        raise ValueError("prelabel receipt not frozen")
    if world.receipt() != frozen["source_private_receipt"]:
        raise ValueError("private source changed between freeze and score")
    truth = {(state, a): world._step_oracle(state, a)
             for state in source.STATES for a in source.ACTIONS}
    rng = Random(int.from_bytes(
        sha256(f"WSP80|SELFTEST|{seed}|two-action-private-32".encode("ascii")).digest(),
        "big"))
    tasks = []
    for _ in range(32):
        state = source.STATES[rng.randrange(len(source.STATES))]
        first, second = rng.randrange(6), rng.randrange(6)
        finish = world._step_oracle(world._step_oracle(state, first), second)
        tasks.append((state, first, second, finish))
    return score_frozen(envelope, truth, tuple(tasks))

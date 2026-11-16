"""WSP121 matched conventional control fixture; never original first-use."""
from __future__ import annotations

import meta_operator as M
import trained_mlp as G


def _score(predict, world):
    # Only scorer accesses the fixture gate. Learner training and selection
    # finish before any held-out oracle lookup.
    truth = [world.routes(s)[M._fixture_gate(world.feature(s))]
             for s in world.held]
    values = [predict(world, s) for s in world.held]
    return {'correct': sum(p is not None and p == y for p, y in zip(values, truth)),
            'wrong_confident': sum(p is not None and p != y for p, y in zip(values, truth)),
            'abstained': sum(p is None for p in values), 'held': len(world.held)}


def engineering_control_fixture():
    numeric, symbolic = M.NumericFastWeights(), M.SymbolicMemo()
    evidence = []
    rows = []
    for ordinal, seed in enumerate(M.ENGINEERING_SEEDS):
        world = M.engineering_world(seed)
        budget = M.FIT_BUDGET if ordinal < 2 else M.TRANSFER_BUDGET
        sources = {name: M.EvidenceSource(world, budget=budget)
                   for name in ('NUMERIC_FAST', 'SYMBOLIC_MEMO', 'TRAINED_MLP')}
        for subject in world.legal[:budget]:
            outcomes = {name: source.query(subject) for name, source in sources.items()}
            if len(set(outcomes.values())) != 1:
                raise AssertionError('WSP121_MLP_SOURCE_RESPONSE_MISMATCH')
            response = outcomes['TRAINED_MLP']
            numeric.observe(world, subject, response)
            symbolic.observe(world, subject, response)
            evidence.append((world.feature(subject), M._route_label(world, subject, response)))
        trained = G.train_conventional_mlp(tuple(evidence))
        if not trained.converged:
            raise RuntimeError('WSP121_MLP_NONCONVERGENCE_INVALID')
        if len({s.receipt for s in sources.values()}) != 1 or any(
                s.count != budget for s in sources.values()):
            raise AssertionError('WSP121_MLP_SOURCE_PARITY')
        # Every held prediction is evaluated only after fit for this world.
        predictions = trained.infer_routes(tuple(world.feature(s) for s in world.held))
        by_subject = {subject: route for subject, route in zip(world.held, predictions)}
        restore = M.NumericFastWeights.restore(numeric.snapshot())
        rows.append({
            'seed': seed, 'budget': budget,
            'source_sha256': sources['TRAINED_MLP'].receipt,
            'numeric': _score(numeric.infer, world),
            'symbolic': _score(symbolic.infer, world),
            'mlp': _score(lambda w, s: w.routes(s)[by_subject[s]]
                          if by_subject[s] is not None else None, world),
            'mlp_control': {
                'converged': trained.converged,
                'training_loss': trained.training_loss,
                'training_accuracy': trained.training_accuracy,
                'winning_seed': trained.winning_seed,
                'epochs_by_seed': trained.epochs_by_seed,
                'train_seconds': trained.wall_seconds,
                'parameter_count': trained.parameter_count,
                'parameter_bytes': trained.parameter_count * 8,  # float64
                'verified_training_examples': trained.evidence_count,
            },
            'numeric_cold_ok': all(numeric.infer(world, s) == restore.infer(world, s)
                                   for s in world.held)
        })
    return {'schema': 'wsp121.matched-mlp-engineering.v1',
            'source_first_use': False, 'scientific': False, 'native_admission': False,
            'primary_seed_accessed': False, 'rows': rows,
            'fit_evidence': 16, 'final_verified_evidence': len(evidence),
            'allowed_worlds': list(M.ENGINEERING_SEEDS)}

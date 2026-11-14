"""Cold, predeclared WSP87 relational-knowledge development comparison."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from weights import NumericKnowledge
from independent_graph import SymbolicGraph
from world import make_world, oracle

DEV_SEEDS = (12011, 12012, 12013, 12014, 12015, 12016, 12017, 12018)
FIXTURE_SEEDS = (91001, 91002)


def queries(relations, entities):
    return tuple((r, a, b, hops) for r in relations for a in entities
                 for b in entities for hops in (1, 2))


def frozen_predictions(model, items):
    return tuple(model.predict(*q) for q in items)


def digest_predictions(*bundles):
    raw = json.dumps(bundles, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


def single_world(seed):
    start = time.process_time_ns()
    world = make_world(seed)
    numeric = NumericKnowledge()
    symbolic = SymbolicGraph()
    for o in world.stage_a:
        numeric.observe(o.relation, o.source, o.target, o.present)
        symbolic.observe(o.relation, o.source, o.target, o.present)
    qa = queries(world.relations_a, world.entities_a)
    na = frozen_predictions(numeric, qa)
    sa = frozen_predictions(symbolic, qa)
    snap_a = numeric.snapshot()
    assert frozen_predictions(NumericKnowledge.restore(snap_a), qa) == na

    for o in world.stage_b:
        numeric.observe(o.relation, o.source, o.target, o.present)
        symbolic.observe(o.relation, o.source, o.target, o.present)
    qb = queries(world.relations_b, world.entities_b)
    nb = frozen_predictions(numeric, qb)
    sb = frozen_predictions(symbolic, qb)
    snap_b = numeric.snapshot()
    cold = NumericKnowledge.restore(snap_b)
    assert frozen_predictions(cold, qb) == nb
    unknown = "unseen-name-not-in-world"
    unknown_answers = (cold.predict(world.relations_b[0], unknown,
                                    world.entities_b[0], 1),
                       cold.predict(unknown, world.entities_b[0],
                                    world.entities_b[1], 2))
    assert unknown_answers == (None, None)
    frozen_sha = digest_predictions(na, sa, nb, sb, unknown_answers)

    # Only now may the evaluator inspect world truth.
    ta = tuple(oracle(world.truth_a, *q) for q in qa)
    tb = tuple(oracle(world.truth_b, *q) for q in qb)
    parity = (na == sa and nb == sb)
    old = {q: (truth, pred) for q, truth, pred in zip(qa, ta, na)}
    later = dict(zip(qb, nb))
    retained = [q for q, (truth, pred) in old.items()
                if truth and pred and oracle(world.truth_b, *q)]
    retained_correct = sum(later[q] is True for q in retained)
    retracted = [o for o in world.stage_b if not o.present]
    edits_correct = sum(cold.predict(o.relation, o.source, o.target, 1) is False
                        for o in retracted)
    novel_two_hop = sum(bool(pred) and truth and
                        not oracle(world.truth_b, r, a, b, 1)
                        for (r, a, b, hops), pred, truth in zip(qb, nb, tb)
                        if hops == 2)

    # Native literal lookup has no two-hop composition and must not be promoted
    # as equivalent when its one-hop lookup happens to collide with a 2-hop query.
    literal_two_hop_correct = sum(
        (symbolic.predict(r, a, b, 1) == truth)
        for (r, a, b, hops), truth in zip(qb, tb) if hops == 2
    )
    zeroed = NumericKnowledge.restore(snap_b)
    for m in zeroed.weights.values():
        for row in m:
            for j in range(len(row)):
                row[j] = 0.0
    positive_example = next(q for q, truth in zip(qb, tb)
                            if q[-1] == 2 and truth)
    assert zeroed.predict(*positive_example) is False

    import copy
    corrupted = json.loads(snap_b)
    corrupted["payload"]["weights"][world.relations_b[0]][0][0] = 3.0
    tamper_rejected = False
    try:
        NumericKnowledge.restore(json.dumps(corrupted))
    except ValueError:
        tamper_rejected = True

    return {
        "seed": seed,
        "stageA_total": len(qa),
        "stageA_correct": sum(x == y for x, y in zip(na, ta)),
        "stageB_total": len(qb),
        "stageB_correct": sum(x == y for x, y in zip(nb, tb)),
        "stageB_symbolic_correct": sum(x == y for x, y in zip(sb, tb)),
        "symbolic_parity": parity,
        "unseen_true_two_hop_correct": novel_two_hop,
        "old_true_unaffected_total": len(retained),
        "old_true_unaffected_retained": retained_correct,
        "retractions_total": len(retracted),
        "retractions_correct": edits_correct,
        "unknown_confident": sum(v is not None for v in unknown_answers),
        "tamper_rejected": tamper_rejected,
        "literal_two_hop_correct": literal_two_hop_correct,
        "literal_two_hop_total": len(qb) // 2,
        "numeric_weight_count": sum(len(m) * len(m) for m in cold.weights.values()),
        "stageA_weight_snapshot_sha256": hashlib.sha256(snap_a.encode()).hexdigest(),
        "stageB_weight_snapshot_sha256": hashlib.sha256(snap_b.encode()).hexdigest(),
        "all_predictions_frozen_before_labels_sha256": frozen_sha,
        "whole_portfolio_process_cpu_ns": time.process_time_ns() - start,
    }


def classify(rows, dev=False):
    a_total = sum(r["stageA_total"] for r in rows)
    b_total = sum(r["stageB_total"] for r in rows)
    retained = sum(r["old_true_unaffected_total"] for r in rows)
    removed = sum(r["retractions_total"] for r in rows)
    novel = sum(r["unseen_true_two_hop_correct"] for r in rows)
    checks = {
        "stageA_99pct": sum(r["stageA_correct"] for r in rows) / a_total >= .99,
        "stageB_99pct": sum(r["stageB_correct"] for r in rows) / b_total >= .99,
        "independent_symbolic_parity": all(r["symbolic_parity"] for r in rows),
        "unseen_true_two_hop_100": novel >= 100 if dev else novel >= 20,
        "unaffected_old_retention_100pct": retained > 0 and
            sum(r["old_true_unaffected_retained"] for r in rows) == retained,
        "retractions_100pct": removed > 0 and
            sum(r["retractions_correct"] for r in rows) == removed,
        "no_unknown_confident": all(r["unknown_confident"] == 0 for r in rows),
        "cold_tamper_refused": all(r["tamper_rejected"] for r in rows),
        "whole_cpu_accounted": all(r["whole_portfolio_process_cpu_ns"] > 0 for r in rows)
    }
    return {
        "schema": "wsp87.direct-relational-knowledge-dev-result.v1",
        "cohort": "UNREGISTERED_DEV" if dev else "PUBLIC_STRUCTURAL_FIXTURE",
        "classification": ("DEV_SUBSTRATE_FEASIBLE" if all(checks.values())
                           else "DEV_SUBSTRATE_NEGATIVE"),
        "checks": checks,
        "stageA_correct": sum(r["stageA_correct"] for r in rows),
        "stageA_total": a_total,
        "stageB_correct": sum(r["stageB_correct"] for r in rows),
        "stageB_total": b_total,
        "novel_true_two_hop_correct": novel,
        "old_true_unaffected_retained": sum(r["old_true_unaffected_retained"] for r in rows),
        "old_true_unaffected_total": retained,
        "full_portfolio_cpu_ns": sum(r["whole_portfolio_process_cpu_ns"] for r in rows),
        "symbolic_superiority_claim": False,
        "scientific_acceptance": "UNVERIFIED",
        "language_or_general_intelligence_proven": False,
        "deployment": "NONE",
        "trials": rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen-unregistered-dev-only", action="store_true")
    parser.add_argument("--structural-fixtures-only", action="store_true")
    args = parser.parse_args()
    if args.frozen_unregistered_dev_only == args.structural_fixtures_only:
        parser.error("select exactly one explicit isolated cohort")
    seeds = DEV_SEEDS if args.frozen_unregistered_dev_only else FIXTURE_SEEDS
    result = classify([single_world(seed) for seed in seeds],
                      dev=args.frozen_unregistered_dev_only)
    print("WSP87_DEV_RESULT=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

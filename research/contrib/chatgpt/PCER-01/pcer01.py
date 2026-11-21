"""PCER-01: read-only active replay INDEX over archived Amalgam witness evidence.

This does not train, restart, prune, or modify NativeCausalAmalgam. The input
is the existing selection_trial.py trace of source-witnessed native predictions.
Selected IDs reference original losslessly retained evidence. Historical
synthetic development is NOT fresh unfamiliar-family science.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import json
import random

SCALE = 1_000_000
EXPERIMENT = "PCER-01"
QUOTAS = (7, 2, 1)
TRACE_COUNT = 96
FIT_END = 50
VALID_END = 64


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def hex_digest(raw):
    return sha256(raw).hexdigest()


def _bit(value):
    if type(value) is not int or value not in (0, 1):
        raise ValueError("PCER_BIT")
    return value


def validate_trace(rows):
    """Source shape, identifiers, prequential prediction and phase boundaries."""
    if type(rows) is not list or len(rows) != TRACE_COUNT:
        raise ValueError("PCER_SOURCE_EPISODE_COUNT")
    ids = set()
    for i, entry in enumerate(rows):
        if type(entry) is not dict or set(entry) != {
                "id", "phase", "origin", "views", "row", "prediction"}:
            raise ValueError("PCER_SOURCE_ROW_SHAPE")
        ident = entry["id"]
        if (type(ident) is not str or len(ident) != 64 or
                any(c not in "0123456789abcdef" for c in ident) or ident in ids):
            raise ValueError("PCER_IDENTITY_OR_DUPLICATE")
        ids.add(ident)
        if entry["phase"] != i // 32:
            raise ValueError("PCER_PHASE_ORDER")
        views = entry["views"]
        if (type(views) is not list or len(views) != 2 or
                any(type(v) is not list or len(v) != 2 for v in views)):
            raise ValueError("PCER_PUBLIC_VIEWS")
        _bit(views[0][0])
        if views[1][0] != views[0][0]:
            raise ValueError("PCER_PAIRED_PUBLIC_CONTEXT")
        row = entry["row"]
        if type(row) is not dict or set(row) != {"s1", "x1", "s2", "x2", "y"}:
            raise ValueError("PCER_PUBLIC_OUTCOME_ROW")
        for field in ("s1", "x1", "s2", "x2", "y"):
            _bit(row[field])
        if row["s1"] != views[0][0]:
            raise ValueError("PCER_CONTEXT_INCONSISTENT")
        pred = entry["prediction"]
        if type(pred) is not dict or type(pred.get("native")) is not int:
            raise ValueError("PCER_PREQUENTIAL_PREDICTION")
        if not 0 <= pred["native"] <= SCALE:
            raise ValueError("PCER_PREDICTION_RANGE")


def _key(entry):
    return (entry["views"][0][0], entry["row"]["x1"])


def _surprise(entry):
    """Squared residual of the archived native PRE-outcome transition forecast."""
    return (entry["prediction"]["native"] -
            SCALE * entry["row"]["s2"]) ** 2


def _uniform_key(entry):
    return (hex_digest(("PCER-01|24011|" + entry["id"]).encode("ascii")),
            entry["id"])


def pick(rows, arm):
    """Return chosen FIT rows in original chronological order, not rank order."""
    if len(rows) != FIT_END or len({r["id"] for r in rows}) != FIT_END:
        raise ValueError("PCER_FIT_CAPACITY_OR_ID")
    if arm == "full":
        return list(rows)
    if arm not in ("pcer", "uniform", "error"):
        raise ValueError("PCER_ARM")
    by_id = {r["id"]: r for r in rows}
    if arm == "uniform":
        selected = {r["id"] for r in sorted(rows, key=_uniform_key)[:10]}
    elif arm == "error":
        selected = {r["id"] for r in sorted(
            rows, key=lambda r: (-_surprise(r), r["id"]))[:10]}
    else:
        high, coverage, uniform = QUOTAS
        selected = {r["id"] for r in sorted(
            rows, key=lambda r: (-_surprise(r), r["id"]))[:high]}
        frequencies = Counter(_key(r) for r in rows)
        for _ in range(coverage):
            retained_keys = {_key(by_id[i]) for i in selected}
            candidates = [r for r in rows if r["id"] not in selected]
            chosen = min(candidates, key=lambda r: (
                _key(r) in retained_keys, frequencies[_key(r)], r["id"]))
            selected.add(chosen["id"])
        candidates = [r for r in rows if r["id"] not in selected]
        selected.update(r["id"] for r in sorted(candidates, key=_uniform_key)[:uniform])
    expected = FIT_END if arm == "full" else 10
    if len(selected) != expected:
        raise ValueError("PCER_SELECTION_QUOTA")
    return [r for r in rows if r["id"] in selected]


def fitted_predictor(chosen):
    """Fully fitted Beta(1,1) cell estimator; NOT the Amalgam native model."""
    counts = defaultdict(lambda: [0, 0])
    for r in chosen:
        cell = counts[_key(r)]
        cell[0] += r["row"]["s2"]
        cell[1] += 1
    return {key: (ones + 1) / (count + 2)
            for key, (ones, count) in counts.items()}


def score(model, rows):
    probabilities = [model.get(_key(r), 0.5) for r in rows]
    return [(p - r["row"]["s2"]) ** 2
            for r, p in zip(rows, probabilities, strict=True)]


def _bootstrap(deltas, seed, repetitions=2000):
    rng = random.Random(seed)
    n = len(deltas)
    values = sorted(
        sum(deltas[rng.randrange(n)] for _ in range(n)) / n
        for _ in range(repetitions)
    )
    return {"seed": seed, "mean": sum(values) / len(values),
            "q025": values[49], "q975": values[1949]}


def analyze(rows, source_sha256, prereg_sha256):
    validate_trace(rows)
    fit = rows[:FIT_END]
    evaluation = {"valid": rows[FIT_END:VALID_END],
                  "return_held": rows[VALID_END:]}
    arms = {a: pick(fit, a) for a in ("full", "uniform", "error", "pcer")}
    models = {a: fitted_predictor(chosen) for a, chosen in arms.items()}
    selected = {a: [r["id"] for r in chosen] for a, chosen in arms.items()}
    metrics = {}
    accepted = True
    for name, slice_rows in evaluation.items():
        loss_vectors = {a: score(model, slice_rows) for a, model in models.items()}
        means = {a: sum(losses) / len(losses) for a, losses in loss_vectors.items()}
        deltas = [p - f for p, f in zip(loss_vectors["pcer"], loss_vectors["full"], strict=True)]
        bounded_min = min(means["uniform"], means["error"])
        eligible = (means["pcer"] - means["full"] <= 0.02 + 1e-12 and
                    means["pcer"] <= bounded_min - 0.005 + 1e-12)
        accepted &= eligible
        metrics[name] = {
            "rows": len(slice_rows), "brier": means,
            "pcer_minus_full": means["pcer"] - means["full"],
            "bounded_best": min(("uniform", "error"), key=lambda a: (means[a], a)),
            "pcer_minus_best_bounded": means["pcer"] - bounded_min,
            "frozen_gate_met": eligible,
            "paired_bootstrap_delta": [_bootstrap(deltas, s) for s in (24011, 24029, 24041)],
        }
    manifest = {"schema": "yggdrasil.pcer01.active-index.v1",
                "source_sha256": source_sha256,
                "prereg_sha256": prereg_sha256,
                "fit_count": FIT_END, "selected": selected["pcer"],
                "all_source_rows_retained": True}
    manifest_sha = hex_digest(canonical(manifest))
    report = {"schema": "yggdrasil.pcer01.dev-result.v1",
              "experiment_id": EXPERIMENT, "source_sha256": source_sha256,
              "prereg_sha256": prereg_sha256, "original_count": len(rows),
              "fit_count": FIT_END, "active_count": len(arms["pcer"]),
              "active_slot_reduction": 1 - len(arms["pcer"]) / FIT_END,
              "original_source_mutated": False, "arms": {k: len(v) for k, v in arms.items()},
              "active_index_sha256": manifest_sha,
              "scoring": metrics,
              "exploratory_result": "SURROGATE_SUPPORT" if accepted else "DEV_NO_GO",
              "scientific_native_gain": "UNVERIFIED",
              "unfamiliar_family_transfer": "UNVERIFIED",
              "cold_native_restoration": "UNVERIFIED",
              "research_only": True}
    return manifest, report


def cold_verify(rows, source_sha256, prereg_sha256, manifest):
    """Recompute selection independently; reject a changed source/index."""
    original, _ = analyze(rows, source_sha256, prereg_sha256)
    if original != manifest:
        raise ValueError("PCER_COLD_INDEX_DIVERGENCE")
    return True


def run(trace, prereg, manifest_path, report_path):
    raw = Path(trace).read_bytes()
    frozen = Path(prereg).read_bytes()
    protocol = json.loads(frozen)
    expected = protocol["inputs"][0]["sha256"]
    source_sha = hex_digest(raw)
    if source_sha != expected or protocol["experiment_id"] != EXPERIMENT:
        raise ValueError("PCER_SOURCE_OR_PROTOCOL_PIN")
    rows = json.loads(raw)
    manifest, report = analyze(rows, source_sha, hex_digest(frozen))
    cold_verify(json.loads(Path(trace).read_bytes()), source_sha, hex_digest(frozen), manifest)
    if hex_digest(Path(trace).read_bytes()) != source_sha:
        raise ValueError("PCER_ORIGINAL_EVIDENCE_CHANGED")
    for path, obj in ((manifest_path, manifest), (report_path, report)):
        out = Path(path)
        if out.exists():
            raise ValueError("PCER_OUTPUT_EXISTS")
        out.write_bytes(canonical(obj))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--prereg", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    a = parser.parse_args()
    print(json.dumps(run(a.trace, a.prereg, a.manifest, a.report),
                     sort_keys=True, indent=2))

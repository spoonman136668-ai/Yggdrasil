"""CAP04 RD06 bounded source-only *retrospective* identifiability proof.

No new training, native model, original-world action, controller, source first use
or scientific PASS. Protocol RD06-FROZEN-IDENTIFIABILITY-CERTIFICATE.md was
committed independently before this analysis or its outcome was calculated.
"""
from __future__ import annotations

import ast
from collections import defaultdict
from fractions import Fraction
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE_FILE = HERE / "rd05_source_support.py"
RD04_FILE = HERE / "rd04_engineering.py"
MODEL_FILE = ROOT / "yggdrasil/native_predictive_state_split.py"
SCHEMA = "yggdrasil.cap04.rd06.retrospective-static-key-proof.v1"
FROZEN = "research/contrib/chatgpt/YGG-CAP04/RD06-FROZEN-IDENTIFIABILITY-CERTIFICATE.md"

_spec = importlib.util.spec_from_file_location("rd05_source_only", SOURCE_FILE)
_source = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_source)
SOURCES = _source.SOURCES
SOURCE_PINS = _source.EXPECTED_SOURCE
canonical = _source.canonical
digest = _source.sha


def require(ok, name):
    if not ok:
        raise ValueError("CAP04_RD06_" + name)


def fixed_rows(name):
    """Regenerate exclusively original already-scored public observations."""
    require(type(name) is str and name in SOURCES, "UNKNOWN_SOURCE")
    original = _source.source(name)
    require(len(original) == 256 and
            digest(canonical(original)) == SOURCE_PINS[name],
            "SOURCE_DRIFT")
    return original


def keyed(rows):
    previous = (0, 0)
    result = []
    for t, row in enumerate(rows):
        views = row["views"]
        require(views[0][1] == views[1][0], "BAD_PUBLIC_VIEW")
        st = (views[0][0], views[0][1], views[1][1])
        key = (st, row["action"], row["s2"], previous)
        # Published witness ID and actual observed reward only.
        result.append({"t": t, "key": key,
                       "y": row["y"], "witness_id": row["id"]})
        previous = row["action"]
    return tuple(result)


def fraction_receipt(x: Fraction):
    require(isinstance(x, Fraction) and x >= 0, "FRACTION")
    return {"numerator": x.numerator, "denominator": x.denominator,
            "value": float(x)}


def minimize(samples, *, phase_oracle=False):
    """Exact best retrospective STATIC Bernoulli lookup (not online model)."""
    counts = defaultdict(lambda: [0, 0])
    ids = defaultdict(list)
    for event in samples:
        t = event["t"]
        phase = 0 if t < 64 else 1 if t < 192 else 2
        group = (phase, event["key"]) if phase_oracle else event["key"]
        counts[group][event["y"]] += 1
        ids[group].append(event)
    total = len(samples)
    require(total in (192, 256), "SAMPLE_COUNT")
    # argmin of n0*p² + n1*(1-p)² is p = n1 / (n0+n1).
    loss = sum((Fraction(n0*n1, n0+n1)
                for n0, n1 in counts.values()), Fraction())
    det_err = sum(min(n0, n1) for n0,n1 in counts.values())
    conflicting = [g for g,(n0,n1) in counts.items() if n0 and n1]
    conflicts_rows = sum(sum(counts[g]) for g in conflicting)
    # Independent exact verification of the closed-form p* minimizing
    # quadratic Brier vs either constant end-point p=0 or 1.
    for n0,n1 in counts.values():
        p = Fraction(n1, n0+n1)
        own = n0*p*p+n1*(1-p)*(1-p)
        require(own == Fraction(n0*n1,n0+n1) and
                own <= n0 and own <= n1, "STATIC_OPTIMUM")
    examples = []
    for group in sorted(conflicting, key=str)[:3]:
        off = next(x for x in ids[group] if x["y"]==0)
        on = next(x for x in ids[group] if x["y"]==1)
        require(off["key"] == on["key"] and
                off["witness_id"] != on["witness_id"], "WITNESS_PAIR")
        examples.append({"identical_public_and_one_lag_key": off["key"],
                         "witness_0": {"t": off["t"], "id": off["witness_id"]},
                         "witness_1": {"t": on["t"], "id": on["witness_id"]}})
    return {
        "n": total, "unique_keys": len(counts),
        "conflicting_key_count": len(conflicting),
        "rows_on_conflicting_keys": conflicts_rows,
        "static_bernoulli_minimum_brier": fraction_receipt(loss / total),
        "static_deterministic_minimum_errors": det_err,
        "witnessed_opposition_examples": examples,
        "unlearned_p_half_brier": fraction_receipt(Fraction(1, 4)),
    }


def probe_conflicts(samples):
    """Original familiar A-prefix query historical tuples, source-only."""
    prefix = samples[:16]
    b = samples[64:192]
    contrary = {e["key"] for e in b if e["y"] == 1}
    # Familiar A y=s2, so ordinary label can be 0 or 1. Compare actual
    # opposite outcome *for the identical full observed public key*.
    opposing = {(e["key"],e["y"]) for e in b}
    affected = [e for e in prefix if (e["key"],1-e["y"]) in opposing]
    return {"probe_count":16,
            "probe_rows_with_opposite_later_b_label":len(affected),
            "distinct_probe_keys_with_opposite_later_b_label":
                len({e["key"] for e in affected}),
            "all_probe_keys_original_previous_action_preserved":True}


def probe_interface_audit():
    """Read source only: fixed views/action/s2 aren't fixed history inputs."""
    src = ast.parse(RD04_FILE.read_text(encoding="utf-8"))
    model = ast.parse(MODEL_FILE.read_text(encoding="utf-8"))
    funcs = {f.name:f for f in src.body if isinstance(f,ast.FunctionDef)}
    require("old_skill_queries" in funcs and "checkpoint" in funcs,
            "RD04_PROBE_SOURCE")
    old = ast.unparse(funcs["old_skill_queries"])
    require("model.forecast(views, action, 'residual', s2)" in old,
            "RD04_PROBE_SIGNATURE")
    classes=[f for f in model.body if isinstance(f,ast.ClassDef)
             and f.name=="PredictiveStateSplit"]
    require(len(classes)==1,"MODEL_CLASS")
    methods={f.name:f for f in classes[0].body
             if isinstance(f,ast.FunctionDef)}
    require("_feature_values" in methods and "forecast" in methods,
            "MODEL_HISTORY_READER")
    features=ast.unparse(methods["_feature_values"])
    forecast=ast.unparse(methods["forecast"])
    require("self._events[-lag]" in features and
            "self._feature_values()" in forecast,
            "HISTORY_CONTEXT_SOURCE")
    return {
        "source_only":True,
        "old_probe_supplies_only":"views,action,s2",
        "lagged_context_inference":"current_learner_events_not_original_query_event",
        "complete_history_input_frozen":False,
        "retention_claim_limit":
            "old_A_probe_drift_alone_cannot_distinguish_forgetting_from_changed_history_context",
    }


def certificate(name):
    events = keyed(fixed_rows(name))
    first_192=events[:192]
    full=events
    prefix=minimize(first_192)
    entire=minimize(full)
    oracle_192=minimize(first_192,phase_oracle=True)
    oracle_full=minimize(full,phase_oracle=True)
    probe = probe_conflicts(events)
    cls=("STATIC_KEY_INSUFFICIENT"
         if prefix["conflicting_key_count"] and
         prefix["static_bernoulli_minimum_brier"]["numerator"]
         else "NO_STATIC_KEY_CONFLICT_FOUND")
    # It is a deterministic phase-specific synthetic source; the oracle
    # must be internally consistent. It is NOT an available learner.
    require(oracle_192["conflicting_key_count"] == 0 and
            oracle_full["conflicting_key_count"] == 0,
            "PHASE_ORACLE_CONTRADICTORY")
    require(all(x["static_bernoulli_minimum_brier"]["denominator"]>0
                for x in (prefix,entire,oracle_192,oracle_full)),
            "INVALID_FRACTION")
    return {"schema":SCHEMA,"evidence_class":"POSTHOC_SYNTHETIC_ONLY",
            "source":name,"original_source_sha256":SOURCE_PINS[name],
            "source_events":256, "registered_source_first_use":False,
            "original_model_read_or_modified":False,
            "phase_is_evaluator_only":True,
            "pre_return_a_b":prefix,
            "full_a_b_a":entire,
            "unavailable_phase_tag_oracle_a_b":oracle_192,
            "unavailable_phase_tag_oracle_a_b_a":oracle_full,
            "historical_old_a_probe_conflict":probe,
            "old_probe_context_limit":probe_interface_audit(),
            "classification":cls, "scientific_pass":False,
            "canonical_model_modified":False}


def audit(raw):
    """Recompute from original witnessed source, reject forged reports."""
    require(type(raw) is bytes and len(raw) < 80000, "AUDIT_SIZE")
    try:
        doc = json.loads(raw.decode("ascii"))
        require(type(doc) is dict and canonical(doc)==raw and
                doc.get("schema")==SCHEMA and
                doc.get("scientific_pass") is False and
                doc.get("canonical_model_modified") is False and
                doc.get("phase_is_evaluator_only") is True and
                doc.get("registered_source_first_use") is False,
                "AUDIT_SCOPE")
        require(canonical(certificate(doc["source"]))==raw,
                "AUDIT_REPLAY")
        return {"source":doc["source"],
                "source_sha256":doc["original_source_sha256"],
                "receipt_sha256":digest(raw),
                "classification":doc["classification"],
                "pre_return_a_b":doc["pre_return_a_b"],
                "full_a_b_a":doc["full_a_b_a"],
                "unavailable_phase_tag_oracle_a_b":
                    doc["unavailable_phase_tag_oracle_a_b"],
                "historical_old_a_probe_conflict":
                    doc["historical_old_a_probe_conflict"],
                "old_probe_context_limit":doc["old_probe_context_limit"],
                "scientific_pass":False}
    except (KeyError, ValueError, TypeError, OverflowError,
            ZeroDivisionError, UnicodeError, IndexError) as e:
        raise ValueError("CAP04_RD06_DIAGNOSTIC_INVALID") from e


if __name__ == "__main__":
    for name in SOURCES:
        report=certificate(name)
        print("CAP04_RD06_CERTIFICATE="+canonical(
            audit(canonical(report))).decode("ascii"), flush=True)

"""CKAD40: DEV-only archive-coverage, identifiability, and oracle-ceiling audit.

Native model is a single continuously trained NativeEpisodeExperience.
True regime labels ONLY reach this diagnostic evaluator for archive purity and
an intentionally non-deployable oracle ceiling; not the native model or source.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "CKAD-39"
sys.path.insert(0, str(PARENT))
spec = importlib.util.spec_from_file_location("ckad39_source_for_40", PARENT / "campaign.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

SCHEMA = "yggdrasil.ckad40.archive-identifiability-dev.v1"
PREREG = "d38ba4e7c438b0a2eb89bf08cd5f54e6ff0fe2e3"
DEV = (40811, 40812)
RESERVED = (41811, 41812, 42811, 42812, 42813)
WINDOW = 16
LATE = ("late_B", "late_return_A")
REGIME_A = ("warm", "stable_A", "early_return_A", "late_return_A")
REGIME_B = ("early_B", "late_B")
CONVENTIONAL = (*C.CONVENTIONAL, "beta_hedge")
ARMS = ("native_stream", "phase_oracle", *CONVENTIONAL)


def source_regime(phase):
    if phase in REGIME_A:
        return "A"
    if phase in REGIME_B:
        return "B"
    raise ValueError("CKAD40_INVALID_PHASE")


def eligible_archive(native, witnessed):
    """Return labelled immutable archive blocks, using EVALUATOR labels only.

    The live novel hypothesis, mixed A/B blocks, unobserved future source
    ranges, and sources overlapping the 16-event evidence window are excluded.
    Not a deployable selector.
    """
    groups = {"A": [], "B": []}
    if native._context_start is None:
        return groups
    for start, stop, _, old_model in native._context_models:
        if not (stop > start and stop - start >= 8
                and stop <= native._context_start and stop <= len(witnessed) - WINDOW):
            continue
        labels = {source_regime(witnessed[i][3]) for i in range(start, stop)}
        if len(labels) == 1:
            groups[labels.pop()].append(old_model)
    return groups


def event_likelihood(model, event):
    _, views, row, _ = event
    p = float(model.forecast(views[0], row["x1"]))
    q = float(model.forecast(views[0], row["x1"], row["s2"], row["x2"]))
    if not (0 < p < 1 and 0 < q < 1):
        raise ValueError("CKAD40_NONPOSITIVE_EVENT_LIKELIHOOD")
    return (p if row["s2"] else 1-p) * (q if row["y"] else 1-q)


def history_logevidence(sources, already_witnessed):
    if len(already_witnessed) != WINDOW or not sources:
        raise ValueError("CKAD40_INVALID_EVIDENCE_WINDOW")
    # Each archived model is equally weighted for each genuine previous event.
    # No phase/label or future reward is accessed inside this likelihood.
    return sum(math.log(sum(event_likelihood(m, e) for m in sources)
                        / len(sources)) for e in already_witnessed)


def source_forecast(sources, view, first, next_state=None, second=None):
    """Archive mean, terminal-conditioned on the ALREADY witnessed transition."""
    if not sources:
        raise ValueError("CKAD40_EMPTY_SOURCE_CLASS")
    p = sum(float(m.forecast(view, first)) for m in sources) / len(sources)
    if next_state is None:
        return p
    weights = [(float(m.forecast(view, first)) if next_state
                else 1-float(m.forecast(view, first))) for m in sources]
    total = sum(weights)
    if total <= 0:
        raise ValueError("CKAD40_INVALID_TERMINAL_WEIGHT")
    return sum(w * float(m.forecast(view, first, next_state, second))
               for w, m in zip(weights, sources)) / total


def brier(p, q, row):
    return ((p-row["s2"])**2 + (q-row["y"])**2) / 2


def case(seed):
    if seed not in DEV:
        raise ValueError("CKAD40_ONLY_REGISTERED_DEV")
    started = time.perf_counter()
    worlds = []
    scored = []
    for world in C.WORLDS:
        events, meta = C.generator(seed, world)
        native = NativeEpisodeExperience(repair=True)
        baseline = C.Conventional()
        source_ids = set()
        archive_prefix = None
        audit_rows = []
        read_checks = 0
        for t, event in enumerate(events):
            identifier, views, row, phase = event
            if t == 48:
                native = native.begin_stream()
                archive_prefix = digest(canonical(native._ledger[:48]))
            view = views[0]
            if t >= 48:
                p0 = float(native.context_forecast(view, row["x1"]))
                q0 = float(native.context_forecast(view, row["x1"],
                                                  row["s2"], row["x2"]))
            else:
                p0 = float(native.forecast(view, row["x1"]))
                q0 = float(native.forecast(view, row["x1"], row["s2"], row["x2"]))
            losses = {}
            for arm in CONVENTIONAL:
                p = baseline.p(arm, "transition", row["s1"], row["x1"])
                q = baseline.p(arm, "terminal", row["s1"], row["x1"],
                               row["s2"], row["x2"])
                losses[arm] = brier(p, q, row)
            if phase in LATE:
                groups = eligible_archive(native, events[:t])
                covered = bool(groups["A"] and groups["B"])
                rec = {"seed": seed, "world": world, "t": t, "phase": phase,
                       "regime": source_regime(phase), "covered": covered,
                       "a_blocks": len(groups["A"]), "b_blocks": len(groups["B"])}
                if covered:
                    # Only the already witnessed 16 events are evidence.
                    previous = events[t-WINDOW:t]
                    if len(previous) != WINDOW or any(e[0] not in source_ids for e in previous):
                        raise AssertionError("CKAD40_FUTURE_OR_UNSEEN_EVIDENCE")
                    checkpoint = native.checkpoint()
                    scores = {regime: history_logevidence(blocks, previous)
                              for regime, blocks in groups.items()}
                    picked = max(("A", "B"), key=lambda label: scores[label])
                    rec["correct"] = scores["A"] != scores["B"] and picked == rec["regime"]
                    true_sources = groups[rec["regime"]]  # EVALUATOR-ONLY oracle ceiling
                    po = source_forecast(true_sources, view, row["x1"])
                    qo = source_forecast(true_sources, view, row["x1"],
                                         row["s2"], row["x2"])
                    rec["losses"] = {"native_stream": brier(p0, q0, row),
                                     "phase_oracle": brier(po, qo, row),
                                     **losses}
                    rec["evidence_margin_for_true_class"] = (scores[rec["regime"]] -
                                        scores["B" if rec["regime"] == "A" else "A"])
                    if native.checkpoint() != checkpoint:
                        raise AssertionError("CKAD40_ARCHIVE_READ_MUTATED_CHECKPOINT")
                    read_checks += 1
                audit_rows.append(rec)
            # All independently trained models see exactly the same genuine
            # consequences, AFTER the forecast and eligibility test.
            native = native.observe(identifier, views, row)
            baseline.observe(row, losses)
            if identifier in source_ids:
                raise AssertionError("CKAD40_DUPLICATE_SOURCE")
            source_ids.add(identifier)
        if len(native._ledger) != len(events) or len(native._ids) != len(events):
            raise AssertionError("CKAD40_INCOMPLETE_NATIVE_LEDGER")
        if digest(canonical(native._ledger[:48])) != archive_prefix:
            raise AssertionError("CKAD40_WARM_SOURCE_ERASED")
        snapshot = native.checkpoint()
        restored = NativeEpisodeExperience.restore(snapshot, digest(snapshot))
        if restored.checkpoint() != snapshot:
            raise AssertionError("CKAD40_COLD_RESTORE_DRIFT")
        identifier, views, row, _ = events[-1]
        if native.observe(identifier, views, row) is not native:
            raise AssertionError("CKAD40_DUPLICATE_NOT_IDEMPOTENT")
        bad_row = dict(row)
        bad_row["y"] ^= 1
        try:
            native.observe(identifier, views, bad_row)
        except ValueError:
            pass
        else:
            raise AssertionError("CKAD40_CONFLICTING_SOURCE_ACCEPTED")
        if native.checkpoint() != snapshot:
            raise AssertionError("CKAD40_CONFLICT_MUTATED_LEARNER")
        worlds.append({"world": world, "authentic_episodes": len(events),
                       "authentic_consequences": 2 * len(events),
                       "source_complete": True, "cold_exact": True,
                       "conflict_atomic": True, "old_source_preserved": True,
                       "read_only_checks": read_checks,
                       "final_checkpoint_sha256": digest(snapshot),
                       "evaluator_private_boundaries": meta})
        scored.extend(audit_rows)
    total = len(scored)
    covered_rows = [r for r in scored if r["covered"]]
    count = len(covered_rows)
    sums = {arm: sum(r["losses"][arm] for r in covered_rows) / count if count
            else None for arm in ARMS}
    control = min((sums[arm] for arm in CONVENTIONAL), default=None) if count else None
    gain_native = sums["native_stream"]-sums["phase_oracle"] if count else None
    gain_conventional = control-sums["phase_oracle"] if count else None
    phase = {}
    for name in LATE:
        these = [r for r in scored if r["phase"] == name]
        selected = [r for r in these if r["covered"]]
        phase[name] = {"episodes": len(these), "covered": len(selected),
                       "correct": sum(r["correct"] for r in selected),
                       "accuracy": (sum(r["correct"] for r in selected)/len(selected)
                                    if selected else None)}
    correct = sum(r["correct"] for r in covered_rows)
    return {"seed": seed, "worlds": worlds, "late_episodes": total,
            "late_covered": count, "coverage": count/total if total else 0,
            "evidence_correct": correct, "evidence_accuracy": correct/count if count else 0,
            "phase": phase, "oracle_brier": sums["phase_oracle"],
            "native_brier": sums["native_stream"],
            "strongest_conventional_brier": control,
            "strongest_conventional_arm": (min(CONVENTIONAL, key=lambda a: sums[a])
                                           if count else None),
            "oracle_gain_vs_native": gain_native,
            "oracle_gain_vs_conventional": gain_conventional,
            "source_model_count": sum(w["authentic_episodes"] for w in worlds),
            "source_read_checks": sum(w["read_only_checks"] for w in worlds),
            "elapsed_wall_seconds": round(time.perf_counter() - started, 5)}


def classify(cases):
    if tuple(x["seed"] for x in cases) != DEV:
        raise AssertionError("CKAD40_FROZEN_DEV_IDENTITY")
    if not all(all(w["source_complete"] and w["cold_exact"] and
                   w["old_source_preserved"] and w["conflict_atomic"]
                   for w in case["worlds"]) for case in cases):
        return "INVALID_SOURCE"
    if not all(x["late_covered"] >= 64 and x["coverage"] >= .50 for x in cases):
        return "ARCHIVE_COVERAGE_GAP"
    if not all(x["evidence_accuracy"] >= .65 for x in cases):
        return "IDENTIFICATION_GAP"
    if not all(x["oracle_gain_vs_native"] >= .015 and
               x["oracle_gain_vs_conventional"] >= .015 for x in cases):
        return "REPRESENTATION_GAP"
    return "DIAGNOSTIC_POTENTIAL"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("preflight", "dev"), required=True)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    if args.mode == "preflight":
        if args.seed is not None:
            raise ValueError("CKAD40_PREFLIGHT_NO_SEED")
        print(json.dumps({"schema": SCHEMA, "prereg": PREREG,
                          "registered_dev": list(DEV),
                          "held_unconsumed": list(RESERVED),
                          "primary_scored": False, "pilot_scored": False}))
        return
    if args.seed not in DEV:
        raise ValueError("CKAD40_ONLY_REGISTERED_DEV")
    print("CKAD40_CASE=" + json.dumps(case(args.seed), sort_keys=True))


if __name__ == "__main__":
    main()

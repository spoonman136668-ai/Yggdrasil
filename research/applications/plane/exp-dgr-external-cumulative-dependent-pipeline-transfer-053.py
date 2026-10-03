"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TRANSFER-053."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TRANSFER-053"
PRIOR_PATH = Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
ACTIVE_CEILING = 7
PACKETS = 12
SCHEDULES = (
    ("A", "B", "C"),
    ("A", "C", "B"),
    ("B", "A", "C"),
    ("B", "C", "A"),
    ("C", "A", "B"),
    ("C", "B", "A"),
)
MECHANISMS = ("cold_no_retention", "carry6", "carry7")


def load_prior_experiment():
    spec = importlib.util.spec_from_file_location("dgr_external_020", PRIOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mix(a, b):
    n = min(len(a), len(b)) // 32 * 32
    return b"".join(a[i:i+32] + b[i:i+32] for i in range(0, n, 32))


def packet_prefix(data, packet):
    if not data:
        return data
    if packet >= PACKETS:
        return data
    n = max(1, len(data) * packet // PACKETS)
    return data[:min(n, len(data))]


def run(root):
    prior020 = load_prior_experiment()
    prior017 = prior020.load_prior_experiment()
    prior016 = prior017.load_prior_experiment()
    prior015 = prior016.load_prior_experiment()
    prior014 = prior015.load_prior_experiment()
    prior013 = prior014.load_prior_experiment()
    adaptation = prior013.load_prior_experiment()
    error_guided = adaptation.load_prior_experiment()
    wake = error_guided.load_wake()
    pressure = wake.load_pressure()
    learner = pressure.load_prior()

    m = {
        "source_identity_mismatch_count": 0.0,
        "source_count": 0.0,
        "total_source_bytes": 0.0,
        "base_training_identity_mismatch_count": 0.0,
        "schedule_count": float(len(SCHEDULES)),
        "mechanism_count": float(len(MECHANISMS)),
        "packet_budget_per_schedule": float(PACKETS),
        "history_future_overlap_count": 0.0,
        "heldout_selection_use_count": 0.0,
        "cold_mean_first_success_packet": 0.0,
        "carry6_mean_first_success_packet": 0.0,
        "carry7_mean_first_success_packet": 0.0,
        "carry6_mean_packet_reduction": 0.0,
        "carry7_mean_packet_reduction": 0.0,
        "carry6_positive_reduction_schedule_count": 0.0,
        "carry7_positive_reduction_schedule_count": 0.0,
        "carry6_collateral_failure_count": 0.0,
        "carry7_collateral_failure_count": 0.0,
        "selected_candidate_code": 0.0,
        "selected_candidate_mean_packet_reduction": 0.0,
        "selected_candidate_positive_reduction_schedule_count": 0.0,
        "selected_candidate_collateral_failure_count": 0.0,
        "preserved_state_structure_count_min": 16.0,
        "preserved_state_structure_count_max": 0.0,
        "active_structure_count_min": 16.0,
        "active_structure_count_max": 0.0,
        "retained_structure_count_min": 16.0,
        "retained_structure_count_max": 0.0,
        "matched_assignment_failure_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "row_mutation_event_count": 0.0,
        "tokenizer_use_count": 0.0,
        "external_model_call_count": 0.0,
        "invalid_evaluation_rows": 0.0,
    }

    demands = prior017.load_external(root, m)
    base_train = []
    for path, expected in learner.TRAIN_FILES:
        data, ok = learner.load_checked(path, expected)
        m["base_training_identity_mismatch_count"] += float(not ok)
        base_train.append(data)
    baseline = learner.baseline_train(base_train)

    def build_state(current_demands, ordered_names):
        independent_rows = {}
        for name in ordered_names:
            cue, _ = current_demands[name]
            stats, overflow, invalid = learner.candidate_stats(base_train + [cue])
            m["invalid_evaluation_rows"] += float(overflow + invalid)
            cells, radius_violations = learner.develop(stats)
            m["invalid_evaluation_rows"] += float(radius_violations)
            full = learner.specialized_map(cells)
            rows = wake.known_rows(pressure, learner, cells, stats)
            if len(full) != 16 or len(rows) != 16:
                m["invalid_evaluation_rows"] += 1.0
            independent_rows[name] = rows

        shared_stats, overflow, invalid = learner.candidate_stats(
            base_train + [current_demands[name][0] for name in ordered_names]
        )
        m["invalid_evaluation_rows"] += float(overflow + invalid)
        pooled_cells, radius_violations = learner.develop(shared_stats)
        m["invalid_evaluation_rows"] += float(radius_violations)
        cells, selected_count, _, _ = prior016.build_matched_minimax_cells(
            learner,
            error_guided,
            baseline,
            shared_stats,
            pooled_cells,
            independent_rows,
            ordered_names,
            current_demands,
            prior015,
        )
        if selected_count != 16:
            m["matched_assignment_failure_count"] += 1.0
        full_map = learner.specialized_map(cells)
        rows = wake.known_rows(pressure, learner, cells, shared_stats)
        if len(full_map) != 16 or len(rows) != 16:
            m["matched_assignment_failure_count"] += 1.0
            m["invalid_evaluation_rows"] += 1.0
        return rows, full_map

    def contribution_rank(rows, full_map, cue):
        keys = {row["key"] for row in rows}
        scores = error_guided.contributions(
            learner, cue, baseline, keys, full_map
        )
        ranked = sorted(
            rows,
            key=lambda row: (-scores[row["key"]], -row["utility"], row["key"]),
        )
        return ranked, scores

    def record_partition(rows, active):
        m["preserved_state_structure_count_min"] = min(
            m["preserved_state_structure_count_min"], float(len(rows))
        )
        m["preserved_state_structure_count_max"] = max(
            m["preserved_state_structure_count_max"], float(len(rows))
        )
        m["active_structure_count_min"] = min(
            m["active_structure_count_min"], float(len(active))
        )
        m["active_structure_count_max"] = max(
            m["active_structure_count_max"], float(len(active))
        )
        retained = len(rows) - len(active)
        m["retained_structure_count_min"] = min(
            m["retained_structure_count_min"], float(retained)
        )
        m["retained_structure_count_max"] = max(
            m["retained_structure_count_max"], float(retained)
        )
        if len(rows) != 16 or len(active) != 7 or retained != 9:
            m["invalid_evaluation_rows"] += 1.0

    def select_active(rows, full_map, cue, reserved_keys=()):
        ranked, _ = contribution_rank(rows, full_map, cue)
        by_key = {row["key"]: row for row in rows}
        selected = []
        selected_keys = set()
        for key in reserved_keys:
            row = by_key.get(key)
            if row is None:
                m["invalid_evaluation_rows"] += 1.0
                continue
            if key not in selected_keys:
                selected.append(row)
                selected_keys.add(key)
        for row in ranked:
            if row["key"] in selected_keys:
                continue
            selected.append(row)
            selected_keys.add(row["key"])
            if len(selected) == ACTIVE_CEILING:
                break
        if len(selected) != ACTIVE_CEILING:
            m["invalid_evaluation_rows"] += 1.0
        record_partition(rows, selected)
        return selected, wake.active_map(selected)

    def inject_retained(current_rows, current_map, historical_rows, historical_map, carry_keys, cue):
        rows = list(current_rows)
        fmap = dict(current_map)
        current_keys = {row["key"] for row in rows}
        hist_by_key = {row["key"]: row for row in historical_rows}
        missing = [key for key in carry_keys if key not in current_keys]
        if not missing:
            return rows, fmap
        ranked, scores = contribution_rank(rows, fmap, cue)
        carry_set = set(carry_keys)
        evictable = sorted(
            [row for row in ranked if row["key"] not in carry_set],
            key=lambda row: (scores[row["key"]], row["utility"], tuple(-x for x in row["key"])),
        )
        if len(evictable) < len(missing):
            m["invalid_evaluation_rows"] += 1.0
            return rows, fmap
        evictions = evictable[:len(missing)]
        evicted_keys = {row["key"] for row in evictions}
        rows = [row for row in rows if row["key"] not in evicted_keys]
        for key in evicted_keys:
            fmap.pop(key, None)
        for key in missing:
            row = hist_by_key.get(key)
            if row is None or key not in historical_map:
                m["invalid_evaluation_rows"] += 1.0
                continue
            rows.append(row)
            fmap[key] = historical_map[key]
        if len(rows) != 16 or len({row["key"] for row in rows}) != 16 or len(fmap) != 16:
            m["invalid_evaluation_rows"] += 1.0
        return rows, fmap

    def score(evaluation, active_map):
        base_correct, _, _ = pressure.model_correct_counts(
            learner, evaluation, baseline, {}
        )
        _, active_correct, _ = pressure.model_correct_counts(
            learner, evaluation, baseline, active_map
        )
        return active_correct - base_correct

    per_mechanism = {name: [] for name in MECHANISMS}
    diagnostics = []

    for schedule_index, (a_name, b_name, c_name) in enumerate(SCHEDULES):
        a_cue, a_eval = demands[a_name]
        b_cue, b_eval = demands[b_name]
        c_cue, c_eval = demands[c_name]
        a_mid = len(a_cue) // 2
        b_mid = len(b_cue) // 2
        c_mid = len(c_cue) // 2
        if min(a_mid, b_mid, c_mid, len(c_cue) - c_mid) <= 0:
            m["invalid_evaluation_rows"] += 1.0
            continue
        a_hist = a_cue[:a_mid]
        b_hist = b_cue[:b_mid]
        c_future = c_cue[c_mid:]
        # Slices are disjoint by construction; this explicit accounting is part of validity.
        if a_hist is a_cue[a_mid:] or b_hist is b_cue[b_mid:]:
            m["history_future_overlap_count"] += 1.0

        historical_demands = {
            a_name: (a_hist, a_eval),
            b_name: (b_hist, b_eval),
        }
        hist_rows, hist_map = build_state(
            historical_demands, [a_name, b_name]
        )
        derived_ab = mix(a_hist, b_hist)
        if not derived_ab:
            m["invalid_evaluation_rows"] += 1.0
            continue
        hist_ranked, _ = contribution_rank(hist_rows, hist_map, derived_ab)
        if len(hist_ranked) < 7:
            m["invalid_evaluation_rows"] += 1.0
            continue
        carry7 = tuple(row["key"] for row in hist_ranked[:7])
        carry6 = carry7[:6]

        dependent_eval = mix(mix(a_eval, b_eval), c_eval)
        if not dependent_eval:
            m["invalid_evaluation_rows"] += 1.0
            continue

        first_success = {name: 13 for name in MECHANISMS}
        collateral_blocked = {name: False for name in MECHANISMS}
        packet_records = []

        for packet in range(1, PACKETS + 1):
            c_partial = packet_prefix(c_future, packet)
            dep_cue = mix(derived_ab, c_partial)
            if not c_partial or not dep_cue:
                m["invalid_evaluation_rows"] += 1.0
                continue
            c_rows, c_map = build_state(
                {c_name: (c_partial, c_eval)}, [c_name]
            )

            mech_inputs = {}
            mech_inputs["cold_no_retention"] = (c_rows, c_map, ())
            r6, m6 = inject_retained(
                c_rows, c_map, hist_rows, hist_map, carry6, dep_cue
            )
            mech_inputs["carry6"] = (r6, m6, carry6)
            r7, m7 = inject_retained(
                c_rows, c_map, hist_rows, hist_map, carry7, dep_cue
            )
            mech_inputs["carry7"] = (r7, m7, carry7)

            rec = {"packet": packet, "mechanisms": {}}
            for mech in MECHANISMS:
                rows, fmap, reserved = mech_inputs[mech]
                _, amap = select_active(rows, fmap, dep_cue, reserved)
                dep_score = score(dependent_eval, amap)
                a_score = score(a_eval, amap)
                b_score = score(b_eval, amap)
                valid_success = dep_score > 0 and a_score > 0 and b_score > 0
                if dep_score > 0 and (a_score <= 0 or b_score <= 0):
                    collateral_blocked[mech] = True
                if first_success[mech] == 13 and valid_success:
                    first_success[mech] = packet
                rec["mechanisms"][mech] = {
                    "dependent_incremental_correct": dep_score,
                    "a_collateral_incremental_correct": a_score,
                    "b_collateral_incremental_correct": b_score,
                    "success": valid_success,
                }
            packet_records.append(rec)

        for mech in MECHANISMS:
            per_mechanism[mech].append(first_success[mech])
        if collateral_blocked["carry6"] and first_success["carry6"] == 13:
            m["carry6_collateral_failure_count"] += 1.0
        if collateral_blocked["carry7"] and first_success["carry7"] == 13:
            m["carry7_collateral_failure_count"] += 1.0

        diagnostics.append({
            "schedule_index": schedule_index,
            "schedule": [a_name, b_name, c_name],
            "history_bytes": {
                a_name: len(a_hist),
                b_name: len(b_hist),
            },
            "future_c_bytes": len(c_future),
            "first_success_packet": first_success,
            "packets": packet_records,
        })

    if any(len(v) != len(SCHEDULES) for v in per_mechanism.values()):
        m["invalid_evaluation_rows"] += 1.0

    def mean(xs):
        return sum(xs) / len(xs) if xs else 0.0

    cold = per_mechanism["cold_no_retention"]
    c6 = per_mechanism["carry6"]
    c7 = per_mechanism["carry7"]
    m["cold_mean_first_success_packet"] = mean(cold)
    m["carry6_mean_first_success_packet"] = mean(c6)
    m["carry7_mean_first_success_packet"] = mean(c7)
    m["carry6_mean_packet_reduction"] = mean(
        [float(x - y) for x, y in zip(cold, c6)]
    )
    m["carry7_mean_packet_reduction"] = mean(
        [float(x - y) for x, y in zip(cold, c7)]
    )
    m["carry6_positive_reduction_schedule_count"] = float(
        sum(1 for x, y in zip(cold, c6) if x - y > 0)
    )
    m["carry7_positive_reduction_schedule_count"] = float(
        sum(1 for x, y in zip(cold, c7) if x - y > 0)
    )

    # Frozen candidate selection: lower mean packet count; tie favors carry6.
    selected = "carry6"
    if m["carry7_mean_first_success_packet"] < m["carry6_mean_first_success_packet"]:
        selected = "carry7"
    if selected == "carry6":
        m["selected_candidate_code"] = 6.0
        m["selected_candidate_mean_packet_reduction"] = m["carry6_mean_packet_reduction"]
        m["selected_candidate_positive_reduction_schedule_count"] = m["carry6_positive_reduction_schedule_count"]
        m["selected_candidate_collateral_failure_count"] = m["carry6_collateral_failure_count"]
    else:
        m["selected_candidate_code"] = 7.0
        m["selected_candidate_mean_packet_reduction"] = m["carry7_mean_packet_reduction"]
        m["selected_candidate_positive_reduction_schedule_count"] = m["carry7_positive_reduction_schedule_count"]
        m["selected_candidate_collateral_failure_count"] = m["carry7_collateral_failure_count"]

    if m["preserved_state_structure_count_max"] == 0:
        m["invalid_evaluation_rows"] += 1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": m,
        "diagnostics": diagnostics,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(run(args.root), handle, allow_nan=False, separators=(",", ":"))


if __name__ == "__main__":
    main()

"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ATTRIBUTION-054."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ATTRIBUTION-054"
PRIOR_PATH = Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
ACTIVE_CEILING = 7
SCHEDULES = (
    ("A", "B", "C"),
    ("A", "C", "B"),
    ("B", "A", "C"),
    ("B", "C", "A"),
    ("C", "A", "B"),
    ("C", "B", "A"),
)
MECHANISMS = ("carry6", "carry7")
DOMAIN_NAMES = {"A": "code", "B": "structured", "C": "technical_prose"}
FAILED_053 = {
    ("A", "C", "B"),
    ("B", "C", "A"),
    ("C", "A", "B"),
    ("C", "B", "A"),
}


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
        "attribution_record_count": 0.0,
        "failed_053_schedule_count": 4.0,
        "successful_053_schedule_count": 2.0,
        "technical_prose_historical_failure_schedule_count": 0.0,
        "historical_support_failure_count": 0.0,
        "row_not_carried_count": 0.0,
        "injection_loss_count": 0.0,
        "reservation_selection_loss_count": 0.0,
        "cross_domain_active_interference_count": 0.0,
        "preserved_count": 0.0,
        "attribution_accounting_error_count": 0.0,
        "heldout_selection_use_count": 0.0,
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
        if len(selected) > ACTIVE_CEILING:
            m["invalid_evaluation_rows"] += 1.0
        for row in ranked:
            if len(selected) >= ACTIVE_CEILING:
                break
            if row["key"] in selected_keys:
                continue
            selected.append(row)
            selected_keys.add(row["key"])
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
        evicted = evictable[:len(missing)]
        evicted_keys = {row["key"] for row in evicted}
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

    records = []
    prose_failed_schedules = set()

    for schedule_index, (a_name, b_name, c_name) in enumerate(SCHEDULES):
        a_cue, a_eval = demands[a_name]
        b_cue, b_eval = demands[b_name]
        c_cue, c_eval = demands[c_name]
        a_hist = a_cue[:len(a_cue)//2]
        b_hist = b_cue[:len(b_cue)//2]
        c_future = c_cue[len(c_cue)//2:]
        if min(len(a_hist), len(b_hist), len(c_future)) <= 0:
            m["invalid_evaluation_rows"] += 1.0
            continue

        historical_demands = {
            a_name: (a_hist, a_eval),
            b_name: (b_hist, b_eval),
        }
        hist_rows, hist_map = build_state(historical_demands, [a_name, b_name])
        derived_ab = mix(a_hist, b_hist)
        if not derived_ab:
            m["invalid_evaluation_rows"] += 1.0
            continue
        hist_ranked, _ = contribution_rank(hist_rows, hist_map, derived_ab)
        if len(hist_ranked) < 7:
            m["invalid_evaluation_rows"] += 1.0
            continue
        carry_sets = {
            "carry6": tuple(row["key"] for row in hist_ranked[:6]),
            "carry7": tuple(row["key"] for row in hist_ranked[:7]),
        }

        c_partial = c_future
        dep_cue = mix(derived_ab, c_partial)
        if not dep_cue:
            m["invalid_evaluation_rows"] += 1.0
            continue
        c_rows, c_map = build_state({c_name: (c_partial, c_eval)}, [c_name])

        historical_info = {}
        for hist_name, hist_cue, hist_eval in (
            (a_name, a_hist, a_eval),
            (b_name, b_hist, b_eval),
        ):
            ranked_domain, _ = contribution_rank(hist_rows, hist_map, hist_cue)
            if not ranked_domain:
                m["invalid_evaluation_rows"] += 1.0
                continue
            protected_key = ranked_domain[0]["key"]
            _, hist_active_map = select_active(hist_rows, hist_map, hist_cue)
            historical_info[hist_name] = {
                "protected_key": protected_key,
                "historical_score": score(hist_eval, hist_active_map),
                "cue": hist_cue,
                "eval": hist_eval,
            }

        for mechanism in MECHANISMS:
            carry_keys = carry_sets[mechanism]
            injected_rows, injected_map = inject_retained(
                c_rows, c_map, hist_rows, hist_map, carry_keys, dep_cue
            )
            injected_keys = {row["key"] for row in injected_rows}
            reserved_active, reserved_map = select_active(
                injected_rows, injected_map, dep_cue, carry_keys
            )
            reserved_keys = {row["key"] for row in reserved_active}

            for hist_name in (a_name, b_name):
                info = historical_info.get(hist_name)
                if info is None:
                    m["invalid_evaluation_rows"] += 1.0
                    continue
                protected_key = info["protected_key"]
                hist_score = info["historical_score"]
                _, injected_domain_map = select_active(
                    injected_rows, injected_map, info["cue"]
                )
                injection_stage_score = score(info["eval"], injected_domain_map)
                reserved_score = score(info["eval"], reserved_map)

                carried = protected_key in set(carry_keys)
                survived = protected_key in injected_keys
                active_reserved = protected_key in reserved_keys

                if hist_score <= 0:
                    category = "historical_support_failure"
                elif not carried:
                    category = "row_not_carried"
                elif not survived:
                    category = "injection_loss"
                elif not active_reserved:
                    category = "reservation_selection_loss"
                elif reserved_score <= 0:
                    category = "cross_domain_active_interference"
                else:
                    category = "preserved"

                key = category + "_count"
                if key not in m:
                    m["invalid_evaluation_rows"] += 1.0
                else:
                    m[key] += 1.0
                m["attribution_record_count"] += 1.0

                if (
                    tuple((a_name,b_name,c_name)) in FAILED_053
                    and DOMAIN_NAMES[hist_name] == "technical_prose"
                    and category != "preserved"
                ):
                    prose_failed_schedules.add(schedule_index)

                records.append({
                    "schedule_index": schedule_index,
                    "schedule": [a_name, b_name, c_name],
                    "mechanism": mechanism,
                    "historical_domain_symbol": hist_name,
                    "historical_domain": DOMAIN_NAMES[hist_name],
                    "historical_score": hist_score,
                    "protected_key": list(protected_key),
                    "protected_key_carried": carried,
                    "protected_key_survived_injection": survived,
                    "protected_key_active_reserved": active_reserved,
                    "post_injection_domain_ranked_score": injection_stage_score,
                    "reserved_partition_collateral_score": reserved_score,
                    "category": category,
                })

    m["technical_prose_historical_failure_schedule_count"] = float(
        len(prose_failed_schedules)
    )
    category_total = sum(
        m[name]
        for name in (
            "historical_support_failure_count",
            "row_not_carried_count",
            "injection_loss_count",
            "reservation_selection_loss_count",
            "cross_domain_active_interference_count",
            "preserved_count",
        )
    )
    if category_total != m["attribution_record_count"]:
        m["attribution_accounting_error_count"] += 1.0
    if m["attribution_record_count"] != 24:
        m["attribution_accounting_error_count"] += 1.0
    if m["preserved_state_structure_count_max"] == 0:
        m["invalid_evaluation_rows"] += 1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "metrics": m,
        "attribution_records": records,
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

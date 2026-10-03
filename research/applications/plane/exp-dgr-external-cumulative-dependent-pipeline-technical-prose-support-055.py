"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TECHNICAL-PROSE-SUPPORT-055."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TECHNICAL-PROSE-SUPPORT-055"
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
MECHANISMS = ("baseline", "rebalanced")
PROSE = "C"
AFFECTED = {
    ("A", "C", "B"),
    ("B", "C", "A"),
    ("C", "A", "B"),
    ("C", "B", "A"),
}
CONTROLS = {
    ("A", "B", "C"),
    ("B", "A", "C"),
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
        "affected_schedule_count": float(len(AFFECTED)),
        "control_schedule_count": float(len(CONTROLS)),
        "mechanism_count": float(len(MECHANISMS)),
        "packet_budget_per_schedule": float(PACKETS),
        "history_byte_budget_mismatch_count": 0.0,
        "heldout_selection_use_count": 0.0,
        "rebalanced_technical_prose_positive_historical_support_count": 0.0,
        "baseline_affected_mean_first_success_packet": 0.0,
        "rebalanced_affected_mean_first_success_packet": 0.0,
        "affected_mean_packet_reduction": 0.0,
        "affected_positive_reduction_schedule_count": 0.0,
        "control_worsening_schedule_count": 0.0,
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
    baseline_model = learner.baseline_train(base_train)

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
            baseline_model,
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
            learner, cue, baseline_model, keys, full_map
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
            learner, evaluation, baseline_model, {}
        )
        _, active_correct, _ = pressure.model_correct_counts(
            learner, evaluation, baseline_model, active_map
        )
        return active_correct - base_correct

    def histories(a_name, b_name, a_cue, b_cue):
        a_base = a_cue[:len(a_cue)//2]
        b_base = b_cue[:len(b_cue)//2]
        base_total = len(a_base) + len(b_base)
        a_re = a_base
        b_re = b_base
        if a_name == PROSE:
            added = len(a_cue) - len(a_base)
            if added >= len(b_base):
                m["invalid_evaluation_rows"] += 1.0
            else:
                a_re = a_cue
                b_re = b_cue[:len(b_base)-added]
        elif b_name == PROSE:
            added = len(b_cue) - len(b_base)
            if added >= len(a_base):
                m["invalid_evaluation_rows"] += 1.0
            else:
                b_re = b_cue
                a_re = a_cue[:len(a_base)-added]
        if len(a_re) + len(b_re) != base_total:
            m["history_byte_budget_mismatch_count"] += 1.0
        return {
            "baseline": (a_base, b_base),
            "rebalanced": (a_re, b_re),
        }

    affected_baseline = []
    affected_rebalanced = []
    diagnostics = []

    for schedule_index, (a_name, b_name, c_name) in enumerate(SCHEDULES):
        a_cue, a_eval = demands[a_name]
        b_cue, b_eval = demands[b_name]
        c_cue, c_eval = demands[c_name]
        c_mid = len(c_cue)//2
        if c_mid <= 0 or len(c_cue)-c_mid <= 0:
            m["invalid_evaluation_rows"] += 1.0
            continue
        c_future = c_cue[c_mid:]
        history_variants = histories(a_name, b_name, a_cue, b_cue)

        variant_data = {}
        for mech in MECHANISMS:
            a_hist, b_hist = history_variants[mech]
            if min(len(a_hist),len(b_hist)) <= 0:
                m["invalid_evaluation_rows"] += 1.0
                continue
            hd = {
                a_name: (a_hist, a_eval),
                b_name: (b_hist, b_eval),
            }
            hist_rows, hist_map = build_state(hd, [a_name,b_name])
            derived_ab = mix(a_hist,b_hist)
            if not derived_ab:
                m["invalid_evaluation_rows"] += 1.0
                continue
            ranked, _ = contribution_rank(hist_rows,hist_map,derived_ab)
            if len(ranked) < 6:
                m["invalid_evaluation_rows"] += 1.0
                continue
            carry6 = tuple(row["key"] for row in ranked[:6])

            prose_support = None
            if PROSE in (a_name,b_name):
                prose_hist = a_hist if a_name==PROSE else b_hist
                prose_eval = a_eval if a_name==PROSE else b_eval
                _, prose_map = select_active(hist_rows,hist_map,prose_hist)
                prose_support = score(prose_eval,prose_map)
                if mech=="rebalanced" and prose_support>0:
                    m["rebalanced_technical_prose_positive_historical_support_count"] += 1.0

            variant_data[mech] = {
                "a_hist": a_hist,
                "b_hist": b_hist,
                "hist_rows": hist_rows,
                "hist_map": hist_map,
                "derived_ab": derived_ab,
                "carry6": carry6,
                "prose_support": prose_support,
            }

        dependent_eval = mix(mix(a_eval,b_eval),c_eval)
        if not dependent_eval:
            m["invalid_evaluation_rows"] += 1.0
            continue

        first_success = {mech:13 for mech in MECHANISMS}
        packet_records = []
        for packet in range(1,PACKETS+1):
            c_partial = packet_prefix(c_future,packet)
            if not c_partial:
                m["invalid_evaluation_rows"] += 1.0
                continue
            c_rows,c_map = build_state({c_name:(c_partial,c_eval)},[c_name])

            rec={"packet":packet,"mechanisms":{}}
            for mech in MECHANISMS:
                vd=variant_data.get(mech)
                if vd is None:
                    m["invalid_evaluation_rows"] += 1.0
                    continue
                dep_cue=mix(vd["derived_ab"],c_partial)
                if not dep_cue:
                    m["invalid_evaluation_rows"] += 1.0
                    continue
                rows,fmap=inject_retained(
                    c_rows,c_map,vd["hist_rows"],vd["hist_map"],vd["carry6"],dep_cue
                )
                _,amap=select_active(rows,fmap,dep_cue,vd["carry6"])
                dep_score=score(dependent_eval,amap)
                a_score=score(a_eval,amap)
                b_score=score(b_eval,amap)
                ok=dep_score>0 and a_score>0 and b_score>0
                if first_success[mech]==13 and ok:
                    first_success[mech]=packet
                rec["mechanisms"][mech]={
                    "dependent_incremental_correct":dep_score,
                    "a_collateral_incremental_correct":a_score,
                    "b_collateral_incremental_correct":b_score,
                    "success":ok,
                }
            packet_records.append(rec)

        sched=(a_name,b_name,c_name)
        if sched in AFFECTED:
            affected_baseline.append(first_success["baseline"])
            affected_rebalanced.append(first_success["rebalanced"])
            if first_success["rebalanced"] < first_success["baseline"]:
                m["affected_positive_reduction_schedule_count"] += 1.0
        elif sched in CONTROLS:
            if first_success["rebalanced"] > first_success["baseline"]:
                m["control_worsening_schedule_count"] += 1.0

        diagnostics.append({
            "schedule_index":schedule_index,
            "schedule":[a_name,b_name,c_name],
            "baseline_history_bytes":{
                a_name:len(history_variants["baseline"][0]),
                b_name:len(history_variants["baseline"][1]),
            },
            "rebalanced_history_bytes":{
                a_name:len(history_variants["rebalanced"][0]),
                b_name:len(history_variants["rebalanced"][1]),
            },
            "baseline_prose_historical_support":variant_data["baseline"]["prose_support"],
            "rebalanced_prose_historical_support":variant_data["rebalanced"]["prose_support"],
            "first_success_packet":first_success,
            "packets":packet_records,
        })

    def mean(xs):
        return sum(xs)/len(xs) if xs else 0.0

    if len(affected_baseline)!=4 or len(affected_rebalanced)!=4:
        m["invalid_evaluation_rows"] += 1.0
    m["baseline_affected_mean_first_success_packet"]=mean(affected_baseline)
    m["rebalanced_affected_mean_first_success_packet"]=mean(affected_rebalanced)
    m["affected_mean_packet_reduction"]=mean(
        [float(x-y) for x,y in zip(affected_baseline,affected_rebalanced)]
    )
    if m["preserved_state_structure_count_max"]==0:
        m["invalid_evaluation_rows"] += 1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {
        "schema":"yggdrasil.research-scientific-result.v1",
        "experiment":EXPERIMENT,
        "metrics":m,
        "diagnostics":diagnostics,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:
        json.dump(run(a.root),f,allow_nan=False,separators=(",",":"))


if __name__=="__main__":
    main()

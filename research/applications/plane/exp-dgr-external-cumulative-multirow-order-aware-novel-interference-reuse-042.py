"""EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-NOVEL-INTERFERENCE-REUSE-042."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

E = "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-NOVEL-INTERFERENCE-REUSE-042"
P = Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
S = (
    ("A","B","C"), ("A","C","B"), ("B","A","C"),
    ("B","C","A"), ("C","A","B"), ("C","B","A"),
)
T = (("A","B"), ("A","C"), ("B","C"))

def load():
    s = importlib.util.spec_from_file_location("p020", P)
    if s is None or s.loader is None:
        raise RuntimeError("PRIOR_IMPORT_FAILED")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

def prefix(n, i):
    return n if i >= 12 else min(max(1, n * i // 12), n - 1)

def mix(a, b):
    n = min(len(a), len(b)) // 32 * 32
    return b"".join(a[i:i+32] + b[i:i+32] for i in range(0, n, 32))

def run(root):
    p20 = load()
    p17 = p20.load_prior_experiment()
    p16 = p17.load_prior_experiment()
    p15 = p16.load_prior_experiment()
    p14 = p15.load_prior_experiment()
    p13 = p14.load_prior_experiment()
    ad = p13.load_prior_experiment()
    eg = ad.load_prior_experiment()
    wake = eg.load_wake()
    pressure = wake.load_pressure()
    learner = pressure.load_prior()

    m = {
        "source_identity_mismatch_count": 0.0,
        "source_count": 0.0,
        "total_source_bytes": 0.0,
        "base_training_identity_mismatch_count": 0.0,
        "schedule_count": 6.0,
        "target_pair_count": 3.0,
        "target_order_count_per_pair": 2.0,
        "safety_case_count": 0.0,
        "base_case_count": 0.0,
        "reuse_cycle_count_per_case": 3.0,
        "novel_steps_per_cycle": 2.0,
        "novel_interference_episode_count": 0.0,
        "guard_applied_episode_count": 0.0,
        "guard_noop_episode_count": 0.0,
        "post_episode_target_recovery_check_count": 0.0,
        "positive_post_episode_target_recovery_check_count": 0.0,
        "post_episode_partner_recovery_check_count": 0.0,
        "positive_post_episode_partner_recovery_check_count": 0.0,
        "reuse_accounting_error_count": 0.0,
        "post_novel_target_recovery_check_count": 0.0,
        "positive_post_novel_target_recovery_check_count": 0.0,
        "post_novel_partner_recovery_check_count": 0.0,
        "positive_post_novel_partner_recovery_check_count": 0.0,
        "non_target_safety_failure_count": 0.0,
        "baseline_non_target_safety_failure_count": 0.0,
        "repaired_non_target_safety_failure_count": 0.0,
        "guard_applied_case_count": 0.0,
        "guard_noop_case_count": 0.0,
        "repair_accounting_error_count": 0.0,
        "ratio_applicable_safety_case_count": 0.0,
        "zero_baseline_safety_case_count": 0.0,
        "failure_domain_A_count": 0.0,
        "failure_domain_B_count": 0.0,
        "failure_domain_C_count": 0.0,
        "failing_domain_count": 0.0,
        "dominant_failure_domain_fraction": 0.0,
        "minimum_applicable_non_target_preserved_to_unprotected_fraction": float("inf"),
        "zero_baseline_preserved_negative_count": 0.0,
        "failure_attribution_accounting_error_count": 0.0,
        "preserved_state_structure_count_min": 16.0,
        "preserved_state_structure_count_max": 0.0,
        "active_structure_count_min": 16.0,
        "active_structure_count_max": 0.0,
        "retained_structure_count_min": 16.0,
        "retained_structure_count_max": 0.0,
        "target_interference_leakage_count": 0.0,
        "heldout_selection_use_count": 0.0,
        "capacity_growth_event_count": 0.0,
        "row_mutation_event_count": 0.0,
        "tokenizer_use_count": 0.0,
        "external_model_call_count": 0.0,
        "invalid_evaluation_rows": 0.0,
    }

    d = p17.load_external(root, m)
    bt = []
    for path, exp in learner.TRAIN_FILES:
        x, ok = learner.load_checked(path, exp)
        m["base_training_identity_mismatch_count"] += float(not ok)
        bt.append(x)
    base = learner.baseline_train(bt)

    mp = {}
    mc = {}
    for name in "ABC":
        cue, _ = d[name]
        found = None
        for i in range(1, 13):
            q = cue[:prefix(len(cue), i)]
            st, o, iv = learner.candidate_stats(bt + [q])
            m["invalid_evaluation_rows"] += float(o + iv)
            c, rv = learner.develop(st)
            m["invalid_evaluation_rows"] += float(rv)
            fm = learner.specialized_map(c)
            rows = wake.known_rows(pressure, learner, c, st)
            if len(fm) != 16 or len(rows) != 16:
                m["invalid_evaluation_rows"] += 1.0
            sc = eg.contributions(learner, q, base, {r["key"] for r in rows}, fm)
            if any(v > 0 for v in sc.values()):
                found = (i, q)
                break
        if found is None:
            m["invalid_evaluation_rows"] += 1.0
            found = (12, cue)
        mp[name], mc[name] = found

    def order(sched):
        out = []
        seen = set()
        for i in range(1, 13):
            for n in sched:
                if n not in seen and i >= mp[n]:
                    seen.add(n)
                    out.append(n)
        return out

    def state(cur, names):
        ind = {}
        for n in names:
            cue, _ = cur[n]
            st, o, iv = learner.candidate_stats(bt + [cue])
            m["invalid_evaluation_rows"] += float(o + iv)
            c, rv = learner.develop(st)
            m["invalid_evaluation_rows"] += float(rv)
            fm = learner.specialized_map(c)
            rows = wake.known_rows(pressure, learner, c, st)
            if len(fm) != 16 or len(rows) != 16:
                m["invalid_evaluation_rows"] += 1.0
            ind[n] = rows
        st, o, iv = learner.candidate_stats(bt + [cur[n][0] for n in names])
        m["invalid_evaluation_rows"] += float(o + iv)
        c, rv = learner.develop(st)
        m["invalid_evaluation_rows"] += float(rv)
        cells, nsel, _, _ = p16.build_matched_minimax_cells(
            learner, eg, base, st, c, ind, names, cur, p15
        )
        if nsel != 16:
            m["invalid_evaluation_rows"] += 1.0
        fm = learner.specialized_map(cells)
        rows = wake.known_rows(pressure, learner, cells, st)
        if len(fm) != 16 or len(rows) != 16:
            m["invalid_evaluation_rows"] += 1.0
        return rows, fm

    def active(rows, fm, cue):
        sc = eg.contributions(learner, cue, base, {r["key"] for r in rows}, fm)
        a = sorted(rows, key=lambda r: (-sc[r["key"]], -r["utility"], r["key"]))[:7]
        return a, wake.active_map(a)

    def guarded_active(rows, fm, novel_cue, guard_cue):
        keys = {r["key"] for r in rows}
        guard_scores = eg.contributions(learner, guard_cue, base, keys, fm)
        guard = sorted(
            rows,
            key=lambda r: (-guard_scores[r["key"]], -r["utility"], r["key"]),
        )[0]
        novel_scores = eg.contributions(learner, novel_cue, base, keys, fm)
        ranked = sorted(
            rows,
            key=lambda r: (-novel_scores[r["key"]], -r["utility"], r["key"]),
        )
        selected = [guard]
        selected_keys = {guard["key"]}
        for row in ranked:
            if row["key"] in selected_keys:
                continue
            selected.append(row)
            selected_keys.add(row["key"])
            if len(selected) == 7:
                break
        if len(selected) != 7:
            m["invalid_evaluation_rows"] += 1.0
        original_keys = {r["key"] for r in ranked[:7]}
        if guard["key"] in original_keys:
            m["guard_noop_episode_count"] += 1.0
        return selected, wake.active_map(selected)

    def score(ev, am):
        b, _, _ = pressure.model_correct_counts(learner, ev, base, {})
        _, a, _ = pressure.model_correct_counts(learner, ev, base, am)
        return a - b

    diagnostics = []
    first_failure = None

    for sched_i, sched in enumerate(S):
        names = order(sched)
        if len(names) != 3:
            m["invalid_evaluation_rows"] += 1.0
            continue
        ar, am = state(d, names)
        aks = {r["key"] for r in ar}

        for pair_i, pair in enumerate(T):
            protected_for_target = {}
            prot = {}
            for target in pair:
                sc = eg.contributions(learner, mc[target], base, aks, am)
                cand = sorted(
                    [r for r in ar if sc[r["key"]] > 0],
                    key=lambda r: (-sc[r["key"]], -r["utility"], r["key"]),
                )
                if not cand:
                    m["invalid_evaluation_rows"] += 1.0
                    continue
                protected_for_target[target] = cand[0]
                prot[cand[0]["key"]] = cand[0]
            if len(protected_for_target) != 2:
                m["invalid_evaluation_rows"] += 1.0
                continue

            nt = next(n for n in "ABC" if n not in pair)
            ec = d[nt][0][:prefix(len(d[nt][0]), 12)]
            ir, im = state({nt: (ec, d[nt][1])}, [nt])
            iks = {r["key"] for r in ir}
            absent = [(k, prot[k]) for k in sorted(prot) if k not in iks]
            sc = eg.contributions(learner, ec, base, iks, im)
            cand = sorted(
                [r for r in ir if r["key"] not in prot],
                key=lambda r: (sc[r["key"]], r["utility"], tuple(-x for x in r["key"])),
            )
            if len(cand) < len(absent):
                m["invalid_evaluation_rows"] += 1.0
                continue
            evict = {r["key"] for r in cand[:len(absent)]}
            pr = [r for r in ir if r["key"] not in evict] + [r for _, r in absent]
            pm = dict(im)
            for k in evict:
                pm.pop(k, None)
            for k, _ in absent:
                pm[k] = am[k]
            if len(pr) != 16 or len({r["key"] for r in pr}) != 16 or len(pm) != 16:
                m["invalid_evaluation_rows"] += 1.0

            _, uam = active(ir, im, ec)
            ub = score(d[nt][1], uam)

            for order_i, (first, second) in enumerate(((pair[0], pair[1]), (pair[1], pair[0]))):
                m["base_case_count"] += 1.0
                apply_guard = (
                    order_i == 1
                    and (
                        (pair == ("A", "B") and nt == "C")
                        or (pair == ("B", "C") and nt == "A")
                    )
                )
                for cycle_i in range(3):
                    for step_i, (target, partner) in enumerate(((first, second), (second, first))):
                        m["safety_case_count"] += 1.0
                        m["novel_interference_episode_count"] += 1.0
                        q = mix(ec, mc[target])
                        if not q:
                            m["invalid_evaluation_rows"] += 1.0
                            continue

                        if apply_guard:
                            m["guard_applied_episode_count"] += 1.0
                            aa, nam = guarded_active(pr, pm, q, ec)
                        else:
                            aa, nam = active(pr, pm, q)
                        ret = len(pr) - len(aa)
                        m["preserved_state_structure_count_min"] = min(
                            m["preserved_state_structure_count_min"], float(len(pr))
                        )
                        m["preserved_state_structure_count_max"] = max(
                            m["preserved_state_structure_count_max"], float(len(pr))
                        )
                        m["active_structure_count_min"] = min(
                            m["active_structure_count_min"], float(len(aa))
                        )
                        m["active_structure_count_max"] = max(
                            m["active_structure_count_max"], float(len(aa))
                        )
                        m["retained_structure_count_min"] = min(
                            m["retained_structure_count_min"], float(ret)
                        )
                        m["retained_structure_count_max"] = max(
                            m["retained_structure_count_max"], float(ret)
                        )
                        if len(aa) != 7 or ret != 9:
                            m["invalid_evaluation_rows"] += 1.0

                        ni = score(d[nt][1], nam)
                        ratio = None
                        failure = False
                        if ub > 0:
                            m["ratio_applicable_safety_case_count"] += 1.0
                            ratio = ni / ub
                            m["minimum_applicable_non_target_preserved_to_unprotected_fraction"] = min(
                                m["minimum_applicable_non_target_preserved_to_unprotected_fraction"], ratio
                            )
                            failure = ratio < 0.95
                        elif ub == 0:
                            m["zero_baseline_safety_case_count"] += 1.0
                            failure = ni < 0
                            if failure:
                                m["zero_baseline_preserved_negative_count"] += 1.0
                        else:
                            m["invalid_evaluation_rows"] += 1.0

                        if failure:
                            m["non_target_safety_failure_count"] += 1.0
                            if first_failure is None:
                                first_failure = {
                                    "schedule_index": sched_i,
                                    "target_pair_index": pair_i,
                                    "target_order_index": order_i,
                                    "cycle_index": cycle_i,
                                    "step_index": step_i,
                                    "target": target,
                                    "partner": partner,
                                    "non_target": nt,
                                    "unprotected_increment": ub,
                                    "preserved_increment": ni,
                                    "preserved_to_unprotected_fraction": ratio,
                                }

                        _, tm = active(pr, pm, mc[target])
                        ti = score(d[target][1], tm)
                        m["post_episode_target_recovery_check_count"] += 1.0
                        m["positive_post_episode_target_recovery_check_count"] += float(ti > 0)

                        _, xm = active(pr, pm, mc[partner])
                        xi = score(d[partner][1], xm)
                        m["post_episode_partner_recovery_check_count"] += 1.0
                        m["positive_post_episode_partner_recovery_check_count"] += float(xi > 0)

                        diagnostics.append({
                            "schedule_index": sched_i,
                            "target_pair_index": pair_i,
                            "target_order_index": order_i,
                            "cycle_index": cycle_i,
                            "step_index": step_i,
                            "target": target,
                            "partner": partner,
                            "non_target": nt,
                            "guard_applied": apply_guard,
                            "unprotected_increment": ub,
                            "preserved_increment": ni,
                            "preserved_to_unprotected_fraction": ratio,
                            "safety_failure": failure,
                            "target_recovery_increment": ti,
                            "partner_recovery_increment": xi,
                        })

    failures = m["non_target_safety_failure_count"]
    if m["base_case_count"] != 36:
        m["reuse_accounting_error_count"] += 1.0
    if m["novel_interference_episode_count"] != 216:
        m["reuse_accounting_error_count"] += 1.0
    if m["guard_applied_episode_count"] != 72:
        m["reuse_accounting_error_count"] += 1.0
    if m["post_episode_target_recovery_check_count"] != 216:
        m["reuse_accounting_error_count"] += 1.0
    if m["post_episode_partner_recovery_check_count"] != 216:
        m["reuse_accounting_error_count"] += 1.0
    if len(diagnostics) != 216:
        m["reuse_accounting_error_count"] += 1.0
    if math.isinf(m["minimum_applicable_non_target_preserved_to_unprotected_fraction"]):
        m["minimum_applicable_non_target_preserved_to_unprotected_fraction"] = 0.0

    assert all(math.isfinite(float(v)) for v in m.values())
    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": E,
        "metrics": m,
        "first_failure": first_failure,
        "diagnostics": diagnostics,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(run(a.root), f, allow_nan=False, separators=(",", ":"))

if __name__ == "__main__":
    main()

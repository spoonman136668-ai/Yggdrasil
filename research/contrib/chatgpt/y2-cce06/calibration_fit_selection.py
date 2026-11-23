"""CCE06 TRAIN-only, public-data control qualification; never reads CAL-EVAL.

This is a preparation tool, NOT calibration scoring or primary first-use.
All selection and stopping decisions use a chronological holdout from TRAIN.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from calibration_controls import ActionHMM, FullSuffixTable, multichannel_brier, validated


@dataclass(frozen=True)
class TrainingSplit:
    fit: tuple[tuple[dict, ...], ...]
    select: tuple[tuple[dict, ...], ...]
    fit_events: int
    select_events: int


def split_train_only(public_train, *, fraction=0.2, min_select=16):
    """Separate suffix portions of each public TRAIN trace; reject hidden fields.

    Never accepts the separately registered CAL-EVAL set. Input identity/custody
    must be checked by the caller; this only enforces field/schema integrity.
    """
    if (type(public_train) not in (tuple, list) or not public_train or
            type(fraction) is not float or not (0.1 <= fraction <= 0.4) or
            type(min_select) is not int or min_select < 4):
        raise ValueError("CCE06_INVALID_TRAIN_PARTITION")
    fit, select = [], []
    for events in public_train:
        validated(events)
        n = len(events)
        selected = max(min_select, math.ceil(n * fraction))
        if n - selected < min_select or selected >= n:
            raise ValueError("CCE06_INSUFFICIENT_TRAIN_ONLY_EVENTS")
        # Copies preserve the exact public event stream but no shared objects.
        a = tuple(dict(observation=e["observation"][:], action=e["action"],
                       next_observation=e["next_observation"][:]) for e in events[:n-selected])
        b = tuple(dict(observation=e["observation"][:], action=e["action"],
                       next_observation=e["next_observation"][:]) for e in events[n-selected:])
        fit.append(a)
        select.append(b)
    return TrainingSplit(tuple(fit), tuple(select), sum(map(len, fit)), sum(map(len, select)))


def score_public_brier(model, data):
    """Prequential predictions with frozen fit; no evaluator or hidden state API."""
    total, count = 0.0, 0
    for events in data:
        validated(events)
        for t, e in enumerate(events):
            probs = model.predict(events[:t], e["action"])
            total += multichannel_brier(probs, e["next_observation"])
            count += 1
    if not count:
        raise ValueError("CCE06_NO_SCORE_EVENTS")
    return total / count


def select_suffix_on_train(public_train, *, depths=tuple(range(1, 9)), fraction=0.2):
    """Choose unrestricted public suffix-depth from TRAIN only, then refit all TRAIN."""
    if (type(depths) is not tuple or not depths or len(set(depths)) != len(depths)
            or any(type(d) is not int or d not in range(1, 9) for d in depths)):
        raise ValueError("CCE06_BAD_SUFFIX_GRID")
    part = split_train_only(public_train, fraction=fraction)
    scored = []
    for d in sorted(depths):
        model = FullSuffixTable(d).fit(part.fit)
        score = score_public_brier(model, part.select)
        if not math.isfinite(score):
            raise ValueError("CCE06_NONFINITE_TRAIN_SCORE")
        scored.append({"depth": d, "train_only_brier": score, "fit_events": part.fit_events,
                       "selection_events": part.select_events})
    best = min(scored, key=lambda row: (row["train_only_brier"], row["depth"]))
    # Selection is finished before any separately held-out calibration data.
    final = FullSuffixTable(best["depth"]).fit(tuple(tuple(e) for e in public_train))
    return final, {"status": "TRAIN_ONLY_SUFFIX_SELECTED", "selected_depth": best["depth"],
                   "grid": tuple(scored), "final_train_events": final.samples}


def select_hmm_on_train(public_train, *, dimensions=tuple(range(2, 9)),
                        restarts=3, max_iters=50, fraction=0.2, seed=60806):
    """Train-only HMM dimension selection and independent EM restarts.

    For each dimension, choose the highest TRAIN log-likelihood restart; compare
    dimensions using chronological TRAIN-selection log-likelihood. A fit that
    exhausts iterations is NOT called converged. Never quietly drop such a fit.
    The eventual CAL gate must still check convergence for all relevant controls.
    """
    if (type(dimensions) is not tuple or not dimensions or len(set(dimensions)) != len(dimensions)
            or any(type(d) is not int or not 2 <= d <= 8 for d in dimensions)
            or type(restarts) is not int or not 3 <= restarts <= 12
            or type(max_iters) is not int or not 3 <= max_iters <= 100
            or type(seed) is not int or seed < 0):
        raise ValueError("CCE06_INVALID_HMM_GRID")
    part = split_train_only(public_train, fraction=fraction)
    candidates = []
    all_runs = []
    for dim in sorted(dimensions):
        dim_runs = []
        for restart in range(restarts):
            run_seed = seed + 1000003 * dim + 17171 * restart
            model = ActionHMM(dim, run_seed).fit(part.fit, max_iters=max_iters)
            if not model.trace or not all(math.isfinite(x) for x in model.trace):
                raise ValueError("CCE06_NONFINITE_HMM_TRAIN")
            trace = model.trace
            declines = tuple(trace[i] - trace[i-1] for i in range(1, len(trace)))
            # Small smoothing bias may give a slight nonmonotonicity; report all.
            fitted = {"dimension": dim, "restart": restart, "seed": run_seed,
                      "iterations": len(trace), "max_iters": max_iters,
                      "initial_log_likelihood": trace[0], "train_log_likelihood": trace[-1],
                      "max_step_drop": min((0.0, *declines)),
                      "converged": len(trace) < max_iters}
            dim_runs.append((model, fitted))
            all_runs.append(fitted)
        best_model, best_run = max(dim_runs,
                                   key=lambda x: (x[1]["train_log_likelihood"], -x[1]["restart"]))
        val_ll = best_model.likelihood(part.select)
        if not math.isfinite(val_ll):
            raise ValueError("CCE06_NONFINITE_HMM_SELECT")
        candidates.append((best_model, {"dimension": dim, "selected_restart": best_run["restart"],
                                        "train_only_select_nll_per_observation": -val_ll / (
                                            part.select_events + len(part.select)),
                                        "converged": best_run["converged"]}))
    selected, chosen = min(candidates, key=lambda x: (
        x[1]["train_only_select_nll_per_observation"], x[1]["dimension"]))
    # Final selected capacity is refit on ALL TRAIN with same deterministic seed,
    # and its fit/convergence receipt is separate from the model-selection receipt.
    final_seed = seed + 1000003 * chosen["dimension"] + 17171 * chosen["selected_restart"]
    final = ActionHMM(chosen["dimension"], final_seed).fit(public_train, max_iters=max_iters)
    final_fit_converged = len(final.trace) < max_iters
    receipt = {"status": "TRAIN_ONLY_HMM_SELECTED" if final_fit_converged else "HMM_CONVERGENCE_UNVERIFIED",
               "selection": chosen, "restarts": tuple(all_runs),
               "fit_events": part.fit_events, "selection_events": part.select_events,
               "full_train_events": final.samples, "final_iters": len(final.trace),
               "final_converged": final_fit_converged,
               "grid_dimensions": tuple(sorted(dimensions)), "grid_restarts": restarts}
    return final, receipt

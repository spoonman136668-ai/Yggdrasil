"""KNOW31: prospective paired A-continuation/B-interference attribution.

Pre-first-use frozen protocol 22a197a61060a97a9aa45aecec78e85c71122600;
48-step compatibility revision 4b392dad590bea0f6b236c4399039c1d9c369a36.
Synthetic source-only. No new model, protected source first-use or native weights.
HELD source is NEVER called by focused/unit tests.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import time
from pathlib import Path

from know30_blind_archive_reactivation_dev import (
    Pair, Single, Joint, trained, high_brier, MODE,
)
from know27_online_action_policy_dev import true_bit
from unknown_action_affordance_dev import (
    TRUE_MAPS, P_TRUE, P_FALSE, canonical, digest,
)

SCHEMA = "yggdrasil.know31.paired-interference-result.v1"
PROTO = "yggdrasil.know31.paired-causal-interference-prereg.v1"
PROTO_GIT_BLOB = "38196b88ddedad232569212713203c39a5f1f557"
PREG = "22a197a61060a97a9aa45aecec78e85c71122600"
REV = "4b392dad590bea0f6b236c4399039c1d9c369a36"
SEEDS = (16001, 16007, 16037, 16061, 16067, 16069, 16073, 16087)
MAPS = (0, 1, 2)
ARMS = ("archive", "switching_bayes", "single", "rolling8")
FORKS = ("control_A", "treatment_B")
PREFIX = 16
B_END = 32
N = 48
K = (0, 1, 2, 4, 8)


def require(v, reason):
    if not v:
        raise ValueError("YGG_KNOW31_" + reason)


def protocol():
    path = Path(__file__).with_name("know31_paired_interference_protocol.json")
    raw = path.read_bytes()
    blob = hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()
    require(blob == PROTO_GIT_BLOB, "PROTOCOL_BLOB")
    p = json.loads(raw)
    b = p["budgets"]
    require(p["schema"] == PROTO
            and p["source_mode"] == MODE
            and p["source"]["seeds"] == list(SEEDS)
            and p["source"]["mapping_ids"] == list(MAPS)
            and p["source"]["steps"] == N
            and b["fork_prefix"] == PREFIX and b["interference"] == 16
            and b["return"] == 16
            and b["actions_both_forks_per_method"] == 2304
            and b["unique_simulator_witnesses_all_worlds"] == 1920
            and p["source"]["protected_original_first_use"] is False
            and p["source"]["accepted_native_modified"] is False,
            "FROZEN_PROTOCOL")
    return p


def private_witness(mid, seed, t, a, branch, *, source_mode=MODE):
    """Evaluator private domain. No policy API accepts mid/seed/branch."""
    require(source_mode == MODE
            and type(mid) is int and mid in MAPS
            and type(seed) is int and seed in SEEDS
            and type(t) is int and 0 <= t < N
            and type(a) is int and a in (0, 1, 2, 3)
            and branch in FORKS, "PRIVATE_SOURCE")
    law = "H2" if branch == "treatment_B" and PREFIX <= t < B_END else "H0"
    c = t % 4
    q = P_TRUE if true_bit(law, c ^ TRUE_MAPS[mid][a]) else P_FALSE
    raw = hashlib.sha256(
        f"know31:private:coin:v1:{mid}:{seed}:{t}".encode("ascii")
    ).digest()
    u = int.from_bytes(raw[:8], "big") / (1 << 64)
    return int(u < q)


def new_arms(fitted):
    _prior, a, b, pooled, _archive = fitted
    return {
        "archive": Pair(a, b, quarantine=True),
        "switching_bayes": Pair(a, b, quarantine=False),
        "single": Single(pooled),
        "rolling8": Single(pooled, rolling=True),
    }


def cold_copy(m):
    """Canonical readback for Pair; deterministic public-history cold replay for Single."""
    if isinstance(m, Pair):
        original = m.checkpoint()
        restored = Pair.restore(original, digest(original))
        require(restored.checkpoint() == original, "PAIR_COLD_BYTES")
    else:
        require(isinstance(m, Single), "MODEL_CLASS")
        public = canonical({
            "rolling": m.rolling, "rows": m.rows,
            "start_prior": m.start.prior, "start_logs": m.start.logs,
            "start_assimilated": m.start.assimilated,
        })
        restored = Single(copy.deepcopy(m.start), rolling=m.rolling)
        for step, (c, a, y) in enumerate(m.rows):
            restored.observe(step, c, a, y)
        reproduced = canonical({
            "rolling": restored.rolling, "rows": restored.rows,
            "start_prior": restored.start.prior,
            "start_logs": restored.start.logs,
            "start_assimilated": restored.start.assimilated,
        })
        require(reproduced == public, "SINGLE_COLD_BYTES")
    require([restored.prob(c, 0) for c in range(8)] ==
            [m.prob(c, 0) for c in range(8)], "COLD_EIGHT_OUTPUTS")
    return restored


def slot_digest(m):
    require(isinstance(m, Pair), "SLOT_PAIR")
    return digest(canonical(m.slots[0].logs))


def a_slot_high(m):
    require(isinstance(m, Pair), "SLOT_PAIR")
    return [m.slots[0].prob(c, 0) for c in range(4, 8)]


def score_at_fork(model):
    return high_brier(model, "H0")


def methods_after_public_prefix(mid, seed, fitted):
    methods = new_arms(fitted)
    for t in range(PREFIX):
        c, a = t % 4, t % 4
        y = private_witness(mid, seed, t, a, "control_A")
        require(y == private_witness(mid, seed, t, a, "treatment_B"),
                "PREFIX_MUST_SHARE_PHYSICAL_Y")
        for m in methods.values():
            m.observe(t, c, a, y)
    for m in methods.values():
        require((m.received if isinstance(m, Pair) else len(m.rows))
                == PREFIX, "PREFIX_BUDGET")
    return methods


def study_world(mid, seed, fitted):
    require(type(mid) is int and mid in MAPS
            and type(seed) is int and seed in SEEDS, "HELD_WORLD")
    prefix = methods_after_public_prefix(mid, seed, fitted)
    old_ref = {
        "readout": a_slot_high(prefix["archive"]),
        "slot_digest": slot_digest(prefix["archive"]),
        "brier": high_brier(prefix["archive"].slots[0], "H0"),
        "received_A": prefix["archive"].slots[0].assimilated,
    }
    base_scores = {name: score_at_fork(m) for name, m in prefix.items()}
    results = {}
    for branch in FORKS:
        # A new branch receives an identical cold-restored public prefix. No
        # inference branch flag or hidden law is provided to any model.
        methods = {name: cold_copy(m) for name, m in prefix.items()}
        postmiddle = None
        after_k = {name: {} for name in ARMS}
        phase_A = {"archive": [], "switching_bayes": []}
        for t in range(PREFIX, N):
            if t == B_END:
                # At the boundary, score BEFORE observing an unannounced return.
                postmiddle = {
                    name: {
                        "old_A_brier": score_at_fork(m),
                        "slot_A_digest": slot_digest(m) if isinstance(m, Pair) else None,
                        "slot_A_high": a_slot_high(m) if isinstance(m, Pair) else None,
                        "received": m.received if isinstance(m, Pair) else len(m.rows),
                        "assigned": [s.assimilated for s in m.slots]
                        if isinstance(m, Pair) else m.live.assimilated,
                        "quarantined": m.quarantined if isinstance(m, Pair) else 0,
                    }
                    for name, m in methods.items()
                }
                for name, value in postmiddle.items():
                    after_k[name]["0"] = value["old_A_brier"]
                methods = {name: cold_copy(m) for name, m in methods.items()}
            c, a = t % 4, t % 4
            y = private_witness(mid, seed, t, a, branch)
            for m in methods.values():
                m.observe(t, c, a, y)
            for name in phase_A:
                phase_A[name].append(methods[name].belief_a)
            k = t + 1 - B_END
            if k in K:
                for name, m in methods.items():
                    after_k[name][str(k)] = score_at_fork(m)
        require(postmiddle is not None and all(
            set(rows) == {str(k) for k in K}
            for rows in after_k.values()), "RETURN_CHECKPOINTS")
        results[branch] = {
            "at32": postmiddle, "after_k": after_k,
            "last_phase_A_beliefs": {name: vals[-8:]
                                     for name, vals in phase_A.items()},
            "final": {name: {
                "received": m.received if isinstance(m, Pair) else len(m.rows),
                "assigned": [s.assimilated for s in m.slots]
                if isinstance(m, Pair) else m.live.assimilated,
                "quarantined": m.quarantined if isinstance(m, Pair) else 0,
                "cold_eight": [cold_copy(m).prob(c, 0) for c in range(8)],
            } for name, m in methods.items()},
        }
    for branch in FORKS:
        for name in ARMS:
            require(results[branch]["final"][name]["received"] == N,
                    "FINAL_WITNESS_BUDGET")
        # The original t16 A reference was copied before both middle forks.
        require(slot_digest(prefix["archive"]) == old_ref["slot_digest"]
                and a_slot_high(prefix["archive"]) == old_ref["readout"],
                "FROZEN_OLD_A_REFERENCE")
    drift = {
        name: (results["treatment_B"]["at32"][name]["old_A_brier"] -
               results["control_A"]["at32"][name]["old_A_brier"])
        for name in ARMS
    }
    live_a = results["treatment_B"]["at32"]["archive"]
    retained_a = (live_a["slot_A_digest"] == old_ref["slot_digest"]
                  and live_a["slot_A_high"] == old_ref["readout"]
                  and live_a["assigned"][0] == old_ref["received_A"])
    return {
        "map_group": mid, "seed": seed,
        "t16_frozen_A": old_ref, "t16_live_old_A_brier": base_scores,
        "forks": results, "paired_B_specific_old_A_drift": drift,
        "frozen_A_reference_immutable": True,
        "live_A_during_B_bit_exact": retained_a,
        "source_private_inputs_to_policy": False,
        "sequential_actions_per_fork_per_policy": N,
    }


def proof():
    begin = time.monotonic()
    protocol()
    fit = {mid: trained(mid) for mid in MAPS}
    worlds = [study_world(mid, seed, fit[mid])
              for mid in MAPS for seed in SEEDS]
    require(len(worlds) == 24
            and sum(w["sequential_actions_per_fork_per_policy"]
                    for w in worlds) * 2 == 2304, "PRIMARY_BUDGET")
    pairs = {}
    for name in ARMS:
        pairs[name] = {
            "mean_B_specific_old_A_drift": sum(
                w["paired_B_specific_old_A_drift"][name] for w in worlds) / 24,
            "mean_treatment_t32_old_A_brier": sum(
                w["forks"]["treatment_B"]["at32"][name]["old_A_brier"]
                for w in worlds) / 24,
            "mean_control_t32_old_A_brier": sum(
                w["forks"]["control_A"]["at32"][name]["old_A_brier"]
                for w in worlds) / 24,
            "treatment_return_after_k": {
                str(k): sum(w["forks"]["treatment_B"]["after_k"][name][str(k)]
                            for w in worlds) / 24 for k in K
            },
        }
    baseline = sum(w["t16_frozen_A"]["brier"] for w in worlds) / 24
    arc, hmm = pairs["archive"], pairs["switching_bayes"]
    pair_wins = sum(
        w["paired_B_specific_old_A_drift"]["archive"] <
        w["paired_B_specific_old_A_drift"]["switching_bayes"]
        for w in worlds)
    k8_wins = sum(
        w["forks"]["treatment_B"]["after_k"]["archive"]["8"] <
        w["forks"]["treatment_B"]["after_k"]["switching_bayes"]["8"]
        for w in worlds)
    h = {
        "P0_old_A_trained": baseline <= .235,
        "H1_B_specific_drift_below_HMM": (
            arc["mean_B_specific_old_A_drift"] <=
            hmm["mean_B_specific_old_A_drift"] - .005 and pair_wins >= 18),
        "H2_return_k4_k8_below_HMM": (
            all(arc["treatment_return_after_k"][str(k)] <=
                hmm["treatment_return_after_k"][str(k)] - .005
                for k in (4, 8)) and k8_wins >= 18),
        "H3_live_old_A_slot_bit_exact_in_B": all(
            w["live_A_during_B_bit_exact"] and
            w["frozen_A_reference_immutable"] for w in worlds),
        "H4_witness_budget_and_cold": all(
            w["sequential_actions_per_fork_per_policy"] == N and
            all(v["final"][m]["received"] == N
                for v in w["forks"].values() for m in ARMS)
            for w in worlds),
    }
    return {
        "schema": SCHEMA, "prereg_original_commit": PREG,
        "prereg_compat_revision": REV, "protocol_git_blob": PROTO_GIT_BLOB,
        "prior_know30_source_blob":
            "9671ffcef8cd5be62eb62643529eca9cf4bb3471",
        "source_mode": MODE,
        "held_world_pairs": len(worlds),
        "per_method_fork_action_occurrences": 2304,
        "unique_private_events_across_worlds": 1920,
        "pre_fork_fitted_A_old_loss": baseline,
        "per_method": pairs, "paired_worlds": worlds,
        "paired_drift_archive_vs_HMM_wins": pair_wins,
        "return_k8_archive_vs_HMM_wins": k8_wins,
        "frozen_hypotheses": h,
        "development_verdict":
            "DEVELOPMENT_SUPPORTED_SYNTHETIC" if all(h.values())
            else "UNDERTRAINED_OLD_A_NO_RETENTION_CLAIM" if not h[
                "P0_old_A_trained"]
            else "DEVELOPMENT_MIXED_OR_NO_GO",
        "engineering":"PASS",
        "scientific":"SCIENCE_NO_GO_SYNTHETIC_NOT_NATIVE",
        "protected_original_first_use": False,
        "accepted_native_modified": False,
        "deployment":"NONE",
        "script_wall_seconds": time.monotonic() - begin,
    }


if __name__ == "__main__":
    print(json.dumps(proof(), sort_keys=True, indent=2))

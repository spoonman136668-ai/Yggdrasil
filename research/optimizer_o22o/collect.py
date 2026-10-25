"""O22-O: FIT-ONLY complete selected-action receipts from original Farama MiniGrid.

This is an authentic public TRAINING source collection, not DEV, not protected
first-use, not independent evidence that a causal learner learned VOI.
It reuses frozen C25 native action selector without tuning it.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from research.mass_r7c20 import run as c20
from research.mass_r7c22 import run as c22
from research.mass_r7c25 import run as c25
from research.native.itd02.r1.native_policy import canonical

P = json.loads((HERE / "PREREG.json").read_text())


def public_array(state):
    return [state.x, state.y, state.direction, state.goal_x,
            state.goal_y, int(state.front_blocked)]


def one_family(family, seeds, shared_motor_fit):
    model = c25.make("native_active", shared_motor_fit)
    env = c20.env_make(family)
    episodes = []
    counts = collections.Counter()
    turns_blocked = 0
    turns_clear = 0
    probes = 0
    try:
        for seed in seeds:
            obs, _ = env.reset(seed=int(seed))
            goal = c20.goal_from(obs)
            dims = tuple(int(x) for x in obs["image"].shape[:2])
            model.reset_episode(*dims)
            rows = []
            terminal = False
            truncated = False
            for step in range(P["source_max_actions_per_episode"]):
                before = c22.public_dynamic(obs, goal)
                chosen = model.choose(before)
                assert type(chosen) is int and chosen in (0, 1, 2)
                info_turn = bool(model.last_information_probe)
                assert not info_turn or chosen in (0, 1)
                next_obs, reward, terminal, truncated, _ = env.step(chosen)
                after = c22.public_dynamic(next_obs, goal)
                assert type(terminal) is bool and type(truncated) is bool
                reward = float(reward)
                assert reward == reward and abs(reward) <= 1.0
                model.observe(before, chosen, after, reward, terminal, False)
                counts[chosen] += 1
                if info_turn:
                    probes += 1
                    if after.front_blocked:
                        turns_blocked += 1
                    else:
                        turns_clear += 1
                # These are ACTUALLY selected legal actions and their returned
                # original observations, never a fabricated no-op or next state.
                rows.append({
                    "source_step": step,
                    "before": public_array(before),
                    "selected_action": chosen,
                    "returned_after": public_array(after),
                    "source_reward": reward,
                    "terminated": terminal,
                    "truncated": truncated,
                    "information_turn": info_turn,
                    "new_front_after_turn": (
                        "BLOCKED" if after.front_blocked else "CLEAR"
                    ) if info_turn else None,
                })
                obs = next_obs
                if terminal or truncated:
                    break
            # Observational continuation returns from this VERY SAME actual
            # subsequent source trajectory; not an alternate-action causal label.
            g = 0.0
            for row in reversed(rows):
                g = row["source_reward"] + 0.99 * g
                row["own_trajectory_discounted_future_reward"] = round(g, 12)
            receipt = {
                "family": family, "seed_public_fit_role": int(seed),
                "n_selected_actions": len(rows),
                "goal_reached": bool(terminal and rows[-1]["source_reward"] > 0),
                "collision_terminated": bool(terminal and rows[-1]["source_reward"] < 0),
                "horizon_truncated": bool(truncated),
                "rows": rows,
                "rows_sha256": hashlib.sha256(canonical(rows)).hexdigest(),
            }
            episodes.append(receipt)
    finally:
        env.close()
    return episodes, {
        "source_episodes": len(episodes),
        "selected_left": counts[0],
        "selected_right": counts[1],
        "selected_forward": counts[2],
        "actually_selected_information_turns": probes,
        "information_turn_revealed_blocked": turns_blocked,
        "information_turn_revealed_clear": turns_clear,
        "goal_reached": sum(int(e["goal_reached"]) for e in episodes),
        "source_actions": sum(e["n_selected_actions"] for e in episodes),
    }


def main():
    import gymnasium
    import minigrid

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    c20.check_source()
    assert P["upstream_original"].split("@")[-1] == \
        "7f5853792ea7f04f75614661006d87fcf949f26d"
    assert P["roles"]["validation"] == []
    assert P["roles"]["public_development"] == []
    assert P["roles"]["protected_holdout"] == []
    t0 = time.process_time()
    motor_fit, identity, historical_counts = c20.fit_data()
    assert len(motor_fit) == 12
    assert identity == P["original_selected_motor_fit_sha256"]
    t1 = time.process_time()
    totals = {}
    episodes = []
    for fam, seeds in P["roles"]["fit_only"].items():
        rs, summary = one_family(fam, seeds, motor_fit)
        totals[fam] = summary
        episodes.extend(rs)
    t2 = time.process_time()

    actions = {str(i): sum(totals[f]["selected_"+name]
                  for f in totals)
               for i, name in enumerate(("left", "right", "forward"))}
    selected_turn = sum(t["information_turn_revealed_blocked"] for t in totals.values())
    selected_clear = sum(t["information_turn_revealed_clear"] for t in totals.values())
    if any(n == 0 for n in actions.values()):
        decision = "NO_GO_REAL_SOURCE_FIT_ACTION_COVERAGE"
    elif not selected_turn or not selected_clear:
        decision = "NO_GO_REAL_SOURCE_FIT_INFORMATION_OUTCOME_COVERAGE"
    else:
        decision = "FIT_ACTION_AND_INFORMATION_OUTCOME_COVERAGE_ONLY"
    out = {
        "schema": P["schema"],
        "source": P["upstream_original"],
        "original_owner": P["original_native_owner_head"],
        "protocol_sha256": hashlib.sha256((HERE/"PREREG.json").read_bytes()).hexdigest(),
        "source_original_motor_fit_sha256": identity,
        "source_original_motor_fit_rows": len(motor_fit),
        "source_original_motor_fit_counts": historical_counts,
        "fit_role_only": True,
        "development_reset_count": 0,
        "protected_reset_count": 0,
        "policy": P["source_selected_policy"],
        "by_family": totals,
        "selected_actions": actions,
        "episodes": episodes,
        "scientific_admission": decision,
        "resource": {
            "cpu_original_motor_fit_s": round(t1 - t0, 6),
            "cpu_new_public_fit_s": round(t2 - t1, 6),
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "gymnasium_version": gymnasium.__version__,
            "minigrid_version": minigrid.__version__,
        },
    }
    Path(args.out).write_bytes(canonical(out) + b"\n")
    print("O22O_ORIGINAL_SELECTED_ACTION_FIT", json.dumps(
        {"actions": actions, "by_family": totals,
         "scientific_admission": decision}, sort_keys=True), flush=True)
    print("O22O_NEW_DEV_SOURCE_EPISODES=0", flush=True)


if __name__ == "__main__":
    main()

"""MG93 early public-behavior divergence diagnostic; retrospective only.

Input: heldout.json from immutable MG93 original artifact 12972852607.
No original environment execution, no hidden state, no policy retraining.
Metrics are descriptive first-16-selected-action diagnostics, paired on family/seed.
"""
import argparse, json, math, statistics
from collections import Counter, defaultdict
from pathlib import Path

ARTIFACT_ID = 12972852607
ARTIFACT_SHA256 = "9f284ce2b793a2f6e0d0d8a1cb097efb5a9e5ce9b5d75f5c53a77f8474d0104a"
ROLES = ("mg92_native_feedback", "mg91_frozen_native_prototypes",
         "mg91_independent_linear_control", "mg86_frozen_teacher")
PREFIX = 16

def entropy(values):
    counts = Counter(values)
    n = len(values)
    return -sum((c/n) * math.log2(c/n) for c in counts.values())

def episode_metrics(ep):
    rows = ep["source_ledger"][:PREFIX]
    if not rows:
        raise ValueError("EMPTY_EPISODE_PREFIX")
    required = ("before_sha", "after_sha", "action", "reward")
    if any(any(k not in row for k in required) for row in rows):
        raise ValueError("SOURCE_LEDGER_SCHEMA")
    edges = {(r["before_sha"], r["action"], r["after_sha"]) for r in rows}
    return {
        "steps": len(rows),
        "unique_after": len({r["after_sha"] for r in rows}),
        "unique_transition_edges": len(edges),
        "action_entropy_bits": entropy([r["action"] for r in rows]),
        "positive_reward_events": sum(r["reward"] > 0 for r in rows),
        "eventual_success": bool(ep["success"]),
        "terminal_return": ep["return"],
    }

def run(path):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if doc.get("schema") != "yggdrasil.itd02.mg93.immutable-original-feedback-replication.v1":
        raise ValueError("MG93_SCHEMA_MISMATCH")
    episodes = doc["episodes"]
    grouped = defaultdict(dict)
    for ep in episodes:
        if ep["role"] in ROLES:
            key = (ep["family"], ep["seed"])
            if ep["role"] in grouped[key]:
                raise ValueError("DUPLICATE_ROLE_EPISODE")
            grouped[key][ep["role"]] = ep
    if len(grouped) != 12 or any(set(v) != set(ROLES) for v in grouped.values()):
        raise ValueError("EXPECTED_12_PAIRED_SEEDS_AND_4_ROLES")
    per_role = {}
    for role in ROLES:
        rows = [episode_metrics(v[role]) for v in grouped.values()]
        per_role[role] = {
            "episodes": len(rows),
            "unique_after_fraction": statistics.mean(x["unique_after"]/x["steps"] for x in rows),
            "unique_edge_fraction": statistics.mean(x["unique_transition_edges"]/x["steps"] for x in rows),
            "mean_action_entropy_bits": statistics.mean(x["action_entropy_bits"] for x in rows),
            "positive_rewards_first16": sum(x["positive_reward_events"] for x in rows),
            "eventual_successes": sum(x["eventual_success"] for x in rows),
            "mean_terminal_return": statistics.mean(x["terminal_return"] for x in rows),
        }
    pairs = []
    for key, roles in sorted(grouped.items()):
        native = episode_metrics(roles["mg92_native_feedback"])
        teacher = episode_metrics(roles["mg86_frozen_teacher"])
        pairs.append({
            "family": key[0], "seed": key[1],
            "native_unique_after": native["unique_after"],
            "teacher_unique_after": teacher["unique_after"],
            "native_unique_edges": native["unique_transition_edges"],
            "teacher_unique_edges": teacher["unique_transition_edges"],
            "teacher_has_more_unique_after": teacher["unique_after"] > native["unique_after"],
            "teacher_has_more_unique_edges": teacher["unique_transition_edges"] > native["unique_transition_edges"],
        })
    return {
        "schema": "mg93.early_public_behavior_divergence.v1",
        "classification": "RETROSPECTIVE_AUTHENTIC_ORIGINAL_LEDGER_DIAGNOSTIC_NOT_CAUSAL",
        "source_artifact_id": ARTIFACT_ID,
        "source_artifact_sha256": ARTIFACT_SHA256,
        "phase": "heldout",
        "paired_seed_count": len(grouped),
        "prefix_steps": PREFIX,
        "actual_prefix_lengths": {role: [len(v[role]["source_ledger"][:PREFIX]) for v in grouped.values()] for role in ROLES},
        "roles": per_role,
        "native_teacher_paired": pairs,
        "interpretation_limit": "Prefix novelty and action entropy are descriptive diagnostics, not randomized interventions, learned causal explanations, or proof that maximizing novelty improves reward."
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("heldout_json")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run(args.heldout_json)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)

"""MG93 teacher-prefix action-entropy diagnostic; retrospective and exploratory.

Consumes only the immutable MG93 heldout artifact. It does not retrain a model,
run an environment, or infer causal benefit from the descriptive association.
"""
import argparse
import hashlib
import itertools
import json
import math
import statistics
import zipfile
from collections import Counter
from pathlib import Path

ARTIFACT_SHA256 = "9f284ce2b793a2f6e0d0d8a1cb097efb5a9e5ce9b5d75f5c53a77f8474d0104a"
HELDOUT_SHA256 = "0cdb155ce150717c3a678f6c536a81f5f4203dd96acafee459b2fdc1d2a36427"
ROLE = "mg86_frozen_teacher"
WINDOWS = (8, 16, 32)


def entropy(values):
    counts = Counter(values)
    n = len(values)
    return -sum((count / n) * math.log2(count / n) for count in counts.values())


def auc(values, labels):
    positives = [v for v, label in zip(values, labels) if label]
    negatives = [v for v, label in zip(values, labels) if not label]
    if not positives or not negatives:
        raise ValueError("BOTH_OUTCOME_CLASSES_REQUIRED")
    return sum((p > n) + 0.5 * (p == n) for p in positives for n in negatives) / (len(positives) * len(negatives))


def label_reallocation_reference(values, labels):
    """Unstratified combinatorial reference only; NOT a valid inferential p-value."""
    positive_count = sum(labels)
    observed = auc(values, labels)
    null = []
    for positive_indices in itertools.combinations(range(len(values)), positive_count):
        selected = set(positive_indices)
        permuted = [i in selected for i in range(len(values))]
        null.append(auc(values, permuted))
    return {
        "observed_auc": observed,
        "all_unstratified_label_assignments": len(null),
        "fraction_ge_observed_not_an_inferential_p_value": sum(x >= observed - 1e-12 for x in null) / len(null),
    }


def load_artifact(path):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != ARTIFACT_SHA256:
        raise ValueError("MG93_ARTIFACT_SHA256_MISMATCH")
    with zipfile.ZipFile(path) as archive:
        payload = archive.read("heldout.json")
    if hashlib.sha256(payload).hexdigest() != HELDOUT_SHA256:
        raise ValueError("MG93_HELDOUT_SHA256_MISMATCH")
    doc = json.loads(payload)
    if doc.get("schema") != "yggdrasil.itd02.mg93.immutable-original-feedback-replication.v1":
        raise ValueError("MG93_SCHEMA_MISMATCH")
    return doc


def run(path):
    doc = load_artifact(path)
    episodes = [e for e in doc["episodes"] if e["role"] == ROLE]
    episodes.sort(key=lambda e: (e["family"], e["seed"]))
    if len(episodes) != 12 or sum(bool(e["success"]) for e in episodes) != 10:
        raise ValueError("EXPECTED_FROZEN_12_TEACHER_EPISODES_10_SUCCESSES")
    if any(len(e["source_ledger"]) < 8 for e in episodes):
        raise ValueError("UNIFORM_EIGHT_ACTION_PREFIX_UNAVAILABLE")

    results = {}
    for window in WINDOWS:
        per_episode = []
        values = []
        labels = []
        for episode in episodes:
            prefix = episode["source_ledger"][:window]
            if not prefix:
                raise ValueError("EMPTY_EPISODE_PREFIX")
            value = entropy([row["action"] for row in prefix])
            values.append(value)
            labels.append(bool(episode["success"]))
            per_episode.append({
                "family": episode["family"],
                "seed": episode["seed"],
                "success": bool(episode["success"]),
                "terminal_return": episode["return"],
                "actual_prefix_length": len(prefix),
                "prefix_action_entropy_bits": value,
            })
        results[str(window)] = {
            "fixed_horizon": all(len(x["source_ledger"]) >= window for x in episodes),
            "auc_success_ranked_by_entropy": auc(values, labels),
            "success_mean_entropy_bits": statistics.mean(v for v, y in zip(values, labels) if y),
            "failure_mean_entropy_bits": statistics.mean(v for v, y in zip(values, labels) if not y),
            "unstratified_label_reallocation_reference": label_reallocation_reference(values, labels),
            "episodes": per_episode,
        }
    return {
        "schema": "mg93.teacher_prefix_entropy_exploratory.v1",
        "classification": "RETROSPECTIVE_EXPLORATORY_ASSOCIATION_NOT_CAUSAL",
        "source_artifact_id": 12972852607,
        "source_artifact_sha256": ARTIFACT_SHA256,
        "heldout_json_sha256": HELDOUT_SHA256,
        "role": ROLE,
        "n_episodes": 12,
        "successes": 10,
        "failures": 2,
        "primary_fixed_horizon": 8,
        "windows": results,
        "interpretation_limit": "Only the 8-action window is uniform across all 12 episodes. The 16-action window includes one episode already terminal at action 14; the 32-action window has multiple early-terminated episodes. Higher AUC at longer windows may reflect time-to-termination leakage. Labels are clustered by family and the same hand-coded teacher; the unstratified label-reallocation fractions are NOT valid inferential p-values. The teacher is not an equally trained control. Entropy may proxy task difficulty or competent navigation. No intervention or unselected action outcomes exist. Do not optimize entropy directly or claim causal value.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_zip")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run(args.artifact_zip)
    rendered = json.dumps(result, sort_keys=True, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)

"""MG93-AN: leave-one-episode-out public-history predictive sufficiency screen.
Retrospective only: two episode ledgers train exact-key lookup and the third is held out.
"""
import argparse, hashlib, json, zipfile
from collections import defaultdict
from pathlib import Path

ARTIFACT = "9f284ce2b793a2f6e0d0d8a1cb097efb5a9e5ce9b5d75f5c53a77f8474d0104a"
HELDOUT = "0cdb155ce150717c3a678f6c536a81f5f4203dd96acafee459b2fdc1d2a36427"
ROLES = ("mg92_native_feedback", "mg91_frozen_native_prototypes",
         "mg91_independent_linear_control", "mg86_frozen_teacher")

def load(path):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != ARTIFACT:
        raise ValueError("ARTIFACT_SHA_MISMATCH")
    with zipfile.ZipFile(path) as z:
        data = z.read("heldout.json")
    if hashlib.sha256(data).hexdigest() != HELDOUT:
        raise ValueError("HELDOUT_SHA_MISMATCH")
    obj = json.loads(data)
    if obj.get("schema") != "yggdrasil.itd02.mg93.immutable-original-feedback-replication.v1":
        raise ValueError("SCHEMA_MISMATCH")
    return obj

def keys(rows, i):
    row = rows[i]
    prev = rows[i-1] if i else None
    prev2 = rows[i-2] if i > 1 else None
    base = (row["before_sha"], row["action"])
    return (
        base,
        base + (prev["action"] if prev else None,),
        base + ((prev["before_sha"], prev["action"]) if prev else (None, None)),
        base + ((prev2["action"] if prev2 else None), (prev["action"] if prev else None)),
    )

def fold(train, test):
    tables = [defaultdict(set) for _ in range(4)]
    for ep in train:
        rows = ep["source_ledger"]
        for i, row in enumerate(rows):
            for table, key in zip(tables, keys(rows, i)):
                table[key].add(row["after_sha"])
    out = {}
    names = ("public_state_action", "plus_previous_action",
             "plus_previous_public_transition", "plus_previous_two_actions")
    rows = test["source_ledger"]
    for name, table, k in zip(names, tables, range(4)):
        covered = correct = ambiguous = 0
        for i, row in enumerate(rows):
            candidates = table.get(keys(rows, i)[k])
            if not candidates:
                continue
            covered += 1
            if len(candidates) > 1:
                ambiguous += 1
            else:
                correct += int(row["after_sha"] in candidates)
        usable = covered - ambiguous
        out[name] = {
            "steps": len(rows), "covered": covered, "ambiguous": ambiguous,
            "coverage": covered / len(rows) if rows else 0.0,
            "correct": correct,
            "accuracy_on_unambiguous_covered": correct / usable if usable else None,
            "correct_fraction_all_steps": correct / len(rows) if rows else 0.0,
        }
    return out

def run(path):
    doc = load(path)
    groups = defaultdict(list)
    for ep in doc["episodes"]:
        if ep["role"] in ROLES:
            groups[(ep["role"], ep["family"])].append(ep)
    if len(groups) != 16 or any(len(v) != 3 for v in groups.values()):
        raise ValueError("EXPECTED_3_SEEDS_PER_ROLE_FAMILY")
    totals = defaultdict(lambda: {"steps": 0, "covered": 0, "ambiguous": 0, "correct": 0, "folds": 0})
    detail = {}
    for (role, family), episodes in sorted(groups.items()):
        episodes.sort(key=lambda e: e["seed"])
        detail[role + "|" + family] = []
        for held in episodes:
            train = [e for e in episodes if e is not held]
            scores = fold(train, held)
            detail[role + "|" + family].append({"heldout_seed": held["seed"], "scores": scores})
            for name, s in scores.items():
                t = totals[(role, name)]
                for f in ("steps", "covered", "ambiguous", "correct"):
                    t[f] += s[f]
                t["folds"] += 1
    summary = {}
    for (role, name), t in sorted(totals.items()):
        usable = t["covered"] - t["ambiguous"]
        summary.setdefault(role, {})[name] = {
            **t,
            "coverage": t["covered"] / t["steps"] if t["steps"] else 0,
            "accuracy_on_unambiguous_covered": t["correct"] / usable if usable else None,
            "correct_fraction_all_steps": t["correct"] / t["steps"] if t["steps"] else 0,
        }
    return {
        "schema": "mg93.history_cv.public_transition.v1",
        "classification": "RETROSPECTIVE_CROSS_EPISODE_PREDICTIVE_SCREEN_NOT_CAUSAL",
        "artifact_id": 12972852607, "artifact_sha256": ARTIFACT, "heldout_sha256": HELDOUT,
        "method": "For each role and task family, fit exact-key transition lookup on two episodes and score successor digest prediction on the third; rotate all three held-out episodes. Keys use current public digest/action plus optional prior selected public history.",
        "totals": summary, "folds": detail,
        "limitations": [
            "Only three seeds per role/family; estimates are small and clustered.",
            "Exact-key lookup is not a learned recurrent or Bayesian model and is not capacity matched.",
            "More history increases key specificity and can reduce coverage.",
            "Logs are policy-selected and observational; no counterfactual actions or randomized memory intervention.",
            "Public observation digests may alias latent pose or inventory.",
            "No task reward, causal improvement, or unfamiliar-family transfer is inferred."
        ]
    }

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("artifact_zip")
    ap.add_argument("--output")
    a = ap.parse_args()
    rendered = json.dumps(run(a.artifact_zip), sort_keys=True, indent=2)
    if a.output:
        Path(a.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)

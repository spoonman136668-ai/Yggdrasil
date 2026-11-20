"""KNOW17: train intervention-utility scoring from old action/consequence trials.

The native accumulator learns whether a *public, precomputed balanced candidate
split* and action have historically reduced the posterior. Candidate tracking,
the split feature and role-consistency filtering remain analytic, not learned.
Synthetic development only; not an autonomous causal planner or model owner.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import time

TRAIN = (1301, 1403)
TRANSFER = (1601, 1709, 1801)
SEEDS = TRAIN + TRANSFER
ROLES = (0, 1, 2, 3)
PREDS = (975, 976, 977, 978)
PROBE = tuple(range(16))
COMMON = (16, 17)
HELD = tuple(range(18, 34))
SUBJECT_BASE = 4_230_000_000
OBJECT_BASE = 4_240_000_000
JOINT_SHA = "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
IMAGE_SHA = "6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1"
PREREG = "4c032aa491bedf473624c835c1c3b19aee19bbf9"

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def require(condition, code):
    if not condition:
        raise ValueError("YGG_KNOW17_" + code)

def subject(seed, entity):
    require(type(seed) is int and seed in SEEDS
            and type(entity) is int and 0 <= entity < 34, "SUBJECT_DOMAIN")
    payload = f"know17:source-id-v1:{seed}:{entity}".encode("ascii")
    return SUBJECT_BASE + int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") % 5_000_000

def object_id(feature, bit):
    require(type(feature) is int and feature in ROLES
            and type(bit) is int and bit in (0, 1), "OBJECT_DOMAIN")
    payload = f"know17:object-id-v1:{feature}:{bit}".encode("ascii")
    return OBJECT_BASE + int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") % 5_000_000

def patterns(seed):
    require(type(seed) is int and seed in SEEDS, "PATTERN_SEED")
    probes = list(range(16))
    held = list(range(16))
    random.Random(seed * 103 + 31).shuffle(probes)
    random.Random(seed * 103 + 97).shuffle(held)
    return tuple(probes + [0, 15] + held)

def source_rows(seed):
    pat = patterns(seed)
    require(len(set(subject(seed, e) for e in range(34))) == 34
            and len(set(object_id(k, v) for k in ROLES for v in (0, 1))) == 8,
            "SOURCE_IDENTIFIER_COLLISION")
    rows = [
        [subject(seed, e), PREDS[k], object_id(k, (pat[e] >> k) & 1),
         f"know17:s{seed}:e{e:02d}:p{k}"]
        for e in range(34) for k in ROLES
    ]
    return sorted(rows, key=lambda item: item[3])

def source_bundle(seed):
    from yggdrasil.native_cumulative_facts import BUNDLE_SCHEMA
    return canonical({
        "schema": BUNDLE_SCHEMA,
        "source_id": f"know17-source-identical-{seed}",
        "source_kind": "direct_public_observation",
        "source_mode": "engineering_fixture_only",
        "records": source_rows(seed)
    })

def bit(facts, seed, entity, feature):
    q, pred = subject(seed, entity), PREDS[feature]
    pair = [facts.fact(q, pred, object_id(feature, v)) for v in (0, 1)]
    visible = [
        item.get("classification") == "DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
        and item.get("witnessed") is True
        and item.get("source_mode") == "engineering_fixture_only"
        and item.get("source_provenance") == "SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED"
        and item.get("native_accepted") is False
        and item.get("verified_new_real_knowledge") is False
        and item.get("can_write_causal_consequence") is False
        for item in pair
    ]
    return visible.index(True) if visible.count(True) == 1 else None

def public_bits(facts, seed, entity):
    values = tuple(bit(facts, seed, entity, k) for k in ROLES)
    require(all(type(v) is int and v in (0, 1) for v in values),
            "SOURCE_FACT_ABSTAIN")
    return values

def outcome(action, value):
    require(type(action) is int and action in (0, 1)
            and type(value) is int and value in (0, 1), "PUBLIC_OUTCOME")
    return action * value

def balanced(bits, possible):
    require(type(possible) is tuple and possible
            and len(set(possible)) == len(possible)
            and all(type(p) is int and p in ROLES for p in possible),
            "CANDIDATE_SET")
    positive = sum(bits[p] for p in possible)
    return int(positive > 0 and positive * 2 == len(possible))

def update(bits, possible, action, witness):
    require(type(witness) is int and witness in (0, 1), "WITNESS_VALUE")
    return tuple(k for k in possible if outcome(action, bits[k]) == witness)

def training_rows(facts, seed):
    """One-action, reset-posterior exploration; label after witnessed effect.

    Before an action: only public balanced indicator and action. The private
    role is consulted *solely* to supply that action's observable consequence.
    After receipt: count eliminated hypotheses and learn binary utility.
    """
    require(seed in TRAIN, "TRAIN_ONLY")
    rows = []
    pat = patterns(seed)
    no_split = pat.index(0)
    split = pat.index(3)
    extra = pat.index(12)
    for private_role in ROLES:
        schedule = [(no_split, 0), (no_split, 1),
                    (split, 0), (split, 1)]
        if seed == TRAIN[1]:
            schedule.append((extra, 0))
        for e, action in schedule:
            bits = public_bits(facts, seed, e)
            context = balanced(bits, ROLES)
            observed = outcome(action, bits[private_role])
            remaining = update(bits, ROLES, action, observed)
            utility = int(len(remaining) <= len(ROLES) // 2)
            rows.append([context, action, utility])
    require(len(rows) == (16 if seed == TRAIN[0] else 20),
            "EXPLORATION_BUDGET")
    require({(c, a) for c, a, v in rows} ==
            {(0, 0), (0, 1), (1, 0), (1, 1)}, "UTILITY_SUPPORT")
    return rows

def symbolic_utility(rows):
    table = {}
    for c, a, value in rows:
        table.setdefault((c, a), []).append(value)
    require(len(table) == 4, "SYMBOLIC_SUPPORT")
    return {key: Fraction(sum(values), len(values))
            for key, values in table.items()}

def tree_utility(rows):
    """Separate fully fitted conventional binary decision-tree leaves."""
    splits = {}
    for candidate_split in (0, 1):
        for action in (0, 1):
            fit = [value for c, a, value in rows
                   if c == candidate_split and a == action]
            require(fit, "CONVENTIONAL_BRANCH_MISSING")
            splits[(candidate_split, action)] = Fraction(sum(fit), len(fit))
    return lambda c, a: splits[(c, a)]

def policy_query(facts, seed, possible, used, policy, *, rnd=None):
    """Policy sees only public source and previous already observed outcomes."""
    require(callable(policy) or policy in ("oracle", "random",
                       "passive", "zero"), "POLICY")
    if policy == "zero":
        return None
    if policy == "random":
        require(rnd is not None, "RNG")
        options = [(e, a) for e in PROBE for a in (0, 1)
                   if (e, a) not in used]
        return rnd.choice(options)
    if policy == "passive":
        return next(((e, 0) for e in PROBE if (e, 0) not in used), None)
    scored = []
    for e in PROBE:
        bits = public_bits(facts, seed, e)
        context = balanced(bits, possible)
        for a in (0, 1):
            if (e, a) in used:
                continue
            if policy == "oracle":
                value = Fraction(context * a)
            else:
                value = policy(context, a) if callable(policy) else None
            if value is None:
                continue
            require(type(value) in (int, Fraction)
                    and not isinstance(value, bool)
                    and 0 <= value <= 1, "LEARNED_POLICY_FORECAST")
            scored.append((-Fraction(value), subject(seed, e), a, e))
    if not scored or scored[0][0] == 0 and all(q[0] == 0 for q in scored):
        return None
    _, _, a, e = min(scored)
    if -min(scored)[0] <= 0:
        return None
    return e, a

def attempt(facts, seed, private_role, strategy):
    """Private role appears only inside the *post-action* outcome oracle."""
    require(seed in TRANSFER and type(private_role) is int
            and private_role in ROLES, "TRANSFER_ONLY")
    remaining = ROLES
    used = set()
    seen = []
    rng = random.Random(seed * 37 + 5)
    for step in range(2):
        query = policy_query(facts, seed, remaining, used,
                             strategy, rnd=rng)
        if query is None:
            break
        e, action = query
        used.add(query)
        bits = public_bits(facts, seed, e)
        observed = outcome(action, bits[private_role])
        remaining = update(bits, remaining, action, observed)
        require(private_role in remaining, "SECRET_ROLE_LOST")
        seen.append([e, action, observed])
    return {
        "selected": remaining[0] if len(remaining) == 1 else None,
        "remaining": len(remaining),
        "action_count": len(seen),
        "transcript": seen
    }

def prove(installed_session, archived_joint):
    from yggdrasil.native_cumulative_facts import CumulativeNativeFacts
    from yggdrasil.native_context_accumulator import NativeContextAccumulator
    from yggdrasil.native_knowledge_activation import (
        PINNED_PACKED_SHA, PINNED_ROWS, open_installed_session)
    begun = time.monotonic()
    protocol = json.loads(Path(__file__).with_name("know17_protocol.json").read_bytes())
    require(protocol.get("schema") ==
            "yggdrasil.know17.learned-intervention-utility-frozen-dev.v1"
            and protocol.get("seeds", {}).get("training") == list(TRAIN)
            and protocol.get("seeds", {}).get("transfer") == list(TRANSFER)
            and protocol.get("train_protocol", {}).get(
                "training_witness_actions") == 36, "PREREG")
    joint = Path(archived_joint)
    require(joint.is_file() and not joint.is_symlink()
            and digest(joint.read_bytes()) == JOINT_SHA, "ARCHIVED_JOINT")
    all_runs = []
    with open_installed_session(installed_session) as source:
        require(len(source._weights) == PINNED_ROWS == 21_343_681
                and PINNED_PACKED_SHA == IMAGE_SHA, "HISTORICAL_IMAGE")
        old_first, old_last = (tuple(source._weights.row_at(i))
                               for i in (0, PINNED_ROWS - 1))
        previous = CumulativeNativeFacts(source)
        facts = previous
        old_bytes = previous.checkpoint()
        sources = {}
        for seed in SEEDS:
            raw = source_bundle(seed)
            sources[seed] = digest(raw)
            facts, receipt = facts.stage(raw, digest(raw))
            require(receipt["new_unique_facts"] == 136, "SYNTHETIC_SOURCE_STAGE")
        A = training_rows(facts, TRAIN[0])
        B = training_rows(facts, TRAIN[1])
        native = NativeContextAccumulator(context_bits=1).stage_update(
            0, A, digest(canonical(A)), max_degree=2)
        readout_A = tuple(native.predict(0, c, a)
                          for c in (0, 1) for a in (0, 1))
        require(readout_A == (0, 0, 0, 1), "NATIVE_UTILITY_FIT_A")
        native = native.stage_update(0, B, digest(canonical(B)), max_degree=2)
        readout_B = tuple(native.predict(0, c, a)
                          for c in (0, 1) for a in (0, 1))
        require(readout_B == readout_A
                and native.profile_info(0)["batches"] == 2,
                "NATIVE_UTILITY_FIT_B_RETENTION")
        saved = native.checkpoint()
        cold = NativeContextAccumulator.restore(saved, digest(saved))
        require(cold.checkpoint() == saved
                and tuple(cold.predict(0, c, a)
                          for c in (0, 1) for a in (0, 1)) == readout_A,
                "NATIVE_POLICY_COLD_RESTORE")
        full = A + B
        table = symbolic_utility(full)
        tree = tree_utility(full)
        require(tuple(table[c, a] for c in (0, 1) for a in (0, 1)) ==
                readout_A, "EQUAL_INFORMATION_CONTROLS")
        strategies = {
            "native": lambda c, a: cold.predict(0, c, a),
            "symbolic": lambda c, a: table[(c, a)],
            "tree": tree,
            "oracle": "oracle", "random": "random",
            "passive": "passive", "zero": "zero"
        }
        for seed in TRANSFER:
            for role in ROLES:
                row = {"seed": seed, "held_role_index": role,
                       "identification": {}, "transcripts": {}}
                for name, policy in strategies.items():
                    result = attempt(facts, seed, role, policy)
                    row["identification"][name] = int(
                        result["selected"] == role)
                    row["transcripts"][name] = result["transcript"]
                    if name in ("native", "symbolic", "tree", "oracle"):
                        require(result["selected"] == role
                                and result["action_count"] == 2,
                                "LEARNED_TRANSFER_FAILURE")
                require(row["transcripts"]["native"] ==
                        row["transcripts"]["symbolic"] ==
                        row["transcripts"]["tree"] ==
                        row["transcripts"]["oracle"],
                        "QUERY_MATCHED_CONTROL_DRIFT")
                all_runs.append(row)
        stored = facts.checkpoint()
        restored = CumulativeNativeFacts(
            source, stored, checkpoint_sha256=facts.checkpoint_sha256)
        require(restored.checkpoint() == stored
                and previous.checkpoint() == old_bytes,
                "FACTUAL_COLD_DRIFT")
        for seed in SEEDS:
            for e in range(34):
                bits = public_bits(restored, seed, e)
                require(bits == tuple((patterns(seed)[e] >> k) & 1
                                      for k in ROLES), "FACTUAL_RESTORE_READOUT")
        require(source.fact(*old_first)["witnessed"]
                and source.fact(*old_last)["witnessed"]
                and digest(joint.read_bytes()) == JOINT_SHA,
                "ORIGINAL_SOURCE_MUTATION")
    counts = {name: sum(row["identification"][name] for row in all_runs)
              for name in strategies}
    require(len(all_runs) == 12
            and counts["native"] == counts["symbolic"] ==
            counts["tree"] == counts["oracle"] == 12
            and counts["zero"] == counts["passive"] == 0,
            "FROZEN_TRANSFER_METRICS")
    return {
        "schema": "yggdrasil.know17.learned-utility-transfer-dev-result.v1",
        "classification": "ISOLATED_SYNTHETIC_DEVELOPMENT_NO_CANONICAL_TRAINING",
        "preregistration_commit": PREREG,
        "trained_intervention_utility_in_existing_native_accumulator": True,
        "handcrafted_public_balanced_split_feature": True,
        "analytic_candidate_consistency_update_retained": True,
        "train_seeds": list(TRAIN), "held_seeds": list(TRANSFER),
        "source_same_for_four_hidden_roles_per_seed": True,
        "source_identical_qpq_facts": 5 * 136,
        "separately_witnessed_training_actions": 36,
        "held_counterfactual_worlds": 12,
        "held_active_actions_per_policy": 24,
        "old_A_native_policy_readouts_changed": 0,
        "native_policy_checkpoint_sha256": digest(saved),
        "native_policy_checkpoint_bytes": len(saved),
        "native_policy_cold_restored": True,
        "factual_source_cold_restored": True,
        "hidden_role_identification": counts,
        "scientific_decision": "DEV_NO_GO_STRONGEST_CONTROL_TIE",
        "scientific_pass": False,
        "canonical_owner_checkpoint": "UNVERIFIED",
        "original_first_use": False,
        "deployment": "NONE",
        "historical_image_sha256": IMAGE_SHA,
        "archived_amalgam_sha256": JOINT_SHA,
        "per_world": all_runs,
        "wall_seconds_excluding_source_fetch": round(
            time.monotonic() - begun, 6)
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--installed-session", type=Path, required=True)
    parser.add_argument("--joint-checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = prove(args.installed_session, args.joint_checkpoint)
    args.output.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8"
    )
    print("KNOW17_LEARNED_INTERVENTION_DEV=" + json.dumps({
        "native": report["hidden_role_identification"]["native"],
        "symbolic": report["hidden_role_identification"]["symbolic"],
        "zero": report["hidden_role_identification"]["zero"],
        "scientific": report["scientific_decision"]
    }, sort_keys=True))

if __name__ == "__main__":
    main()

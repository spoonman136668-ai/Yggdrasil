"""KNOW08: retrospective functional-retention fingerprint of archived native knowledge.

Read-only replay of the *existing* 1,025 witnessed experimental events before,
during, and after synthetic factual staging and fresh-process-style cold restore.
An in-sample fingerprint and Brier score are NOT prospective science and do
not establish benefit from factual knowledge. No owner checkpoint or new events.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import time

from native_cold_shadow import (
    FrozenNative, JOINT_SHA, NATIVE_SHA, valid_nested, digest, require)
from typed_readout_bridge import TypedFactualReadoutBridge
from explicit_view_projection import ExplicitPublicViewProjection, make_fixture_manifest
from real_image_pairing import bundle

EXPECTED_WITNESSES = 1025
HISTORICAL_IMAGE_SHA = "6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a4cdae3d1"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def fingerprint(learner, *, expected=EXPECTED_WITNESSES):
    """Score final-state *retrospective* old readouts, never a held prediction."""
    ledger = learner._episode_reader()._ledger
    require(type(ledger) is tuple and len(ledger) == expected and
            0 < expected <= 1152, "HISTORICAL_LEDGER_LENGTH")
    count, loss = 0, Fraction(0)
    h = hashlib.sha256()
    unique = set()
    for event in ledger:
        require(type(event) is tuple and len(event) == 6,
                "HISTORICAL_LEDGER_SHAPE")
        identifier, views, first, state, second, reward = event
        require(type(identifier) is str and len(identifier) == 64
                and all(c in "0123456789abcdef" for c in identifier)
                and identifier not in unique, "WITNESS_IDENTITY")
        unique.add(identifier)
        require(type(views) is tuple and len(views) == 2 and
                all(type(v) is tuple and len(v) == 2 and
                    all(type(b) is int and b in (0, 1) for b in v)
                    for v in views) and
                all(type(x) is int and x in (0, 1)
                    for x in (first, state, second, reward)),
                "PUBLIC_EVENT_BITS")
        for view in views:
            transition = learner.experience_forecast(view, first)
            terminal = learner.experience_forecast(view, first, state, second)
            require(type(transition) is Fraction and type(terminal) is Fraction
                    and 0 <= transition <= 1 and 0 <= terminal <= 1,
                    "PUBLIC_FORECAST_RANGE")
            loss += (transition - state) ** 2 + (terminal - reward) ** 2
            h.update(canonical([identifier, list(view), first, state, second,
                                reward, [transition.numerator, transition.denominator],
                                [terminal.numerator, terminal.denominator]]) + b"\n")
            count += 2
    mean = loss / count
    return {"witnesses": len(ledger), "forecast_readouts": count,
            "retrospective_readout_sha256": h.hexdigest(),
            "retrospective_mean_brier_fraction":
                [mean.numerator, mean.denominator],
            "independent_heldout": False, "prequential": False}


def prove(installed_session, joint_checkpoint):
    from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
    from yggdrasil.native_cumulative_facts import CumulativeNativeFacts
    from yggdrasil.native_knowledge_activation import (
        PINNED_ROWS, PINNED_PACKED_SHA, open_installed_session)

    begin = time.monotonic()
    path = Path(joint_checkpoint)
    require(path.is_file() and not path.is_symlink()
            and 0 < path.stat().st_size <= 32 * 1024 * 1024,
            "ARCHIVED_JOINT_PATH")
    joint = path.read_bytes()
    native_raw = valid_nested(joint, JOINT_SHA, NATIVE_SHA)
    native = NativeCumulativeLearner.restore(native_raw, NATIVE_SHA)
    require(native.checkpoint() == native_raw, "NATIVE_COLD_RESTORE")
    before = fingerprint(native)
    shadow = FrozenNative(joint, native_raw, native)

    with open_installed_session(installed_session) as base:
        require(len(base._weights) == PINNED_ROWS == 21_343_681
                and PINNED_PACKED_SHA ==
                "6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1",
                "HISTORICAL_SOURCE_IDENTITY")
        first, last = (tuple(base._weights.row_at(i))
                       for i in (0, PINNED_ROWS - 1))
        original = CumulativeNativeFacts(base)
        original_bytes = original.checkpoint()
        fixture = [
            (4294960000, 901, 4294961000),
            (4294960001, 901, 4294961001),
            (4294961000, 902, 4294962000),
            (4294961001, 902, 4294962001),
        ]
        require(all(not base.fact(*row)["witnessed"] for row in fixture),
                "FIXTURE_COLLIDES_WITH_HISTORICAL_FACT")
        b1 = bundle("know08-retention-fixture-a", [
            [*fixture[0], "a:01"], [*fixture[1], "a:02"]])
        b2 = bundle("know08-retention-fixture-b", [
            [*fixture[2], "b:01"], [*fixture[3], "b:02"]])
        staged1, receipt1 = original.stage(b1, digest(b1))
        staged2, receipt2 = staged1.stage(b2, digest(b2))
        require(receipt1["new_unique_facts"] == 2
                and receipt2["new_unique_facts"] == 2,
                "STAGED_FIXTURE_COUNT")
        during = fingerprint(native)
        cold_facts = CumulativeNativeFacts(
            base, staged2.checkpoint(),
            checkpoint_sha256=staged2.checkpoint_sha256)
        cold_native = NativeCumulativeLearner.restore(native_raw, NATIVE_SHA)
        after = fingerprint(cold_native)
        require(before == during == after,
                "HISTORICAL_FUNCTIONAL_RETENTION_DRIFT")
        require(original.checkpoint() == original_bytes
                and cold_facts.checkpoint() == staged2.checkpoint()
                and native.checkpoint() == cold_native.checkpoint() == native_raw
                and shadow.checkpoint() == joint,
                "IMMUTABLE_BASELINE_DRIFT")
        for fact in fixture:
            require(cold_facts.fact(*fact)["classification"] ==
                    "DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED",
                    "NEW_FIXTURE_FACT_MISSING")
        for fact in (first, last):
            require(cold_facts.fact(*fact)["classification"] ==
                    "HISTORICAL_TRAIN_FACT", "OLD_FACT_ERASED")
        shadow_bridge = TypedFactualReadoutBridge(
            shadow, cold_facts, native_checkpoint_sha256=JOINT_SHA,
            facts_checkpoint_sha256=cold_facts.checkpoint_sha256)
        rows = sorted([[list(first), [[0, 0], [0, 1]]],
                       [list(last), [[1, 1], [1, 0]]]],
                      key=lambda item: item[0])
        mapping, mapping_sha = make_fixture_manifest(
            JOINT_SHA, cold_facts.checkpoint_sha256, rows)
        proposal = ExplicitPublicViewProjection(
            shadow_bridge, mapping, mapping_sha)
        matched_plans = 0
        for fact, view in ((first, (0, 0)), (last, (1, 1))):
            answer = proposal.shadow_plan(*fact)
            require(answer["classification"] == "SYNTHETIC_VIEW_PROPOSAL_ONLY"
                    and answer["native_plan_called"] is True
                    and answer["shadow_plan"] == shadow.plan(view)
                    and answer["native_training_performed"] is False
                    and answer["causal_observation_admitted"] is False,
                    "SHADOW_VS_NATIVE_CONTROL")
            matched_plans += 1
        require(proposal.shadow_plan(0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF)[
                "classification"] == "ABSTAIN_UNKNOWN_FACT",
                "UNKNOWN_ABSTENTION")
        require(fingerprint(native) == before
                and fingerprint(cold_native) == before
                and native.checkpoint() == cold_native.checkpoint() == native_raw
                and shadow.checkpoint() == joint
                and original.checkpoint() == original_bytes,
                "POST_QUERY_RETENTION_DRIFT")
    return {
        "schema": "yggdrasil.know08.archived-native-functional-retention.v1",
        "classification": "RETROSPECTIVE_ENGINEERING_DIAGNOSTIC_ONLY",
        "archived_joint_sha256": JOINT_SHA,
        "native_checkpoint_sha256": NATIVE_SHA,
        "historical_train_fact_rows": 21_343_681,
        **before,
        "before_during_cold_after_fingerprints_identical": True,
        "historical_native_readout_changes": 0,
        "matched_native_only_shadow_plans": matched_plans,
        "new_unique_synthetic_fixture_facts": 4,
        "retained_old_historical_fact_probes": 2,
        "factual_cold_restore": True,
        "old_native_weights_and_ledger_unchanged": True,
        "four_specialist_heads_replayed": False,
        "new_real_world_facts": 0,
        "new_causal_observations": 0,
        "trained_native_improvement": False,
        "scientific_pass": False,
        "owner_accepted_canonical_checkpoint": "UNVERIFIED",
        "deployment": "NONE",
        "wall_seconds_excluding_source_fetch": round(
            time.monotonic() - begin, 6),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--installed-session", type=Path, required=True)
    p.add_argument("--joint-checkpoint", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = prove(args.installed_session, args.joint_checkpoint)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print("KNOW08_RETROSPECTIVE_FUNCTIONAL_RETENTION_PASS " +
          json.dumps({"witnesses": result["witnesses"],
                      "old_readouts_unchanged":
                          result["before_during_cold_after_fingerprints_identical"],
                      "scientific_pass": False}, sort_keys=True))


if __name__ == "__main__":
    main()

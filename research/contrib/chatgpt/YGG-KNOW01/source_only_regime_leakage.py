"""KNOW15 source-only falsification of KNOW14's synthetic regime cue.

No action-outcome labels, oracle role IDs, native fits or causal training are
available to select_cue_without_actions(). Read only direct source-typed
factual Q/P/Q membership in the existing unaccepted NKR08 development overlay.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import time

from same_slot_blind_regime_dev import (
    SEEDS, CUES, FIT, IMAGE_SHA, JOINT_SHA, bundle, canonical, digest,
    fact_bit, subject, world, require
)

PREREG_SHA = "60d05953796d37306fd7d2bae9455d69d30a3526"
SCHEMA = "yggdrasil.know15.source-only-regime-cue-leakage-falsification.v1"


def select_cue_without_actions(facts, seed_index):
    """Choose a unique source-only A/B cue from 256 binary candidate values.

    Does not know private generator roles, native weights, mode P960,
    outcomes, actions or any information from held entities e=32..63.
    """
    require(type(seed_index) is int and 0 <= seed_index < len(SEEDS),
            "SEED_DOMAIN")
    candidates = []
    readouts = 0
    for cue, predicate in enumerate(CUES):
        task_values = []
        for task in (0, 1):
            values = []
            for entity in range(FIT):
                value = fact_bit(
                    facts, subject(seed_index, task, entity),
                    predicate, task, cue
                )
                if type(value) is not int or value not in (0, 1):
                    return {
                        "status": "ABSTAIN_UNQUALIFIED_OR_CONFLICTING_SOURCE",
                        "cue": None, "readouts": readouts,
                        "observed_action_outcomes": 0,
                    }
                values.append(value)
                readouts += 1
            task_values.append(values)
        if (all(v == task_values[0][0] for v in task_values[0])
                and all(v == task_values[1][0] for v in task_values[1])
                and task_values[0][0] != task_values[1][0]):
            candidates.append(cue)
    if len(candidates) != 1:
        return {
            "status": "ABSTAIN_ZERO_OR_MULTIPLE_SOURCE_CUES",
            "cue": None, "readouts": readouts,
            "candidate_count": len(candidates),
            "observed_action_outcomes": 0,
        }
    return {
        "status": "SOURCE_ONLY_UNIQUE_REGIME_CUE",
        "cue": candidates[0],
        "selected_predicate": CUES[candidates[0]],
        "readouts": readouts,
        "membership_probes": 2 * readouts,
        "observed_action_outcomes": 0,
    }


def prove(installed_session, joint_checkpoint, know14_receipt):
    from yggdrasil.native_cumulative_facts import CumulativeNativeFacts
    from yggdrasil.native_knowledge_activation import (
        PINNED_PACKED_SHA, PINNED_ROWS, open_installed_session
    )
    t0 = time.monotonic()
    protocol = json.loads(
        Path(__file__).with_name("know15_protocol.json").read_bytes()
    )
    require(protocol.get("schema") == SCHEMA
            and protocol.get("frozen_seeds") == list(SEEDS)
            and protocol.get("frozen_primary", "").startswith(
                "Factual-only selection"),
            "PREREG_MISMATCH")
    joint_path = Path(joint_checkpoint)
    require(joint_path.is_file() and not joint_path.is_symlink()
            and digest(joint_path.read_bytes()) == JOINT_SHA,
            "ARCHIVED_AMALGAM_CHECKPOINT")
    baseline = json.loads(Path(know14_receipt).read_bytes())
    require(
        baseline.get("schema") ==
        "yggdrasil.know14.blind-regime-cue-dev-result.v1"
        and baseline.get("prereg_sha") ==
        "045048c2869a41817d16deddc1ebc49cb444b245"
        and baseline.get("unique_cues_selected") == 3
        and baseline.get("staged_synthetic_facts") == 1920
        and baseline.get("separately_witnessed_fit_actions") == 384
        and baseline.get("held_action_forecasts") == 384
        and baseline.get("historical_image_sha256") == IMAGE_SHA
        and baseline.get("amalgam_joint_sha256") == JOINT_SHA
        and baseline.get("scientific_pass") is False,
        "KNOW14_SAME_SOURCE_CONTROL_DRIFT"
    )
    results = []
    with open_installed_session(installed_session) as historical:
        require(len(historical._weights) == PINNED_ROWS == 21_343_681
                and PINNED_PACKED_SHA == IMAGE_SHA,
                "ORIGINAL_TRAIN_IMAGE")
        first = tuple(historical._weights.row_at(0))
        last = tuple(historical._weights.row_at(PINNED_ROWS - 1))
        require(historical.fact(*first)["witnessed"]
                and historical.fact(*last)["witnessed"],
                "OLD_FACT_BASELINE")
        pristine = CumulativeNativeFacts(historical)
        facts = pristine
        initial_bytes = pristine.checkpoint()
        for i, seed in enumerate(SEEDS):
            for task in (0, 1):
                raw = bundle(i, task)
                facts, receipt = facts.stage(raw, digest(raw))
                require(receipt["new_unique_facts"] == 320
                        and receipt["native_accepted"] is False,
                        "UNACCEPTED_FIXTURE_ONLY")
            predicted = select_cue_without_actions(facts, i)
            require(predicted["status"] == "SOURCE_ONLY_UNIQUE_REGIME_CUE"
                    and predicted["readouts"] == 256
                    and predicted["membership_probes"] == 512
                    and predicted["observed_action_outcomes"] == 0,
                    "SOURCE_ONLY_BASELINE_DID_NOT_IDENTIFY")
            # PRIVATE evaluator role may be consulted ONLY after source
            # cue selection is complete; never inside the selector.
            hidden_role, _, _ = world(i, 0)
            require(predicted["cue"] == hidden_role,
                    "SOURCE_ONLY_SELECTED_WRONG_ROLE")
            results.append({
                "seed": seed,
                "selected_predicate": predicted["selected_predicate"],
                "same_regime_cue_as_know14": True,
                "source_value_readouts": predicted["readouts"],
                "qpq_membership_queries": predicted["membership_probes"],
                "action_observations_used_to_select_cue": 0
            })
        staged = facts.checkpoint()
        restored = CumulativeNativeFacts(
            historical, staged, checkpoint_sha256=facts.checkpoint_sha256
        )
        require(restored.checkpoint() == staged
                and pristine.checkpoint() == initial_bytes,
                "FACTUAL_BASE_MUTATION")
        for i in range(len(SEEDS)):
            before = select_cue_without_actions(facts, i)
            after = select_cue_without_actions(restored, i)
            require(before == after, "SOURCE_ONLY_COLD_READOUT_DRIFT")
        require(historical.fact(*first)["witnessed"]
                and historical.fact(*last)["witnessed"]
                and digest(joint_path.read_bytes()) == JOINT_SHA,
                "OLD_HISTORICAL_OR_JOINT_CHANGED")
    require(len(results) == 3
            and sum(item["source_value_readouts"] for item in results) == 768
            and sum(item["qpq_membership_queries"] for item in results) == 1536,
            "FROZEN_SOURCE_BUDGET")
    return {
        "schema": "yggdrasil.know15.source-only-regime-falsification-result.v1",
        "classification": "DEVELOPMENT_SOURCE_LEAKAGE_FALSIFICATION",
        "protocol_commit": PREREG_SHA,
        "seeds": list(SEEDS),
        "prior_know14_source_pinned": True,
        "factual_only_regime_cues_correct": len(results),
        "factual_only_total_candidate_bit_readouts": 768,
        "factual_only_membership_queries": 1536,
        "factual_only_action_outcomes_used": 0,
        "know14_native_action_outcomes_used": 384,
        "know14_native_roles_correct": 3,
        "match_previous_native_roles": True,
        "per_seed_results": results,
        "fact_candidate_overlay_cold_restored": True,
        "historical_train_fact_rows": 21_343_681,
        "historical_image_sha256": IMAGE_SHA,
        "original_amalgam_joint_sha256": JOINT_SHA,
        "old_model_modified": False,
        "native_training_performed": False,
        "scientific_result":
            "KNOW14_CUE_IDENTIFICATION_CAUSAL_WITNESSES_NOT_NECESSARY",
        "retention_result_know14_not_overturned": True,
        "independent_causal_intelligence_gain": False,
        "protected_original_first_use": False,
        "canonical_owner_checkpoint": "UNVERIFIED",
        "accepted_main_changed": False,
        "deployment": "NONE",
        "wall_seconds_excluding_source_downloads": round(
            time.monotonic() - t0, 6
        )
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--installed-session", type=Path, required=True)
    parser.add_argument("--joint-checkpoint", type=Path, required=True)
    parser.add_argument("--know14-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    a = parser.parse_args()
    result = prove(a.installed_session, a.joint_checkpoint, a.know14_receipt)
    a.output.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8"
    )
    print("KNOW15_SOURCE_ONLY_FALSIFICATION=" + json.dumps({
        "roles_selected_without_actions":
            result["factual_only_regime_cues_correct"],
        "actions_used": result["factual_only_action_outcomes_used"],
        "conclusion": result["scientific_result"]
    }, sort_keys=True))


if __name__ == "__main__":
    main()

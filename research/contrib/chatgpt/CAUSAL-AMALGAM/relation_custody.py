"""Cold-checkpoint read-only adapter for the relation shadow research module.

This is a consumption-only diagnostic of already admitted public development
witnesses.  The caller must source the native bytes from a separately pinned,
owner-qualified artifact.  This module validates native cold replay but does not
grant source first-use, controller authority, policy action or scientific PASS.
"""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path

from relation_shadow import RelationShadow
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "sources.json"


def require(condition, label):
    if not condition:
        raise ValueError(label)


def audit_native_checkpoint(raw, native_sha256):
    """Independently restore the native checkpoint and audit only revealed rows.

    The learned native projection must select the matching coordinate of BOTH
    public views; ambiguous paired views are excluded rather than guessed.
    Leave-one-cell-out masks use the original development ledger for a historical
    engineering diagnostic, never for prospective scientific admission.
    """
    require(type(raw) is bytes and sha256(raw).hexdigest() == native_sha256,
            "RELATION_NATIVE_CHECKPOINT_PIN")
    native = NativeCumulativeLearner.restore(raw, native_sha256)
    require(native.checkpoint() == raw, "RELATION_NATIVE_COLD_BYTES")
    reader = native._episode_reader()
    info = reader.info()
    projection = info.get("projection")
    require(type(projection) is int and projection in (0, 1),
            "RELATION_NATIVE_PROJECTION")
    original = reader._ledger
    require(len(original) == info.get("count") and len(original) > 0,
            "RELATION_NATIVE_LEDGER_COUNT")
    aligned = tuple(event for event in original
                    if event[1][0][projection] == event[1][1][projection])
    skipped = len(original) - len(aligned)
    require(len(aligned) > 0, "RELATION_NO_ALIGNED_WITNESSES")
    shared = RelationShadow(aligned, projection=projection)
    require(shared.witness_count == len(aligned), "RELATION_SHADOW_LEDGER_COUNT")
    if shared.projection != projection:
        raise ValueError("RELATION_SHADOW_PROJECTION_DRIFT")

    masks = []
    total_error = 0.0
    total_held = 0
    proposed = 0
    for context in (0, 1):
        for missing_action in (0, 1):
            held = tuple(e for e in aligned
                         if e[1][0][projection] == context and
                         e[2] == missing_action)
            if not held:
                continue
            fit = tuple(e for e in aligned
                        if not (e[1][0][projection] == context and
                                e[2] == missing_action))
            # Proposals must never see these held consequence labels.
            candidate = RelationShadow(fit, projection=projection).propose(
                context, missing_action)
            if candidate is None:
                masks.append({"context": context, "action": missing_action,
                              "held": len(held), "status": "ABSTAIN",
                              "decision_eligible": False})
                continue
            require(candidate["identification_status"] == "UNIDENTIFIED_TARGET_ACTION"
                    and candidate["target_action_support"] == 0
                    and candidate["identified_probability_interval"] == (0.0, 1.0)
                    and candidate["decision_forecast"] is None
                    and candidate["decision_eligible"] is False
                    and candidate["decision_authority"] == "NONE_SHADOW_ONLY",
                    "RELATION_MASKED_ACTION_NOT_REFUSED")
            q = candidate["forecast"]
            error = sum((q - row[3]) ** 2 for row in held)
            total_error += error
            total_held += len(held)
            proposed += 1
            masks.append({
                "context": context, "action": missing_action,
                "held": len(held),
                "fit": len(fit),
                "source_other_action_support": candidate["other_action_support"],
                "other_contrast_contexts": candidate["independent_contrast_contexts"],
                "diagnostic_brier": round(error / len(held), 9),
                "neutral_brier": 0.25,
                "status": "HISTORICAL_SHADOW_ONLY",
                "decision_eligible": False,
            })

    require(native.checkpoint() == raw, "RELATION_NATIVE_MUTATED")
    require(reader._ledger == original, "RELATION_ACCEPTED_LEDGER_MUTATED")
    return {
        "source_checkpoint_sha256": native_sha256,
        "verified_native_projection": projection,
        "retained_native_witnesses": len(original),
        "aligned_public_witnesses": len(aligned),
        "skipped_ambiguous_views": skipped,
        "aligned_public_receipts_sha256": shared.witness_sha256,
        "masked_readouts": masks,
        "masked_proposals": proposed,
        "historical_masked_brier_if_proposed": (
            round(total_error / total_held, 9) if total_held else None),
        "historical_masked_held_count": total_held,
        "scope": "UNSCOPED_ARCHIVED_DEVELOPMENT_REPLAY_ONLY",
        "source_actions": 0,
        "checkpoint_updates": 0,
        "new_training": False,
        "decision_authority": "NONE_SHADOW_ONLY",
        "scientific_pass": False,
        "deployment": "NONE",
    }


def run(native_directory):
    manifest = json.loads(MANIFEST.read_bytes())
    receipts = []
    for filename, expected in sorted(manifest["native_artifacts_sha256"].items()):
        raw = (native_directory / filename).read_bytes()
        receipt = audit_native_checkpoint(raw, expected)
        receipt["archive"] = filename
        receipts.append(receipt)
    return {"schema": "yggdrasil.amalgam.relation-custody.v1",
            "archive_count": len(receipts), "archives": receipts,
            "source_actions": 0, "checkpoint_updates": 0,
            "scientific_pass": False, "deployment": "NONE"}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("native_directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.native_directory), sort_keys=True, indent=2))

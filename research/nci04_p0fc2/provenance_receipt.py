"""P0F-C2R: proposal for a content-addressed, UNATTESTED model-evidence envelope.

Advisory engineering artifact only. Does not attest source custody or authorize
original-source execution, protected scientific first-use, acceptance, or merge.
The frozen learner and the P0F-C2 numerical protocol remain unchanged.
"""
from hashlib import sha256
import json
import re
import random

from public_counts import PublicCounts

SCHEMA = "yggdrasil.nci04.p0fc2.model-lineage-envelope.proposal.v1"
FROZEN_DESIGN_BLOB = "42db4b7e285a1ee0423c219febc6892f76d9e875"
LEARNER_BLOB = "6a42b4d1d040d0924dbb153a6dfc1d24c3dc3e10"
SOURCE_COMMITS = {
    "FaramaMiniGridDoorKey8": (
        "7f5853792ea7f04f75614661006d87fcf949f26d", 147, 7),
    "DeepMindPycolabApprehend": (
        "6504c8065dd5322438f23a2a9026649904f3322a", 70, 2),
}
SEEDS = {
    "engineering_only": (699901, 699907, 699911, 699931),
    "train_fit": (700101, 700103, 700109, 700127, 700129, 700171,
                  700181, 700201, 700211, 700223, 700237, 700249,
                  700271, 700277, 700279, 700303, 700307, 700319,
                  700333, 700339),
    "train_validation": (700361, 700369, 700381, 700391),
    "held_development": (701101, 701107, 701111, 701117, 701147, 701159,
                         701171, 701181, 701201, 701209, 701213, 701219),
}
ACTOR_RULE = (
    "python:random.Random(1000003*source_reset_seed+337);"
    "action:actor.randrange(native_action_count);"
    "limit:96 true original source actions;"
    "stop:source termination;"
    "interventions:none"
)


def _is_hash(value, digits):
    return (isinstance(value, str) and
            re.fullmatch("[0-9a-f]{%d}" % digits, value) is not None)


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def training_public_digest(model, episodes, seeds):
    """Digest exact PUBLIC (before, action, after) rows in seed order.

    Must receive precisely the episodes used for model.fit, not a re-rendering
    from actor or source. No held-out observation is needed or imported.
    """
    if not isinstance(episodes, (tuple, list)) or not episodes:
        raise ValueError("P0FC2R_EMPTY_INPUT")
    if len(episodes) != len(seeds):
        raise ValueError("P0FC2R_SEED_EPISODE_COUNT_DRIFT")
    h = sha256(b"P0FC2R_PUBLIC_TRAINING_ROWS_V1\0")
    # Count fitting is order-invariant across episodes; pin by seed so an
    # incidental input enumeration order does not invalidate qualification.
    h.update(len(episodes).to_bytes(4, "big"))
    total_steps = 0
    for seed, episode in sorted(zip(seeds, episodes), key=lambda item: item[0]):
        if not isinstance(episode, (tuple, list)) or not episode:
            raise ValueError("P0FC2R_EMPTY_EPISODE")
        if len(episode) > 96:
            raise ValueError("P0FC2R_ACTION_BUDGET_EXCEEDED")
        h.update(seed.to_bytes(8, "big"))
        h.update(len(episode).to_bytes(4, "big"))
        rng = random.Random(1000003 * seed + 337)
        preceding_after = None
        for row in episode:
            before, action, after = model._row(row)
            if preceding_after is not None and before != preceding_after:
                raise ValueError("P0FC2R_PUBLIC_EPISODE_CONTINUITY_DRIFT")
            preceding_after = after
            if action != rng.randrange(model.action_count):
                raise ValueError("P0FC2R_SOURCE_BLIND_ACTOR_TRACE_MISMATCH")
            h.update(len(before).to_bytes(2, "big"))
            h.update(before)
            h.update(bytes([action]))
            h.update(len(after).to_bytes(2, "big"))
            h.update(after)
            total_steps += 1
    return h.hexdigest(), total_steps


def make_evidence_envelope(model, episodes, seeds, *, source_name,
                           source_commit, cohort, harness_sha256,
                           runtime_contract_sha256, code_blob=LEARNER_BLOB,
                           design_blob=FROZEN_DESIGN_BLOB):
    """Bind exactly identified learner counts + input rows + frozen contracts.

    Returns only a UNATTESTED declaration. External source birth, clean
    worktree, actor provenance, custody, runners and independent qualification
    are mandatory outside this envelope.
    """
    if not isinstance(model, PublicCounts):
        raise ValueError("P0FC2R_UNSUPPORTED_MODEL")
    if source_name not in SOURCE_COMMITS:
        raise ValueError("P0FC2R_UNKNOWN_SOURCE")
    sha, length, actions = SOURCE_COMMITS[source_name]
    if source_commit != sha or (model.length, model.action_count) != (length, actions):
        raise ValueError("P0FC2R_SOURCE_WIRE_IDENTITY_DRIFT")
    if code_blob != LEARNER_BLOB or design_blob != FROZEN_DESIGN_BLOB:
        raise ValueError("P0FC2R_FROZEN_INPUT_IDENTITY_DRIFT")
    if not (_is_hash(harness_sha256, 64) and
            _is_hash(runtime_contract_sha256, 64)):
        raise ValueError("P0FC2R_QUALIFICATION_DEPENDENCIES_MISSING")
    if cohort not in ("engineering_only", "train_fit", "train_combined"):
        raise ValueError("P0FC2R_DISALLOWED_TRAINING_COHORT")
    allowed = (SEEDS["engineering_only"] if cohort == "engineering_only"
               else SEEDS["train_fit"] if cohort == "train_fit"
               else SEEDS["train_fit"] + SEEDS["train_validation"])
    if (not isinstance(seeds, (tuple, list)) or
            any(type(seed) is not int for seed in seeds) or
            len(set(seeds)) != len(seeds) or
            not set(seeds).issubset(set(allowed)) or not seeds):
        raise ValueError("P0FC2R_CONSUMED_OR_UNAUTHORIZED_SEED")
    if cohort in ("train_fit", "train_combined") and set(seeds) != set(allowed):
        raise ValueError("P0FC2R_FROZEN_FIT_COHORT_INCOMPLETE")
    digest, steps = training_public_digest(model, episodes, seeds)
    original = model.canonical_receipt()
    if (original["training_episodes"] != len(episodes) or
            original["training_steps"] != steps):
        raise ValueError("P0FC2R_MODEL_INPUT_COUNT_MISMATCH")
    verification = PublicCounts(model.length, model.action_count).fit(episodes)
    if verification.canonical_receipt() != original:
        raise ValueError("P0FC2R_MODEL_INPUT_CONTENT_MISMATCH")
    payload = {
        "schema": SCHEMA,
        "status": "DECLARED_NOT_INDEPENDENTLY_ATTESTED",
        "source_name": source_name,
        "source_commit_sha1": sha,
        "design_git_blob_sha1": design_blob,
        "learner_git_blob_sha1": code_blob,
        "actor_policy": ACTOR_RULE,
        "cohort": cohort,
        "reset_seeds_by_identity": sorted(seeds),
        "public_training_rows_sha256": digest,
        "harness_sha256": harness_sha256,
        "runtime_contract_sha256": runtime_contract_sha256,
        "learner_count_tables": original,
        "fit_recomputed_from_identical_rows": True,
    }
    # This is NOT an independent source-birth/actor/runner attestation.
    return {"payload": payload, "envelope_sha256": sha256(_canonical(payload)).hexdigest()}

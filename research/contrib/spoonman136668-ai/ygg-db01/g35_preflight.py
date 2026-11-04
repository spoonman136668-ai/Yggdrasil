"""G35 prospective admission preflight, not an execution or science authority.

This validator checks candidate plan integrity and *presence/shape* of required
source-custody inputs. It cannot authenticate independent provenance or approve
primary first-use. Even a structurally complete candidate remains NO-GO.
"""
from __future__ import annotations

import hashlib
import json
import re

SHA256 = re.compile(r"[a-f0-9]{64}\Z")
SHA40 = re.compile(r"[a-f0-9]{40}\Z")
EXPECTED_CONDITIONS = (
    "mapped", "reversed", "sham", "polarity_flip", "phase_shift", "no_feedback"
)
MATCHED_ENERGY = EXPECTED_CONDITIONS[:-1]
EVIDENCE_FIELDS = (
    "source_commit_sha", "task_source_url", "task_license",
    "task_manifest_sha256", "evaluator_commit_sha", "evaluator_sha256",
    "fit_cohort_sha256", "transfer_cohort_sha256",
    "independent_custodian", "prediction_seal_receipt_sha256",
    "label_release_receipt_sha256", "primary_thresholds_receipt_sha256"
)
HASH_FIELDS = frozenset(k for k in EVIDENCE_FIELDS if k.endswith("_sha256"))
COMMIT_FIELDS = frozenset(("source_commit_sha", "evaluator_commit_sha"))
CAPACITY = {
    "width": 4, "height": 4, "channels": 16, "genome_parameters": 398,
    "frames_per_case": 16, "development_steps_per_case": 16,
    "train_updates_per_case": 0, "float_logical_bytes": 8
}


def _fail(message):
    raise ValueError("YGG_G35_FAIL_CLOSED: " + message)


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                      separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("utf-8")).hexdigest()


def budget_proxy(capacity):
    """Analytic upper-bound proxy, not a measurement of Python allocation/CPU."""
    if type(capacity) is not dict or capacity != CAPACITY:
        _fail("capacity or frame/compute budget drift")
    w, h = capacity["width"], capacity["height"]
    neighbors = sum(
        (min(h, y + 2) - max(0, y - 1)) *
        (min(w, x + 2) - max(0, x - 1))
        for y in range(h) for x in range(w))
    frames = capacity["frames_per_case"]
    return {
        "development_cell_updates_per_case": frames * w * h,
        "moore_neighbor_visits_per_case": frames * neighbors,
        "neighbor_channel_reads_proxy": frames * neighbors * capacity["channels"],
        "logical_state_float_bytes": w * h * capacity["channels"] * 8,
        "logical_genome_float_bytes": capacity["genome_parameters"] * 8,
        "not_measured": ["wall_time", "peak_ram", "actual_python_memory",
                         "flops", "learning_budget"],
    }


def inspect(candidate):
    if type(candidate) is not dict or set(candidate) != {
        "schema", "project", "experiment_id", "status", "authority",
        "proposed_design", "external_evidence", "provenance_note"}:
        _fail("candidate schema keys")
    if (candidate["schema"] != "yggdrasil.db01.g35-preflight.v1" or
            candidate["project"] != "Yggdrasil" or
            candidate["experiment_id"] != "YGG-DB01-G35" or
            candidate["status"] != "PROSPECTIVE_INCOMPLETE"):
        _fail("identity/status")
    authority = candidate["authority"]
    if type(authority) is not dict or set(authority) != {
            "primary_execution_allowed", "protected_first_use_allowed",
            "production_authority", "accepted_ref_mutation",
            "scientific_acceptance_authority"} or any(
            type(v) is not bool or v for v in authority.values()):
        _fail("authority must remain explicitly false")
    plan = candidate["proposed_design"]
    if type(plan) is not dict or set(plan) != {
        "capacity", "fit_seed_ids", "transfer_seed_ids",
        "planned_outcomes_per_seed", "conditions", "energy_matched_conditions",
        "per_case_condition_budget", "evidence_class"}:
        _fail("design schema")
    if (type(plan["fit_seed_ids"]) is not list or
            type(plan["transfer_seed_ids"]) is not list):
        _fail("cohorts must be explicit arrays")
    fit, transfer = plan["fit_seed_ids"], plan["transfer_seed_ids"]
    if not (len(fit) == len(transfer) == 8 and
            all(type(x) is int and 0 <= x < 2**32 for x in fit + transfer)
            and len(set(fit + transfer)) == len(fit + transfer)):
        _fail("seed cohort overlap or unbalanced planned seed counts")
    if (plan["planned_outcomes_per_seed"] != [0, 1] or
            plan["conditions"] != list(EXPECTED_CONDITIONS) or
            plan["energy_matched_conditions"] != list(MATCHED_ENERGY) or
            plan["evidence_class"] != "PLANNED_ONLY_NO_TASK_LABELS"):
        _fail("planned labels/conditions/energy group")
    proxy = budget_proxy(plan["capacity"])
    b = plan["per_case_condition_budget"]
    if type(b) is not dict or set(b) != set(EXPECTED_CONDITIONS):
        _fail("condition budgets missing/extra")
    for condition in EXPECTED_CONDITIONS:
        if type(b[condition]) is not dict or b[condition] != {
                "frames": 16, "cell_updates": 256, "train_updates": 0}:
            _fail("unequal/expanded condition budget: " + condition)
    fields = candidate["external_evidence"]
    if type(fields) is not dict or set(fields) != set(EVIDENCE_FIELDS):
        _fail("evidence field names")
    missing = []
    for name in EVIDENCE_FIELDS:
        val = fields[name]
        if val is None:
            missing.append(name)
        elif type(val) is not str or not val.strip():
            _fail("blank or invalid evidence value: " + name)
        elif name in HASH_FIELDS and not SHA256.fullmatch(val):
            _fail("invalid SHA256 shape: " + name)
        elif name in COMMIT_FIELDS and not SHA40.fullmatch(val):
            _fail("invalid commit SHA shape: " + name)
        elif len(val) > 1024:
            _fail("unbounded external evidence field: " + name)
    if candidate["provenance_note"] != (
            "Independent originals unavailable; a declared hash or custodian "
            "string is not custody verification. No protected cohort used."):
        _fail("provenance claim drift")
    return {
        "preflight": ("BLOCKED_MISSING_EVIDENCE" if missing else
                      "STRUCTURE_ONLY_EXTERNAL_AUTHENTICITY_UNVERIFIED"),
        "missing_evidence": missing,
        "source_and_custody_authenticated": False,
        "primary_execution_allowed": False,
        "scientific_acceptance_allowed": False,
        "planned_cohort_class_balance_is_not_observed_labels": True,
        "planning_digest_sha256": canonical_digest(candidate),
        "resource_proxy": proxy,
    }

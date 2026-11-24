"""Source-free native receipt reconstruction; no original source or action execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
CONTRIB = ROOT / "research/contrib/gemini/y2-scdr04-wscm-grid5"
sys.path.insert(0, str(CONTRIB))
from yggdrasil.native_grid5_evidence import NativeGrid5Evidence
from yggdrasil.native_grid5_ingress import SIDE, ACTIONS, HORIZON, public_state, pinned
from scdr_grid5_observer import SCDRGrid5Observer
from test_native_grid5_evidence_dev import receipt

EXPERIMENT = "WSCM-SCDR04-WITNESS-BOUND-01"
PINS = {
    "yggdrasil/native_grid5_evidence.py": "e743a02d194e2e76c6a689268d376bb3d2b4880e",
    "yggdrasil/native_grid5_ingress.py": "2733e0c587ae64ec7e17a550bda243569353dbc4",
    "research/contrib/gemini/y2-scdr04-wscm-grid5/scdr_grid5_observer.py": "9bb942e79041af0745c4bf849f3092917b22422e",
    "research/contrib/chatgpt/WSCM-EPISTEMIC-GUARD-01/guard.py": "4e2970cade642aa46426165d9d74aa6e219ff9dd",
}
DELTAS = {"STAY": (0, 0), "PLUS_X": (1, 0), "MINUS_X": (-1, 0),
          "PLUS_Y": (0, 1), "MINUS_Y": (0, -1)}


def check(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def verify_pins():
    for path, expected in PINS.items():
        actual = subprocess.check_output(["git", "hash-object", "--no-filters", path],
                                         cwd=ROOT, text=True).strip()
        check(actual == expected, "SOURCE_BLOB_DRIFT:" + path)


def move(state, delta):
    return tuple(max(0, min(SIDE - 1, c + d)) for c, d in zip(state, delta))


def witness_bound_readout(evidence, state, action, *, episode_id):
    """A pure development-only diagnostic; no external observer input or actor."""
    if type(evidence) is not NativeGrid5Evidence:
        raise TypeError("NATIVE_EVIDENCE_REQUIRED")
    state = public_state(state)
    if type(action) is not int or not 0 <= action < ACTIONS or not pinned(episode_id):
        raise ValueError("GRID5_QUERY")
    raw = evidence.checkpoint()
    sha = hashlib.sha256(raw).hexdigest()
    records = json.loads(raw)["records"]
    if records:
        validated = NativeGrid5Evidence.restore(raw, sha)
        records = json.loads(validated.checkpoint())["records"]
    else:
        validated = NativeGrid5Evidence()
        check(validated.checkpoint() == raw, "EMPTY_CHECKPOINT_DRIFT")
    # Derive every update from unique, replay-validated, same-episode receipts.
    rows = [row for row in records if row[1] == episode_id]
    observer = SCDRGrid5Observer(grid_size=SIDE)
    for row in rows:
        observer.observe_transition(tuple(row[3]), row[4], tuple(row[5]))
    result = observer.guarded_diagnostic_readout(validated, list(state), action, episode_id=episode_id)
    # Exact independent role control; conditional on the disclosed fixture grammar,
    # not a proof of the real environment law or an authenticated action identity.
    support = [row for row in rows if row[4] == action]
    roles = sorted(name for name, delta in DELTAS.items()
                   if all(move(tuple(row[3]), delta) == tuple(row[5]) for row in support))
    if not support:
        status = "UNWITNESSED"
    elif not roles:
        status = "CONTRADICTION"
    elif len(roles) == 1:
        status = "CONDITIONAL_UNIQUE_ROLE"
    else:
        status = "AMBIGUOUS_ROLE"
    result.update({
        "fixture_episode_id": episode_id,
        "episode_receipt_count": len(rows),
        "action_receipt_count": len(support),
        "grid_side": SIDE,
        "conditional_role_status": status,
        "conditional_roles": roles,
        "conditional_unique_role": roles[0] if status == "CONDITIONAL_UNIQUE_ROLE" else None,
        "conditional_outcomes": sorted(set(move(state, DELTAS[role]) for role in roles)) if support else [],
        "source_authenticated": False,
    })
    check(result["action_admissible"] is False and result["family_authenticated"] is False
          and result["actionable_next_state"] is None, "GUARD_AUTHORITY_DRIFT")
    check(evidence.checkpoint() == raw, "NATIVE_MUTATION")
    return result


def append_line(evidence, episode, sid_base, delta, count):
    before = (0, 0)
    last_receipt = None
    for i in range(count):
        after = move(before, delta)
        last_receipt = receipt(i, act=0, before=before, after=after, episode=episode,
                               sid=f"{sid_base + i:064x}")
        evidence = evidence.observe_public_receipt(*last_receipt)
        before = after
    return evidence, last_receipt


def qualify():
    verify_pins()
    check(SIDE == 9 and ACTIONS == 5 and HORIZON == 50, "NATIVE_CONTRACT_DRIFT")
    a, b, unknown = "a" * 64, "b" * 64, "c" * 64
    small, _ = append_line(NativeGrid5Evidence(), a, 1, (1, 0), 9)
    raw = small.checkpoint()
    plan = small.public_plan([4, 4], episode_id=a)
    old = SCDRGrid5Observer()
    for row in json.loads(raw)["records"]:
        old.observe_transition(tuple(row[3]), row[4], tuple(row[5]))
    before = old.guarded_diagnostic_readout(small, [4, 4], 0, episode_id=a)
    after = witness_bound_readout(small, [4, 4], 0, episode_id=a)
    check(old.grid_size == 5, "OLD_SIDE_DRIFT")
    check(before["scdr_action_role_map"] == "NOVEL_OR_CONTRADICTED", "OLD_NEGATIVE_NOT_REPRODUCED")
    check(after["scdr_action_role_map"] == "PLUS_X" and after["conditional_unique_role"] == "PLUS_X"
          and after["scdr_action_novel_abstain"] < before["scdr_action_novel_abstain"],
          "BOUNDARY_CORRECTION_FAILED")
    check(small.checkpoint() == raw and small.public_plan([4, 4], episode_id=a) == plan,
          "NATIVE_PLAN_DRIFT")

    first, dup = append_line(NativeGrid5Evidence(), a, 100, (1, 0), HORIZON)
    first_read = witness_bound_readout(first, [4, 4], 0, episode_id=a)
    check(first.observe_public_receipt(*dup) is first, "DUPLICATE_NOT_IDEMPOTENT")
    both, _ = append_line(first, b, 200, (0, 1), HORIZON)
    old_a = witness_bound_readout(both, [4, 4], 0, episode_id=a)
    new_b = witness_bound_readout(both, [4, 4], 0, episode_id=b)
    # No hidden global belief: contributor is recreated per episode on each read.
    check(first_read == old_a and old_a["conditional_unique_role"] == "PLUS_X"
          and new_b["conditional_unique_role"] == "PLUS_Y"
          and old_a["episode_receipt_count"] == new_b["episode_receipt_count"] == HORIZON,
          "CROSS_EPISODE_CONTAMINATION")
    both_raw = both.checkpoint()
    cold = NativeGrid5Evidence.restore(both_raw, hashlib.sha256(both_raw).hexdigest())
    check(cold.checkpoint() == both_raw and witness_bound_readout(cold, [4, 4], 0, episode_id=b) == new_b,
          "COLD_RECONSTRUCTION_DRIFT")
    rejected = 0
    try:
        NativeGrid5Evidence.restore(both_raw, "0" * 64)
    except ValueError:
        rejected += 1
    try:
        witness_bound_readout(both, [9, 0], 0, episode_id=a)
    except ValueError:
        rejected += 1
    try:
        witness_bound_readout(both, [4, 4], True, episode_id=a)
    except ValueError:
        rejected += 1
    try:
        witness_bound_readout(both, [4, 4], 0, episode_id=None)
    except ValueError:
        rejected += 1
    check(rejected == 4, "NEGATIVE_REJECTION_COUNT")
    for evidence, episode in ((NativeGrid5Evidence(), a), (both, unknown)):
        empty = witness_bound_readout(evidence, [4, 4], 0, episode_id=episode)
        check(empty["conditional_role_status"] == "UNWITNESSED"
              and empty["action_receipt_count"] == 0 and empty["conditional_unique_role"] is None,
              "UNKNOWN_EPISODE_NOT_ABSTAINED")
    corner, _ = append_line(NativeGrid5Evidence(), a, 400, (0, 0), 2)
    ambiguity = witness_bound_readout(corner, [4, 4], 0, episode_id=a)
    check(ambiguity["conditional_roles"] == ["MINUS_X", "MINUS_Y", "STAY"]
          and ambiguity["conditional_role_status"] == "AMBIGUOUS_ROLE"
          and ambiguity["conditional_unique_role"] is None
          and len(ambiguity["conditional_outcomes"]) == 3, "AMBIGUITY_MISLABELLED")
    # Run the original native Grid5 and guard interfaces, plus contributor suite,
    # without any simulator construction or protected experiment.
    patterns = [
        "test_native_grid5_evidence_dev.py", "test_wscm_grid5_episode_scope_dev.py",
        "test_wscm_native_grid5_dev.py", "test_wscm_grid5_conditional_native_dev.py",
        "test_wscm_grid5_corroboration_dev.py", "test_wscm_grid5_discrimination_preflight_dev.py",
        "test_wscm_grid5_version_space_dev.py", "test_wscm_grid5_learned_delta_dev.py",
        "test_wscm_epistemic_guard01_native.py", "test_wscm_epistemic_guard01_cross_readout.py",
    ]
    totals = {"run": 0, "failures": 0, "errors": 0, "skips": 0}
    for start, pattern in [(ROOT / "tests", p) for p in patterns] + [(CONTRIB, "test_scdr_grid5_observer.py")]:
        suite = unittest.TestLoader().discover(str(start), pattern=pattern)
        res = unittest.TextTestRunner(verbosity=1).run(suite)
        check(res.testsRun > 0 and res.wasSuccessful(), "INHERITED_TEST_FAILURE:" + pattern)
        totals["run"] += res.testsRun
        totals["failures"] += len(res.failures)
        totals["errors"] += len(res.errors)
        totals["skips"] += len(res.skipped)
    return {
        "schema": "yggdrasil.research-scientific-result.v1", "experiment": EXPERIMENT,
        "status": "WITNESS_BOUND_FIXTURE_ENGINEERING_PASS", "scientific_pass": False,
        "scientific_gain_verified": False, "source_first_use": False,
        "metrics": {"source_blobs_verified": len(PINS), "native_side": SIDE, "old_side": old.grid_size,
                    "boundary_fixture_receipts": 9, "old_boundary_map": before["scdr_action_role_map"],
                    "old_novel_mass": before["scdr_action_novel_abstain"],
                    "corrected_boundary_map": after["scdr_action_role_map"],
                    "corrected_novel_mass": after["scdr_action_novel_abstain"],
                    "scoped_fixture_receipts": 100, "episode_a_role": old_a["conditional_unique_role"],
                    "episode_b_role": new_b["conditional_unique_role"], "episode_isolation": True,
                    "duplicate_idempotence": True, "cold_restore_parity": True,
                    "invalid_rejections": rejected, "empty_unknown_scope_abstain": True,
                    "corner_ambiguity_roles": ambiguity["conditional_roles"],
                    "native_checkpoint_and_plan_unchanged": True, "inherited_focused_tests": totals,
                    "source_actions": 0, "original_worlds_constructed": 0, "action_authorized": False,
                    "full_final_regression": "NOT_RUN", "source_authenticated": False},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = qualify()
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes((json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"))

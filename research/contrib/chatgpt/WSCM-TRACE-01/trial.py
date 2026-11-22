"""WSCM-TRACE-01: preregistered, source-free exact trace equivalence trial.

No native-world invocation, training, learning outcome, or held evaluator.
The conventional control is an independent iterative implementation of a
finite-horizon TD(lambda=1/2) eligibility kernel with matched surprise gate.
"""

from __future__ import annotations

import argparse
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import platform
import sys

PREREG_COMMIT = "02cfcf273c706f000175d7aab274db83b4b957c3"
PREREG_BLOB = "9602fe948924833685ad4ccc9f075e0f39319757"
PARENT_COMMIT = "053bafd38531aee961dadf240ca6164a5dab0ef3"
RING_BLOB = "c010d7a74cf95cd579223e0b09f09f1d6cbb899c"
PREDICTIONS = (0, 64, 128, 192, 256)
MAX_N = 17
WINDOW = 16


def git_blob_sha(path):
    payload = Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()


def load_ring(source):
    if git_blob_sha(source) != RING_BLOB:
        raise ValueError("WSCM_TRACE_SOURCE_DRIFT")
    spec = spec_from_file_location("wscm01_delayed_credit_pinned", source)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    if (module.WINDOW, module.SCALE, module.SURPRISE_THRESHOLD) != (16, 256, 128):
        raise ValueError("WSCM_TRACE_SOURCE_PARAMS")
    return module


def conventional_trace(staged, target_id, observed):
    """Independent, equal-input conventional truncated TD(lambda) control.

    Source row: (event_id, action_id, prediction_q8, hypothetical_role).
    No algorithm output is imported from the WSCM ring.
    """
    if type(observed) is not int or observed not in (0, 1):
        raise ValueError("CONTROL_OUTCOME")
    retained = staged[-WINDOW:]
    positions = [i for i, row in enumerate(retained) if row[0] == target_id]
    if not positions:
        return None  # expired target
    target_index = positions[0]
    signed_error = 256 * observed - retained[target_index][2]
    if abs(signed_error) < 128:
        return ()
    weight = 32768
    reverse_proposals = []
    for lag, item in enumerate(reversed(retained[:target_index + 1])):
        reverse_proposals.append((item[0], item[3], lag, weight, signed_error))
        weight //= 2  # lambda=1/2, Q15 integer decay
    return tuple(reversed(reverse_proposals))


def run_trial(source_path):
    ring_module = load_ring(source_path)
    summary = {
        "experiment_id": "WSCM-TRACE-01",
        "preregistration_commit": PREREG_COMMIT,
        "parent_source_commit": PARENT_COMMIT,
        "ring_git_blob": RING_BLOB,
        "case_count": 0,
        "eligible_cases": 0,
        "expired_cases": 0,
        "matching_cases": 0,
        "mismatched_cases": 0,
        "proposal_elements": 0,
        "surprising_cases": 0,
        "nonsurprising_cases": 0,
        "uncontrolled_source_uses": 0,
    }
    transcript = hashlib.sha256()
    for n in range(1, MAX_N + 1):
        for target in range(n):
            for target_q8 in PREDICTIONS:
                for outcome in (0, 1):
                    ring = ring_module.DelayedCreditRing()
                    staged = []
                    for event_id in range(n):
                        row = (event_id, 100 + event_id,
                               target_q8 if event_id == target else 128,
                               event_id % 16)
                        staged.append(row)
                        ring.stage(*row[:3], candidate_role=row[3])
                    conventional = conventional_trace(staged, target, outcome)
                    outcome_id = 1000 + n * 100 + target * 10 + target_q8 + outcome
                    if conventional is None:
                        try:
                            ring.reveal(target, outcome_id, outcome,
                                        charged=True, controlled=True)
                        except ValueError as exc:
                            if str(exc) != "WSCM_TARGET_EXPIRED_OR_UNKNOWN":
                                raise
                            ring_result = "EXPIRED"
                        else:
                            ring_result = "UNEXPECTED_ACCEPT"
                        equal = ring_result == "EXPIRED"
                        summary["expired_cases"] += 1
                    else:
                        ring_result = ring.reveal(target, outcome_id, outcome,
                                                   charged=True, controlled=True)
                        equal = ring_result == conventional
                        summary["eligible_cases"] += 1
                        summary["proposal_elements"] += len(ring_result)
                        if conventional:
                            summary["surprising_cases"] += 1
                        else:
                            summary["nonsurprising_cases"] += 1
                    summary["case_count"] += 1
                    summary["matching_cases" if equal else "mismatched_cases"] += 1
                    # Every public case enters deterministic provenance, no sample selection.
                    record = [n, target, target_q8, outcome, ring_result,
                              conventional if conventional is not None else "EXPIRED"]
                    transcript.update(json.dumps(record, separators=(",", ":"),
                                                 ensure_ascii=True).encode("ascii") + b"\n")
    summary["transcript_sha256"] = transcript.hexdigest()
    if (summary["case_count"] != 1530 or summary["eligible_cases"] != 1520
            or summary["expired_cases"] != 10):
        summary["classification"] = "INVALID_PRECOMMIT_CASE_COUNTS"
    elif summary["mismatched_cases"]:
        summary["classification"] = "CONTROL_MISMATCH_NO_SCIENCE_CLAIM"
    else:
        summary["classification"] = "MECHANISM_EQUIVALENCE_NO_UNIQUE_GAIN"
    summary["scientific_gain_verified"] = False
    summary["native_retention_or_transfer_tested"] = False
    summary["independent_real_source_first_use"] = False
    return summary


def main():
    here = Path(__file__).resolve().parent
    source = here.parent / "CAUSAL-AMALGAM" / "wscm01_delayed_credit.py"
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=here / "result.json")
    parser.add_argument("--provenance", type=Path, default=here / "provenance.json")
    args = parser.parse_args()
    # Preregistration is already frozen on GitHub; when this file is checked out
    # alongside prereg.json, validate that original exact prereg blob as well.
    prereg = here / "prereg.json"
    if prereg.is_file() and git_blob_sha(prereg) != PREREG_BLOB:
        raise ValueError("WSCM_TRACE_PREREG_DRIFT")
    outcome = run_trial(source)
    args.output.write_text(json.dumps(outcome, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    provenance = {
        "experiment_id": "WSCM-TRACE-01",
        "preregistration_commit": PREREG_COMMIT,
        "prereg_git_blob": PREREG_BLOB,
        "code_parent_sha": PARENT_COMMIT,
        "ring_git_blob": RING_BLOB,
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "source_free": True,
        "no_protected_actions": True,
        "cwd": "not-recorded-reproducibility-independent",
    }
    args.provenance.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, sort_keys=True))
    return 0 if outcome["classification"] == "MECHANISM_EQUIVALENCE_NO_UNIQUE_GAIN" else 2


if __name__ == "__main__":
    sys.exit(main())

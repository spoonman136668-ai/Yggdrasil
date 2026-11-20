"""Source-only original Amalgam checkpoint regime-overlap audit.

No model imports, trainer, source actor, forecast or checkpoint writes. The
original archived 1,025 rows were all consumed during engineering research;
this retrospective result is not an independently held scientific test.
"""
import hashlib
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

ZIP_SHA256 = "b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d"
STATE_SHA256 = "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
SOURCE_SHA256 = "20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"
MEMBER = "amalgam-joint-state.json"
RANGES = (
    ("terminal_switch_r0_tail", 891, 912),
    ("context_switch_r1", 912, 976),
    ("invariant_r0", 976, 1024),
    ("single_fixed_engineering", 1024, 1025),
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def expected_id(stage, cohort, seed, index, arm):
    return digest(canonical([stage, SOURCE_SHA256, cohort, seed, index, arm]))


def validate_rows(episodes):
    if len(episodes) != 1025 or len({row[0] for row in episodes}) != 1025:
        raise ValueError("ORIGINAL_LEDGER_COUNT_IDS")
    for i in range(891, 1024):
        if episodes[i][0] != expected_id("ckad25", "ckad25-stream", 56101, i - 832, "coverage_active"):
            raise ValueError("CKAD25_SOURCE_ID_DRIFT")
    if episodes[1024][0] != expected_id("ckad20", "amalgam-growth-engineering-v1", 271991, 0, "engineering"):
        raise ValueError("GROWTH_FIXTURE_ID_DRIFT")
    for row in episodes[891:1025]:
        if (type(row) is not list or len(row) != 6 or
            type(row[1]) is not list or len(row[1]) != 2 or
            any(type(view) is not list or len(view) != 2 for view in row[1]) or
            any(type(bit) is not int or bit not in (0, 1)
                for view in row[1] for bit in view) or
            any(type(bit) is not int or bit not in (0, 1) for bit in row[2:]) or
            row[1][0][0] != row[1][1][0]):
            raise ValueError("PUBLIC_EVENT_SHAPE")


def read_original_archive(path):
    raw = Path(path).read_bytes()
    if digest(raw) != ZIP_SHA256:
        raise ValueError("ORIGINAL_ZIP_PIN")
    with zipfile.ZipFile(path) as z:
        if MEMBER not in z.namelist():
            raise ValueError("ORIGINAL_MEMBER_MISSING")
        state_raw = z.read(MEMBER)
    if digest(state_raw) != STATE_SHA256:
        raise ValueError("ORIGINAL_STATE_PIN")
    state = json.loads(state_raw)
    if state.get("schema") != "yggdrasil.ckad.native-causal-amalgam.v1":
        raise ValueError("ORIGINAL_AMALGAM_SCHEMA")
    native = json.loads(state["native_ascii"])
    if native.get("schema") != "yggdrasil.ckad.native-cumulative-learner.v5":
        raise ValueError("ORIGINAL_NATIVE_SCHEMA")
    episode = json.loads(native["experience_ascii"])
    if (episode.get("schema") != "yggdrasil.ckad.native-episode-experience.v6" or
        episode.get("context_start") != 891 or episode.get("stream_start") != 448 or
        episode.get("refresh_start") != 832 or episode.get("episode_limit") != 1152 or
        episode.get("novel") is not True):
        raise ValueError("ORIGINAL_ACTIVE_CONTEXT_DRIFT")
    rows = episode["episodes"]
    validate_rows(rows)
    return rows


def count_transition(rows, begin, end, *, s1, x1):
    counts = Counter(row[3] for row in rows[begin:end]
                     if row[1][0][0] == s1 and row[2] == x1)
    return {"next_0": counts[0], "next_1": counts[1],
            "total": counts[0] + counts[1]}


def audit(rows):
    validate_rows(rows)
    phases = {}
    for name, start, stop in RANGES:
        phases[name] = {"count": stop - start,
                        "s1_0_transition": {str(x1): count_transition(
                            rows, start, stop, s1=0, x1=x1)
                            for x1 in (0, 1)}}
    first = phases["terminal_switch_r0_tail"]["s1_0_transition"]
    changed = phases["context_switch_r1"]["s1_0_transition"]
    returned = phases["invariant_r0"]["s1_0_transition"]
    for action in ("0", "1"):
        if any(region[action]["total"] == 0 for region in (first, changed, returned)):
            raise ValueError("MISSING_REGIME_TRANSITION_SUPPORT")
    def rate(value):
        return value["next_1"] / value["total"]
    reversals = {
        "x1_0": (rate(first["0"]) < rate(changed["0"]) and
                 rate(returned["0"]) < rate(changed["0"])),
        "x1_1": (rate(first["1"]) > rate(changed["1"]) and
                 rate(returned["1"]) > rate(changed["1"])),
    }
    return {"schema": "yggdrasil.archive-regime-overlap.v1",
            "source_mode": "already_consumed_engineering_archive_read_only",
            "active_context_start": 891, "active_context_rows": 134,
            "phase_counts": phases, "observed_A_B_A_reversals": reversals,
            "full_regression_qualified": False,
            "native_policy_advantage_verified": False,
            "scientific_gain_verified": False,
            "original_world_first_use": 0}


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: archive_regime_overlap_audit.py ARCHIVED_ZIP")
    print(json.dumps(audit(read_original_archive(sys.argv[1])), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

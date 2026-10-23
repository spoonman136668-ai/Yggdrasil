#!/usr/bin/env python3
"""Preregistered PUBLIC engineering smoke on original DTR SCM/PCH; never trains."""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
from isolated_original_dtr_import import original_dtr_classes
from preflight_original_dtr import PIN, BLOBS, command

PREREG_FIRST = "4d31b11b7f7e8156cf0d2e65f8da1fe0ecd54dcb"
CASES = ((920101, (0, 0)), (920102, (1, 1)))

def require(condition: bool, label: str) -> None:
    if not condition:
        raise RuntimeError(label)

def source_identity(source: pathlib.Path) -> dict:
    rev = command(["git", "rev-parse", "HEAD"], source)
    require(rev["exit"] == 0 and rev["stdout"].strip() == PIN,
            "UPSTREAM_SOURCE_HEAD_DRIFT")
    entries = {}
    for path, expected in sorted(BLOBS.items()):
        v = command(["git", "hash-object", "--", path], source)
        require(v["exit"] == 0 and v["stdout"].strip() == expected,
                "UPSTREAM_BLOB_DRIFT:" + path)
        entries[path] = expected
    clean = command(["git", "diff", "--exit-code", "--", "setup.py", "causal_gym"], source)
    require(clean["exit"] == 0, "ORIGINAL_UPSTREAM_WORKTREE_MODIFIED")
    return {"commit": PIN, "pinned_original_blobs": entries}

def binary(value, label: str) -> int:
    require(type(value) is int and value in (0, 1),
            "NONBINARY_" + label)
    return value

def native_run(DTRSCM, DTRPCH, seed, choices, counters):
    # The callbacks below are the entire allowed policy-facing surface.
    pch = DTRPCH()
    s1, reset_info = pch.reset(seed=seed)
    counters["pch_reset_calls"] += 1
    binary(s1, "S1")
    require(isinstance(reset_info, dict), "INVALID_RESET_INFO_TYPE")
    stage0_args = []
    def policy0(public_s1):
        stage0_args.append([public_s1])
        require(public_s1 == s1, "STAGE0_PUBLIC_CONTEXT_MISMATCH")
        return choices[0]
    s2, zero_reward, term1, trunc1, info1 = pch.do(policy0)
    counters["pch_do_calls"] += 1
    require(stage0_args == [[s1]], "STAGE0_CALLBACK_FIELD_LEAK_OR_COUNT")
    binary(s2, "S2")
    require(zero_reward == 0 and term1 is False and trunc1 is False,
            "INVALID_NATIVE_FIRST_STAGE")
    require(isinstance(info1, dict), "INVALID_STAGE1_INFO_TYPE")
    stage1_args = []
    def policy1(public_s1, public_x1, public_s2):
        stage1_args.append([public_s1, public_x1, public_s2])
        require((public_s1, public_x1, public_s2) == (s1, choices[0], s2),
                "STAGE1_PUBLIC_CONTEXT_MISMATCH")
        return choices[1]
    terminal_obs, y, term2, trunc2, info2 = pch.do(policy1)
    counters["pch_do_calls"] += 1
    require(stage1_args == [[s1, choices[0], s2]],
            "STAGE1_CALLBACK_FIELD_LEAK_OR_COUNT")
    binary(y, "TERMINAL_Y")
    require(terminal_obs is None and term2 is True and trunc2 is False,
            "INVALID_NATIVE_TERMINAL_STAGE")
    require(isinstance(info2, dict), "INVALID_STAGE2_INFO_TYPE")

    # Independent *original upstream SCM*, with no copied mechanism.
    # This reference is test-only: never passed to a public policy.
    twin = DTRSCM()
    t_s1, t_reset_info = twin.reset(seed=seed)
    counters["scm_reference_reset_calls"] += 1
    t_s2, t_zero, t_term1, t_trunc1, t_info1 = twin.step(choices[0])
    counters["scm_reference_step_calls"] += 1
    t_final, t_y, t_term2, t_trunc2, t_info2 = twin.step(choices[1])
    counters["scm_reference_step_calls"] += 1
    require((s1, s2, zero_reward, term1, trunc1, terminal_obs, y, term2, trunc2)
            == (t_s1, t_s2, t_zero, t_term1, t_trunc1, t_final, t_y, t_term2, t_trunc2),
            "ORIGINAL_PCH_SCM_SOURCE_PARITY_FAIL")
    require(isinstance(t_reset_info, dict) and
            isinstance(t_info1, dict) and isinstance(t_info2, dict),
            "SCM_REFERENCE_INFO_SHAPE_INVALID")
    counters["completed_public_smoke_episodes"] += 1
    counters["completed_scm_reference_twins"] += 1
    # This is the ENTIRE archived public trace. No hidden source info.
    return {"source_native_reset_seed": seed,
            "source_native_public_s1": s1,
            "public_action_x1": choices[0],
            "source_native_public_s2": s2,
            "first_stage_reward": zero_reward,
            "public_action_x2": choices[1],
            "source_native_terminal_y": y,
            "terminal": bool(term2),
            "truncated": bool(trunc2),
            "allowed_policy_callback_arity": [1, 3],
            "original_scm_twin_parity": "PASS"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    root = pathlib.Path(args.upstream).resolve()
    out = pathlib.Path(args.receipt)
    counts = {"pch_reset_calls": 0, "pch_do_calls": 0,
              "scm_reference_reset_calls": 0, "scm_reference_step_calls": 0,
              "completed_public_smoke_episodes": 0,
              "completed_scm_reference_twins": 0}
    rec = {"schema": "mass.dtr01.preregistered-source-native-public-smoke.v1",
           "frozen_first_prereg_commit": PREREG_FIRST,
           "source_original_environment_not_reimplemented": True,
           "source_role": "PUBLIC_ENGINEERING_ONLY_NOT_FIT_DEV_OR_SEALED",
           "contract": "UPSTREAM_TWO_STAGE_DTR_NATIVE_DO",
           "canonical_whole_package_import_qualified": False,
           "model_fit_updates": 0, "protected_role_episodes": 0,
           "independent_sealed_source_first_use": False,
           "native_yggdrasil_r10_execution": False,
           "controller_admission_observed": False,
           "source_native_public_transcripts": [],
           "counts": counts,
           "disposition": "PUBLIC_ORIGINAL_DTR_NATIVE_ACTION_PATH_SMOKE_NO_GO"}
    try:
        rec["source"] = source_identity(root)
        require(len(CASES) == 2 and all(len(actions) == 2 for _, actions in CASES),
                "PREREG_CORPUS_DRIFT")
        DTRSCM, DTRPCH, _ = original_dtr_classes(root)
        for seed, choices in CASES:
            rec["source_native_public_transcripts"].append(
                native_run(DTRSCM, DTRPCH, seed, choices, counts))
        require(counts == {
            "pch_reset_calls": 2, "pch_do_calls": 4,
            "scm_reference_reset_calls": 2, "scm_reference_step_calls": 4,
            "completed_public_smoke_episodes": 2,
            "completed_scm_reference_twins": 2}, "NATIVE_CALL_COUNT_DRIFT")
        rec["disposition"] = "PUBLIC_ORIGINAL_DTR_NATIVE_ACTION_PATH_SMOKE_PASS"
    except Exception as exc:
        rec["first_failure"] = type(exc).__name__ + ":" + str(exc)[:600]
    finally:
        out.parent.mkdir(parents=True, exist_ok=True)
        rec["canonical_public_transcript_sha256"] = hashlib.sha256(
            json.dumps(rec["source_native_public_transcripts"],
                       sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        out.write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    print(rec["disposition"])
    print("PUBLIC_ENGINEERING_COMPLETED_EPISODES=" + str(counts["completed_public_smoke_episodes"]))
    print("MODEL_FIT_UPDATES=0")
    return 0 if rec["disposition"].endswith("_PASS") else 2

if __name__ == "__main__":
    sys.exit(main())

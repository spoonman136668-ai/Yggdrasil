"""RET1025: cold readout of ORIGINAL Amalgam native class on consumed archive only.

This is a reproduction of historical data, not a new science experiment:
no environment reset/step, no new action, no held-out first use, no trained
model replacement, and no oracle regime labels in the predictor.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

JOINT_LINUX_SHA256 = "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
NATIVE_SHA256 = "5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d"
ORIGINAL_RETURN_SHA256 = "8064affa804d7f011b86210b3564e99ac714c4f26c6e14f0ec2b924c0a7a0797"
ORIGINAL_EPISODE_SHA256 = "3c6433c9e60a0f7e6b750327ae7b705984fb20b25e8bd04fe16a3e9a31c9dde8"
STOP_BEFORE = 976
STOP_AFTER = 1024
EVENTS_TOTAL = 1025
STREAM_START = 448
REFRESH_START = 832
GROWTH_START = 1024

# Pre-existing RET1025 original local readout, NOT a newly selected held target.
EXPECTED_NATIVE = 0.208754978727
EXPECTED_BETA = 0.153910607450
EXPECTED_NEGATIVE_DELTA = 0.054844371277
PRECISION = 1e-9


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_original_archive(linux_file: Path, windows_file: Path | None = None) -> dict:
    """Reject wrong original object; never deserialize as code or execute contents."""
    raw = linux_file.read_bytes()
    if sha(raw) != JOINT_LINUX_SHA256:
        raise ValueError("RET1025_ORIGINAL_JOINT_SHA")
    joint = json.loads(raw)
    if joint.get("schema") != "yggdrasil.ckad.native-causal-amalgam.v1":
        raise ValueError("RET1025_ORIGINAL_SCHEMA")
    nested = joint.get("native_ascii")
    if type(nested) is not str or sha(nested.encode("ascii")) != NATIVE_SHA256:
        raise ValueError("RET1025_ORIGINAL_NATIVE_SHA")
    if windows_file is not None:
        win = json.loads(windows_file.read_bytes())
        if win.get("schema") != joint["schema"] or win.get("native_ascii") != nested:
            raise ValueError("RET1025_ORIGINAL_WINDOWS_NATIVE_MISMATCH")
    native = json.loads(nested)
    raw_episode = native.get("experience_ascii")
    if type(raw_episode) is not str:
        raise ValueError("RET1025_EPISODE_BYTES_NOT_PRESENT")
    ep = json.loads(raw_episode)
    if (len(raw_episode.encode("ascii")) != 93555
            or ep.get("state_sha256") != ORIGINAL_EPISODE_SHA256
            or ep.get("schema") != "yggdrasil.ckad.native-episode-experience.v6"
            or ep.get("stream_start") != STREAM_START
            or ep.get("refresh_start") != REFRESH_START
            or ep.get("episode_limit") != 1152
            or ep.get("repair") is not True
            or len(ep.get("episodes", ())) != EVENTS_TOTAL):
        raise ValueError("RET1025_ORIGINAL_EPISODE_LINEAGE")
    tape = ep["episodes"]
    if digest(canonical(tape[STOP_BEFORE:STOP_AFTER])) != ORIGINAL_RETURN_SHA256:
        raise ValueError("RET1025_RETURN_COHORT_SHA")
    ids = [r[0] for r in tape]
    if len(set(ids)) != EVENTS_TOTAL or any(len(e) != 6 for e in tape):
        raise ValueError("RET1025_DUPLICATE_OR_INVALID_WITNESS")
    return {"episode_ascii":raw_episode,"tape":tape,
            "native_raw_sha256":sha(nested.encode("ascii")),
            "original_joint_sha256":sha(raw)}


def _public_row(e):
    identifier, views, first, state, second, outcome = e
    if (type(views) is not list or len(views) != 2 or
            any(type(v) is not list or len(v) != 2 for v in views)):
        raise ValueError("RET1025_PUBLIC_VIEWS")
    coords = tuple(tuple(v) for v in views)
    return identifier, coords, {"s1":coords[0][0],"x1":first,"s2":state,
                                "x2":second,"y":outcome}


def original_class_replay(tape):
    """Only replay *existing* public witness values into original source class."""
    learner = NativeEpisodeExperience(repair=True)
    pre_return = None
    for i, raw in enumerate(tape):
        if i == STREAM_START:
            learner = learner.begin_stream()
        if i == REFRESH_START:
            learner = learner.enable_context_refresh()
        if i == GROWTH_START:
            learner = learner.extend_witness_capacity()
        if i == STOP_BEFORE:
            pre_return = learner  # immutable source instance retained
        identifier, views, row = _public_row(raw)
        learner = learner.observe(identifier, views, row)
    if pre_return is None:
        raise ValueError("RET1025_NO_PRETURN_NATIVE_STATE")
    return pre_return, learner


def score_without_feedback(pre_return, tape):
    """Predict historical return without updates; source-native then matched Beta."""
    old = tape[:STOP_BEFORE]
    new = tape[STOP_BEFORE:STOP_AFTER]
    counts = defaultdict(lambda: [0, 0])
    for e in old:
        _, views, row = _public_row(e)
        x = views[0][0]
        counts[("transition", x, row["x1"])][row["s2"]] += 1
        counts[("terminal", x, row["x1"], row["s2"], row["x2"])][row["y"]] += 1

    old_checkpoint = pre_return.checkpoint()
    totals = {"native_transition":Fraction(0), "native_terminal":Fraction(0),
              "beta_transition":Fraction(0),"beta_terminal":Fraction(0)}
    for e in new:
        _, views, row = _public_row(e)
        view = views[0]
        first, state, second, outcome = (
            row["x1"],row["s2"],row["x2"],row["y"])
        forecasts = (
            pre_return.context_forecast(view, first),
            pre_return.context_forecast(view, first, state, second))
        keys = (("transition", view[0], first),
                ("terminal", view[0], first, state, second))
        for target, truth, source, key in zip(
                ("transition","terminal"), (state,outcome),forecasts,keys,strict=True):
            n0, n1 = counts[key]
            fitted = Fraction(2*n1+1,2*(n0+n1+1))
            totals["native_"+target] += (source-truth)**2
            totals["beta_"+target] += (fitted-truth)**2
    if pre_return.checkpoint() != old_checkpoint:
        raise ValueError("RET1025_READOUT_MUTATED_NATIVE_STATE")
    n = len(new)
    if n != 48:
        raise ValueError("RET1025_RETURN_COUNT")
    values = {k:float(v/n) for k,v in totals.items()}
    values["native_mean"] = (values["native_transition"]+values["native_terminal"])/2
    values["beta_mean"] = (values["beta_transition"]+values["beta_terminal"])/2
    values["native_minus_beta_mean"] = values["native_mean"]-values["beta_mean"]
    return values, sha(old_checkpoint)


def evaluate(linux_file: Path, windows_file: Path | None = None):
    source=read_original_archive(linux_file,windows_file)
    before, after=original_class_replay(source["tape"])
    original_raw=source["episode_ascii"].encode("ascii")
    # Crucial: original native CLASS has independently reproduced the actual
    # archived complete checkpoint exactly; prior local-only audit didn't.
    if (after.checkpoint()!=original_raw or
            after.info()["state_sha256"]!=ORIGINAL_EPISODE_SHA256):
        raise ValueError("RET1025_ORIGINAL_CLASS_COLD_REPLAY_DRIFT")
    cold=NativeEpisodeExperience.restore(original_raw,sha(original_raw))
    if cold.checkpoint()!=original_raw:
        raise ValueError("RET1025_NATIVE_CLASS_COLD_RESTORE_DRIFT")
    scores,pre_return_sha=score_without_feedback(before,source["tape"])
    for field,old in (("native_mean",EXPECTED_NATIVE),
                      ("beta_mean",EXPECTED_BETA),
                      ("native_minus_beta_mean",EXPECTED_NEGATIVE_DELTA)):
        if abs(scores[field]-old)>PRECISION:
            raise ValueError("RET1025_ORIGINAL_CLASS_SCORE_MISMATCH:"+field)
    if scores["native_minus_beta_mean"]<=0:
        raise ValueError("RET1025_MISSING_ORIGINAL_SCIENTIFIC_NEGATIVE")
    return {
        "schema":"ygg.ret1025.original_native_class_readback.v1",
        "scope":"Already-consumed native development archive, no new first-use",
        "original_joint_sha256":source["original_joint_sha256"],
        "original_native_sha256":source["native_raw_sha256"],
        "original_episode_checkpoint_sha256":sha(original_raw),
        "original_episode_state_sha256":ORIGINAL_EPISODE_SHA256,
        "original_witnesses":EVENTS_TOTAL,
        "frozen_return_start":STOP_BEFORE,
        "frozen_return_end_exclusive":STOP_AFTER,
        "return_witness_sha256":ORIGINAL_RETURN_SHA256,
        "pre_return_checkpoint_sha256":pre_return_sha,
        "original_native_class_exact_final_replay":True,
        "original_native_class_exact_cold_restore":True,
        "return_scored_without_any_updates":True,
        "scores":scores,
        "classification":"RETROSPECTIVE_DEV_NO_GAIN",
        "scientific_gain_verified":False,
        "source_actions_executed":0,
        "accepted_model_updated":False,
    }


if __name__=="__main__":
    if len(sys.argv) not in (2,3):
        raise SystemExit("usage: ret1025_original_class.py LINUX_JSON [WINDOWS_JSON]")
    report=evaluate(Path(sys.argv[1]),Path(sys.argv[2]) if len(sys.argv)==3 else None)
    print(json.dumps(report,sort_keys=True,indent=2))

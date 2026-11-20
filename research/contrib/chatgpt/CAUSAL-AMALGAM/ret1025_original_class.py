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



# RET1025-PROBE-CURVE-DEV01, frozen before scoring: #1355 comment 7053465572.
# Only the original already-consumed public return witnesses may be replayed.
RECOVERY_K = (0, 1, 2, 4, 8, 16, 32)
ORIGINAL_BAYES_SOURCE_BLOB = "659bcac55aba4e90eb27bccf90e9fb4fc2fc2bce"


def _native_pinned_bayes_class():
    """Load *only* exact pinned TransitionControls class AST, not POSIX imports."""
    import ast
    from collections import deque
    raw = (Path(__file__).resolve().parent / "selection_trial.py").read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != ORIGINAL_BAYES_SOURCE_BLOB:
        raise ValueError("RET1025_CONTROL_ORIGINAL_BLOB_DRIFT")
    tree = ast.parse(raw)
    clauses = [n for n in tree.body if isinstance(n, ast.ClassDef)
               and n.name == "TransitionControls"]
    if len(clauses) != 1:
        raise ValueError("RET1025_CONTROL_CLASS_MISSING")
    module = ast.fix_missing_locations(ast.Module(body=clauses, type_ignores=[]))
    env = {"defaultdict":defaultdict, "deque":deque}
    exec(compile(module, "selection_trial.TransitionControls", "exec"), env)
    return env["TransitionControls"]


def _paired_keys(e):
    _, views, row = _public_row(e)
    context = views[0][0]
    return (("transition",context,row["x1"]),row["s2"]), (
        ("terminal",context,row["x1"],row["s2"],row["x2"]),row["y"])


class _HistoryControls:
    """Native source-identical Beta/full/trailing32/change-point32 formulas."""
    def __init__(self):
        self.full = defaultdict(lambda:[0,0])
        self.online = _native_pinned_bayes_class()(32, 1/32)

    def observe(self,e):
        for key,outcome in _paired_keys(e):
            if type(outcome) is not int or outcome not in (0,1):
                raise ValueError("RET1025_INVALID_PUBLIC_OUTCOME")
            self.full[key][outcome] += 1
            self.online.update(key,outcome)

    def forecast(self,key):
        failures,successes=self.full[key]
        full=(successes+0.5)/(successes+failures+1)
        trailing,change_point=self.online.forecast(key)
        return full,trailing,change_point


def _score_remaining(state, control, tape):
    old=state.checkpoint()
    total={n:[0.0,0.0] for n in ("native","full_beta","trailing32_beta","change_point32_beta")}
    for e in tape:
        _,views,row=_public_row(e)
        x=views[0][0]
        a,s,b,y=row["x1"],row["s2"],row["x2"],row["y"]
        predictions=(
            (float(state.context_forecast(views[0],a)),
             float(state.context_forecast(views[0],a,s,b))),
            control.forecast(("transition",x,a)),
            control.forecast(("terminal",x,a,s,b)))
        )
        for target,truth in enumerate((s,y)):
            q=predictions[0][target]
            if not 0<=q<=1:
                raise ValueError("RET1025_NATIVE_INVALID_FORECAST")
            total["native"][target]+=(q-truth)**2
            for name,p in zip(("full_beta","trailing32_beta","change_point32_beta"),
                              predictions[target+1], strict=True):
                if not 0<=p<=1:
                    raise ValueError("RET1025_CONTROL_INVALID_FORECAST")
                total[name][target]+=(p-truth)**2
    if state.checkpoint()!=old:
        raise ValueError("RET1025_READOUT_MUTATED")
    n=len(tape)
    if not n:
        raise ValueError("RET1025_RECOVERY_EMPTY_SUFFIX")
    return {name:{"transition_brier":round(v[0]/n,12),
                  "terminal_brier":round(v[1]/n,12),
                  "mean_brier":round((v[0]+v[1])/(2*n),12)}
            for name,v in total.items()}


def recovery_curve(linux_file:Path, windows_file:Path|None=None):
    """Fixed K-shot future-suffix retrospective readout of original native class."""
    archive=read_original_archive(linux_file,windows_file)
    tape=archive["tape"]
    if RECOVERY_K!=(0,1,2,4,8,16,32) or len(tape)!=1025:
        raise ValueError("RET1025_RECOVERY_MANIFEST_DRIFT")
    state,final=original_class_replay(tape)
    if final.checkpoint()!=archive["episode_ascii"].encode("ascii"):
        raise ValueError("RET1025_ORIGINAL_REPLAY_DRIFT")
    control=_HistoryControls()
    for row in tape[:STOP_BEFORE]:
        control.observe(row)
    updated=0
    results=[]
    for k in RECOVERY_K:
        while updated<k:
            e=tape[STOP_BEFORE+updated]
            identifier,views,row=_public_row(e)
            state=state.observe(identifier,views,row)
            control.observe(e)
            updated+=1
        end=STOP_BEFORE+k
        if len(state._ledger)!=end:
            raise ValueError("RET1025_RECOVERY_LEAK_OR_MISSING_EVIDENCE")
        snapshot=state.checkpoint()
        cold=NativeEpisodeExperience.restore(snapshot,sha(snapshot))
        if cold.checkpoint()!=snapshot:
            raise ValueError("RET1025_COLD_RESTORE_DRIFT")
        scores=_score_remaining(cold,control,tape[end:STOP_AFTER])
        best=min((scores[n]["mean_brier"],n) for n in
                 ("full_beta","trailing32_beta","change_point32_beta"))
        weights=cold._context_weights
        if not weights or sum(weights,Fraction(0))!=1:
            raise ValueError("RET1025_RECOVERY_INVALID_POSTERIOR")
        results.append({
            "k_prior_return_witnesses":k,
            "public_prefix_count":end,
            "historical_future_score_count":STOP_AFTER-end,
            "public_prefix_sha256":digest(canonical(tape[:end])),
            "consumed_return_prefix_sha256":digest(canonical(tape[STOP_BEFORE:end])),
            "cold_native_sha256":sha(snapshot),
            "cold_restoration_exact":True,
            "context_component_count":len(weights),
            "highest_posterior_weight":round(float(max(weights)),12),
            "stream_detections":len(cold._stream_detections),
            "brier":scores,
            "best_conventional":best[1],
            "native_minus_best":round(scores["native"]["mean_brier"]-best[0],12),
            "candidate_beats_all_controls_by_0_005":
                scores["native"]["mean_brier"]<=best[0]-0.005,
        })
    if abs(results[0]["brier"]["native"]["mean_brier"]-EXPECTED_NATIVE)>PRECISION:
        raise ValueError("RET1025_ZERO_PROBE_NATIVE_REGRESSION")
    if abs(results[0]["brier"]["full_beta"]["mean_brier"]-EXPECTED_BETA)>PRECISION:
        raise ValueError("RET1025_ZERO_PROBE_BETA_REGRESSION")
    positive=all(x["candidate_beats_all_controls_by_0_005"] for x in results
                 if x["k_prior_return_witnesses"] in (1,2,4,8))
    return {
        "schema":"ygg.ret1025.native-return-recovery-dev.v1",
        "pre_result_freeze":"https://github.com/spoonman136668-ai/Yggdrasil/pull/1355#issuecomment-7053465572",
        "classification":("RET1025_RECOVERY_DEV_SIGNAL_ONLY" if positive
                          else "RET1025_RECOVERY_DEV_NO_PAIRED_GAIN"),
        "fixed_probe_counts":list(RECOVERY_K),
        "original_joint_sha256":archive["original_joint_sha256"],
        "native_source_unchanged":True,
        "full_native_checkpoint_replay_exact":True,
        "all_cold_restores_exact":True,
        "results":results,
        "scientific_gain_verified":False,
        "source_actions_executed":0,
        "already_consumed_historical_source_only":True,
        "accepted_model_updated":False,
    }

if __name__=="__main__":
    if len(sys.argv) in (3,4) and sys.argv[1]=="--recovery-dev":
        output=recovery_curve(Path(sys.argv[2]),
                              Path(sys.argv[3]) if len(sys.argv)==4 else None)
        print(json.dumps(output,sort_keys=True,indent=2))
        raise SystemExit(0)
    if len(sys.argv) not in (2,3):
        raise SystemExit("usage: ret1025_original_class.py [--recovery-dev] LINUX_JSON [WINDOWS_JSON]")
    report=evaluate(Path(sys.argv[1]),Path(sys.argv[2]) if len(sys.argv)==3 else None)
    print(json.dumps(report,sort_keys=True,indent=2))

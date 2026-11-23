"""WSCM-COLD-READ-01 read-only full/pooled native forecast ablation.

The original NativeEpisodeExperience checkpoint is restored with repository
code at exact Amalgam parent; readout candidates do not train, promote,
intervene, or mutate it. Input is archived GitHub Actions artifact #14492525071,
plus three already-consumed original prequential development traces.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256, sha1
import argparse
import json
from pathlib import Path

from yggdrasil.native_episode_experience import NativeEpisodeExperience, _probability

ARTIFACT_SHA = "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
EXPERIENCE_STATE_SHA = "3c6433c9e60a0f7e6b750327ae7b705984fb20b25e8bd04fe16a3e9a31c9dde8"
NATIVE_SHA = "5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d"
NATIVE_PARENT_SHA = "a00119c73a6431172c19b39ec67a1d94b470897a32c55c1c946071793f37dcc4"
PARENT_GIT_SHA = "86264b41a08d49f558418c0fba367f3a2636befa"
SCALE = 1_000_000
TRACES = {
    818621: "7b3f2ff0b120d6557d4630de3461276d892b503f",
    818653: "bac19fb71d2a9918bd4ede1d3f2e6bae7b81dc48",
    818687: "449a186109b0b30ec98352b5b4565e2e96435b14",
}
ARMS = ("default", "full", "pooled", "unguarded", "fit_full", "fit_trailing", "fit_change_point")


def load_native(joint_path):
    raw = Path(joint_path).read_bytes()
    if sha256(raw).hexdigest() != ARTIFACT_SHA:
        raise ValueError("WSCM_JOINT_ARTIFACT_SHA")
    joint = json.loads(raw)
    if joint.get("native_parent_sha256") != NATIVE_PARENT_SHA:
        raise ValueError("WSCM_PARENT_SOURCE_SHA")
    native = joint["native_ascii"].encode("ascii")
    if sha256(native).hexdigest() != NATIVE_SHA:
        raise ValueError("WSCM_NATIVE_CHECKPOINT_SHA")
    data = json.loads(native)
    read = data["experience_ascii"].encode("ascii")
    expected_experience = json.loads(read)
    if (len(expected_experience["episodes"]) != 1025 or
            expected_experience.get("state_sha256") != EXPERIENCE_STATE_SHA):
        raise ValueError("WSCM_EXPERIENCE_CUSTODY")
    restored = NativeEpisodeExperience.restore(read, sha256(read).hexdigest())
    if restored.checkpoint() != read or restored._state_digest() != EXPERIENCE_STATE_SHA:
        raise ValueError("WSCM_COLD_REPLAY_DRIFT")
    return restored


def _candidate_from_model(model, view, first, state, second, arm):
    if arm == "full":
        return model.forecast(view, first, state, second, full=True)
    if arm != "pooled":
        raise ValueError("WSCM_READOUT_ARM")
    bank, slots, _loss, action = model._cell_choices(view, first, state, second)
    return _probability(bank, slots[1], action)


def forecast(restored, view, first, state=None, second=None, *, arm="default"):
    """Pure read with matching conditional terminal Bayes mixture weights."""
    if arm == "default":
        return restored.context_forecast(view, first, state, second)
    if arm not in ("full", "pooled"):
        raise ValueError("WSCM_READOUT_ARM")
    models = [item[3] for item in restored._context_models]
    weights = restored._context_weights
    if not models or len(models) != len(weights):
        raise ValueError("WSCM_CONTEXT_MODELS")
    predictions = [_candidate_from_model(m, view, first, state, second, arm)
                   for m in models]
    if state is None:
        return sum((w * p for w, p in zip(weights, predictions, strict=True)), Fraction(0))
    transition = [_candidate_from_model(m, view, first, None, None, arm)
                  for m in models]
    support = [w * (p if state else 1-p)
               for w, p in zip(weights, transition, strict=True)]
    total = sum(support, Fraction(0))
    if total <= 0:
        raise ValueError("WSCM_ZERO_SUPPORT")
    return sum((w * p for w, p in zip(support, predictions, strict=True)),
               Fraction(0)) / total


def _git_blob(raw):
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()


def audit(joint_path, source_root):
    native = load_native(joint_path)
    source_root = Path(source_root)
    before = native.checkpoint()
    stats, parity, seed_checks = {}, 0, []
    for seed, expected_blob in TRACES.items():
        path = source_root / ("research/contrib/chatgpt/CAUSAL-AMALGAM/"
                              f"staged-retention-dev-01/seed-{seed}/trace.json")
        raw = path.read_bytes()
        if _git_blob(raw) != expected_blob:
            raise ValueError("WSCM_TRACE_SOURCE_BLOB")
        records = json.loads(raw)
        if len(records) != 72:
            raise ValueError("WSCM_SOURCE_COUNT")
        matched = 0
        for i, rec in enumerate(records):
            if rec.get("stage") != 1 + i // 24:
                raise ValueError("WSCM_STAGE_DRIFT")
            views = rec["views"]
            ctx = views[0][0]
            first, state, second = (rec["row"][k] for k in ("x1", "s2", "x2"))
            reward = rec["row"]["y"]
            if (rec["row"]["s1"] != ctx or
                    any(type(x) is not int or x not in (0, 1)
                        for x in (ctx, first, state, second, reward))):
                raise ValueError("WSCM_PUBLIC_CONTRACT")
            view = tuple(views[0])
            predictions = {
                arm: [round(forecast(native, view, first, arm=arm) * SCALE),
                      round(forecast(native, view, first, state, second, arm=arm) * SCALE)]
                for arm in ("default", "full", "pooled")
            }
            if predictions["default"] != rec["forecast"]["pinned"]:
                raise ValueError("WSCM_NATIVE_PINNED_PARITY")
            matched += 1
            parity += 1
            for arm in ("unguarded", "fit_full", "fit_trailing", "fit_change_point"):
                predictions[arm] = rec["forecast"][arm]
            key = (rec["stage"], ctx)
            cell = stats.setdefault(key, {"n": 0, "loss": {name: [0,0] for name in ARMS}})
            cell["n"] += 1
            for arm in ARMS:
                for target, truth in enumerate((state, reward)):
                    cell["loss"][arm][target] += (predictions[arm][target] - SCALE * truth)**2
        seed_checks.append({"seed": seed, "trace_git_blob": expected_blob,
                            "exact_pinned_parity": matched, "events": len(records)})
    out = []
    for (stage, context), cell in sorted(stats.items()):
        n = cell["n"]
        briers = {name: [round(x / (n * SCALE**2), 9) for x in cell["loss"][name]]
                  for name in ARMS}
        avg = {name: round(sum(briers[name])/2, 9) for name in ARMS}
        out.append({"stage": stage, "public_context": context, "count": n,
                    "target_brier": briers, "mean_brier": avg,
                    "forced_full_minus_default": round(avg["full"]-avg["default"], 9),
                    "forced_pooled_minus_default": round(avg["pooled"]-avg["default"], 9)})
    if native.checkpoint() != before:
        raise ValueError("WSCM_NATIVE_STATE_MUTATION")
    return {"schema":"yggdrasil.wscm.cold-readout-ablation-01.v1",
            "source_git_head":PARENT_GIT_SHA,
            "joint_artifact_sha256":ARTIFACT_SHA,
            "native_episode_source_git_blob":"5a18b00a4c4131526e71f51d63dfd9eb9471c81e",
            "readout_only":True,"new_world_actions":0,"new_training_steps":0,
            "prospective_scientific_trial":False,"scientific_gain_verified":False,
            "total_exact_default_parity":parity,"seed_sources":seed_checks,
            "cells":out}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--joint",required=True,type=Path)
    parser.add_argument("--repo",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    result=audit(args.joint,args.repo)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("WSCM_COLD_READ_ONLY",result["total_exact_default_parity"],"pinned parity rows")


if __name__=="__main__":
    main()

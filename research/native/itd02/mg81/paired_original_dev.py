#!/usr/bin/env python3
"""MG81 prospective ORIGINAL Farama MiniGrid, unchanged native Yggdrasil MG28/MG37.

DEV and heldout runs use real env.step(action) with exact original public fields.
No privileged simulator state, source-free imitation, synthetic rewards, or oracle.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

from research.native.itd02.mg19.original_mission_cells import (
    OriginalMissionAdapter, original_public)
from research.native.itd02.mg28.selected_change_cells import SelectedChangeCells
from research.native.itd02.mg37.source_bridge import SelectedProgressCells
from research.native.itd02.r10.public_adapter import canonical, digest

UPSTREAM = "7f5853792ea7f04f75614661006d87fcf949f26d"
DOORKEY_BLOB = "df5b29ef063be34e6d83b8b478e092c6e3e01512"
PREREG = "8f2273b01fb5b3a957417fbc6f71d23e1fe704be"
MG80 = "aa05346f5844c68c700280b5af63b022a58c3bc4"
FAMILIES = (
    ("MiniGrid-KeyCorridorS3R2-v0", "minigrid.envs:KeyCorridorEnv",
     (2111101, 2111103), 3111107),
    ("MiniGrid-KeyCorridorS4R3-v0", "minigrid.envs:KeyCorridorEnv",
     (2111201, 2111203), 3111207),
    ("MiniGrid-ObstructedMaze-1Dl-v0", "minigrid.envs:ObstructedMaze_1Dlhb",
     (2111301, 2111303), 3111307),
)
BLOBS = {
    "research/native/itd02/mg37/source_bridge.py":
        "ed9184349dc74b43d8a28e18ac1d558512b7948c",
    "research/native/itd02/mg37/progress_cells.py":
        "175c4a7e2ed83a37c2f103339aefc9a4e95eca86",
    "research/native/itd02/mg28/selected_change_cells.py":
        "2c30ca4da6f6603ecc5ec36b1f460a246b120d89",
}
ROLES = ("mg37_reward_guard", "mg28_parent")
CAP = 96

def git(*args, cwd=None):
    p = subprocess.run(("git", *args), cwd=cwd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError("MG81_GIT_SOURCE_IDENTITY_FAIL: " +
                           " ".join(args) + ": " + p.stderr[-150:])
    return p.stdout.strip()

def preflight():
    for pin in (PREREG, MG80):
        git("merge-base", "--is-ancestor", pin, "HEAD")
    for path, expected in BLOBS.items():
        if git("hash-object", path) != expected:
            raise RuntimeError("MG81_NATIVE_FROZEN_SOURCE_CHANGED: " + path)
    content = Path("research/native/itd02/mg81/PREREG.md").read_text("utf-8")
    if (UPSTREAM not in content or
        "2111101" not in content or "3111307" not in content or
        git("hash-object", "research/native/itd02/mg81/PREREG.md") !=
        git("rev-parse", PREREG + ":research/native/itd02/mg81/PREREG.md")):
        raise RuntimeError("MG81_PREREG_SOURCE_DRIFT")
    if len({s for _, _, pair, val in FAMILIES for s in (*pair,val)}) != 9:
        raise RuntimeError("MG81_SEED_COHORT_NOT_DISTINCT")
    print("MG81_PROSPECTIVE_PREREG_AND_NATIVE_SOURCE_FROZEN_PASS")

def check_original(source):
    import gymnasium as gym
    import minigrid
    root = Path(source).resolve()
    location = Path(minigrid.__file__).resolve()
    if not location.is_relative_to(root):
        raise RuntimeError("MG81_NOT_IMPORTED_PINNED_ORIGINAL_MINIGRID")
    if git("rev-parse", "HEAD", cwd=root) != UPSTREAM:
        raise RuntimeError("MG81_ORIGINAL_FARAMA_REVISION_DRIFT")
    if git("hash-object", "minigrid/envs/doorkey.py", cwd=root) != DOORKEY_BLOB:
        raise RuntimeError("MG81_ORIGINAL_FARAMA_DOORKEY_BLOB_DRIFT")
    for family, entry, _, _ in FAMILIES:
        if gym.spec(family).entry_point != entry:
            raise RuntimeError("MG81_ORIGINAL_REGISTERED_FAMILY_DRIFT: " + family)
    return gym

def public(raw):
    if type(raw) is not dict or set(raw) != {"image","direction","mission"}:
        raise RuntimeError("MG81_PRIVILEGED_OR_INVALID_OBSERVATION")
    image = raw["image"]
    if type(image).__module__ == "numpy" and type(image).__name__ == "ndarray":
        image = image.tolist()
    direction = raw["direction"]
    # Original Farama's scalar numpy.int64 is public, but the frozen R10 API
    # deliberately requires a canonical JSON-native Python int.
    if type(direction).__module__.startswith("numpy") and hasattr(direction,"item"):
        direction = direction.item()
    if type(direction) is not int:
        raise RuntimeError("MG81_NONCANONICAL_PUBLIC_DIRECTION")
    frame = {"image":image, "direction":direction,
             "mission":raw["mission"]}
    original_public(frame)
    return frame

def learner(role):
    return SelectedProgressCells() if role == ROLES[0] else SelectedChangeCells()

def restored(role, raw):
    cls = SelectedProgressCells if role == ROLES[0] else SelectedChangeCells
    obj = cls.restore(raw)
    if obj.checkpoint() != raw:
        raise RuntimeError("MG81_COLD_CHECKPOINT_CONTENT_NOT_IDENTICAL")
    return obj

def episode(gym, family, entry, seed, model, role, phase):
    env = gym.make(family)
    try:
        if gym.spec(family).entry_point != entry or env.action_space.n != 7:
            raise RuntimeError("MG81_SOURCE_ACTION_FAMILY_CHANGED")
        start = time.perf_counter()
        obs, _ = env.reset(seed=seed)
        first = public(obs)
        adapter = OriginalMissionAdapter()
        adapter.reset_public(first)
        model.start_session(adapter, "mg81-"+phase+"-"+role+"-"+str(seed), live=False)
        positive = False
        overrides = 0
        before_success_overrides = 0
        positive_events = 0
        selected = []
        total_reward = 0.0
        ended, truncated = False, False
        for index in range(1, CAP + 1):
            before = public(obs)
            if before["mission"] != first["mission"]:
                raise RuntimeError("MG81_MISSION_CHANGED_MID_EPISODE")
            choice = model.choose(before)
            if type(choice) is not dict or type(choice.get("action")) is not int:
                raise RuntimeError("MG81_NOT_OWN_NATIVE_ACTION")
            action = choice["action"]
            if action not in range(7) or choice.get("external_fallback") is not False:
                raise RuntimeError("MG81_NATIVE_ORIGINAL_ACTION_INVALID")
            override = choice.get("status") == "MG43_CONTEXT_REWARD_PROGRESS_OVERRIDE"
            if override and role != ROLES[0]:
                raise RuntimeError("MG81_CONTROL_REWARD_OVERRIDE")
            if override:
                overrides += 1
                if not positive:
                    before_success_overrides += 1
            submitted = adapter.submit(action)
            if submitted != action:
                raise RuntimeError("MG81_ACTION_REMAP")
            nxt, reward, ended, truncated, _ = env.step(action)
            if type(ended) is not bool or type(truncated) is not bool:
                raise RuntimeError("MG81_NON_ORIGINAL_TERMINAL")
            next_public = public(nxt)
            if type(reward) not in (int,float) or not math.isfinite(float(reward)):
                raise RuntimeError("MG81_NONFINITE_SOURCE_REWARD")
            adapter.complete(next_public,float(reward),ended,truncated)
            model.learn_selected(adapter,before,next_public)
            row = adapter.ledger[-1]
            if (row["action"] != action or row["before_sha"] != digest(before) or
                row["after_sha"] != digest(next_public) or row["index"] != index):
                raise RuntimeError("MG81_SELECTED_ORIGINAL_LEDGER_DRIFT")
            total_reward += float(reward)
            if reward > 0 and ended:
                positive = True
                positive_events += 1
            selected.append({"action":action,"before_sha":row["before_sha"],
                             "after_sha":row["after_sha"],"reward":float(reward),
                             "terminal":bool(ended or truncated),
                             "override":bool(override)})
            obs = nxt
            if ended or truncated:
                break
        if not selected or adapter.events != len(selected):
            raise RuntimeError("MG81_NO_ORIGINAL_SELECTED_ACTIONS")
        return {"family":family,"role":role,"phase":phase,"seed":seed,
                "mission":first["mission"],"start_public_sha256":digest(first),
                "original_selected_actions":len(selected),
                "positive_terminal_rewards":positive_events,
                "return":total_reward,"terminated":ended,"truncated":truncated,
                "changed_public_views":sum(x["before_sha"]!=x["after_sha"]
                                             for x in selected),
                "reward_guard_overrides":overrides,
                "pre_first_positive_overrides":before_success_overrides,
                "source_ledger_sha256":digest(selected),
                "elapsed_wall_seconds":round(time.perf_counter()-start,6),
                "source_ledger":selected}
    finally:
        env.close()

def verify_clean():
    if git("status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("MG81_SOURCE_CHECKOUT_DIRTY")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--phase",choices=("preflight","train","heldout"),required=True)
    p.add_argument("--source-root",type=Path)
    p.add_argument("--output-root",type=Path)
    a=p.parse_args()
    preflight()
    if a.phase=="preflight":
        verify_clean()
        return
    if not a.source_root or not a.output_root:
        raise RuntimeError("MG81_REQUIRED_SOURCE_AND_OUTPUT_ROOT")
    gym=check_original(a.source_root)
    out=a.output_root.resolve()
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    for family,entry,seeds,heldout in FAMILIES:
        for role in ROLES:
            checkpoint=out/("checkpoint-"+family+"-"+role+".bin")
            model=learner(role) if a.phase=="train" else restored(role,checkpoint.read_bytes())
            # MG37 wraps the unchanged MG28 parent and deliberately does not
            # expose a separate top-level samples property.
            initial_samples=(model.parent.samples if role==ROLES[0]
                             else model.samples)
            if a.phase=="train":
                for seed in seeds:
                    results.append(episode(gym,family,entry,seed,model,role,"train"))
                wire=model.checkpoint()
                if restored(role,wire).checkpoint()!=wire:
                    raise RuntimeError("MG81_TRAIN_CHECKPOINT_INVALID")
                checkpoint.write_bytes(wire)
            else:
                results.append(episode(gym,family,entry,heldout,model,role,"heldout"))
            final_samples=(model.parent.samples if role==ROLES[0]
                           else model.samples)
            observed=sum(e["original_selected_actions"] for e in results
                         if e["family"]==family and e["role"]==role
                         and e["phase"]==a.phase)
            if final_samples!=initial_samples+observed:
                raise RuntimeError("MG81_ORIGINAL_SELECTED_SAMPLE_CONSERVATION")
    role_counts={role:sum(q["original_selected_actions"] for q in results
                          if q["role"]==role) for role in ROLES}
    if any(v<=0 for v in role_counts.values()):
        raise RuntimeError("MG81_MISSING_MATCHED_ORIGINAL_ROLE")
    if len(results)!=(12 if a.phase=="train" else 6):
        raise RuntimeError("MG81_MISSING_PREDECLARED_EPISODE")
    report={"schema":"yggdrasil.mg81.original-source-paired-dev.v1",
            "phase":a.phase,"upstream":UPSTREAM,"prereg":PREREG,
            "roles":list(ROLES),"family_count":3,
            "episodes":results,"source_step_counts":role_counts,
            "scientific_admission":"DEV_ONLY_NO_CAUSAL_OR_GENERALIZATION_CLAIM"}
    payload=canonical(report)
    target=out/(a.phase+".json")
    target.write_bytes(payload)
    print("MG81_ORIGINAL_FARAMA_"+a.phase.upper()+
          "_SOURCE_EVENTS_PASS " + hashlib.sha256(payload).hexdigest())
    verify_clean()

if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        print("MG81_FAIL_CLOSED: "+str(exc),file=sys.stderr)
        raise

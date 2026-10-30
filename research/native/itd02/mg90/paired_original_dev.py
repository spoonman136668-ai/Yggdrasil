#!/usr/bin/env python3
"""MG90 empirical public landmark relation graph vs frozen native controls and conventional calibration.

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
try:
    import resource
except ModuleNotFoundError:
    resource=None  # Windows source-only validation; original Farama runner is Linux.

from research.native.itd02.mg19.original_mission_cells import (
    OriginalMissionAdapter, original_public)
from research.native.itd02.mg28.selected_change_cells import SelectedChangeCells
from research.native.itd02.mg82.effect_cells import PublicEffectCells
from research.native.itd02.mg83.revisit_cells import RevisitGuard
from research.native.itd02.mg85.public_map_control import PublicMapControl
from research.native.itd02.mg86.public_map_repair import RepairedMapControl
from research.native.itd02.mg87.transition_cells import PublicTransitionCells
from research.native.itd02.mg88.alignment_cells import PublicAlignmentCells
from research.native.itd02.mg89.landmark_cells import LandmarkLinkCells
from research.native.itd02.mg90.relational_cells import RelationalFrontierCells
from research.native.itd02.r10.public_adapter import canonical, digest

UPSTREAM = "7f5853792ea7f04f75614661006d87fcf949f26d"
DOORKEY_BLOB = "df5b29ef063be34e6d83b8b478e092c6e3e01512"
PREREG = "fb64295433180dde1350ff4f2263b5b5f516b67d"
BASE_MG89 = "bc7549dba7d657c6bcb2bd5a4a507a76b3249ad4"
FAMILIES = (
    ("MiniGrid-KeyCorridorS3R2-v0", "minigrid.envs:KeyCorridorEnv",
     (2211101, 2211103), 2311107),
    ("MiniGrid-KeyCorridorS4R3-v0", "minigrid.envs:KeyCorridorEnv",
     (2211201, 2211203), 2311207),
    ("MiniGrid-ObstructedMaze-1Dl-v0", "minigrid.envs:ObstructedMaze_1Dlhb",
     (2211301, 2211303), 2311307),
)
BLOBS = {
    "research/native/itd02/mg90/relational_cells.py":
        "35051cdc198727ed1f56d025159c96f075768354",
    "research/native/itd02/mg89/landmark_cells.py":
        "ac505e4c2dfd41ce29189fbc202c42f188f0f39d",
    "research/native/itd02/mg88/alignment_cells.py":
        "b53963959606dd13db5a40d0f3f81abc35dc1a4f",
    "research/native/itd02/mg87/transition_cells.py":
        "958e30b8da6610d721ab57485f0271ac4caabd02",
    "research/native/itd02/mg86/public_map_repair.py":
        "3c4b3ce716d51b96415cb0bd5ceb56d6d7897bfb",
    "research/native/itd02/mg85/public_map_control.py":
        "cdb2a6bf4feca1093537bab2d9207ea9f5e24e07",
    "research/native/itd02/mg83/revisit_cells.py":
        "f45ff00875256502011c39e5a5b0ea40300286ab",
    "research/native/itd02/mg82/effect_cells.py":
        "7e45d03a83f6e17c36337acf7d2ec9d8e703a056",
    "research/native/itd02/mg37/progress_cells.py":
        "175c4a7e2ed83a37c2f103339aefc9a4e95eca86",
    "research/native/itd02/mg28/selected_change_cells.py":
        "2c30ca4da6f6603ecc5ec36b1f460a246b120d89",
}
ROLES = ("mg90_relational_frontier", "mg89_landmark_links", "mg87_count_only", "mg86_public_map_repaired")
CAP = 384

def git(*args, cwd=None):
    p = subprocess.run(("git", *args), cwd=cwd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError("MG90_GIT_SOURCE_IDENTITY_FAIL: " +
                           " ".join(args) + ": " + p.stderr[-150:])
    return p.stdout.strip()

def preflight():
    for pin in (PREREG, BASE_MG89):
        git("merge-base", "--is-ancestor", pin, "HEAD")
    for path, expected in BLOBS.items():
        if git("hash-object", path) != expected:
            raise RuntimeError("MG90_NATIVE_FROZEN_SOURCE_CHANGED: " + path)
    content = Path("research/native/itd02/mg90/PREREG.md").read_text("utf-8")
    if (UPSTREAM not in content or
        "2211101" not in content or "2311307" not in content or
        git("hash-object", "research/native/itd02/mg90/PREREG.md") !=
        git("rev-parse", PREREG + ":research/native/itd02/mg90/PREREG.md")):
        raise RuntimeError("MG90_PREREG_SOURCE_DRIFT")
    if len({s for _, _, pair, val in FAMILIES for s in (*pair,val)}) != 9:
        raise RuntimeError("MG90_SEED_COHORT_NOT_DISTINCT")
    print("MG90_PROSPECTIVE_PREREG_AND_NATIVE_SOURCE_FROZEN_PASS")

def check_original(source):
    import gymnasium as gym
    import minigrid
    root = Path(source).resolve()
    location = Path(minigrid.__file__).resolve()
    if not location.is_relative_to(root):
        raise RuntimeError("MG90_NOT_IMPORTED_PINNED_ORIGINAL_MINIGRID")
    if git("rev-parse", "HEAD", cwd=root) != UPSTREAM:
        raise RuntimeError("MG90_ORIGINAL_FARAMA_REVISION_DRIFT")
    if git("hash-object", "minigrid/envs/doorkey.py", cwd=root) != DOORKEY_BLOB:
        raise RuntimeError("MG90_ORIGINAL_FARAMA_DOORKEY_BLOB_DRIFT")
    for family, entry, _, _ in FAMILIES:
        if gym.spec(family).entry_point != entry:
            raise RuntimeError("MG90_ORIGINAL_REGISTERED_FAMILY_DRIFT: " + family)
    return gym

def public(raw):
    if type(raw) is not dict or set(raw) != {"image","direction","mission"}:
        raise RuntimeError("MG90_PRIVILEGED_OR_INVALID_OBSERVATION")
    image = raw["image"]
    if type(image).__module__ == "numpy" and type(image).__name__ == "ndarray":
        image = image.tolist()
    direction = raw["direction"]
    # Original Farama's scalar numpy.int64 is public, but the frozen R10 API
    # deliberately requires a canonical JSON-native Python int.
    if type(direction).__module__.startswith("numpy") and hasattr(direction,"item"):
        direction = direction.item()
    if type(direction) is not int:
        raise RuntimeError("MG87_NONCANONICAL_PUBLIC_DIRECTION")
    frame = {"image":image, "direction":direction,
             "mission":raw["mission"]}
    original_public(frame)
    return frame

def learner(role):
    if role==ROLES[0]: return RelationalFrontierCells()
    if role==ROLES[1]: return LandmarkLinkCells()
    if role==ROLES[2]: return PublicTransitionCells(mode="count")
    if role==ROLES[3]: return RepairedMapControl()
    raise ValueError("MG87_INVALID_ROLE")

def restored(role, raw):
    if role not in ROLES: raise ValueError("MG87_INVALID_ROLE")
    cls = (RelationalFrontierCells if role==ROLES[0] else
           LandmarkLinkCells if role==ROLES[1] else
           PublicTransitionCells if role==ROLES[2] else RepairedMapControl)
    obj = cls.restore(raw)
    if role==ROLES[2] and obj.mode!="count":
        raise ValueError("MG90_COLD_MODE_DRIFT")
    if obj.checkpoint() != raw:
        raise RuntimeError("MG90_COLD_CHECKPOINT_CONTENT_NOT_IDENTICAL")
    return obj

def public_object_hits(frame):
    image=frame["image"]  # Exact original public source only.
    return {"visible_key":any(px[0]==5 for row in image for px in row),
            "visible_door":any(px[0]==4 for row in image for px in row),
            "visible_goal":any(px[0]==8 for row in image for px in row)}

def public_selected_effect(before,action,after):
    a=before["image"][3][5]
    b=after["image"][3][5]
    heading_unchanged=before["direction"]==after["direction"]
    return {"possible_public_key_pickup":bool(action==3 and heading_unchanged
            and a[0]==5 and b!=a),
            "public_door_open":bool(action==5 and heading_unchanged
            and a[0]==4 and b[0]==4 and a[1]==b[1]
            and a[2] in (1,2) and b[2]==0)}

def episode(gym, family, entry, seed, model, role, phase):
    env = gym.make(family)
    try:
        if gym.spec(family).entry_point != entry or env.action_space.n != 7:
            raise RuntimeError("MG90_SOURCE_ACTION_FAMILY_CHANGED")
        start = time.perf_counter()
        obs, _ = env.reset(seed=seed)
        first = public(obs)
        adapter = OriginalMissionAdapter()
        adapter.reset_public(first)
        model.start_session(adapter, "mg90-"+phase+"-"+role+"-"+str(seed), live=False)
        positive = False
        overrides = 0
        before_success_overrides = 0
        positive_events = 0
        events_seen={"visible_key":0,"visible_door":0,"visible_goal":0,
                     "possible_public_key_pickup":0,"public_door_open":0}
        first_visible={"visible_key":None,"visible_door":None,"visible_goal":None}
        selected = []
        total_reward = 0.0
        ended, truncated = False, False
        for index in range(1, CAP + 1):
            before = public(obs)
            if before["mission"] != first["mission"]:
                raise RuntimeError("MG90_MISSION_CHANGED_MID_EPISODE")
            choice = model.choose(before)
            if type(choice) is not dict or type(choice.get("action")) is not int:
                raise RuntimeError("MG90_NOT_OWN_NATIVE_ACTION")
            action = choice["action"]
            if action not in range(7) or choice.get("external_fallback") is not False:
                raise RuntimeError("MG90_NATIVE_ORIGINAL_ACTION_INVALID")
            status=choice.get("status")
            required={
                ROLES[1]:"MG90_SELECTED_PUBLIC_LANDMARK_LINKS",
                ROLES[2]:"MG87_PUBLIC_COUNT_ABLATION",
            }
            if role==ROLES[0]:
                if status not in ("MG90_RELATIONAL_SOURCE_FRONTIER_PROBE",
                                  "MG90_SOURCE_OBSERVED_SHORTEST_FRONTIER_PATH",
                                  "MG90_SOURCE_GRAPH_LOCAL_ESCAPE"):
                    raise RuntimeError("MG90_NATIVE_POLICY_STATUS_DRIFT")
            elif role==ROLES[3]:
                if not (type(status) is str and status.startswith("MG86_CONVENTIONAL_")):
                    raise RuntimeError("MG90_CONVENTIONAL_SOURCE_DRIFT")
            elif status!=required[role]:
                raise RuntimeError("MG90_NATIVE_SOURCE_DRIFT")
            override=False
            if override:
                overrides += 1
                if not positive:
                    before_success_overrides += 1
            submitted = adapter.submit(action)
            if submitted != action:
                raise RuntimeError("MG90_ACTION_REMAP")
            nxt, reward, ended, truncated, _ = env.step(action)
            if type(ended) is not bool or type(truncated) is not bool:
                raise RuntimeError("MG90_NON_ORIGINAL_TERMINAL")
            next_public = public(nxt)
            visible=public_object_hits(next_public)
            for label,seen in visible.items():
                if seen:
                    events_seen[label]+=1
                    if first_visible[label] is None:
                        first_visible[label]=index
            effect=public_selected_effect(before,action,next_public)
            for label,seen in effect.items():
                if seen:
                    events_seen[label]+=1
            if type(reward) not in (int,float) or not math.isfinite(float(reward)):
                raise RuntimeError("MG87_NONFINITE_SOURCE_REWARD")
            adapter.complete(next_public,float(reward),ended,truncated)
            model.learn_selected(adapter,before,next_public)
            row = adapter.ledger[-1]
            if (row["action"] != action or row["before_sha"] != digest(before) or
                row["after_sha"] != digest(next_public) or row["index"] != index):
                raise RuntimeError("MG90_SELECTED_ORIGINAL_LEDGER_DRIFT")
            total_reward += float(reward)
            if reward > 0 and ended:
                positive = True
                positive_events += 1
            selected.append({"action":action,"before_sha":row["before_sha"],
                             "after_sha":row["after_sha"],"reward":float(reward),
                             "terminal":bool(ended or truncated),
                             "visible":visible,"selected_public_effect":effect,
                             "override":bool(override)})
            obs = nxt
            if ended or truncated:
                break
        if not selected or adapter.events != len(selected):
            raise RuntimeError("MG87_NO_ORIGINAL_SELECTED_ACTIONS")
        return {"family":family,"role":role,"phase":phase,"seed":seed,
                "mission":first["mission"],"start_public_sha256":digest(first),
                "original_selected_actions":len(selected),
                "positive_terminal_rewards":positive_events,
                "return":total_reward,"terminated":ended,"truncated":truncated,
                "changed_public_views":sum(x["before_sha"]!=x["after_sha"]
                                             for x in selected),
                "distinct_public_successors":len({x["after_sha"] for x in selected}),
                "repeated_exact_selected_consequence":len(selected)-len({
                    (x["before_sha"],x["action"],x["after_sha"]) for x in selected}),
                "public_goal_events":events_seen,
                "first_public_visibility_index":first_visible,
                "public_action_counts":{str(a):sum(e["action"]==a for e in selected)
                                        for a in range(7)},
                "reward_guard_overrides":overrides,
                "pre_first_positive_overrides":before_success_overrides,
                "source_ledger_sha256":digest(selected),
                "elapsed_wall_seconds":round(time.perf_counter()-start,6),
                "source_ledger":selected}
    finally:
        env.close()

def verify_clean():
    if git("status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("MG90_SOURCE_CHECKOUT_DIRTY")

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
        raise RuntimeError("MG90_REQUIRED_SOURCE_AND_OUTPUT_ROOT")
    gym=check_original(a.source_root)
    out=a.output_root.resolve()
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    for family,entry,seeds,heldout in FAMILIES:
        for role in ROLES:
            checkpoint=out/("checkpoint-"+family+"-"+role+".bin")
            model=learner(role) if a.phase=="train" else restored(role,checkpoint.read_bytes())
            # All three source-owned policies expose original selected samples.
            initial_samples=model.samples
            if a.phase=="train":
                for seed in seeds:
                    results.append(episode(gym,family,entry,seed,model,role,"train"))
                wire=model.checkpoint()
                if restored(role,wire).checkpoint()!=wire:
                    raise RuntimeError("MG90_TRAIN_CHECKPOINT_INVALID")
                checkpoint.write_bytes(wire)
            else:
                results.append(episode(gym,family,entry,heldout,model,role,"heldout"))
            final_samples=model.samples
            observed=sum(e["original_selected_actions"] for e in results
                         if e["family"]==family and e["role"]==role
                         and e["phase"]==a.phase)
            if final_samples!=initial_samples+observed:
                raise RuntimeError("MG90_ORIGINAL_SELECTED_SAMPLE_CONSERVATION")
    role_counts={role:sum(q["original_selected_actions"] for q in results
                          if q["role"]==role) for role in ROLES}
    if any(v<=0 for v in role_counts.values()):
        raise RuntimeError("MG90_MISSING_MATCHED_ORIGINAL_ROLE")
    if len(results)!=(24 if a.phase=="train" else 12):
        raise RuntimeError("MG90_MISSING_PREDECLARED_EPISODE")
    report={"schema":"yggdrasil.mg90.empirical-relational-frontier-dev.v1",
            "phase":a.phase,"upstream":UPSTREAM,"prereg":PREREG,
            "roles":list(ROLES),"family_count":3,
            "episodes":results,"source_step_counts":role_counts,
            "scientific_admission":"DEV_ONLY_NO_CAUSAL_OR_GENERALIZATION_CLAIM",
            "process_max_rss_kib":(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                                   if resource is not None else None)}
    payload=canonical(report)
    target=out/(a.phase+".json")
    target.write_bytes(payload)
    print("MG90_ORIGINAL_FARAMA_"+a.phase.upper()+
          "_SOURCE_EVENTS_PASS " + hashlib.sha256(payload).hexdigest())
    verify_clean()

if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        print("MG90_FAIL_CLOSED: "+str(exc),file=sys.stderr)
        raise

#!/usr/bin/env python3
"""MG93 frozen MG92 exact-source replication and DoorKey zero-shot transfer.

No new learner/weights/teacher policy. Re-create identical 9 original MG92
training checkpoints and compare SHA256 byte-for-byte to published MG92
original-source artifact; only then evaluate entirely new original seeds.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
try:
    import resource
except ModuleNotFoundError:
    resource=None
from research.native.itd02.mg92 import paired_original_dev as frozen
from research.native.itd02.mg92.feedback_cells import PublicFeedbackGate
from research.native.itd02.mg91.native_prototypes import PublicRewardPrototypes
from research.native.itd02.mg91.independent_linear import IndependentLinearControl
from research.native.itd02.r10.public_adapter import canonical,digest

SCHEMA="yggdrasil.itd02.mg93.immutable-original-feedback-replication.v1"
PREREG="449701262c72c91b884ccb1b78eeabb6a6da94c3"
BASE="c7db7b4a6da5233029e22163b2a4d01fdd71879b"
UPSTREAM="7f5853792ea7f04f75614661006d87fcf949f26d"
SOURCE={
 "research/native/itd02/mg92/paired_original_dev.py":"6c3809d831ba0fd28b3ee8f7287803560286ab8f",
 "research/native/itd02/mg92/feedback_cells.py":"e4be6548bf04e83e1ec2464657679c1633f83784",
 "research/native/itd02/mg91/native_prototypes.py":"8176b310b572427e68b24d13f284ae597c05c17b",
 "research/native/itd02/mg91/independent_linear.py":"17a2f652d5f05f2a45bb85159341f9daa5d9266e",
 "research/native/itd02/mg86/public_map_repair.py":"3c4b3ce716d51b96415cb0bd5ceb56d6d7897bfb"}
# Frozen MG92 artifact 12972751160 sha256, original positive teacher
# source-selected examples, no retraining on novel or DoorKey observations.
CHECKPOINT_SHA={
 ("MiniGrid-KeyCorridorS3R2-v0","mg92_native_feedback"):"a9b2e90077a38023afbf9e4098e91add57397c84074af4b3a855753ed23b0fdb",
 ("MiniGrid-KeyCorridorS3R2-v0","mg91_frozen_native_prototypes"):"d3c50822649130b64327fde351011e7d41c7131c25302378ee199cab2b05d2c8",
 ("MiniGrid-KeyCorridorS3R2-v0","mg91_independent_linear_control"):"dd637c69a6a44fd20a41be0c9c4172b48c68839b0afbc8ffd5691ae5ef3f526e",
 ("MiniGrid-KeyCorridorS4R3-v0","mg92_native_feedback"):"edf7d8e091a3d2d3274bdffc04791fc85918d7b385a3017e18717e478d18dfd8",
 ("MiniGrid-KeyCorridorS4R3-v0","mg91_frozen_native_prototypes"):"215edb1dfcf5dd4976d1cd2f508457f4957307b0d9a1dd79f197872c93776954",
 ("MiniGrid-KeyCorridorS4R3-v0","mg91_independent_linear_control"):"88a037678edfccec9db7af2bf54ee6d85ca2f686ec15c14fb863df032f1c439a",
 ("MiniGrid-ObstructedMaze-1Dl-v0","mg92_native_feedback"):"cf1fb86a436352837a2ce0870a22fe14e2fd748a9c6eb6d7d06da00bd69230df",
 ("MiniGrid-ObstructedMaze-1Dl-v0","mg91_frozen_native_prototypes"):"844da43f828c9a27eb170760fb9135a5bd11c84ebe6fa9e296c09122a4edcbb8",
 ("MiniGrid-ObstructedMaze-1Dl-v0","mg91_independent_linear_control"):"8cf20c8e0b3cbed62c515fdc165b692c2eb998fbcbd2d2f42572e892f0ac8eab"}
NATIVE=(
 (frozen.ROLES[0],PublicFeedbackGate),
 (frozen.ROLES[1],PublicRewardPrototypes),
 (frozen.ROLES[2],IndependentLinearControl)
)
# Exactly nine previously sealed NEW familiar seeds + three source-distinct
# family seeds. Never substitute outcomes or use test seeds for fitting.
FAMILIAR={
 "MiniGrid-KeyCorridorS3R2-v0":(2811107,2811111,2811113),
 "MiniGrid-KeyCorridorS4R3-v0":(2811207,2811211,2811213),
 "MiniGrid-ObstructedMaze-1Dl-v0":(2811307,2811311,2811313)}
TRANSFER_FAMILY="MiniGrid-DoorKey-6x6-v0"
TRANSFER_ENTRY="minigrid.envs:DoorKeyEnv"
TRANSFER_SOURCE="MiniGrid-KeyCorridorS3R2-v0"
TRANSFER_SEEDS=(2911407,2911411,2911413)

def preflight():
    for commit in (PREREG,BASE):
        frozen.git("merge-base","--is-ancestor",commit,"HEAD")
    if (frozen.git("hash-object","research/native/itd02/mg93/PREREG.md")
        !=frozen.git("rev-parse",PREREG+":research/native/itd02/mg93/PREREG.md")):
        raise RuntimeError("MG93_FROZEN_PROSPECTIVE_PREREG_CHANGED")
    for path,pin in SOURCE.items():
        if frozen.git("hash-object",path)!=pin:
            raise RuntimeError("MG93_FROZEN_ACTOR_DRIFT "+path)
    frozen.preflight()
    assert frozen.UPSTREAM==UPSTREAM
    assert len(CHECKPOINT_SHA)==9
    assert len({s for seeds in FAMILIAR.values() for s in seeds}|set(TRANSFER_SEEDS))==12
    assert all(x not in [2711107,2711207,2711307] for seeds in FAMILIAR.values() for x in seeds)
    frozen.verify_clean()
    print("MG93_PINNED_ORIGINAL_SOURCE_AND_MG92_MODELS_PASS")

def check_checkpoint(folder,family,role):
    path=frozen.checkpoint_path(folder,family,role)
    raw=path.read_bytes()
    want=CHECKPOINT_SHA[(family,role)]
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=want:
        raise RuntimeError("MG93_FROZEN_MODEL_SHA256_MISMATCH "+family+" "+role+" "+actual)
    return raw

def run_reproduction(gym,out):
    actual=[]
    cohorts=[]
    for family,entry,seeds,_ in frozen.FAMILIES:
        source=[frozen.run_teacher(gym,family,entry,seed) for seed in seeds]
        actual.extend(source)
        winning=[{"seed":r["seed"],"success":True,"steps":r["source_ledger"]}
                 for r in source if r["success"]]
        if not winning:
            raise RuntimeError("MG93_FROZEN_POSITIVE_TEACHER_DATA_ABSENT "+family)
        actors=[(role,cls()) for role,cls in NATIVE]
        for role,actor in actors:
            actor.fit(winning)
        if len({m.data_sha for _,m in actors})!=1:
            raise RuntimeError("MG93_EXACT_IDENTICAL_SUCCESSFUL_TEACHER_DATA_FAILED")
        for role,actor in actors:
            raw=actor.checkpoint()
            if hashlib.sha256(raw).hexdigest()!=CHECKPOINT_SHA[(family,role)]:
                raise RuntimeError("MG93_RECREATED_ORIGINAL_MG92_CHECKPOINT_NOT_IDENTICAL "+family+" "+role)
            if type(actor).restore(raw).checkpoint()!=raw:
                raise RuntimeError("MG93_COLD_CHECKPOINT_CANONICAL_FAIL")
            frozen.checkpoint_path(out,family,role).write_bytes(raw)
        cohorts.append({"family":family,"real_original_teacher_wins":len(winning),
                        "original_successful_teacher_selected_actions":actors[0][1].training_count,
                        "frozen_original_MG92_training_sha256":actors[0][1].data_sha})
    if len(actual)!=12:
        raise RuntimeError("MG93_FROZEN_ORIGINAL_TEACHER_DEV_COHORT_INCOMPLETE")
    return actual,cohorts

def execute_heldout(gym,out):
    results=[]
    registry={family:entry for family,entry,_,_ in frozen.FAMILIES}
    testcases=[(family,seed,"new_same_family",family)
               for family,seeds in FAMILIAR.items() for seed in seeds]
    testcases.extend((TRANSFER_FAMILY,seed,"zero_shot_unfamiliar_family",TRANSFER_SOURCE)
                     for seed in TRANSFER_SEEDS)
    if len(testcases)!=12:
        raise RuntimeError("MG93_PREDECLARED_SOURCE_COHORT_INCOMPLETE")
    for family,seed,scope,training_family in testcases:
        entry=registry.get(family,TRANSFER_ENTRY)
        if gym.spec(family).entry_point!=entry:
            raise RuntimeError("MG93_ORIGINAL_FARAMA_REGISTRATION_OR_FAMILY_CHANGED")
        fitted=[]
        for role,cls in NATIVE:
            raw=check_checkpoint(out,training_family,role)
            actor=cls.restore(raw)  # separate fresh model for EVERY episode
            if actor.checkpoint()!=raw:
                raise RuntimeError("MG93_FROZEN_RESTORED_MODEL_NOT_IDENTICAL")
            fitted.append((role,actor))
        if len({m.data_sha for _,m in fitted})!=1:
            raise RuntimeError("MG93_LEARNING_DATA_MISMATCH")
        for role,actor in fitted:
            r=frozen.run_frozen(gym,family,entry,seed,actor,role)
            r["evaluation_scope"]=scope
            r["trained_original_family"]=training_family
            r["original_training_checkpoint_sha256"]=CHECKPOINT_SHA[(training_family,role)]
            r["source_real_task_success"]=r["success"]
            results.append(r)
        diagnostic=frozen.run_teacher(gym,family,entry,seed)
        diagnostic["source_ledger"]=[{k:v for k,v in step.items() if k!="before"}
                                     for step in diagnostic["source_ledger"]]
        diagnostic["evaluation_scope"]=scope
        diagnostic["trained_original_family"]=None
        diagnostic["source_real_task_success"]=diagnostic["success"]
        results.append(diagnostic)
    if len(results)!=48:
        raise RuntimeError("MG93_EXACT_ORIGINAL_TEST_COHORT_NOT_COMPLETE")
    return results

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--phase",choices=("preflight","train","heldout"),required=True)
    parser.add_argument("--source-root",type=Path)
    parser.add_argument("--output-root",type=Path)
    a=parser.parse_args()
    preflight()
    if a.phase=="preflight":
        return
    if not a.source_root or not a.output_root:
        raise RuntimeError("MG93_SOURCE_AND_OUTPUT_REQUIRED")
    gym=frozen.check_original(a.source_root)
    if gym.spec(TRANSFER_FAMILY).entry_point!=TRANSFER_ENTRY:
        raise RuntimeError("MG93_UNFAMILIAR_FAMILY_NOT_ORIGINAL_FARAMA_REGISTRY")
    out=a.output_root.resolve()
    out.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter()
    if a.phase=="train":
        episodes,cohorts=run_reproduction(gym,out)
    else:
        # The separate Python invocation is the independent cold process.
        # Source-training checkpoints are read-only, restored anew for every
        # original test episode, and never fitted after test has started.
        for family,_,_,_ in frozen.FAMILIES:
            for role,_ in NATIVE:
                check_checkpoint(out,family,role)
        episodes=execute_heldout(gym,out)
        cohorts=[]
    data={"schema":SCHEMA,"phase":a.phase,"upstream":UPSTREAM,
          "prereg":PREREG,"exact_parent":BASE,
          "frozen_training_artifact_id":12972751160,
          "roles":list(frozen.ROLES),"episodes":episodes,
          "same_original_training_reproduction":cohorts,
          "source_step_counts":{role:sum(x["original_selected_actions"]
                             for x in episodes if x["role"]==role)
                             for role in frozen.ROLES},
          "run_elapsed_wall_seconds":round(time.perf_counter()-started,6),
          "max_process_rss_kib":(
              resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
              if resource is not None else None)}
    (out/(a.phase+".json")).write_bytes(canonical(data))
    frozen.verify_clean()
    print("MG93_"+a.phase.upper()+"_ORIGINAL_FARAMA_SOURCE_REPLICATION_PASS "+
          hashlib.sha256(canonical(data)).hexdigest())

if __name__=="__main__":
    try:
        main()
    except Exception as error:
        print("MG93_FAIL_CLOSED: "+str(error),file=sys.stderr)
        raise

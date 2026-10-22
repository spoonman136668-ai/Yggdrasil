"""MR34E: preregistered DEV-only history-identifiability prerequisite.

Both engines are independently authored and invoked unchanged. This
retrospective source-public diagnostic asks whether complete CURRENT public
frames and the exact same action sometimes produce different original NEXT
public frames across distinct reset seeds, and whether public 2-step history
separates any of these pairs. It does NOT show trainability, independent
scientific transfer, causal interventions, or superior learned cognition.
"""
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess
import sys
import time

import numpy as np
import psutil

FROZEN=Path(__file__).with_name("frozen_protocol.json")
ENGINES={
  "FaramaMiniGridDoorKey8":{
    "sha":"7f5853792ea7f04f75614661006d87fcf949f26d",
    "shape":(7,7,3),"actions":7,
  },
  "DeepMindPycolabApprehend":{
    "sha":"6504c8065dd5322438f23a2a9026649904f3322a",
    "shape":(10,7),"actions":2,
  },
}
SEEDS=(1201,1213,1217,1223,1229,1231,1237,1249,
       1259,1277,1279,1283,1289,1291,1297,1301)

def sha(blob):
    return sha256(blob).hexdigest()

def canon(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"))

def source(root, name):
    root=Path(root).resolve()
    if not root.is_dir():
        raise ValueError("MR34E_ORIGINAL_PUBLIC_SOURCE_NOT_PRESENT_"+name)
    head=subprocess.check_output(
        ["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    if head != ENGINES[name]["sha"]:
        raise ValueError("MR34E_ORIGINAL_AUTHOR_SOURCE_SHA_DRIFT_"+name)
    dirty=subprocess.check_output(
        ["git","-C",str(root),"status","--porcelain"],text=True)
    if dirty.strip():
        raise ValueError("MR34E_ORIGINAL_SOURCE_WORKTREE_MUTATED_"+name)
    return root

def contract():
    cfg=json.loads(FROZEN.read_text(encoding="utf-8"))
    original=cfg["public_source_engines"]
    if (cfg["schema"]!=
            "yggdrasil.mr34e.two-independently-authored-original-public-history-alias.dev.v1"
        or cfg["parent_exact_git_sha"]!=
            "a2464da8d3a8a9bb28dcd3a37638c5309dc63247"
        or cfg["new_development_only_independent_native_reset_seeds"]!=list(SEEDS)
        or cfg["max_original_native_actions_per_seed"]!=96
        or len(original)!=2 or
        any(q["id"] not in ENGINES or
            q["source_sha"]!=ENGINES[q["id"]]["sha"] or
            q["public_shape"]!=list(ENGINES[q["id"]]["shape"]) or
            q["native_actions"]!=ENGINES[q["id"]]["actions"]
            for q in original) or
        cfg["no_candidate_model_training"] is not True or
        cfg["independent_first_use_scientific_samples_consumed"] is not False
        or cfg["no_source_tuning_or_seed_search_after_results"] is not True):
        raise ValueError("MR34E_FROZEN_ORIGINAL_SCIENTIFIC_CONTRACT_DRIFT")
    return cfg

def public(raw, shape):
    if (not isinstance(raw,np.ndarray)
        or raw.shape!=shape or raw.dtype!=np.uint8):
        raise ValueError("MR34E_PUBLIC_ORIGINAL_FRAME_SHAPE_OR_DTYPE_DRIFT")
    return raw.tobytes()

def raw_episode(engine, original_source, seed, limit):
    mode=ENGINES[engine]
    policy=random.Random(1000003*seed+337)
    if engine=="FaramaMiniGridDoorKey8":
        from minigrid.envs.doorkey import DoorKeyEnv
        env=DoorKeyEnv(size=8,render_mode=None)
        first,_=env.reset(seed=seed)
        start=public(first["image"],mode["shape"])
    else:
        from pycolab.examples import apprehend
        from pycolab import rendering
        random.seed(seed)
        env=apprehend.make_game()
        painter=rendering.ObservationCharacterRepainter(
            apprehend.REPAINT_MAPPING)
        first,_,_=env.its_showtime()
        start=public(painter(first).board,mode["shape"])
        if set(start)-{ord(" "),ord("X")}:
            raise ValueError("MR34E_UNMASKED_ORIGINAL_SOURCE_IDENTITY")
    initial=start
    evidence=sha256()
    zero=b"\x00"*len(initial)
    history=[(zero,255),(zero,255)]
    event_rows=[]
    try:
        for t in range(limit):
            action=policy.randrange(mode["actions"])
            if engine=="FaramaMiniGridDoorKey8":
                nxt,_,done,trunc,_=env.step(action)
                after=public(nxt["image"],mode["shape"])
                terminated=bool(done or trunc)
            else:
                nxt,_,discount=env.play(action)
                after=public(painter(nxt).board,mode["shape"])
                if set(after)-{ord(" "),ord("X")}:
                    raise ValueError("MR34E_UNMASKED_ORIGINAL_NEXT_SOURCE")
                terminated=float(discount)==0.
            evidence.update(start)
            evidence.update(bytes([action]))
            evidence.update(after)
            current=sha256(start).digest()+bytes([action])
            past=(
                sha256(history[0][0]).digest()+bytes([history[0][1]])+
                sha256(history[1][0]).digest()+bytes([history[1][1]])
            )
            event_rows.append({
                "seed":seed, "step":t, "current_key":current,
                "history_key":current+past,
                "next_key":sha256(after).digest(),
            })
            history=history[1:]+[(start,action)]
            start=after
            if terminated:
                break
    finally:
        if hasattr(env,"close"):
            env.close()
    if len(event_rows)==0:
        raise ValueError("MR34E_ORIGINAL_SOURCE_EXECUTED_ZERO_ACTIONS")
    return event_rows,{
        "original_native_reset_seed":seed,
        "native_original_source_steps":len(event_rows),
        "source_initial_full_public_sha256":sha(initial),
        "source_full_public_action_next_digest":evidence.hexdigest()
    }

def alias_report(rows):
    groups=defaultdict(list)
    for row in rows:
        groups[row["current_key"]].append(row)
    all_pairs=0
    conflicting=0
    different_hist=0
    same_hist=0
    source_pair_clusters=set()
    source_seeds=set()
    source_hist_clusters=set()
    per_seed_conflict=defaultdict(int)
    distinct_source_current_groups=0
    for group in groups.values():
        seeds={r["seed"] for r in group}
        if len(seeds)<2:
            continue
        distinct_source_current_groups+=1
        for i,one in enumerate(group):
            for other in group[i+1:]:
                if one["seed"]==other["seed"]:
                    continue
                all_pairs+=1
                if one["next_key"] == other["next_key"]:
                    continue
                conflicting+=1
                a,b=sorted((one["seed"],other["seed"]))
                source_pair_clusters.add((a,b))
                source_seeds.update((a,b))
                per_seed_conflict[a]+=1
                per_seed_conflict[b]+=1
                if one["history_key"]!=other["history_key"]:
                    different_hist+=1
                    source_hist_clusters.update((a,b))
                else:
                    same_hist+=1
    return {
        "independent_original_reset_seed_clusters":len(set(r["seed"] for r in rows)),
        "original_native_public_events":len(rows),
        "cross_seed_exact_current_action_alias_groups":distinct_source_current_groups,
        "cross_seed_exact_current_action_matched_event_pairs":all_pairs,
        "cross_seed_same_current_action_different_genuine_next_pairs":conflicting,
        "distinct_native_seed_pairs_with_next_public_conflict":len(source_pair_clusters),
        "independent_seed_clusters_with_natural_next_public_conflict":len(source_seeds),
        "conflicting_outcome_pairs_distinguished_by_prior_two_public_actions":different_hist,
        "conflicting_outcome_pairs_still_aliased_after_two_step_public_history":same_hist,
        "independent_seed_clusters_with_historical_distinction":len(source_hist_clusters),
        "per_original_reset_seed_conflict_pair_incidence":{
            str(k):v for k,v in sorted(per_seed_conflict.items())},
        "strict_source_public_alias_prerequisite_DEV_GO":
            len(source_seeds)>=2 and different_hist>0 and
            len(source_hist_clusters)>=2,
        "retrospective_context_distinction_is_not_prospective_prediction":True
    }

def peak_rss():
    if sys.platform=="win32":
        v=getattr(psutil.Process().memory_info(),"peak_wset",None)
        if not v:
            raise ValueError("MR34E_WINDOWS_PEAK_RSS_UNMEASURABLE")
        return int(v)
    if sys.platform.startswith("linux"):
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1024
    raise ValueError("MR34E_RESOURCE_OS_UNSUPPORTED")

def main(farama,pycolab):
    cfg=contract()
    roots={
        "FaramaMiniGridDoorKey8":source(farama,"FaramaMiniGridDoorKey8"),
        "DeepMindPycolabApprehend":source(pycolab,"DeepMindPycolabApprehend"),
    }
    importdir=sys.path
    # Import both independently authored original source engines unchanged.
    sys.path.insert(0,str(roots["FaramaMiniGridDoorKey8"]))
    sys.path.insert(0,str(roots["DeepMindPycolabApprehend"]))
    from research.mr27.natural_memory import source_guard
    source_guard(roots["FaramaMiniGridDoorKey8"])
    start=time.process_time_ns()
    output={}
    all_receipts=[]
    count=0
    for engine in ENGINES:
        rows=[]
        receipts=[]
        for seed in SEEDS:
            entry,receipt=raw_episode(
                engine,roots[engine],seed,
                cfg["max_original_native_actions_per_seed"])
            rows+=entry
            receipts.append(receipt)
        if len(receipts)!=16:
            raise ValueError("MR34E_INDEPENDENT_EPISODE_COHORT_DRIFT")
        audit=alias_report(rows)
        audit["native_original_source_episode_receipts"]=receipts
        audit["original_episode_receipt_digest"]=sha(canon(receipts).encode())
        output[engine]=audit
        all_receipts.append([engine,audit["original_episode_receipt_digest"]])
        count+=len(rows)
    for engine,root in roots.items():
        source(root,engine)
    go=all(o["strict_source_public_alias_prerequisite_DEV_GO"]
           for o in output.values())
    print("MR34E_INDEPENDENT_ORIGINAL_PUBLIC_CAUSAL_HISTORY_ALIAS="+canon({
        "original_author_exact_git_commits":{
            name:ENGINES[name]["sha"] for name in ENGINES},
        "frozen_protocol_sha256":sha(FROZEN.read_bytes()),
        "two_independently_authored_original_source_dev_audits":output,
        "original_source_episode_digest":sha(canon(all_receipts).encode()),
        "independent_source_families_admitted_native":2,
        "source_original_episodes":len(SEEDS)*len(ENGINES),
        "original_native_actions":count,
        "source_public_full_frame_hashes_only":True,
        "source_private_world_state_as_actor_or_history_feature":False,
        "no_conventional_predictor_or_yggdrasil_learner_trained":True,
        "retrospective_same_current_different_future_not_causal_identification":True,
        "both_independent_native_sources_meet_strict_alias_prerequisite_DEV_GO":go,
        "native_dual_source_process_cpu_ns":time.process_time_ns()-start,
        "whole_original_two_source_process_peak_rss_bytes":peak_rss(),
        "cross_source_compute_parity_not_established":True,
        "protected_scientific_first_use_consumed":False,
        "G29_atlas_and_final_regression":"BLOCKED",
        "scientific_admission":"NO_GO",
    }))

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: python -m research.mr34e.public_alias FARAMA PYCOLAB")
    main(sys.argv[1],sys.argv[2])

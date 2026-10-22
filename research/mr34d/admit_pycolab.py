"""MR34D source-bound development admission of original DeepMind Pycolab Apprehend.

This is SOURCE BIRTH only, not history information sufficiency or transferable
cognition. Original upstream Pycolab code is imported unchanged and called
through its native game.its_showtime()/game.play() interface. Only the
upstream public repainted board reaches the source-blind external actor.
"""
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
SOURCE_SHA="6504c8065dd5322438f23a2a9026649904f3322a"
PARENT_SHA="b01a487eb8ba4df9b3317438cb9c0324d50d48ad"
EXPECTED_SEEDS=(1013,1019,1021,1031)
STREAMS=(0,1)

def exact_source(path):
    root=Path(path).resolve()
    if not root.is_dir():
        raise ValueError("MR34D_ORIGINAL_PYCOLAB_SOURCE_ABSENT")
    actual=subprocess.check_output(
        ["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    if actual!=SOURCE_SHA:
        raise ValueError("MR34D_ORIGINAL_PYCOLAB_GIT_SHA_DRIFT")
    status=subprocess.check_output(
        ["git","-C",str(root),"status","--porcelain"],text=True)
    if status.strip():
        raise ValueError("MR34D_ORIGINAL_PYCOLAB_DIRTY")
    if not (root/"LICENSE").is_file():
        raise ValueError("MR34D_ORIGINAL_UPSTREAM_LICENSE_MISSING")
    return root

def freeze():
    cfg=json.loads(FROZEN.read_text(encoding="utf-8"))
    src=cfg["replacement_independent_source"]
    if (cfg["schema"]!=
            "yggdrasil.mr34d.original-independent-pycolab-source-admission.v1" or
        cfg["exact_predecessor_mr34c_sha"]!=PARENT_SHA or
        src["sha"]!=SOURCE_SHA or
        src["source_original_module"]!="pycolab.examples.apprehend" or
        src["source_original_game_factory"]!="make_game()" or
        cfg["newly_frozen_development_seed_clusters"]!=list(EXPECTED_SEEDS) or
        cfg["fixed_stream_ids"]!=list(STREAMS) or
        cfg["max_native_original_game_actions_per_episode"]!=16 or
        cfg["trained_cognitive_model"] is not False or
        cfg["protected_science_first_use_consumed"] is not False):
        raise ValueError("MR34D_PRECOMMITTED_ORIGINAL_SOURCE_PROTOCOL_DRIFT")
    return cfg

def OS_peak_resident():
    if sys.platform=="win32":
        value=getattr(psutil.Process().memory_info(),"peak_wset",None)
        if not value:
            raise ValueError("MR34D_WINDOWS_OS_PROCESS_PEAK_RSS_NOT_AVAILABLE")
        return int(value)
    if sys.platform.startswith("linux"):
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1024
    raise ValueError("MR34D_OS_RESOURCE_MEASUREMENT_UNSUPPORTED")

def public_bytes(obs,repainter):
    out=repainter(obs)
    board=out.board
    if not isinstance(board,np.ndarray) or board.dtype!=np.uint8 or board.shape!=(10,7):
        raise ValueError("MR34D_ORIGINAL_PUBLIC_REPAINT_FRAME_INVALID")
    # Ensure the original Apprehend game hides source character identities.
    used=set(np.unique(board).tolist())
    if not used.issubset({ord(" "),ord("X")}):
        raise ValueError("MR34D_ORIGINAL_REPAINT_LEAKED_CHARACTERS")
    return board.tobytes()

def main(upstream):
    cfg=freeze()
    root=exact_source(upstream)
    sys.path.insert(0,str(root))
    from pycolab.examples import apprehend
    from pycolab import rendering
    if apprehend.REPAINT_MAPPING!={"b":"X","P":"X"}:
        raise ValueError("MR34D_UPSTREAM_PUBLIC_REPAINT_IDENTITY_DRIFT")
    if len(apprehend.GAME_ART)!=10 or len(apprehend.GAME_ART[0])!=7:
        raise ValueError("MR34D_ORIGINAL_APPREHEND_GAME_BOARD_DRIFT")
    start=time.process_time_ns()
    original=[]
    count=0
    for seed in EXPECTED_SEEDS:
        for stream in STREAMS:
            # Original source calls Python random.uniform to initialise the
            # falling ball; set native RNG before unchanged native game creation.
            random.seed(seed)
            original_game=apprehend.make_game()
            observer=rendering.ObservationCharacterRepainter(
                apprehend.REPAINT_MAPPING)
            source_obs,_source_reward,_source_discount=original_game.its_showtime()
            before=public_bytes(source_obs,observer)
            initial=sha256(before).hexdigest()
            policy=random.Random(1000003*seed+337+10007*stream)
            event=sha256()
            steps=0
            step_digests=[]
            last_discount=None
            for step in range(cfg["max_native_original_game_actions_per_episode"]):
                # Actor policy uses ONLY its public action count (two original
                # move directions), not game sprite positions or native reward.
                action=policy.randrange(2)
                obs,reward,discount=original_game.play(action)
                after=public_bytes(obs,observer)
                event.update(before)
                event.update(bytes([action]))
                event.update(after)
                step_digests.append(sha256(
                    before+bytes([action])+after).hexdigest())
                before=after
                steps+=1
                last_discount=float(discount)
                if discount==0.0:
                    break
            if steps<=0:
                raise ValueError("MR34D_ORIGINAL_GAME_EMITTED_NO_NATIVE_STEPS")
            original.append({
                "development_reset_seed":seed,
                "source_blind_stream_id":stream,
                "native_original_pycolab_game_actions":steps,
                "public_initial_repainted_frame_sha256":initial,
                "original_public_action_consequence_sha256":event.hexdigest(),
                "source_action_public_frame_event_sha256":step_digests,
                "terminal_original_discount":last_discount
            })
            count+=steps
    if len(original)!=8:
        raise ValueError("MR34D_ORIGINAL_SOURCE_EPISODE_COUNT_DRIFT")
    canonical=json.dumps(original,sort_keys=True,separators=(",",":"))
    exact_source(root)
    print("MR34D_ORIGINAL_PYCOLAB_SOURCE_ADMISSION="+json.dumps({
        "original_upstream_owner":"google-deepmind",
        "original_source_git_sha":SOURCE_SHA,
        "exact_frozen_protocol_sha256":sha256(FROZEN.read_bytes()).hexdigest(),
        "source_original_apprehend_native_episodes":len(original),
        "source_original_game_native_actions":count,
        "original_repainted_public_board_shape":[10,7],
        "source_original_action_count":2,
        "native_episode_source_evidence":original,
        "source_native_reset_action_public_digest":sha256(canonical.encode()).hexdigest(),
        "source_original_clean_checkout":True,
        "original_engine_not_mutated":True,
        "only_public_repainted_observation_to_actor":True,
        "no_source_sprite_identifiers_or_private_velocity_to_policy":True,
        "original_source_worker_cpu_ns_including_obs_and_actor":time.process_time_ns()-start,
        "whole_original_source_worker_os_peak_rss_bytes":OS_peak_resident(),
        "serialized_original_source_evidence_bytes":len(canonical.encode()),
        "source_reused_scientific_first_use":False,
        "no_cognitive_model_trained":True,
        "dual_authored_source_admission_target":"REQUIRES_CROSS_OS_IDENTICAL_DIGEST",
        "historical_information_sufficiency_proven":False,
        "scientific_admission":"NO_GO",
        "G29_source_bound_atlas":"FAIL_CLOSED"
    },sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr34d.admit_pycolab PYCOLAB_ORIGINAL_SOURCE")
    main(sys.argv[1])

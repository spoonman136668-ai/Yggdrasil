#!/usr/bin/env python3
"""CS06 source-native, originally authored POBAX partial information admission.

This is original-source PUBLIC evaluator evidence ONLY, not model training.
No substituted environment or source-private information given to policies.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import inspect
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
import types

UPSTREAM="a5e1d62d14e4efe783885b9d4f19cffa2a568eec"
FIRST="0f420c7eaf520b2de6d5abe8ec2a250b3d3a8b80"
BLOBS={
    "pobax/envs/jax/rocksample.py":"5808900a96db02f843fe917275aed5176c3d967e",
    "pobax/envs/jax/battleship.py":"762119e6e9d9045def9e543dcafb12b1422de1fa",
    "pobax/envs/wrappers/gymnax.py":"fab29996319d455a42d7ce333dac81cc31a12ad0",
    "pobax/envs/configs/rocksample_5_5_config.json":"d1fabe03e59db376ce2858ff339770550953d85e",
    "pobax/definitions.py":"5e1a5902e0b2a244474b07df238eb343dd108de5",
    "setup.py":"cada33673514d490f8082de6c1587ecbf3e1ef33",
    "requirements.txt":"367106b77c2c5e21788e01b0924bcf5307e6cde3",
}
N=128
ROCK_SEEDS=tuple(range(1100000,1100128))

def fail_if(not_ok,why):
    if not_ok: raise RuntimeError(why)
def asjson(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def digest(x):
    return hashlib.sha256(asjson(x).encode()).hexdigest()
def source_identity(root):
    def cmd(args):
        p=subprocess.run(args,cwd=root,text=True,capture_output=True,timeout=30)
        return p.returncode,p.stdout.strip(),p.stderr[-1000:]
    rc,v,_=cmd(["git","rev-parse","HEAD"])
    fail_if(rc!=0 or v!=UPSTREAM,"UPSTREAM_GIT_COMMIT_MISMATCH")
    for path,want in BLOBS.items():
        rc,got,_=cmd(["git","hash-object","--",path])
        fail_if(rc!=0 or got!=want,"ORIGINAL_GIT_BLOB_MISMATCH:"+path)
    rc,_,_=cmd(["git","diff","--exit-code","--","pobax","setup.py","requirements.txt"])
    fail_if(rc!=0,"UPSTREAM_SOURCE_MODIFIED")
    return {"upstream_sha":UPSTREAM,"original_blobs":BLOBS}
def original_scoped_modules(root):
    """Load genuine upstream classes; avoid upstream eager optional navix imports.

    No fake GymnaxWrapper: its genuine upstream source is imported normally.
    """
    for name,path in (
        ("pobax.envs",root/"pobax"/"envs"),
        ("pobax.envs.jax",root/"pobax"/"envs"/"jax"),
        ("pobax.envs.wrappers",root/"pobax"/"envs"/"wrappers"),
    ):
        fail_if(name in sys.modules,"UPSTREAM_PACKAGE_ALREADY_IMPORTED")
        m=types.ModuleType(name)
        m.__path__=[str(path)]
        m.__package__=name
        sys.modules[name]=m
    wrappers=importlib.import_module("pobax.envs.wrappers.gymnax")
    rock=importlib.import_module("pobax.envs.jax.rocksample")
    ship=importlib.import_module("pobax.envs.jax.battleship")
    for module,path in ((wrappers,"pobax/envs/wrappers/gymnax.py"),
                        (rock,"pobax/envs/jax/rocksample.py"),
                        (ship,"pobax/envs/jax/battleship.py")):
        fail_if(Path(inspect.getfile(module)).resolve()!=root/path,
                "IMPORTED_MODULE_NOT_ORIGINAL:"+path)
    for cls,module in ((rock.RockSample,rock),(ship.Battleship,ship),
                       (wrappers.GymnaxWrapper,wrappers)):
        fail_if(Path(inspect.getfile(cls)).resolve()!=Path(module.__file__).resolve(),
                "NOT_GENUINE_ORIGINAL_CLASS")
    return rock.RockSample,ship.Battleship

def array(x):
    import numpy as np
    return np.asarray(x)
def steps_rock(RockSample,root):
    import jax
    import numpy as np
    conf=root/"pobax/envs/configs/rocksample_5_5_config.json"
    env=RockSample(key=jax.random.PRNGKey(7264),config_path=conf)
    fail_if(env.size!=5 or env.k!=5,"ROCKSAMPLE_UPSTREAM_CONFIG_DRIFT")
    map_actual=array(env.rock_positions)
    fail_if(map_actual.shape!=(5,2) or len({tuple(v) for v in map_actual.tolist()})!=5,
            "NOT_FIVE_ORIGINAL_ROCK_LOCATIONS")
    records=[]
    report={"constructor_private_rock_map_for_auditor_only":map_actual.tolist(),
            "private_map_passed_to_policy":False,"ordinary_public_rock_coordinates_present":False}
    for seed in ROCK_SEEDS:
        obs,state=env.reset_env(jax.random.PRNGKey(seed),env.default_params)
        reset=array(obs)
        hidden=array(state.rock_morality)
        fail_if(reset.shape!=(15,) or hidden.shape!=(5,),
                "ORIGINAL_ROCK_SHAPE_INVALID")
        fail_if(not np.isfinite(reset).all() or not np.all(reset[10:]==0),
                "ORIGINAL_RESET_PUBLIC_ROCK_REPORT_INVALID")
        fail_if(int(np.sum(reset[:5]))!=1 or int(np.sum(reset[5:10]))!=1,
                "ORIGINAL_PUBLIC_POSITION_ENCODING_INVALID")
        obs1,state1,reward1,done1,info1=env.step_env(
            jax.random.PRNGKey(seed+1000000),state,5,env.default_params)
        check=array(obs1)
        fail_if(check.shape!=(15,) or int(np.count_nonzero(check[10:]))!=1
                or abs(float(check[10]))!=1
                or int(np.count_nonzero(check[11:]))!=0,
                "ORIGINAL_CHECK_ACTION_DID_NOT_REPORT_ONLY_ROCK0")
        fail_if(bool(done1) or float(reward1)!=0 or len(info1)!=0,
                "CHECK_TERMINATED_OR_REWARDED")
        obs2,state2,reward2,done2,info2=env.step_env(
            jax.random.PRNGKey(seed+2000000),state1,1,env.default_params)
        after=array(obs2)
        fail_if(after.shape!=(15,) or not np.all(after[10:]==0),
                "ROCK_REPORT_DID_NOT_CLEAR_AFTER_LEGAL_MOVE")
        fail_if(int(np.sum(after[:5]))!=1 or int(np.sum(after[5:10]))!=1,
                "POST_MOVE_POSITION_ENCODING_INVALID")
        fail_if(float(reward2) not in (0.,float(env.exit_reward)) or len(info2)!=0,
                "ORIGINAL_MOVE_REWARD_OR_INFO_UNEXPECTED")
        records.append({
            "seed":seed,"public_reset":reset.tolist(),
            "public_after_check":check.tolist(),"public_after_move":after.tolist(),
            "public_check_rock0_sign":int(check[10]),
            "auditor_only_rock0_truth":int(hidden[0]),
            "auditor_only_rock_five_truths":hidden.astype(int).tolist(),
            "native_check_reward":float(reward1),
            "native_move_reward":float(reward2),
            "native_move_terminated":bool(done2)
        })
    unique_hidden={tuple(x["auditor_only_rock_five_truths"]) for x in records}
    unique_current={tuple(x["public_after_move"]) for x in records}
    signs={x["public_check_rock0_sign"] for x in records}
    truths={x["auditor_only_rock0_truth"] for x in records}
    witness=None
    groups={}
    for r in records:
        groups.setdefault(tuple(r["public_after_move"]),[]).append(r)
    for _,same in sorted(groups.items()):
        for a in same:
            for b in same:
                if a["seed"]>=b["seed"]:continue
                if a["public_check_rock0_sign"]==b["public_check_rock0_sign"]:continue
                if a["auditor_only_rock0_truth"]==b["auditor_only_rock0_truth"]:continue
                witness={
                    "seed_a":a["seed"],"seed_b":b["seed"],
                    "identical_public_current_observation_sha256":digest(a["public_after_move"]),
                    "previous_public_check_a":a["public_check_rock0_sign"],
                    "previous_public_check_b":b["public_check_rock0_sign"],
                    "auditor_only_rock0_truth_a":a["auditor_only_rock0_truth"],
                    "auditor_only_rock0_truth_b":b["auditor_only_rock0_truth"],
                }
                break
            if witness is not None:break
        if witness is not None:break
    report.update({
        "original_reset_calls":N,
        "original_check_step_calls":N,
        "original_move_step_calls":N,
        "native_engineering_seeds_public_consumed":list(ROCK_SEEDS),
        "distinct_five_bit_hidden_rock_vectors":len(unique_hidden),
        "distinct_post_move_public_observations":len(unique_current),
        "observed_rock0_check_signs":sorted(signs),
        "observed_hidden_rock0_truths":sorted(truths),
        "number_moved_into_native_terminal":sum(x["native_move_terminated"] for x in records),
        "same_current_public_different_previous_check_and_truth_witness":witness,
        "source_orig_public_full_trace_sha256":digest(records),
        "individual_original_public_trace_records":records,
    })
    fail_if(len(unique_hidden)<8 or len(unique_current)<3 or signs!={-1,1}
            or truths!={0,1} or witness is None,
            "PUBLIC_CS06_ROCKSOURCE_INFORMATION_ALIAS_NO_GO")
    return report
def steps_battleship(Battleship):
    import jax
    import numpy as np
    env=Battleship(rows=6,cols=6,ship_lengths=(3,2),dense_reward=False)
    o,s=env.reset_env(jax.random.PRNGKey(1200000),env.default_params)
    mask0=array(o.action_mask)
    fail_if(mask0.shape!=(36,) or not np.all(mask0==1),
            "BATTLESHIP_INITIAL_PUBLIC_ACTION_MASK_INVALID")
    o1,s1,r1,d1,info1=env.step_env(jax.random.PRNGKey(1200001),s,0,env.default_params)
    mask1=array(o1.action_mask)
    fail_if(mask1.shape!=(36,) or mask1[0]!=0 or not np.all(mask1[1:]==1),
            "BATTLESHIP_PUBLIC_MASK_DOES_NOT_REVEAL_FIRST_ACTION")
    o2,s2,r2,d2,info2=env.step_env(jax.random.PRNGKey(1200002),s1,1,env.default_params)
    mask2=array(o2.action_mask)
    fail_if(mask2.shape!=(36,) or mask2[0]!=0 or mask2[1]!=0 or
            not np.all(mask2[2:]==1),
            "BATTLESHIP_PUBLIC_MASK_DOES_NOT_REVEAL_TWO_ACTIONS")
    fail_if(bool(d1) or bool(d2),"BATTLESHIP_UNEXPECTED_EARLY_TERMINATION")
    return {"original_source_native_resets":1,"original_source_native_steps":2,
            "public_seed_consumed":1200000,
            "public_hit_observations":[array(z.obs).tolist() for z in (o,o1,o2)],
            "public_action_masks_sha256":[digest(array(z.action_mask).tolist()) for z in (o,o1,o2)],
            "public_previous_shots_encodable_in_current_mask":True,
            "hit_miss_history_not_fully_reconstructible_from_mask_alone":True,
            "source_reward_observations":[float(r1),float(r2)],
            "private_board_passed_to_policy":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    root=Path(args.upstream).resolve()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"mass.cs06.pobax.original_public_source_screen.v1",
        "frozen_first_prereg":FIRST,
        "source_role":"PUBLIC_SOURCE_ADMISSION_ENGINEERING_ONLY",
        "learners_fitted":0,"native_yggdrasil_model_tested":False,
        "unfamiliar_sealed_first_use":False,"protected_holdout_consumed":False,
        "controller_science_admission_observed":False,
        "private_source_to_policy_leak":False,
        "disposition":"PUBLIC_CS06_SOURCE_EXECUTION_BLOCKED"}
    t=time.process_time_ns()
    try:
        receipt["source"]=source_identity(root)
        RockSample,Battleship=original_scoped_modules(root)
        import jax,numpy,brax,gymnax,chex,flax
        receipt["package_versions"]={
            "jax":jax.__version__,
            "numpy":numpy.__version__,
            "brax":getattr(brax,"__version__","UNKNOWN"),
            "gymnax":getattr(gymnax,"__version__","UNKNOWN"),
            "chex":getattr(chex,"__version__","UNKNOWN"),
            "flax":getattr(flax,"__version__","UNKNOWN")}
        receipt["rocksample"]=steps_rock(RockSample,root)
        receipt["battleship"]=steps_battleship(Battleship)
        receipt["disposition"]="PUBLIC_CS06_ROCKSOURCE_ALIAS_AND_BATTLESHIP_MASK_VERIFIED"
        receipt["science_training_admissible"]="CONDITIONAL_SOURCE_INFORMATION_SUFFICIENCY_UNRESOLVED"
    except Exception as e:
        receipt["first_failure"]=type(e).__name__+":"+str(e)[:800]
    finally:
        receipt["process_cpu_ns_all_inclusive"]=time.process_time_ns()-t
        receipt["process_peak_rss_kib_inclusive"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (out/"cs06-original-source-receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("CS06_DISPOSITION="+receipt["disposition"],flush=True)
    return 0 if receipt["disposition"]=="PUBLIC_CS06_ROCKSOURCE_ALIAS_AND_BATTLESHIP_MASK_VERIFIED" else 2
if __name__=="__main__":
    raise SystemExit(main())

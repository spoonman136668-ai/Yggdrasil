"""FKP-26: ONE authorized first-use of original, exact-source CausalGym MDPPCH.do.

Four previously unopened mechanical seeds only; max 32 source actions each.
This is NOT model training or causal discovery. No second execution/replay of
uncertain-effect actions after any runtime interruption. Import the original
MDPPCH/SCM/PCH code unchanged through already qualified FKP25 targeted
namespaces, not the upstream optional-env-heavy package initializers.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"FKP-25"))
sys.path.insert(0,str(HERE.parent/"FKP-24"))
import runtime_probe as fkp25
import native_public_mdp as fkp24

SEEDS=(996100,996101,996102,996103)
MAX_ACTIONS=32
SOURCE_PIN="c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
AUTHORITY_TAG="FKP26-996100-996103-20261116"
ALLOWED_RUN_ATTEMPT="1"


def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def sha(x):
    return hashlib.sha256(x).hexdigest()


def atomic_receipt(path,doc):
    """Each per-seed completion is written before any subsequent source reset."""
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    staged=path.with_name(path.name+".tmp")
    raw=canon(doc)+b"\n"
    with staged.open("wb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    staged.replace(path)


def verify_one_shot_boundary(*,attempt,tag,seeds,limit):
    if (str(attempt)!=ALLOWED_RUN_ATTEMPT or tag!=AUTHORITY_TAG
            or tuple(seeds)!=SEEDS or type(limit) is not int
            or not 1<=limit<=MAX_ACTIONS):
        raise PermissionError("FKP26_FIRST_USE_BOUNDARY_OR_RETRY_DENIED")
    if SOURCE_PIN!=fkp24.UPSTREAM_SHA or SOURCE_PIN!=fkp25.PIN:
        raise ValueError("FKP26_INHERITED_SOURCE_PIN_DRIFT")


@contextmanager
def exact_original_factory(checkout):
    """Unmodified upstream original classes through qualified FKP25 namespaces.

    Do not use a mocked source here. FKP25 constructor preflight must have
    succeeded earlier in this same job before this method is called.
    """
    root=Path(checkout).expanduser().resolve(strict=True)
    custody=fkp25.verify_extended_original_git(root)
    deps=fkp25._require_dependency_versions()
    if not custody["clean"] or len(custody["checked_original_blobs"])!=16:
        raise ValueError("FKP26_ORIGINAL_SOURCE_UNQUALIFIED")
    if any(k=="causal_gym" or k.startswith("causal_gym.") for k in sys.modules):
        raise ValueError("FKP26_GLOBAL_SOURCE_NAMESPACE_NOT_ISOLATED")
    base=root/"causal_gym"
    paths=tuple(fkp25._ensure_checkout_file(path,root)
                for path in ("causal_gym/core/__init__.py",
                             "causal_gym/envs/mdp.py",
                             "causal_gym/core/scm.py",
                             "causal_gym/core/pch.py"))
    try:
        sys.modules["causal_gym"]=fkp25._memory_package("causal_gym",base)
        core=importlib.import_module("causal_gym.core")
        if Path(core.__file__).resolve()!=paths[0]:
            raise ValueError("FKP26_IMPORTED_CORE_PATH_MISMATCH")
        rootpkg=sys.modules["causal_gym"]
        for attr in ("SCM","PCH","Task","Graph"):
            setattr(rootpkg,attr,getattr(core,attr))
        sys.modules["causal_gym.envs"]=fkp25._memory_package(
            "causal_gym.envs",base/"envs")
        native=importlib.import_module("causal_gym.envs.mdp")
        if Path(native.__file__).resolve()!=paths[1]:
            raise ValueError("FKP26_IMPORTED_ORIGINAL_MDP_PATH_MISMATCH")
        if Path(importlib.import_module("causal_gym.core.scm").__file__).resolve()!=paths[2]:
            raise ValueError("FKP26_ORIGINAL_SCM_PATH_DRIFT")
        if Path(importlib.import_module("causal_gym.core.pch").__file__).resolve()!=paths[3]:
            raise ValueError("FKP26_ORIGINAL_PCH_PATH_DRIFT")
        from causal_gym.core.task import Task,LearningRegime
        if not issubclass(native.MDPPCH,core.PCH):
            raise ValueError("FKP26_NOT_ORIGINAL_PCH_SUBCLASS")
        def factory():
            obj=native.MDPPCH(
                max_step=30,task=Task(learning_regime=LearningRegime.do))
            if (not isinstance(obj,native.MDPPCH)
                    or not callable(obj.do)
                    or obj.task.learning_regime!=LearningRegime.do
                    or getattr(obj.env,"num_step",None)!=0):
                raise ValueError("FKP26_ORIGINAL_CONSTRUCTOR_REJECTED")
            return obj
        yield factory,{"original_sha":SOURCE_PIN,
                       "source_blobs_verified":len(custody["checked_original_blobs"]),
                       "package_import_mode":"FKP25_TARGETED_ORIGINAL_SOURCE_NOT_STOCK",
                       "dependencies":deps}
    finally:
        for k in tuple(sys.modules):
            if k=="causal_gym" or k.startswith("causal_gym."):
                del sys.modules[k]


def validate_complete_transcript(row,expected_seed,policy):
    if (row.get("public_seed")!=expected_seed or
            row.get("upstream_sha")!=SOURCE_PIN or
            row.get("schema")!="fkp24.native-public-mdp-transcript.v1" or
            row.get("counterfactuals_used") is not False or
            row.get("forbidden_info_passed_to_policy") is not False):
        raise ValueError("FKP26_PUBLIC_TRANSCRIPT_CONTRACT_VIOLATION")
    n=row.get("physical_do_actions")
    events=row.get("public_transitions")
    if (type(n) is not int or not 1<=n<=MAX_ACTIONS
            or type(events) is not list or len(events)!=n
            or policy.actions!=n or len(policy.received)!=n):
        raise ValueError("FKP26_ACTION_COUNT_OR_POLICY_MISMATCH")
    allowed={"before","action","reward","after","terminated","truncated"}
    for index,e in enumerate(events):
        if (type(e) is not dict or set(e)!=allowed
                or any(type(e[k]) is not int or e[k] not in (0,1)
                       for k in ("before","action","reward","after"))
                or type(e["terminated"]) is not bool
                or type(e["truncated"]) is not bool
                or (index<n-1 and (e["terminated"] or e["truncated"]))):
            raise ValueError("FKP26_PRIVATE_OR_INVALID_PUBLIC_ROW")
    if sha(canon(events))!=row.get("public_transitions_sha256"):
        raise ValueError("FKP26_PUBLIC_TRANSCRIPT_SHA_DRIFT")
    if not row["ended_by_source"] and not row["budget_exhausted"]:
        raise ValueError("FKP26_EARLY_TERMINATION_WITHOUT_CAUSE")
    if row["ended_by_source"] and row["budget_exhausted"]:
        raise ValueError("FKP26_INCONSISTENT_END_CAUSE")


def run_approved(checkout,out_dir,*,expected_git_head,attempt,tag):
    verify_one_shot_boundary(attempt=attempt,tag=tag,seeds=SEEDS,limit=MAX_ACTIONS)
    if (type(expected_git_head) is not str or len(expected_git_head)!=40
            or any(c not in "0123456789abcdef" for c in expected_git_head)):
        raise ValueError("FKP26_CANDIDATE_SOURCE_HEAD_INVALID")
    out_dir=Path(out_dir)
    out_dir.mkdir(parents=True,exist_ok=False)  # no accidental reuse
    journal=out_dir/"execution-journal.json"
    state={"schema":"yggdrasil.fkp26.original-mechanical-first-use.v1",
           "classification":"STARTED_NO_SOURCE_ACTION_YET",
           "candidate_sha":expected_git_head,
           "source_sha":SOURCE_PIN,
           "authorized_mechanical_seeds":list(SEEDS),
           "max_actions_each":MAX_ACTIONS,
           "max_actions_total":MAX_ACTIONS*len(SEEDS),
           "run_attempt":int(attempt),
           "github_run_id":os.environ.get("GITHUB_RUN_ID","UNKNOWN"),
           "completed":[],"currently_at_seed":None,
           "scientific_pass":False,"trained_model":False,
           "native_accepted":False,"protected_seeds_opened":False,
           "source_original":True,"source_private_info_in_policy":False}
    atomic_receipt(journal,state)
    try:
        # This gate requires zero-source FKP25 original constructor preflight
        # as a separate earlier step of the SAME run.
        with exact_original_factory(checkout) as (factory,source_meta):
            state["source_custody"]=source_meta
            for seed in SEEDS:
                state["classification"]="SOURCE_FIRST_USE_IN_PROGRESS_NO_RETRY"
                state["currently_at_seed"]=seed
                atomic_receipt(journal,state)
                policy=fkp24.FixedPublicPolicy()
                original=fkp24.public_mechanical_episode(
                    factory,policy,seed=seed,max_actions=MAX_ACTIONS)
                validate_complete_transcript(original,seed,policy)
                # Commit an exact public source-only seed receipt BEFORE next
                # reset; if a later seed fails, earlier outcomes survive.
                receipt_path=out_dir/("seed-%d.json"%seed)
                atomic_receipt(receipt_path,original)
                state["completed"].append({
                    "seed":seed,
                    "physical_do_actions":original["physical_do_actions"],
                    "earned_reward_count":sum(r["reward"] for r in original["public_transitions"]),
                    "public_transitions_sha256":original["public_transitions_sha256"],
                    "public_receipt_sha256":sha(canon(original)),
                    "ended_by_source":original["ended_by_source"]})
                state["currently_at_seed"]=None
                state["completed_physical_do_actions"]=sum(
                    r["physical_do_actions"] for r in state["completed"])
                atomic_receipt(journal,state)
        if [r["seed"] for r in state["completed"]]!=list(SEEDS):
            raise AssertionError("FKP26_INCOMPLETE_AUTHORIZED_SOURCE_COHORT")
        total=state["completed_physical_do_actions"]
        if not 4<=total<=128:
            raise AssertionError("FKP26_TOTAL_ACTION_BUDGET_DRIFT")
        state["classification"]="ORIGINAL_EXTERNAL_MDP_PUBLIC_MECHANICAL_PASS"
        state["mechanical_source_first_use_complete"]=True
        state["source_first_use"]=True
        state["observed_external_do_actions"]=total
        state["currently_at_seed"]=None
        state["scientific_pass"]=False
        atomic_receipt(journal,state)
        result={k:v for k,v in state.items() if k!="source_custody"}
        result["source_custody"]=state["source_custody"]
        result["receipt_sha256"]=sha(canon(result))
        atomic_receipt(out_dir/"complete.json",result)
        print("FKP26_ORIGINAL_MDP_MECHANICAL_RESULT="+json.dumps({
            "classification":result["classification"],
            "source_sha":result["source_sha"],
            "candidate_sha":result["candidate_sha"],
            "completed":result["completed"],
            "observed_external_do_actions":total,
            "scientific_pass":False,
            "receipt_sha256":result["receipt_sha256"],
        },sort_keys=True,separators=(",",":")),flush=True)
        return result
    except BaseException:
        state["classification"]="STOPPED_AFTER_POTENTIAL_SOURCE_FIRST_USE_NO_REPLAY"
        state["mechanical_source_first_use_complete"]=False
        state["source_first_use"]="POSSIBLY_CONSUMED_OR_PARTIALLY_CONSUMED"
        atomic_receipt(journal,state)
        raise


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--checkout",required=True)
    p.add_argument("--output-dir",required=True)
    p.add_argument("--candidate-sha",required=True)
    args=p.parse_args()
    run_approved(args.checkout,args.output_dir,
                 expected_git_head=args.candidate_sha,
                 attempt=os.environ.get("GITHUB_RUN_ATTEMPT",""),
                 tag=os.environ.get("FKP26_APPROVED_ONCE",""))


if __name__=="__main__":
    main()

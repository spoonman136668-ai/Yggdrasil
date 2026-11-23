#!/usr/bin/env python3
"""One-episode API smoke on the exact pinned, historically consumed CausalGym DTR family."""
from __future__ import annotations
import argparse, hashlib, importlib, importlib.util, json, platform, subprocess, sys, tempfile, types, urllib.request, shutil, os
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

EXPERIMENT="WSCM-CAUSALGYM-DTR-API-SMOKE-01"
SOURCE_REPO="CausalAILab/Causal-Gymnasium"
SOURCE_COMMIT="c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
RAW_ROOT=f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_COMMIT}/"
SEED=20261123
PINNED={"numpy":"1.26.4","gymnasium":"0.29.1","networkx":"3.4.2","toposort":"1.10","pydash":"8.0.5"}
SOURCE_BLOBS={
"LICENSE":"993e3a4922f003dced0fd061735697c850ea7205","setup.py":"31097c35f908e393bfd4763a298c1d5f4ab60600",
"causal_gym/envs/dtr.py":"6af2371dce21804140ea141ccb7be14e003ba275",
"causal_gym/core/scm.py":"f66f2638c797cfeaf0e96d4e13c06d4fabc2c8d5",
"causal_gym/core/pch.py":"ff37780c6b791877c70583b8d5f699be7fcd8817",
"causal_gym/core/types.py":"4a591d6ec18c0c8807885b698e7fe8086a35279e",
"causal_gym/core/task.py":"668262f3f5c88fa2865b08ef10bbf96b09a3b73e",
"causal_gym/core/policy_scope.py":"284b4a1ae031ef401d106fde603ba016e0d8136d",
"causal_gym/core/graph.py":"6be7da2fbd8a6d6df45d273d34c40b44f0fe6af6",
"causal_gym/core/graph_defs.py":"5ec4cfd96ed0be5e8334ebb856941cf39dd1974d",
"causal_gym/core/graph_utils.py":"1f51ddc8d739cf41ec2ef5931cb2668e6f7d811b",
"causal_gym/core/set_utils.py":"ed914a581fa22152d6086b2e4d642045c954908e",
"causal_gym/core/object_utils.py":"477a83eaef8605d222dab5ebfeeb5e33edd9f3e4"
}

def git_blob_sha(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii")+data).hexdigest()

def download_sources(root):
    verified,errors=0,[]
    for rel,expected in SOURCE_BLOBS.items():
        try:
            req=urllib.request.Request(RAW_ROOT+rel,headers={"User-Agent":"Yggdrasil-WSCM-DTR-smoke/1"})
            with urllib.request.urlopen(req,timeout=30) as response: data=response.read(8*1024*1024+1)
            if len(data)>8*1024*1024: errors.append(f"{rel}:FILE_TOO_LARGE"); continue
            if git_blob_sha(data)!=expected: errors.append(f"{rel}:GIT_BLOB_MISMATCH"); continue
            dest=root/rel; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(data); verified+=1
        except Exception as exc: errors.append(f"{rel}:{type(exc).__name__}")
    return verified,errors

def ensure_packages(target):
    sys.path.insert(0,str(target)); importlib.invalidate_caches()
    versions={}
    try:
        for name,expected in PINNED.items():
            actual=version(name)
            if actual!=expected: raise PackageNotFoundError(name)
            versions[name]=actual
        return True,versions
    except PackageNotFoundError:
        try: sys.path.remove(str(target))
        except ValueError: pass
        if target.exists(): shutil.rmtree(target)
    args=[sys.executable,"-m","pip","install","--disable-pip-version-check","--no-input","--only-binary=:all:","--target",str(target),"--upgrade"]+[f"{n}=={v}" for n,v in PINNED.items()]
    try: proc=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,timeout=900)
    except Exception as exc: return False,"PIP_EXECUTION_"+type(exc).__name__
    if proc.returncode!=0: return False,f"PIP_EXIT_{proc.returncode}"
    sys.path.insert(0,str(target)); importlib.invalidate_caches()
    try:
        for name,expected in PINNED.items():
            actual=version(name)
            if actual!=expected: return False,"PIN_MISMATCH_"+name.upper()
            versions[name]=actual
        return True,versions
    except PackageNotFoundError as exc: return False,"PACKAGE_METADATA_MISSING_"+str(exc)

def load_dtr(root):
    missing=[n for n in PINNED if importlib.util.find_spec(n) is None]
    if missing: return None,"MISSING_DEPENDENCY:"+missing[0]
    package=types.ModuleType("causal_gym"); package.__path__=[str(root/"causal_gym")]; package.__package__="causal_gym"; sys.modules["causal_gym"]=package
    core=types.ModuleType("causal_gym.core"); core.__path__=[str(root/"causal_gym"/"core")]; core.__package__="causal_gym.core"; sys.modules["causal_gym.core"]=core
    envs=types.ModuleType("causal_gym.envs"); envs.__path__=[str(root/"causal_gym"/"envs")]; envs.__package__="causal_gym.envs"; sys.modules["causal_gym.envs"]=envs
    try:
        t=importlib.import_module("causal_gym.core.types"); task=importlib.import_module("causal_gym.core.task")
        scm=importlib.import_module("causal_gym.core.scm"); pch=importlib.import_module("causal_gym.core.pch")
        graph=importlib.import_module("causal_gym.core.graph")
        for n in ("ObsType","ActType","PolicyType","WrapperObsType","WrapperActType","WrapperPolicyType"): setattr(core,n,getattr(t,n))
        core.Task,core.SCM,core.PCH,core.Graph=task.Task,scm.SCM,pch.PCH,graph.Graph
        package.SCM,package.PCH=scm.SCM,pch.PCH
        dtr=importlib.import_module("causal_gym.envs.dtr")
        if dtr.DTRSCM.__module__!="causal_gym.envs.dtr" or dtr.DTRPCH.__module__!="causal_gym.envs.dtr":
            return None,"UPSTREAM_CLASS_IDENTITY_MISMATCH"
        return dtr.DTRSCM,None
    except Exception as exc: return None,"IMPORT_ERROR_"+type(exc).__name__

def smoke(cls):
    env=cls()
    s1,_=env.reset(seed=SEED)
    s2,r1,t1,tr1,_=env.step(0)
    obs2,y,t2,tr2,_=env.step(1)
    ok=(type(s1) is int and s1 in (0,1) and type(s2) is int and s2 in (0,1)
        and r1==0 and t1 is False and tr1 is False and obs2 is None
        and type(y) is int and y in (0,1) and t2 is True and tr2 is False and env.stage==2)
    record={"seed":SEED,"episodes":1,"actions":[0,1],"s1":s1,"s2":s2,"y":y,
            "first_stage_terminated":t1,"final_terminated":t2,"final_truncated":tr2,"final_stage":env.stage}
    return ok,record

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--out",required=True); args=parser.parse_args()
    errors=[]; verified=0; dep_ok=False; dep_status="NOT_ATTEMPTED"; versions={}; api_ok=False; api_status="NOT_ATTEMPTED"; public={}
    target=Path(os.environ.get("RUNNER_TEMP",tempfile.gettempdir()))/"wscm-causalgym-smoke-packages"
    with tempfile.TemporaryDirectory(prefix="wscm-causalgym-dtr-source-") as tmp:
        root=Path(tmp); verified,errors=download_sources(root)
        if not errors and verified==len(SOURCE_BLOBS):
            dep_ok,dep=ensure_packages(target)
            if dep_ok:
                versions=dep; cls,err=load_dtr(root)
                if cls is not None:
                    api_ok,public=smoke(cls); api_status="DTR_TWO_STAGE_PUBLIC_API_PASS" if api_ok else "DTR_TWO_STAGE_PUBLIC_API_ASSERTION_FAILED"
                else: api_status=err
            else: dep_status=dep
    result={
      "schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,
      "status":"DTR_API_SMOKE_PASS" if api_ok else ("SOURCE_FETCH_BLOCKED" if errors else ("DEPENDENCY_INSTALL_BLOCKED" if not dep_ok else "DTR_API_SMOKE_BLOCKED")),
      "metrics":{
        "source_repository":SOURCE_REPO,"source_commit":SOURCE_COMMIT,"source_file_count_expected":len(SOURCE_BLOBS),
        "source_file_count_git_blob_verified":verified,"source_blob_errors":sorted(errors),
        "dependency_install_pass":dep_ok,"dependency_install_status":"PINNED_TEMPORARY_DEPENDENCIES_AVAILABLE" if dep_ok else dep_status,
        "dependency_versions":versions,"api_smoke_pass":api_ok,"api_smoke_status":api_status,"public_observation":public,
        "source_family_previously_consumed":True,"source_family_virgin":False,"scored":False,
        "native_learner_updates":0,"model_fits":0,"heldout_scoring":0,
        "source_environment_constructed":api_ok,"source_reset_calls":1 if api_ok else 0,
        "source_step_calls":2 if api_ok else 0,"source_interventions":2 if api_ok else 0,
        "persistent_runner_changes":0,"dependency_target":"RUNNER_TEMP; parent workflow cleans after both child interpreters exit"
      },
      "scientific_pass":False,"scientific_gain_verified":False,"source_first_use":False
    }
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    return 0
if __name__=="__main__": raise SystemExit(main())

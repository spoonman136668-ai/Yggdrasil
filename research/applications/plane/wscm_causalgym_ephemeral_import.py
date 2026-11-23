#!/usr/bin/env python3
"""Pinned Causal-Gymnasium import preflight with a job-scoped dependency target."""
from __future__ import annotations
import argparse, hashlib, importlib, importlib.util, json, platform, subprocess, sys, tempfile, types, urllib.request, shutil, os
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
EXPERIMENT = "WSCM-CAUSALGYM-EPHEMERAL-IMPORT-02"
SOURCE_REPO = "CausalAILab/Causal-Gymnasium"
SOURCE_COMMIT = "c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
RAW_ROOT = f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_COMMIT}/"
SOURCE_BLOBS = {
"LICENSE":"993e3a4922f003dced0fd061735697c850ea7205","setup.py":"31097c35f908e393bfd4763a298c1d5f4ab60600",
"causal_gym/envs/dtr.py":"6af2371dce21804140ea141ccb7be14e003ba275","causal_gym/core/scm.py":"f66f2638c797cfeaf0e96d4e13c06d4fabc2c8d5",
"causal_gym/core/pch.py":"ff37780c6b791877c70583b8d5f699be7fcd8817","causal_gym/core/types.py":"4a591d6ec18c0c8807885b698e7fe8086a35279e",
"causal_gym/core/task.py":"668262f3f5c88fa2865b08ef10bbf96b09a3b73e","causal_gym/core/policy_scope.py":"284b4a1ae031ef401d106fde603ba016e0d8136d",
"causal_gym/core/graph.py":"6be7da2fbd8a6d6df45d273d34c40b44f0fe6af6","causal_gym/core/graph_defs.py":"5ec4cfd96ed0be5e8334ebb856941cf39dd1974d",
"causal_gym/core/graph_utils.py":"1f51ddc8d739cf41ec2ef5931cb2668e6f7d811b","causal_gym/core/set_utils.py":"ed914a581fa22152d6086b2e4d642045c954908e",
"causal_gym/core/object_utils.py":"477a83eaef8605d222dab5ebfeeb5e33edd9f3e4"}
PINNED={"numpy":"1.26.4","gymnasium":"0.29.1","networkx":"3.4.2","toposort":"1.10","pydash":"8.0.5"}
def git_blob_sha(data): return hashlib.sha1(f"blob {len(data)}\0".encode("ascii")+data).hexdigest()
def download_pinned_files(root):
    verified,errors=0,[]
    for rel,expected in SOURCE_BLOBS.items():
        try:
            req=urllib.request.Request(RAW_ROOT+rel,headers={"User-Agent":"Yggdrasil-WSCM-source-preflight/2"})
            with urllib.request.urlopen(req,timeout=30) as response: data=response.read(8*1024*1024+1)
            if len(data)>8*1024*1024: errors.append(f"{rel}:FILE_TOO_LARGE"); continue
            if git_blob_sha(data)!=expected: errors.append(f"{rel}:GIT_BLOB_MISMATCH"); continue
            dest=root/rel; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(data); verified+=1
        except Exception as exc: errors.append(f"{rel}:{type(exc).__name__}")
    return verified,errors
def ensure_ephemeral_dependencies(target):
    target.parent.mkdir(parents=True,exist_ok=True); sys.path.insert(0,str(target)); importlib.invalidate_caches()
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
def import_exact_dtr_modules(root):
    missing=[name for name in PINNED if importlib.util.find_spec(name) is None]
    if missing: return False,"MISSING_DEPENDENCIES:"+",".join(missing)
    package=types.ModuleType("causal_gym"); package.__path__=[str(root/"causal_gym")]; package.__package__="causal_gym"; sys.modules["causal_gym"]=package
    core=types.ModuleType("causal_gym.core"); core.__path__=[str(root/"causal_gym"/"core")]; core.__package__="causal_gym.core"; sys.modules["causal_gym.core"]=core
    envs=types.ModuleType("causal_gym.envs"); envs.__path__=[str(root/"causal_gym"/"envs")]; envs.__package__="causal_gym.envs"; sys.modules["causal_gym.envs"]=envs
    try:
        t=importlib.import_module("causal_gym.core.types"); task=importlib.import_module("causal_gym.core.task")
        scm=importlib.import_module("causal_gym.core.scm"); pch=importlib.import_module("causal_gym.core.pch")
        graph=importlib.import_module("causal_gym.core.graph")
        for name in ("ObsType","ActType","PolicyType","WrapperObsType","WrapperActType","WrapperPolicyType"): setattr(core,name,getattr(t,name))
        core.Task,core.SCM,core.PCH,core.Graph=task.Task,scm.SCM,pch.PCH,graph.Graph
        package.SCM,package.PCH=scm.SCM,pch.PCH
        dtr=importlib.import_module("causal_gym.envs.dtr")
        if dtr.DTRSCM.__module__!="causal_gym.envs.dtr" or dtr.DTRPCH.__module__!="causal_gym.envs.dtr": return False,"UPSTREAM_CLASS_IDENTITY_MISMATCH"
        return True,"EXACT_DTRSCM_AND_DTRPCH_IMPORTED_NO_ENVIRONMENT_CREATED"
    except Exception as exc: return False,"IMPORT_ERROR_"+type(exc).__name__
def main():
    p=argparse.ArgumentParser(); p.add_argument("--out",required=True); args=p.parse_args()
    errors=[]; verified=0; dep_ok=False; dep_status="NOT_ATTEMPTED"; versions={}; imported=False; import_status="NOT_ATTEMPTED"
    runner_temp=Path(os.environ.get("RUNNER_TEMP",tempfile.gettempdir()))
    target=runner_temp/"wscm-causalgym-import02-packages"
    with tempfile.TemporaryDirectory(prefix="wscm-causalgym-source-") as tmp:
        root=Path(tmp); verified,errors=download_pinned_files(root)
        if not errors and verified==len(SOURCE_BLOBS):
            dep_ok,dep_result=ensure_ephemeral_dependencies(target)
            if dep_ok: versions=dep_result; imported,import_status=import_exact_dtr_modules(root)
            else: dep_status=dep_result
        else: dep_status="SOURCE_FETCH_INCOMPLETE"
    result={"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,
    "status":"SOURCE_IMPORT_PASS" if imported else ("SOURCE_FETCH_BLOCKED" if errors else ("DEPENDENCY_INSTALL_BLOCKED" if not dep_ok else "SOURCE_IMPORT_BLOCKED")),
    "metrics":{"source_repository":SOURCE_REPO,"source_commit":SOURCE_COMMIT,"source_file_count_expected":len(SOURCE_BLOBS),
    "source_file_count_git_blob_verified":verified,"source_blob_errors":sorted(errors),"dependency_install_pass":dep_ok,
    "dependency_install_status":"PINNED_TEMPORARY_DEPENDENCIES_AVAILABLE" if dep_ok else dep_status,"dependency_versions":versions,
    "dependency_target":"RUNNER_TEMP; parent workflow cleans after both child interpreters exit","class_import_pass":imported,
    "import_status":import_status,"python_version":platform.python_version(),"source_environment_constructed":False,
    "source_reset_calls":0,"source_step_calls":0,"source_interventions":0,"model_fits":0,"persistent_runner_changes":0},
    "scientific_pass":False,"scientific_gain_verified":False,"source_first_use":False}
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8"); return 0
if __name__=="__main__": raise SystemExit(main())

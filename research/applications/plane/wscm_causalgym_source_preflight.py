#!/usr/bin/env python3
"""Pinned Causal-Gymnasium import preflight; deliberately performs zero source interactions."""
from __future__ import annotations
import argparse, hashlib, importlib, importlib.util, json, platform, sys, tempfile, types, urllib.request
from pathlib import Path

EXPERIMENT = "WSCM-CAUSALGYM-SOURCE-PREFLIGHT-01"
SOURCE_REPO = "CausalAILab/Causal-Gymnasium"
SOURCE_COMMIT = "c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
RAW_ROOT = f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_COMMIT}/"
SOURCE_BLOBS = {
    "LICENSE": "993e3a4922f003dced0fd061735697c850ea7205",
    "setup.py": "31097c35f908e393bfd4763a298c1d5f4ab60600",
    "causal_gym/envs/dtr.py": "6af2371dce21804140ea141ccb7be14e003ba275",
    "causal_gym/core/scm.py": "f66f2638c797cfeaf0e96d4e13c06d4fabc2c8d5",
    "causal_gym/core/pch.py": "ff37780c6b791877c70583b8d5f699be7fcd8817",
    "causal_gym/core/types.py": "4a591d6ec18c0c8807885b698e7fe8086a35279e",
    "causal_gym/core/task.py": "668262f3f5c88fa2865b08ef10bbf96b09a3b73e",
    "causal_gym/core/policy_scope.py": "284b4a1ae031ef401d106fde603ba016e0d8136d",
    "causal_gym/core/graph.py": "6be7da2fbd8a6d6df45d273d34c40b44f0fe6af6",
    "causal_gym/core/graph_defs.py": "5ec4cfd96ed0be5e8334ebb856941cf39dd1974d",
    "causal_gym/core/graph_utils.py": "1f51ddc8d739cf41ec2ef5931cb2668e6f7d811b",
    "causal_gym/core/set_utils.py": "ed914a581fa22152d6086b2e4d642045c954908e",
    "causal_gym/core/object_utils.py": "477a83eaef8605d222dab5ebfeeb5e33edd9f3e4",
}
REQUIRED_MODULES = ("numpy", "gymnasium", "networkx", "toposort", "pydash")

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()

def download_pinned_files(root: Path):
    verified, errors = 0, []
    for relpath, expected in SOURCE_BLOBS.items():
        try:
            request = urllib.request.Request(RAW_ROOT + relpath, headers={"User-Agent":"Yggdrasil-WSCM-source-preflight/1"})
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read(8 * 1024 * 1024 + 1)
            if len(data) > 8 * 1024 * 1024:
                errors.append(f"{relpath}:FILE_TOO_LARGE"); continue
            if git_blob_sha(data) != expected:
                errors.append(f"{relpath}:GIT_BLOB_MISMATCH"); continue
            dest = root / relpath
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            verified += 1
        except Exception as exc:
            errors.append(f"{relpath}:{type(exc).__name__}")
    return verified, errors

def import_exact_dtr_modules(root: Path):
    missing = [name for name in REQUIRED_MODULES if importlib.util.find_spec(name) is None]
    if missing:
        return False, "MISSING_DEPENDENCIES:" + ",".join(missing)
    # Namespace containers only; all imported behavior/classes come from the
    # exact upstream source files. This bypasses unrelated eager env imports.
    package = types.ModuleType("causal_gym")
    package.__path__ = [str(root / "causal_gym")]
    package.__package__ = "causal_gym"
    sys.modules["causal_gym"] = package
    core = types.ModuleType("causal_gym.core")
    core.__path__ = [str(root / "causal_gym" / "core")]
    core.__package__ = "causal_gym.core"
    sys.modules["causal_gym.core"] = core
    envs = types.ModuleType("causal_gym.envs")
    envs.__path__ = [str(root / "causal_gym" / "envs")]
    envs.__package__ = "causal_gym.envs"
    sys.modules["causal_gym.envs"] = envs
    try:
        type_module = importlib.import_module("causal_gym.core.types")
        task_module = importlib.import_module("causal_gym.core.task")
        scm_module = importlib.import_module("causal_gym.core.scm")
        pch_module = importlib.import_module("causal_gym.core.pch")
        graph_module = importlib.import_module("causal_gym.core.graph")
        for name in ("ObsType","ActType","PolicyType","WrapperObsType","WrapperActType","WrapperPolicyType"):
            setattr(core, name, getattr(type_module, name))
        core.Task, core.SCM, core.PCH, core.Graph = task_module.Task, scm_module.SCM, pch_module.PCH, graph_module.Graph
        package.SCM, package.PCH = scm_module.SCM, pch_module.PCH
        dtr_module = importlib.import_module("causal_gym.envs.dtr")
        assert dtr_module.DTRSCM.__module__ == "causal_gym.envs.dtr"
        assert dtr_module.DTRPCH.__module__ == "causal_gym.envs.dtr"
        # Import and inspect class definitions only: no environment instance.
        return True, "EXACT_DTR_CLASSES_IMPORTED_NO_ENVIRONMENT_CREATED"
    except Exception as exc:
        return False, "IMPORT_ERROR:" + type(exc).__name__

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="wscm-causalgym-preflight-") as tmp:
        root = Path(tmp)
        verified, fetch_errors = download_pinned_files(root)
        imports, import_status = (False, "NOT_ATTEMPTED_SOURCE_BYTES_INCOMPLETE")
        if not fetch_errors and verified == len(SOURCE_BLOBS):
            imports, import_status = import_exact_dtr_modules(root)
    result = {
        "schema":"yggdrasil.research-scientific-result.v1",
        "experiment":EXPERIMENT,
        "status":"SOURCE_IMPORT_PASS" if imports else ("SOURCE_FETCH_BLOCKED" if fetch_errors else "SOURCE_IMPORT_BLOCKED"),
        "metrics":{
            "source_repository":SOURCE_REPO,"source_commit":SOURCE_COMMIT,
            "source_file_count_expected":len(SOURCE_BLOBS),"source_file_count_git_blob_verified":verified,
            "source_blob_errors":sorted(fetch_errors),
            "required_dependency_presence":{name:importlib.util.find_spec(name) is not None for name in REQUIRED_MODULES},
            "class_import_pass":imports,"import_status":import_status,"python_version":platform.python_version(),
            "source_environment_constructed":False,"source_reset_calls":0,"source_step_calls":0,
            "source_interventions":0,"model_fits":0,"persistent_runner_changes":0
        },
        "scientific_pass":False,"scientific_gain_verified":False,"source_first_use":False
    }
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

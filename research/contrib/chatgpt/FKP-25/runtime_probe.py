"""FKP-25 targeted constructor of exact original external CausalGym MDPSCM/MDPPCH.

Execution loads all original core/MDP source files from an exact, clean,
detached CausalAILab/Causal-Gymnasium Git checkout. It DOES NOT execute the
upstream package's unrelated eager envs/__init__.py imports; those two package
containers are in-memory Python import namespaces. Thus this qualifies the
ORIGINAL target causal implementation with targeted import wiring, NOT a
stock full-distribution package import.

ABSOLUTE first-use fence: no reset(), do(), step(), see(), ctf_do(), seeded
worlds, source rewards, learner training, hidden state read or model promotion.
The constructor is called, but no source world is instantiated by reset.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib
from importlib import metadata
from importlib.machinery import ModuleSpec
import json
from pathlib import Path
import subprocess
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"FKP-24"))
from verify_upstream import inspect_exact_checkout, PIN, REQUIRED as FKP24_REQUIRED


DIRECT_PINNED={
    "causal_gym/envs/__init__.py":"a36a43e2ccbca2c924db6b2852c70b5635bca181",
    "causal_gym/core/__init__.py":"7affd0694b0f31dcc05e3d6b47a5eaf3d311e327",
    "causal_gym/core/policy_scope.py":"284b4a1ae031ef401d106fde603ba016e0d8136d",
    "causal_gym/core/types.py":"4a591d6ec18c0c8807885b698e7fe8086a35279e",
    "causal_gym/core/graph.py":"6be7da2fbd8a6d6df45d273d34c40b44f0fe6af6",
    "causal_gym/core/graph_utils.py":"1f51ddc8d739cf41ec2ef5931cb2668e6f7d811b",
    "causal_gym/core/graph_defs.py":"5ec4cfd96ed0be5e8334ebb856941cf39dd1974d",
    "causal_gym/core/set_utils.py":"ed914a581fa22152d6086b2e4d642045c954908e",
    "causal_gym/core/object_utils.py":"477a83eaef8605d222dab5ebfeeb5e33edd9f3e4"
}
ALL_SOURCE_BLOBS={**FKP24_REQUIRED, **DIRECT_PINNED}
PINNED_PACKAGES={
    "numpy":"1.26.4",
    "gymnasium":"0.29.1",
    "networkx":"3.2.1",
    "toposort":"1.10",
    "pydash":"8.0.5"
}


def _json(value):
    return json.dumps(value,sort_keys=True,allow_nan=False,
                      separators=(",",":")).encode("ascii")


def _require_dependency_versions(*,get_version=metadata.version):
    result={}
    for name,expected in PINNED_PACKAGES.items():
        try:
            value=get_version(name)
        except metadata.PackageNotFoundError as e:
            raise ValueError("FKP25_PINNED_DEPENDENCY_MISSING:"+name) from e
        if value!=expected:
            raise ValueError("FKP25_PINNED_DEPENDENCY_DRIFT:"+name)
        result[name]=value
    return result


def verify_extended_original_git(path,*,runner=subprocess.run):
    """Strictly read-only exact Git custody; no import occurs here."""
    base=Path(path).expanduser().resolve(strict=True)
    previous=inspect_exact_checkout(base,runner=runner)
    if previous["commit"]!=PIN or previous["actual_env_executed"] is not False:
        raise ValueError("FKP25_PREDECESSOR_CUSTODY_FAILED")
    for file,expected in DIRECT_PINNED.items():
        result=runner(["git","-C",str(base),"rev-parse","HEAD:"+file],
                      check=True,capture_output=True,text=True)
        if result.stdout.strip()!=expected:
            raise ValueError("FKP25_EXTERNAL_SOURCE_BLOB_DRIFT:"+file)
    return {"original_source_sha":PIN,"checked_original_blobs":
            dict(sorted(ALL_SOURCE_BLOBS.items())),"clean":True,
            "real_actions":0}


def _memory_package(name,path):
    pkg=types.ModuleType(name)
    pkg.__package__=name
    pkg.__path__=[str(path)]
    pkg.__spec__=ModuleSpec(name,loader=None,is_package=True)
    pkg.__file__=None
    return pkg


def _ensure_checkout_file(file,root):
    expected=(root/file).resolve(strict=True)
    if not expected.is_file() or not expected.is_relative_to(root):
        raise ValueError("FKP25_ORIGINAL_FILE_NOT_IN_CHECKOUT:"+file)
    return expected


def _constructor_in_isolated_import_space(root):
    """Original code imported through source-only module namespaces.

    Never replace the MDPSCM/MDPPCH class, patch its implementation, execute
    upstream package-wide initializer, or use real-world seed/data.
    """
    if any(key=="causal_gym" or key.startswith("causal_gym.")
           for key in sys.modules):
        raise ValueError("FKP25_EXISTING_UPSTREAM_MODULES_NOT_ISOLATED")
    paths=[_ensure_checkout_file(p,root) for p in
           ("causal_gym/core/__init__.py",
            "causal_gym/envs/mdp.py",
            "causal_gym/core/scm.py",
            "causal_gym/core/pch.py")]
    rootpkg=root/"causal_gym"
    try:
        sys.modules["causal_gym"]=_memory_package("causal_gym",rootpkg)
        core=importlib.import_module("causal_gym.core")
        root_module=sys.modules["causal_gym"]
        if core.__file__ is None or Path(core.__file__).resolve()!=paths[0]:
            raise ValueError("FKP25_ORIGINAL_CORE_IMPORT_PATH_DRIFT")
        if not hasattr(core,"SCM") or not hasattr(core,"PCH"):
            raise ValueError("FKP25_ORIGINAL_CORE_PUBLIC_EXPORT_MISSING")
        root_module.SCM=core.SCM
        root_module.PCH=core.PCH
        root_module.Task=core.Task
        root_module.Graph=core.Graph
        envs=_memory_package("causal_gym.envs",rootpkg/"envs")
        sys.modules["causal_gym.envs"]=envs
        native=importlib.import_module("causal_gym.envs.mdp")
        if native.__file__ is None or Path(native.__file__).resolve()!=paths[1]:
            raise ValueError("FKP25_ORIGINAL_MDP_IMPORT_PATH_DRIFT")
        if Path(importlib.import_module("causal_gym.core.scm").__file__).resolve()!=paths[2]:
            raise ValueError("FKP25_ORIGINAL_SCM_SOURCE_CHANGED")
        if Path(importlib.import_module("causal_gym.core.pch").__file__).resolve()!=paths[3]:
            raise ValueError("FKP25_ORIGINAL_PCH_SOURCE_CHANGED")
        if not issubclass(native.MDPSCM,core.SCM) or (
                not issubclass(native.MDPPCH,core.PCH)):
            raise ValueError("FKP25_ORIGINAL_CLASS_MISMATCH")
        from causal_gym.core.task import Task,LearningRegime
        obj=native.MDPPCH(
            max_step=30,task=Task(learning_regime=LearningRegime.do))
        if not isinstance(obj,native.MDPPCH) or not callable(obj.do):
            raise ValueError("FKP25_ORIGINAL_NATIVE_MDP_CONSTRUCTION_FAILED")
        if obj.task.learning_regime!=LearningRegime.do:
            raise ValueError("FKP25_INTERVENTION_ONLY_REGIME_DRIFT")
        # Original constructor sets num_step=0 and does not draw RNG or
        # perform a seeded reset. Harness-only check, NEVER model input.
        if getattr(obj.env,"num_step",None)!=0:
            raise ValueError("FKP25_CONSTRUCTOR_PRECONSUMED_SOURCE_STEPS")
        return {
            "original_core_entrypoint":paths[0].relative_to(root).as_posix(),
            "original_mdp_entrypoint":paths[1].relative_to(root).as_posix(),
            "original_mdp_class":"causal_gym.envs.mdp.MDPPCH",
            "source_classes_unmodified":True,
            "constructor_created":True,
            "do_method_present":True,
            "source_learning_regime":"do",
            "package_import_mode":"PINNED_TARGETED_NAMESPACE_NOT_STOCK_PACKAGE_INIT",
            "package_initializers_replaced_with_in_memory_namespaces":[
                "causal_gym/__init__.py","causal_gym/envs/__init__.py"],
            "reset_invocations":0,"do_invocations":0,
            "external_physical_actions":0,"world_seeds_consumed":0
        }
    finally:
        for key in list(sys.modules):
            if key=="causal_gym" or key.startswith("causal_gym."):
                del sys.modules[key]


def probe_exact_original_constructor(checkout):
    root=Path(checkout).expanduser().resolve(strict=True)
    custody=verify_extended_original_git(root)
    deps=_require_dependency_versions()
    runtime=_constructor_in_isolated_import_space(root)
    report={
        "schema":"fkp25.unchanged-mdp-targeted-constructor.v1",
        "source_sha":PIN,
        "license":"Apache-2.0",
        "original_source_git_sha_verified":custody["clean"],
        "original_source_blobs":custody["checked_original_blobs"],
        "pinned_python_dependencies":deps,
        **runtime,
        "source_first_use":False,
        "training_or_learning_run":False,
        "native_yggdrasil_modified":False,
        "scientific_pass":False
    }
    report["receipt_sha256"]=sha256(_json(report)).hexdigest()
    return report


def main():
    args=argparse.ArgumentParser()
    args.add_argument("--checkout",required=True)
    args.add_argument("--output-json",required=True)
    cfg=args.parse_args()
    receipt=probe_exact_original_constructor(cfg.checkout)
    path=Path(cfg.output_json)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",
                    encoding="utf-8")
    print("FKP25_ORIGINAL_TARGETED_CONSTRUCTOR="+json.dumps({
        k:receipt[k] for k in (
          "schema","source_sha","constructor_created","package_import_mode",
          "pinned_python_dependencies","reset_invocations","do_invocations",
          "external_physical_actions","world_seeds_consumed","receipt_sha256",
          "source_first_use","scientific_pass")},sort_keys=True,separators=(",",":")))


if __name__=="__main__":
    main()

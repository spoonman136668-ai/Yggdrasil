#!/usr/bin/env python3
"""Load only unmodified ORIGINAL causal_gym.core and envs.mdp.

Never executes the upstream eager optional-environment __init__ modules.
No dummy SCM/PCH class or rewritten environment and no source reset/step here.
"""
import importlib
import inspect
from pathlib import Path
import sys
import types

def original_mdp_classes(upstream):
    root=Path(upstream).resolve()/"causal_gym"
    if "causal_gym" in sys.modules:
        raise RuntimeError("SOURCE_IMPORT_ALREADY_OCCUPIED")
    if not (root/"core"/"__init__.py").is_file() or not (root/"envs"/"mdp.py").is_file():
        raise RuntimeError("ORIGINAL_MDP_MISSING")
    base=types.ModuleType("causal_gym")
    base.__path__=[str(root)]
    base.__package__="causal_gym"
    sys.modules["causal_gym"]=base
    core=importlib.import_module("causal_gym.core")
    for cls,filename in ((core.SCM,"scm.py"),(core.PCH,"pch.py")):
        if Path(inspect.getfile(cls)).resolve()!=root/"core"/filename:
            raise RuntimeError("CORE_SOURCE_IDENTITY_MISMATCH")
    base.SCM=core.SCM
    base.PCH=core.PCH
    envs=types.ModuleType("causal_gym.envs")
    envs.__package__="causal_gym.envs"
    envs.__path__=[str(root/"envs")]
    sys.modules["causal_gym.envs"]=envs
    base.envs=envs
    mdp=importlib.import_module("causal_gym.envs.mdp")
    for cls in (mdp.MDPSCM, mdp.MDPPCH):
        if Path(inspect.getfile(cls)).resolve()!=root/"envs"/"mdp.py":
            raise RuntimeError("MDP_NOT_SOURCE_OWNED")
    if not issubclass(mdp.MDPSCM,core.SCM) or not issubclass(mdp.MDPPCH,core.PCH):
        raise RuntimeError("MDP_CLASS_ANCESTRY_INVALID")
    if "causal_gym.envs.mnist" in sys.modules or "causal_gym.envs.dtr" in sys.modules:
        raise RuntimeError("UNRELATED_ENV_IMPORT")
    return mdp.MDPSCM,mdp.MDPPCH

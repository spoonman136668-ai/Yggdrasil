#!/usr/bin/env python3
"""Source-faithful *isolated import* of ORIGINAL Causal-Gym DTR (not canonical package import).

This file creates only namespace shells for two package directories. It executes
the genuine unmodified upstream causal_gym.core and envs.dtr Python modules;
there are no replacement SCM/PCH classes, models, episodes, reset or step calls.
"""
from __future__ import annotations
import argparse
import importlib
import inspect
import json
import pathlib
import sys
import types

def original_dtr_classes(source: pathlib.Path):
    root = source.resolve() / "causal_gym"
    if "causal_gym" in sys.modules:
        raise RuntimeError("CAUSAL_GYM_ALREADY_IMPORTED_FAIL_CLOSED")
    if not (root / "core" / "__init__.py").is_file() or not (root / "envs" / "dtr.py").is_file():
        raise RuntimeError("ORIGINAL_DTR_SOURCE_NOT_FOUND")

    # Namespace packages only. Bypass unrelated eager envs/__init__.py, but
    # load and execute the original causal_gym/core/__init__.py in full.
    package = types.ModuleType("causal_gym")
    package.__package__ = "causal_gym"
    package.__path__ = [str(root)]
    sys.modules["causal_gym"] = package
    core = importlib.import_module("causal_gym.core")
    if pathlib.Path(inspect.getfile(core.SCM)).resolve() != root / "core" / "scm.py":
        raise RuntimeError("SCM_NOT_ORIGINAL_SOURCE")
    if pathlib.Path(inspect.getfile(core.PCH)).resolve() != root / "core" / "pch.py":
        raise RuntimeError("PCH_NOT_ORIGINAL_SOURCE")
    package.SCM = core.SCM
    package.PCH = core.PCH

    env_pkg = types.ModuleType("causal_gym.envs")
    env_pkg.__package__ = "causal_gym.envs"
    env_pkg.__path__ = [str(root / "envs")]
    sys.modules["causal_gym.envs"] = env_pkg
    package.envs = env_pkg
    dtr = importlib.import_module("causal_gym.envs.dtr")
    if pathlib.Path(inspect.getfile(dtr.DTRSCM)).resolve() != root / "envs" / "dtr.py":
        raise RuntimeError("DTRSCM_NOT_ORIGINAL_SOURCE")
    if pathlib.Path(inspect.getfile(dtr.DTRPCH)).resolve() != root / "envs" / "dtr.py":
        raise RuntimeError("DTRPCH_NOT_ORIGINAL_SOURCE")
    if not issubclass(dtr.DTRSCM, core.SCM) or not issubclass(dtr.DTRPCH, core.PCH):
        raise RuntimeError("ORIGINAL_CLASS_INHERITANCE_MISMATCH")
    if "causal_gym.envs.windy_minigrid" in sys.modules or "causal_gym.envs.mnist" in sys.modules:
        raise RuntimeError("UNRELATED_OPTIONAL_ENV_IMPORTED")
    if hasattr(package, "__file__") or hasattr(env_pkg, "__file__"):
        raise RuntimeError("NAMESPACE_SHOULD_NOT_EXECUTE_PACKAGE_INIT")
    return dtr.DTRSCM, dtr.DTRPCH, core

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    args = ap.parse_args()
    source = pathlib.Path(args.upstream).resolve()
    dtr, pch, core = original_dtr_classes(source)
    assert callable(dtr.reset) and callable(dtr.step)
    print(json.dumps({
        "disposition": "ORIGINAL_DTR_ISOLATED_SOURCE_IMPORT_PASS",
        "mode": "ISOLATED_ORIGINAL_MODULES_NOT_CANONICAL_PACKAGE_IMPORT",
        "original_dtr_file": str(pathlib.Path(inspect.getfile(dtr)).resolve().relative_to(source)),
        "original_pch_file": str(pathlib.Path(inspect.getfile(pch)).resolve().relative_to(source)),
        "original_scm_file": str(pathlib.Path(inspect.getfile(core.SCM)).resolve().relative_to(source)),
        "original_episodes_generated": 0,
        "model_fit_updates": 0,
        "first_use": False,
        "canonical_package_import_claim": False
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

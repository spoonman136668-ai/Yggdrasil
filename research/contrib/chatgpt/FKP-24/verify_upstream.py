"""FKP-24 read-only upstream source provenance fence.

No download, clone, import, source step, or source-world first use happens
here. Only inspect a previously independently authorized local Git checkout.
Never accept an origin URL or public branch name as a substitute for SHA
and Git blob custody. Never modify a dirty user checkout.
"""
from __future__ import annotations

from pathlib import Path
import subprocess

PIN="c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
REQUIRED={
    "LICENSE":"993e3a4922f003dced0fd061735697c850ea7205",
    "causal_gym/envs/mdp.py":"6264ec5450754c009e98c3e85f6d5927ece0a9ab",
    "causal_gym/core/pch.py":"ff37780c6b791877c70583b8d5f699be7fcd8817",
    "causal_gym/core/task.py":"668262f3f5c88fa2865b08ef10bbf96b09a3b73e",
    "causal_gym/core/scm.py":"f66f2638c797cfeaf0e96d4e13c06d4fabc2c8d5",
    "causal_gym/envs/__init__.py":"a36a43e2ccbca2c924db6b2852c70b5635bca181",
    "causal_gym/__init__.py":"6f8129d2caa303ee9fe87ff18fdbdfa153d8a53f",
    "setup.py":"31097c35f908e393bfd4763a298c1d5f4ab60600"
}


def inspect_exact_checkout(path,*,runner=subprocess.run):
    root=Path(path).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("FKP24_NOT_A_SOURCE_CHECKOUT")
    def git(*args):
        result=runner(["git","-C",str(root),*args],check=True,
                      capture_output=True,text=True)
        return result.stdout.strip()
    if git("rev-parse","HEAD")!=PIN:
        raise ValueError("FKP24_UPSTREAM_COMMIT_DRIFT")
    if git("status","--porcelain","--untracked-files=all"):
        raise ValueError("FKP24_UPSTREAM_SOURCE_DIRTY")
    for p,sha in REQUIRED.items():
        if git("rev-parse","HEAD:"+p)!=sha:
            raise ValueError("FKP24_UPSTREAM_BLOB_CHANGED:"+p)
    return {"schema":"fkp24.upstream-causal-source-custody.v1",
            "upstream":"CausalAILab/Causal-Gymnasium",
            "commit":PIN,
            "blobs":dict(sorted(REQUIRED.items())),
            "clean":True,
            "actual_env_executed":False}


if __name__=="__main__":
    import argparse
    import json
    args=argparse.ArgumentParser(description="Read-only exact upstream source custody")
    args.add_argument("--checkout",required=True)
    x=args.parse_args()
    receipt=inspect_exact_checkout(x.checkout)
    print("FKP24_READONLY_EXTERNAL_GIT_CUSTODY="+json.dumps(receipt,
          sort_keys=True,separators=(",",":")))

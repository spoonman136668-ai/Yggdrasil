#!/usr/bin/env python3
"""Read-only original-upstream package preflight; never generates an episode."""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

PIN = "c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
BLOBS = {
    "LICENSE": "993e3a4922f003dced0fd061735697c850ea7205",
    "setup.py": "31097c35f908e393bfd4763a298c1d5f4ab60600",
    "causal_gym/__init__.py": "6f8129d2caa303ee9fe87ff18fdbdfa153d8a53f",
    "causal_gym/envs/__init__.py": "a36a43e2ccbca2c924db6b2852c70b5635bca181",
    "causal_gym/envs/dtr.py": "6af2371dce21804140ea141ccb7be14e003ba275",
    "causal_gym/core/pch.py": "ff37780c6b791877c70583b8d5f699be7fcd8817",
}
def command(args: list[str], cwd: pathlib.Path | None = None, timeout: int = 35) -> dict:
    try:
        p = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=False)
        return {"exit": p.returncode, "stdout": p.stdout[-2400:], "stderr": p.stderr[-2400:]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exit": 125, "stdout": "", "stderr": str(exc)}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--pip-exit", type=int, required=True)
    args = ap.parse_args()
    upstream = pathlib.Path(args.upstream).resolve()
    data = {
        "schema": "mass.original-dtr.package-preflight.v1",
        "source_repo": "CausalAILab/Causal-Gymnasium",
        "expected_source_sha": PIN,
        "required_git_blobs": BLOBS,
        "pip_install_exit": args.pip_exit,
        "original_episodes_generated": 0,
        "model_fit_updates": 0,
        "dev_or_heldout_consumed": 0,
        "scientific_first_use": False,
        "controller_dispatch": False,
        "native_r10_protocol_modified": False,
        "controls": {},
    }
    rev = command(["git", "rev-parse", "HEAD"], upstream)
    data["controls"]["source_head"] = rev
    ok = rev["exit"] == 0 and rev["stdout"].strip() == PIN
    for path, expected in BLOBS.items():
        resp = command(["git", "hash-object", "--", path], upstream)
        data["controls"]["blob:" + path] = resp
        ok &= (resp["exit"] == 0 and resp["stdout"].strip() == expected)
    clean = command(["git", "diff", "--exit-code", "--", "setup.py", "causal_gym"], upstream)
    data["controls"]["tracked_source_diff"] = clean
    ok &= clean["exit"] == 0
    compile_check = command([sys.executable, "-B", "-c",
        "import ast, pathlib, sys; root=pathlib.Path(sys.argv[1]);"
        "ast.parse((root/'causal_gym/envs/dtr.py').read_text());"
        "ast.parse((root/'causal_gym/core/pch.py').read_text());"
        "print('ORIGINAL_SOURCE_AST_PASS')", str(upstream)])
    data["controls"]["syntax"] = compile_check
    ok &= compile_check["exit"] == 0
    # Import the original installed package, not a rewritten module or stub.
    import_check = command([sys.executable, "-B", "-c",
        "import inspect, causal_gym;"
        "from causal_gym.envs.dtr import DTRSCM,DTRPCH;"
        "assert inspect.isclass(DTRSCM) and inspect.isclass(DTRPCH);"
        "assert callable(DTRSCM.reset) and callable(DTRSCM.step);"
        "print('ORIGINAL_DTR_IMPORT_PASS_NO_RESET_OR_STEP')"], timeout=45)
    data["controls"]["upstream_package_import"] = import_check
    ok &= (args.pip_exit == 0 and import_check["exit"] == 0)
    data["disposition"] = "ORIGINAL_DTR_PACKAGE_PREFLIGHT_PASS" if ok else "ORIGINAL_DTR_PACKAGE_PREFLIGHT_NO_GO"
    receipt = pathlib.Path(args.receipt)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")
    print(data["disposition"])
    print("ORIGINAL_EPISODES_GENERATED=0")
    return 0 if ok else 2

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Pinned, zero-interaction CausalMBRL chemistry import preflight."""
from __future__ import annotations
import argparse, ast, hashlib, importlib, importlib.metadata as metadata
import json, os, shutil, subprocess, sys, tempfile, urllib.request
from pathlib import Path

EXPERIMENT = "WSCM-CAUSALMBRL-IMPORT-01-R2"
REPO = "dido1998/CausalMBRL"
COMMIT = "2c595988b06b3d568fdde53213029e97841acb03"
ROOT_URL = f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/"
FILES = {
    "LICENSE": "cff393fe08ddf5fdd6fa4b8f509df9789bf54900",
    "envs/__init__.py": "cbc2249a3893cf821aaf55464ec72871fe51569f",
    "envs/chemistry_env_rl.py": "58af54d7e7e30f8abe059df3d68565845a5b2c51",
    "cswm/utils.py": "0957887f49293195ebdc76f68ca6be3bc1a110da",
    "cswm/models/__init__.py": "2a7cfd6149cf5f8a1b180e62008fa7fefc0f8001",
    "cswm/models/losses.py": "fa7edc79220e05eec641df1928f13e8364d1abf8",
}
PACKAGES = [
    "numpy==1.26.4", "torch==2.5.1+cpu", "torchvision==0.20.1+cpu",
    "gym==0.26.2", "matplotlib==3.9.4", "Pillow==11.0.0",
    "scikit-image==0.24.0", "h5py==3.12.1", "tqdm==4.67.1",
]
PACKAGE_VERSIONS = {
    "numpy": "1.26.4", "torch": "2.5.1+cpu", "torchvision": "0.20.1+cpu",
    "gym": "0.26.2", "matplotlib": "3.9.4", "Pillow": "11.0.0",
    "scikit-image": "0.24.0", "h5py": "3.12.1", "tqdm": "4.67.1",
}
def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
def method_source(tree, source_text, name):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_source_segment(source_text, node) or ""
    return ""
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out = Path(ap.parse_args().out)
    tmp = Path(os.environ.get("RUNNER_TEMP", tempfile.gettempdir()))
    package_target = tmp / "wscm-causalgym-import02-packages"
    pip_cache = tmp / "wscm-causalgym-import02-pip-cache"
    source_root = Path(tempfile.mkdtemp(prefix="causalmbrl-import01-", dir=str(tmp)))
    source_errors = []
    source_verified = 0
    dependency_status = "NOT_ATTEMPTED"
    import_status = "NOT_ATTEMPTED"
    class_import_pass = False
    versions = {}
    leakage = {}
    signatures = {}
    try:
        for rel, expected in FILES.items():
            try:
                with urllib.request.urlopen(ROOT_URL + rel, timeout=45) as response:
                    data = response.read()
                actual = git_blob(data)
                if actual != expected:
                    source_errors.append(rel + ":BLOB_MISMATCH")
                    continue
                dest = source_root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
                source_verified += 1
            except Exception as exc:
                source_errors.append(rel + ":" + type(exc).__name__)
        if source_errors or source_verified != len(FILES):
            dependency_status = "SKIPPED_SOURCE_PIN_FAILURE"
            import_status = "SKIPPED_SOURCE_PIN_FAILURE"
            status = "SOURCE_BLOB_VERIFICATION_BLOCKED"
        else:
            marker = package_target / ".wscm-causalmbrl-import01-ready"
            if marker.exists():
                dependency_status = "PINNED_JOB_SCOPED_DEPENDENCIES_AVAILABLE"
            else:
                package_target.mkdir(parents=True, exist_ok=True)
                env = os.environ.copy()
                env["PIP_CACHE_DIR"] = str(pip_cache)
                env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
                env["PYTHONDONTWRITEBYTECODE"] = "1"
                command = [
                    sys.executable, "-m", "pip", "install",
                    "--disable-pip-version-check", "--no-warn-script-location",
                    "--target", str(package_target),
                    "--index-url", "https://pypi.org/simple",
                    "--extra-index-url", "https://download.pytorch.org/whl/cpu",
                    *PACKAGES,
                ]
                proc = subprocess.run(command, capture_output=True, text=True, env=env)
                if proc.returncode != 0:
                    dependency_status = "PIP_FAILED_EXIT_" + str(proc.returncode)
                    status = "DEPENDENCY_INSTALL_BLOCKED"
                    print("DEPENDENCY_INSTALL_DIAGNOSTIC=" + (proc.stderr or proc.stdout)[-2500:])
                else:
                    (package_target / ".wscm-causalmbrl-import01-ready").write_text("ready\n", encoding="ascii")
                    dependency_status = "PINNED_JOB_SCOPED_DEPENDENCIES_AVAILABLE"
                shutil.rmtree(pip_cache, ignore_errors=True)
            if dependency_status not in ("PIP_FAILED_EXIT_1",) and not dependency_status.startswith("PIP_FAILED_EXIT_"):
                sys.path.insert(0, str(package_target))
                try:
                    versions = {name: metadata.version(name) for name in PACKAGE_VERSIONS}
                    if versions != PACKAGE_VERSIONS:
                        raise RuntimeError("PINNED_DISTRIBUTION_VERSION_MISMATCH")
                    sys.path.insert(0, str(source_root))
                    os.environ["MPLBACKEND"] = "Agg"
                    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
                    module = importlib.import_module("envs.chemistry_env_rl")
                    cls = getattr(module, "ColorChangingRL")
                    import gym
                    if not issubclass(cls, gym.Env):
                        raise RuntimeError("ORIGINAL_CLASS_NOT_GYM_ENV")
                    signatures = {
                        "constructor": str(__import__("inspect").signature(cls.__init__)),
                        "reset": str(__import__("inspect").signature(cls.reset)),
                        "step": str(__import__("inspect").signature(cls.step)),
                    }
                    source_text = (source_root / "envs/chemistry_env_rl.py").read_text(encoding="utf-8")
                    tree = ast.parse(source_text)
                    reset_src = method_source(tree, source_text, "reset")
                    render_src = method_source(tree, source_text, "render")
                    get_state_src = method_source(tree, source_text, "get_state")
                    save_src = method_source(tree, source_text, "get_save_information")
                    step_src = method_source(tree, source_text, "step")
                    seed_src = method_source(tree, source_text, "seed")
                    leakage = {
                        "reset_returns_target_state": "state_target" in reset_src and "observations_target" in reset_src,
                        "render_combines_target": "render_grid_target" in render_src or "render_circles_target" in render_src or "render_shapes_target" in render_src,
                        "get_state_returns_target_tensor": "im_target" in get_state_src,
                        "save_api_exposes_graph_or_weights": "adjacency_matrix" in save_src and "state_dict" in save_src,
                        "step_initializes_done_false": "done = False" in step_src,
                        "step_checks_max_steps": "self.cur_step >= self.max_steps" in step_src,
                        "seed_method_uses_gym_seed_only": "seeding.np_random" in seed_src and "np.random.seed" not in seed_src and "random.seed" not in seed_src and "torch.manual_seed" not in seed_src,
                    }
                    class_import_pass = True
                    import_status = "EXACT_UPSTREAM_COLORCHANGINGRL_IMPORTED_NO_INSTANCE_CREATED"
                    status = "SOURCE_IMPORT_PASS"
                except Exception as exc:
                    import_status = "CLASS_IMPORT_FAILED_" + type(exc).__name__
                    status = "CLASS_IMPORT_BLOCKED"
    finally:
        shutil.rmtree(source_root, ignore_errors=True)
        shutil.rmtree(pip_cache, ignore_errors=True)
    result = {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "status": status,
        "metrics": {
            "source_repository": REPO, "source_commit": COMMIT,
            "source_files_expected": len(FILES), "source_files_git_blob_verified": source_verified,
            "source_blob_errors": source_errors,
            "dependency_install_status": dependency_status,
            "dependency_target": "RUNNER_TEMP; parent workflow removes after both duplicate runs",
            "dependency_versions": versions,
            "import_status": import_status, "class_import_pass": class_import_pass,
            "python_version": sys.version.split()[0], "class_signatures": signatures,
            "source_boundary_findings": leakage,
            "environment_instances_created": 0, "source_reset_calls": 0,
            "source_step_calls": 0, "source_interventions": 0, "model_fits": 0,
            "persistent_runner_changes": 0,
        },
        "source_first_use": False,
        "scientific_gain_verified": False,
        "scientific_pass": False,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print("WSCM_CAUSALMBRL_STATUS=" + status)
    print("WSCM_CAUSALMBRL_SOURCE_BLOBS=" + str(source_verified) + "/" + str(len(FILES)))
    print("WSCM_CAUSALMBRL_IMPORT=" + import_status)
    print("WSCM_CAUSALMBRL_WORLD_ACTIONS=0")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())

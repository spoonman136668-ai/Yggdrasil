#!/usr/bin/env python3
"""Source-free contract gate: pinned DTR API import + exact native fixture mapping.

Never constructs DTRSCM/DTRPCH and never calls reset/see/do/ctf_do/step.
Only synthetic binary episodes are admitted to NativeEpisodeExperience.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import importlib.util
import inspect
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import types
import urllib.request
from pathlib import Path

EXPERIMENT = "WSCM-DTR-NATIVE-CONTRACT-01"
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
PINNED = {
    "numpy": "1.26.4",
    "gymnasium": "0.29.1",
    "networkx": "3.4.2",
    "toposort": "1.10",
    "pydash": "8.0.5",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def download_pinned_files(root: Path) -> int:
    verified = 0
    for relative_path, expected in SOURCE_BLOBS.items():
        request = urllib.request.Request(
            RAW_ROOT + relative_path,
            headers={"User-Agent": "Yggdrasil-WSCM-DTR-contract/1"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read(8 * 1024 * 1024 + 1)
        require(len(payload) <= 8 * 1024 * 1024, "SOURCE_FILE_TOO_LARGE")
        require(git_blob_sha(payload) == expected, f"SOURCE_BLOB_MISMATCH:{relative_path}")
        destination = root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        verified += 1
    require(verified == len(SOURCE_BLOBS), "SOURCE_BLOB_COUNT_MISMATCH")
    return verified


def ensure_ephemeral_dependencies(target: Path) -> dict[str, str]:
    target.parent.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(target))
    importlib.invalidate_caches()
    try:
        versions = {name: importlib.metadata.version(name) for name in PINNED}
        if versions == PINNED:
            return versions
    except importlib.metadata.PackageNotFoundError:
        pass

    try:
        sys.path.remove(str(target))
    except ValueError:
        pass
    if target.exists():
        shutil.rmtree(target)

    command = [
        sys.executable, "-m", "pip", "install",
        "--disable-pip-version-check", "--no-input",
        "--only-binary=:all:", "--target", str(target), "--upgrade",
    ] + [f"{name}=={version}" for name, version in PINNED.items()]
    completed = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False, timeout=900,
    )
    require(completed.returncode == 0, f"PINNED_PIP_INSTALL_FAILED:{completed.returncode}")
    sys.path.insert(0, str(target))
    importlib.invalidate_caches()
    versions = {name: importlib.metadata.version(name) for name in PINNED}
    require(versions == PINNED, "PINNED_DEPENDENCY_VERSION_MISMATCH")
    return versions


def import_exact_dtr_modules(root: Path):
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

    task = importlib.import_module("causal_gym.core.task")
    scm = importlib.import_module("causal_gym.core.scm")
    pch = importlib.import_module("causal_gym.core.pch")
    graph = importlib.import_module("causal_gym.core.graph")
    for name in (
        "ObsType", "ActType", "PolicyType",
        "WrapperObsType", "WrapperActType", "WrapperPolicyType",
    ):
        module = importlib.import_module("causal_gym.core.types")
        setattr(core, name, getattr(module, name))
    core.Task = task.Task
    core.SCM = scm.SCM
    core.PCH = pch.PCH
    core.Graph = graph.Graph
    package.SCM = scm.SCM
    package.PCH = pch.PCH

    dtr = importlib.import_module("causal_gym.envs.dtr")
    require(dtr.DTRSCM.__module__ == "causal_gym.envs.dtr", "DTRSCM_MODULE_IDENTITY")
    require(dtr.DTRPCH.__module__ == "causal_gym.envs.dtr", "DTRPCH_MODULE_IDENTITY")
    return dtr, pch.PCH, task.Task, task.LearningRegime, task.Assumptions


def verify_upstream_contract(dtr, pch_class, task_class, learning_regime, assumptions) -> None:
    # Class import and introspection only; no instance is constructed.
    constructor = inspect.signature(dtr.DTRPCH)
    require(tuple(constructor.parameters) == ("a1", "a2"), "DTRPCH_CONSTRUCTOR_CHANGED")
    require("task" not in constructor.parameters, "UNEXPECTED_TASK_CONSTRUCTOR_PARAMETER")

    default_task = task_class()
    require(default_task.learning_regime == learning_regime.ctf_do,
            "TASK_DEFAULT_NOT_CTF_DO")

    do_only = task_class(
        learning_regime=learning_regime.do,
        assumptions=assumptions.dag,
    )

    class PermissionSubject:
        task = do_only

    # Exercise the original PCH permission method on a minimal subject, not a DTR instance.
    pch_class._permission_check(PermissionSubject(), "do")
    for forbidden_method in ("see", "ctf_do", "step"):
        try:
            pch_class._permission_check(PermissionSubject(), forbidden_method)
        except PermissionError:
            pass
        else:
            raise RuntimeError(f"DO_ONLY_PERMISSION_DID_NOT_DENY:{forbidden_method}")

    do_source = inspect.getsource(dtr.DTRPCH.do)
    see_source = inspect.getsource(dtr.DTRPCH.see)
    dtr_step_source = inspect.getsource(dtr.DTRSCM.step)
    dtr_init_source = inspect.getsource(dtr.DTRPCH.__init__)

    require("self.env.s1" in do_source, "DO_CALLBACK_MISSING_S1")
    require("self.env.x1" in do_source and "self.env.s2" in do_source,
            "DO_CALLBACK_MISSING_STAGE1_HISTORY")
    require("self.env.u" not in do_source, "DO_CALLBACK_EXPOSES_U")
    require("self.env.u" in see_source, "SEE_U_EXPOSURE_NOT_DETECTED")
    require("super().__init__()" in dtr_init_source, "DTRPCH_INIT_PARENT_CALL_CHANGED")
    require('"s1": self.s1' in dtr_step_source, "INFO_S1_FIELD_NOT_FOUND")
    require('"x1": self.x1' in dtr_step_source, "INFO_X1_FIELD_NOT_FOUND")
    require('"s2": self.s2' in dtr_step_source, "INFO_S2_FIELD_NOT_FOUND")
    require('"y": self.y' in dtr_step_source, "INFO_TERMINAL_Y_FIELD_NOT_FOUND")
    # Deliberately do not read, pass, or train on the upstream info dictionary.


def run_native_fixture_contract(repo_root: Path) -> dict[str, object]:
    sys.path.insert(0, str(repo_root))
    from yggdrasil.native_context_basis import digest
    from yggdrasil.native_episode_experience import NativeEpisodeExperience

    learner = NativeEpisodeExperience()
    events = []
    for index in range(32):
        s1 = index % 2
        x1 = (index // 2) % 2
        s2 = (index // 4) % 2
        x2 = (index // 8) % 2
        y = s1 ^ x1 ^ s2 ^ x2
        event_id = f"{index + 1:064x}"
        # Stable S1 in coordinate 0; coordinate 1 is a public stage marker.
        views = ((s1, 0), (s1, 1))
        row = {"s1": s1, "x1": x1, "s2": s2, "x2": x2, "y": y}
        learner = learner.observe(event_id, views, row)
        events.append((event_id, views, row))

    native_info = learner.info()
    require(native_info["count"] == 32, "NATIVE_EVENT_COUNT")
    require(native_info["projection"] == 0, "NATIVE_PROJECTION_NOT_STABLE_S1")

    stage0_proposals = [learner.propose((state, 0)) for state in (0, 1)]
    stage1_proposals = [
        learner.propose((state, 1), first=1, next_state=1)
        for state in (0, 1)
    ]
    require(all(type(value) is int and value in (0, 1)
                for value in stage0_proposals + stage1_proposals),
            "NATIVE_PROPOSAL_NOT_BINARY")

    forecasts = [
        learner.forecast((state, 1), first, next_state, second)
        for state in (0, 1)
        for first in (0, 1)
        for next_state in (0, 1)
        for second in (0, 1)
    ]
    raw = learner.checkpoint()
    restored = NativeEpisodeExperience.restore(raw, digest(raw))
    require(restored.checkpoint() == raw, "NATIVE_COLD_CHECKPOINT_MISMATCH")
    restored_forecasts = [
        restored.forecast((state, 1), first, next_state, second)
        for state in (0, 1)
        for first in (0, 1)
        for next_state in (0, 1)
        for second in (0, 1)
    ]
    require(restored_forecasts == forecasts, "NATIVE_COLD_FORECAST_MISMATCH")
    require(
        [restored.propose((state, 0)) for state in (0, 1)] == stage0_proposals,
        "NATIVE_COLD_STAGE0_PROPOSAL_MISMATCH",
    )
    require(
        [restored.propose((state, 1), first=1, next_state=1)
         for state in (0, 1)] == stage1_proposals,
        "NATIVE_COLD_STAGE1_PROPOSAL_MISMATCH",
    )

    # Exact duplicate is idempotent; conflicting reuse and malformed rows fail closed.
    last_id, last_views, last_row = events[-1]
    require(learner.observe(last_id, last_views, last_row) is learner,
            "NATIVE_EXACT_DUPLICATE_NOT_IDEMPOTENT")
    before_invalid = learner.checkpoint()
    rejected = 0
    invalid_cases = []

    missing = dict(last_row)
    missing.pop("y")
    invalid_cases.append((f"{'f' * 64}", last_views, missing))
    extra = dict(last_row)
    extra["info"] = {"y": 0}
    invalid_cases.append((f"{'e' * 64}", last_views, extra))
    boolean = dict(last_row)
    boolean["s2"] = True
    invalid_cases.append((f"{'d' * 64}", last_views, boolean))
    invalid_cases.append((f"{'c' * 64}", ((last_views[0][0], 0),), last_row))

    for identifier, views, row in invalid_cases:
        try:
            learner.observe(identifier, views, row)
        except (TypeError, ValueError):
            rejected += 1
        else:
            raise RuntimeError("NATIVE_INVALID_EVENT_ACCEPTED")
    conflicting = dict(last_row)
    conflicting["y"] = 1 - last_row["y"]
    try:
        learner.observe(last_id, last_views, conflicting)
    except (TypeError, ValueError):
        rejected += 1
    else:
        raise RuntimeError("NATIVE_CONFLICTING_REPLAY_ACCEPTED")
    require(rejected == 5, "NATIVE_NEGATIVE_COUNT")
    require(learner.checkpoint() == before_invalid,
            "NATIVE_INVALID_INPUT_MUTATED_STATE")

    return {
        "synthetic_events": 32,
        "learned_projection_coordinate": native_info["projection"],
        "expected_projection_coordinate": 0,
        "stage0_binary_proposals": stage0_proposals,
        "stage1_binary_proposals": stage1_proposals,
        "forecast_combinations_checked": len(forecasts),
        "cold_checkpoint_roundtrip": True,
        "cold_forecast_and_proposal_parity": True,
        "exact_duplicate_idempotent": True,
        "invalid_and_conflicting_events_rejected": rejected,
        "invalid_input_state_unchanged": True,
        "checkpoint_bytes": len(raw),
        "scientific_gain_verified": False,
    }


def run() -> dict[str, object]:
    runner_temp = Path(os.environ.get("RUNNER_TEMP", tempfile.gettempdir()))
    dependency_target = runner_temp / "wscm-causalgym-import02-packages"
    with tempfile.TemporaryDirectory(prefix="wscm-dtr-contract-source-") as source_dir:
        upstream_root = Path(source_dir)
        blob_count = download_pinned_files(upstream_root)
        versions = ensure_ephemeral_dependencies(dependency_target)
        dtr, pch_class, task_class, learning_regime, assumptions = \
            import_exact_dtr_modules(upstream_root)
        verify_upstream_contract(dtr, pch_class, task_class, learning_regime, assumptions)

    repo_root = Path(__file__).resolve().parents[3]
    native = run_native_fixture_contract(repo_root)
    return {
        "schema": "yggdrasil.research-scientific-result.v1",
        "experiment": EXPERIMENT,
        "status": "SOURCE_FREE_ADAPTER_CONTRACT_PASS",
        "metrics": {
            "upstream_repository": SOURCE_REPO,
            "upstream_commit": SOURCE_COMMIT,
            "source_file_count_expected": len(SOURCE_BLOBS),
            "source_file_count_git_blob_verified": blob_count,
            "exact_dtrscm_and_dtrpch_class_imports": True,
            "dtr_objects_constructed": 0,
            "default_task_regime": "ctf_do",
            "do_only_permission_allows_do": True,
            "do_only_permission_denies_see_ctf_do_step": True,
            "do_callback_uses_public_state_history_not_u": True,
            "see_callback_hidden_u_detected_and_forbidden": True,
            "raw_info_dictionary_used_by_adapter": False,
            "pinned_dependencies": versions,
            "native_contract": native,
            "source_reset_calls": 0,
            "source_see_calls": 0,
            "source_do_calls": 0,
            "source_step_calls": 0,
            "source_interventions": 0,
            "original_source_model_fits": 0,
            "persistent_runner_changes": 0,
        },
        "scientific_pass": False,
        "scientific_gain_verified": False,
        "source_first_use": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run()
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

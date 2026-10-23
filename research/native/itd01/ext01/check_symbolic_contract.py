"""Source-only DeepMind Alchemy native interface gate. Never imports/runs benchmark."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess

UPSTREAM_SHA = "68a26254b5c0f15e84fa0c15d66bf0c626ede8e0"
FILES = {
    "dm_alchemy/symbolic_alchemy.py": "e9485856726462f0c4a9aa2501e14ebedb5e4122",
    "dm_alchemy/symbolic_alchemy_test.py": "2c044c997429b33646c6525f0a79323f645ade74",
    "docs/index.md": "77f540812c7bc63b7d01b62d9cbd81e61587d70f",
    "setup.py": "a99fdd6f4134fb8c9074cc6c1d91bb18f1ca8365",
    "dm_alchemy/types/graphs.py": "29e058dbecb54a3d38d276de12d320d3cb6b5fec",
}
REQUIRED_METHODS = (
    "__init__", "reset", "step", "step_slot_based_action",
    "observation", "observation_spec", "action_spec",
)


def require(value: bool, reason: str) -> None:
    if not value:
        raise ValueError("EXT01_SOURCE_CONTRACT_FAIL_CLOSED: " + reason)


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def git(upstream: Path, *args: str) -> str:
    p = subprocess.run(("git", "-C", str(upstream), *args),
                       capture_output=True, text=True, check=False)
    require(p.returncode == 0, "upstream git ref unavailable")
    return p.stdout.strip()


def inspect_symbolic_ast(raw: bytes) -> dict:
    tree = ast.parse(raw.decode("utf-8-sig"), filename="symbolic_alchemy.py")
    consts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    consts[target.id] = node.value.value
    require(consts.get("MAX_STONES") == 3, "original stone-slot limit changed")
    require(consts.get("MAX_POTIONS") == 12, "original potion-slot limit changed")
    require(consts.get("DEFAULT_MAX_STEPS_PER_TRIAL") == 20,
            "upstream trial-step limit changed")
    klass = next((n for n in tree.body
                  if isinstance(n, ast.ClassDef) and n.name == "SymbolicAlchemy"), None)
    require(klass is not None, "native symbolic environment missing")
    methods = {n.name: n for n in klass.body if isinstance(n, ast.FunctionDef)}
    require(all(k in methods for k in REQUIRED_METHODS),
            "source-native reset, step or observation contract missing")
    fn = methods["__init__"]
    args = fn.args.args
    defaults = dict(zip((a.arg for a in args[len(args) - len(fn.args.defaults):]),
                        fn.args.defaults))
    for param, expected in (("end_trial_action", False), ("observe_used", True),
                            ("generate_events", False), ("fix_obs_length", False),
                            ("see_chemistries", None)):
        expr = defaults.get(param)
        require(isinstance(expr, ast.Constant) and expr.value is expected,
                "original constructor default changed: " + param)
    require(isinstance(defaults.get("max_steps_per_trial"), ast.Name) and
            defaults["max_steps_per_trial"].id == "DEFAULT_MAX_STEPS_PER_TRIAL",
            "native maximum trial steps changed")
    observation = ast.unparse(methods["observation_spec"])
    action = ast.unparse(methods["action_spec"])
    step = ast.unparse(methods["step"])
    require("symbolic_obs" in observation and "obs_features" in observation,
            "source symbolic observation specification absent")
    for token in ("MAX_STONES", "MAX_POTIONS", "num_special_actions",
                  "BoundedArray", "num_actions - 1"):
        require(token in action, "source action bounds changed: " + token)
    require("step_slot_based_action" in step and "_int_to_slot_based_action" in step,
            "public integer step no longer routed to native slot action")
    require("reset_no_observation" in ast.unparse(methods["reset"]),
            "native episode reset no longer source-owned")
    require("return self._internal_step" in ast.unparse(methods["step_slot_based_action"]),
            "source slot actions no longer enter native transition")
    return {
        "class": klass.name,
        "native_stone_slots": consts["MAX_STONES"],
        "native_potion_slots": consts["MAX_POTIONS"],
        "source_default_trial_step_limit": consts["DEFAULT_MAX_STEPS_PER_TRIAL"],
        "integer_action_count_default_no_end_trial": 3 * (12 + 1) + 1,
        "integer_action_count_optional_end_trial": 3 * (12 + 1) + 2,
        "constructor_defaults_checked": ["end_trial_action", "observe_used",
                                         "generate_events", "fix_obs_length",
                                         "see_chemistries", "max_steps_per_trial"],
        "native_methods_verified": list(REQUIRED_METHODS),
    }


def inspect_graph_constraints(raw: bytes) -> dict:
    """Source-only constraint diversity check, NOT a nonisomorphism proof."""
    tree = ast.parse(raw.decode("utf-8-sig"), filename="graphs.py")
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    labels = ("no_bottleneck_constraints", "bottleneck1_constraints",
              "bottleneck2_constraints", "bottleneck3_constraints")
    signatures = {}
    for label in labels:
        require(label in functions, "original graph-constraint family missing: " + label)
        returns = [n for n in functions[label].body if isinstance(n, ast.Return)]
        require(len(returns) == 1, "graph family not literal: " + label)
        try:
            constraints = ast.literal_eval(returns[0].value)
        except (ValueError, TypeError, SyntaxError, MemoryError):
            require(False, "graph family not inspectable as a literal: " + label)
        require(isinstance(constraints, list) and len(constraints) == 1,
                "graph constraint distribution shape drift: " + label)
        matrix = constraints[0]
        require(len(matrix) == 3 and all(len(row) == 3 for row in matrix),
                "graph constraint axes drift: " + label)
        signatures[label] = sum(item not in ("X", "*")
                                 for row in matrix for item in row)
    require(signatures == {"no_bottleneck_constraints": 0,
                           "bottleneck1_constraints": 2,
                           "bottleneck2_constraints": 1,
                           "bottleneck3_constraints": 3},
            "source-level graph constraint classes drifted")
    for fname in ("graph_distr", "random_graph"):
        require(fname in functions, "upstream graph-distribution API missing: " + fname)
    require("get_num_constraints" in ast.unparse(functions["graph_distr"]),
            "graph class count no longer enters upstream distribution")
    return {
        "native_constraint_classes": signatures,
        "distinct_declared_constraint_counts": [0, 1, 2, 3],
        "nonisomorphic_graph_families_proven": False,
        "unseen_graph_family_birth_witnessed": False,
        "finite_episode_identifiability_proven": False,
        "graph_sampling_executed": False,
    }


def audit(upstream: Path) -> dict:
    require(git(upstream, "rev-parse", "HEAD") == UPSTREAM_SHA,
            "upstream source commit drift")
    observed = {}
    for path, blob in FILES.items():
        raw = (upstream / path).read_bytes()
        require(git_blob_sha(raw) == blob, "working-tree upstream blob drift: " + path)
        require(git(upstream, "rev-parse", "HEAD:" + path) == blob,
                "upstream commit blob identity drift: " + path)
        observed[path] = {"git_blob_sha": blob, "sha256": hashlib.sha256(raw).hexdigest(),
                          "bytes": len(raw)}
    contract = inspect_symbolic_ast(
        (upstream / "dm_alchemy/symbolic_alchemy.py").read_bytes())
    graph_contract = inspect_graph_constraints(
        (upstream / "dm_alchemy/types/graphs.py").read_bytes())
    doc = (upstream / "docs/index.md").read_text(encoding="utf-8")
    require("symbolic version" in doc.lower(), "source native symbolic documentation missing")
    require("stone" in doc.lower() and "potion" in doc.lower(),
            "real chemistry action documentation missing")
    return {
        "schema": "itd01.ext01.upstream-symbolic-interface-audit.v1",
        "external_repository": "google-deepmind/dm_alchemy",
        "exact_upstream_commit": UPSTREAM_SHA,
        "source_files": observed,
        "contract": contract,
        "graph_family_static_contract": graph_contract,
        "benchmark_installed_or_imported": False,
        "benchmark_reset_or_step_executed": False,
        "generated_episodes": 0,
        "learner_trained": False,
        "external_scientific_first_use": False,
        "source_role_custody_independently_witnessed": False,
        "actual_heldout_admitted": False,
        "ckb_controller_admission": "NOT_OBSERVED",
        "yggdrasil_r10_modified": False,
        "science_disposition": "SOURCE_CONTRACT_SCREEN_ONLY_NOT_ADMITTED",
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", type=Path, required=True)
    ap.add_argument("--audit", action="store_true", required=True)
    args = ap.parse_args()
    print(json.dumps(audit(args.upstream), indent=2, sort_keys=True))

"""Read-only EXT01 original Alchemy factory contract gate; no benchmark imports."""
import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path

COMMIT = "68a26254b5c0f15e84fa0c15d66bf0c626ede8e0"
FILE = "dm_alchemy/symbolic_alchemy.py"
BLOB = "e9485856726462f0c4a9aa2501e14ebedb5e4122"


def check(ok, why):
    if not ok:
        raise ValueError("EXT01_FACTORY_SOURCE_REJECT:" + why)


def original_bytes(upstream):
    root = Path(upstream)
    def git(*args):
        p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True, check=False)
        check(p.returncode == 0, "GIT_LOOKUP_FAILED")
        return p.stdout.strip()
    check(git("rev-parse", "HEAD") == COMMIT, "COMMIT_DRIFT")
    check(git("rev-parse", "HEAD:" + FILE) == BLOB, "COMMIT_BLOB_DRIFT")
    raw = (root / FILE).read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    check(actual == BLOB, "SOURCE_BLOB_DRIFT")
    return raw


def ast_function(nodes, name):
    matches = [n for n in nodes if isinstance(n, ast.FunctionDef) and n.name == name]
    check(len(matches) == 1, "EXPECTED_FUNCTION_" + name)
    return matches[0]


def defaults(fn):
    args = fn.args.posonlyargs + fn.args.args
    return {a.arg: n.value if isinstance(n, ast.Constant) else "<NONLITERAL>"
            for a, n in zip(args[-len(fn.args.defaults):], fn.args.defaults)}


def audit_source(raw):
    tree = ast.parse(raw.decode("utf-8-sig"))
    factory = ast_function(tree.body, "get_symbolic_alchemy_level")
    original = defaults(factory)
    required = {"observe_used": True, "end_trial_action": False,
                "num_trials": 10, "num_stones_per_trial": 3,
                "num_potions_per_trial": 12, "see_chemistries": None,
                "generate_events": False}
    for key, value in required.items():
        check(key in original and original[key] == value, "FACTORY_DEFAULT_" + key)
    expected = {
        "perceptual_mapping_randomized": (("random_stone_map", "random_potion_map"),
                                         ("all_fixed_stone_map", "all_fixed_potion_map")),
        "random_bottleneck": (("graph_distr(possible_constraints())",), ()),
        "rotation": (("random_rotation",), ("np.eye(3)",)),
    }
    for name, (yes, no) in expected.items():
        branches = [n for n in ast.walk(factory) if isinstance(n, ast.If) and
                    isinstance(n.test, ast.Compare) and len(n.test.ops) == 1 and
                    isinstance(n.test.ops[0], ast.In) and
                    isinstance(n.test.left, ast.Constant) and n.test.left.value == name and
                    len(n.test.comparators) == 1 and isinstance(n.test.comparators[0], ast.Name) and
                    n.test.comparators[0].id == "level_name"]
        check(len(branches) == 1, "SWITCH_" + name)
        then = ast.unparse(ast.Module(body=branches[0].body, type_ignores=[]))
        otherwise = ast.unparse(ast.Module(body=branches[0].orelse, type_ignores=[]))
        check(all(x in then for x in yes), "RANDOM_BRANCH_" + name)
        check(all(x in otherwise for x in no), "FIXED_BRANCH_" + name)
    constructors = [n for n in ast.walk(factory) if isinstance(n, ast.Call) and
                    isinstance(n.func, ast.Name) and n.func.id == "SymbolicAlchemy"]
    check(len(constructors) == 1, "FACTORY_CONSTRUCTOR")
    check("fix_obs_length" not in [x.arg for x in constructors[0].keywords], "FACTORY_LENGTH_ARG")
    check("fix_obs_length" not in [a.arg for a in factory.args.args], "FACTORY_LENGTH_PARAMETER")
    cls = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "SymbolicAlchemy"]
    check(len(cls) == 1, "SYMBOLIC_CLASS")
    ctor = ast_function(cls[0].body, "__init__")
    check(defaults(ctor).get("fix_obs_length") is False, "CONSTRUCTOR_LENGTH_DEFAULT")
    return {"factory_switches": list(expected), "factory_defaults": required,
            "factory_fix_obs_length_passed": False, "native_constructor_fix_obs_length": False,
            "source_only": True, "episodes": 0, "scientific_first_use": False,
            "mode_not_sealed": True, "disposition": "EXT01_FACTORY_MODE_NOT_FROZEN"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = audit_source(original_bytes(args.upstream))
    payload = (json.dumps({"upstream_commit": COMMIT, "upstream_blob": BLOB, **result},
                          sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    args.output.write_bytes(payload)


if __name__ == "__main__":
    main()

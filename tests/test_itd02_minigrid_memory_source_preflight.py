"""Static source preflight for pinned MiniGrid MemoryEnv; never imports/runs it."""
import ast
import os
import subprocess
import tomllib
import unittest
from pathlib import Path

UPSTREAM_COMMIT = "7f5853792ea7f04f75614661006d87fcf949f26d"
MEMORY_BLOB = "660b0a1b769948034c87bb421759c2b9a4f24548"
BASE_ENV_BLOB = "eb29e9a902de0715ab77ec981a2113576d7664fa"
ACTIONS_BLOB = "b440438bcb5a76a113d9d947b87a54dc8479ab15"
REGISTRATION_BLOB = "41b4a731255d19bdf61072b7100e752a759a3ae4"
LICENSE_BLOB = "880057397a1f9f7b3b1f0870eb84fa699ecbf50c"


def git(root, *args):
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, check=True, timeout=15
    ).stdout


def classes(tree):
    return {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}


def methods(cls):
    return {node.name: node for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


class PinnedMiniGridMemoryPreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get("MINIGRID_SOURCE")
        if not source:
            raise RuntimeError("MINIGRID_SOURCE_REQUIRED")
        cls.root = Path(source).resolve()
        rel = {
            "memory": "minigrid/envs/memory.py",
            "base": "minigrid/minigrid_env.py",
            "actions": "minigrid/core/actions.py",
            "registration": "minigrid/__init__.py",
        }
        for name, path in rel.items():
            if not (cls.root / path).is_file():
                raise RuntimeError("UPSTREAM_SOURCE_MISSING_" + name.upper())
        cls.rel = rel
        cls.trees = {
            name: ast.parse((cls.root / path).read_text(encoding="utf-8"), filename=path)
            for name, path in rel.items()
        }

    def test_exact_upstream_commit_blobs_license_and_clean_checkout(self):
        self.assertEqual(git(self.root, "rev-parse", "HEAD").decode().strip(), UPSTREAM_COMMIT)
        for path, blob in (
            (self.rel["memory"], MEMORY_BLOB),
            (self.rel["base"], BASE_ENV_BLOB),
            (self.rel["actions"], ACTIONS_BLOB),
            (self.rel["registration"], REGISTRATION_BLOB),
            ("LICENSE", LICENSE_BLOB),
        ):
            self.assertEqual(git(self.root, "rev-parse", "HEAD:" + path).decode().strip(), blob)
            self.assertEqual(git(self.root, "hash-object", str(self.root / path)).decode().strip(), blob)
        self.assertEqual(git(self.root, "status", "--porcelain").decode().strip(), "")

    def test_memory_world_has_a_real_history_dependent_matching_rule(self):
        memory_classes = classes(self.trees["memory"])
        self.assertIn("MemoryEnv", memory_classes)
        ms = methods(memory_classes["MemoryEnv"])
        grid = ast.unparse(ms["_gen_grid"])
        step = ast.unparse(ms["step"])
        self.assertIn("start_room_obj = self._rand_elem([Key, Ball])", grid)
        self.assertIn("other_objs = self._rand_elem([[Ball, Key], [Key, Ball]])", grid)
        self.assertIn("if start_room_obj == other_objs[0]", grid)
        self.assertIn("self.success_pos", grid)
        self.assertIn("self.failure_pos", grid)
        self.assertIn("tuple(self.agent_pos) == self.success_pos", step)
        self.assertIn("tuple(self.agent_pos) == self.failure_pos", step)
        self.assertIn("reward = self._reward()", step)
        self.assertIn("reward = 0", step)

    def test_public_observation_action_and_gym_step_contract_are_explicit(self):
        base_classes = classes(self.trees["base"])
        bs = methods(base_classes["MiniGridEnv"])
        init_text = ast.unparse(bs["__init__"])
        reset_text = ast.unparse(bs["reset"])
        step_text = ast.unparse(bs["step"])
        self.assertIn("spaces.Discrete(len(self.actions))", init_text)
        self.assertIn("shape=(self.agent_view_size, self.agent_view_size, 3)", init_text)
        self.assertIn('"image"', init_text)
        self.assertIn('"direction"', init_text)
        self.assertIn('"mission"', init_text)
        self.assertIn("obs = self.gen_obs()", reset_text)
        self.assertIn("return (obs, {})", reset_text)
        self.assertIn("return (obs, reward, terminated, truncated, {})", step_text)
        self.assertIn("return obs, reward, terminated, truncated, info", ast.unparse(methods(classes(self.trees["memory"])["MemoryEnv"])["step"]))

    def test_registered_fixed_size_variants_and_no_private_object_in_info(self):
        registration = ast.unparse(self.trees["registration"])
        for env_id in ("MiniGrid-MemoryS7-v0", "MiniGrid-MemoryS11-v0", "MiniGrid-MemoryS13-v0"):
            self.assertIn(env_id, registration)
        memory_step = methods(classes(self.trees["memory"])["MemoryEnv"])["step"]
        # The upstream MemoryEnv adds no private fields to info and never returns
        # its grid, cue, success position or failure position as learner data.
        self.assertFalse(any(isinstance(n, ast.Subscript) and
                             isinstance(n.value, ast.Name) and n.value.id == "info"
                             for n in ast.walk(memory_step)))
        returns = [n for n in ast.walk(memory_step) if isinstance(n, ast.Return)]
        self.assertTrue(returns)
        source = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
        self.assertFalse(any(isinstance(n.func, ast.Name) and n.func.id in ("MemoryEnv", "gym.make") for n in calls))
        self.assertFalse(any(isinstance(n.func, ast.Attribute) and n.func.attr in ("reset", "step") for n in calls))
        imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        self.assertFalse(any(module and module.startswith("minigrid") for module in imports))

    def test_license_metadata_is_mit(self):
        data = tomllib.loads((self.root / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertIn("MIT License", data["project"]["license"]["text"])


if __name__ == "__main__":
    unittest.main()

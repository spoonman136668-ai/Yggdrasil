"""F17 source-free DEV tests; actual Linux kernel enforcement is tested by CI smoke."""
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import f17_isolation_smoke as f


class F17(unittest.TestCase):
    def test_worker_compiles_without_installed_model_package(self):
        compile(f.WORKER_SOURCE, "<isolated-worker>", "exec")

    def test_worker_only_sees_allowlisted_public_fields(self):
        command = [sys._base_executable, "-I", "-S", "-B", "-c", f.WORKER_SOURCE]
        messages = [
            {"op": "act", "public_wire": json.dumps(
                {"observation": [1, 2], "done": False}), "action_dim": 2},
            {"op": "act", "public_wire": json.dumps(
                {"observation": [1, 2], "done": False, "answer_key": 1}), "action_dim": 1},
            {"op": "act", "public_wire": json.dumps(
                {"observation": [1], "done": False}), "action_dim": True},
        ]
        completed = subprocess.run(
            command, input="".join(json.dumps(msg) + "\n" for msg in messages),
            text=True, capture_output=True, timeout=8, check=True)
        answers = [json.loads(x) for x in completed.stdout.splitlines()]
        self.assertEqual(answers[0]["action"], [0.15000000000000002] * 2)
        self.assertEqual(answers[1], {"op": "error", "error": "ValueError"})
        self.assertEqual(answers[2], {"op": "error", "error": "ValueError"})

    def test_landlock_missing_fails_closed(self):
        with patch.object(f, "syscall", side_effect=OSError(38, "ENOSYS")):
            with self.assertRaises(OSError):
                f.install_landlock(object(), "/usr")

    def test_pinned_source_identity_and_non_claim(self):
        self.assertEqual(len(f.UPSTREAM_SHA), 40)
        self.assertEqual(len(f.UPSTREAM_TREE), 40)
        self.assertNotIn("import causal_worlds", f.WORKER_SOURCE)
        self.assertNotIn("from causal_worlds", f.WORKER_SOURCE)


if __name__ == "__main__":
    unittest.main()

"""Source-free separate-process checkpoint restoration proof for issue 568."""
import hashlib
import subprocess
import sys
import unittest
from pathlib import Path
from public_transition_planner import PublicTransitionPlanner

ROOT = Path(__file__).resolve().parent

class ColdProcessTests(unittest.TestCase):
    def test_independent_pid_restoration(self):
        p = PublicTransitionPlanner()
        p.observe(b"start", [0, 1])
        p.learn(1, b"middle", 0, False)
        p.observe(b"middle", [0, 2])
        p.learn(2, b"goal", 1, True)
        raw = p.checkpoint()
        p.observe(b"start", [0, 1])
        expected = str(p.choose(horizon=2))
        script = (
            "import sys; from public_transition_planner import PublicTransitionPlanner;"
            " p=PublicTransitionPlanner.restore(sys.stdin.buffer.read());"
            " p.observe(b'start',[0,1]);"
            " print(p.choose(horizon=2));"
            " print(p.checkpoint().hex())"
        )
        run = subprocess.run([sys.executable, "-c", script], input=raw,
                             cwd=str(ROOT), capture_output=True, timeout=10, check=True)
        lines = run.stdout.decode().splitlines()
        self.assertEqual(lines, [expected, raw.hex()])
        self.assertEqual(hashlib.sha256(bytes.fromhex(lines[1])).digest(),
                         hashlib.sha256(raw).digest())

if __name__ == "__main__":
    unittest.main()

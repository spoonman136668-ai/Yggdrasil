"""Engineering fixtures only: selected-experience planning survives cold restart.

No Farama environment is imported or stepped; no scientific cohort is used.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from research.native.itd02.mg90.relational_cells import RelationalFrontierCells, nodekey
from research.native.itd02.mg90.test_relational_cells import selected
from research.native.itd02.mg28.test_selected_change_cells import frame


class PersistentPlanningTest(unittest.TestCase):
    def learned_chain(self):
        model = RelationalFrontierCells()
        a, b, c = frame(heading=0), frame(heading=1), frame(heading=2)
        # Only completed selected feedback supplies the graph. All other
        # tried actions loop locally; the frontier is two observed edges away.
        for action in range(7):
            selected(model, a, b if action == 4 else a, action)
            selected(model, b, c if action == 3 else b, action)
        return model, a, b, c

    def test_two_step_route_is_learned_not_untrained_default(self):
        model, a, b, c = self.learned_chain()
        self.assertEqual(model.samples, 14)
        self.assertEqual(model.choose(a)["action"], 4)
        self.assertEqual(model.choose(b)["action"], 3)
        self.assertEqual(model.choose(a)["status"],
                         "MG90_SOURCE_OBSERVED_SHORTEST_FRONTIER_PATH")
        self.assertNotEqual(RelationalFrontierCells().choose(a)["action"], 4)
        self.assertEqual(model.graph[nodekey(a)][4]["next"], {nodekey(b): 1})
        self.assertNotIn(nodekey(c), model.graph[nodekey(a)][4]["next"])
        self.assertTrue(all(row["q"] == 0 for rows in model.graph.values() for row in rows))

    def test_reversed_experience_changes_plan_with_equal_sample_budget(self):
        model, a, b, c = self.learned_chain()
        control = RelationalFrontierCells()
        for action in range(7):
            selected(control, a, b if action == 2 else a, action)
            selected(control, b, c if action == 5 else b, action)
        self.assertEqual(model.samples, control.samples)
        self.assertEqual(control.choose(a)["action"], 2)
        self.assertEqual(control.choose(b)["action"], 5)

    def test_cold_process_preserves_decisions_not_only_checkpoint_bytes(self):
        model, a, b, _ = self.learned_chain()
        before = model.checkpoint()
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint = Path(tmp) / "checkpoint.json"
            observations = Path(tmp) / "observations.json"
            checkpoint.write_bytes(before)
            observations.write_text(json.dumps([a, b]), encoding="utf8")
            program = (
                "import json,pathlib,sys; "
                "from research.native.itd02.mg90.relational_cells import RelationalFrontierCells; "
                "raw=pathlib.Path(sys.argv[1]).read_bytes(); "
                "m=RelationalFrontierCells.restore(raw); "
                "obs=json.loads(pathlib.Path(sys.argv[2]).read_text(encoding='utf8')); "
                "print(json.dumps([m.choose(x) for x in obs],sort_keys=True)); "
                "assert m.checkpoint()==raw"
            )
            result = subprocess.run([sys.executable, "-B", "-c", program,
                                     str(checkpoint), str(observations)],
                                    check=True, timeout=30, capture_output=True, text=True,
                                    env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
            self.assertEqual(json.loads(result.stdout), [model.choose(a), model.choose(b)])
        self.assertEqual(model.checkpoint(), before)

    def test_unrelated_mission_experience_does_not_replace_old_route(self):
        model, a, b, _ = self.learned_chain()
        other = frame("pick up the blue ball", heading=0)
        selected(model, other, frame("pick up the blue ball", heading=1), 6)
        restored = RelationalFrontierCells.restore(model.checkpoint())
        self.assertEqual(restored.choose(a)["action"], 4)
        self.assertEqual(restored.choose(b)["action"], 3)
        self.assertEqual(restored.samples, 15)


if __name__ == "__main__":
    unittest.main()

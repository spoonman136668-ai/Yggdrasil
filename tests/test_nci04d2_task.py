"""NCI-04D2 integrated task consumer; tests must not imply scientific success."""
import io
import json
import math
import unittest
from yggdrasil.task_runtime import LocalTaskRuntime, LocalCountControl
from scripts.nci04d2_task import run

class NativeTaskContract(unittest.TestCase):
    def test_train_predict_lesion_unlabeled_repair_and_checkpoint(self):
        graph=[((i+2)%8,(i+5)%8) for i in range(8)]
        task=LocalTaskRuntime(graph)
        count=LocalCountControl(graph)
        observations=[]
        for n in range(60):
            bits=[(n//(1+(i%3)) + i)%2 for i in range(8)]
            targets=[bits[graph[i][0]] ^ bits[graph[i][1]] for i in range(8)]
            task.observe(bits,targets)
            count.observe(bits,targets)
            observations.append(bits)
        sample=observations[13]
        self.assertEqual(len(task.predict(sample)),8)
        self.assertEqual(len(count.predict(sample)),8)
        snapshot=task.snapshot()
        same=LocalTaskRuntime.restore(snapshot)
        self.assertEqual(same.snapshot(),snapshot)
        same.lesion([1,4,6])
        before=same.snapshot()
        with self.assertRaises(ValueError):
            same.observe(sample,[0]*8)
        self.assertEqual(same.snapshot(),before)
        saved_genome=json.dumps(same.core.genome)
        repaired=same.repair_unlabeled(sample,steps=10)
        self.assertEqual(json.dumps(same.core.genome),saved_genome)
        self.assertEqual(len(repaired),8)
        self.assertTrue(all(math.isfinite(x) and 0<=x<=1 for x in repaired))
        self.assertEqual(LocalTaskRuntime.restore(same.snapshot()).snapshot(),same.snapshot())

    def test_repair_uses_only_local_inputs(self):
        task=LocalTaskRuntime()
        bits=[0]*8
        first=task.predict(bits)
        other=bits[:]
        other[4]=1
        self.assertEqual(task.component(bits,0),task.component(other,0))
        task.lesion([0])
        task.repair_unlabeled(bits,3)
        self.assertEqual(task.steps,3)

    def test_reject_illegal_topology_and_lesions(self):
        for edges in ([[1,1]]*8, [[1,9]]*8, [[0,1]]*8, []):
            with self.assertRaises(ValueError):
                LocalTaskRuntime(edges)
        task=LocalTaskRuntime()
        for cells in ([0,0],[0,8],[]):
            with self.assertRaises(ValueError): task.lesion(cells)

    def test_cli_source_free_end_to_end(self):
        events=[
          {"op":"init"},
          {"op":"observe","bits":[0]*8,"outcomes":[1]*8},
          {"op":"predict","bits":[0]*8},
          {"op":"lesion","cells":[2,3]},
          {"op":"repair_unlabeled","bits":[0]*8,"steps":3},
          {"op":"snapshot"}]
        dst=io.StringIO()
        run(io.StringIO("\n".join(json.dumps(x) for x in events)+"\n"),dst)
        outputs=[json.loads(x) for x in dst.getvalue().splitlines()]
        self.assertEqual(len(outputs),3)
        self.assertIn("count_control",outputs[0])
        self.assertIn("candidate_after_repair",outputs[1])
        self.assertEqual(outputs[2]["damaged"],[2,3])
        bad=[{"op":"init"},{"op":"lesion","cells":[1]},{"op":"observe","bits":[0]*8,"outcomes":[1]*8}]
        with self.assertRaises(ValueError):
            run(io.StringIO("\n".join(json.dumps(x) for x in bad)+"\n"),io.StringIO())

if __name__=="__main__":unittest.main()

"""MG90 source-only selected-graph, delayed original reward and cold-process tests."""
import os
import subprocess
import sys
import tempfile
import unittest
from research.native.itd02.mg90.relational_cells import RelationalFrontierCells,nodekey
from research.native.itd02.mg28.test_selected_change_cells import frame
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter

def selected(model,before,after,action,reward=0):
    adapter=OriginalMissionAdapter()
    adapter.reset_public(before)
    model.start_session(adapter,"mg90-source-engineering-fixture",live=False)
    adapter.submit(action)
    adapter.complete(after,float(reward),bool(reward),False)
    return model.learn_selected(adapter,before,after)

class RelationalGraphTest(unittest.TestCase):
    def test_source_graph_edges_only_from_selected_original(self):
        agent=RelationalFrontierCells()
        a=frame()
        b=frame(heading=1)
        self.assertEqual(agent.choose(a)["action"],0)
        selected(agent,a,b,0)
        self.assertEqual(agent.samples,1)
        self.assertEqual(agent.graph[nodekey(a)][0]["next"],{nodekey(b):1})
        self.assertEqual(agent.graph[nodekey(a)][0]["count"],1)
        self.assertEqual(agent.choose(a)["action"],1)
        self.assertEqual(agent.graph[nodekey(a)][0]["q"],0)

    def test_bfs_navigates_only_source_observed_edge(self):
        agent=RelationalFrontierCells()
        a=frame()
        b=frame(heading=1)
        for action in range(7):
            selected(agent,a,b,action)
        self.assertEqual(agent.samples,7)
        self.assertEqual(agent.choose(a)["action"],0)
        self.assertEqual(agent.choose(a)["status"],
                         "MG90_SOURCE_OBSERVED_SHORTEST_FRONTIER_PATH")
        self.assertNotIn(nodekey(b),agent.graph)

    def test_original_positive_reward_backs_up_only_selected_episode(self):
        agent=RelationalFrontierCells()
        a=frame()
        b=frame(heading=1)
        c=frame(heading=2)
        adapter=OriginalMissionAdapter()
        adapter.reset_public(a)
        agent.start_session(adapter,"mg90-same-episode",live=False)
        adapter.submit(0)
        adapter.complete(b,0.,False,False)
        agent.learn_selected(adapter,a,b)
        adapter.submit(1)
        adapter.complete(c,.8,True,False)
        agent.learn_selected(adapter,b,c)
        self.assertGreater(agent.graph[nodekey(a)][0]["q"],0)
        self.assertGreater(agent.graph[nodekey(b)][1]["q"],0)
        checkpoint=agent.checkpoint()
        # A new source episode must not carry its prior eligibility trace.
        adapter2=OriginalMissionAdapter()
        adapter2.reset_public(a)
        agent.start_session(adapter2,"new-source-episode",live=False)
        self.assertEqual(agent.trace,[])
        self.assertEqual(agent.samples,2)
        self.assertEqual(RelationalFrontierCells.restore(checkpoint).checkpoint(),
                         checkpoint)

    def test_mission_isolation_and_unselected_feedback(self):
        agent=RelationalFrontierCells()
        a=frame("pick up the red ball")
        b=frame("pick up the blue ball")
        self.assertNotEqual(nodekey(a),nodekey(b))
        adapter=OriginalMissionAdapter()
        adapter.reset_public(a)
        agent.start_session(adapter,"source-only",live=False)
        before=agent.checkpoint()
        with self.assertRaises(ValueError):
            agent.learn_selected(adapter,a,frame(heading=1))
        self.assertEqual(agent.checkpoint(),before)

    def test_canonical_cold_restore_new_python_process(self):
        agent=RelationalFrontierCells()
        a=frame()
        selected(agent,a,frame(heading=1),0)
        blob=agent.checkpoint()
        with self.assertRaises(ValueError):
            RelationalFrontierCells.restore(blob+b"!")
        with tempfile.TemporaryDirectory() as temp:
            name=os.path.join(temp,"model.bin")
            with open(name,"wb") as f:
                f.write(blob)
            script=("import pathlib,sys; "
                    "from research.native.itd02.mg90.relational_cells import RelationalFrontierCells; "
                    "v=pathlib.Path(sys.argv[1]).read_bytes(); "
                    "assert RelationalFrontierCells.restore(v).checkpoint()==v")
            subprocess.run([sys.executable,"-B","-c",script,name],
                           timeout=30,check=True)

if __name__=="__main__":
    unittest.main()

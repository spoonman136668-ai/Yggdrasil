import unittest
from agent import TrajectoryAgent,MembershipAgent,TrainedOneHot
from world import World
from battery import reachable_states


class Tests(unittest.TestCase):
    def test_only_real_action_reachable_sources(self):
        world=World(4,'arbitrary_hash','unit-reachable');agent=TrajectoryAgent(4)
        for _ in range(130):agent.transition(world.apply)
        reached=set(reachable_states(world,4));self.assertEqual(agent.resets,2)
        for t,(a,x,y) in enumerate(agent.rows):
            self.assertEqual(x,0 if t%64==0 else agent.rows[t-1][2]);self.assertIn(x,reached);self.assertEqual(y,world.apply(a,x))

    def test_numeric_least_visit_winner(self):
        agent=TrajectoryAgent(4);self.assertEqual(agent.choose_action(),0)
        agent.visits[0][0]=3;self.assertEqual(agent.choose_action(),1)
        agent.visits[1][0]=3;self.assertEqual(agent.choose_action(),0)

    def test_only_chosen_action_visit_weights_change(self):
        agent=TrajectoryAgent(4)
        for _ in range(20):agent.transition(lambda a,x:0)
        self.assertEqual(sum(agent.visits[0]),10);self.assertEqual(sum(agent.visits[1]),10)
        self.assertEqual([a for a,x,y in agent.rows],[0,1]*10)

    def test_membership_full_rule_reconstruction(self):
        world=World(4,'arbitrary_hash','unit-membership');agent=MembershipAgent(4)
        for _ in range(32):agent.transition(world.apply)
        self.assertEqual(len({(a,x) for a,x,y in agent.rows}),32)
        for a in range(2):
            for x in range(16):self.assertEqual(agent.apply(a,x),world.apply(a,x))

    def test_replay_determinism_and_onehot_fit(self):
        world=World(4,'quadratic','unit-replay');agents=[TrajectoryAgent(4,'random') for _ in range(2)]
        for agent in agents:
            for _ in range(70):agent.transition(world.apply)
        self.assertEqual(agents[0].rows,agents[1].rows);self.assertEqual(agents[0].visits,agents[1].visits)
        self.assertEqual(TrainedOneHot(agents[0].rows).training_errors,0)

    def test_unobserved_counterworld_indistinguishable(self):
        world=World(4,'arbitrary_hash','unit-counterworld');agent=TrajectoryAgent(4)
        agent.transition(world.apply);seen={(a,x) for a,x,y in agent.rows}
        pair=next((a,x) for a in range(2) for x in range(16) if (a,x) not in seen)
        def alternative(a,x):return world.apply(a,x)^int((a,x)==pair)
        self.assertTrue(all(alternative(a,x)==y for a,x,y in agent.rows))
        self.assertNotEqual(alternative(*pair),world.apply(*pair))


if __name__=='__main__':unittest.main()

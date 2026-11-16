"""CB7 contract and exact strong Bayesian negative tests."""
import unittest
from collections import namedtuple
from itertools import product
from public_world import World, public_config
from policies import DirectOneStep,ExactBayesianDP, NoProbe
from study import run_one, one_world


class PublicCostTests(unittest.TestCase):
    def test_seed_fence_and_costs(self):
        for invalid in (True,82599,82632,978500,978600):
            with self.assertRaises(PermissionError): public_config(invalid)
        for s in range(82600,82632):
            p,c=public_config(s)
            self.assertAlmostEqual(sum(p),1.)
            self.assertTrue(all(0.02-1e-10<=x<=0.45 for x in c))

    def test_public_event_contains_no_owner_identity(self):
        env=World(82600,5)
        p=env.probe(1)
        self.assertEqual(p._fields,('channel','positive','cost'))
        self.assertFalse(hasattr(p,'hidden'))
        self.assertFalse(p.positive)

    def test_actual_probe_and_terminal_budget(self):
        env=World(82600,3)
        env.probe(0)
        with self.assertRaises(ValueError):env.probe(0)
        value,correct=env.terminal(3)
        self.assertTrue(correct)
        self.assertAlmostEqual(value,1-env.costs[0])
        with self.assertRaises(ValueError):env.probe(1)

    def test_high_cost_stops_without_probe(self):
        prior=tuple([1/6]*6)
        cost=tuple([.9]*6)
        greedy,dp=DirectOneStep(prior,cost),ExactBayesianDP(prior,cost)
        self.assertIsNone(greedy.next_probe())
        self.assertIsNone(dp.next_probe())
        self.assertAlmostEqual(dp.expected_optimal,1/6)

    def test_optimal_upper_bound_across_all_actual_hidden(self):
        for seed in range(82600,82632):
            r=one_world(seed)
            self.assertGreaterEqual(r['summary']['EXACT_BAYES']['expected_net_value']+1e-10,
                                    r['summary']['DIRECT_GREEDY']['expected_net_value'])

    def test_invalid_public_receipt_is_atomic(self):
        prior,cost=public_config(82600)
        model=DirectOneStep(prior,cost)
        Event=namedtuple('Event','channel positive cost')
        Extra=namedtuple('Extra','channel positive cost hidden_owner')
        bad=(Extra(0,True,cost[0],4), Event(True,False,cost[0]),
             Event(0,0,cost[0]),Event(0,False,cost[0]*2))
        for e in bad:
            receipt=model.public_receipt()
            with self.assertRaises(ValueError):model.observe(e)
            self.assertEqual(receipt,model.public_receipt())
        model.observe(Event(0,False,cost[0]))
        with self.assertRaises(ValueError):model.observe(Event(0,False,cost[0]))

    def test_conditional_exact_posterior_all_six(self):
        prior=(.45,.2,.1,.1,.1,.05)
        cost=(.02,.1,.1,.1,.1,.1)
        for hidden in range(6):
            env=World(82600,hidden)
            agent=ExactBayesianDP(prior,cost)
            while (channel:=agent.next_probe()) is not None:
                # Use public deterministic result, not private env hidden in agent.
                agent.observe(type(env.probe(channel))(channel,channel==hidden,cost[channel]))
            self.assertIn(agent.choose_answer(),range(6))

    def test_no_pretense_of_training_or_cross_world_memory(self):
        for hidden in range(6):
            r=run_one(82601,hidden,'NO_PROBE')
            self.assertEqual(r['paid_probe_actions'],0)
            self.assertEqual(r['paid_total_cost'],0.)

if __name__=='__main__':unittest.main()

"""NCI-04E: one-hop survival and irrecoverable-function tests."""
import unittest
from yggdrasil.distributed_setpoint import DistributedSetpoint

def experience(t, impossible=False):
    bit=t%2
    sensors=[(t+i*3)%2 for i in range(8)]
    sensors[2]=bit
    sensors[4]=bit
    outcomes=sensors.copy()
    outcomes[3]=(t//2)%2 if impossible else bit
    return sensors,outcomes

class TestNCI04ELocalSurvival(unittest.TestCase):
    def test_information_survives_destroyed_cell_and_restores_output(self):
        m=DistributedSetpoint()
        for t in range(64):
            x,y=experience(t)
            m.observe(x,y)
        before=m.has_neighbor_memory(3)
        self.assertEqual(before,(64,64))
        m.lesion(3)
        self.assertEqual(m.shadow[3],[[[0,0] for _ in range(2)] for _ in range(2)])
        self.assertEqual(m.has_neighbor_memory(3),before)
        self.assertIsNone(m.recovered_function(3))
        m.regrow_blank(3)
        # No new supervised observations are supplied after lesion.
        recovered=0
        for t in range(64,80):
            x,y=experience(t)
            m.exchange_one_hop(x)
            result=m.recovered_function(3)
            self.assertIsNotNone(result)
            recovered+=int(result==y[3])
        self.assertEqual(recovered,16)
        self.assertEqual(m.steps,64)
        print("NCI04E_Y_PREDICTIONS=16/16 NEIGHBOR_RETAINED=64,64 POST_LESION_TARGET_LABELS=0")
        # A cold cell with the same local input but no retained neighbor
        # predictions cannot form a confident recovery assertion.
        cold=DistributedSetpoint()
        cold.lesion(3)
        cold.regrow_blank(3)
        x,_=experience(80)
        cold.exchange_one_hop(x)
        self.assertIsNone(cold.recovered_function(3))
        # A conventional equal-information shadow-table peer can also solve
        # this simple case: do not claim competitive learning advantage.

    def test_irrecoverable_function_must_abstain(self):
        m=DistributedSetpoint()
        for t in range(64):
            x,y=experience(t,impossible=True)
            m.observe(x,y)
        m.lesion(3)
        m.regrow_blank(3)
        hard_false_predictions=0
        for t in range(64,80):
            x,_=experience(t,impossible=True)
            m.exchange_one_hop(x)
            if m.recovered_function(3) is not None:
                hard_false_predictions+=1
        self.assertEqual(hard_false_predictions,0)
        print("NCI04E_Y_IRRECOVERABLE_HARD_FALSE_PREDICTIONS=0/16")

    def test_one_hop_only_no_hidden_nonlocal_channel(self):
        m=DistributedSetpoint()
        for t in range(64):
            x,y=experience(t)
            m.observe(x,y)
        m.lesion(3)
        m.regrow_blank(3)
        x,_=experience(80)
        m.exchange_one_hop(x)
        first=m.recovered_function(3)
        # Cell 0 is three ring edges from 3. Editing its stored predictions
        # must not affect delivery to 3 in this single synchronous round.
        m.shadow[0]=[[[9,0] for _ in range(2)] for _ in range(2)]
        m.exchange_one_hop(x)
        self.assertEqual(first,m.recovered_function(3))
        m.lesion(2)
        m.exchange_one_hop(x)
        self.assertIsNone(m.recovered_function(3))
        with self.assertRaises(ValueError):
            m.exchange_one_hop([0]*7)
        with self.assertRaises(ValueError):
            m.lesion(8)

if __name__=="__main__":
    unittest.main()

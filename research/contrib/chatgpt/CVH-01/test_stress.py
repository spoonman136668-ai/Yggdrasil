"""Source-free deterministic randomized return-to-go and cold-custody controls."""
from collections import namedtuple
import random
import unittest
import earned_memory as native
from strong_conventional import batch_public_returns

P=namedtuple("PublicConsequence",native.FIELDS)

class BoundedPublicStreamStress(unittest.TestCase):
    def test_700_independent_fabricated_public_streams(self):
        rng=random.Random(2401)
        n=0
        largest=0
        for sequence in range(700):
            model=native.EarnedReturnMemory()
            witnessed=[]
            state=rng.randrange(2)
            length=rng.randrange(1,60)
            for step in range(length):
                a=rng.randrange(2)
                reward=rng.randrange(2)
                after=rng.randrange(2)
                done=bool(rng.randrange(13)==0 or step==length-1)
                row=P(state,a,reward,after,done,False)
                model.observe(row)
                witnessed.append(row)
                control_count,control_total=batch_public_returns(witnessed)
                self.assertEqual((model.count,model.total),(control_count,control_total))
                cold=native.EarnedReturnMemory.restore(model.snapshot())
                self.assertEqual(model.snapshot(),cold.snapshot())
                largest=max(largest,len(model.snapshot()))
                n+=1
                state=rng.randrange(2) if done else after
        self.assertEqual(n,21231)
        self.assertLess(largest,12000)

if __name__=="__main__":
    unittest.main()

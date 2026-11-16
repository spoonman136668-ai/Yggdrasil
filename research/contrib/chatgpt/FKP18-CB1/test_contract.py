"""Public-only, source-independent CB1 tests on delayed action consequences."""
from collections import Counter, namedtuple
import random
import unittest
import binding as m

Past = namedtuple('Past', m.PAST_FIELDS)
Step = namedtuple('Step', m.FIELDS)


def tape(seed, a, b, table, n=131):
    rng = random.Random(seed)
    states = [tuple(rng.randrange(16) for _ in range(8)) for _ in range(n+1)]
    actions = [rng.randrange(2) for _ in range(n)]
    rewards = [0]*n
    for t in range(3,n):
        j=t-2
        bits=m._feature_bits(states[j], actions[j-1], actions[j-2] if j>=2 else 0)
        key=((bits>>a&1)<<1)|(bits>>b&1)
        output=(table>>key)&1
        rewards[t]=1 if actions[j]==output else -1
    return [Step(states[t], actions[t], states[t+1], rewards[t], False,
                 tuple(Past(states[j], actions[j], rewards[j], states[j+1], False)
                       for j in range(max(0,t-16),t))) for t in range(n)]


class ContractTests(unittest.TestCase):
    def test_three_new_context_families_and_cold_restore(self):
        for seed,a,b,table in ((7125,1,6,6),(7126,18,32,6),(7127,5,35,8)):
            learned=m.ConditionalTemporalBinder()
            for row in tape(seed,a,b,table):
                learned.observe_public(row)
            learned.seal()
            self.assertEqual(learned.binding[:3],(a,b,table))
            self.assertEqual(learned.binding[-2:],(128,128))
            self.assertLessEqual(len(learned.snapshot()),128)
            cold=m.ConditionalTemporalBinder.restore(learned.snapshot())
            self.assertEqual(cold.snapshot(),learned.snapshot())
            rng=random.Random(seed+500)
            for _ in range(128):
                state=tuple(rng.randrange(16) for _ in range(8))
                s0=tuple(rng.randrange(16) for _ in range(8))
                s1=tuple(rng.randrange(16) for _ in range(8))
                p0,p1=rng.randrange(2),rng.randrange(2)
                history=(Past(s0,p0,0,s1,False),Past(s1,p1,0,state,False))
                bits=m._feature_bits(state,p1,p0)
                correct=(table>>(((bits>>a&1)<<1)|(bits>>b&1)))&1
                self.assertEqual(learned.choose_public(state,history),correct)
                self.assertEqual(cold.choose_public(state,history),correct)

    def test_equal_marginal_histogram_distinct_binding(self):
        def one(flip):
            states=[(2*((t//2)%2),4*(t%2),0,0,0,0,0,0) for t in range(132)]
            actions=[(t//4)%2 for t in range(131)]
            rewards=[0]*131
            for t in range(3,131):
                j=t-2; bit=((states[j][0]>>1)&1)^((states[j][1]>>2)&1)^flip
                rewards[t]=1 if actions[j]==bit else -1
            return [Step(states[t],actions[t],states[t+1],rewards[t],False,
                         tuple(Past(states[j],actions[j],rewards[j],states[j+1],False)
                               for j in range(max(0,t-16),t))) for t in range(131)]
        def marginal(rows):
            counts=Counter(); sums=Counter()
            for r in rows:
                sums[r.action]+=r.reward
                for i in range(8): counts[r.action,i,(r.after[i]-r.before[i])%16]+=1
            return counts,sums
        first,second=one(0),one(1)
        self.assertEqual(marginal(first),marginal(second))
        models=[]
        for rows in (first,second):
            learner=m.ConditionalTemporalBinder()
            for r in rows: learner.observe_public(r)
            models.append(learner.seal())
        self.assertNotEqual(models[0].choose_public((0,)*8,()),
                            models[1].choose_public((0,)*8,()))

    def test_strict_public_schema_and_atomicity(self):
        learner=m.ConditionalTemporalBinder()
        row=tape(7125,1,6,6)[5]
        Extra=namedtuple('Extra',m.FIELDS+('private_oracle',))
        for invalid in (Extra(*row,1),row._replace(action=True),
                        row._replace(reward=float('nan')),
                        row._replace(before=(0,)*7),
                        row._replace(history=row.history+(row.history[-1],))):
            with self.assertRaises(ValueError):learner.observe_public(invalid)
            self.assertEqual(learner._credited,0)

    def test_cap_and_insufficient_evidence(self):
        learner=m.ConditionalTemporalBinder()
        self.assertIsNone(learner.choose_public((0,)*8,()))
        data=tape(7125,1,6,6)
        for row in data[:30]:learner.observe_public(row)
        with self.assertRaises(ValueError):learner.seal()
        for row in data[30:]:learner.observe_public(row)
        with self.assertRaises(ValueError):learner.observe_public(data[-1])
        learner.seal()
        with self.assertRaises(ValueError):learner.observe_public(data[-1])

    def test_cold_checksum_rejects_corruption(self):
        learner=m.ConditionalTemporalBinder()
        for row in tape(7125,1,6,6):learner.observe_public(row)
        checkpoint=bytearray(learner.seal().snapshot());checkpoint[8]^=1
        with self.assertRaises(ValueError):
            m.ConditionalTemporalBinder.restore(bytes(checkpoint))


if __name__=='__main__':unittest.main()

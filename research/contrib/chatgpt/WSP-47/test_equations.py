import unittest
from equations import EquationBank,AdaptiveModel,BankModel
from reference import BatchBank
from world import World


class Tests(unittest.TestCase):
    def test_nonbasis_linear_learning(self):
        world=World(4,'linear','unit-nonbasis');bank=EquationBank(4,1)
        # These five input vectors span affine features; not zero+singletons.
        states=(15,14,13,11,7)
        for x in states:bank.observe(x,world.apply(0,x))
        self.assertEqual(sum(bank.occupied),5)
        for x in range(16):self.assertEqual(bank.predict(x),world.apply(0,x))

    def test_abstains_outside_observation_span(self):
        bank=EquationBank(4,1);bank.observe(15,7)
        self.assertEqual(bank.predict(15),7);self.assertIsNone(bank.predict(0))

    def test_retains_facts_after_prior_contradiction(self):
        bank=EquationBank(4,1)
        rows=[(x,int(x&3==3)) for x in range(16)]
        for x,y in rows:bank.observe(x,y)
        self.assertEqual(bank.fault,1)
        self.assertEqual([bank.predict(x) for x in range(16)],[y for x,y in rows])

    def test_independent_batch_fit_parity(self):
        for degree in (1,2,3,'full'):
            world=World(4,'cubic_ood','unit-parity');rows=[(x,world.apply(0,x)) for x in (15,3,7,0,9,2,12,5)]
            bank=EquationBank(4,degree)
            for x,y in rows:bank.observe(x,y)
            ref=BatchBank(4,degree,rows)
            self.assertEqual([bank.predict(x) for x in range(16)],[ref.predict(x) for x in range(16)])

    def test_numeric_adaptive_rejects_inconsistent_low_prior(self):
        models=[BankModel([EquationBank(4,d) for _ in range(2)]) for d in (1,2,3,'full')]
        for x in range(16):
            for model in models:model.banks[0].observe(x,int(x&3==3))
        adaptive=AdaptiveModel(models);self.assertEqual(adaptive.selected(0),[0,1,0,0])
        self.assertEqual([adaptive.apply(0,x) for x in range(16)],[int(x&3==3) for x in range(16)])

    def test_snapshot_tamper_and_action_isolation(self):
        bank=EquationBank(4,2);bank.observe(7,9);snap=bank.snapshot()
        self.assertEqual(EquationBank.restore(snap).snapshot(),snap)
        other=EquationBank(4,2);other.observe(3,4);self.assertEqual(bank.snapshot(),snap)
        with self.assertRaises(ValueError):EquationBank.restore(snap+b'x')
        with self.assertRaises(ValueError):EquationBank(4,5)

    def test_wrong_consistent_prior_can_be_confident_before_evidence(self):
        bank=EquationBank(4,1)
        for x in (0,1,2,4,8):bank.observe(x,int(x&3==3))
        self.assertEqual(bank.predict(3),0)  # True AND source returns1 here.
        bank.observe(3,1)
        self.assertEqual(bank.fault,1);self.assertEqual(bank.predict(3),1)
        self.assertIsNone(bank.predict(5))


if __name__=='__main__':unittest.main()

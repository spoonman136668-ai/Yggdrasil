"""DEV optimizer fixtures only; no actual corpus or protected trial."""
import copy
import unittest

import torch
from torch import nn
from bounded_train import train


class Fixture(nn.Module):
    def __init__(self):
        super().__init__()
        self.weight = nn.Parameter(torch.tensor(0.1))
        self.target = nn.Parameter(torch.tensor(0.1), requires_grad=False)
        self.updates = 0
        self.fail = False

    def objective(self, context, future):
        x = torch.tensor([c[0]/255 for c in context])
        y = torch.tensor([c[0]/255 for c in future])
        loss = (self.weight*x-y).square().mean()
        if self.fail:
            loss = loss * float('nan')
        return loss, {"min_online_std": x.std(unbiased=False)}

    @torch.no_grad()
    def update_target(self):
        self.target.lerp_(self.weight, 0.1)
        self.updates += 1


class TrainTests(unittest.TestCase):
    pairs = [(b'a', b'b'), (b'c', b'd'), (b'e', b'f'), (b'g', b'h')]

    def test_accounting_and_updates(self):
        model = Fixture()
        r = train(model, self.pairs, seed=5, epochs=2, batch_size=2)
        self.assertEqual((r['steps'], r['observations'], r['exposure_bytes']), (4, 8, 16))
        self.assertEqual(model.updates, 4)
        self.assertFalse(model.training)
        self.assertNotEqual(float(model.weight.detach()), 0.1)
        self.assertIsNone(model.target.grad)

    def test_reproducibility(self):
        a, b = Fixture(), Fixture()
        x = train(a, self.pairs, seed=8, batch_size=2)
        y = train(b, self.pairs, seed=8, batch_size=2)
        x.pop('elapsed_seconds'); y.pop('elapsed_seconds')
        self.assertEqual(x, y)
        for p,q in zip(a.parameters(), b.parameters()):
            torch.testing.assert_close(p, q, rtol=0, atol=0)

    def test_budgets_fail_before_mutation(self):
        for kw in ({'max_steps':1}, {'max_bytes':7}, {'epochs':0}, {'rate':float('nan')}):
            m = Fixture()
            before = copy.deepcopy(m.state_dict())
            with self.assertRaises(ValueError):
                train(m, self.pairs, seed=1, batch_size=2, **kw)
            self.assertEqual(m.updates, 0)
            for k,p in m.state_dict().items():
                torch.testing.assert_close(p, before[k])

    def test_invalid_observations(self):
        for pairs in (self.pairs[:3], [(b'a', b''), (b'b', b'c')], [('a', b'b'), (b'b', b'c')]):
            with self.assertRaises(ValueError):
                train(Fixture(), pairs, seed=1, batch_size=2)

    def test_nonfinite_loss(self):
        m = Fixture(); m.fail = True
        with self.assertRaises(RuntimeError):
            train(m, self.pairs, seed=1, batch_size=2)
        self.assertEqual(m.updates, 0)


if __name__ == '__main__':
    unittest.main()

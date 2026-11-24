"""Fabricated engineering fixtures, not a scientific workload."""
import unittest

import torch
from torch import nn
from anchor_loss import anchors, anchor_loss, objective


class Fixture(nn.Module):
    def __init__(self):
        super().__init__()
        self.project = nn.Linear(8, 8, bias=False)
        nn.init.zeros_(self.project.weight)

    def encode(self, rows):
        return self.project(anchors(rows, 8))

    def objective(self, context, future):
        z = self.encode(context)
        return z.square().mean(), {'base': z.detach().square().mean()}


class AnchorTests(unittest.TestCase):
    rows = [bytes([0]*4), bytes([255]*4), bytes([0,255,0,255]), bytes([255,0,255,0])]

    def test_position_and_determinism(self):
        a = anchors(self.rows, 8)
        self.assertTrue(torch.equal(a, anchors(self.rows, 8)))
        self.assertTrue(torch.equal(a[0], -a[1]))
        self.assertFalse(torch.equal(a[2], a[3]))
        self.assertFalse(a.requires_grad)

    def test_collapse_gradient(self):
        z = torch.zeros((4,8), requires_grad=True)
        variance = torch.relu(.2-(z.var(dim=0,unbiased=False)+1e-4).sqrt()).mean()
        variance.backward()
        self.assertEqual(float(z.grad.abs().max()), 0.)
        z.grad.zero_()
        anchor_loss(z, self.rows).backward()
        self.assertGreater(float(z.grad.abs().max()), 0.)
        self.assertFalse(torch.equal(z.grad[0], z.grad[1]))

    def test_sham_and_off(self):
        z = anchors(self.rows, 8).requires_grad_()
        self.assertEqual(float(anchor_loss(z, self.rows).detach()), 0.)
        self.assertGreater(float(anchor_loss(z, self.rows,'sham').detach()), 0.)
        anchor_loss(z, self.rows,'off').backward()
        self.assertEqual(float(z.grad.abs().max()), 0.)

    def test_projection_recovery(self):
        for mode in ('aligned', 'off'):
            model = Fixture()
            opt = torch.optim.SGD(model.parameters(), lr=.1)
            loss,_ = objective(model, self.rows, self.rows, mode)
            loss.backward(); opt.step()
            spread = float(model.encode(self.rows).detach().std(dim=0).mean())
            if mode == 'aligned':
                self.assertGreater(spread, 0.)
            else:
                self.assertEqual(spread, 0.)

    def test_invalid_inputs(self):
        for rows in ([b'', b'a'], [b'a'], [b'a'*257, b'b']):
            with self.assertRaises(ValueError):
                anchors(rows,8)
        with self.assertRaises(ValueError):
            anchor_loss(torch.zeros(4,8),self.rows,'unknown')
        with self.assertRaises(ValueError):
            objective(Fixture(),self.rows,self.rows,weight=float('nan'))


if __name__ == '__main__':
    unittest.main()

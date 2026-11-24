import hashlib
import json
import unittest

import torch
from corpus_prepare import convert
from pair_controls import PairControl
from bounded_train import train


def convert_fixture(item, source='aqua'):
    raw = json.dumps(item).encode()
    return convert(raw, hashlib.sha256(raw).hexdigest(), source, 'train')


class Tests(unittest.TestCase):
    def test_aqua(self):
        item = dict(question='1+1?', options=['A)0','B)2','C)3','D)4','E)5'], correct='B', rationale='DO NOT EXPOSE')
        rows, counts = convert_fixture(item)
        self.assertEqual(rows[0]['answer'], 1)
        self.assertEqual(rows[0]['options'][1], '2')
        self.assertNotIn('DO NOT EXPOSE', str(rows))
        self.assertEqual(counts, dict(input=1, eligible=1, excluded_length=0))
        item['question'] = 'x'*257
        self.assertEqual(convert_fixture(item)[1]['excluded_length'], 1)

    def test_openbook(self):
        item = dict(id='q1', question=dict(stem='Which?', choices=[dict(label=k,text=k.lower()) for k in 'DCBA']), answerKey='A', fact1='SECRET')
        rows, _ = convert_fixture(item, 'openbookqa')
        self.assertEqual(rows[0]['answer'], 3)
        self.assertNotIn('SECRET', str(rows))

    def test_digest(self):
        with self.assertRaises(ValueError):
            convert(b'{}', '0'*64, 'aqua', 'train')

    def test_controls(self):
        for kind in ('recurrent','attention'):
            torch.manual_seed(7)
            model = PairControl(kind)
            pairs = [b'ab',b'cd',b'ef',b'gh']
            before = model.output.weight.detach().clone()
            loss, stats = model.objective(pairs, pairs[::-1])
            self.assertTrue(torch.isfinite(loss))
            opt = torch.optim.SGD(model.parameters(), lr=.01)
            loss.backward(); opt.step()
            self.assertFalse(torch.equal(before, model.output.weight))
            model.eval()
            self.assertEqual(len(model.scores(b'ab', pairs)),4)
            torch.testing.assert_close(model.encode([b'ab'])[0], model.encode([b'ab', b'abcde'])[0])
            # All identical targets are positives; never false-negative each other.
            self.assertAlmostEqual(float(model.objective(pairs, [b'a']*4)[0].detach()),0.)

    def test_existing_trainer(self):
        pairs = [(b'ab', b'bc'), (b'cd', b'de'), (b'ef', b'fg'), (b'gh', b'hi')]
        for kind in ('recurrent', 'attention'):
            torch.manual_seed(11)
            model = PairControl(kind)
            before = model.output.weight.detach().clone()
            result = train(model, pairs, seed=5, batch_size=2, epochs=2)
            self.assertEqual((result['steps'], result['observations'], result['exposure_bytes']), (4, 8, 32))
            self.assertLessEqual(abs(result['trainable_parameters'] - 1546), 50)
            self.assertFalse(torch.equal(before, model.output.weight))
            self.assertFalse(model.training)


if __name__ == '__main__':
    unittest.main()

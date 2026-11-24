"""Actual JEPA and bounded trainer DEV integration; fabricated observations only."""
import unittest
import torch
from learned_jepa import LearnedJEPA
from bounded_train import train
from anchor_adapter import AnchorTrainingAdapter


class AdapterTests(unittest.TestCase):
    def test_all_arms_both_heads(self):
        pairs = [(b'ab', b'bc'), (b'cd', b'de'), (b'ef', b'fg'), (b'gh', b'hi')]
        for head in ('mixture', 'pooled'):
            for mode in ('aligned', 'sham', 'off'):
                torch.manual_seed(11)
                model = LearnedJEPA(head)
                before = model.online.project.weight.detach().clone()
                adapter = AnchorTrainingAdapter(model, mode)
                result = train(adapter, pairs, seed=5, batch_size=4)
                self.assertEqual(result['steps'], 1)
                self.assertEqual(result['observations'], 4)
                self.assertEqual(result['trainable_parameters'], model.trainable_count())
                self.assertFalse(torch.equal(before, model.online.project.weight))
                self.assertTrue(all(p.grad is None for p in model.target.parameters()))
                self.assertFalse(model.training)

    def test_off_matches_unwrapped_update(self):
        pairs = [(b'ab', b'bc'), (b'cd', b'de')]
        torch.manual_seed(5)
        a = LearnedJEPA()
        b = LearnedJEPA()
        b.load_state_dict(a.state_dict())
        train(a, pairs, seed=5, batch_size=2)
        train(AnchorTrainingAdapter(b, 'off'), pairs, seed=5, batch_size=2)
        for k, v in a.state_dict().items():
            torch.testing.assert_close(v, b.state_dict()[k], rtol=0, atol=0)


if __name__ == '__main__':
    unittest.main()

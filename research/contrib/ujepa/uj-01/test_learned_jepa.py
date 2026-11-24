"""Fabricated engineering fixtures, not a scientific training workload."""
import copy
import unittest

import torch

from learned_jepa import LearnedJEPA, byte_signal


class LearnedJEPATests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(11)
        self.context = [b"abc", b"defg", b"123", b"4567"]
        self.future = [b"d", b"h", b"4", b"8"]

    def test_byte_signal(self):
        x, lengths = byte_signal([b"\\x00", b"\\xff\\x80"])
        self.assertEqual(lengths.tolist(), [1, 2])
        self.assertEqual(x[0, 0].tolist(), [-1]*8)
        self.assertEqual(x[1, 0].tolist(), [1]*8)
        self.assertEqual(x[1, 1].tolist(), [-1]*7+[1])

    def test_matched_capacity(self):
        a, b = LearnedJEPA("mixture"), LearnedJEPA("pooled")
        self.assertEqual(a.trainable_count(), b.trainable_count())
        self.assertEqual(list(a.state_dict()), list(b.state_dict()))
        b.load_state_dict(a.state_dict())
        for x, y in zip(a.predict(self.context), b.predict(self.context)):
            torch.testing.assert_close(x, y)

    def test_gradients_and_ema(self):
        for mode in ("mixture", "pooled"):
            model = LearnedJEPA(mode)
            original = copy.deepcopy(model.state_dict())
            loss, stats = model.objective(self.context, self.future)
            self.assertTrue(torch.isfinite(loss))
            loss.backward()
            for p in model.online.parameters():
                self.assertIsNotNone(p.grad)
                self.assertTrue(torch.isfinite(p.grad).all())
            self.assertTrue(all(p.grad is None for p in model.target.parameters()))
            optimizer = torch.optim.SGD(model.online.parameters(), lr=0.01)
            optimizer.step()
            self.assertTrue(any(not torch.equal(p, original["online."+k])
                                for k,p in model.online.state_dict().items()))
            for k,p in model.target.state_dict().items():
                torch.testing.assert_close(p, original["target."+k])
            model.update_target()
            for k,p in model.target.state_dict().items():
                expected = original["target."+k].lerp(
                    model.online.state_dict()[k], 1-model.ema)
                torch.testing.assert_close(p, expected)

    def test_padding_invariance_and_order(self):
        model = LearnedJEPA()
        a = model.encode([b"ab", b"cd"])
        b = model.encode([b"ab", b"longer"])
        torch.testing.assert_close(a[0], b[0])
        c = model.encode([b"ab", b"ba"])
        self.assertFalse(torch.allclose(c[0], c[1]))

    def test_collapse_diagnostic(self):
        model = LearnedJEPA()
        with torch.no_grad():
            for p in model.online.parameters():
                p.zero_()
        _, stats = model.objective(self.context, self.future)
        self.assertAlmostEqual(float(stats["variance_penalty"]), 0.19, places=5)
        self.assertAlmostEqual(float(stats["min_online_std"]), 0.01, places=5)

    def test_read_only_invalid_inputs(self):
        model = LearnedJEPA()
        original = copy.deepcopy(model.state_dict())
        model.objective(self.context, self.future)
        for bad in ([b"", b"a"], ["a", "b"], [b"a"*257, b"b"]):
            with self.assertRaises(ValueError):
                model.predict(bad)
        with self.assertRaises(ValueError):
            model.objective(self.context, self.future[:2])
        for k,p in model.state_dict().items():
            torch.testing.assert_close(p, original[k])


if __name__ == "__main__":
    unittest.main()

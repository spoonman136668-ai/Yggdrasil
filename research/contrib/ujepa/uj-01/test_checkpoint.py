import hashlib
import json
import unittest

import torch
from learned_jepa import LearnedJEPA
from checkpoint import snapshot, restore, representation_health


class CheckpointTests(unittest.TestCase):
    rows = [b'a', b'b', b'c', b'd']
    source, corpus = 'a'*64, 'b'*64

    def test_exact_roundtrip_after_update(self):
        for mode in ('mixture', 'pooled'):
            torch.manual_seed(11)
            model = LearnedJEPA(mode)
            opt = torch.optim.SGD([p for p in model.parameters() if p.requires_grad], lr=.01)
            loss, _ = model.objective(self.rows, self.rows[::-1])
            loss.backward()
            opt.step()
            model.update_target()
            raw, digest = snapshot(model, source=self.source, corpus=self.corpus)
            rng = torch.random.get_rng_state().clone()
            other = restore(raw, sha256=digest, source=self.source, corpus=self.corpus)
            self.assertTrue(torch.equal(rng, torch.random.get_rng_state()))
            self.assertFalse(other.training)
            self.assertEqual(other.mode, mode)
            self.assertTrue(all(not p.requires_grad for p in other.target.parameters()))
            for k,v in model.state_dict().items():
                self.assertTrue(torch.equal(v, other.state_dict()[k]))
            for a,b in zip(model.predict(self.rows), other.predict(self.rows)):
                torch.testing.assert_close(a,b,rtol=0,atol=0)
            self.assertEqual(snapshot(other, source=self.source, corpus=self.corpus), (raw,digest))

    def test_digest_and_provenance_rejection(self):
        raw, digest = snapshot(LearnedJEPA(), source=self.source, corpus=self.corpus)
        for data,sha,source,corpus in [(raw+b' ',digest,self.source,self.corpus),
                                      (raw,digest,'c'*64,self.corpus),
                                      (raw,digest,self.source,'c'*64)]:
            with self.assertRaises(ValueError):
                restore(data,sha256=sha,source=source,corpus=corpus)

    def test_bad_state(self):
        raw,_ = snapshot(LearnedJEPA(),source=self.source,corpus=self.corpus)
        for mode in ('key','shape','nan'):
            doc = json.loads(raw)
            key = next(iter(doc['state']))
            if mode == 'key':
                del doc['state'][key]
            else:
                doc['state'][key] = [float('nan') if mode == 'nan' else 1.0]
            data = json.dumps(doc).encode()
            with self.assertRaises(ValueError):
                restore(data,sha256=hashlib.sha256(data).hexdigest(),source=self.source,corpus=self.corpus)

    def test_raw_collapse_and_rank(self):
        model = LearnedJEPA()
        a = representation_health(model,self.rows)
        self.assertGreater(a['online']['mean_std'],0)
        self.assertLessEqual(a['online']['effective_rank'],3+1e-9)
        with torch.no_grad():
            for p in model.parameters():
                p.zero_()
        for stats in representation_health(model,self.rows).values():
            self.assertEqual(stats['min_std'],0)
            self.assertEqual(stats['mean_std'],0)
            self.assertEqual(stats['effective_rank'],0)

    def test_exact_collapse_variance_gradient(self):
        z = torch.zeros((4,8),requires_grad=True)
        penalty = torch.relu(.2-(z.var(dim=0,unbiased=False)+1e-4).sqrt()).mean()
        penalty.backward()
        self.assertAlmostEqual(float(penalty.detach()),.19,places=6)
        self.assertEqual(float(z.grad.abs().max()),0)


if __name__ == '__main__':
    unittest.main()

"""UJ-02 engineering fixtures only; fabricated byte pairs, no corpus."""
import hashlib
import json
import unittest

import torch

from session import Session


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.threads = torch.get_num_threads()
        self.deterministic = torch.are_deterministic_algorithms_enabled()
        self.warn_only = torch.is_deterministic_algorithms_warn_only_enabled()
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        self.rows = [(b'a',b'x'),(b'b',b'y'),(b'c',b'z'),(b'd',b'w')]
        self.source = 'a'*64
        self.plan = dict(seed=7,epochs=3,batch_size=2,rate=.001,max_steps=6,
                         max_bytes=24,mode='mixture',width=4,latent=2)

    def tearDown(self):
        torch.set_num_threads(self.threads)
        torch.use_deterministic_algorithms(self.deterministic, warn_only=self.warn_only)

    def start(self):
        return Session(self.rows,source=self.source,**self.plan)

    def load(self, raw, digest, **kw):
        args = dict(sha256=digest,pairs=self.rows,source=self.source,plan=self.plan)
        args.update(kw)
        return Session.load(raw,**args)

    def test_exact_resume(self):
        a,b = self.start(),self.start()
        a.advance(6)
        b.advance(3)
        raw,digest = b.save()
        c = self.load(raw,digest)
        self.assertEqual(c.save(),(raw,digest))
        c.advance(3)
        self.assertEqual(a.save(),c.save())
        self.assertEqual(c.exposure,24)
        with self.assertRaises(ValueError):
            c.advance()

    def test_identity_and_tamper(self):
        a = self.start()
        a.advance()
        raw,digest = a.save()
        with self.assertRaises(ValueError):
            self.load(raw+b' ',digest)
        with self.assertRaises(ValueError):
            self.load(raw,digest,source='b'*64)
        with self.assertRaises(ValueError):
            self.load(raw,digest,pairs=list(reversed(self.rows)))
        with self.assertRaises(ValueError):
            self.load(raw,digest,plan=dict(self.plan,epochs=2))
        for field,value in [('cursor',2),('exposure',0),('moments',{})]:
            d=json.loads(raw)
            d[field]=value
            changed=json.dumps(d).encode()
            with self.assertRaises(ValueError):
                self.load(changed,hashlib.sha256(changed).hexdigest())

    def test_zero_boundary_and_budget(self):
        a=self.start()
        raw,digest=a.save()
        self.assertEqual(self.load(raw,digest).save(),(raw,digest))
        with self.assertRaises(ValueError):
            Session(self.rows,source=self.source,**dict(self.plan,max_bytes=23))
        with self.assertRaises(ValueError):
            Session(self.rows,source=self.source,**dict(self.plan,max_steps=5))

    def test_failed_step_is_not_checkpointable(self):
        a=self.start()
        def fail(*args):
            raise RuntimeError('fixture failure')
        a.model.objective=fail
        with self.assertRaises(RuntimeError):
            a.advance()
        with self.assertRaises(RuntimeError):
            a.save()
        with self.assertRaises(RuntimeError):
            a.advance()


if __name__ == '__main__':
    unittest.main()

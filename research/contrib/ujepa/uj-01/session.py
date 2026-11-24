"""UJ-02 DEV: standalone CPU session with clean-boundary continuation.

No dataset acquisition, scientific dispatch, pickle, or Yggdrasil import.
A failed step poisons the session; external trial custody is caller-owned.
"""
import hashlib
import json
import math
import platform
import random
import sys

import torch

from checkpoint import snapshot, restore, _digest
from learned_jepa import LearnedJEPA

LIMIT = 16 * 1024 * 1024


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


def _environment():
    if (torch.get_num_threads() != 1 or not torch.are_deterministic_algorithms_enabled()
            or torch.is_deterministic_algorithms_warn_only_enabled()
            or torch.get_default_device().type != 'cpu' or torch.get_default_dtype() != torch.float32):
        raise ValueError('requires strict deterministic single-thread float32 CPU runtime')
    return dict(python=sys.version, torch=str(torch.__version__), machine=platform.machine(),
                system=platform.platform(), build=_hash(torch.__config__.show().encode()),
                mkldnn=torch.backends.mkldnn.enabled)


def _pairs(rows):
    if not isinstance(rows, (tuple, list)) or not 2 <= len(rows) <= 65536:
        raise ValueError('invalid pair count')
    result = []
    for row in rows:
        if not isinstance(row, (tuple, list)) or len(row) != 2 or any(
                type(v) is not bytes or not 1 <= len(v) <= 256 for v in row):
            raise ValueError('invalid observation')
        result.append(tuple(row))
    return tuple(result)


class Session:
    """One fixed corpus, model configuration and bounded schedule; no replay authority."""
    def __init__(self, pairs, *, source, seed, epochs=1, batch_size=8, rate=0.001,
                 max_steps=1024, max_bytes=2**20, mode='mixture', width=16, latent=8):
        self.source = _digest(source)
        self.environment = _environment()
        self.pairs = _pairs(pairs)
        if (type(seed) is not int or not 0 <= seed < 2**32
                or type(epochs) is not int or not 1 <= epochs <= 32
                or type(batch_size) is not int or not 2 <= batch_size <= 64
                or type(rate) not in (float, int) or not math.isfinite(rate) or not 0 < rate <= .01
                or type(max_steps) is not int or not 1 <= max_steps <= 4096
                or type(max_bytes) is not int or not 1 <= max_bytes <= 2**24
                or len(self.pairs) % batch_size):
            raise ValueError('invalid schedule')
        self.plan = dict(seed=seed, epochs=epochs, batch_size=batch_size, rate=rate,
                         max_steps=max_steps, max_bytes=max_bytes, mode=mode,
                         width=width, latent=latent)
        self.total = epochs * len(self.pairs) // batch_size
        if self.total > max_steps or epochs * sum(len(c)+len(y) for c,y in self.pairs) > max_bytes:
            raise ValueError('budget exceeded')
        self.corpus = _hash(_json([[c.hex(), y.hex()] for c,y in self.pairs]))
        with torch.random.fork_rng(devices=[]):
            torch.random.default_generator.manual_seed(seed)
            self.model = LearnedJEPA(mode=mode, width=width, latent=latent).cpu().float()
        self.params = dict((n,p) for n,p in self.model.named_parameters() if p.requires_grad)
        self.optimizer = torch.optim.AdamW(self.params.values(), lr=rate, weight_decay=0.,
                                           foreach=False, fused=False)
        self.cursor = 0
        self.exposure = 0
        self.poisoned = False
        self._epoch, self._order = None, ()
        self.model.eval()

    def _batch(self, step):
        count = len(self.pairs) // self.plan['batch_size']
        epoch, offset = divmod(step, count)
        if epoch != self._epoch:
            order = list(range(len(self.pairs)))
            random.Random(self.plan['seed'] + epoch).shuffle(order)
            self._epoch, self._order = epoch, tuple(order)
        k = self.plan['batch_size']
        return [self.pairs[i] for i in self._order[offset*k:(offset+1)*k]]

    def advance(self, count=1):
        if self.poisoned or _environment() != self.environment:
            raise RuntimeError('session invalid')
        if type(count) is not int or not 1 <= count <= self.total-self.cursor:
            raise ValueError('schedule exhausted or invalid count')
        self.poisoned = True
        self.model.train()
        for _ in range(count):
            batch = self._batch(self.cursor)
            c,y = zip(*batch)
            self.optimizer.zero_grad(set_to_none=True)
            loss, metrics = self.model.objective(c,y)
            std = float(metrics['min_online_std'])
            if not torch.isfinite(loss) or not math.isfinite(std) or std < 0:
                raise RuntimeError('invalid objective')
            loss.backward()
            if any(p.grad is None or not torch.isfinite(p.grad).all() for p in self.params.values()):
                raise RuntimeError('invalid gradient')
            self.optimizer.step()
            self.model.update_target()
            if any(not torch.isfinite(p).all() for p in self.model.parameters()):
                raise RuntimeError('invalid weights')
            if any(not torch.isfinite(v).all() for st in self.optimizer.state.values() for v in st.values()):
                raise RuntimeError('invalid optimizer')
            self.cursor += 1
            self.exposure += sum(len(c)+len(y) for c,y in batch)
        self.optimizer.zero_grad(set_to_none=True)
        self.model.eval()
        self.poisoned = False

    def save(self):
        if self.poisoned or _environment() != self.environment:
            raise RuntimeError('invalid checkpoint boundary')
        weights, digest = snapshot(self.model, source=self.source, corpus=self.corpus)
        moments = {}
        for n,p in self.params.items():
            st = self.optimizer.state.get(p, {})
            if st:
                if set(st) != {'step','exp_avg','exp_avg_sq'} or float(st['step']) != self.cursor:
                    raise ValueError('optimizer state mismatch')
                moments[n] = {k:v.detach().cpu().tolist() for k,v in st.items()}
        raw = _json(dict(schema='ujepa.session.v1', source=self.source, corpus=self.corpus,
                         environment=self.environment, plan=self.plan, cursor=self.cursor,
                         exposure=self.exposure, weights=weights.decode(), weights_sha256=digest,
                         moments=moments))
        if len(raw) > LIMIT:
            raise ValueError('checkpoint size exceeded')
        return raw, _hash(raw)

    @classmethod
    def load(cls, raw, *, sha256, pairs, source, plan):
        if type(raw) is not bytes or not 1 <= len(raw) <= LIMIT or _hash(raw) != _digest(sha256):
            raise ValueError('checkpoint digest or size')
        d = json.loads(raw)
        if (type(d) is not dict or set(d) != {'schema','source','corpus','environment','plan',
                'cursor','exposure','weights','weights_sha256','moments'}
                or d['schema'] != 'ujepa.session.v1' or d['source'] != _digest(source)
                or _json(d['plan']) != _json(plan)):
            raise ValueError('checkpoint identity')
        s = cls(pairs, source=source, **plan)
        if d['corpus'] != s.corpus or d['environment'] != s.environment:
            raise ValueError('corpus or runtime drift')
        cursor = d['cursor']
        if type(cursor) is not int or not 0 <= cursor <= s.total:
            raise ValueError('invalid cursor')
        exposure = sum(len(c)+len(y) for i in range(cursor) for c,y in s._batch(i))
        if type(d['exposure']) is not int or d['exposure'] != exposure:
            raise ValueError('exposure mismatch')
        restored = restore(d['weights'].encode(), sha256=d['weights_sha256'],
                           source=s.source, corpus=s.corpus)
        if (restored.mode != s.model.mode or restored.latent != s.model.latent
                or restored.ema != s.model.ema
                or restored.online.recurrent.hidden_size != s.model.online.recurrent.hidden_size):
            raise ValueError('model config mismatch')
        s.model.load_state_dict(restored.state_dict(), strict=True)
        moments = d['moments']
        if type(moments) is not dict or set(moments) != (set(s.params) if cursor else set()):
            raise ValueError('optimizer names mismatch')
        for n,st in moments.items():
            p = s.params[n]
            if type(st) is not dict or set(st) != {'step','exp_avg','exp_avg_sq'}:
                raise ValueError('optimizer fields')
            if type(st['step']) not in (float,int) or st['step'] != cursor:
                raise ValueError('optimizer cursor')
            state = {'step': torch.tensor(float(cursor), dtype=torch.float32)}
            for k in ('exp_avg','exp_avg_sq'):
                v = torch.tensor(st[k], dtype=torch.float32)
                if v.shape != p.shape or not torch.isfinite(v).all() or (k=='exp_avg_sq' and (v<0).any()):
                    raise ValueError('optimizer tensor')
                state[k] = v
            s.optimizer.state[p] = state
        s.cursor, s.exposure = cursor, exposure
        return s

"""DEV weight snapshot and representation diagnostics; not training resume."""
import hashlib
import json
import re

import torch
from learned_jepa import LearnedJEPA


MAX_BYTES = 8 * 1024 * 1024


def _digest(value):
    if type(value) is not str or not re.fullmatch(r'[0-9a-f]{64}', value):
        raise ValueError('expected SHA-256')
    return value


def snapshot(model, *, source, corpus):
    config = dict(mode=model.mode, width=model.online.recurrent.hidden_size,
                  latent=model.latent, ema=model.ema)
    state = {}
    for name, value in model.state_dict().items():
        if value.dtype != torch.float32 or not torch.isfinite(value).all():
            raise ValueError('only finite float32 state is supported')
        state[name] = value.detach().cpu().tolist()
    raw = json.dumps(dict(schema='ujepa.weights.v1', source=_digest(source),
                          corpus=_digest(corpus), config=config, state=state),
                     sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    if len(raw) > MAX_BYTES:
        raise ValueError('snapshot size exceeded')
    return raw, hashlib.sha256(raw).hexdigest()


def restore(raw, *, sha256, source, corpus):
    if type(raw) is not bytes or not 1 <= len(raw) <= MAX_BYTES:
        raise ValueError('invalid snapshot bytes')
    if hashlib.sha256(raw).hexdigest() != _digest(sha256):
        raise ValueError('snapshot digest mismatch')
    doc = json.loads(raw)
    if (type(doc) is not dict or set(doc) != {'schema','source','corpus','config','state'}
            or doc['schema'] != 'ujepa.weights.v1' or doc['source'] != _digest(source)
            or doc['corpus'] != _digest(corpus)):
        raise ValueError('snapshot identity mismatch')
    config = doc['config']
    if type(config) is not dict or set(config) != {'mode','width','latent','ema'}:
        raise ValueError('invalid snapshot config')
    with torch.random.fork_rng(devices=[]):
        model = LearnedJEPA(**config).cpu().float()
    state = doc['state']
    expected = model.state_dict()
    if type(state) is not dict or set(state) != set(expected):
        raise ValueError('snapshot state keys mismatch')
    tensors = {}
    for name, value in state.items():
        tensor = torch.tensor(value, dtype=torch.float32)
        if tensor.shape != expected[name].shape or not torch.isfinite(tensor).all():
            raise ValueError('invalid snapshot tensor')
        tensors[name] = tensor
    model.load_state_dict(tensors, strict=True)
    return model.eval()


@torch.no_grad()
def representation_health(model, rows):
    """Raw dispersion and effective rank, with no epsilon variance floor."""
    result = {}
    for name, target in [('online', False), ('target', True)]:
        z = model.encode(rows, target=target).detach().cpu().double()
        if not torch.isfinite(z).all():
            raise ValueError('nonfinite representation')
        centered = z - z.mean(dim=0)
        std = centered.square().mean(dim=0).sqrt()
        energy = torch.linalg.svdvals(centered).square()
        total = energy.sum()
        rank = float(total.square() / energy.square().sum()) if total > 0 else 0.0
        result[name] = dict(min_std=float(std.min()), mean_std=float(std.mean()),
                            effective_rank=rank, rank_ceiling=min(len(rows)-1,z.shape[1]))
    return result

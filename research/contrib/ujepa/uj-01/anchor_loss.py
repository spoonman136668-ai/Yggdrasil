"""DEV input-derived anchors; no labels, vocabulary, or learned parameters."""
import torch
from torch.nn import functional as F


def anchors(rows, latent, *, device=None, dtype=torch.float32):
    """Mean bit channels in four relative-position bins; no corpus statistics."""
    if type(latent) is not int or not 2 <= latent <= 32:
        raise ValueError('invalid latent size')
    if not isinstance(rows, (list, tuple)) or not 2 <= len(rows) <= 64:
        raise ValueError('invalid batch')
    result = []
    for row in rows:
        if type(row) is not bytes or not 1 <= len(row) <= 256:
            raise ValueError('invalid signal')
        bins = [[] for _ in range(4)]
        for i, value in enumerate(row):
            bins[4*i//len(row)].append(value)
        features = []
        # Interleave bins within each bit so small latents retain position info.
        for k in range(8):
            for part in bins:
                features.append(sum(2*((v >> k) & 1)-1 for v in part)/len(part)
                                if part else 0.)
        result.append(features[:latent])
    return torch.tensor(result, device=device, dtype=dtype)


def anchor_loss(z, rows, mode='aligned'):
    """Matched work: aligned, cyclic-misaligned sham, or zero-weight control."""
    if mode not in ('aligned', 'sham', 'off'):
        raise ValueError('invalid anchor mode')
    if z.ndim != 2 or len(rows) != z.shape[0] or not torch.isfinite(z).all():
        raise ValueError('invalid representation')
    target = anchors(rows, z.shape[1], device=z.device, dtype=z.dtype)
    if mode == 'sham':
        target = target.roll(1, dims=0)
    loss = F.mse_loss(z, target)
    return loss * (0. if mode == 'off' else 1.)


def objective(model, context, future, mode='aligned', weight=0.25):
    """DEV explicit objective adapter, not an implicit checkpoint change."""
    if type(weight) not in (int, float) or not 0 <= weight <= 1:
        raise ValueError('invalid anchor weight')
    base, stats = model.objective(context, future)
    aux = (anchor_loss(model.encode(context), context, mode) +
           anchor_loss(model.encode(future), future, mode))/2
    return base + weight*aux, dict(stats, anchor_loss=aux.detach())

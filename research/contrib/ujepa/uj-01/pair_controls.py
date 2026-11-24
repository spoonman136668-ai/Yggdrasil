"""DEV recurrent and attention comparison models, same raw positive pairs."""
import torch
from torch import nn
from torch.nn import functional as F


class PairControl(nn.Module):
    def __init__(self, kind, width=None, latent=8):
        super().__init__()
        if width is None:
            width = 17 if kind == 'recurrent' else 12
        if kind not in ('recurrent', 'attention') or type(width) is not int or not 4 <= width <= 64 or (kind == 'attention' and width % 2):
            raise ValueError('control configuration')
        if type(latent) is not int or not 2 <= latent <= 32:
            raise ValueError('latent size')
        self.kind = kind
        if kind == 'recurrent':
            self.encoder = nn.GRU(8, width, batch_first=True)
        else:
            self.input = nn.Linear(9, width)
            self.encoder = nn.TransformerEncoderLayer(width, 2, 2*width, dropout=0., batch_first=True)
        self.output = nn.Linear(width, latent)

    def encode(self, rows):
        if not 1 <= len(rows) <= 64 or any(type(r) is not bytes or not 1 <= len(r) <= 256 for r in rows):
            raise ValueError('signal bounds')
        lengths = torch.tensor([len(r) for r in rows], dtype=torch.long)
        n = int(lengths.max())
        signal = torch.zeros(len(rows), n, 8, device=self.output.weight.device, dtype=self.output.weight.dtype)
        for i, row in enumerate(rows):
            data = torch.tensor(list(row), device=signal.device)
            bits = (data[:, None] >> torch.arange(8, device=signal.device)) & 1
            signal[i, :len(row)] = 2*bits-1
        if self.kind == 'recurrent':
            packed = nn.utils.rnn.pack_padded_sequence(signal, lengths, batch_first=True, enforce_sorted=False)
            _, h = self.encoder(packed)
            pooled = h[-1]
        else:
            steps = torch.arange(n, device=signal.device)[None, :]
            mask = steps >= lengths.to(signal.device)[:, None]
            pos = (steps.expand(len(rows), n) / 255).to(signal.dtype)
            h = self.encoder(self.input(torch.cat([signal, pos[..., None]], -1)), src_key_padding_mask=mask)
            pooled = h.masked_fill(mask[..., None], 0).sum(1) / lengths.to(signal.device)[:, None]
        return self.output(pooled).tanh()

    def objective(self, context, future):
        if len(context) != len(future) or len(context) < 2:
            raise ValueError('paired batch')
        x, y = self.encode(context), self.encode(future)
        scores = x @ y.T
        positive = torch.tensor([[a == b for b in future] for a in future], device=x.device)
        loss = (scores.logsumexp(1) - scores.masked_fill(~positive, -torch.inf).logsumexp(1)).mean()
        return loss, {'min_online_std': x.detach().std(dim=0, unbiased=False).min()}

    def update_target(self):
        """No target encoder in these controls; trainer interface only."""

    @torch.no_grad()
    def scores(self, context, options):
        return (self.encode(options) @ self.encode([context])[0]).cpu().tolist()

"""UJ-01B DEV: learned raw-byte signal encoder and matched latent heads."""
import copy
import math

import torch
from torch import nn
from torch.nn import functional as F


def byte_signal(rows):
    """Bit planes of raw bytes; no vocabulary, token IDs or embedding lookup."""
    if not isinstance(rows, (list, tuple)) or not 2 <= len(rows) <= 64:
        raise ValueError("batch must contain 2..64 byte strings")
    if any(type(r) is not bytes or not 1 <= len(r) <= 256 for r in rows):
        raise ValueError("each signal must contain 1..256 bytes")
    lengths = torch.tensor([len(r) for r in rows], dtype=torch.long)
    signal = torch.zeros(len(rows), int(lengths.max()), 8)
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            signal[i, j] = torch.tensor([2 * ((value >> k) & 1) - 1
                                         for k in range(8)])
    return signal, lengths


class SignalEncoder(nn.Module):
    def __init__(self, width, latent):
        super().__init__()
        self.recurrent = nn.GRU(8, width, batch_first=True)
        self.project = nn.Linear(width, latent)

    def forward(self, signal, lengths):
        packed = nn.utils.rnn.pack_padded_sequence(
            signal, lengths.cpu(), batch_first=True, enforce_sorted=False)
        _, state = self.recurrent(packed)
        return self.project(state[-1]).tanh()


class LearnedJEPA(nn.Module):
    """EMA target; online variance pressure; equal head parameter budgets."""
    def __init__(self, mode="mixture", width=16, latent=8, ema=0.99):
        super().__init__()
        if mode not in ("mixture", "pooled"):
            raise ValueError("invalid mode")
        if type(width) is not int or not 4 <= width <= 64:
            raise ValueError("invalid width")
        if type(latent) is not int or not 2 <= latent <= 32:
            raise ValueError("invalid latent")
        if not 0 < ema < 1:
            raise ValueError("invalid EMA")
        self.mode, self.latent, self.ema = mode, latent, ema
        self.online = SignalEncoder(width, latent)
        self.target = copy.deepcopy(self.online).requires_grad_(False)
        self.head = nn.Linear(latent, 2 * (latent + 1))

    def encode(self, rows, target=False):
        signal, lengths = byte_signal(rows)
        encoder = self.target if target else self.online
        return encoder(signal.to(self.head.weight), lengths)

    def _components(self, z):
        raw = self.head(z).reshape(-1, 2, self.latent + 1)
        return raw[..., 0].log_softmax(dim=1), raw[..., 1:].tanh()

    def _distribution(self, z):
        logp, means = self._components(z)
        if self.mode == "pooled":
            means = (logp.exp()[..., None] * means).sum(1, keepdim=True)
            logp = torch.zeros_like(logp[:, :1])
        return logp, means

    def predict(self, context):
        """Log weights and means of the actual predictive distribution."""
        return self._distribution(self.encode(context))

    def objective(self, context, future):
        if len(context) != len(future):
            raise ValueError("context/future batch mismatch")
        z = self.encode(context)
        logp, means = self._distribution(z)
        with torch.no_grad():
            y = self.encode(future, target=True)
        sigma = 0.5
        constant = self.latent * math.log(sigma * math.sqrt(2 * math.pi))
        nll = -torch.logsumexp(logp - constant -
            (means - y[:, None]).square().sum(-1) / (2*sigma**2), dim=1)
        # Equal regularizer and information for both heads. No target gradient.
        views = (z, self.encode(future))
        stds = [torch.sqrt(v.var(dim=0, unbiased=False) + 1e-4)
                for v in views]
        penalty = sum(F.relu(0.2-s).mean() for s in stds) / 2
        return nll.mean() + penalty, {
            "nll": nll.mean().detach(),
            "variance_penalty": penalty.detach(),
            "min_online_std": torch.stack(stds).min().detach(),
        }

    @torch.no_grad()
    def update_target(self):
        """Call explicitly once after a successful online optimizer step."""
        for target, online in zip(self.target.parameters(),
                                  self.online.parameters()):
            target.lerp_(online, 1-self.ema)

    def trainable_count(self):
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

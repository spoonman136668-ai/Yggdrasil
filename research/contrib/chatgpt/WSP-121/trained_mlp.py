"""WSP-121 conventional gradient-trained CPU control; SOURCE-SAFE ONLY.

Train on verified (3-bit public context, selected-route label) pairs. No
worlds, protected seeds, original cohort, held endpoints, or oracle access.
No held-label or transfer-label tuning: selection is training-loss only.
"""
from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

OBSERVATION_LIMIT = 288
SEEDS = (121951, 121952, 121953)  # optimization seeds, never world IDs
MAX_EPOCHS = 1600
LR = 0.03
LOSS_CEILING = 0.005
REQUIRED_TORCH = "2.10.0"


def _torch():
    import torch
    if torch.__version__.split("+")[0] != REQUIRED_TORCH:
        raise RuntimeError("WSP121_MLP_TORCH_VERSION_MISMATCH")
    return torch


def _validate(evidence):
    if type(evidence) not in (list, tuple) or not (1 <= len(evidence) <= OBSERVATION_LIMIT):
        raise ValueError("WSP121_MLP_EVIDENCE_LENGTH")
    observed = {}
    for pair in evidence:
        if type(pair) not in (list, tuple) or len(pair) != 2:
            raise ValueError("WSP121_MLP_INVALID_EVIDENCE")
        context, route = pair
        if (type(context) is not int or not 0 <= context < 8 or
                type(route) is not int or route not in (0, 1)):
            raise ValueError("WSP121_MLP_INVALID_EVIDENCE")
        if context in observed and observed[context] != route:
            raise ValueError("WSP121_MLP_CONTRADICTORY_EVIDENCE")
        observed[context] = route


def _features(torch, contexts):
    contexts = tuple(contexts)
    if any(type(c) is not int or not 0 <= c < 8 for c in contexts):
        raise ValueError("WSP121_MLP_INVALID_CONTEXT")
    return torch.tensor([[(c >> bit) & 1 for bit in range(3)]
                         for c in contexts], dtype=torch.float64)


def _model(torch):
    from torch import nn
    return nn.Sequential(nn.Linear(3, 32), nn.Tanh(),
                         nn.Linear(32, 32), nn.Tanh(), nn.Linear(32, 2)).double()


@dataclass
class TrainedMLP:
    network: object | None
    converged: bool
    training_accuracy: float
    training_loss: float
    winning_seed: int | None
    epochs_by_seed: dict
    wall_seconds: float
    parameter_count: int
    evidence_count: int

    def infer_routes(self, contexts):
        contexts = tuple(contexts)
        features = _features(_torch(), contexts)
        if not self.converged or self.network is None:
            return tuple(None for _ in contexts)
        torch = _torch()
        with torch.no_grad():
            self.network.eval()
            return tuple(int(x) for x in self.network(features).argmax(1).tolist())


def train_conventional_mlp(evidence):
    """Fully train three pinned seeds, select only on verified training loss.

    Nonconvergence is an INVALID science control, never a numeric victory.
    No independent world/held source is opened by this function.
    """
    _validate(evidence)
    torch = _torch()
    from torch.nn import functional as F
    features = _features(torch, (c for c, _ in evidence))
    labels = torch.tensor([r for _, r in evidence], dtype=torch.long)
    start = perf_counter()
    old_threads = torch.get_num_threads()
    old_determinism = torch.are_deterministic_algorithms_enabled()
    best = None
    best_loss = float("inf")
    winner = None
    records = {}
    parameters = 0
    try:
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        with torch.random.fork_rng(devices=[]):
            for seed in SEEDS:
                torch.manual_seed(seed)
                net = _model(torch)
                parameters = sum(p.numel() for p in net.parameters())
                optimizer = torch.optim.Adam(net.parameters(), lr=LR)
                for epoch in range(1, MAX_EPOCHS + 1):
                    net.train()
                    optimizer.zero_grad(set_to_none=True)
                    logits = net(features)
                    loss = F.cross_entropy(logits, labels)
                    loss.backward()
                    optimizer.step()
                    with torch.no_grad():
                        logits = net(features)
                        final_loss = F.cross_entropy(logits, labels).item()
                        final_acc = (logits.argmax(1) == labels).double().mean().item()
                    if final_acc == 1.0 and final_loss <= LOSS_CEILING:
                        break
                passed = final_acc == 1.0 and final_loss <= LOSS_CEILING
                records[seed] = dict(epochs=epoch, loss=final_loss,
                                     training_accuracy=final_acc, converged=passed)
                if passed and (final_loss, seed) < (best_loss, winner or seed):
                    best = net
                    best_loss = final_loss
                    winner = seed
    finally:
        torch.use_deterministic_algorithms(old_determinism)
        torch.set_num_threads(old_threads)
    return TrainedMLP(best, best is not None,
                      1.0 if best is not None else 0.0,
                      best_loss, winner, records, perf_counter() - start,
                      parameters, len(evidence))

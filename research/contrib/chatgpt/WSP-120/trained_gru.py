"""WSP-120 fully trained, source-safe conventional GRU control.

Comparator only, not a Yggdrasil substrate. Receives the public graph and
verified source observations, never oracle/held-out endpoints while training.
"""
from __future__ import annotations

from dataclasses import dataclass
import time

N, R = 64, 6
SEEDS = (120901, 120902, 120903)  # Optimization seeds; NOT new world cohorts.
MAX_EPOCHS = 2000
LR = 0.01
TRAIN_LOSS_CEILING = 0.01
REQUIRED_TORCH = "2.10.0"


def _torch():
    import torch
    if torch.__version__.split("+")[0] != REQUIRED_TORCH:
        raise RuntimeError("WSP120_GRU_TORCH_VERSION_MISMATCH")
    return torch


def _validate(graph, observations):
    if type(graph) not in (list, tuple) or len(graph) != R:
        raise ValueError("WSP120_GRU_INVALID_GRAPH")
    for rel in graph:
        if type(rel) is not dict or any(
                type(k) is not int or type(v) is not int
                or not (0 <= k < N and 0 <= v < N)
                for k, v in rel.items()):
            raise ValueError("WSP120_GRU_INVALID_GRAPH")
    if type(observations) not in (tuple, list) or len(observations) > 32:
        raise ValueError("WSP120_GRU_INVALID_EVIDENCE")
    seen = set()
    for pair in observations:
        if type(pair) not in (tuple, list) or len(pair) != 2:
            raise ValueError("WSP120_GRU_INVALID_EVIDENCE")
        subject, outcome = pair
        if (type(subject) is not int or type(outcome) is not int
                or not (0 <= subject < N and 0 <= outcome < N)
                or subject in seen):
            raise ValueError("WSP120_GRU_INVALID_EVIDENCE")
        seen.add(subject)


def _features(torch, graph, subjects):
    from torch.nn import functional as F
    names = tuple(subjects)
    if any(type(s) is not int or not 0 <= s < N for s in names):
        raise ValueError("WSP120_GRU_INVALID_SUBJECT")
    if not names:
        return torch.empty((0, R, 2*N+R), dtype=torch.float32)
    subject_onehot = F.one_hot(torch.tensor(names), num_classes=N).float()
    rows = torch.tensor(
        [[rel.get(i, -1) for i in range(N)] for rel in graph],
        dtype=torch.float32)
    edge_map = (rows + 1.0)/65.0  # Zero is UNKNOWN; unseen edges never inferred.
    return torch.cat((
        subject_onehot[:, None].expand(-1, R, -1),
        edge_map[None].expand(len(names), -1, -1),
        torch.eye(R)[None].expand(len(names), -1, -1)), dim=2)


def _model(torch):
    from torch import nn

    class EndpointGRU(nn.Module):
        def __init__(self):
            super().__init__()
            self.recurrent = nn.GRU(
                input_size=2*N+R, hidden_size=64, batch_first=True)
            self.readout = nn.Linear(64, N)

        def forward(self, x):
            _, h = self.recurrent(x)
            return self.readout(h[-1])

    return EndpointGRU()


@dataclass
class TrainedGRUResult:
    graph: tuple
    network: object | None
    converged: bool
    training_accuracy: float
    training_loss: float
    winning_seed: int | None
    epochs_by_seed: dict
    wall_seconds: float
    parameter_count: int

    def infer(self, subjects):
        subjects = tuple(subjects)
        if not self.converged or self.network is None:
            return tuple(None for _ in subjects)
        torch = _torch()
        with torch.no_grad():
            logits = self.network(_features(torch, self.graph, subjects))
            return tuple(int(v) for v in logits.argmax(1).tolist())


def train_conventional_gru(graph, observations):
    """Fit frozen three-seed conventional GRU; select on training loss ONLY.

    Nonconvergence INVALIDATES scientific comparison rather than awarding a
    victory to direct numerical memory. The caller must supply verified
    source responses and score held-out subjects only after selection.
    """
    torch = _torch()
    from torch.nn import functional as F
    _validate(graph, observations)
    if not observations:
        return TrainedGRUResult(
            tuple(dict(g) for g in graph), None, False,
            0.0, float("nan"), None, {}, 0.0, 0)
    x = _features(torch, graph, (s for s, _ in observations))
    y = torch.tensor([v for _, v in observations], dtype=torch.long)
    best, best_loss, best_seed = None, float("inf"), None
    best_train_accuracy = 0.0
    params, records = 0, {}
    wall_start = time.monotonic()
    old_threads = torch.get_num_threads()
    try:
        torch.set_num_threads(1)
        with torch.random.fork_rng(devices=[]):
            for seed in SEEDS:
                torch.manual_seed(seed)
                network = _model(torch)
                params = sum(p.numel() for p in network.parameters())
                optimizer = torch.optim.Adam(network.parameters(), lr=LR)
                converged = False
                for epoch in range(1, MAX_EPOCHS+1):
                    network.train()
                    optimizer.zero_grad(set_to_none=True)
                    logits = network(x)
                    loss = F.cross_entropy(logits, y)
                    loss.backward()
                    optimizer.step()
                    with torch.no_grad():
                        logits = network(x)
                        checked_loss = F.cross_entropy(logits, y).item()
                        accuracy = (logits.argmax(1) == y).float().mean().item()
                    if accuracy == 1.0 and checked_loss <= TRAIN_LOSS_CEILING:
                        converged = True
                        break
                records[seed] = {
                    "epochs": epoch, "loss": checked_loss,
                    "training_accuracy": accuracy, "converged": converged}
                if converged and (checked_loss, seed) < (best_loss, best_seed or seed):
                    best = network
                    best_loss, best_seed = checked_loss, seed
                    best_train_accuracy = accuracy
    finally:
        torch.set_num_threads(old_threads)
    return TrainedGRUResult(
        tuple(dict(g) for g in graph), best, best is not None,
        best_train_accuracy, best_loss, best_seed, records,
        time.monotonic()-wall_start, params)

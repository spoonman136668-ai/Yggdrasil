"""FKP-17 independent genuinely gradient-trained recurrent action-effect control.

A 32-hidden-unit GRU predicts each of eight NEXT public register values from
up to 16 *previously observed* public transitions plus current state/action.
The fully qualifying mode trains two distinct seeds through 24 COMPLETE epochs
each on all 32,768 observed foundation facts and selects a checkpoint using
public source-safe VAL only. No hidden law, future action reward, or oracle.
Source-safe smoke mode is explicitly nonqualifying and never scientific proof.
"""
from __future__ import annotations

from hashlib import sha256
import copy
import json
import math
import struct
import time

from strong_controls import _row, _state, _receipt_bytes, FOUNDATION_RECORDS, MAX_MEMORY

SEEDS = (1515, 2626)
EPOCHS = 24
HIDDEN = 32
INPUT = 27
OUTPUT = 8 * 16
BATCH = 128
LEARNING_RATE = 0.003
MAX_HISTORY = 16


def _torch():
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("FKP17_RECURRENT_TORCH_CPU_REQUIRED") from exc
    return torch


def _vector(before, action, after=None, reward=0.0, done=False, current=False):
    a = _state(before)
    if type(action) is not int or not 0 <= action < 8:
        raise ValueError("FKP17_RECURRENT_ACTION")
    output = [value / 15.0 for value in a]
    output.extend([(value / 15.0) for value in _state(after)] if after is not None
                  else [0.0] * 8)
    output.extend(float(i == action) for i in range(8))
    output.extend((float(reward), float(done), float(current)))
    if len(output) != INPUT:
        raise AssertionError("FKP17_RECURRENT_INPUT_DIMENSIONS")
    return output


def _sequence(before, action, history):
    if len(history) > MAX_HISTORY:
        raise ValueError("FKP17_RECURRENT_HISTORY_BUDGET")
    prior = []
    for old in history:
        # Every old record was already publicly observed. No future outcomes.
        b, a, r, after, done = old
        prior.append(_vector(b, a, after, r, done, False))
    inputs = prior[-MAX_HISTORY:] + [_vector(before, action, current=True)]
    inputs = [[0.0] * INPUT] * (MAX_HISTORY + 1 - len(inputs)) + inputs
    return inputs


def _public_training(rows):
    # Owns no source generator. Callers supply only public streams.
    examples = []
    h = sha256()
    for record in rows:
        verified = _row(record)
        h.update(_receipt_bytes(verified))
        before, action, after, reward, done, history = verified
        examples.append((_sequence(before, action, history), tuple(after)))
    return examples, h.hexdigest()


def _network(torch):
    class RecurrentRegisterPredictor(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.gru = torch.nn.GRU(INPUT, HIDDEN, batch_first=True)
            self.project = torch.nn.Linear(HIDDEN, OUTPUT)

        def forward(self, x):
            # All inputs are past, except this action with a blanked outcome.
            hidden, _ = self.gru(x)
            return self.project(hidden[:, -1, :]).reshape(-1, 8, 16)
    return RecurrentRegisterPredictor()


def _tensors(torch, rows):
    import torch as _t  # locally pinned by caller workflow, not source owner
    x = _t.tensor([v[0] for v in rows], dtype=_t.float32, device="cpu")
    y = _t.tensor([v[1] for v in rows], dtype=_t.long, device="cpu")
    return x, y


def _validation_loss(torch, model, data):
    model.eval()
    x, y = data
    total, n = 0.0, 0
    with torch.no_grad():
        for start in range(0, len(x), BATCH):
            inp = x[start:start + BATCH]
            actual = y[start:start + BATCH]
            logits = model(inp)
            loss = torch.nn.functional.cross_entropy(
                logits.reshape(-1, 16), actual.reshape(-1), reduction="sum")
            total += float(loss)
            n += actual.numel()
    if not n:
        raise ValueError("FKP17_RECURRENT_EMPTY_VALIDATION")
    return total / n


class FullyTrainedRecurrent:
    """Separate frozen-model, public-history-only recurrent reference."""
    def __init__(self):
        self._net = None
        self._torch = None
        self._digest = ""
        self._observed_count = 0
        self._history = []
        self.training_receipt = None
        self.foundation_count = 0
        self.world_count = 0

    @property
    def foundation_sha256(self):
        return self._digest

    @property
    def learned_bytes(self):
        if self._net is None:
            return 0
        return sum(p.numel() * p.element_size() for p in self._net.parameters())

    def fit_public_foundation(self, public_rows, validation_rows):
        examples, digest = _public_training(public_rows)
        validation, _ = _public_training(validation_rows)
        if len(examples) != FOUNDATION_RECORDS or len(validation) == 0:
            raise ValueError("FKP17_RECURRENT_FULL_FOUNDATION_AND_VALIDATION_REQUIRED")
        return self._fit(examples, validation, digest, seeds=SEEDS, epochs=EPOCHS,
                         scientific_qualification_candidate=True)

    def _fit(self, examples, validation, digest, *, seeds, epochs,
             scientific_qualification_candidate):
        torch = _torch()
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        if self._net is not None:
            raise ValueError("FKP17_RECURRENT_DOUBLE_FIT")
        if not examples or not validation:
            raise ValueError("FKP17_RECURRENT_EMPTY_SOURCE")
        if scientific_qualification_candidate and (
                len(examples) != FOUNDATION_RECORDS or
                seeds != SEEDS or epochs != EPOCHS):
            raise ValueError("FKP17_RECURRENT_FROZEN_FIT_MISMATCH")
        if type(epochs) is not int or epochs < 1 or epochs > EPOCHS:
            raise ValueError("FKP17_RECURRENT_EPOCHS_INVALID")
        train = _tensors(torch, examples)
        val = _tensors(torch, validation)
        best, best_state, selected = float("inf"), None, None
        trained = []
        started = time.perf_counter()
        for seed in seeds:
            if type(seed) is not int:
                raise ValueError("FKP17_RECURRENT_SEED")
            torch.manual_seed(seed)
            net = _network(torch).to("cpu")
            optim = torch.optim.Adam(net.parameters(), lr=LEARNING_RATE)
            generator = torch.Generator(device="cpu")
            generator.manual_seed(seed)
            epoch_receipts = []
            # No early stop: COMPLETE 24 full epochs for EACH seed, even when
            # an earlier checkpoint has better VAL loss.
            for epoch in range(1, epochs + 1):
                net.train()
                perm = torch.randperm(len(train[0]), generator=generator)
                for start in range(0, len(perm), BATCH):
                    select = perm[start:start + BATCH]
                    x, y = train[0][select], train[1][select]
                    logits = net(x)
                    loss = torch.nn.functional.cross_entropy(
                        logits.reshape(-1, 16), y.reshape(-1))
                    optim.zero_grad(set_to_none=True)
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
                    optim.step()
                val_loss = _validation_loss(torch, net, val)
                epoch_receipts.append(val_loss)
                if val_loss < best:
                    best = val_loss
                    best_state = {k: v.detach().clone() for k, v in net.state_dict().items()}
                    selected = (seed, epoch)
            trained.append({"seed": seed, "complete_epochs": epochs,
                            "last_validation_crossentropy": epoch_receipts[-1]})
        assert best_state is not None and selected is not None
        torch.manual_seed(selected[0])
        winner = _network(torch).to("cpu")
        winner.load_state_dict(best_state)
        winner.eval()
        bytes_used = sum(p.numel() * p.element_size() for p in winner.parameters())
        if bytes_used > MAX_MEMORY:
            raise ValueError("FKP17_RECURRENT_PARAMETER_CAPACITY")
        self._net, self._torch = winner, torch
        self._digest = digest
        self.foundation_count = len(examples)
        self.training_receipt = {
            "status": "FULL_TRAINED" if scientific_qualification_candidate else "SMOKE_NOT_QUALIFIED",
            "seeds_trained": trained,
            "selected_seed": selected[0], "selected_epoch": selected[1],
            "validation_crossentropy_per_register": best,
            "foundation_public_rows": len(examples),
            "validation_public_rows": len(validation),
            "parameters": sum(p.numel() for p in winner.parameters()),
            "learned_bytes": bytes_used,
            "wall_seconds": time.perf_counter() - started,
            "source_public_sha256": digest,
        }
        return self

    def begin_world(self):
        if self._net is None:
            raise ValueError("FKP17_RECURRENT_PRIOR_NOT_TRAINED")
        self._history = []
        self.world_count = 0

    def observe_public(self, record):
        if self._net is None or self.world_count >= 256:
            raise ValueError("FKP17_RECURRENT_WORLD_NOT_READY_OR_OVERBUDGET")
        before, action, after, reward, done, history = _row(record)
        self._history.append((before, action, reward, after, done))
        if len(self._history) > MAX_HISTORY:
            self._history.pop(0)
        self.world_count += 1

    def choose_public(self, state):
        if self._net is None:
            raise ValueError("FKP17_RECURRENT_UNTRAINED_CHOICE")
        before = _state(state)
        torch = self._torch
        inp = [_sequence(before, action, self._history) for action in range(8)]
        data = torch.tensor(inp, dtype=torch.float32, device="cpu")
        with torch.inference_mode():
            p = torch.softmax(self._net(data), dim=-1)
            costs = torch.tensor([abs(x - 8) for x in range(16)], dtype=torch.float32)
            future_cost = (p * costs).sum(dim=(-1, -2))
            best = int(torch.argmin(future_cost))
        return best

    def state_receipt(self):
        if self._net is None:
            raise ValueError("FKP17_RECURRENT_UNTRAINED_RECEIPT")
        h = sha256()
        h.update(b"FKP17-FULLY-TRAINED-RECURRENT-V1")
        h.update(bytes.fromhex(self._digest))
        for k, tensor in sorted(self._net.state_dict().items()):
            h.update(k.encode("ascii"))
            h.update(tensor.detach().cpu().contiguous().numpy().tobytes())
        h.update(json.dumps(self._history, separators=(",", ":")).encode("ascii"))
        h.update(struct.pack("<I", self.world_count))
        return h.hexdigest()


def source_safe_dev_smoke(public_examples, validation_examples):
    """2-pass/1-seed engineering smoke; explicitly cannot satisfy prereg."""
    examples, digest = _public_training(public_examples)
    val, _ = _public_training(validation_examples)
    return FullyTrainedRecurrent()._fit(examples, val, digest,
                                        seeds=(1515,), epochs=1,
                                        scientific_qualification_candidate=False)

"""UJ-01D DEV: deterministic bounded optimizer path, no corpus acquisition."""
import math
import random
import time

import torch


def train(model, pairs, *, seed, epochs=1, batch_size=8, rate=0.001,
          max_steps=1024, max_bytes=2**20):
    """Train on explicitly supplied TRAIN positives only; return accounting.

    A failed run is not resumable: discard its in-memory model. No checkpoint,
    external IO, holdout evaluation or automatic budget expansion is performed.
    Caller must establish corpus and model custody and freeze initialization.
    """
    if (type(seed) is not int or type(epochs) is not int or not 1 <= epochs <= 32
            or type(batch_size) is not int or not 2 <= batch_size <= 64
            or type(max_steps) is not int or not 1 <= max_steps <= 4096
            or type(max_bytes) is not int or not 1 <= max_bytes <= 2**24
            or not math.isfinite(rate) or not 0 < rate <= 0.01):
        raise ValueError("invalid training budget")
    if not isinstance(pairs, (list, tuple)) or not 2 <= len(pairs) <= 65536:
        raise ValueError("invalid training pairs")
    for pair in pairs:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2 or any(
                type(v) is not bytes or not 1 <= len(v) <= 256 for v in pair):
            raise ValueError("invalid training observation")
    # Avoid dropping data or producing a singleton; reject uneven schedules.
    if len(pairs) % batch_size:
        raise ValueError("training size must divide evenly by batch size")
    steps = epochs * (len(pairs) // batch_size)
    exposure_bytes = epochs * sum(len(c) + len(y) for c, y in pairs)
    if steps > max_steps or exposure_bytes > max_bytes:
        raise ValueError("training budget exceeded before execution")
    params = [p for p in model.parameters() if p.requires_grad]
    if not params or any(not torch.isfinite(p).all() for p in model.parameters()):
        raise ValueError("invalid initial parameters")
    optimizer = torch.optim.AdamW(params, lr=rate, weight_decay=0.)
    order = list(range(len(pairs)))
    rng = random.Random(seed)
    model.train()
    start = time.perf_counter()
    losses, min_stds = [], []
    for _ in range(epochs):
        rng.shuffle(order)
        for offset in range(0, len(order), batch_size):
            batch = [pairs[i] for i in order[offset:offset + batch_size]]
            context, future = zip(*batch)
            optimizer.zero_grad(set_to_none=True)
            loss, metrics = model.objective(context, future)
            std = float(metrics["min_online_std"])
            if not torch.isfinite(loss) or not math.isfinite(std) or std < 0:
                raise RuntimeError("nonfinite or invalid objective; discard model")
            loss.backward()
            if any(p.grad is None or not torch.isfinite(p.grad).all() for p in params):
                raise RuntimeError("missing or nonfinite gradient; discard model")
            optimizer.step()
            model.update_target()
            if any(not torch.isfinite(p).all() for p in model.parameters()):
                raise RuntimeError("nonfinite update; discard model")
            losses.append(float(loss.detach()))
            min_stds.append(std)
    model.eval()
    return {"steps": steps, "observations": epochs * len(pairs),
            "exposure_bytes": exposure_bytes, "mean_loss": sum(losses)/steps,
            "min_online_std": min(min_stds), "elapsed_seconds": time.perf_counter()-start,
            "trainable_parameters": sum(p.numel() for p in params)}

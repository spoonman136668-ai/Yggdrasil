"""Explicit DEV training adapter; snapshot the underlying model, not this wrapper."""
from torch import nn
from anchor_loss import objective


class AnchorTrainingAdapter(nn.Module):
    def __init__(self, model, mode, weight=0.25):
        super().__init__()
        if mode not in ('aligned', 'sham', 'off') or type(weight) not in (int, float) or not 0 <= weight <= 1:
            raise ValueError('invalid anchor configuration')
        self.model, self.mode, self.weight = model, mode, weight

    def objective(self, context, future):
        return objective(self.model, context, future, self.mode, self.weight)

    def update_target(self):
        self.model.update_target()

"""MD35 negative-only action/outcome correspondence control.

The input is ALWAYS the authentic four-episode public charged transcript.
The negative replaces only TRAINING LABELS with another episode's label
from the SAME four-episode law block. No new physical receipt or history is
fabricated. Never use these labels for validation, transfer, cold or scoring.
"""
from dataclasses import dataclass
import random

from public_actions import PublicEpisode, require_public_blocks

SEED = 35047
REAL = "charged_real"
SHUFFLED = "shuffled_training_negative"
MODES = (REAL, SHUFFLED)


@dataclass(frozen=True)
class TrainingOnlyTarget:
    terminal_reward: float
    diagnostic_bit: int
    donor_index: int
    donor_trace_sha256: str

    def __post_init__(self):
        if (type(self.terminal_reward) is not float or
                self.terminal_reward not in (-0.52, 0.98) or
                type(self.diagnostic_bit) is not int or
                self.diagnostic_bit not in (0, 1) or
                type(self.donor_index) is not int or
                self.donor_index not in range(4) or
                type(self.donor_trace_sha256) is not str or
                len(self.donor_trace_sha256) != 64):
            raise AssertionError("MD35_NEGATIVE_LABELS_INVALID")


def training_targets(blocks, *, mode=REAL):
    """384 TRAIN-only blocks; never output PublicEpisode or fake receipts.

    Frozen independent permutation seed and within-block cyclic derangement
    preserve every block's diagnostic-bit and binary terminal-label counts,
    while disrupting which public action caused the observed outcome.
    """
    if mode not in MODES:
        raise AssertionError("MD35_UNREGISTERED_TRAIN_SUPERVISION")
    source = require_public_blocks(blocks, expected_count=384)
    rng = random.Random(SEED)
    result = []
    for block in source:
        if any(len(ep.events) != 4 or ep.diagnostic() is None
               for ep in block):
            raise AssertionError("MD35_NEGATIVE_TRAIN_MUST_PAY_ALL_PROBES")
        shift = rng.randrange(1, 4) if mode == SHUFFLED else 0
        targets = []
        for i, _ in enumerate(block):
            donor = (i + shift) % 4
            ep = block[donor]
            label = TrainingOnlyTarget(
                float(ep.terminal()[3]), ep.diagnostic()[4],
                donor, ep.trace_sha256)
            if mode == SHUFFLED and donor == i:
                raise AssertionError("MD35_SHUFFLE_DERANGEMENT_BROKEN")
            targets.append(label)
        if (sorted((t.terminal_reward, t.diagnostic_bit) for t in targets) !=
                sorted((ep.terminal()[3], ep.diagnostic()[4]) for ep in block)):
            raise AssertionError("MD35_NEGATIVE_BLOCK_MARGINALS_DRIFT")
        result.append(tuple(targets))
    return tuple(result)

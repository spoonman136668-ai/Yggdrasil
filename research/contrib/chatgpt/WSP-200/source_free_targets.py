"""WSP-207: fabricated-only interaction target assembly and one-look boundary.

No original GFP measurements may be passed to this object.  It uses the
synthetic sentinel digest and FABRICATED_* backgrounds.  The official
WSP-200 original first-use guard is a separate owner-controlled decision.
"""
from __future__ import annotations

from collections import defaultdict
import math
from typing import Mapping

from learner import Sample
from source_free_partition import SYNTHETIC_DIGEST, StructuralManifest


def asinh_interaction(double: float, single_a: float,
                      single_b: float, wildtype: float) -> float:
    """Pinned WSP-200 four-measurement interaction, without censoring."""
    vals = (double, single_a, single_b, wildtype)
    if any(type(x) not in (int, float) or not math.isfinite(x) for x in vals):
        raise ValueError("missing/nonfinite numeric fluorescence: INVALID study")
    return math.asinh(double) - math.asinh(single_a) - math.asinh(single_b) + math.asinh(wildtype)


class SyntheticOneLook:
    """Progressive B0..B3 FIT access, then exactly one PUBLIC_DEV read.

    Merely constructing a gate never accesses numeric labels.  Attempted
    partial/invalid stages consume that stage: fail closed, never replay.
    RESERVED_UNTOUCHED has no read path.  The labels port must not
    pre-evaluate protected source fields before being handed to this class.
    """

    def __init__(self, manifest: StructuralManifest, wildtype_receipt: str,
                 labels: Mapping[str, float], *, source_digest: str):
        if source_digest != SYNTHETIC_DIGEST or not isinstance(wildtype_receipt, str):
            raise ValueError("synthetic-only target gate")
        if not manifest.eligible or not all(
            row.gene.startswith("FABRICATED_") for row in manifest.eligible
        ):
            raise ValueError("only fabricated genotype manifests allowed")
        if len({row.gene for row in manifest.eligible}) != 1:
            raise ValueError("separate model for each fabricated background")
        self.manifest = manifest
        self.wildtype_receipt = wildtype_receipt
        self.labels = labels
        self.next_stage = 0
        self.dev_opened = False
        self.invalid = False

    def _sample(self, row) -> Sample:
        # All other backgrounds and protected cohorts are excluded by caller.
        aa, bb = row.mutations
        left = f"{row.gene}\0{aa[1]}\0{aa[0]}\0{aa[2]}"
        right = f"{row.gene}\0{bb[1]}\0{bb[0]}\0{bb[2]}"
        values = [self.labels[key] for key in (
            row.row_id, row.parent_ids[0], row.parent_ids[1], self.wildtype_receipt
        )]
        return Sample(row.row_id, row.group, left, right,
                      asinh_interaction(*values))

    def fit_stage(self, stage: int) -> list[Sample]:
        if self.invalid or self.dev_opened or stage != self.next_stage or stage not in range(4):
            raise ValueError("future/replayed/non-FIT first-use stage")
        # Fail closed on any partial access.  A bad label invalidates rather than
        # authorizes a replay or silently excludes a sample.
        self.next_stage += 1
        chosen = [r for r in self.manifest.eligible
                  if r.bucket == "FIT" and r.stage == stage]
        if not chosen:
            self.invalid = True
            raise ValueError("empty predeclared FIT stage")
        try:
            batch = [self._sample(r) for r in chosen]
            for row in batch:
                row.validate(stage)
            return batch
        except Exception:
            self.invalid = True
            raise

    def public_dev_once(self) -> list[Sample]:
        if self.invalid or self.next_stage != 4 or self.dev_opened:
            raise ValueError("public DEV remains sealed or was already consumed")
        self.dev_opened = True  # consumed even if a numeric label is invalid
        chosen = [r for r in self.manifest.eligible if r.bucket == "PUBLIC_DEV"]
        if not chosen:
            self.invalid = True
            raise ValueError("empty predeclared PUBLIC_DEV")
        try:
            return [self._sample(r) for r in chosen]
        except Exception:
            self.invalid = True
            raise


def group_weighted_rmse(samples: list[Sample], predict, mean: float, sd: float) -> float:
    """Equal group weights within a background; no individual-row pooling."""
    if not samples or not math.isfinite(mean) or not math.isfinite(sd) or sd <= 1e-12:
        raise ValueError("invalid held scoring normalization")
    errors = defaultdict(list)
    for row in samples:
        pred = predict(row.left, row.right)
        if not math.isfinite(pred) or not math.isfinite(row.target):
            raise ValueError("nonfinite held scoring value")
        errors[row.group].append((pred-(row.target-mean)/sd)**2)
    return math.sqrt(sum(sum(err)/len(err) for err in errors.values())/len(errors))

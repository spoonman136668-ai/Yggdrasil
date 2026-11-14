"""Two independently fitted conventional causal response controls for MD33.

Bayesian: factorized Dirichlet encoder/decoder likelihoods with paid block
memory. Empirical model-based RL: categorical physical transition model and
one-step Bellman value-of-information choice using the same charged data.
Neither controller sees motif, hidden encoder/decoder, offset, rewire or seed.
"""
import json
import math
from pathlib import Path

from synthetic import LOCK
from compositional_relay import canonical, digest

CFG = LOCK["controls"]
KIND = ("encoder", "decoder")
PROBE_COST = LOCK["paid_data"]["probe_cost"]
GAIN_IF_CORRECT = 1.5
THRESHOLD = CFG["bayesian"]["probe_vs_actuator_threshold"]


def public_result(sensor):
    if (type(sensor) is not list or len(sensor) != 4 or
            any(type(v) is not int or v not in (0, 1) for v in sensor)
            or sum(sensor) != 1):
        raise AssertionError("MD33_UNPAID_OR_INVALID_ONE_HOT")
    return sensor.index(1)


def validate_public_probe(before, action, after):
    hist = after.get("charged_history", ())
    if (len(hist) != len(before["charged_history"]) + 1 or
            hist[-1]["action"] != action or
            hist[-1]["reward"] != -0.08 or
            action["kind"] != "diagnostic"):
        raise AssertionError("MD33_MODEL_REQUIRES_PHYSICALLY_PAID_PROBE")
    return public_result(hist[-1]["sensor_vector"])


def _new_counts():
    return [[[0] * 4 for _ in range(4)] for _ in range(2)]


class EmpiricalCausalControl:
    def __init__(self, mode):
        if mode not in ("bayesian", "empirical_rl"):
            raise AssertionError("MD33_UNKNOWN_CONVENTIONAL_MODE")
        self.mode = mode
        self.alpha = (CFG["bayesian"]["prior_alpha"] if mode == "bayesian"
                      else CFG["model_based_rl"]["smoothing"])
        self.global_counts = _new_counts()
        self.fit_examples = 0
        self.model_calls = 0
        self._local = {}
        self.validation_nll = None

    def begin_block(self):
        self._local = {}

    def fit(self, blocks):
        if len(blocks) != 192 or self.fit_examples:
            raise AssertionError("MD33_CONVENTIONAL_FIT_COUNT_DRIFT")
        for block in blocks:
            if len(block) != 4:
                raise AssertionError("MD33_WRONG_PAID_TRAIN_BLOCK")
            for episode in block:
                if len(episode) != 2:
                    raise AssertionError("MD33_WRONG_PAID_PROBE_COUNT")
                for kind, channel, response in episode:
                    if (kind not in KIND or type(channel) is not int or
                            channel not in range(4) or
                            type(response) is not int or response not in range(4)):
                        raise AssertionError("MD33_NONPUBLIC_TRAINING_ROW")
                    self.global_counts[KIND.index(kind)][channel][response] += 1
                    self.fit_examples += 1
        if self.fit_examples != 1536:
            raise AssertionError("MD33_CONVENTIONAL_UNDERTRAINED")
        return self

    def predict(self, kind, channel):
        if kind not in KIND or channel not in range(4):
            raise AssertionError("MD33_INVALID_PUBLIC_QUERY")
        self.model_calls += 1
        key = (kind, channel)
        if key in self._local:
            observed = self._local[key]
            return tuple(float(i == observed) for i in range(4))
        counts = self.global_counts[KIND.index(kind)][channel]
        total = sum(counts) + 4 * self.alpha
        return tuple((v + self.alpha) / total for v in counts)

    def observe(self, kind, channel, result):
        if kind not in KIND or channel not in range(4) or result not in range(4):
            raise AssertionError("MD33_INVALID_CHARGED_MODEL_UPDATE")
        # This method may be called only from an actual paid trace guard in
        # evaluation. The global fitted model is never updated on holdout.
        self._local[(kind, channel)] = result

    def should_probe(self, prob):
        confidence = max(prob)
        if self.mode == "bayesian":
            return confidence < THRESHOLD
        # A one-step Bellman comparison of two terminal decisions.
        # With a real diagnostic the physical target is observed exactly,
        # while skipping must act on the most probable category.
        no_probe_value = 1.5 * confidence - 0.54
        paid_probe_value = 0.96 - PROBE_COST
        gain = paid_probe_value - no_probe_value
        return gain > 1e-12

    def validation(self, blocks):
        if self.fit_examples != 1536 or len(blocks) != 48:
            raise AssertionError("MD33_INVALID_VALIDATION_SPLIT")
        losses = []
        for block in blocks:
            self.begin_block()
            for episode in block:
                for kind, channel, result in episode:
                    p = self.predict(kind, channel)
                    losses.append(-math.log(max(p[result], 1e-12)))
                    self.observe(kind, channel, result)
        self.validation_nll = round(math.fsum(losses) / len(losses), 8)
        self.begin_block()
        if not math.isfinite(self.validation_nll):
            raise AssertionError("MD33_NONFINITE_VALIDATION_NLL")
        return self.validation_nll

    def checkpoint(self):
        if self.fit_examples != 1536:
            raise AssertionError("MD33_CONTROL_NOT_TRAINED")
        return {
            "schema": "md33.fitted-public-categorical-control.v1",
            "mode": self.mode, "smoothing": self.alpha,
            "trained_public_probe_samples": self.fit_examples,
            "physical_response_counts": self.global_counts,
            "validation_nll": self.validation_nll,
        }

    @classmethod
    def from_checkpoint(cls, checkpoint):
        if (checkpoint.get("schema") !=
                "md33.fitted-public-categorical-control.v1"):
            raise AssertionError("MD33_CONTROL_BAD_COLD_CHECKPOINT")
        model = cls(checkpoint["mode"])
        if checkpoint["smoothing"] != model.alpha:
            raise AssertionError("MD33_CONTROL_COLD_HYPERPARAMETER_DRIFT")
        model.global_counts = checkpoint["physical_response_counts"]
        model.fit_examples = checkpoint["trained_public_probe_samples"]
        model.validation_nll = checkpoint["validation_nll"]
        if checkpoint != model.checkpoint():
            raise AssertionError("MD33_CONTROL_COLD_BYTES_DIFFER")
        return model

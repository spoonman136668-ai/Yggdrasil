"""P0F-C2: source-independent, PUBLIC-only finite-count learner (engineering ONLY).

No native environment imported, no real or held samples touched. This module is
not a scientific acceptance or a claim about the 45-parameter Yggdrasil model.
Must pass independent frozen-contract review and original-source qualification
before source execution. Original design: FROZEN_DESIGN.json (do not edit).
"""
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math

ALPHA = 0.5
KAPPA = 8.0
CATEGORIES = 256
COPY_MASS = 0.90
SCHEMA = "yggdrasil.nci04.p0fc2.public-history-counts-engineering.v1"


class PublicCounts:
    def __init__(self, frame_length, action_count):
        if frame_length not in (147, 70) or action_count not in (7, 2):
            raise ValueError("P0FC2_UNSUPPORTED_ORIGINAL_SOURCE_WIRE")
        if (frame_length, action_count) not in ((147, 7), (70, 2)):
            raise ValueError("P0FC2_ORIGINAL_SOURCE_SHAPE_ACTION_DRIFT")
        self.length = frame_length
        self.action_count = action_count
        self.prior = defaultdict(Counter)
        self.current = defaultdict(Counter)
        self.history = defaultdict(Counter)
        self.training_episodes = 0
        self.training_steps = 0

    def _row(self, row):
        if (not isinstance(row, (tuple, list)) or len(row) != 3 or
                type(row[0]) is not bytes or type(row[2]) is not bytes or
                len(row[0]) != self.length or len(row[2]) != self.length or
                type(row[1]) is not int or
                row[1] not in range(self.action_count)):
            raise ValueError("P0FC2_INVALID_NATIVE_PUBLIC_ROW")
        return row

    @staticmethod
    def _pack(frame, action):
        return len(frame).to_bytes(2, "big") + frame + bytes([action])

    def _current(self, frame, action):
        return self._pack(frame, action)

    def _historical(self, frame, action, past):
        if len(past) != 2:
            raise ValueError("P0FC2_HISTORY_WINDOW_DRIFT")
        result = self._current(frame, action)
        for previous in past:
            result += (b"\\x00" if previous is None
                       else b"\\x01" + self._pack(*previous))
        return result

    def fit(self, episodes):
        if self.training_episodes or self.training_steps:
            raise ValueError("P0FC2_FIT_ALREADY_COMPLETED")
        if not isinstance(episodes, (tuple, list)) or not episodes:
            raise ValueError("P0FC2_EMPTY_TRAINING_EPISODES")
        for episode in episodes:
            if not isinstance(episode, (tuple, list)) or not episode:
                raise ValueError("P0FC2_EMPTY_TRAINING_EPISODE")
            past = [None, None]
            for row in episode:
                before, action, after = self._row(row)
                cur = self._current(before, action)
                hist = self._historical(before, action, past)
                self.current[cur][after] += 1
                self.history[hist][after] += 1
                for position in range(self.length):
                    self.prior[(position, before[position], action)][
                        after[position]] += 1
                past = [past[1], (before, action)]
                self.training_steps += 1
            self.training_episodes += 1
        return self

    def _base(self, position, before_value, action, value):
        values = self.prior.get((position, before_value, action))
        total = sum(values.values()) if values is not None else 0
        found = values[value] if values is not None else 0
        return (found + ALPHA) / (total + CATEGORIES * ALPHA)

    def probability(self, model, before, action, past, position, value):
        if (type(before) is not bytes or len(before) != self.length or
                type(action) is not int or action not in range(self.action_count) or
                type(value) is not int or value not in range(CATEGORIES) or
                type(position) is not int or position not in range(self.length)):
            raise ValueError("P0FC2_INVALID_PUBLIC_PREDICTION_QUERY")
        if model == "copy":
            return COPY_MASS * (value == before[position]) + (
                (1.0 - COPY_MASS) / CATEGORIES)
        base = self._base(position, before[position], action, value)
        if model == "prior":
            return base
        if model == "current":
            observations = self.current.get(self._current(before, action))
        elif model == "history":
            observations = self.history.get(self._historical(
                before, action, past))
        else:
            raise ValueError("P0FC2_UNKNOWN_PRECOMMITTED_MODEL")
        if not observations:
            return base
        total = sum(observations.values())
        matched = sum(n for nxt, n in observations.items()
                      if nxt[position] == value)
        return (matched + KAPPA * base) / (total + KAPPA)

    def episode_nll(self, model, episode):
        if not isinstance(episode, (tuple, list)) or not episode:
            raise ValueError("P0FC2_EMPTY_SCORING_EPISODE")
        past = [None, None]
        total = 0.0
        for row in episode:
            before, action, after = self._row(row)
            for position, value in enumerate(after):
                probability = self.probability(
                    model, before, action, past, position, value)
                if not (0.0 < probability <= 1.0) or not math.isfinite(
                        probability):
                    raise ValueError("P0FC2_INVALID_PROPER_PREDICTIVE_MASS")
                total -= math.log(probability)
            past = [past[1], (before, action)]
        return total / (len(episode) * self.length)

    def mean_episode_nll(self, model, episodes):
        if not isinstance(episodes, (tuple, list)) or not episodes:
            raise ValueError("P0FC2_EMPTY_SCORING_COHORT")
        return sum(self.episode_nll(model, ep) for ep in episodes) / len(episodes)

    def canonical_receipt(self):
        """Deterministic source-neutral checkpoint receipt, no source run."""
        def encode_table(table):
            result = []
            for key in sorted(table):
                if type(key) is bytes:
                    label = key.hex()
                else:
                    label = list(key)
                result.append([
                    label,
                    [[after.hex() if type(after) is bytes else after, n]
                     for after, n in sorted(table[key].items())]
                ])
            return result
        output = {"schema": SCHEMA,
                  "frame_length": self.length,
                  "action_count": self.action_count,
                  "training_episodes": self.training_episodes,
                  "training_steps": self.training_steps,
                  "prior": encode_table(self.prior),
                  "current": encode_table(self.current),
                  "history": encode_table(self.history)}
        wire = json.dumps(output, sort_keys=True, separators=(",", ":"),
                          allow_nan=False).encode("utf-8")
        return {"sha256": sha256(wire).hexdigest(), "bytes": len(wire),
                "training_episodes": self.training_episodes,
                "training_steps": self.training_steps}


def synthetic_contract_selftest():
    """Fixed hand-authored bytes, NOT original source or scientific exposure."""
    length = 70
    common = bytes([0]) * length
    a = bytes([11]) * length
    b = bytes([12]) * length
    out_a = bytes([2]) * length
    out_b = bytes([3]) * length
    episodes = [[(a, 0, common), (common, 1, out_a)],
                [(b, 0, common), (common, 1, out_b)]]
    first = PublicCounts(70, 2).fit(episodes)
    second = PublicCounts(70, 2).fit(episodes)
    if first.canonical_receipt() != second.canonical_receipt():
        raise AssertionError("P0FC2_CHECKPOINT_NOT_DETERMINISTIC")
    if not (first.probability("history", common, 1, [None, (a, 0)],
                              0, 2) >
            first.probability("current", common, 1, [None, (a, 0)],
                              0, 2)):
        raise AssertionError("P0FC2_PUBLIC_HISTORY_NOT_CONDITIONING")
    for model in ("copy", "prior", "current", "history"):
        probabilities = [first.probability(
            model, common, 1, [None, (a, 0)], 0, v)
                         for v in range(CATEGORIES)]
        if not math.isclose(sum(probabilities), 1, rel_tol=0,
                            abs_tol=1e-12):
            raise AssertionError("P0FC2_NOT_NORMALIZED_" + model)
        if not math.isfinite(first.mean_episode_nll(model, episodes)):
            raise AssertionError("P0FC2_NONFINITE_" + model)
    return "P0FC2_SYNTHETIC_PUBLIC_COUNTS_CONTRACT=PASS"


if __name__ == "__main__":
    print(synthetic_contract_selftest())

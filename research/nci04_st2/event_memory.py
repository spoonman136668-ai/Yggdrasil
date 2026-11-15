"""ST2 opt-in public-appearance memory. Development mechanics, NOT scientific evidence.

Public 3-byte appearances are only provisional associations, not object IDs.
An association is usable solely when it occurs once in both consecutive
preaction public frames. No future image, environment internals, reward,
grid, mission, pose, or ST1 topology enters a prediction.

Only a separately authenticated original env.step is eligible as evidence;
this API checks byte-level target consistency, not source provenance.
"""
import hashlib
import json

from research.mr18.native_public_learning import validate
from research.nci04_s1.local_messages import LocalPredictiveMessages45
from yggdrasil.developmental import valid

N = 8
ACTIONS = 6
MAX_COUNT = 65535
SCHEMA = "yggdrasil.nci04.st2.public-event-memory.v1"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def check_raw(raw):
    if (type(raw) not in (tuple, list) or len(raw) != 24 or
            any(type(x) is not int or not 0 <= x <= 255 for x in raw)):
        raise ValueError("NCI04_ST2_INVALID_PUBLIC_RAW")


def signatures(raw):
    check_raw(raw)
    return tuple(tuple(raw[3 * i:3 * i + 3]) for i in range(N))


def correspondences(previous_raw, current_raw):
    """Preaction current-location -> (public signature, prior location) or None.

    The all-zero signature is uninformative, and any duplicate on either
    side is UNKNOWN, including duplicates at a previously known location.
    """
    current = signatures(current_raw)
    if previous_raw is None:
        return (None,) * N
    previous = signatures(previous_raw)
    return tuple(
        (s, previous.index(s)) if (
            s != (0, 0, 0) and
            current.count(s) == 1 and previous.count(s) == 1
        ) else None for s in current
    )


def cross_position_headroom(previous_raw, current_raw):
    """Public-only stage-0 diagnostic; never use future frames for matching."""
    return sum(1 for i, match in enumerate(
        correspondences(previous_raw, current_raw)
    ) if match is not None and match[1] != i)


class EventGroundedMemory45:
    """Frozen original S1 with eight bounded 6-action binary event-count tracks."""

    def __init__(self, original_s1_snapshot):
        self.native = LocalPredictiveMessages45.restore(original_s1_snapshot)
        self.weights_sha256 = self._weights_digest()
        self.labels = [None] * N
        self.counts = [[[0, 0] for _ in range(ACTIONS)] for _ in range(N)]
        self.last_used = [0] * N
        self.clock = 0
        self.previous_raw = None

    def _weights_digest(self):
        return hashlib.sha256(
            self.native.runtime.core.snapshot().encode("utf-8")
        ).hexdigest()

    def _check_weights(self):
        if self._weights_digest() != self.weights_sha256:
            raise ValueError("NCI04_ST2_FROZEN_45_COEFFICIENT_DRIFT")

    @staticmethod
    def _validate_input(raw, bits, action):
        validate(raw, bits, action)
        if action >= ACTIONS:
            raise ValueError("NCI04_ST2_ACTION_OUTSIDE_FROZEN_SIX")

    def _slot(self, signature):
        try:
            return self.labels.index(signature)
        except ValueError:
            return None

    def _allocate(self, signature):
        slot = self._slot(signature)
        if slot is not None:
            return slot
        try:
            slot = self.labels.index(None)
        except ValueError:
            # Least recently touched slot; stable index resolves ties.
            slot = min(range(N), key=lambda i: (self.last_used[i], i))
        self.labels[slot] = signature
        self.counts[slot] = [[0, 0] for _ in range(ACTIONS)]
        self.last_used[slot] = 0
        return slot

    def predict(self, raw, bits, action):
        self._validate_input(raw, bits, action)
        self._check_weights()
        result = self.native.predict(raw, bits, action)
        for i, match in enumerate(correspondences(self.previous_raw, raw)):
            if match is None:
                continue
            slot = self._slot(match[0])
            if slot is None:
                continue
            changed, unchanged = self.counts[slot][action]
            if changed + unchanged >= 4:
                estimate = (1 + changed) / (2 + changed + unchanged)
                result[i] = 0.5 * result[i] + 0.5 * estimate
        return result

    def observe(self, raw, bits, action, targets, next_raw, *, train=True):
        """Return PREACTION prediction, then update on supplied public outcome.

        The caller must authenticate the original post-action environment step.
        next_raw is used only to validate outcomes AFTER prediction was formed.
        """
        self._validate_input(raw, bits, action)
        valid(targets)
        check_raw(next_raw)
        if type(train) is not bool:
            raise ValueError("NCI04_ST2_INVALID_TRAINING_MODE")
        derived = [int(tuple(raw[3*i:3*i+3]) !=
                       tuple(next_raw[3*i:3*i+3])) for i in range(N)]
        if list(targets) != derived:
            raise ValueError("NCI04_ST2_PUBLIC_OUTCOME_MISMATCH")
        before = self.snapshot()
        try:
            prediction = self.predict(raw, bits, action)
            native_prediction = self.native.predict(raw, bits, action)
            matches = correspondences(self.previous_raw, raw)
            returned = self.native.observe(
                raw, bits, action, targets, train=False
            )
            if returned != native_prediction:
                raise ValueError("NCI04_ST2_S1_PREDICTION_DRIFT")
            self._check_weights()
            if train:
                if self.clock >= 100000000:
                    raise ValueError("NCI04_ST2_CLOCK_EXHAUSTED")
                self.clock += 1
                for i, match in enumerate(matches):
                    if match is None:
                        continue
                    slot = self._allocate(match[0])
                    pair = self.counts[slot][action]
                    if max(pair) == MAX_COUNT:
                        pair[0] //= 2
                        pair[1] //= 2
                    pair[0 if targets[i] else 1] += 1
                    self.last_used[slot] = self.clock
            # Never store next_raw for preaction association or peek ahead.
            self.previous_raw = list(raw)
            self._check_weights()
            if type(self).restore(self.snapshot()).snapshot() != self.snapshot():
                raise ValueError("NCI04_ST2_COLD_RESTORE_DRIFT")
            return prediction
        except Exception:
            self.__dict__.update(type(self).restore(before).__dict__)
            raise

    def reset_episode(self):
        self._check_weights()
        self.native.reset_episode()
        self.previous_raw = None  # Counts and labels survive physical reset.

    def accounting(self):
        self._check_weights()
        return {
            "original_frozen_coefficients": 45,
            "original_inference_state_scalars": 8,
            "additional_trainable_neural_coefficients": 0,
            "persistent_uint16_counter_bytes": N * ACTIONS * 2 * 2,
            "reserved_public_signature_bytes": N * 3,
            "extra_registers": {
                "last_used_uint32_bytes": N * 4,
                "clock_uint32_bytes": 4,
                "ephemeral_previous_public_raw_bytes": 24,
            },
            "tracked_signatures": sum(s is not None for s in self.labels),
            "checkpoint_bytes": len(self.snapshot().encode("utf-8")),
            "scientific_first_use_qualified": False,
            "physical_distributed_messages_qualified": False,
        }

    def snapshot(self):
        self._check_weights()
        return canonical({
            "schema": SCHEMA,
            "native": json.loads(self.native.snapshot()),
            "weights_sha256": self.weights_sha256,
            "labels": [list(s) if s is not None else None for s in self.labels],
            "counts": self.counts,
            "last_used": self.last_used,
            "clock": self.clock,
            "previous_raw": self.previous_raw,
        })

    @classmethod
    def restore(cls, payload):
        if type(payload) is not str or len(payload) > 65536:
            raise ValueError("NCI04_ST2_INVALID_CHECKPOINT_SIZE")
        try:
            d = json.loads(payload)
            if (type(d) is not dict or set(d) != {
                    "schema", "native", "weights_sha256", "labels", "counts",
                    "last_used", "clock", "previous_raw"
                } or d["schema"] != SCHEMA or
                type(d["labels"]) is not list or len(d["labels"]) != N or
                type(d["counts"]) is not list or len(d["counts"]) != N or
                type(d["last_used"]) is not list or len(d["last_used"]) != N or
                type(d["clock"]) is not int or
                not 0 <= d["clock"] <= 100000000 or
                (d["previous_raw"] is not None and
                 not _valid_raw(d["previous_raw"]))):
                raise ValueError("NCI04_ST2_INVALID_CHECKPOINT_SHAPE")
            labels = d["labels"]
            for s in labels:
                if s is not None and (
                    type(s) is not list or len(s) != 3 or
                    any(type(x) is not int or not 0 <= x <= 255 for x in s) or
                    s == [0, 0, 0]
                ):
                    raise ValueError("NCI04_ST2_INVALID_LABEL")
            occupied = [tuple(s) for s in labels if s is not None]
            if len(occupied) != len(set(occupied)):
                raise ValueError("NCI04_ST2_DUPLICATE_LABEL")
            for i, row in enumerate(d["counts"]):
                if (type(row) is not list or len(row) != ACTIONS or
                    any(type(p) is not list or len(p) != 2 or
                        any(type(v) is not int or not 0 <= v <= MAX_COUNT
                            for v in p) for p in row) or
                    type(d["last_used"][i]) is not int or
                    not 0 <= d["last_used"][i] <= d["clock"] or
                    (labels[i] is None and (
                        d["last_used"][i] != 0 or
                        any(p != [0, 0] for p in row)))):
                    raise ValueError("NCI04_ST2_INVALID_COUNTER_SHAPE")
            obj = cls(canonical(d["native"]))
            obj.labels = [tuple(s) if s is not None else None for s in labels]
            obj.counts = [[p[:] for p in row] for row in d["counts"]]
            obj.last_used = d["last_used"][:]
            obj.clock = d["clock"]
            obj.previous_raw = d["previous_raw"]
            if (d["weights_sha256"] != obj.weights_sha256 or
                    obj.snapshot() != payload):
                raise ValueError("NCI04_ST2_CHECKPOINT_IDENTITY_DRIFT")
            return obj
        except (TypeError, KeyError, OverflowError) as exc:
            raise ValueError("NCI04_ST2_MALFORMED_CHECKPOINT") from exc


def _valid_raw(raw):
    try:
        check_raw(raw)
        return True
    except ValueError:
        return False

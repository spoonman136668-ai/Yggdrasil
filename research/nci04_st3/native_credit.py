"""ST3 eight local native intervention-credit cells; DEVELOPMENT, not science.

Integer causal rule bank. A cell observes only an 8-bit PUBLIC frame,
the announced action and the prior public action/consequence. It updates
only AFTER an actual source step. Source law IDs, pending effects, seed,
SHA-masks and rotation are never inputs to this class.

Architectural prior: three one-hop/two-hop/three-hop candidate rotations;
this is a disclosed task-aligned prior, NOT learned physical-world semantics.
Each cell holds per-rotation, per-action, prior-intervention-conditioned
binary residual evidence. Profiles are recovered from observed intervention
consequences; no privileged context ID. All data-dependent state is integer.
"""
import json

CELLS = 8
ROTATIONS = (1, 2, 3)
ACTIONS = 4
MODES = 8
SLOTS = 9
MAX_COUNT = 255
MAX_BAD = 65535
MAX_CLOCK = 100000000
WARMUP = 4
SCHEMA = "yggdrasil.nci04.st3.native-intervention-credit.v1"
VARIANTS = ("causal", "no_delay", "sham", "episode_erase")


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False)


def check_bits(bits):
    if (type(bits) not in (tuple, list) or len(bits) != CELLS or
            any(type(v) is not int or v not in (0, 1) for v in bits)):
        raise ValueError("ST3_CELL_INVALID_PUBLIC_BITS")


def check_action(action):
    if type(action) is not int or action not in range(ACTIONS):
        raise ValueError("ST3_CELL_INVALID_ACTION")


def rot_bit(raw, index, rotation):
    return raw[(index - rotation) % CELLS]


def blank_profile():
    return {
        "evidence": [
            [[[0, 0] for _ in range(MODES)] for _ in range(CELLS)]
            for _ in ROTATIONS
        ],
        "contradictions": [0, 0, 0],
        "observations": 0,
        "last_used": 0,
    }


def row_mode(action, prior, variant, *, update):
    """Sham corrupts temporal CREDIT at update, not the forecast readout."""
    check_action(action)
    if prior is not None:
        check_action(prior)
    if variant == "no_delay":
        return action
    flagged = prior == (1 if variant == "sham" and update else 2)
    return action + (4 if flagged else 0)


def residual(raw, target, cell, rotation):
    # target is observed change bit, not next-state truth ahead of time.
    next_bit = raw[cell] ^ target[cell]
    return next_bit ^ rot_bit(raw, cell, rotation)


def choose_rotation(profile):
    # Each candidate receives the SAME number of eligible public events.
    # Fewer past contradictory outcomes wins; stable tie -> smaller shift.
    return min(range(len(ROTATIONS)),
               key=lambda r: (profile["contradictions"][r], r))


def predict_profile(profile, raw, action, prior, variant):
    r = choose_rotation(profile)
    mode = row_mode(action, prior, variant, update=False)
    out = []
    for i in range(CELLS):
        yes, no = profile["evidence"][r][i][mode]
        # Laplace-smoothed binary residual likelihood.
        prob = (1 + yes) / (2 + yes + no)
        changed_without_residual = raw[i] ^ rot_bit(raw, i, ROTATIONS[r])
        out.append((1.0 - prob) if changed_without_residual else prob)
    return out


def update_profile(profile, raw, action, prior, target, variant, clock):
    mode = row_mode(action, prior, variant, update=True)
    for ri, k in enumerate(ROTATIONS):
        for i in range(CELLS):
            value = residual(raw, target, i, k)
            pair = profile["evidence"][ri][i][mode]
            # Update model-selection contradiction BEFORE incorporating target.
            if sum(pair) >= 2 and value != int(pair[0] >= pair[1]):
                profile["contradictions"][ri] = min(
                    MAX_BAD, profile["contradictions"][ri] + 1
                )
            if MAX_COUNT in pair:
                pair[0] //= 2
                pair[1] //= 2
            pair[0 if value else 1] += 1
    profile["observations"] = min(MAX_CLOCK, profile["observations"] + 1)
    profile["last_used"] = clock


def match_cost(profile, history, variant):
    # Integer mismatch score, each public consequence incurs all eight bits.
    # Use a candidate rotation learned via its own prior public outcomes.
    r = choose_rotation(profile)
    total = 0
    for raw, action, prior, target in history:
        mode = row_mode(action, prior, variant, update=False)
        for i in range(CELLS):
            yes, no = profile["evidence"][r][i][mode]
            n = yes + no
            v = residual(raw, target, i, ROTATIONS[r])
            wrong = no if v else yes
            total += 256 * (1 + wrong) // (2 + n)
    return total


class NativeInterventionCredit8:
    """Bounded bank of eight-bit public causal hypotheses.

    No training-law ID ever enters reset, predict, observe or checkpoint.
    Profiles are selected by likelihood of a four-transition public preamble.
    On high-confidence contradictory events a slot is retried/evicted.
    """

    def __init__(self, variant="causal"):
        if variant not in VARIANTS:
            raise ValueError("ST3_INVALID_FROZEN_VARIANT")
        self.variant = variant
        self.profiles = [None] * SLOTS
        self.active = None
        self.preamble = []
        self.prior_action = None
        self.clock = 0
        self.episode_steps = 0
        self.contradiction_streak = 0
        self.updates = 0
        self.retrievals = 0
        self.forks = 0

    def reset_episode(self):
        if self.variant == "episode_erase":
            self.profiles = [None] * SLOTS
        self.active = None
        self.preamble = []
        self.prior_action = None
        self.episode_steps = 0
        self.contradiction_streak = 0

    def _assign(self):
        if len(self.preamble) < WARMUP:
            return
        candidates = []
        for index, profile in enumerate(self.profiles):
            if profile is None or profile["observations"] < 16:
                continue
            score = match_cost(profile, self.preamble, self.variant)
            candidates.append((score, index))
        # Each preamble has 32 binary observations; mean < 0.25 error
        # is a declared architectural retrieval threshold (not tuned).
        best = min(candidates) if candidates else None
        if best is not None and best[0] < WARMUP * CELLS * 64:
            index = best[1]
            self.retrievals += 1
        else:
            try:
                index = self.profiles.index(None)
            except ValueError:
                index = min(range(SLOTS), key=lambda i: (
                    self.profiles[i]["last_used"], i
                ))
            self.profiles[index] = blank_profile()
            self.forks += 1
        self.active = index
        profile = self.profiles[index]
        for raw, action, prior, target in self.preamble:
            update_profile(profile, raw, action, prior, target,
                           self.variant, self.clock)
        self.preamble = []

    def _retrieve_without_learning(self):
        """Select an old hypothesis from public consequences; never fit it."""
        if len(self.preamble) < WARMUP:
            return
        choices = []
        for index, profile in enumerate(self.profiles):
            if profile is None or profile["observations"] < 16:
                continue
            choices.append((match_cost(profile, self.preamble, self.variant),
                            index))
        best = min(choices) if choices else None
        if best is not None and best[0] < WARMUP * CELLS * 64:
            self.active = best[1]
            self.retrievals += 1
            self.preamble = []
        else:
            # A sliding observation-only inference window; no new profile,
            # count, learned coefficient or source-private identity is written.
            self.preamble = self.preamble[1:]

    def predict(self, public_bits, action):
        check_bits(public_bits)
        check_action(action)
        if self.active is None:
            return [0.5] * CELLS
        return predict_profile(
            self.profiles[self.active], public_bits, action,
            self.prior_action, self.variant
        )

    def observe(self, public_bits, action, targets, next_public_bits,
                *, learn=True):
        """Preaction output, then actual public consequence, never future peek."""
        check_bits(public_bits)
        check_bits(next_public_bits)
        check_bits(targets)
        check_action(action)
        if type(learn) is not bool:
            raise ValueError("ST3_OBSERVE_INVALID_LEARN")
        expected = [a ^ b for a,b in zip(public_bits,next_public_bits)]
        if list(targets) != expected:
            raise ValueError("ST3_OBSERVE_UNAUTHENTIC_PUBLIC_CONSEQUENCE")
        if self.clock >= MAX_CLOCK or self.episode_steps >= 64:
            raise ValueError("ST3_OBSERVE_STEP_OR_CLOCK_BUDGET")
        pred = self.predict(public_bits, action)
        if learn:
            self.clock += 1
            obs = (list(public_bits), action, self.prior_action, list(targets))
            if self.active is None:
                self.preamble.append(obs)
                self._assign()
            else:
                # A deterministic confidence-weighted public contradiction:
                # high-confidence errors on >=4 cells for 3 steps in a row
                # force a fresh public-only context retrieval.
                wrong = sum(
                    (p > 0.75 and y == 0) or (p < 0.25 and y == 1)
                    for p,y in zip(pred,targets)
                )
                self.contradiction_streak = (
                    self.contradiction_streak + 1 if wrong >= 4 else 0
                )
                if self.contradiction_streak >= 3:
                    self.active = None
                    self.preamble = [obs]
                    self.contradiction_streak = 0
                else:
                    update_profile(
                        self.profiles[self.active],
                        public_bits,action,self.prior_action,targets,
                        self.variant,self.clock
                    )
            self.updates += 1
        elif self.active is None:
            self.preamble.append((
                list(public_bits), action, self.prior_action, list(targets)
            ))
            self._retrieve_without_learning()
        self.prior_action = action
        self.episode_steps += 1
        return pred

    def snapshot(self):
        return canonical({
            "schema": SCHEMA,
            "variant": self.variant,
            "profiles": self.profiles,
            "active": self.active,
            "preamble": self.preamble,
            "prior_action": self.prior_action,
            "clock": self.clock,
            "episode_steps": self.episode_steps,
            "contradiction_streak": self.contradiction_streak,
            "updates": self.updates,
            "retrievals": self.retrievals,
            "forks": self.forks,
        })

    @classmethod
    def restore(cls, payload):
        if type(payload) is not str or len(payload) > 250000:
            raise ValueError("ST3_NATIVE_INVALID_CHECKPOINT_BYTES")
        try:
            d = json.loads(payload)
            if (type(d) is not dict or
                set(d) != {
                    "schema", "variant", "profiles", "active", "preamble",
                    "prior_action", "clock", "episode_steps",
                    "contradiction_streak", "updates", "retrievals", "forks"
                } or d["schema"] != SCHEMA or d["variant"] not in VARIANTS or
                type(d["profiles"]) is not list or len(d["profiles"]) != SLOTS or
                (d["active"] is not None and (
                    type(d["active"]) is not int or
                    d["active"] not in range(SLOTS))) or
                type(d["preamble"]) is not list or
                len(d["preamble"]) >= WARMUP or
                (d["prior_action"] is not None and (
                    type(d["prior_action"]) is not int or
                    d["prior_action"] not in range(ACTIONS))) or
                any(type(d[k]) is not int or d[k] < 0 or
                    d[k] > MAX_CLOCK for k in
                    ("clock","contradiction_streak","updates","retrievals","forks")) or
                type(d["episode_steps"]) is not int or
                d["episode_steps"] not in range(65)):
                raise ValueError("ST3_NATIVE_INVALID_CHECKPOINT_SHAPE")
            for profile in d["profiles"]:
                if profile is None:
                    continue
                if (type(profile) is not dict or set(profile) != {
                    "evidence","contradictions","observations","last_used"
                } or type(profile["evidence"]) is not list or
                    len(profile["evidence"]) != 3 or
                    type(profile["contradictions"]) is not list or
                    len(profile["contradictions"]) != 3 or
                    any(type(v) is not int or v < 0 or v > MAX_BAD
                        for v in profile["contradictions"]) or
                    any(type(profile[k]) is not int or
                        not 0 <= profile[k] <= d["clock"]
                        for k in ("observations","last_used"))):
                    raise ValueError("ST3_NATIVE_INVALID_PROFILE")
                for rotation in profile["evidence"]:
                    if type(rotation) is not list or len(rotation) != CELLS:
                        raise ValueError("ST3_NATIVE_INVALID_ROTATION_DATA")
                    for cell in rotation:
                        if type(cell) is not list or len(cell) != MODES:
                            raise ValueError("ST3_NATIVE_INVALID_CELL_DATA")
                        for pair in cell:
                            if (type(pair) is not list or len(pair) != 2 or
                                any(type(v) is not int or v < 0 or
                                    v > MAX_COUNT for v in pair)):
                                raise ValueError("ST3_NATIVE_INVALID_EVIDENCE")
            if d["active"] is not None and d["profiles"][d["active"]] is None:
                raise ValueError("ST3_NATIVE_MISSING_ACTIVE_PROFILE")
            for row in d["preamble"]:
                if (type(row) is not list or len(row) != 4 or
                    (row[2] is not None and
                     (type(row[2]) is not int or row[2] not in range(4)))):
                    raise ValueError("ST3_NATIVE_INVALID_PREAMBLE")
                check_bits(row[0]);check_action(row[1]);check_bits(row[3])
            if d["active"] is not None and d["preamble"]:
                raise ValueError("ST3_NATIVE_ACTIVE_PREAMBLE_COLLISION")
            obj = cls(d["variant"])
            obj.profiles = d["profiles"]
            for k in ("active","preamble","prior_action","clock",
                      "episode_steps","contradiction_streak","updates",
                      "retrievals","forks"):
                setattr(obj,k,d[k])
            if obj.snapshot() != payload:
                raise ValueError("ST3_NATIVE_NONCANONICAL_CHECKPOINT")
            return obj
        except (TypeError, KeyError, OverflowError) as exc:
            raise ValueError("ST3_NATIVE_INVALID_CHECKPOINT") from exc

    def accounting(self):
        return {
            "native_cells": CELLS,
            "rotation_hypotheses_per_cell": len(ROTATIONS),
            "max_public_law_profiles": SLOTS,
            "binary_residual_uint8_counter_capacity_bytes":
                SLOTS * len(ROTATIONS) * CELLS * MODES * 2,
            "per_profile_contradiction_uint16_bytes": SLOTS * 3 * 2,
            "extra_neural_weights": 0,
            "state_integer_only": True,
            "additional_causal_history_buffer_max_actions": WARMUP - 1,
            "checkpoint_json_bytes": len(self.snapshot().encode("utf-8")),
            "source_world_truth_access": False,
        }

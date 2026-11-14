"""MD35 public-only physically charged actions and model-facing transcript gate.

Never imports frozen private laws or opens reserved MD35 cohorts. A trusted
harness supplies a world port exposing observe(), step(), and receipt().
Trainers receive PublicEpisode only, never World, seed, spec or law metadata.
"""
from dataclasses import dataclass
import hashlib
import json
import random


EXPLORATION_SEED = 35049  # fixed prior to all MD35 train/validation first use
ALLOWED_REWARDS = (-0.52, -0.09, -0.05, -0.02, 0.98)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@dataclass(frozen=True)
class PublicEpisode:
    context: int
    # (phase, kind, argument, reward, physically_observed_bit_or_minus_one)
    events: tuple
    trace_sha256: str
    net_utility: float

    def route(self):
        return next(x[2] for x in self.events if x[1] == "route")

    def terminal(self):
        return next(x for x in self.events if x[1] == "terminal")

    def diagnostic(self):
        return next((x for x in self.events if x[1] == "diagnostic"), None)


def admit_receipt(context, receipt):
    """Admit *only* a complete MD34 public physical receipt.

    The provenance chain must start in the trusted world port: this verifier
    detects altered/unpaid/incomplete traces but a digest is not a signature.
    """
    if type(context) is not int or context not in range(4):
        raise AssertionError("MD35_INVALID_PUBLIC_CONTEXT")
    if type(receipt) is not dict or set(receipt) != {
        "schema", "paid_steps", "charged_diagnostics", "net_utility",
        "trace", "public_trace_sha256",
    } or receipt["schema"] != "md34.public-three-stage-paid-physical-receipt.v1":
        raise AssertionError("MD35_PRIVATE_OR_FORGED_RECEIPT_FIELDS")
    trace = receipt["trace"]
    if type(trace) is not list or len(trace) not in (3, 4):
        raise AssertionError("MD35_PHYSICAL_EPISODE_INCOMPLETE")
    digest = hashlib.sha256(canonical(trace).encode("utf-8")).hexdigest()
    if (receipt["public_trace_sha256"] != digest or
            receipt["paid_steps"] != len(trace)):
        raise AssertionError("MD35_PHYSICAL_TRACE_INTEGRITY")
    phase = 0
    used_probe = 0
    events = []
    for i, row in enumerate(trace):
        if type(row) is not dict or set(row) != {
            "phase", "action", "sensor_vector", "reward",
        } or type(row["phase"]) is not int or row["phase"] != phase:
            raise AssertionError("MD35_NONPUBLIC_OR_WRONG_PHASE_ROW")
        action, sensor, reward = row["action"], row["sensor_vector"], row["reward"]
        if (type(action) is not dict or type(sensor) is not list or
                type(reward) not in (int, float) or
                float(reward) not in ALLOWED_REWARDS):
            raise AssertionError("MD35_UNCHARGED_OR_BAD_PHYSICAL_EVENT")
        kind = action.get("kind")
        bit, arg = -1, 0
        if kind == "diagnostic":
            if used_probe or i == len(trace) - 1 or reward != -0.09:
                raise AssertionError("MD35_UNPAID_OR_DUPLICATE_DIAGNOSTIC")
            allowed = (
                {"kind": "diagnostic", "mechanism": "encoder_parity",
                 "channel": context} if phase == 0 else
                {"kind": "diagnostic", "mechanism": "terminal_parity"}
                if phase == 2 else None
            )
            if phase == 1:
                if (set(action) != {"kind", "mechanism", "channel"} or
                        action["mechanism"] != "route_parity" or
                        type(action["channel"]) is not int or
                        action["channel"] not in (0, 1)):
                    raise AssertionError("MD35_INVALID_PAID_ROUTE_DIAGNOSTIC")
                arg = action["channel"]
            elif action != allowed:
                raise AssertionError("MD35_INVALID_PAID_DIAGNOSTIC")
            if (len(sensor) != 2 or
                    any(type(v) is not int or v not in (0, 1) for v in sensor)
                    or sum(sensor) != 1):
                raise AssertionError("MD35_DIAGNOSTIC_NOT_ONE_PHYSICAL_BIT")
            bit = sensor.index(1)
            used_probe += 1
        else:
            if sensor != [0, 0]:
                raise AssertionError("MD35_FREE_SENSOR_INFORMATION")
            if kind == "actuator" and phase == 0:
                if action != {"kind": "actuator", "channel": context} or reward != -0.02:
                    raise AssertionError("MD35_INVALID_PRECURSOR")
                arg = context
            elif kind == "route" and phase == 1:
                if (set(action) != {"kind", "choice"} or
                        type(action["choice"]) is not int or
                        action["choice"] not in (0, 1)):
                    raise AssertionError("MD35_INVALID_CHARGED_ROUTE")
                arg = action["choice"]
                if reward != (-0.02 if arg == 0 else -0.05):
                    raise AssertionError("MD35_MISSING_ROUTE_COST")
            elif kind == "terminal" and phase == 2:
                if (set(action) != {"kind", "guess"} or
                        type(action["guess"]) is not int or
                        action["guess"] not in range(4) or
                        reward not in (-0.52, 0.98) or i != len(trace) - 1):
                    raise AssertionError("MD35_INVALID_TERMINAL_OUTCOME")
                arg = action["guess"]
            else:
                raise AssertionError("MD35_INVALID_CAUSAL_ACTION")
            phase += 1
        events.append((row["phase"], kind, arg, float(reward), bit))
    if (phase != 3 or used_probe != receipt["charged_diagnostics"] or
            abs(sum(x[3] for x in events) - receipt["net_utility"]) > 1e-9 or
            len(events) != 3 + used_probe):
        raise AssertionError("MD35_PHYSICAL_CHARGE_OR_TERMINAL_MISMATCH")
    return PublicEpisode(context, tuple(events), digest, float(receipt["net_utility"]))


def explore_episode(world, slot, rng):
    """Exactly one charged diagnostic rotating the four preregistered phases.

    World construction/selection and any hidden metadata stay in a separate
    authority-gated harness. This policy receives only public port methods.
    """
    if type(slot) is not int or slot not in range(4) or not isinstance(rng, random.Random):
        raise AssertionError("MD35_INVALID_SHARED_EXPLORER")
    initial = world.observe()
    if (type(initial) is not dict or
            type(initial.get("required_context")) is not int or
            initial.get("phase") != 0 or initial.get("charged_history") != []):
        raise AssertionError("MD35_INVALID_INITIAL_PUBLIC_OBSERVATION")
    context = initial["required_context"]
    if slot == 0:
        world.step({"kind": "diagnostic", "mechanism": "encoder_parity",
                    "channel": context})
    world.step({"kind": "actuator", "channel": context})
    if slot in (1, 2):
        world.step({"kind": "diagnostic", "mechanism": "route_parity",
                    "channel": slot - 1})
    route = rng.randrange(2)
    world.step({"kind": "route", "choice": route})
    if slot == 3:
        world.step({"kind": "diagnostic", "mechanism": "terminal_parity"})
    world.step({"kind": "terminal", "guess": rng.randrange(4)})
    observation = world.observe()
    receipt = world.receipt()
    if (observation["phase"] != "done" or
            observation["charged_history"] != receipt["trace"] or
            receipt["charged_diagnostics"] != 1 or receipt["paid_steps"] != 4):
        raise AssertionError("MD35_SHARED_EXPLORER_PHYSICAL_CUSTODY")
    return admit_receipt(context, receipt)


def require_public_blocks(blocks, *, expected_count=None):
    if type(blocks) not in (list, tuple) or (
            expected_count is not None and len(blocks) != expected_count):
        raise AssertionError("MD35_UNQUALIFIED_TRAIN_BLOCKS")
    for block in blocks:
        if type(block) not in (list, tuple) or len(block) != 4:
            raise AssertionError("MD35_FOUR_EPISODE_PUBLIC_BLOCK_REQUIRED")
        for context, episode in enumerate(block):
            if type(episode) is not PublicEpisode or episode.context != context:
                raise AssertionError("MD35_PRIVATE_METADATA_OR_CONTEXT_ORDER")
            if len(episode.events) not in (3, 4):
                raise AssertionError("MD35_UNPAID_EPISODE")
    return tuple(tuple(block) for block in blocks)

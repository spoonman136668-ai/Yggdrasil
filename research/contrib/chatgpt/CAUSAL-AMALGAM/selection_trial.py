"""Bounded synthetic-development continuation of the saved native/JEPA state."""

from collections import Counter, defaultdict, deque
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import resource
import sys
from time import monotonic

from shadow_preflight import checked_bytes
from specialist_selection import SpecialistSelection
from yggdrasil.native_causal_amalgam import NativeCausalAmalgam
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "CKAD-20" / "synthetic_world.py"
SCALE = 1_000_000


class TransitionControls:
    """Fully fit public conditional trailing and change-point predictors."""

    def __init__(self, depth, hazard):
        self.depth = depth
        self.hazard = hazard
        self.observations = defaultdict(lambda: deque(maxlen=depth))
        self.weights = defaultdict(lambda: [1.0])

    @staticmethod
    def estimate(ones, length):
        return (ones + 0.5) / (length + 1)

    def hypotheses(self, key):
        counts = [0]
        for outcome in reversed(self.observations[key]):
            counts.append(counts[-1] + outcome)
        return [self.estimate(ones, length) for length, ones in enumerate(counts)]

    def forecast(self, key):
        hypotheses = self.hypotheses(key)
        weights = self.weights[key]
        return (hypotheses[-1],
                sum(w * p for w, p in zip(weights, hypotheses, strict=True)))

    def update(self, key, outcome):
        likelihood = [p if outcome else 1 - p for p in self.hypotheses(key)]
        updated = [0.0] * min(self.depth + 1, len(likelihood) + 1)
        for length, (weight, probability) in enumerate(
                zip(self.weights[key], likelihood, strict=True)):
            mass = weight * probability
            # A reset after observing this row predicts the next from its prior.
            updated[0] += self.hazard * mass
            updated[min(length + 1, self.depth)] += (1 - self.hazard) * mass
        normalization = sum(updated)
        self.weights[key] = [item / normalization for item in updated]
        self.observations[key].append(outcome)


def source_module(expected):
    checked_bytes(SOURCE, expected)
    spec = importlib.util.spec_from_file_location("amalgam_ckad20_source", SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def restore(directory, protocol, state_name=None, state_pin=None):
    native = checked_bytes(directory / protocol["native_name"], protocol["native_sha256"])
    donor = json.loads(checked_bytes(
        directory / protocol["donor_name"], protocol["donor_sha256"]))
    name = state_name or protocol["joint_name"]
    pin = state_pin or protocol["joint_sha256"]
    joint = checked_bytes(directory / name, pin)
    return NativeCausalAmalgam.restore(
        joint, pin, native_parent=native, native_pin=protocol["native_sha256"],
        donor_parent=donor["state_ascii"].encode("ascii"), donor_pin=donor["state_sha256"],
    )


def configuration(protocol):
    return dict(window=protocol["window"], minimum_count=protocol["minimum_count"],
                minimum_gain=Fraction(protocol["selection_gain"]))


def trial(directory, protocol, output):
    started = monotonic()
    source = source_module(protocol["world_sha256"])
    anchor = restore(directory, protocol)
    gate = SpecialistSelection(anchor, **configuration(protocol))
    original = anchor.native._episode_reader()
    count = sum(phase["episodes"] for phase in protocol["phases"])
    if len(original._ledger) + count > original._episode_limit:
        raise ValueError("Trial would exceed the existing witness capacity")
    controls = TransitionControls(protocol["control_depth"], float(Fraction(protocol["hazard"])))
    for _, views, action, state, _, _ in original._ledger:
        controls.update((views[0][0], action), state)
    records = []
    coverage = Counter()
    for phase_index, phase in enumerate(protocol["phases"]):
        for index in range(phase["episodes"]):
            if monotonic() - started >= protocol["wall_cap_seconds"]:
                raise TimeoutError("Frozen development wall cap")
            episode = source.make_episode(cohort=protocol["cohort"], seed=phase["seed"],
                                          index=index, family=phase["family"], regime=phase["regime"])
            views = source.public_views(episode)
            public_context = views[0][0]
            first = coverage[public_context] % 2
            second = (coverage[public_context] // 2) % 2
            coverage[public_context] += 1
            key = public_context, first
            native, direct, temporal = gate._forecasts(views, (first,))
            origin = gate.selection(views, first)
            trailing, change_point = controls.forecast(key)
            permuted = tuple((1 - context, nuisance) for context, nuisance in views)
            _, wrong_direct, wrong_temporal = gate._forecasts(permuted, (first,))
            forecasts = {
                "native": native, "direct": direct, "temporal": temporal,
                "selector": (native, direct, temporal)[origin],
                "fixed_blend": (6 * native + direct + temporal) / 8,
                "misaligned_selector": (native, wrong_direct, wrong_temporal)[origin],
                "trailing": trailing, "change_point": change_point,
            }
            prediction = {name: round(p * SCALE) for name, p in forecasts.items()}
            row = source.rollout(episode, lambda _: first, lambda *_: second)
            identifier = digest(canonical([protocol["cohort"], phase["seed"], index]))
            gate = gate.observe_experience(
                identifier, views, row, source_sha256=EXPERIENCE_SOURCE,
                packet_sha256=digest(canonical([identifier, views, row])),
            )
            controls.update(key, row["s2"])
            records.append(dict(phase=phase_index, id=identifier, views=views, row=row,
                                prediction=prediction, origin=origin))
    checkpoint = gate.system.checkpoint()
    if anchor.checkpoint() != checked_bytes(directory / protocol["joint_name"], protocol["joint_sha256"]):
        raise RuntimeError("The starting state changed")
    if len(gate.system.native._episode_reader()._ledger) != len(original._ledger) + count:
        raise RuntimeError("Observed receipts and training count differ")
    output.mkdir(exist_ok=False)
    (output / "joint-descendant.json").write_bytes(checkpoint)
    (output / "trace.json").write_bytes(canonical(records))
    return dict(episodes=count, actions=count * 2, checkpoint_sha256=digest(checkpoint),
                native_sha256=digest(gate.system.native.checkpoint()),
                trace_sha256=digest(canonical(records)), parent_sha256=protocol["joint_sha256"],
                head_gradient_steps=[after.steps - before.steps
                                     for before, after in zip(anchor._heads, gate.system._heads, strict=True)],
                wall_seconds=monotonic() - started, max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


if __name__ == "__main__":
    directory, manifest, output = (Path(arg) for arg in sys.argv[1:])
    report = trial(directory, json.loads(manifest.read_bytes()), output)
    print(json.dumps(report, indent=2, sort_keys=True))

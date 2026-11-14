"""DG1-MD32 Compositional Causal Relay v1: PHYSICS-ONLY preflight.

A sequential, non-token environment with two hidden causal mechanisms:
encoder[a] -> latent intermediate h -> decoder[h] -> final actuator b.
One may learn those laws across four context-varied episodes per block.
Diagnostics are real, paid physical interventions, not root previews.
This source cannot instantiate official train/DEV/cold/registered cohorts.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCK = json.loads((HERE / "prereg.json").read_text("utf-8"))
assert LOCK["schema"] == "yggdrasil.dg1-md32-compositional-causal-relay-prereg.v1"
assert LOCK["status"] == "FROZEN_TASK_DESIGN_ONLY_BEFORE_GENERATOR_SOURCE_OR_FIXTURE_RESULTS"
BASES = {
    k: (tuple(v["encode"]), tuple(v["decode"]))
    for k, v in LOCK["law_family"]["map_contract"].items()
}
MOTIFS = tuple(BASES)
TRAIN = tuple(LOCK["law_family"]["train_motifs"])
TRANSFER = tuple(LOCK["law_family"]["unfamiliar_transfer_motifs"])
FIXTURE_FIRST, FIXTURE_LAST = LOCK["allocation"]["synthetic_fixture_seeds"]
ZERO = (0, 0, 0, 0)
N = 4


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def one_hot(index):
    if type(index) is not int or not 0 <= index < N:
        raise AssertionError("MD32_INVALID_ONE_HOT")
    return tuple(int(j == index) for j in range(N))


def fixture_spec(seed):
    """Construct fixture metadata. Never call this in a policy."""
    if type(seed) is not int or not FIXTURE_FIRST <= seed <= FIXTURE_LAST:
        raise AssertionError("MD32_OFFICIAL_FIRST_USE_OR_UNALLOCATED_SEED_FORBIDDEN")
    block, episode = divmod(seed - FIXTURE_FIRST, 4)
    motif = MOTIFS[block % len(MOTIFS)]
    offset = block // len(MOTIFS)
    encoder, decoder = BASES[motif]
    if len(encoder) != N or len(decoder) != N or offset not in range(N):
        raise AssertionError("MD32_BAD_FROZEN_LAW")
    return {
        "seed": seed,
        "block": block,
        "episode": episode,
        "motif": motif,
        "offset": offset,
        "encoder": encoder,
        "decoder": decoder,
        "required_precursor": episode,
    }


class RelayWorld:
    """Only observe/step/receipt are policy-facing; private law is not."""

    def __init__(self, spec, *, rewire):
        if type(rewire) is not bool:
            raise AssertionError("MD32_UNFROZEN_CHANGE_CONDITION")
        self._spec = dict(spec)
        self._rewire = rewire
        self._stage = 0
        self._latched = None
        self._sensors = ZERO
        self._spent = [False, False]
        self._history = []
        self._rewards = []

    def observe(self):
        if self._stage == 0:
            menu = {"mechanism": "encoder",
                    "channels": [self._spec["required_precursor"]]}
        elif self._stage == 1:
            menu = {"mechanism": "decoder", "channels": list(range(N))}
        else:
            menu = {"mechanism": "none", "channels": []}
        return {
            "phase": self._stage if self._stage < 2 else "done",
            "sensor_vector": list(self._sensors),
            "required_precursor": self._spec["required_precursor"],
            "diagnostic_menu": menu,
            "remaining_diagnostics": (
                int(not self._spent[self._stage])
                if self._stage < 2 else 0),
            "charged_history": deepcopy(self._history),
        }

    def _decode(self, intermediate):
        return ((self._spec["decoder"][intermediate] +
                 self._spec["offset"] + int(self._rewire)) % N)

    def step(self, action):
        if self._stage == 2:
            raise AssertionError("MD32_NO_ACTION_AFTER_DONE")
        if type(action) is not dict or action.get("kind") not in (
                "diagnostic", "actuator"):
            raise AssertionError("MD32_INVALID_ACTION")
        stage = self._stage
        if action["kind"] == "diagnostic":
            if (set(action) != {"kind", "mechanism", "channel"} or
                    self._spent[stage] or
                    type(action["channel"]) is not int):
                raise AssertionError("MD32_PAID_PROBE_CAP_OR_SHAPE")
            channel = action["channel"]
            if stage == 0:
                if (action["mechanism"] != "encoder" or
                        channel != self._spec["required_precursor"]):
                    raise AssertionError("MD32_NO_ROOT_OR_FOREIGN_ENCODER_PREVIEW")
                self._sensors = one_hot(self._spec["encoder"][channel])
            else:
                if action["mechanism"] != "decoder" or not 0 <= channel < N:
                    raise AssertionError("MD32_ONLY_INTERNAL_DECODER_PROBE")
                self._sensors = one_hot(self._decode(channel))
            self._spent[stage] = True
            reward = -0.08
        else:
            if set(action) != {"kind", "channel"} or type(action["channel"]) is not int:
                raise AssertionError("MD32_ACTUATOR_SHAPE_OR_TYPE")
            channel = action["channel"]
            if stage == 0:
                if channel != self._spec["required_precursor"]:
                    raise AssertionError("MD32_CONTEXT_PRECURSOR_RESTRICTION")
                self._latched = self._spec["encoder"][channel]
                self._stage = 1
                self._sensors = ZERO
                reward = -0.02
            else:
                if not 0 <= channel < N or self._latched is None:
                    raise AssertionError("MD32_INVALID_TERMINAL_ACTUATOR")
                success = channel == self._decode(self._latched)
                reward = 0.98 if success else -0.52
                self._stage = 2
                self._sensors = ZERO
        row = {
            "phase": stage,
            "action": dict(action),
            "sensor_vector": list(self._sensors),
            "reward": reward,
        }
        self._history.append(row)
        self._rewards.append(reward)
        if len(self._history) > 4:
            raise AssertionError("MD32_PHYSICAL_STEPS_EXCEEDED")
        return self.observe(), reward, self._stage == 2

    def receipt(self):
        if self._stage != 2:
            raise AssertionError("MD32_INCOMPLETE_PHYSICAL_EPISODE")
        public_trace = deepcopy(self._history)
        return {
            "schema": "md32.public-charged-relay-episode.v1",
            "paid_steps": len(public_trace),
            "net_utility": round(sum(self._rewards), 6),
            "trace": public_trace,
            "public_trace_sha256": digest(public_trace),
        }


def fixture_world(seed, *, rewire):
    return RelayWorld(fixture_spec(seed), rewire=rewire)


def _public_hot(observation):
    sensors = observation["sensor_vector"]
    if (len(sensors) != N or sum(sensors) != 1 or
            any(type(v) is not int or v not in (0, 1) for v in sensors)):
        raise AssertionError("MD32_PHYSICAL_PROBE_NOT_ONE_HOT")
    return sensors.index(1)


def run_public_two_probe(world):
    """Nonlearner proof of physical identifiability; ONLY observe/step."""
    obs = world.observe()
    precursor = obs["required_precursor"]
    obs, cost, done = world.step(
        {"kind": "diagnostic", "mechanism": "encoder",
         "channel": precursor})
    if done or cost != -0.08:
        raise AssertionError("MD32_ENCODER_PROBE_NOT_CHARGED")
    intermediate = _public_hot(obs)
    obs, cost, done = world.step({"kind": "actuator", "channel": precursor})
    if done or cost != -0.02 or obs["sensor_vector"] != list(ZERO):
        raise AssertionError("MD32_STAGE_BOUNDARY_LEAK")
    obs, cost, done = world.step(
        {"kind": "diagnostic", "mechanism": "decoder",
         "channel": intermediate})
    if done or cost != -0.08:
        raise AssertionError("MD32_DECODER_PROBE_NOT_CHARGED")
    terminal = _public_hot(obs)
    obs, reward, done = world.step({"kind": "actuator", "channel": terminal})
    if not done or reward != 0.98:
        raise AssertionError("MD32_PHYSICAL_COMPOSITION_POLICY_DID_NOT_SOLVE")
    return world.receipt()


def run_public_blind(world):
    """No labels/probes; fixed terminal action 0. Never reads hidden law."""
    prefix = world.observe()["required_precursor"]
    obs, cost, done = world.step({"kind": "actuator", "channel": prefix})
    if done or cost != -0.02:
        raise AssertionError("MD32_BLIND_STAGE0_INVALID")
    obs, terminal, done = world.step({"kind": "actuator", "channel": 0})
    if not done or terminal not in (0.98, -0.52):
        raise AssertionError("MD32_BLIND_TERMINAL_INVALID")
    return world.receipt()


def run_privileged_oracle(world, spec, rewire):
    """Physics ceiling ONLY, not a learner; privileged structure in harness."""
    precursor = world.observe()["required_precursor"]
    correct = ((spec["decoder"][spec["encoder"][precursor]] +
                spec["offset"] + int(rewire)) % N)
    world.step({"kind": "actuator", "channel": precursor})
    world.step({"kind": "actuator", "channel": correct})
    return world.receipt()


def law_manifest():
    signatures = {name: digest({"encode": enc, "decode": dec})
                  for name, (enc, dec) in sorted(BASES.items())}
    if (len(BASES) != 6 or len(set(signatures.values())) != 6 or
            len(TRAIN) != 3 or len(TRANSFER) != 3 or
            set(TRAIN) & set(TRANSFER)):
        raise AssertionError("MD32_COMPOSITION_STRUCTURE_OVERLAP")
    return {
        "train_motifs": list(TRAIN),
        "transfer_motifs": list(TRANSFER),
        "mechanism_sha256": signatures,
        "structural_family_sha256": digest(signatures),
    }


def preflight_task():
    """Physics audit on fixture-only paired worlds; NO model is trained."""
    manifest = law_manifest()
    rows = []
    for seed in range(FIXTURE_FIRST, FIXTURE_LAST + 1):
        spec = fixture_spec(seed)
        for rewire in (False, True):
            two = run_public_two_probe(fixture_world(seed, rewire=rewire))
            blind = run_public_blind(fixture_world(seed, rewire=rewire))
            oracle = run_privileged_oracle(
                fixture_world(seed, rewire=rewire), spec, rewire)
            stage0 = fixture_world(seed, rewire=rewire)
            # The first physical action is a fully charged causal choice.
            obs, _, _ = stage0.step(
                {"kind": "actuator", "channel": spec["required_precursor"]})
            if obs["sensor_vector"] != list(ZERO):
                raise AssertionError("MD32_FREE_STAGE1_HIDDEN_STATE_LEAK")
            rows.append({
                "seed": seed, "motif": spec["motif"], "rewire": rewire,
                "oracle": oracle["net_utility"], "blind": blind["net_utility"],
                "two_probe": two["net_utility"],
                "blind_correct": blind["net_utility"] == 0.96,
                "blind_sha": blind["public_trace_sha256"],
                "two_probe_sha": two["public_trace_sha256"],
                "oracle_sha": oracle["public_trace_sha256"],
            })
    if len(rows) != 192:
        raise AssertionError("MD32_FIXTURE_ALLOCATION_DRIFT")
    # Each hidden-offset is seen once per motif; this guarantees exactly
    # one out of four fixed terminal guesses is correct for each context.
    per = {}
    for motif in MOTIFS:
        a = [r for r in rows if r["motif"] == motif]
        stable = [r for r in a if not r["rewire"]]
        changed = [r for r in a if r["rewire"]]
        if (len(stable) != 16 or len(changed) != 16 or
                sum(r["blind_correct"] for r in stable) != 4 or
                sum(r["blind_correct"] for r in changed) != 4):
            raise AssertionError("MD32_BLIND_CLASS_BALANCE_FAILURE")
        per[motif] = {"fixture_worlds": len(a),
                      "fixed_terminal_success": sum(
                          r["blind_correct"] for r in a)}
    def avg(field):
        return round(sum(r[field] for r in rows) / len(rows), 6)
    oracle, blind, physical = (avg("oracle"), avg("blind"), avg("two_probe"))
    if (oracle != 0.96 or blind != -0.165 or physical != 0.8 or
            round(oracle - blind, 6) != 1.125 or
            round(oracle - physical, 6) != 0.16):
        raise AssertionError("MD32_TASK_DISTRIBUTION_HEADROOM_DRIFT")
    # Prove same context and stage0 public observation but opposite final
    # causal consequence, with a charged decoder query distinguishing.
    for seed in range(FIXTURE_FIRST, FIXTURE_LAST + 1):
        a = fixture_world(seed, rewire=False)
        b = fixture_world(seed, rewire=True)
        if a.observe() != b.observe():
            raise AssertionError("MD32_HIDDEN_EVENT_PUBLICLY_ANNOUNCED")
        prefix = a.observe()["required_precursor"]
        diagnostic = {"kind": "diagnostic",
                      "mechanism": "encoder", "channel": prefix}
        oa, _, _ = a.step(diagnostic)
        ob, _, _ = b.step(diagnostic)
        if oa != ob:
            raise AssertionError("MD32_STAGE0_PROBE_LEAKS_FUTURE_CHANGE")
        intermediate = _public_hot(oa)
        action = {"kind": "actuator", "channel": prefix}
        oa, _, _ = a.step(action)
        ob, _, _ = b.step(action)
        if oa != ob:
            raise AssertionError("MD32_STAGE1_AMBIENT_LEAKS_CHANGE")
        query = {"kind": "diagnostic", "mechanism": "decoder",
                 "channel": intermediate}
        oa, ra, _ = a.step(query)
        ob, rb, _ = b.step(query)
        if (ra != -0.08 or rb != -0.08 or
                oa["sensor_vector"] == ob["sensor_vector"]):
            raise AssertionError("MD32_REWIRE_NOT_PHYSICALLY_IDENTIFIABLE")
    return {
        "schema": "md32.task-physics-fixture-only.v1",
        "status": "TASK_PREFLIGHT_ONLY_NO_TRAINED_CONTROL_NO_SCIENCE",
        "official_first_use": False,
        "fixture_seed_range": [FIXTURE_FIRST, FIXTURE_LAST],
        "fixture_worlds": len(rows),
        "structure": manifest,
        "per_motif": per,
        "oracle_mean_net_utility": oracle,
        "blind_mean_net_utility": blind,
        "public_two_probe_mean_net_utility": physical,
        "oracle_blind_headroom": round(oracle - blind, 6),
        "oracle_two_probe_gap": round(oracle - physical, 6),
        "fixed_action_success_fraction": round(
            sum(r["blind_correct"] for r in rows) / len(rows), 6),
        "paired_stable_rewire_identifiability": "96/96",
        "public_trace_sha256": digest(rows),
        "strong_conventional_control_headroom": "UNVERIFIED",
        "learner_training_executed": False,
    }


if __name__ == "__main__":
    print(canonical(preflight_task()))

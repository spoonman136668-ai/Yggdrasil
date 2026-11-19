"""Independent CKAD21 context retrieval reference and checkpoint audit."""

import argparse
from fractions import Fraction
from hashlib import sha256
import importlib.util
from itertools import product
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / "CKAD-20"
sys.path.append(str(PREVIOUS))
from synthetic_world import make_episode, public_views, rollout


spec = importlib.util.spec_from_file_location("ckad20_independent_replay", PREVIOUS / "independent_audit.py")
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)
Replay = reference.Replay
canonical, sha, ratio = reference.canonical, reference.sha, reference.ratio
require = reference.require
BITS = (0, 1)
SCHEMA = "yggdrasil.ckad.native-episode-experience.v2"


class Mixture:
    """Exact conventional mixture fitted to the same disjoint public evidence blocks."""

    def __init__(self, events, *, repair=True):
        self.start = len(events)
        self.models = []
        self.ranges = []
        for start in range(0, len(events), 32):
            block = events[start:start + 32]
            if len(block) < 8:
                break
            candidate = Replay(repair)
            for event in block:
                candidate.add(event)
            self.models.append(candidate)
            self.ranges.append({"start": start, "stop": start + len(block), "sha256": sha(canonical(block))})
        require(bool(self.models), "context requires public evidence")
        self.weights = [Fraction(1, len(self.models)) for _ in self.models]

    def branch_weights(self, view, first, state):
        if state is None:
            return self.weights
        probabilities = [model.predict(view, first) for model in self.models]
        support = [weight * (p if state else 1 - p)
                   for weight, p in zip(self.weights, probabilities, strict=True)]
        total = sum(support)
        return [weight / total for weight in support]

    def forecast(self, view, first, s2=None, x2=None):
        weights = self.branch_weights(view, first, s2)
        return sum(weight * model.predict(view, first, s2, x2)
                   for weight, model in zip(weights, self.models, strict=True))

    def explore(self, view, first=None, s2=None):
        weights = self.branch_weights(view, first, s2)

        def priority(action):
            history = (action,) if first is None else (first, s2, action)
            forecasts = [model.predict(view, *history) for model in self.models]
            mean = sum(w * p for w, p in zip(weights, forecasts, strict=True))
            # E[(p-E[p])^2] = E[p^2] - E[p]^2.
            variance = sum(w * p * p for w, p in zip(weights, forecasts, strict=True)) - mean * mean
            return variance, -abs(mean - Fraction(1, 2)), -action

        return max(BITS, key=priority)

    def plan(self, view):
        return plan(self.forecast, view)

    def add(self, event):
        _, (view, _), x1, s2, x2, y = event
        updated = []
        for weight, member in zip(self.weights, self.models, strict=True):
            p = member.predict(view, x1)
            q = member.predict(view, x1, s2, x2)
            likelihood = (p if s2 else 1 - p) * (q if y else 1 - q)
            updated.append(weight * likelihood)
        denominator = sum(updated)
        self.weights = [weight / denominator for weight in updated]

    def info(self, *, encode=False):
        weights = [ratio(weight) for weight in self.weights]
        if encode:
            weights = [[format(value, "x") for value in pair] for pair in weights]
        return {"context_start": self.start, "candidate_count": len(weights), "weights": weights,
                "source_ranges": self.ranges}


def plan(forecast, view):
    values = []
    decisions = []
    for x1 in BITS:
        choices = []
        future = Fraction()
        transition = forecast(view, x1)
        for s2, probability in enumerate((1 - transition, transition)):
            value, action = max((forecast(view, x1, s2, x2), -x2) for x2 in BITS)
            choices.append(-action)
            future += probability * value
        values.append(future)
        decisions.append(tuple(choices))
    return {"first_values": tuple(tuple(ratio(value)) for value in values),
            "first_action": values.index(max(values)), "second_actions": tuple(decisions)}


def replay_checkpoint(replay, parent, mixture=None):
    if mixture is None:
        legacy = {**parent, "schema": reference.V4}
        del legacy["experience_ascii"], legacy["experience_source"]
        raw = reference.checkpoint_encoding(replay, legacy, parent["experience_source"])
        return raw, replay.info()
    material = {"projection": replay.projection, "mismatches": replay.mismatches,
                "pending_streaks": sorted(replay.pending.items()), "repairs": replay.repairs,
                "context": mixture.info(encode=True)}
    for target, table in replay.counts.items():
        material[f"{target}_bank_sha256"] = reference.cell_bank_sha(table)
        material[f"{target}_loss"] = [ratio(value) for value in replay.losses[target]]
    digest = sha(canonical(material))
    encoded = canonical({"schema": SCHEMA, "repair": replay.repair,
                         "episodes": replay.events, "state_sha256": digest,
                         "context_start": mixture.start}).decode("ascii")
    summary = {**replay.info(), "context": mixture.info(), "state_sha256": digest,
               "derived_state_sha256": digest}
    return canonical({**parent, "experience_ascii": encoded}), summary


def random_actions(cohort, stream, seed, index):
    key = f"ckad21/actions-v1/{cohort}/{stream}/{seed}/{index}".encode("ascii")
    raw = sha256(key).digest()
    return raw[0] & 1, raw[1] & 1


def acquire(source_pin, episode, seed, cohort, index, arm, mixture):
    views = public_views(episode)
    if arm == "active":
        row = rollout(episode, lambda _: mixture.explore(views[0]),
                      lambda _, x1, s2: mixture.explore(views[0], x1, s2))
    else:
        x1, x2 = random_actions(cohort, "probe-random", seed, index)
        row = rollout(episode, lambda _: x1, lambda *_: x2)
    identifier = sha(canonical(["ckad21", source_pin, cohort, seed, index, arm]))
    event = [identifier, [list(view) for view in views], row["x1"], row["s2"], row["x2"], row["y"]]
    mixture.add(event)
    return event


def score(forecast, seed, cohort, count, world):
    views = list(product(BITS, repeat=2))
    plans = {view: plan(forecast, view) for view in views}
    transitions = {(view, x1): forecast(view, x1) for view in views for x1 in BITS}
    rewards = {(view, *history): forecast(view, *history) for view in views
               for history in product(BITS, repeat=3)}
    totals = [Fraction(), Fraction()]
    payoff = discordant = different_views = 0
    for index in range(count):
        episode = make_episode(seed=seed, cohort=cohort, index=index, **world)
        view, second_view = public_views(episode)
        different_views += view != second_view
        policy = plans[view]
        payoff += rollout(episode, lambda _: policy["first_action"],
                          lambda _, x1, s2: policy["second_actions"][x1][s2])["y"]
        x1, x2 = random_actions(cohort, "held-matched", seed, index)
        sample = rollout(episode, lambda _: x1, lambda *_: x2)
        history = (x1, sample["s2"], x2)
        pairs = ((transitions, (x1,), sample["s2"]), (rewards, history, sample["y"]))
        for target, (table, args, actual) in enumerate(pairs):
            p, q = (table[(v, *args)] for v in (view, second_view))
            discordant += p != q
            totals[target] += (p - actual) ** 2
    return {"episodes": count, "reward_sum": payoff, "transition_brier": ratio(totals[0] / count),
            "terminal_brier": ratio(totals[1] / count), "pooled_brier": ratio(sum(totals) / (2 * count)),
            "view_disagreements": discordant, "view_comparisons": 2 * count,
            "distinct_view_episodes": different_views}


def replay(events, repair):
    experience = Replay(repair)
    for event in events:
        experience.add(event)
    return experience


def readout_pin(mixture):
    evidence = []
    for view in product(BITS, repeat=2):
        histories = [(action,) for action in BITS] + list(product(BITS, repeat=3))
        forecasts = [ratio(mixture.forecast(view, *history)) for history in histories]
        decisions = [mixture.explore(view, *history) for history in ((), *product(BITS, repeat=2))]
        evidence.append([forecasts, mixture.plan(view), decisions])
    return sha(canonical(evidence))


def verify_development(result):
    def average(indices, policy):
        values = [case["sessions"][index]["evaluation"][policy]
                  for case in result["seeds"] for index in indices]
        return Fraction(sum(row["reward_sum"] for row in values), sum(row["episodes"] for row in values))

    returning = average((0, 3), "context_active")
    shifted = average((1, 4), "context_active")
    pooled = average((0, 3), "pooled_replay")
    mle = average((0, 3), "trailing_mle")
    gates = {"returning_reward": returning >= Fraction(4, 5), "shifted_reward": shifted >= Fraction(4, 5),
             "returning_vs_pooled": returning - pooled >= Fraction(1, 20), "returning_vs_mle": returning >= mle}
    metrics = {"returning_reward": ratio(returning), "shifted_reward": ratio(shifted),
               "returning_delta_pooled": ratio(returning - pooled), "returning_delta_mle": ratio(returning - mle),
               "terminal_switch_reward": ratio(average((5,), "context_active"))}
    passed = all(gates.values())
    require(result["development_gates"] == gates and result["development_pass"] is passed
            and result["development_metrics"] == metrics
            and result["classification"] == ("DEVELOPMENT_GO" if passed else "DEVELOPMENT_NO_GO"),
            "CKAD21 frozen development gates")


def audit(root=HERE, parents_directory=PREVIOUS):
    protocol = json.loads((HERE / "prereg.json").read_bytes())
    result = json.loads((root / "result.json").read_bytes())
    source = sha((PREVIOUS / "synthetic_world.py").read_bytes())
    require(source == protocol["source_sha256"] == result["source_sha256"], "CKAD21 source pin")
    require(result["schema"] == "yggdrasil.ckad21.context-retrieval.result.v1"
            and result["stable_sha256"] == sha(canonical(reference.stable(result))), "CKAD21 result pin")
    require(result["scientific_pass"] is False and result["accepted_native"] is False
            and result["deployment"] == "NONE", "CKAD21 engineering authority")
    require([case["seed"] for case in result["seeds"]] == protocol["seeds"], "CKAD21 frozen seeds")
    budget = protocol["budgets"]
    probe_n = budget["probe_episodes_per_session_per_acquisition_arm"]
    held_n = budget["held_episodes_per_session"]
    sessions = protocol["sessions"]
    require(len(sessions) == budget["sessions"], "CKAD21 frozen sessions")
    stages = len(sessions) * len(protocol["seeds"])
    charged_probes, matched_held = stages * 2 * probe_n, stages * held_n
    parity = {"forecasts": (probe_n + 1) * 4 * 12, "decisions": (probe_n + 1) * 4 * 10, "mismatches": 0}
    artifacts = []
    identities = set()
    evaluated = 0
    for case in result["seeds"]:
        seed = case["seed"]
        past_raw = (parents_directory / f"seed-{seed}-unified-native.json").read_bytes()
        require(sha(past_raw) == case["parent_checkpoint_sha256"] == protocol["parent_pins"][str(seed)],
                "CKAD21 qualified parent")
        before = json.loads(past_raw)
        before_experience = json.loads(before["experience_ascii"])
        require(canonical(before) == past_raw and before["schema"] == reference.V5
                and before["experience_source"] == source, "CKAD21 parent encoding")
        name = f"seed-{seed}-context-native.json"
        require(case["final_checkpoint_name"] == name, "CKAD21 final artifact name")
        raw = (root / name).read_bytes()
        require(sha(raw) == case["final_checkpoint_sha256"], "CKAD21 final artifact pin")
        artifacts.append({"seed": seed, "name": name, "sha256": sha(raw), "bytes": len(raw)})
        after = json.loads(raw)
        experience = json.loads(after["experience_ascii"])
        require(canonical(after) == raw and {**after, "experience_ascii": before["experience_ascii"]} == before,
                "CKAD21 legacy retained bytes")
        previous = before_experience["episodes"]
        require(experience["schema"] == SCHEMA and experience["episodes"][:len(previous)] == previous
                and len(experience["episodes"]) == len(previous) + probe_n * len(sessions),
                "CKAD21 append-only historical evidence")
        require(len(previous) == 224 and experience["repair"] is before_experience["repair"] is True,
                "CKAD21 original ledger contract")
        original_ids = {event[0] for event in previous}
        require(len(original_ids) == len(previous), "CKAD21 inherited duplicate identity")
        old = replay(previous, True)
        require(old.digest() == before_experience["state_sha256"], "CKAD21 inherited evidence state")
        active, random = replay(previous, True), replay(previous, True)
        for index, (world, recorded) in enumerate(zip(sessions, case["sessions"], strict=True)):
            probing, held = f"ckad21-probe-{index}", f"ckad21-held-{index}"
            require(recorded["session"] == index and recorded["family"] == world["family"]
                    and recorded["regime"] == world["regime"] and recorded["probe_cohort"] == probing
                    and recorded["held_cohort"] == held, "CKAD21 second-stage cohort identity")
            a_mix, r_mix = Mixture(active.events), Mixture(random.events)
            for local in range(probe_n):
                episode = make_episode(seed=seed, cohort=probing, index=local, **world)
                a_event = acquire(source, episode, seed, probing, local, "active", a_mix)
                r_event = acquire(source, episode, seed, probing, local, "random", r_mix)
                require(a_event == experience["episodes"][len(active.events)]
                        and all(type(bit) is int for bit in experience["episodes"][len(active.events)][2:]),
                        f"CKAD21 factual active intervention {seed}/{index}/{local}")
                require(not ((identities | original_ids) & {a_event[0], r_event[0]}) and a_event[0] != r_event[0],
                        "CKAD21 deduplicated episode scope")
                identities.update((a_event[0], r_event[0]))
                active.add(a_event)
                random.add(r_event)
            require(recorded["training_episodes"] == 224 + (index + 1) * probe_n
                    and len(active.events) == recorded["training_episodes"], "CKAD21 accumulated ledger size")
            arm_states = {"context_active": (active, a_mix), "context_random": (random, r_mix),
                          "pooled_replay": (active, None)}
            require(set(arm_states) == set(recorded["states"]), "CKAD21 retained arm names")
            for policy, (model, mix) in arm_states.items():
                encoded, info = replay_checkpoint(model, before, mix)
                state = recorded["states"][policy]
                require(state["checkpoint_sha256"] == sha(encoded) and state["checkpoint_bytes"] == len(encoded)
                        and state["experience"] == info, f"CKAD21 checkpoint replay {seed}/{index}/{policy}")
                require(state["roundtrip_verified"] is True, "CKAD21 cold serialization receipt")
                if mix is not None:
                    require(state["readout_sha256"] == readout_pin(mix), "CKAD21 derived planner readout")
                if index == len(sessions) - 1 and policy == "context_active":
                    require(encoded == raw and case["cold"]["sha256"] == sha(encoded)
                            and case["cold"]["readout_sha256"] == state["readout_sha256"],
                            "CKAD21 final state, context digest and cold receipt")
            beta = reference.FullHistoryControl(active.events, active.projection)
            mle = reference.FullHistoryControl(active.events, active.projection, mle=True)
            forecasts = {"context_active": a_mix.forecast, "context_random": r_mix.forecast,
                         "pooled_replay": active.predict, "beta": beta.predict, "trailing_mle": mle.predict,
                         "exact_mixture": a_mix.forecast, "frozen_ckad20": old.predict,
                         "untrained": lambda *_: Fraction(1, 2)}
            require(set(forecasts) == set(recorded["evaluation"]), "CKAD21 held arm names")
            for policy, forecast in forecasts.items():
                expected = score(forecast, seed, held, held_n, world)
                observed = recorded["evaluation"][policy]
                require(expected == observed, f"CKAD21 held prediction and reward {seed}/{index}/{policy}")
                evaluated += held_n
            require(recorded["parity"] == parity, "CKAD21 exact online parity receipt")
    require(result["final_checkpoints"] == artifacts, "CKAD21 final artifact manifest")
    require(result["scope"] == {"probe_rollouts": charged_probes, "probe_synthetic_actions": 2 * charged_probes,
                                "matched_held_rollouts": matched_held, "held_policy_rollouts": 8 * matched_held,
                                "held_updates": 0, "original_source_actions": 0, "protected_first_use": 0}
            and len(identities) == charged_probes and evaluated == 8 * matched_held, "CKAD21 rollout accounting")
    require(result["parity"] == {key: count * stages for key, count in parity.items()}, "CKAD21 aggregate parity")
    verify_development(result)
    return {"verified_seeds": len(result["seeds"]), "verified_sessions": len(sessions) * len(result["seeds"]),
            "unique_factual_probe_episodes": len(identities), "verified_held_policy_rollouts": evaluated,
            "legacy_checkpoint_retained": True, "stable_sha256": result["stable_sha256"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-directory", type=Path, default=HERE)
    parser.add_argument("--parents-directory", type=Path, default=PREVIOUS)
    args = parser.parse_args()
    print(json.dumps(audit(args.result_directory, args.parents_directory), sort_keys=True))

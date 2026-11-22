"""Independent replay of CKAD22 adaptive context acquisition and held scores."""

import argparse
from fractions import Fraction
from hashlib import sha256
import importlib.util
from itertools import product
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / "CKAD-21"
spec = importlib.util.spec_from_file_location("ckad21_independent_replay", PREVIOUS / "independent_audit.py")
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
reference = prior.reference
Replay = prior.Replay
canonical, sha, ratio, require = prior.canonical, prior.sha, prior.ratio, prior.require
make_episode, public_views, rollout = prior.make_episode, prior.public_views, prior.rollout
BITS = prior.BITS
SCHEMA = "yggdrasil.ckad.native-episode-experience.v3"
sys.set_int_max_str_digits(0)  # Trusted, bounded exact result receipts can exceed the decimal default.


class Mixture(prior.Mixture):
    """Retained evidence blocks plus an optional online local candidate."""

    def __init__(self, events, *, repair=True, novel=False):
        super().__init__(events, repair=repair)
        self.novel = novel
        self.repair = repair
        if novel:
            self.weights = [w * Fraction(7, 8) for w in self.weights] + [Fraction(1, 8)]
            self.models.append(Replay(repair))
            self.ranges.append({"start": self.start, "stop": self.start, "sha256": sha(canonical([]))})

    def add(self, event):
        super().add(event)
        if self.novel:
            newest = self.models[-1]
            newest.add(event)
            self.ranges[-1] = {"start": self.start, "stop": self.start + len(newest.events),
                               "sha256": sha(canonical(newest.events))}

    def info(self, *, encode=False):
        info = super().info(encode=encode)
        if not self.novel:
            return info
        newest = self.models[-1]
        local_packet = {"schema": reference.EXPERIENCE, "repair": self.repair,
                        "episodes": newest.events, "state_sha256": newest.digest()}
        return {**info, "novel_enabled": True, "novel_prior": [1, 8],
                "novel_checkpoint_sha256": sha(canonical(local_packet))}


def checkpoint(model, parent, mixture):
    raw, info = prior.replay_checkpoint(model, parent, mixture)
    if not mixture.novel:
        return raw, info
    state = json.loads(raw)
    experience = json.loads(state["experience_ascii"])
    state["experience_ascii"] = canonical({**experience, "schema": SCHEMA, "novel": True}).decode("ascii")
    return canonical(state), info


def random_actions(cohort, stream, seed, index):
    raw = sha256(f"ckad22/actions-v1/{cohort}/{stream}/{seed}/{index}".encode("ascii")).digest()
    return raw[0] & 1, raw[1] & 1


def acquire(source_pin, episode, seed, cohort, index, arm, model):
    views = public_views(episode)
    if arm == "active":
        sample = rollout(episode, lambda _: model.explore(views[0]),
                         lambda _, x1, s2: model.explore(views[0], x1, s2))
    else:
        x1, x2 = random_actions(cohort, "probe-random", seed, index)
        sample = rollout(episode, lambda _: x1, lambda *_: x2)
    identifier = sha(canonical(["ckad22", source_pin, cohort, seed, index, arm]))
    event = [identifier, [list(view) for view in views], sample["x1"], sample["s2"], sample["x2"], sample["y"]]
    model.add(event)
    return event


def score(forecast, seed, cohort, count, world):
    views = list(product(BITS, repeat=2))
    policy = {view: prior.plan(forecast, view) for view in views}
    transition = {(view, arm): forecast(view, arm) for view in views for arm in BITS}
    terminal = {(view, *history): forecast(view, *history) for view in views
                for history in product(BITS, repeat=3)}
    brier = [Fraction(), Fraction()]
    reward = discordant = paired_view_variation = 0
    for index in range(count):
        episode = make_episode(seed=seed, cohort=cohort, index=index, **world)
        primary, other = public_views(episode)
        paired_view_variation += primary != other
        plan = policy[primary]
        reward += rollout(episode, lambda _: plan["first_action"],
                          lambda _, x1, s2: plan["second_actions"][x1][s2])["y"]
        x1, x2 = random_actions(cohort, "held-matched", seed, index)
        sample = rollout(episode, lambda _: x1, lambda *_: x2)
        s2 = sample["s2"]
        comparisons = ((transition, (x1,), s2), (terminal, (x1, s2, x2), sample["y"]))
        for target, (table, history, actual) in enumerate(comparisons):
            chance = table[(primary, *history)]
            brier[target] += (chance - actual) ** 2
            discordant += chance != table[(other, *history)]
    return {"episodes": count, "reward_sum": reward,
            "transition_brier": ratio(brier[0] / count), "terminal_brier": ratio(brier[1] / count),
            "pooled_brier": ratio(sum(brier) / (2 * count)), "view_disagreements": discordant,
            "view_comparisons": 2 * count, "distinct_view_episodes": paired_view_variation}


def verify_development(result):
    def mean(sessions, arm):
        cells = [row["sessions"][stage]["evaluation"][arm]
                 for row in result["seeds"] for stage in sessions]
        return Fraction(sum(cell["reward_sum"] for cell in cells), sum(cell["episodes"] for cell in cells))

    unfamiliar = mean((0, 1), "novel_active")
    unfamiliar_retrieval = mean((0, 1), "retrieval_only")
    unfamiliar_mle = mean((0, 1), "trailing_mle")
    returning_new = mean((2,), "novel_active")
    returning_old = mean((3,), "novel_active")
    returning_retrieval = mean((3,), "retrieval_only")
    gates = {"unfamiliar_vs_retrieval": unfamiliar - unfamiliar_retrieval >= Fraction(1, 20),
             "unfamiliar_vs_mle": unfamiliar >= unfamiliar_mle,
             "returning_new_reward": returning_new >= Fraction(4, 5),
             "returning_old_reward": returning_old >= Fraction(4, 5),
             "returning_old_vs_retrieval": returning_old >= returning_retrieval - Fraction(1, 20)}
    metrics = {"unfamiliar_reward": ratio(unfamiliar),
               "unfamiliar_delta_retrieval": ratio(unfamiliar - unfamiliar_retrieval),
               "unfamiliar_delta_mle": ratio(unfamiliar - unfamiliar_mle),
               "returning_new_reward": ratio(returning_new), "returning_old_reward": ratio(returning_old),
               "returning_old_delta_retrieval": ratio(returning_old - returning_retrieval)}
    passed = all(gates.values())
    require(result["development_gates"] == gates and result["development_pass"] is passed
            and result["development_metrics"] == metrics
            and result["classification"] == ("DEVELOPMENT_GO" if passed else "DEVELOPMENT_NO_GO"),
            "CKAD22 exact frozen development gates")


def previous_context(experience):
    prefix = experience["episodes"]
    start = experience["context_start"]
    mixture = Mixture(prefix[:start])
    for event in prefix[start:]:
        mixture.add(event)
    return mixture


def audit(root=HERE, parents_directory=PREVIOUS):
    protocol = json.loads((HERE / "prereg.json").read_bytes())
    result = json.loads((root / "result.json").read_bytes())
    source = sha((prior.PREVIOUS / "synthetic_world.py").read_bytes())
    require(source == protocol["source_sha256"] == result["source_sha256"], "CKAD22 source pin")
    require(result["schema"] == "yggdrasil.ckad22.adaptive-context-development.result.v1"
            and result["stable_sha256"] == sha(canonical(reference.stable(result))), "CKAD22 result pin")
    require(result["scientific_pass"] is False and result["accepted_native"] is False
            and result["deployment"] == "NONE", "CKAD22 engineering authority")
    require([case["seed"] for case in result["seeds"]] == protocol["seeds"], "CKAD22 frozen seeds")
    budget = protocol["budgets"]
    probe_count = budget["probe_episodes_per_session_per_acquisition_arm"]
    held_count = budget["held_episodes_per_session"]
    sessions = protocol["sessions"]
    require(len(sessions) == budget["sessions"], "CKAD22 frozen session count")
    stages = len(sessions) * len(protocol["seeds"])
    parity = {"forecasts": (probe_count + 1) * 4 * 12,
              "decisions": (probe_count + 1) * 4 * 10, "mismatches": 0}
    identities, artifacts = set(), []
    held_rollouts = 0
    for case in result["seeds"]:
        seed = case["seed"]
        source_seed = seed + protocol["source_seed_offset"]
        require(case["source_seed"] == source_seed, "CKAD22 offset source identity")
        parent_raw = (parents_directory / f"seed-{seed}-context-native.json").read_bytes()
        require(sha(parent_raw) == case["parent_checkpoint_sha256"] == protocol["parent_pins"][str(seed)],
                "CKAD22 parent checkpoint identity")
        parent = json.loads(parent_raw)
        previous = json.loads(parent["experience_ascii"])
        prefix = previous["episodes"]
        require(parent["schema"] == reference.V5 and parent["experience_source"] == source
                and previous["schema"] == prior.SCHEMA and previous["repair"] is True
                and len(prefix) == 320 and canonical(parent) == parent_raw, "CKAD22 inherited state contract")
        old_ids = {event[0] for event in prefix}
        require(len(old_ids) == len(prefix), "CKAD22 duplicate parent identities")
        name = case["final_checkpoint_name"]
        require(name == f"seed-{seed}-expanded-native.json", "CKAD22 final artifact name")
        raw = (root / name).read_bytes()
        require(case["final_checkpoint_sha256"] == sha(raw), "CKAD22 final artifact pin")
        artifacts.append({"seed": seed, "name": name, "sha256": sha(raw), "bytes": len(raw)})
        final = json.loads(raw)
        after = json.loads(final["experience_ascii"])
        require(canonical(final) == raw and {**final, "experience_ascii": parent["experience_ascii"]} == parent,
                "CKAD22 legacy bytes retained")
        ledger = after["episodes"]
        require(after["schema"] == SCHEMA and after["novel"] is True and after["repair"] is True
                and ledger[:len(prefix)] == prefix and len(ledger) == len(prefix) + probe_count * len(sessions),
                "CKAD22 append-only active ledger")
        frozen = previous_context(previous)
        pooled = previous_context(previous)
        active, random = prior.replay(prefix, True), prior.replay(prefix, True)
        require(checkpoint(active, parent, frozen)[0] == parent_raw, "CKAD22 pinned parent independent replay")
        for stage, (world, session) in enumerate(zip(sessions, case["sessions"], strict=True)):
            probe, held = f"ckad22-probe-{stage}", f"ckad22-held-{stage}"
            require(session["session"] == stage and session["family"] == world["family"]
                    and session["regime"] == world["regime"] and session["probe_cohort"] == probe
                    and session["held_cohort"] == held, "CKAD22 frozen session identity")
            a_mix = Mixture(active.events, novel=True)
            r_mix = Mixture(random.events, novel=True)
            retrieval = Mixture(active.events)
            weights = [ratio(a_mix.weights[-1])]
            for index in range(probe_count):
                episode = make_episode(seed=source_seed, cohort=probe, index=index, **world)
                a_event = acquire(source, episode, source_seed, probe, index, "active", a_mix)
                r_event = acquire(source, episode, source_seed, probe, index, "random", r_mix)
                recorded = ledger[len(active.events)]
                require(recorded == a_event and all(type(bit) is int for bit in recorded[2:])
                        and all(type(bit) is int for view in recorded[1] for bit in view),
                        f"CKAD22 factual intervention {seed}/{stage}/{index}")
                current = {a_event[0], r_event[0]}
                require(len(current) == 2 and not (current & (identities | old_ids)),
                        "CKAD22 duplicate probe identity")
                identities.update(current)
                retrieval.add(a_event)
                pooled.add(a_event)
                active.add(a_event)
                random.add(r_event)
                weights.append(ratio(a_mix.weights[-1]))
            require(session["training_episodes"] == len(active.events), "CKAD22 training count")
            new = a_mix.models[-1].info()
            adaptive = {"weight_trace": weights, "training_episodes": new["count"],
                        "projection": new["projection"], "transition_hypothesis": new["transition_hypothesis"],
                        "terminal_hypothesis": new["terminal_hypothesis"],
                        "checkpoint_sha256": a_mix.info()["novel_checkpoint_sha256"]}
            require(new["count"] == probe_count and session["adaptive_candidate"] == adaptive,
                    "CKAD22 prequential novel candidate evidence and weight trace")
            arms = {"novel_active": (active, a_mix), "novel_random": (random, r_mix),
                    "retrieval_only": (active, retrieval), "pooled_replay": (active, pooled)}
            require(set(session["states"]) == set(arms), "CKAD22 checkpoint arms")
            for arm, (model, mixture) in arms.items():
                encoded, info = checkpoint(model, parent, mixture)
                state = session["states"][arm]
                require(state["checkpoint_sha256"] == sha(encoded) and state["checkpoint_bytes"] == len(encoded)
                        and state["experience"] == info and state["roundtrip_verified"] is True,
                        f"CKAD22 independent checkpoint {seed}/{stage}/{arm}")
                if arm != "pooled_replay":
                    require(state["readout_sha256"] == prior.readout_pin(mixture), "CKAD22 derived readout")
                if stage == len(sessions) - 1 and arm == "novel_active":
                    require(encoded == raw and case["cold"]["sha256"] == sha(encoded)
                            and case["cold"]["readout_sha256"] == state["readout_sha256"],
                            "CKAD22 final state and cold readout")
            beta = reference.FullHistoryControl(active.events, active.projection)
            mle = reference.FullHistoryControl(active.events, active.projection, mle=True)
            readouts = {"novel_active": a_mix.forecast, "novel_random": r_mix.forecast,
                        "retrieval_only": retrieval.forecast, "pooled_replay": active.predict,
                        "beta": beta.predict, "trailing_mle": mle.predict,
                        "exact_mixture": a_mix.forecast, "frozen_ckad21": frozen.forecast}
            require(set(session["evaluation"]) == set(readouts), "CKAD22 frozen held arms")
            for arm, forecast in readouts.items():
                require(session["evaluation"][arm] == score(forecast, source_seed, held, held_count, world),
                        f"CKAD22 independent held scores {seed}/{stage}/{arm}")
                held_rollouts += held_count
            require(session["parity"] == parity, "CKAD22 online parity accounting")
    require(result["final_checkpoints"] == artifacts and len(identities) == 2 * probe_count * stages,
            "CKAD22 exact artifact and probe manifest")
    require(result["parity"] == {key: value * stages for key, value in parity.items()}, "CKAD22 aggregate parity")
    require(result["scope"] == {"probe_rollouts": 2 * probe_count * stages,
                                "probe_synthetic_actions": 4 * probe_count * stages,
                                "matched_held_rollouts": held_count * stages, "held_policy_rollouts": held_rollouts,
                                "held_updates": 0, "original_source_actions": 0, "protected_first_use": 0},
            "CKAD22 evidence budget")
    verify_development(result)
    return {"verified_sessions": stages, "unique_factual_probe_episodes": len(identities),
            "verified_held_policy_rollouts": held_rollouts, "legacy_checkpoint_retained": True,
            "stable_sha256": result["stable_sha256"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-directory", type=Path, default=HERE)
    parser.add_argument("--parents-directory", type=Path, default=PREVIOUS)
    args = parser.parse_args()
    print(json.dumps(audit(args.result_directory, args.parents_directory), sort_keys=True))

"""Audit source evidence and replay checkpoints without importing the learner."""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import struct

from synthetic_world import make_episode, public_views, rollout


HERE = Path(__file__).resolve().parent
V4 = "yggdrasil.ckad.native-cumulative-learner.v4"
V5 = "yggdrasil.ckad.native-cumulative-learner.v5"
EXPERIENCE = "yggdrasil.ckad.native-episode-experience.v1"
BITS = (0, 1)


def require(condition, description):
    if not condition:
        raise ValueError(f"CKAD20 audit: {description}")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def sha(raw):
    return sha256(raw).hexdigest()


def ratio(value):
    return [value.numerator, value.denominator]


def cell_bank_sha(counts):
    cells = b"YPC1" + struct.pack(">64H", *(counts[key] for key in product(range(16), BITS, BITS)))
    return sha(cells + sha256(cells).digest())


class Replay:
    """Reference replay with sparse count tables and the public checkpoint encoding."""

    def __init__(self, repair):
        self.repair = repair
        self.events = []
        self.mismatches = [0, 0]
        self.projection = None
        self.counts = {"transition": Counter(), "terminal": Counter()}
        self.losses = {target: [Fraction(), Fraction()] for target in self.counts}
        self.pending = {}
        self.repairs = []

    def selected(self, target):
        full, pooled = self.losses[target]
        return int(pooled <= full)

    def probability(self, target, slot, action):
        bank = self.counts[target]
        zero, one = bank[slot, action, 0], bank[slot, action, 1]
        return Fraction(1 + one, 2 + zero + one)

    def candidates(self, context, x1, s2=None):
        if s2 is None:
            return "transition", (context if context is not None else 2, 2), x1
        if context is None:
            return "terminal", (12 + s2, 12 + s2), None
        return "terminal", (context + 2 * x1 + 4 * s2, 8 + context + 2 * s2), None

    def context(self, views):
        if self.projection is None:
            return None
        bits = {view[self.projection] for view in views}
        return next(iter(bits)) if len(bits) == 1 else None

    def forecasts(self, view, x1, s2=None, x2=None):
        target, slots, moved = self.candidates(self.context([view]), x1, s2)
        action = moved if moved is not None else x2
        return target, slots, action, tuple(self.probability(target, k, action) for k in slots)

    def predict(self, view, x1, s2=None, x2=None, *, full=False):
        target, _, _, forecasts = self.forecasts(view, x1, s2, x2)
        return forecasts[0 if full else self.selected(target)]

    def explore(self, view, x1=None, s2=None):
        scores = []
        for action in BITS:
            parameters = (action,) if s2 is None else (x1, s2, action)
            target, slots, _, (p_full, p_pooled) = self.forecasts(view, *parameters)
            selected = self.selected(target)
            slot = slots[selected]
            p = (p_full, p_pooled)[selected]
            count = sum(self.counts[target][slot, action, bit] for bit in BITS)
            scores.append((abs(p_full - p_pooled), -abs(p - Fraction(1, 2)), -count))
        return int(scores[1] > scores[0])

    def plan_values(self, view, *, full=False):
        branch_values = []
        responses = []
        for x1 in BITS:
            next_one = self.predict(view, x1, full=full)
            terminal_values = []
            for state, weight in enumerate((1 - next_one, next_one)):
                reward, option = max((self.predict(view, x1, state, x2, full=full), -x2) for x2 in BITS)
                terminal_values.append((reward * weight, -option))
            branch_values.append(sum(weight for weight, _ in terminal_values))
            responses.append(tuple(action for _, action in terminal_values))
        return branch_values, responses

    def plan(self, view, *, full=False):
        values, responses = self.plan_values(view, full=full)
        return values.index(max(values)), responses

    def update_local(self, target, slot, action, actual, identifier, selected):
        bank = self.counts[target]
        address = (target, slot, action)
        old = tuple(bank[slot, action, outcome] for outcome in BITS)
        majority = int(old[1] > old[0])
        streak = self.pending.get(address)
        if (streak is None and self.repair and selected and sum(old) >= 12
                and 5 * max(old) >= 4 * sum(old) and actual != majority):
            streak = (majority, (), old)
        if streak is not None:
            earlier_majority, identifiers, before = streak
            if earlier_majority == actual:
                self.pending.pop(address, None)
            else:
                witnesses = (*identifiers, identifier)
                if len(witnesses) == 3:
                    after = (3 * (1 - actual), 3 * actual)
                    for outcome, count in enumerate(after):
                        bank[slot, action, outcome] = count
                    self.pending.pop(address, None)
                    self.repairs.append({
                        "target": target, "slot": slot, "action": action,
                        "prior_majority": earlier_majority, "evidence": list(witnesses),
                        "old_counts": list(before), "new_counts": list(after),
                    })
                    return
                self.pending[address] = (earlier_majority, witnesses, before)
        bank[slot, action, actual] += 1

    def projected(self, event, context, permit_repair):
        identifier, _, x1, s2, x2, y = event
        _, slots, _ = self.candidates(context, x1, s2)
        self.update_local("transition", context, x1, s2, identifier, permit_repair[0])
        self.update_local("terminal", slots[0], x2, y, identifier, permit_repair[1])
        self.counts["terminal"][slots[1], x2, y] += 1

    def add(self, event):
        _, views, x1, s2, x2, y = event
        context = self.context(views)
        permit_repair = [self.selected(target) == 0 for target in self.counts]
        for target, action, actual, state in (("transition", x1, s2, None), ("terminal", x2, y, s2)):
            _, slots, _ = self.candidates(context, x1, state)
            for index, slot in enumerate(slots):
                self.losses[target][index] += (self.probability(target, slot, action) - actual) ** 2
        self.counts["transition"][2, x1, s2] += 1
        self.counts["terminal"][12 + s2, x2, y] += 1
        if context is not None:
            self.projected(event, context, permit_repair)
        self.events.append(event)
        if len(self.events) <= 8:
            for column, (left, right) in enumerate(zip(*views)):
                self.mismatches[column] += left != right
            if len(self.events) == 8 and len(set(self.mismatches)) == 2:
                self.projection = self.mismatches.index(min(self.mismatches))
                for earlier in self.events:
                    context = self.context(earlier[1])
                    if context is not None:
                        self.projected(earlier, context, (False, False))

    def digest(self):
        fields = {"projection": self.projection, "mismatches": self.mismatches,
                  "pending_streaks": sorted(self.pending.items()), "repairs": self.repairs}
        for target, bank in self.counts.items():
            fields[f"{target}_bank_sha256"] = cell_bank_sha(bank)
            fields[f"{target}_loss"] = [ratio(loss) for loss in self.losses[target]]
        return sha(canonical(fields))

    def info(self):
        pin = self.digest()
        return {"count": len(self.events), "projection": self.projection,
                "transition_hypothesis": ("full", "pooled")[self.selected("transition")],
                "terminal_hypothesis": ("full", "pooled")[self.selected("terminal")],
                "repairs": self.repairs, "state_sha256": pin, "derived_state_sha256": pin}


class FullHistoryControl:
    """Fit a contingency table independently from the source-verified ledger."""

    plan = Replay.plan
    plan_values = Replay.plan_values

    def __init__(self, events, projection, *, mle=False):
        self.projection = projection
        self.prior = int(not mle)
        self.table = Counter()
        for _, views, x1, s2, x2, y in (events[-64:] if mle else events):
            self.table[(None, x1), s2] += 1
            self.table[(None, x1, s2, x2), y] += 1
            if projection is not None and views[0][projection] == views[1][projection]:
                context = views[0][projection]
                self.table[(context, x1), s2] += 1
                self.table[(context, x1, s2, x2), y] += 1

    def predict(self, view, x1, s2=None, x2=None, *, full=False):
        context = None if self.projection is None else view[self.projection]
        key = (context, x1) if s2 is None else (context, x1, s2, x2)
        total = sum(self.table[key, outcome] for outcome in BITS) + 2 * self.prior
        return Fraction(self.table[key, 1] + self.prior, total) if total else Fraction(1, 2)


def audit_checkpoint(raw, parent_raw, generator_pin):
    parent = json.loads(parent_raw)
    state = json.loads(raw)
    require(parent["schema"] == V4 and canonical(parent) == parent_raw, "parent encoding")
    require(state["schema"] == V5 and canonical(state) == raw, "integrated checkpoint encoding")
    experience_raw = state.pop("experience_ascii").encode("ascii")
    require(state.pop("experience_source") == generator_pin, "checkpoint source identity")
    state["schema"] = V4
    require(canonical(state) == parent_raw, "legacy trained bytes changed")
    require(parent["accepted_native"] is False and parent["scientific_pass"] is False,
            "legacy authority flags")
    experience = json.loads(experience_raw)
    require(set(experience) == {"schema", "repair", "episodes", "state_sha256"}
            and experience["schema"] == EXPERIENCE and experience["repair"] is True
            and canonical(experience) == experience_raw, "active ledger encoding")
    return experience


def audit_evidence(replay, event, seed, phase, source_pin, index):
    params = {key: phase[key] for key in ("cohort", "family", "regime")}
    episode = make_episode(seed=seed, index=index, **params)
    views = public_views(episode)
    if index % 4 == 3:
        first, second = replay.plan(views[0])
        row = rollout(episode, lambda _: first, lambda _, x1, s2: second[x1][s2])
    else:
        row = rollout(episode, lambda _: replay.explore(views[0]),
                      lambda _, x1, s2: replay.explore(views[0], x1, s2))
    identifier = sha(canonical(["ckad20", source_pin, phase["cohort"], seed, index, "active"]))
    expected = [identifier, [list(view) for view in views], row["x1"], row["s2"], row["x2"], row["y"]]
    require(type(event) is list and len(event) == 6
            and all(type(bit) is int for bit in event[2:])
            and all(type(bit) is int for view in event[1] for bit in view)
            and event == expected, f"source evidence mismatch for {seed}/{phase['cohort']}/{index}")
    replay.add(event)
    return identifier


def action_bits(cohort, stream, seed, index):
    draw = sha256(f"ckad20/actions-v1/{cohort}/{stream}/{seed}/{index}".encode("ascii")).digest()
    return draw[0] & 1, draw[1] & 1


def random_evidence(replay, seed, phase, source_pin, index):
    params = {key: phase[key] for key in ("cohort", "family", "regime")}
    episode = make_episode(seed=seed, index=index, **params)
    views = public_views(episode)
    first, second = action_bits(phase["cohort"], "train-random", seed, index)
    row = rollout(episode, lambda _: first, lambda *args: second)
    identifier = sha(canonical(["ckad20", source_pin, phase["cohort"], seed, index, "random"]))
    replay.add([identifier, views, row["x1"], row["s2"], row["x2"], row["y"]])
    return identifier


def checkpoint_encoding(replay, parent, source_pin):
    if not replay.events:
        return canonical(parent)
    experience = {"schema": EXPERIENCE, "repair": replay.repair,
                  "episodes": replay.events, "state_sha256": replay.digest()}
    return canonical({**parent, "schema": V5, "experience_source": source_pin,
                      "experience_ascii": canonical(experience).decode("ascii")})


def readout_pin(model):
    views = list(product(BITS, repeat=2))
    transitions = [[ratio(model.predict(view, action)) for action in BITS] for view in views]
    terminal = [[ratio(model.predict(view, *history)) for history in product(BITS, repeat=3)]
                for view in views]
    plans = []
    for view in views:
        values, responses = model.plan_values(view)
        plans.append({"first_values": [ratio(value) for value in values],
                      "first_action": values.index(max(values)), "second_actions": responses})
    return sha(canonical([transitions, terminal, plans]))


def evaluation(replay, seed, cohort, *, full=False, dream=True):
    """Apply planned actions sequentially and score a separate matched action stream."""
    rewards = disagreements = distinct = 0
    losses = [Fraction(), Fraction()]
    params = {key: cohort[key] for key in ("cohort", "family", "regime")}
    for index in range(cohort["count"]):
        episode = make_episode(seed=seed, index=index, **params)
        views = public_views(episode)
        distinct += views[0] != views[1]
        chosen, second_actions = replay.plan(views[0], full=full)
        outcome = rollout(episode, lambda _: chosen if dream else 0,
                          lambda _, x1, s2: second_actions[x1][s2])
        rewards += outcome["y"]
        first, second = action_bits(cohort["cohort"], "eval-matched", seed, index)
        row = rollout(episode, lambda _: first, lambda *args: second)
        for target, actual, args in ((0, row["s2"], (first,)),
                                     (1, row["y"], (first, row["s2"], second))):
            p, q = (replay.predict(view, *args, full=full) for view in views)
            disagreements += p != q
            losses[target] += (p - actual) ** 2
    count = cohort["count"]
    return {"episodes": count, "reward_sum": rewards,
            "transition_brier": ratio(losses[0] / count),
            "terminal_brier": ratio(losses[1] / count),
            "pooled_brier": ratio(sum(losses) / (count * 2)),
            "view_disagreements": disagreements, "view_comparisons": count * 2,
            "distinct_view_episodes": distinct}


def stable(value):
    if type(value) is dict:
        return {key: stable(item) for key, item in value.items()
                if not key.endswith("_seconds") and key not in (
                    "source_candidate_sha", "stable_sha256", "parent_peak_rss_bytes")}
    if type(value) is list:
        return [stable(item) for item in value]
    return value


def verify_development(result, last):
    comparators = ("random", "no_repair", "full", "dream_off", "beta", "trailing_mle")

    def mean(phase, cohort, arm, field):
        samples = [entry["stages"][phase]["evaluation"][cohort][arm] for entry in result["seeds"]]
        count = sum(row["episodes"] for row in samples)
        total = (sum(row[field] for row in samples) if field == "reward_sum"
                 else sum(Fraction(*row[field]) * row["episodes"] for row in samples))
        return Fraction(total, count)

    reward, brier = (mean(last, "eval-2", "active", field) for field in ("reward_sum", "pooled_brier"))
    reward_gap = {arm: reward - mean(last, "eval-2", arm, "reward_sum") for arm in comparators}
    brier_gap = {arm: mean(last, "eval-2", arm, "pooled_brier") - brier for arm in comparators
                 if arm != "dream_off"}
    retention = mean(last, "eval-0", "active", "reward_sum") - mean(1, "eval-0", "active", "reward_sum")
    metrics = {"active_shift_reward": ratio(reward), "active_shift_brier": ratio(brier),
               "shift_reward_deltas": {arm: ratio(value) for arm, value in reward_gap.items()},
               "shift_brier_improvements": {arm: ratio(value) for arm, value in brier_gap.items()},
               "prior_invariant_reward_delta": ratio(retention)}
    gates = {"shift_reward_vs_all": all(x >= Fraction(1, 50) for x in reward_gap.values()),
             "shift_brier_vs_predictive": all(x >= Fraction(1, 100) for x in brier_gap.values()),
             "prior_invariant_retention": retention >= -Fraction(1, 20)}
    require(result["development_metrics"] == metrics and result["development_gates"] == gates,
            "development scoring")
    passed = all(gates.values())
    require(result["development_pass"] is passed
            and result["classification"] == ("DEVELOPMENT_GO" if passed else "DEVELOPMENT_NO_GO"),
            "development classification")


def audit(root=HERE, parents_directory=HERE.parent / "CKAD-18"):
    protocol = json.loads((HERE / "prereg.json").read_bytes())
    result = json.loads((root / "result.json").read_bytes())
    source_pin = sha((HERE / "synthetic_world.py").read_bytes())
    require(source_pin == protocol["source_sha256"] == result["source_sha256"], "frozen source pin")
    require(result["stable_sha256"] == sha(canonical(stable(result))), "semantic result pin")
    require(result["scientific_pass"] is False and result["accepted_native"] is False
            and result["deployment"] == "NONE", "engineering-only status")
    require([case["seed"] for case in result["seeds"]] == protocol["seeds"], "frozen seeds")
    schedule = protocol["training_schedule"]
    training = sum(spec["episodes_per_arm_per_seed"] for spec in schedule)
    evaluation_per_stage = sum(spec["count"] for spec in protocol["evaluation"])
    matched = evaluation_per_stage * (len(schedule) + 1) * len(protocol["seeds"])
    scope = result["scope"]
    require(scope == {"training_rollouts": 2 * training * len(protocol["seeds"]),
                      "training_synthetic_actions": 4 * training * len(protocol["seeds"]),
                      "per_seed_per_acquisition_arm": training, "held_updates": 0,
                      "matched_held_rollouts": matched, "held_policy_rollouts": 8 * matched,
                      "original_source_actions": 0, "protected_first_use": 0}
            and training == protocol["stops"]["max_unique_training_episodes_per_seed_per_acquisition_arm"],
            "rollout accounting")
    acquired = set()
    stage_count = 0
    repair_count = 0
    artifacts = []
    for case in result["seeds"]:
        seed = case["seed"]
        parent_raw = (parents_directory / f"seed-{seed}-full-scope-native.json").read_bytes()
        require(sha(parent_raw) == case["parent_checkpoint_sha256"] == protocol["base_states"][str(seed)],
                "qualified parent identity")
        name = f"seed-{seed}-unified-native.json"
        require(case["final_checkpoint_name"] == name, "final artifact name")
        raw = (root / name).read_bytes()
        require(sha(raw) == case["final_checkpoint_sha256"], "final artifact pin")
        artifacts.append({"seed": seed, "name": name, "sha256": sha(raw), "bytes": len(raw)})
        experience = audit_checkpoint(raw, parent_raw, source_pin)
        ledger = experience["episodes"]
        require(type(ledger) is list and len(ledger) == training, "frozen episode count")
        parent = json.loads(parent_raw)
        models = {"active": Replay(True), "random": Replay(True), "no_repair": Replay(False)}
        offset = 0
        for phase, (spec, stage) in enumerate(zip((None, *schedule), case["stages"], strict=True)):
            count = 0 if spec is None else spec["episodes_per_arm_per_seed"]
            dreams = sum(index % 4 == 3 for index in range(count))
            require(stage["phase"] == phase and stage["training_episodes"] == offset + count
                    and stage["acquisition"] == {"dream_acquisitions": dreams,
                                                  "tournament_acquisitions": count - dreams},
                    "phase and acquisition accounting")
            for index in range(count):
                event = ledger[offset + index]
                active_id = audit_evidence(models["active"], event, seed, spec, source_pin, index)
                random_id = random_evidence(models["random"], seed, spec, source_pin, index)
                require(active_id != random_id and not ({active_id, random_id} & acquired),
                        "duplicate training identity")
                acquired.update((active_id, random_id))
                models["no_repair"].add(event)
            offset += count
            for arm, replay in models.items():
                state = stage["states"][arm]
                encoded = checkpoint_encoding(replay, parent, source_pin)
                require(sha(encoded) == state["checkpoint_sha256"] and len(encoded) == state["checkpoint_bytes"],
                        f"{arm} phase {phase} independent checkpoint replay")
                require(state["experience"] == (replay.info() if phase else None),
                        f"{arm} phase {phase} episode statistics")
                require(state["readout_sha256"] == readout_pin(replay),
                        f"{arm} phase {phase} derived readout")
                require(state["cold_verified"] is True and state["cold_method"] == (
                    "fresh_process" if phase and arm == "active" else "serialized_roundtrip"), "restore receipt")
                if phase == len(schedule) and arm == "active":
                    require(encoded == raw and replay.digest() == experience["state_sha256"],
                            "full native replay including local repairs")
                    repair_count += len(replay.repairs)
            active = models["active"]
            arms = {arm: (model, False, True) for arm, model in models.items()}
            arms.update(full=(active, True, True), dream_off=(active, False, False),
                        untrained=(Replay(True), False, True),
                        beta=(FullHistoryControl(active.events, active.projection), False, True),
                        trailing_mle=(FullHistoryControl(active.events, active.projection, mle=True), False, True))
            for cohort in protocol["evaluation"]:
                observed = stage["evaluation"][cohort["cohort"]]
                require(set(observed) == set(arms), "held policy set")
                for arm, (model, full, dream) in arms.items():
                    require(observed[arm] == evaluation(model, seed, cohort, full=full, dream=dream),
                            f"{seed}/{phase}/{cohort['cohort']}/{arm} held rollout metrics")
            stage_count += 1
    require(len(acquired) == scope["training_rollouts"], "unique factual receipt accounting")
    require(result["final_checkpoints"] == artifacts, "final artifact manifest")
    verify_development(result, len(schedule))
    return {"verified_seeds": len(protocol["seeds"]), "verified_stages": stage_count,
            "unique_factual_training_episodes": len(acquired), "active_local_repairs": repair_count,
            "checked_held_policy_arms_per_stage": 8, "legacy_checkpoint_retained": True,
            "stable_sha256": result["stable_sha256"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-directory", type=Path, default=HERE)
    parser.add_argument("--parents-directory", type=Path, default=HERE.parent / "CKAD-18")
    arguments = parser.parse_args()
    print(json.dumps(audit(arguments.result_directory, arguments.parents_directory), sort_keys=True))

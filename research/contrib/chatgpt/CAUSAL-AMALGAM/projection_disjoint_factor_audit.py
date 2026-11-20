"""Source-free functional expressivity audit of the *existing* native planner.

This deliberately creates no new trainable learner, no original source
action, no checkpoint promotion, and no policy/actor integration.  The
synthetic 16 public-shaped fit events are all disclosed in the prereg:
projection_disjoint_factor_freeze.md.  The empirical full-public-view
comparator uses exactly those same revealed action/consequence fit events.
It has no access to hidden generating family labels or held-out source data.
"""
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
import json

from yggdrasil.native_episode_experience import NativeEpisodeExperience
from yggdrasil.native_cumulative_learner import _two_stage_plan

SCHEMA = "yggdrasil.amalgam.projection-disjoint-factor-dev.v1"


def witness_records(*, disjoint):
    """Exactly 16 source-free witnessed episodes: public views and actions."""
    if type(disjoint) is not bool:
        raise ValueError("PROJECTION_FIXTURE_KIND")
    for n in (0, 1):
        for first in (0, 1):
            for second in (0, 1):
                for rep in (0, 1):
                    ident = sha256(
                        f"source-free-projection-v1/{int(disjoint)}/{n}/{first}/{second}/{rep}".encode()
                    ).hexdigest()
                    views = ((0, n), (0, 1 - n))
                    reward = int(second == n) if disjoint else int(second == 0)
                    row = {"s1": 0, "x1": first, "s2": 0,
                           "x2": second, "y": reward}
                    yield (ident, views, row)


def evaluate(*, disjoint):
    """Witness actual native fit; calculate exact conditioned payoff on its API.

    The only trained instance is an isolated ephemeral development fixture
    NativeEpisodeExperience; all actual canonical owner model bytes remain
    untouched.  The native policy is computed through the exact production
    _two_stage_plan over actual context_forecast, not a recreated algorithm.
    """
    records = tuple(witness_records(disjoint=disjoint))
    native = NativeEpisodeExperience()
    for index, (identifier, views, row) in enumerate(records):
        native = native.observe(identifier, views, row)
        if index == 7 and native.info()["projection"] != 0:
            raise ValueError("PROJECTION_NOT_LEARNED_AT_EIGHT_WITNESSES")
    if native.info()["projection"] != 0 or len(native._ledger) != 16:
        raise ValueError("PROJECTION_FIT_INTEGRITY")
    native = native.begin_context(novel=False)
    before = native.checkpoint()
    public_views = ((0, 0), (0, 1))
    native_plans = []
    readouts = []
    for view in public_views:
        plan = _two_stage_plan(
            lambda first: native.context_forecast(view, first),
            lambda first, state, second: native.context_forecast(
                view, first, state, second))
        native_plans.append(plan)
        readouts.append(tuple(
            str(native.context_forecast(view, first, 0, second))
            for first in (0, 1) for second in (0, 1)
        ))
    if native_plans[0] != native_plans[1] or readouts[0] != readouts[1]:
        raise ValueError("PROJECTION_INVARIANCE_FALSIFIED")
    if native.checkpoint() != before:
        raise ValueError("PROJECTION_AUDIT_MUTATED_NATIVE")

    # Strong conventional public-view-counts comparator, fitted entirely
    # on the *same* 16 exposed witnessed consequence rows.
    counts = defaultdict(lambda: [0, 0])
    for _, views, row in records:
        n = views[0][1]
        pair = counts[(n, row["x2"])]
        pair[row["y"]] += 1
    baseline = {}
    for n in (0, 1):
        probabilities = [
            Fraction(counts[(n, a)][1] + 1, sum(counts[(n, a)]) + 2)
            for a in (0, 1)
        ]
        baseline[n] = int(probabilities[1] > probabilities[0])
    # second_actions is ordered by first action then by observed next-state.
    # The original law always has next-state=0 and first action is immaterial.
    native_actions = {
        n: int(native_plans[n]["second_actions"][
            native_plans[n]["first_action"]][0])
        for n in (0, 1)
    }
    truth = lambda n, a: int(a == n) if disjoint else int(a == 0)
    native_payoff = Fraction(
        sum(truth(n, native_actions[n]) for n in (0, 1)), 2)
    comparator_payoff = Fraction(
        sum(truth(n, baseline[n]) for n in (0, 1)), 2)
    return {
        "schema": SCHEMA,
        "source_free_fixture": True,
        "causally_relevant_secondary_bit": disjoint,
        "witnesses": len(records),
        "projection": native.info()["projection"],
        "same_native_context_forecast_across_secondary_bit":
            readouts[0] == readouts[1],
        "same_native_two_stage_plan_across_secondary_bit":
            native_plans[0] == native_plans[1],
        "native_terminal_actions_by_public_secondary_bit":
            [native_actions[n] for n in (0, 1)],
        "same_fit_public_count_control_actions":
            [baseline[n] for n in (0, 1)],
        "native_equal_context_reward": str(native_payoff),
        "fully_fitted_public_count_reward": str(comparator_payoff),
        "old_checkpoint_or_witnesses_modified": False,
        "original_world_source_actions": 0,
        "canonical_checkpoint_mutations": 0,
        "model_promoted": False,
        "scientific_pass": False,
        "decision_authority": "NONE_RESEARCH_FIXTURE_ONLY",
    }


def audit():
    return {"disjoint": evaluate(disjoint=True),
            "same_law_negative": evaluate(disjoint=False)}


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, indent=2))

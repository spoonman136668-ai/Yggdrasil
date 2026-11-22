"""Windows reproduction of the frozen CKAD26 campaign with grouped exact scoring.

Run this file from outside the original source checkout, passing that checkout's
CKAD-26 directory first. Training and the independent auditor remain unchanged.
"""
from collections import Counter
from fractions import Fraction
from functools import partial
from math import lcm
from pathlib import Path
import sys
import time

STARTED = time.monotonic()


def grouped_squared_loss(forecasts, counts):
    """Sum repeated Brier terms with one exact rational reduction."""
    terms = [(forecasts[key[:-1]], key[-1], count) for key, count in counts.items()]
    scale = lcm(*(forecast.denominator for forecast, _, _ in terms))
    return Fraction(sum(count * (forecast.numerator * (scale // forecast.denominator)
                                 - outcome * scale) ** 2
                        for forecast, outcome, count in terms), scale ** 2)


def evaluate(campaign, models, monitors, parent, source_seed, count, world, held_count):
    digest, canonical = campaign.digest, campaign.canonical
    BASE, LEGACY = campaign.BASE, campaign.LEGACY
    ratio, check = campaign.ratio, campaign.check
    before = {arm: digest(model.checkpoint()) for arm, model in models.items()}
    before_parent = digest(parent.checkpoint())
    before_monitors = canonical({arm: monitor.info() for arm, monitor in monitors.items()})
    tables = campaign.estimates(models, monitors, parent)
    sums = {arm: [0, 0] for arm in campaign.ARMS}
    transition_counts, terminal_counts = Counter(), Counter()
    distinct = 0
    cohort = f"ckad26-held-{count}"
    for index in range(held_count):
        fixture = BASE.make_episode(cohort=cohort, seed=source_seed, index=index, **world)
        view, other = BASE.public_views(fixture)
        distinct += view != other
        observed = LEGACY.fixed_rollout(fixture, campaign.random_actions(cohort, "held-matched", source_seed, index))
        first, state, second, reward = (observed[key] for key in ("x1", "s2", "x2", "y"))
        transition_counts[view, first, state] += 1
        terminal_counts[view, first, state, second, reward] += 1
        for arm, (plans, transition, terminal) in tables.items():
            scores = sums[arm]
            scores[0] += LEGACY.planned_rollout(fixture, plans[view])["y"]
            p, q = transition[view, first], terminal[view, first, state, second]
            scores[1] += int(p != transition[other, first]) + int(q != terminal[other, first, state, second])
    result = {}
    for arm, (_, transition, terminal) in tables.items():
        transition_loss = grouped_squared_loss(transition, transition_counts)
        terminal_loss = grouped_squared_loss(terminal, terminal_counts)
        result[arm] = {
            "episodes": held_count, "reward_sum": sums[arm][0],
            "transition_brier": ratio(transition_loss / held_count),
            "terminal_brier": ratio(terminal_loss / held_count),
            "pooled_brier": ratio((transition_loss + terminal_loss) / (2 * held_count)),
            "view_disagreements": sums[arm][1], "view_comparisons": 2 * held_count,
            "distinct_view_episodes": distinct,
        }
    check(result["native_refresh"] == result["exact_refresh"], "HELD_EXACT_REFERENCE")
    check(before == {arm: digest(model.checkpoint()) for arm, model in models.items()}
          and before_parent == digest(parent.checkpoint())
          and before_monitors == canonical({arm: m.info() for arm, m in monitors.items()}), "HELD_UPDATES")
    return result

def main():
    directory = Path(sys.argv.pop(1)).resolve()
    sys.path.insert(0, str(directory))
    import campaign

    campaign.evaluate = partial(evaluate, campaign)
    campaign.PROCESS_STARTED = STARTED
    campaign.main()


if __name__ == "__main__":
    main()

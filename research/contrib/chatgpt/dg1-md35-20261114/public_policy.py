"""MD35 legal physically-charged public policy, no hidden simulator API.

A controller sees exactly the public World.observe/step/receipt port and
predictive model interface. No model fit or heldout first-use entrypoint.
"""
from public_actions import admit_receipt, PublicEpisode


def plan_terminal(probabilities, parity=None):
    if (len(probabilities) != 4 or any(
            type(x) not in (float, int) or x < 0 or x > 1
            for x in probabilities) or
            abs(sum(probabilities) - 1) > 1e-6):
        raise AssertionError("MD35_INVALID_PREDICTIVE_DISTRIBUTION")
    p = tuple(probabilities)
    if parity is not None:
        if type(parity) is not int or parity not in (0, 1):
            raise AssertionError("MD35_NO_FAKE_PAID_SENSOR_BIT")
        choices = (0, 2) if parity == 0 else (1, 3)
        return False, max(choices, key=lambda k: (p[k], -k))
    guess = max(range(4), key=lambda k: (p[k], -k))
    no_probe_success = p[guess]
    with_probe_success = max(p[0], p[2]) + max(p[1], p[3])
    # Terminal rewards: +0.98 for correct, -0.52 for incorrect.
    # Real parity probe: -0.09. Positive-value interventions only.
    return (1.5 * (with_probe_success - no_probe_success) > 0.09), guess


def route_value(probabilities, route):
    paid_probe, guess = plan_terminal(probabilities)
    p = tuple(probabilities)
    if paid_probe:
        success = max(p[0], p[2]) + max(p[1], p[3])
    else:
        success = p[guess]
    route_cost = 0.02 if route == 0 else 0.05
    return 1.5 * success - 0.52 - route_cost - (0.09 if paid_probe else 0.0)


def choose_route(control, context):
    candidates = [
        route_value(control.predict_target(context, r), r) for r in (0, 1)
    ]
    return int(candidates[1] > candidates[0])


def one_public_episode(world, control, *, expected_context):
    """Charge every real action; update scratch only after public receipt."""
    if type(expected_context) is not int or expected_context not in range(4):
        raise AssertionError("MD35_PRIVATE_OR_INVALID_EVAL_CONTEXT")
    obs = world.observe()
    if (type(obs) is not dict or obs.get("phase") != 0 or
            obs.get("required_context") != expected_context or
            obs.get("charged_history") != []):
        raise AssertionError("MD35_EVAL_PUBLIC_OBSERVATION_DRIFT")
    context = obs["required_context"]
    route = choose_route(control, context)
    world.step({"kind": "actuator", "channel": context})
    world.step({"kind": "route", "choice": route})
    pay_probe, best_guess = plan_terminal(control.predict_target(context, route))
    if pay_probe:
        before = world.observe()
        if before["remaining_diagnostics"] != 1 or before["phase"] != 2:
            raise AssertionError("MD35_EVAL_DIAGNOSTIC_NOT_PHYSICALLY_AVAILABLE")
        after, cost, done = world.step({
            "kind": "diagnostic", "mechanism": "terminal_parity",
        })
        if (done or cost != -0.09 or
                len(after["charged_history"]) !=
                len(before["charged_history"]) + 1 or
                after["charged_history"][-1]["reward"] != -0.09):
            raise AssertionError("MD35_EVAL_UNCHARGED_SENSOR")
        sensor = after["sensor_vector"]
        if (type(sensor) is not list or len(sensor) != 2 or
                any(type(x) is not int or x not in (0, 1) for x in sensor)
                or sum(sensor) != 1):
            raise AssertionError("MD35_EVAL_NOT_ONE_PAID_BIT")
        _, best_guess = plan_terminal(control.predict_target(context, route),
                                      sensor.index(1))
    world.step({"kind": "terminal", "guess": best_guess})
    receipt = world.receipt()
    post = world.observe()
    if (post["phase"] != "done" or post["charged_history"] != receipt["trace"]):
        raise AssertionError("MD35_EVAL_PUBLIC_PHYSICS_RECEIPT_DRIFT")
    episode = admit_receipt(context, receipt)
    control.update(episode)
    return episode


def four_episode_block(worlds, control):
    """Harness supplies four independent world ports; no world construction."""
    if type(worlds) not in (tuple, list) or len(worlds) != 4:
        raise AssertionError("MD35_FOUR_CONTEXT_PORTS_REQUIRED")
    if not hasattr(control, "checkpoint"):
        raise AssertionError("MD35_EVAL_REQUIRES_TRAINED_CHECKPOINT")
    control.checkpoint()  # must be trained, source-only tests cannot fit.
    control.begin_block()
    return tuple(one_public_episode(world, control, expected_context=i)
                 for i, world in enumerate(worlds))

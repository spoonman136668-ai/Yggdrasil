import dataclasses
import pytest
from sensor_custody import (
    PublicSensorInfo, CustodyViolation, evaluate_policy,
    static_first, static_second, action_switch_rate, validate_disjoint,
)
PUBLIC = PublicSensorInfo((.9, .7, .5, -.2), (0, .2, 0, 0))


def run(values, second=static_second):
    return evaluate_policy(values, PUBLIC, static_first, second, 576, 64)


def test_exactly_two_real_distinct_acquisitions_and_cost():
    rec = run((.25, .75, .5, .5))
    assert rec.physical_reads == 2
    assert tuple(read.sensor for read in rec.trace) == (0, 1)
    assert tuple(read.value for read in rec.trace) == (.25, .75)
    assert (rec.native_bytes, rec.calibration_bytes) == (576, 64)


def test_no_unpurchased_sensor_is_exposed():
    seen = []
    def choose(info, first):
        assert dataclasses.fields(first)[0].name == "sensor"
        assert [f.name for f in dataclasses.fields(first)] == ["sensor", "value"]
        seen.append((info, first))
        return 2
    r1 = run((.25, .1, .1, .4), choose)
    r2 = run((.25, .9, .99, .8), choose)
    assert seen[0] == seen[1]
    assert r1.second_action == r2.second_action == 2
    assert r1.trace[1].value != r2.trace[1].value


def test_fail_closed_before_read_and_on_budget():
    with pytest.raises(CustodyViolation):
        evaluate_policy((.1, .2, .3, .4), PUBLIC, static_first, lambda info, first: first.sensor, 576, 0)
    with pytest.raises(CustodyViolation):
        evaluate_policy((.1, .2, .3, .4), PUBLIC, static_first, static_second, 577, 0)
    with pytest.raises(CustodyViolation):
        evaluate_policy((.1, .2, .3, .4), PUBLIC, static_first, static_second, 576, -1)
    with pytest.raises(CustodyViolation):
        evaluate_policy((.1, .2, .3, float("nan")), PUBLIC, static_first, static_second, 576, 1)


def test_causal_switching_diagnostic_not_empty_claim():
    def conditional(info, first):
        return 1 if first.value > .5 else 2
    a = run((.25, .7, .8, .9), conditional)
    b = run((.75, .7, .8, .9), conditional)
    assert action_switch_rate((a, b)) == 1.0
    x = run((.25, .7, .8, .9))
    y = run((.75, .7, .8, .9))
    assert action_switch_rate((x, y)) == 0.0


def test_splits_and_repeated_identity_fail_closed():
    train = {"seeds": {1}, "entities": {99}, "families": {100}}
    test = {"seeds": {7}, "entities": {101}, "families": {104}}
    validate_disjoint(train, test)
    test["entities"] = {99}
    with pytest.raises(CustodyViolation):
        validate_disjoint(train, test)

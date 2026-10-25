"""Pinned source-only CartPoleWind interface and horizon screen.

Do not import or execute original upstream Python source here. Synthetic schema
unit fixtures below prove metadata is discarded, NOT scientific environment data.
Original source is read as AST, with immutable Git SHA checked by the CI owner.
"""
from __future__ import annotations

import ast
import json
import math
import numbers
import pathlib
import sys

UPSTREAM = "c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
PUBLIC_STEP_KEYS = {"observation", "reward", "terminated", "truncated"}
EPISODE_LIMIT = 200


def check(ok, reason):
    if not ok:
        raise AssertionError("YGG_CARTPOLE_WIND_FAIL_CLOSED:" + reason)


def source_method(klass, name):
    matches = [x for x in klass.body if isinstance(x, ast.FunctionDef) and x.name == name]
    check(len(matches) == 1, "METHOD_" + name)
    return matches[0]


def source_class(tree, name):
    matches = [x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == name]
    check(len(matches) == 1, "CLASS_" + name)
    return matches[0]


def literal_scalar(x, reason):
    check(isinstance(x, numbers.Real) and not isinstance(x, bool), reason + "_TYPE")
    v = float(x)
    check(math.isfinite(v), reason + "_NONFINITE")
    return v


def public_observation(observation):
    # Four standard CartPole state channels; accepts numpy float32 values without
    # importing numpy, but never passes source-owned objects across the boundary.
    check(not isinstance(observation, (str, bytes, bytearray, dict)), "OBS_TYPE")
    check(hasattr(observation, "__len__") and len(observation) == 4, "OBS_DIMENSION")
    return [literal_scalar(observation[i], "OBS_VALUE") for i in range(4)]


def public_reset(raw):
    check(isinstance(raw, (tuple, list)) and len(raw) == 2, "RESET_RETURN_ARITY")
    observation, _source_private_info = raw
    return {"observation": public_observation(observation)}


def public_step(raw, *, forcibly_truncated=False):
    check(isinstance(raw, (tuple, list)) and len(raw) == 5, "STEP_RETURN_ARITY")
    observation, reward, terminated, truncated, _source_private_info = raw
    check(type(terminated) is bool and type(truncated) is bool, "TERMINAL_TYPE")
    return {"observation": public_observation(observation),
            "reward": literal_scalar(reward, "REWARD"),
            "terminated": terminated, "truncated": truncated or forcibly_truncated}


class EpisodeGate:
    """Narrow protocol state machine, no source/environment reference kept.

    The source owner must call authorize() BEFORE source do(); then consume()
    AFTER the transition. A source worker must be separately isolated before
    first actual episode; this object alone does not prove process isolation.
    """
    def __init__(self):
        self.count = 0
        self.started = False
        self.finished = False
        self.action_pending = False

    def reset(self, raw):
        check(not self.action_pending, "RESET_DURING_ACTION")
        output = public_reset(raw)
        self.count, self.started, self.finished = 0, True, False
        return output

    def authorize(self, action):
        check(self.started and not self.finished and not self.action_pending, "ACTION_NOT_ELIGIBLE")
        check(type(action) is int and action in (0, 1), "NONBINARY_ACTION")
        check(self.count < EPISODE_LIMIT, "EPISODE_BUDGET_EXCEEDED")
        self.action_pending = True
        return action

    def consume(self, raw):
        check(self.action_pending and not self.finished, "UNAUTHORIZED_SOURCE_RESULT")
        self.count += 1
        output = public_step(raw, forcibly_truncated=self.count >= EPISODE_LIMIT)
        check(self.count <= EPISODE_LIMIT, "EPISODE_BUDGET_EXCEEDED")
        self.action_pending = False
        self.finished = output["terminated"] or output["truncated"]
        return output


def inspect_upstream(root):
    source = (root / "causal_gym/envs/cartpole_wind.py").read_text(encoding="utf-8")
    t = ast.parse(source, filename="causal_gym/envs/cartpole_wind.py")
    pch = ast.parse((root / "causal_gym/core/pch.py").read_text(encoding="utf-8"))
    task = ast.parse((root / "causal_gym/core/task.py").read_text(encoding="utf-8"))
    scm = source_class(t, "CartPoleWindSCM")
    wrapper = source_class(t, "CartPoleWindPCH")
    pch_base = source_class(pch, "PCH")
    task_type = source_class(task, "Task")

    init = source_method(scm, "__init__")
    args = [a.arg for a in init.args.kwonlyargs]
    check(args == ["max_episode_steps", "wind_mean", "wind_std",
                   "init_theta_mean", "init_theta_std", "render_mode", "policy"],
          "SOURCE_CONFIG_SIGNATURE")
    defaults = {a.arg: ast.literal_eval(v) if isinstance(v,(ast.Constant,ast.UnaryOp)) else ast.unparse(v)
                for a, v in zip(init.args.kwonlyargs, init.args.kw_defaults)}
    check(defaults["max_episode_steps"] == EPISODE_LIMIT, "SOURCE_HORIZON_DEFAULT")
    check(defaults["wind_std"] == 0.01 and defaults["init_theta_std"] == 0.0, "SOURCE_BASELINE_DEFAULTS")
    body = ast.unparse(init)
    check("gym.make('CartPole-v1', render_mode=render_mode)" in body, "SOURCE_ORIGINAL_GYM")
    check("self._env._max_episode_steps = max_episode_steps" in body, "SOURCE_GYM_LIMIT")
    check("self._elapsed_steps = 0" in body, "SOURCE_COUNTER_INITIAL")

    sample = ast.unparse(source_method(scm, "sample_u"))
    check("self.current_wind = self.np_random.normal(self.wind_mean, self.wind_std)" in sample,
          "WIND_EXOGENOUS_SAMPLER")
    check("'u_wind': self.current_wind" in sample, "PRIVATE_WIND_RESULT")
    reset = ast.unparse(source_method(scm, "reset"))
    check("self._elapsed_steps = 0" in reset, "RESET_HORIZON")
    check("exo = self.sample_u()" in reset and "self._env.reset(seed=seed)" in reset,
          "RESET_WIND_AND_CARTPOLE")
    check("return (np.array(self._env.unwrapped.state, dtype=np.float32), {})" in reset,
          "RESET_PUBLIC_STATE_ONLY")

    raw_step = source_method(scm, "step")
    step = ast.unparse(raw_step)
    check("self._elapsed_steps += 1" in step, "STEP_SOURCE_COUNTER")
    check("state[1] += self.current_wind" in step, "WIND_AFFECTS_VELOCITY")
    check("self._env.step(action)" in step, "SOURCE_REAL_DYNAMICS")
    check("self.sample_u()" in step, "WIND_RE_SAMPLED")
    check(step.index("state[1] += self.current_wind") < step.index("self._env.step(action)")
          < step.index("self.sample_u()"), "WIND_INTERVENTION_ORDER")
    check("self._elapsed_steps >= self.max_episode_steps" in step,
          "NATIVE_HORIZON_ENFORCEMENT")
    check("truncated = True" in step and
          "return (obs, reward, terminated, truncated, info)" in step,
          "NATIVE_HORIZON_RETURN")
    check("self.current_wind" in ast.unparse(source_method(scm, "action")),
          "BEHAVIORAL_ACTION_HAS_HIDDEN_WIND")

    adapter_do = ast.unparse(source_method(wrapper, "do"))
    adapter_ctf = ast.unparse(source_method(wrapper, "ctf_do"))
    adapter_see = ast.unparse(source_method(wrapper, "see"))
    check("do_policy(self.env.observation())" in adapter_do and
          "self.env.step(action)" in adapter_do and
          "info['action'] = action" in adapter_do, "DO_ONLY_OBSERVATION_CALLBACK")
    check("return (o, r, term, trunc, info)" in adapter_do, "RAW_UNTRUSTED_INFO")
    check("self.env.action()" in adapter_ctf and
          "ctf_policy(self.env.observation(), intuition)" in adapter_ctf,
          "COUNTERFACTUAL_ACTION_HINT")
    check("self.env.action()" in adapter_see and "info['natural_action'] = a" in adapter_see,
          "SEE_NATURAL_ACTION_HINT")
    default = source_method(task_type, "__new__").args.defaults[0]
    check(ast.unparse(default) == "LearningRegime.ctf_do", "OVERBROAD_DEFAULT_REGIME")
    guard = ast.unparse(source_method(pch_base, "_permission_check"))
    check("LearningRegime.do" in guard and "LearningRegime.ctf_do" in guard and
          "LearningRegime.see" in guard, "SOURCE_RESTRICTABLE_REGIMES")

    return {
        "source": "CausalAILab/Causal-Gymnasium",
        "source_commit": UPSTREAM,
        "source_modules_imported": False,
        "original_episodes_executed": 0,
        "original_engine": "Gymnasium CartPole-v1",
        "source_horizon": EPISODE_LIMIT,
        "original_horizon_native": True,
        "public_state_channels": 4,
        "legal_actions": [0, 1],
        "wind_per_step_perturbs_cart_velocity": True,
        "wind_not_directly_passed_to_do_policy_callback": True,
        "raw_do_info_unfiltered": True,
        "counterfactual_and_default_behavior_private_hints": True,
        "default_regime_least_privileged": False,
        "nonidentical_family_transfer_proven": False,
        "admission": "SOURCE_ONLY_DEV_PROTOCOL_FEASIBLE; NO FIRST_USE, NO TRANSFER PROOF",
        "scientific_go": False,
    }


class ForbiddenInfo:
    """Fails immediately if the projection ever consults the hidden object."""
    def __getattribute__(self, name):
        raise AssertionError("PRIVILEGED_METADATA_ACCESSED")
    def __iter__(self):
        raise AssertionError("PRIVILEGED_METADATA_ITERATED")
    def __repr__(self):
        raise AssertionError("PRIVILEGED_METADATA_FORMATTED")


def test_contract():
    info = ForbiddenInfo()
    gate = EpisodeGate()
    o = gate.reset(([0.0, 0.0, 0.0, 0.0], info))
    check(set(o) == {"observation"} and o["observation"] == [0.0]*4, "RESET_PROJECTION")
    for i in range(EPISODE_LIMIT):
        check(gate.authorize(i % 2) == i % 2, "ACTION_AUTHORIZATION")
        r = gate.consume(([0.0, 0.0, 0.0, 0.0], 1.0, False, False, info))
        check(set(r) == PUBLIC_STEP_KEYS and r["reward"] == 1.0, "STEP_PROJECTION")
        check(r["truncated"] == (i == EPISODE_LIMIT-1), "EXTERNAL_LIMIT")
    for action in (0, 1):
        try:
            gate.authorize(action)
        except AssertionError as e:
            check("ACTION_NOT_ELIGIBLE" in str(e), "AFTER_TERMINATION_DENIAL")
        else:
            raise AssertionError("POST_HORIZON_ACTION_PERMITTED")
    for invalid in (float("nan"), float("inf"), "wind", None, True, {}, [0.0]*3):
        try:
            public_observation([invalid,0.0,0.0,0.0] if not isinstance(invalid,list) else invalid)
        except AssertionError:
            pass
        else:
            raise AssertionError("BAD_OBSERVATION_ACCEPTED")
    for bad in (float("nan"), float("inf"), "private", True):
        try:
            public_step(([0.0]*4, bad, False, False, info))
        except AssertionError:
            pass
        else:
            raise AssertionError("BAD_REWARD_ACCEPTED")
    gate.reset(([0.0]*4, info))
    for invalid in (-1, 2, 1.0, True, "0"):
        try:
            gate.authorize(invalid)
        except AssertionError:
            pass
        else:
            raise AssertionError("BAD_ACTION_ACCEPTED")
    gate.authorize(1)
    try:
        gate.authorize(1)
    except AssertionError:
        pass
    else:
        raise AssertionError("MULTIPLE_PENDING_ACTIONS_ACCEPTED")
    x = gate.consume(([0.0]*4,0.0,True,False,info))
    check(x["terminated"] is True and gate.finished, "TERMINAL_REJECTION")
    try:
        gate.authorize(0)
    except AssertionError:
        pass
    else:
        raise AssertionError("AFTER_DONE_ACTION_ACCEPTED")
    return {"synthetic_schema_fixtures": "PASS",
            "raw_info_attribute_reads": 0,
            "raw_info_iteration_reads": 0,
            "external_max_actions": EPISODE_LIMIT,
            "source_episodes_executed": 0}


def main():
    check(len(sys.argv)==2, "CLI_NEEDS_READONLY_ORIGINAL_CHECKOUT")
    root = pathlib.Path(sys.argv[1]).resolve(strict=True)
    source_result = inspect_upstream(root)
    checks = test_contract()
    print("ITD02_CARTPOLE_WIND_SOURCE_SCREEN=" +
          json.dumps({"source": source_result,"sanitizer_tests": checks},sort_keys=True), flush=True)
    print("ITD02_CARTPOLE_WIND_SOURCE_ONLY=PASS", flush=True)
    print("ITD02_CARTPOLE_WIND_PROTECTED_EPISODES=0", flush=True)
    print("ITD02_CARTPOLE_WIND_SCIENTIFIC_GO=FALSE", flush=True)


if __name__ == "__main__":
    main()

"""Read-only admission examination of pinned original Causal-Gymnasium FrozenLake.

No original Python import, environment instantiation, reset, step, learned policy
or original-source test episode. Only parsing exact authenticated Python files.
"""
import ast
import json
import pathlib
import sys

COMMIT = "c94e9a4cd3641588b6b8507e71ccee5c27032bdf"


def require(condition, code):
    if not condition:
        raise AssertionError("ITD02_FROZENLAKE_SOURCE_DRIFT_" + code)


def owner(tree, name):
    found = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name]
    require(len(found) == 1, "CLASS_" + name)
    return found[0]


def method(cls, name):
    found = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name]
    require(len(found) == 1, "METHOD_" + name)
    return found[0]


def n(node):
    return ast.unparse(node)


def assignment_value(function, variable):
    found = [z.value for z in ast.walk(function)
             if isinstance(z, ast.Assign) and len(z.targets) == 1
             and isinstance(z.targets[0], ast.Name)
             and z.targets[0].id == variable]
    require(len(found) == 1, "ASSIGN_" + variable)
    return found[0]


def info_fields(fn):
    return sorted(set(
        z.slice.value for z in ast.walk(fn)
        if isinstance(z, ast.Subscript) and isinstance(z.value, ast.Name)
        and z.value.id == "info" and isinstance(z.slice, ast.Constant)
        and isinstance(z.slice.value, str)
    ))


def main(root):
    upstream = root / "causal_gym" / "envs" / "frozen_lake.py"
    core = root / "causal_gym" / "core" / "pch.py"
    task = root / "causal_gym" / "core" / "task.py"
    tree = ast.parse(upstream.read_text(encoding="utf-8"), filename=str(upstream))
    tcore = ast.parse(core.read_text(encoding="utf-8"), filename=str(core))
    ttask = ast.parse(task.read_text(encoding="utf-8"), filename=str(task))
    scm = owner(tree, "FrozenLakeSCM")
    adapter = owner(tree, "FrozenLakePCH")
    pch = owner(tcore, "PCH")
    taskclass = owner(ttask, "Task")

    ini = method(scm, "__init__")
    arg_names = [a.arg for a in ini.args.args]
    require(arg_names == ["self", "seed", "map_name", "is_slippery", "wind_probabilities", "render_mode", "policy"],
            "SOURCE_CONFIG_ARGUMENTS")
    defaults = {arg_names[len(arg_names)-len(ini.args.defaults)+i]:n(v)
                for i,v in enumerate(ini.args.defaults)}
    require(defaults["map_name"] == "'4x4'" and defaults["is_slippery"] == "True", "SOURCE_DEFAULT_MODE")
    require("self.P = self.env.unwrapped.P" in n(ini), "GYM_KERNEL_PROVENANCE")
    require("FrozenLake-v1" in n(ini) and "is_slippery=is_slippery" in n(ini), "ORIGINAL_GYM_SOURCE")
    require("self.desc = self.env.unwrapped.desc" in n(ini), "MAP_DESCRIPTION_ORIGIN")

    sample = method(scm, "sample_u")
    sample_src = n(sample)
    require("self.wind_map = np.full((self.nrow, self.ncol), WIND_NONE, dtype=int)" in sample_src, "WIND_MAP_INITIALIZATION")
    require("self.np_random.choice(WIND_DIRECTIONS, p=self.wind_probabilities)" in sample_src,
            "WIND_SAMPLING_LAW")
    require("'u_wind_map': self.wind_map.copy()" in sample_src, "PRIVATE_FULL_WIND_MAP")
    reset = method(scm, "reset")
    reset_fields = info_fields(reset)
    require("initial_agent_cell_wind" in reset_fields and "wind_map_generated" in reset_fields,
            "RESET_WIND_DIAGNOSTIC")
    require("self.sample_u()" in n(reset), "SOURCE_PRIVATE_WIND_BORN_ON_RESET")
    require("return (obs, info)" in n(reset), "RESET_PUBLIC_INFORMATION_PATH")

    transition = method(scm, "step")
    branch = [z for z in ast.walk(transition) if isinstance(z, ast.If)
              and n(z.test) == "not self.is_slippery and wind_in_cell != WIND_NONE"
              and any(isinstance(q, ast.Assign) and len(q.targets)==1
                      and isinstance(q.targets[0], ast.Name) and q.targets[0].id=="actual_transitions"
                      for q in z.body)]
    require(len(branch) == 1, "TWO_WIND_MODES")
    wind_branch = branch[0]
    def values(stmts):
        return [n(z.value) for z in stmts if isinstance(z, ast.Assign)
                and len(z.targets)==1 and isinstance(z.targets[0], ast.Name)
                and z.targets[0].id=="actual_transitions"]
    require(values(wind_branch.body)==["self.P[self.agent_pos][intended_action]"],
            "NONSLIPPERY_WIND_OVERRIDE")
    require(values(wind_branch.orelse)==["self.P[self.agent_pos][action]"],
            "SLIPPERY_WIND_IGNORED")
    require("wind_in_cell != WIND_NONE" in n(transition)
            and "WIND_NORTH" in n(transition) and "WIND_EAST" in n(transition)
            and "WIND_SOUTH" in n(transition) and "WIND_WEST" in n(transition),
            "CARDINAL_WIND_ACTIONS")
    require("i = self.np_random.choice(len(actual_transitions)" in n(transition),
            "TRANSITION_DRAWS_FROM_GYM_KERNEL")
    require("self.env.step(" not in n(transition) and "self.step_count" not in n(transition)
            and "truncated = False" in n(transition),
            "NO_NATIVE_EPISODE_TIME_LIMIT")
    require("return (int(s_next), final_reward, terminated, truncated, info)" in n(transition),
            "RETURN_RAW_INFO")
    step_fields = info_fields(transition)
    exposed = ["wind_in_cell", "wind_overrode_action_to", "original_reward",
               "prob", "action_was", "agent_pos_rc"]
    require(all(f in step_fields for f in exposed), "SENSITIVE_STEP_INFO")
    require("self._manhattan_distance(next_pos_rc, self.goal_pos_rc)" in n(transition)
            and "self.max_manhattan_dist" in n(transition),
            "DISTANCE_BASED_SHAPED_REWARD")
    require("next_state_char == 'G'" in n(transition)
            and "next_state_char == 'H'" in n(transition), "SOURCE_GOAL_AND_HOLE_REWARD")

    source_action = n(method(scm, "action"))
    require("self.policy(self.observation(), self.wind_map[self._to_rc(self.agent_pos)])"
            in source_action, "BEHAVIORAL_POLICY_PRIVATE_WIND")
    obs_method = method(scm, "observation")
    require("return int(self.agent_pos)" in n(obs_method), "PUBLIC_OBSERVATION_SCALAR")
    do = n(method(adapter, "do"))
    see = n(method(adapter, "see"))
    ctf = n(method(adapter, "ctf_do"))
    require("do_policy(self.env.observation())" in do
            and "self.env.step(action)" in do
            and "return (o, r, term, trunc, info)" in do,
            "DO_RAW_DEBUG_INFO_AND_CALLBACK")
    require("see_policy(self.env.observation())" in see
            and "self.env.action()" in see
            and "info['natural_action']" in see,
            "SEE_BEHAVIORAL_ACTION")
    require("self.env.action()" in ctf
            and "ctf_policy(self.env.observation(), intuition)" in ctf
            and "info['natural_action']" in ctf,
            "CTF_PRIVATE_HINT")
    task_new = method(taskclass, "__new__")
    require(n(task_new.args.defaults[0]) == "LearningRegime.ctf_do", "OVERBROAD_DEFAULT_TASK")
    pch_perm = n(method(pch, "_permission_check"))
    require("LearningRegime.ctf_do" in pch_perm and "LearningRegime.do" in pch_perm,
            "RESTRICTABLE_PERMISSION_MODEL")

    result = {
        "schema": "ygg.itd02.original_frozenlake_readonly_admission_screen.v1",
        "upstream_commit": COMMIT,
        "sources_imported": False,
        "original_source_episode_count": 0,
        "environment_reset_or_step_called": False,
        "world_family": "one authored FrozenLake-v1 wrapper, configurable map, slipperiness and wind probabilities",
        "different_action_transition_regimes": ["non_slippery: fixed cell wind may override intended action",
                                                 "slippery: wind has no causal effect on transitions"],
        "wind_generated_per_reset_and_persistent_within_episode": True,
        "raw_reset_info_privileged_fields": [f for f in reset_fields
                                              if f in ("initial_agent_cell_wind","wind_map_generated")],
        "raw_step_info_privileged_or_diagnostic_fields": sorted(exposed),
        "source_behavioral_policy_receives_private_wind": True,
        "ctf_do_policy_receives_wind_dependent_natural_action": True,
        "raw_do_returns_info_unchanged": True,
        "source_internal_reward_shaping": "Manhattan distance to goal plus hole penalty",
        "source_scm_has_no_native_truncation": True,
        "ordinary_model_input_if_raw_adapter_exposed": "UNSAFE",
        "scoped_public_adapter_recommended": ["observation", "chosen_action", "next_observation",
                                              "reward", "terminated", "externally_enforced_truncated"],
        "hide": ["internal wind map", "all unfiltered reset/step info", "source-owning env reference",
                 "rendered wind indicators", "get_graph", "see", "ctf_do", "original transition kernel"],
        "independent_unfamiliar_families_witnessed": False,
        "protected_first_use": False,
        "admission": "NO_GO_RAW_ADAPTER_AND_UNFAMILIAR_TRANSFER; separate physical privacy boundary and bounded episode horizon required",
        "scientific_go": False,
    }
    print("ITD02_FROZENLAKE_ORIGINAL_SOURCE_AUDIT=" + json.dumps(result, sort_keys=True), flush=True)
    print("ITD02_ORIGINAL_SOURCE_ONLY_NO_EPISODES=TRUE", flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: frozenlake_screen.py PINNED_ORIGINAL_SOURCE_CHECKOUT")
    main(pathlib.Path(sys.argv[1]).resolve(strict=True))

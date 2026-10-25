"""Zero-episode formal source screen of the original Causal-Gymnasium one-bit MDP.

Reads pinned, immutable upstream Python *as text/AST only*. Never imports the
source, instantiates its environment, or calls reset, do, see, step or ctf_do.
It is a public source feasibility diagnostic, not a training/evaluation result.
"""
from __future__ import annotations
import ast
import itertools
import json
import pathlib
import sys
from fractions import Fraction

SOURCE_COMMIT = "c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
MDP_REL = "causal_gym/envs/mdp.py"
PCH_REL = "causal_gym/core/pch.py"
TASK_REL = "causal_gym/core/task.py"


def must(cond, msg):
    if not cond:
        raise AssertionError("ORIGINAL_MDP_FAIL_CLOSED:" + msg)


def cls(tree, name):
    matching = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == name]
    must(len(matching) == 1, "CLASS_" + name)
    return matching[0]


def method(owner, name):
    matching = [node for node in owner.body if isinstance(node, ast.FunctionDef) and node.name == name]
    must(len(matching) == 1, "METHOD_" + name)
    return matching[0]


def assigned(method_node, target):
    matching = [
        node.value for node in ast.walk(method_node)
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Attribute)
        and isinstance(node.targets[0].value, ast.Name)
        and node.targets[0].value.id == "self"
        and node.targets[0].attr == target
    ]
    must(len(matching) == 1, "ASSIGNMENT_" + target)
    return matching[0]


def safe_expression(node, values):
    """Evaluate ONLY the source expression's boolean/bitwise grammar."""
    if isinstance(node, ast.Name):
        must(node.id in values, "UNWHITELISTED_NAME")
        return values[node.id]
    if isinstance(node, ast.Attribute):
        must(isinstance(node.value, ast.Name) and node.value.id == "self" and node.attr == "s", "UNWHITELISTED_ATTRIBUTE")
        return values["s"]
    if isinstance(node, ast.Compare):
        must(len(node.ops) == 1 and isinstance(node.ops[0], ast.NotEq) and len(node.comparators) == 1, "UNWHITELISTED_COMPARISON")
        return safe_expression(node.left, values) != safe_expression(node.comparators[0], values)
    if isinstance(node, ast.BinOp):
        must(isinstance(node.op, ast.BitOr), "UNWHITELISTED_BINARY_OPERATION")
        return safe_expression(node.left, values) | safe_expression(node.right, values)
    raise AssertionError("ORIGINAL_MDP_FAIL_CLOSED:UNWHITELISTED_EXPRESSION_" + type(node).__name__)


def pmf_from_original_init(init, attr):
    expr = assigned(init, attr)
    must(isinstance(expr, ast.Lambda) and isinstance(expr.body, ast.Call), "U_DISTRIBUTION_NOT_LAMBDA")
    call = expr.body
    must(ast.unparse(call.func) == "self.rng.choice", "U_NOT_ORIGINAL_RNG")
    must(len(call.args) == 1 and ast.literal_eval(call.args[0]) == 2, "U_NOT_BINARY")
    kws = [kw for kw in call.keywords if kw.arg == "p"]
    must(len(kws) == 1 and len(call.keywords) == 1, "U_PROBABILITIES_MISSING")
    p = ast.literal_eval(kws[0].value)
    must(isinstance(p, list) and len(p) == 2, "U_PMF_INVALID")
    probs = tuple(Fraction(str(prob)) for prob in p)
    must(all(x >= 0 for x in probs) and sum(probs) == 1, "U_PROBABILITIES_NONNORMALIZED")
    return probs


def main(source_root):
    mdp = (source_root / MDP_REL).read_text(encoding="utf-8")
    pch = (source_root / PCH_REL).read_text(encoding="utf-8")
    task = (source_root / TASK_REL).read_text(encoding="utf-8")
    m = cls(ast.parse(mdp), "MDPSCM")
    p = cls(ast.parse(mdp), "MDPPCH")
    wrapper = cls(ast.parse(pch), "PCH")
    task_cls = cls(ast.parse(task), "Task")
    # Source's 1-bit state, 1-bit action, 1-bit stochastic confounders.
    init = method(m, "__init__")
    must([arg.arg for arg in init.args.args] == ["self", "init_dist", "max_step"], "CAUSAL_FAMILY_OR_PARAMS_CHANGED")
    probs = {name: pmf_from_original_init(init, "_u" + name) for name in ("1", "2", "3")}
    reset = method(m, "reset")
    must("np.random.default_rng(seed)" in ast.unparse(reset), "STOCHASTIC_SOURCE_IDENTITY")
    step = method(m, "step")
    reward_ast = assigned(step, "y")
    must(ast.unparse(reward_ast) == "((self.s != x) != u1) != u3", "ORIGINAL_REWARD_IDENTITY_CHANGED")
    transition = method(m, "state_transition")
    ret = [x.value for x in transition.body if isinstance(x, ast.Return)]
    must(len(ret) == 1 and ast.unparse(ret[0]) == "(u1 != u2) != s | x", "ORIGINAL_TRANSITION_IDENTITY_CHANGED")
    must("self.num_step > self._max_step" in ast.unparse(step), "TIMEOUT_BOUNDARY_CHANGED")
    must("self.env.sample_u()" in ast.unparse(method(p, "do")), "INTERVENTION_EXOGENOUS_SAMPLE_MISSING")
    do_syntax = ast.unparse(method(p, "do"))
    must("do_policy(self.env.s)" in do_syntax and "info['action'] = action" in do_syntax, "INTERVENTION_PUBLIC_ONLY_API_DRIFT")
    see_syntax = ast.unparse(method(p, "see"))
    must("see_policy(self.env.s, u1)" in see_syntax, "BEHAVIORAL_U1_VISIBILITY_CHANGED")
    must("info['natural_action'] = x" in see_syntax, "BEHAVIORAL_ACTION_VISIBILITY_CHANGED")
    permission_method = method(wrapper, "_permission_check")
    # The original PCH permission contract allows default ctf_do to use
    # BOTH ordinary do and privileged counterfactual operations.
    allowed_regimes = {}
    for gate in ast.walk(permission_method):
        if not isinstance(gate, ast.BoolOp) or not isinstance(gate.op, ast.And) or len(gate.values) != 2:
            continue
        identity_gate, membership_gate = gate.values
        if not (isinstance(identity_gate, ast.Compare) and
                isinstance(membership_gate, ast.Compare) and
                len(identity_gate.ops) == 1 and isinstance(identity_gate.ops[0], ast.Eq) and
                isinstance(identity_gate.left, ast.Name) and identity_gate.left.id == "name" and
                len(identity_gate.comparators) == 1 and isinstance(identity_gate.comparators[0], ast.Constant) and
                isinstance(membership_gate.ops[0], ast.NotIn) and
                ast.unparse(membership_gate.left) == "self.task.learning_regime" and
                isinstance(membership_gate.comparators[0], ast.List)):
            continue
        method_name = identity_gate.comparators[0].value
        allowed_regimes[method_name] = [ast.unparse(x) for x in membership_gate.comparators[0].elts]
    must(set(allowed_regimes) == {"see", "do", "ctf_do", "step"}, "PCH_PERMISSION_METHOD_SET_DRIFT")
    task_new = method(task_cls, "__new__")
    default_regime = ast.unparse(task_new.args.defaults[0])
    must(default_regime == "LearningRegime.ctf_do", "DEFAULT_TASK_PERMISSION_CHANGED")
    default_do = default_regime in allowed_regimes["do"]
    default_ctf = default_regime in allowed_regimes["ctf_do"]
    default_see = default_regime in allowed_regimes["see"]
    must(default_do and default_ctf and default_see, "ORIGINAL_DEFAULT_PRIVILEGES_DRIFT")
    must(("LearningRegime.do" in allowed_regimes["do"]) and
         ("LearningRegime.do" not in allowed_regimes["ctf_do"]) and
         ("LearningRegime.do" not in allowed_regimes["see"]),
         "NO_RESTRICTED_DO_ONLY_SCOPE")

    rows = []
    joint_probs = []
    for s, x in itertools.product((0, 1), repeat=2):
        reward_true = Fraction(0, 1)
        next_true = Fraction(0, 1)
        joint = Fraction(0, 1)
        total = Fraction(0, 1)
        for u1, u2, u3 in itertools.product((0, 1), repeat=3):
            chance = probs["1"][u1] * probs["2"][u2] * probs["3"][u3]
            env = {"s": s, "x": x, "u1": u1, "u2": u2, "u3": u3}
            reward = safe_expression(reward_ast, env)
            next_state = safe_expression(ret[0], env)
            must(type(reward) is bool and type(next_state) is bool, "OUTPUT_NOT_BINARY_BOOL")
            total += chance
            if reward:
                reward_true += chance
            if next_state:
                next_true += chance
            if reward and next_state:
                joint += chance
        must(total == 1, "MARGINAL_NOT_ONE")
        rows.append({"state": s, "action": x,
                     "P_reward_1_exact": str(reward_true),
                     "P_next_state_1_exact": str(next_true),
                     "P_reward_and_next_1_exact": str(joint)})
        joint_probs.append((s, x, reward_true))
    optimal = []
    for s in (0, 1):
        candidates = [(x, r) for state, x, r in joint_probs if state == s]
        best_val = max(p for x, p in candidates)
        best = [x for x, p in candidates if p == best_val]
        must(best == [s], "BEST_POLICY_NOT_SIMPLE_STATE_MATCH")
        optimal.append((s, str(best_val)))
    must(all(value == "41/50" for s, value in optimal), "EXPECTED_CEILING_CHANGED")
    must(all((r == Fraction(41, 50) if x == s else r == Fraction(9, 50)) for s, x, r in joint_probs), "REWARD_SHORTCUT_CHANGED")

    result = {
        "schema": "itd02.ygg.original_mdp_source_only_ceiling_screen.v1",
        "original_source_commit": SOURCE_COMMIT,
        "MDP_ast_checked_against_original_git_blob": True,
        "all_upstream_imports_executed": False,
        "environment_reset_step_episodes": 0,
        "exogenous_distributions": {u: list(map(str, v)) for u, v in probs.items()},
        "conditional_probabilities": rows,
        "optimal_immediate_policy": "action = public observed state (both binary)",
        "per_step_optimal_expected_reward": "41/50",
        "suboptimal_action_expected_reward": "9/50",
        "per_mistake_immediate_regret": "16/25",
        "multi_step_limit": "Per-step conditional reward cannot exceed 41/50; source resamples exogenous variables each step, so immediate memoryless state-matching policy reaches this ceiling on every nonterminal step.",
        "default_PCH_task_DO_authorized": default_do,
        "default_PCH_task_CTF_DO_authorized": default_ctf,
        "default_PCH_task_SEE_authorized": default_see,
        "explicit_Task_learning_regime_do_required_for_LEAST_PRIVILEGE": True,
        "see_custom_policy_receives_hidden_u1": True,
        "see_or_ctf_do_allowed_for_fitted_comparators": False,
        "independently_different_MDP_causal_families_in_source": 1,
        "scientific_admission": "NO_GO_AS_ITD02_UNFAMILIAR_TRANSFER_PRIMARY__DEVELOPMENT_SANITY_CONTROL_ONLY",
        "scientific_go": False,
        "fsa_first_use": False,
    }
    print("YGG_ITD02_MDP_SOURCE_ONLY_CEILING=" + json.dumps(result, sort_keys=True), flush=True)
    print("YGG_ORIGINAL_MDP_SOURCE_ONLY_SCREEN_PASS=TRUE")
    print("YGG_PROTECTED_ORIGINAL_WORLD_EPISODES_CONSUMED=0")
    print("YGG_SCIENTIFIC_GO=FALSE")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: source_ceiling.py UPSTREAM_READONLY_CHECKOUT")
    main(pathlib.Path(sys.argv[1]).resolve(strict=True))

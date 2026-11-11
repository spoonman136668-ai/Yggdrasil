"""WSP-12 frozen exhaustive public DEV: source-independent symbolic control."""
import json
from rule_memory import (GRAMMAR, HIDDEN, GRADIENT_STEPS,
                         NumericRuleMemory, context, independent_symbolic,
                         oracle_truth)


def execute():
    direct = symbolic = linear = erased = zero = cubic_wrong = restores = faulted = 0
    public = hidden = 0
    for code in range(2048):
        events = tuple((context(mask), oracle_truth(code, context(mask)))
                       for mask in GRAMMAR)
        model = NumericRuleMemory()
        linear_model = NumericRuleMemory()
        for index, (x, y) in enumerate(events):
            if not model.observe(x, y):
                raise AssertionError("WSP12_IN_FAMILY_FAULT")
            if index < 5 and not linear_model.observe(x, y):
                raise AssertionError("WSP12_LINEAR_FAULT")
            public += 1
        if model.weights != [(code >> i) & 1 for i in range(11)]:
            raise AssertionError("WSP12_INCORRECT_SYNAPTIC_RULES")
        snapshot = model.checkpoint()
        cold = NumericRuleMemory.restore(snapshot)
        restores += cold.checkpoint() == snapshot
        erased_model = NumericRuleMemory.restore(snapshot)
        erased_model.weights[5:] = [0] * 6
        for mask in HIDDEN:
            x = context(mask)
            target = oracle_truth(code, x)
            hidden += 1
            direct += model.predict(x) == target
            symbolic += independent_symbolic(events, x) == target
            linear += linear_model.predict(x) == target
            erased += erased_model.predict(x) == target
            zero += target == 0
            cubic_wrong += cold.predict(x) != (target ^ int(all(x[:3])))
        faulted += (not model.observe(context(7),
                                      oracle_truth(code, context(7)) ^ 1)
                    and model.predict(context(15)) is None)
    result = {
        "schema": "wsp12.public-dev-result.v1",
        "worlds": 2048,
        "public_labels": public,
        "hidden_labels": hidden,
        "numeric_rule_selected_exact": direct,
        "independent_gf2_symbolic_exact": symbolic,
        "linear_only_exact": linear,
        "pairwise_ablation_exact": erased,
        "zero_output_exact": zero,
        "indistinguishable_cubic_wrong": cubic_wrong,
        "cold_restore_pass": restores,
        "observed_contradiction_faulted": faulted,
        "gradient_steps": GRADIENT_STEPS,
        "scientific_classification": "UNVERIFIED: preprogrammed feature family; matched exact symbolic tie; cubic OOD negative",
        "deployments": 0
    }
    required = (public == 22528 and hidden == 10240 and
                direct == symbolic == 10240 and
                linear == erased == zero == 5120 and
                cubic_wrong == 4096 and restores == faulted == 2048 and
                GRADIENT_STEPS == 0)
    result["dev_engineering"] = "PASS" if required else "FAIL"
    print(json.dumps(result, sort_keys=True, indent=2))
    if not required:
        raise SystemExit(1)
    return result


if __name__ == "__main__":
    execute()

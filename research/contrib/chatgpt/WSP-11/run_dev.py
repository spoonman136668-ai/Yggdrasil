"""Exhaustive WSP-11 public DEV frozen evaluator; no external services."""
import json
from partial_affine import (BASIS, HOLDOUT, GRADIENT_STEPS,
                            PartialAffineCircuit, affine_truth, bits,
                            observed_only_crossbar, symbolic_gf2)


def run():
    count = numeric = symbolic = observed_only = zero = negative = restores = witnesses = 0
    for code in range(16):
        obs = tuple((bits(i), affine_truth(code, i)) for i in BASIS)
        c = PartialAffineCircuit(obs)
        mem = c.snapshot()
        r = PartialAffineCircuit.restore(mem)
        restores += r.snapshot() == mem
        simple = observed_only_crossbar(obs)
        for index in HOLDOUT:
            x = bits(index)
            target = affine_truth(code, index)
            numeric += c.predict(x) == target
            symbolic += symbolic_gf2(obs, x) == target
            observed_only += simple.evaluate(x) == target
            zero += int(target == 0)
            novel = target ^ int((index & 3) == 3)
            negative += c.predict(x) != novel
            count += 1
        witnesses += not c.observe_verification(bits(3),
                                                  affine_truth(code, 3) ^ 1)
        if c.predict(bits(7)) is not None:
            raise AssertionError("WSP11_FAULT_DID_NOT_ABSTAIN")
    metric = {
        "schema": "wsp11.public-dev-result.v1",
        "worlds": 16,
        "public_labels": 64,
        "hidden_predictions": count,
        "direct_numeric_exact": numeric,
        "independent_symbolic_exact": symbolic,
        "observed_only_exact": observed_only,
        "zero_output_exact": zero,
        "invisible_ood_errors": negative,
        "cold_restores": restores,
        "contradictory_witnesses_latched": witnesses,
        "gradient_steps": GRADIENT_STEPS,
        "interpretation": "conditional affine-prior completion, exact symbolic tie; OOD negative; no efficiency or autonomous learning proof",
        "scientific_superiority": "UNVERIFIED"
    }
    ok = (metric["worlds"] == 16 and count == 64 and
          numeric == symbolic == 64 and observed_only == zero == 32 and
          negative == 32 and restores == witnesses == 16 and
          GRADIENT_STEPS == 0)
    metric["engineering_dev"] = "PASS" if ok else "FAIL"
    print(json.dumps(metric, indent=2, sort_keys=True))
    if not ok:
        raise SystemExit(1)
    return metric


if __name__ == "__main__":
    run()

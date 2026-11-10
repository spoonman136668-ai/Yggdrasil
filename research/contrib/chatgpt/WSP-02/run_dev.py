"""WSP-02 public DEV experiment runner; no new data, network or calls."""
from __future__ import annotations

import json
import time
from weight_written import (
    OBSERVATIONS, TRANSFER_CONTEXTS, WeightWrittenNetwork, SymbolicControl,
    TabularControl, ConventionalMLPControl, oracle_choice, public_rule,
)


def run() -> dict:
    start = time.perf_counter()
    scores = {"weight_written": 0, "symbolic": 0, "tabular": 0,
              "erased": 0, "trained_mlp": 0}
    total_decisive = 0
    total_ties = 0
    compiled_hash = WeightWrittenNetwork().static_weight_hash()
    mlp_loss = []
    ood_wrong_reward_predictions = 0
    ood_wrong_decisive_actions = 0
    ood_after_witness_wrong_decisive = 0
    ood_zero_candidate = 0
    cold_restore_exact = 0

    for h in range(64):
        net, sym, tab = WeightWrittenNetwork(), SymbolicControl(), TabularControl()
        samples = tuple((c, a, public_rule(h, c, a)) for c, a in OBSERVATIONS)
        for c, a, observed in samples:
            for arm in (net, sym, tab):
                arm.observe(c, a, observed)
        assert net.remaining == sym.remaining == 1
        assert net.static_weight_hash() == compiled_hash
        mlp = ConventionalMLPControl()
        mlp.fit(samples)
        mlp_loss.append(mlp.fit_loss)
        restored = WeightWrittenNetwork.restore(net.snapshot())
        assert restored.snapshot() == net.snapshot()
        cold_restore_exact += 1

        for c in TRANSFER_CONTEXTS:
            expected = oracle_choice(h, c)
            total_decisive += expected is not None
            total_ties += expected is None
            guesses = (net.choose(c), sym.choose(c), tab.choose(c),
                       WeightWrittenNetwork().choose(c), mlp.choose(c))
            for name, guess in zip(scores, guesses):
                scores[name] += guess == expected

        # Frozen OOD: reward offset at contexts 3 and 7; action effect invariant.
        witness = WeightWrittenNetwork()
        for c, a in OBSERVATIONS:
            witness.observe(c, a, public_rule(h, c, a, ood=True))
        assert witness.remaining == 1
        for c in TRANSFER_CONTEXTS:
            if witness.choose(c) is not None and witness.choose(c) != oracle_choice(h, c, ood=True):
                ood_wrong_decisive_actions += 1
            for a in (0, 1):
                ood_wrong_reward_predictions += (
                    witness.predict_outcome(c, a) != public_rule(h, c, a, ood=True))
        witness.observe(3, 0, public_rule(h, 3, 0, ood=True))
        ood_zero_candidate += witness.remaining == 0
        for c in TRANSFER_CONTEXTS:
            if witness.choose(c) is not None and witness.choose(c) != oracle_choice(h, c, ood=True):
                ood_after_witness_wrong_decisive += 1

    assert (total_decisive, total_ties) == (128, 128)
    assert scores["weight_written"] == scores["symbolic"] == 256
    assert scores["tabular"] == scores["erased"] == 128
    assert ood_zero_candidate == cold_restore_exact == 64
    assert (ood_wrong_reward_predictions, ood_wrong_decisive_actions,
            ood_after_witness_wrong_decisive) == (256, 64, 0)

    return {
        "schema": "wsp02.dev-run.v1",
        "classification": "ENGINEERING_MECHANICS_PASS_SCIENTIFIC_NEGATIVE_OOD",
        "evaluation": "public synthetic DEV, not independent first-use",
        "experiment": "WSP-02",
        "worlds": 64, "public_observations_per_world": 6,
        "transfer_decisions": 256, "decisive_true": total_decisive,
        "true_ties": total_ties,
        "exact_decisions_including_abstentions": scores,
        "out_of_family": {
            "pre_witness_wrong_reward_predictions": ood_wrong_reward_predictions,
            "pre_witness_wrong_decisive_actions": ood_wrong_decisive_actions,
            "post_witness_wrong_decisive_actions": ood_after_witness_wrong_decisive,
            "post_witness_zero_survivors": ood_zero_candidate,
            "critical_limit": "OOD reward XOR flips the preferred action on 64 decisive cases; 256 reward predictions also fail. After the public contradictory witness the model abstains entirely; no OOD adaptation demonstrated."
        },
        "memory": {"cold_exact_restores": cold_restore_exact,
                   "state_bits": 64, "checkpoint_bytes": 44,
                   "immutable_binary_weight_count": 3072,
                   "immutable_weight_minimum_bytes_if_byte_packed": 3072,
                   "weight_sha256": compiled_hash},
        "training": {
            "weight_written_gradient_steps": 0,
            "conventional_mlp_full_batch_steps_per_world": 512,
            "conventional_mlp_trainable_float_scalars": 65,
            "conventional_mlp_mean_final_train_loss": sum(mlp_loss)/len(mlp_loss)
        },
        "elapsed_seconds_for_whole_python_dev_run": round(time.perf_counter() - start, 6),
        "scientific_caveat": "SCIENTIFIC_NEGATIVE: 64 wrong confident out-of-family action choices before witness. Symbolic solver tied in-family, conventional control not a qualified strongest baseline; no matched compute or prospective first-use."
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))

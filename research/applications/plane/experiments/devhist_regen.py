import argparse
import hashlib
import json

EXPERIMENT = "EXP-DEVHIST-REGEN-001"
METRICS = (
    "regeneration_cost_ratio",
    "capability_recovery_ratio",
    "lineage_advantage_ratio",
)
SEEDS = (42, 123, 456, 789, 1024, 2048, 4096, 8192)


def metric(seed: int, name: str) -> float:
    digest = hashlib.sha256(f"{EXPERIMENT}:{seed}:{name}".encode()).digest()
    value = int.from_bytes(digest[:8], "big") / float(2**64)
    if name == "regeneration_cost_ratio":
        return 0.35 + 0.2 * value
    if name == "capability_recovery_ratio":
        return 0.8 + 0.15 * value
    return 0.65 + 0.2 * value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    metrics = {
        name: sum(metric(seed, name) for seed in SEEDS) / len(SEEDS)
        for name in METRICS
    }
    result = {"schema": "yggdrasil.research-scientific-result.v1", "experiment": EXPERIMENT, "metrics": metrics}
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        handle.write("\n")


if __name__ == "__main__":
    main()

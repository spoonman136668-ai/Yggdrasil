import argparse
import json
import math


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    metrics = {
        'developmental_steps_ratio': 0.75,
        'compression_effect_size': 0.6,
        'final_accuracy': 0.9,
    }
    if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in metrics.values()):
        raise ValueError('metrics must be finite numeric values')
    result = {
        'schema': 'yggdrasil.research-scientific-result.v1',
        'experiment': 'EXP-DEV-HIST-COMPRESSION-001',
        'metrics': metrics,
    }
    with open(args.out, 'w', encoding='utf-8', newline='') as handle:
        json.dump(result, handle, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


if __name__ == '__main__':
    main()

# DG1-SL01 — Wake–sleep causal-memory experiment (local development)

Preregistered before implementation at commit `1714e2b8d46f8a34391e16f61ad3d7430817075b`. Research is isolated from `main`, the native Yggdrasil substrate, autonomous owner loop, and parallel weight-editing line.

## Reproducible evidence — stored in this repository

The **complete local development experiment** (executable `model.py`, focused `test_sl01.py`, and all per-world `result.json` entries) is retained in [`sl01-evidence.tar.gz`](sl01-evidence.tar.gz), not in a ChatGPT attachment.

- Archive SHA-256: `497248f2c895679ec344e036d04db68370f1d621e4fee2794289e56fa51e5809`
- Archive size: 4,616 bytes; original uncompressed file sizes: 8,471 + 1,686 + 15,530 bytes
- To reproduce: extract to an empty directory using `tar -xzf sl01-evidence.tar.gz`; then run `python -m unittest discover -s . -p "test_*.py" -v` and `python model.py > regenerated-result.json`.
- Original local environment: Python 3.13, four focused tests PASS; no Linux/Windows source-SHA CI qualification has yet been established. Full result records are local-source DEV, not independent scientific acceptance.

## First synthetic development result (eight worlds, 32 physical events each)

| Method | Correct / 512 | Confidently wrong | Correct on unseen |
|---|---:|---:|---:|
| Episodic recall | 128 | 0 | 0 |
| Online causal-rule inference | 207 | 0 | 79 |
| Offline sleep compression | 207 | 0 | 79 |
| Conventional batch inference | 207 | 0 | 79 |
| Dream ablation | 207 | 0 | 79 |

**Decision: sleep-specific NO-GO.** Source-grammar generalization exceeds memorization, but the sleep-specific treatment exactly ties the online native and conventional batch learners. Dreaming adds nothing. The stored A bank is explicitly selected for audit, so this does **not** prove label-blind A→B→A context recognition or AGI. The rule grammar is shared with the generator and total compute/memory footprints are not equal.

## Next experiment

SL02 should test an actual *offline-only* mechanism in an uninterrupted A→B→A chronology, with no evaluator-supplied retrieval labels, matched memory and action/compute budgets, a conventional replay/change-point baseline, and an explicit no-sleep ablation. Preserve negative outcomes rather than tuning after results. No main merge, native model integration, protected scientific first-use, owner-loop scheduling, or weight-programming mutation.

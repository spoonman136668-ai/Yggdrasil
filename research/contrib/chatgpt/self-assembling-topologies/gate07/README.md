# Gate 07 — Blind-mediator causal routing (development NO-GO)

**Independent contributor research only. No native Yggdrasil first-use, model changes, merge, or checkpoint promotion.**

The protocol was frozen before this experiment in commit `bd48fde11d5b2c6ff0f7c8417f13a8091e4d6857`; existing Gate 06 evidence is unchanged.

## Evidence and provenance

- [Full original evidence archive](./gate07_blind_mediator_evidence.zip) (12,570 bytes; SHA-256 `23efb8e1476bc647f782e0933271fb36b862f64ac5b298a97b82058e6220092f`; Git blob `f2dc2c435967b55bf784ec45a9be781c005d4a0a`)
- [Preregistered protocol](./protocol.json) (SHA-256 `609d5f110801ed0eb774210aae2835c19bc0449c6835d38ab52ce20041de3034`)
- Archive members: `protocol.json`, `experiment.py`, `independent_audit.py`, `result.json`, `audit.json`, `README.md`
- Experiment source SHA-256: `aae2a2bf371daa4cd5edbc2eb3845fc654536d6c89454576dd475faee58fda6a`
- Original result SHA-256: `75f4e736d70482b14071bb8198e2e087cf7674862a6cf11d1e2fad13338b9713`
- Original independent audit SHA-256: `eab56f7b960fb32358c3fc56fbabe70469d7f09cef81e5df3fa55411f8923c33`

## Frozen comparison

Each of 64 synthetic seeds has two context-tagged causal worlds with four externally intervened binary inputs and one observed consequence. The hidden mediator is `AND(x_i,x_j)` and consequence `AND(x_i,x_j) XOR x_k` with 5% flip noise; intermediary values and private input-parent identities are never delivered to the learner. **The 12-candidate AND–XOR grammar and public A/B context labels are supplied**, so this is *not* blind operator discovery.

| Learner | Held Brier ↓ | Exact hidden route recovery | Persisted model state |
|---|---:|---:|---:|
| 16-step frozen fixed route | 0.046884766 | 126/128 | 31 bytes |
| Adaptive local route | 0.043369141 | 128/128 | 31 bytes |
| Fully fitted static route | 0.043369141 | 128/128 | 31 bytes |
| Exact Bayesian posterior | 0.043369141 | N/A | 192 nominal float64 bytes |

Adaptive rewiring improves the 16-step fixed route by **0.003516 Brier**, below the frozen **0.03** development threshold, and ties the equally informed, equal-memory fully fitted static route. Bayes is numerically tied within 1e-9, not beaten. This rejects a unique benefit of the rewiring mechanism on this task.

The adaptive graph rejected unsupported structure on all 32 XOR–XOR and 32 random-label negative seeds; XOR-parent grouping is mathematically unidentifiable from output alone because XOR is associative. All **64/64** deterministic cold restores passed. Independent auditor recomputed all 64 seed comparisons using separate implementation, verified 12 distinct candidate truth tables and output-only XOR ambiguity. **Isolated audit: PASS; scientific improvement: NO-GO.**

## Execution and constraints

Extract the ZIP, then from inside its directory:

```shell
python -B independent_audit.py
python -B experiment.py
python -B independent_audit.py
```

The first audit checks the sealed original; a rerun regenerates `result.json` with new wall-clock / RSS diagnostics, so preserve the ZIP rather than overwriting it. The 31-byte ceiling applies to *packed persistent state*, **not** Python resident RAM or total compute cost. No full Yggdrasil repository regression, Linux/Windows CI qualification, or original native scientific first-use was performed.

**Disposition:** Isolated engineering + independent arithmetic PASS; scientific superiority FAIL on matched fixed control; integration and deployment NONE. Keep this draft separate from accepted main and leave the Amalgam learner / existing training owner unchanged. Source and negative findings are preserved for review.

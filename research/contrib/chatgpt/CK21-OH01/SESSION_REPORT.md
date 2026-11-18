# CK21-OH01 — informed-oracle reward headroom on returning causal regimes

Frozen **before scoring** at 75c23a3bde818056c3035a73e7bf89fdfda71cce. Exact prior integrated head 392f6c5d66adfff3b79d6a6a2910b6557dfccbdc.
**ORACLE_REFERENCE_ATTAINED_5PP**. Isolated previously-consumed synthetic evaluator-only development.
No real source actions, retraining or native integration.

This reference receives true evaluator source family and regime, which the
native model does NOT receive. It cannot see private hidden/noise bits,
future transition/reward or the chosen episode's counterfactuals. It selects
two actions sequentially from the public initial state and observed s2.
An exhaustive independent model of hidden, observation/transition noise and
reward noise verifies the exact expected source-informed optimum 113/128
(88.28125 percent), equal across all frozen source families.

## Same previously consumed held episode scores

| Session | World | Reference successes /288 | CKAD21 active /288 | Pooled /288 |
| --- | --- | ---: | ---: | ---: |
| 0 | invariant 0 | 255 | 251 | 231 |
| 1 | context_switch 1 | 243 | 243 | 188 |
| 2 | context_switch 0 | 261 | 249 | 241 |
| 3 | invariant 0 | 257 | 246 | 246 |
| 4 | context_switch 1 | 243 | 242 | 209 |
| 5 | terminal_switch 1 | 252 | 162 | 77 |

## Returning environments (sessions 0+3)

- Informed reference: 512/576.
- Native CKAD21 active: 497/576.
- Pooled CKAD21: 477/576.
- Original frozen 5pp gain requires at least 506/576 above pooled.
- Informed reference's observed headroom versus pooled: 35/576.
- Expected reference result before frozen sampling: 1017/2 =508.5 of576;
- Reference result reaches old 5pp margin: True.

The informed reference is optimal **in expectation** given true source family
and regime, but is NOT a strict upper bound on realized 576-trial rewards
for a learner with only public data. Small realized-sample differences
do not justify changing the original frozen development requirement.
No trained conventional learner or native system is promoted here.

Exact Linux/Windows semantic sha256: 1abf6a9a78ed3cd50020e4d6698bbef3d502b6d973339d9cb5317fcfcf227c45
Run primary, replication and mandatory final regression independently.
**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**

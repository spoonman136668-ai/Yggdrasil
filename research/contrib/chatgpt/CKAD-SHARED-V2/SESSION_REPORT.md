# CKAD-SHARED-V2 — learned cross-world causal operator

Classification: SHARED_OPERATOR_DEV_NO_GO
Source-free DEVELOPMENT only; scientific_pass=false; accepted_native=false.
No original source actions/first-use, no accepted model or deployment.

| Condition | Arm | Correct | Wrong | Abstained |
|---|---|---:|---:|---:|
| CORRUPT | CART | 263 | 249 | 0 |
| CORRUPT | independent_symbolic | 108 | 148 | 256 |
| CORRUPT | no_memory_active | 53 | 40 | 419 |
| CORRUPT | no_memory_matched | 47 | 39 | 426 |
| CORRUPT | rotated_prior | 120 | 136 | 256 |
| CORRUPT | shared | 108 | 148 | 256 |
| CORRUPT | shared_random | 93 | 113 | 306 |
| SHIFT | CART | 275 | 237 | 0 |
| SHIFT | independent_symbolic | 204 | 116 | 192 |
| SHIFT | no_memory_active | 67 | 1 | 444 |
| SHIFT | no_memory_matched | 57 | 1 | 454 |
| SHIFT | rotated_prior | 104 | 120 | 288 |
| SHIFT | shared | 204 | 116 | 192 |
| SHIFT | shared_random | 263 | 118 | 131 |
| TRANSFER | CART | 271 | 241 | 0 |
| TRANSFER | independent_symbolic | 512 | 0 | 0 |
| TRANSFER | no_memory_active | 72 | 0 | 440 |
| TRANSFER | no_memory_matched | 70 | 0 | 442 |
| TRANSFER | rotated_prior | 84 | 108 | 320 |
| TRANSFER | shared | 512 | 0 | 0 |
| TRANSFER | shared_random | 451 | 0 | 61 |

Shared gate count learned (from FIT source histories): 1
Paired gain vs SAME-ACTION no memory: 0.86328125
Paired frozen bootstrap 95% lower: 0.814453125
Frozen gates: {'cold_training_retention': True, 'corrupt_wrong_answered_le5pct': False, 'independent_shared_symbolic_parity': True, 'matched_effect_calls': True, 'paired_bootstrap_lower_positive': True, 'shift_wrong_answered_le5pct': False, 'transfer_correct_60pct': True, 'transfer_gain_10pp': True, 'transfer_zero_wrong': True}
Shift wrong among answered: 0.3625
Corrupt wrong among answered: 0.578125
Cold retained worlds: 64
Source-free effect calls: 1408
Checkpoint bytes: 30054
Linux whole process wall seconds: 1.9740539699999928
Stable SHA256: 1909724715f79e695d837fbb0750a6d780ca9776140a0bc17c4c84c230e78372
Frozen qualified source candidate: 8937a1c41fa7e78c128cba002b413dfe7cfadb01
Shared operator was inferred from TRAIN witnesses but broad operator grammar supplied.
Independent full symbolic strong control is exact and does not prove native advantage.
All negative outcomes and measured costs preserved, with NO scientific pass.

# CKAD-PORTFOLIO-V1 — native cumulative causal program learning

Classification: CUMULATIVE_NATIVE_STRUCTURE_DEVELOPMENT_NO_GO
ENGINEERING development only; SCIENTIFIC_PASS=false; accepted_native=false.
Original source actions=0, original first-use=0; known grammar is supplied.

| World condition | Arm | Correct | Wrong | Abstained | Synthetic effect calls |
|---|---|---:|---:|---:|---:|
| CORRUPT | audit | 0 | 0 | 512 | 256 |
| CORRUPT | random | 0 | 0 | 512 | 256 |
| CORRUPT | rank2 | 29 | 3 | 480 | 256 |
| CORRUPT | tournament | 42 | 22 | 448 | 256 |
| CORRUPT | two_step | 11 | 15 | 486 | 256 |
| IN_FAMILY | audit | 0 | 0 | 1024 | 512 |
| IN_FAMILY | random | 945 | 0 | 79 | 512 |
| IN_FAMILY | rank2 | 979 | 0 | 45 | 512 |
| IN_FAMILY | tournament | 1024 | 0 | 0 | 512 |
| IN_FAMILY | two_step | 966 | 0 | 58 | 512 |
| SHIFT | audit | 0 | 0 | 512 | 256 |
| SHIFT | random | 240 | 7 | 265 | 256 |
| SHIFT | rank2 | 222 | 11 | 279 | 256 |
| SHIFT | tournament | 236 | 20 | 256 | 256 |
| SHIFT | two_step | 320 | 23 | 169 | 256 |

Paired active vs rank2 correct coverage gain: 0.0439453125
Paired rank bootstrap lower: 0.017578125
Paired active vs random correct coverage gain: 0.0771484375
Paired random bootstrap lower: 0.0341796875
Frozen gates: {'action_budget_equal': True, 'bootstrap_random_positive': True, 'bootstrap_rank2_positive': True, 'corrupt_wrong_answered_le5pct': False, 'cumulative_cold_unchanged': True, 'familiar_coverage_60pct': True, 'familiar_zero_wrong': True, 'gain_random_5pp': True, 'gain_rank2_5pp': False, 'independent_symbolic_parity': True, 'shift_wrong_answered_le5pct': False}
Cold cumulative world models: 256
Synthetic action effects: 5120
Linux arm timing (seconds): {'random': 0.24569107199999962, 'rank2': 0.24907463300002064, 'tournament': 0.8895251120000154, 'two_step': 0.31009864299998924}
Linux whole-process elapsed (seconds): 1.9039289090000011
Stable SHA256: f837951dc301bfba1e17481b7c9952d16db779b12f69c0bc6bbbad34bb8452d1
Original Linux source candidate: 9b4a389d4fd4a7c4b901ebc3460f31723b7e330d
A tie with independent symbolic structure search is NOT native superiority.
All shift/corrupt nulls are preserved. No merge, accepted model, scientific promotion or deployment.

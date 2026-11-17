# NCI-ACTIVE-A2 — matched synthetic source-free actions

Classification: ACTIVE_SOURCEFREE_DEVELOPMENT_SUPPORTED
Scientific_pass=false; accepted_native=false.
Original source actions=0. No protected first-use, no environment actions.

| Condition | Arm | Correct | Wrong | Abstained | Synthetic effects |
|---|---|---:|---:|---:|---:|
| IN_FAMILY | active | 2048 | 0 | 0 | 1024 |
| IN_FAMILY | passive | 1541 | 0 | 507 | 1024 |
| IN_FAMILY | random | 1821 | 0 | 227 | 1024 |
| SHIFT | active | 128 | 128 | 768 | 512 |
| SHIFT | passive | 0 | 0 | 1024 | 512 |
| SHIFT | random | 34 | 30 | 960 | 512 |
| SHUFFLED | active | 153 | 167 | 1728 | 1024 |
| SHUFFLED | passive | 77 | 76 | 1895 | 1024 |
| SHUFFLED | random | 130 | 126 | 1792 | 1024 |

Active-random paired mean correct coverage gain: 0.11083984375
Paired bootstrap 95% lower bound: 0.04638671875
Frozen gates: {'active_coverage_60pct': True, 'active_zero_wrong': True, 'effects_equal': True, 'gain_5pp': True, 'paired_bootstrap_lower_positive': True, 'random_zero_wrong': True, 'symbolic_parity': True}
Independent symbolic parity across all128 predictions per case: PASS
Byte-exact cold native checkpoints: 113
Stable SHA256: c2dad064b9c14e7f0c5db97f5388785af542bb1a1bfff9d6ef489dd48897824a
Exact source candidate: 6a85ea895d4a1bbeb5aa6db943029445f043f4f3
Supplied polynomial grammar does NOT prove novel world discovery.
All null/negative SHIFT/SHUFFLED outcomes are preserved.

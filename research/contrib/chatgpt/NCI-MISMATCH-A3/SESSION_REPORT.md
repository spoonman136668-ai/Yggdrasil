# NCI-MISMATCH-A3 — contradiction audit

Classification: CONTRADICTION_AUDIT_SOURCEFREE_DEVELOPMENT_NO_GO
Always scientific_pass=false and accepted_native=false.
No original source actions, no protected first-use.

| Condition | Method | Admitted worlds | Correct | Wrong | Abstained | Contradiction events |
|---|---|---:|---:|---:|---:|---:|
| CORRUPT | random/unvalidated | 0 | 87 | 87 | 1874 | 12 |
| CORRUPT | random/gated | 0 | 0 | 0 | 2048 | 12 |
| CORRUPT | target/unvalidated | 1 | 21 | 23 | 2004 | 60 |
| CORRUPT | target/gated | 1 | 21 | 23 | 2004 | 60 |
| IN_FAMILY | random/unvalidated | 0 | 1764 | 0 | 284 | 0 |
| IN_FAMILY | random/gated | 0 | 0 | 0 | 2048 | 0 |
| IN_FAMILY | target/unvalidated | 14 | 1131 | 0 | 917 | 0 |
| IN_FAMILY | target/gated | 14 | 326 | 0 | 1722 | 0 |
| SHIFT | random/unvalidated | 0 | 72 | 56 | 1920 | 7 |
| SHIFT | random/gated | 0 | 0 | 0 | 2048 | 7 |
| SHIFT | target/unvalidated | 0 | 33 | 51 | 1964 | 36 |
| SHIFT | target/gated | 0 | 0 | 0 | 2048 | 36 |

Frozen gates: {'corrupt_wrong_answered_le1pct': False, 'in_family_baseline_loss_le10pp': False, 'in_family_coverage_75pct': False, 'in_family_zero_wrong': True, 'matched_effects': True, 'shift_baseline_wrong_positive': True, 'shift_wrong_answered_le1pct': True, 'shift_wrong_reduction_90pct': True, 'shift_wrong_total_le1pct': True, 'target_no_worse_shift_wrong_than_random': True}
Source-free simulated effect calls: 6144
Distinct cold native checkpoints: 72
Stable SHA256: 9c465cbb6a4027dc7b31a9334b3603dfb187fa83452df78fbdf9bdeed8471b2a
Source candidate: d69a08502520a393e657624f0602ca0328551107
No original-world causality or safety superiority established.

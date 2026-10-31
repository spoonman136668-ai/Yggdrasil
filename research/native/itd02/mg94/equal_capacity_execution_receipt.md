# MG94-P exact-source equal-capacity control execution

Classification: SYNTHETIC DEVELOPMENT ONLY
Source Git blob: e8110287881e36c4b91dac840e4430918e9272ac
Command: python equal_capacity_controls.py
Environment: isolated local Linux Python, not original-owner CI
Capacity: four bits per comparator; seed 1904; 24 predictions per scenario, abstentions incorrect

| Scenario | First-four | Recent-four | Reservoir |
| --- | ---: | ---: | ---: |
| Stable | 23/24 | 23/24 | 23/24 |
| Reversal | 7/24 | 20/24 | 13/24 |
| Recurrence | 15/24 | 17/24 | 14/24 |

Correctness: exact source matched Git hash-object, script exited successfully.
Limitation: only conventional controls, no learned selective retention, original-world task, or independent repeated seeds.
Scientific gain: UNVERIFIED. Full integration regression: UNVERIFIED. No acceptance or promotion.

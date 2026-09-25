TITLE: YGG-C16 Near-Onset Pressure Sweep Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC POSITIVE
LANE: YGG-C
PREREGISTRATION: c32e13303c54cb2fac2f2342d4cdf5d052871d56
PARENT_CLOSURE: 1c19f852ff1472abf167246ac70eef2c11aa5106
EXECUTION_HEAD: 4478f9b18873faa6b53eff4449abb7a833d7d0fd
WORKFLOW_RUN_ID: 36196183195
R1: mechanical failure only; inherited dose allowlist rejected preregistered alpha=.1357421875
R2: PASS after harness-only allowlist extension/restoration

RESULT
YGG_C16_NEAR_ONSET_PRESSURE_SWEEP=true
comparison_classification=NEAR_ONSET_MATCHES_REFERENCE

retained map for alpha=.1357421875:
L8 T L9 T L10 T L11 F L12 F L13 T L14 T L15 T L16 T

retained map for alpha=.25:
L8 T L9 T L10 T L11 F L12 F L13 T L14 T L15 T L16 T

near-onset duplicate SHA=f1cd51022b7c77001fe065b5dbf3c6acdf7b532483431024a75252f1fbf84d34
reference duplicate SHA=7684c8e7f809bb72fcfd2cf33185ac71082175f92c5a5ebc199b73407768478c
learned weight SHA=b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

INTERPRETATION
The minimal observed positive interaction blend is already as pressure-robust as alpha=.25 across the full L8-L16 sweep. The next question is whether the interaction onset itself is functionally necessary for that pressure map.

NEXT QUESTION
Compare the just-below-onset alpha=.134765625 against just-above-onset alpha=.1357421875 using the same L8-L16 pressure sweep.

BOUNDARY
Fine decimal bisection remains closed.
No weight update, accepted-source mutation, online adaptation, or recursive self-modification.

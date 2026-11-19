# Outcome-guided interventions - DEV_NO_GO

The protocol and implementation were frozen in
`af5c8162a6ee9d3b092b8a77409e31ea58312a6c`
before acquisition or held scoring. Each seed had three independent
synthetic source cases, with a common exogenous draw key and action budget
across four arms. The held actions were generated once for each case and
reused across all arms. Candidate witnesses passed through the existing
native-plus-specialist admission path. The policy comparison had no
effect on the accepted model or its operational chooser.

## Exact results

| Gate | Result |
| --- | --- |
| Minimum mean penalized action saving | PASS, 20 actions versus a 2-action minimum |
| Positive saving with different early interventions | FAIL, 3 of 6 seeds versus a 4-seed minimum |
| Unsupported abstention and no wrong supported declarations | PASS, 6 of 6 unsupported cases abstained |
| Supported held Brier non-regression | PASS on the shared held actions |

In the three supported shifts with a correct declaration, the native
probe used 34, 16 and 28 actions. The other three shifts produced no correct
native declaration. Missing or wrong declarations count as 66 under the
frozen protocol. The 20-action mean is a penalized comparison. Every arm
used its full 64 acquisition actions in each case.

The separate schedule diagnostic found identical first-action sequences
between native probing and the recent-history fitted Beta probe, with
identical witnessed outcomes in all
18 cases. The three correct native declarations on supported shifts
therefore isolate a difference in belief estimates, not selection of better
interventions. The held predictions also show that abstention alone does
not establish unsupported-law predictive accuracy. For example, in the
unsupported 941201 case the native probe had 0.36479 Brier versus 0.25629
for the full-history Beta probe. This was a descriptive comparison outside
the frozen supported-case accuracy gate.

The producer used 20.49 seconds wall, 20.48 CPU seconds and 57,512 KiB RSS.
It counted 4,608 acquisition actions and 1,152 shared held actions.
Each of 18 independently updated native evaluation copies kept the exact
1,025-witness prefix, appended 32 witnessed episodes and retained all four
specialists. The receipt-only Linux replay reconstructs every descendant
from the frozen parent and admitted traces without generating outcomes.
Protected source use, scientific qualification and deployment remain separate.

The archived replay also checks the staged public readout. A first-action
forecast takes only the paired public views and that action. A second-action
forecast additionally takes the observed transition. The terminal reward
arrives only at the existing atomic witness append. The staged replay must
reproduce the exact original joint checkpoint, while out-of-order and
duplicate events are covered by focused engineering tests.

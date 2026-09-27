YGG-B52 PREREGISTRATION — TARGET-REFRESH DOSE RESPONSE
Parent B51 valid NO_RESTORATIVE_PRE_REPLAY_IDENTITY; B48 established target-identity unique rescue.
Question: is one exact target rewrite the least disruptive sufficient intervention, or does repeated target rehearsal change collateral under fixed capacity?
Freeze exact B51/B48 model, training/evaluation rows, 120 parameters, 32 persistent-state scalars, seven initial bindings, seeds [111,222,333,444,555], old-query strata q=[0..4], deterministic Torch. No retraining/adaptation/capacity/architecture/threshold change.
For every seed/q row use one shared baseline after the original seven writes.
Arms:
D1: write exact binding q once.
D2: write exact binding q twice consecutively.
D3: write exact binding q three times consecutively.
After each dose score all seven original bindings.
Primary:
- target-q accuracy and >=.90 capability;
- collateral baseline-correct opportunities, NEW_ERROR and REPAIR across the six non-target bindings.
Inherited anchor: D1 target-q >=.90 for every stratum.
Classification:
SINGLE_REFRESH_MINIMAL if D1/D2/D3 all preserve universal target rescue and aggregate collateral NEW_ERROR is nondecreasing with dose with D1 strictly lowest.
REPEATED_REFRESH_REDUCES_COLLATERAL if a higher dose preserves universal target rescue and has lower aggregate collateral NEW_ERROR than D1.
DOSE_NONMONOTONIC if all doses preserve target rescue but collateral does not fit either pattern.
TARGET_RESCUE_LOST_AT_HIGHER_DOSE if D2 or D3 loses target capability in any stratum.
ANCHOR_NOT_REPRODUCED if D1 anchor fails.
OTHER_VALID_PATTERN otherwise.
No collateral threshold is introduced; exact counts are reported.
Validity: exact seeds/q/doses; only exact target binding rewritten; doses exactly1/2/3 consecutive writes; same baseline; all six non-target bindings scored; state/params exact; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.

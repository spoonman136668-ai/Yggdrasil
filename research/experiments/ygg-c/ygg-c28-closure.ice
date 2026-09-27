YGG-C28 CLOSURE
Run 36322950976 SHA d7a803a742e4139b6b689a33feb0a9d472f2b1f7
Classification: PARTIAL_CRITICAL_COMPENSABILITY
Valid: true. Duplicate SHA256 94437436d893f79c8190ca5825fde26ce1de5b2f756c0149d307c48c109e96ca.
For universally forbidden additions4 and5:
- remove6 restores rescue at every level8..16;
- remove42 or46 also restore from level10 upward.
For forbidden addition41:
- levels8..9: remove42 rescues;
- levels10..12: no single present-cell removal rescues;
- levels13..16: remove46 rescues.
Interpretation: critical additions4/5 share a stable suppressor relationship with cell6, while cell41 exhibits a pressure-dependent suppressor handoff from42 to46 with an uncompensated gap at levels10..12.
Plain speak: cells4/5 can always be countered by taking out cell6. Cell41 is harder: one fix works early, a different fix works late, and neither works in the middle.
Next: at the cell41 gap levels10..12, test the combined removal42+46 against a matched nonsuppressor pair6+14. This asks whether the early and late suppressors cooperate in the middle or whether any two-cell reduction is sufficient.

YGG-C29 CLOSURE
Run 36327042750 SHA 93d604bbad76d0c438fbf11835372f3c9caab610
Classification: COOPERATIVE_42_46_SUPPRESSION
Valid: true. Duplicate SHA256 7a9b49248f84985e86524a2d4ea6e0e4b8b3a9ff7d4d5ac37a85b7cd30ababc0.
At levels10,11,12:
- BASE_38_TO_42 rescues.
- ADD41 fails.
- ADD41_REMOVE42 fails.
- ADD41_REMOVE46 fails.
- ADD41_REMOVE42_REMOVE46 rescues.
- matched ADD41_REMOVE6_REMOVE14 fails.
Structural controls:
- BASE_REMOVE42_REMOVE46 fails.
- BASE_REMOVE6_REMOVE14 rescues.
Interpretation: cells42 and46 jointly suppress the otherwise critical ADD41 failure in the mid-pressure gap. The effect is not explained by generic two-cell removal. Moreover, removing42+46 from the repaired base is itself damaging, while adding41 to that double-removal state restores rescue: strong context-dependent sign reversal.
Plain speak: cell41 is harmful in the normal repaired state, but becomes helpful when42 and46 are both absent.
Next: starting from the failing BASE_REMOVE42_REMOVE46 state, add each currently absent cell one at a time at levels10..12 to determine whether41 is a specific compensatory addition or one of many interchangeable additions.

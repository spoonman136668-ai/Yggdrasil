YGG-B43 CLOSURE
Run 36275111281 SHA fb966df2f6db3d5b4eaa22619cfa140118598b17
Classification: RECENCY_BAND
Valid: true. Duplicate SHA256 d7ffd19349122791db2c5d226eb423d34854c41c3240252fdd3423da8e3791ba.
Across frozen seed/query strata, queried-binding relocation was universally capable at destination5 (25/25 eligible strata) and destination6 (30/30), but not at destinations0..4. Counts: d0=0/25, d1=0/25, d2=0/25, d3=0/25, d4=3/25, d5=25/25, d6=30/30.
All B42 d6 endpoints reproduced at accuracy1.0. Exact destination/parking rules, binding multiset, state/parameter counts, and duplicate execution passed.
Interpretation: recovery is not unique to the final write; the two most recent binding positions form a candidate recency band. Because each B43 destination used one deterministic parking choice, destination sufficiency is not yet proven parking-independent.
Plain speak: putting the requested item in either of the last two write slots always works. Earlier slots mostly do not. Next we make sure that finding is about recency itself, not where the displaced item happened to be parked.
Next: exhaustive valid-parking sweep for destinations4,5,6.

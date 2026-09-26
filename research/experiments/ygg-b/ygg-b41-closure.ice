YGG-B41 CLOSURE
Run 36272095308 SHA e2724795476bc9b8c190c63b40310cb6f5108c47
Classification: QUERY_RELATIVE_PORTABLE
Valid: true. Duplicate SHA256 49ef731a0b313c0d93df85756ffd554084f636cbd90b0ae466379c4a20e8d964.
Frozen seeds [111,222,333,444,555], query strata 0..5, threshold 0.90, 120 parameters, 32 persistent-state scalars.
For every seed and every tested first-read query position 0..5, reciprocal swap 6<->query_position produced accuracy exactly 1.0. Capable counts were 5/5 at every query position. Query-position4 inherited B40 endpoints reproduced exactly. Every stratum was nonempty; binding multiset preserved; duplicate byte identity passed.
Interpretation: the B40 destination4 effect was query-relative rather than absolute-position specific. However reciprocal swapping confounds two directional changes: it moves the queried binding to latest position6 while simultaneously moving position6 content into the queried slot.
Plain speak: slot4 was not magic. Whichever item is being asked about becomes perfectly recoverable when that item is swapped with the final write. The next experiment must determine which half of that swap causes the rescue.
Next: three-cycle directional decomposition separating queried-binding-to-position6 from position6-content-to-query.

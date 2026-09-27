YGG-A65 CLOSURE
Run 36346244037 SHA 30ad30fadd6675e444958d57f670d0f454f47731
Classification: COMPOUND_CONTEXT_BREAKS_SELECTOR
Valid: true. Duplicate SHA256 79e3351eea0e40922b2289cc1edc22715613cffdaa9a8344f6c27de82126dcaa.
All37 A64-derived cases reproduced pair-only and each single-context anchor.
Under both context flips simultaneously,5/37 selected pairs failed identically in U_A0/U_A25:
contexts(97,103) selected pair(105,111)
contexts(97,105) selected pair(103,111)
contexts(98,117) selected pair(105,111)
contexts(99,105) selected pair(103,111)
contexts(106,121) selected pair(105,117)
Interpretation: the single-context suppressor matrix does not compose perfectly under compound context. Pair viability itself has higher-order context dependence.
Plain speak: choosing a repair route because each disturbance is safe by itself is not always enough; two disturbances together can still break that route.
Next: for exactly these five failed compound contexts, test every frozen A57 causal pair that does not overlap the context positions. Determine whether an alternate route still abolishes collapse under the same two-context state.

TITLE: YGG-B29 READ-1 Interference Localization Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_RESULT: YGG-B28 READ1_LIMITED

QUESTION
Does the READ-1 deficit arise from the first query itself, from optimization competition with READ-2, or from the intervening overwrite requirement?

FROZEN
Keep B28 architecture, 32-state/120-parameter budget, seeds, data split, optimizer, epochs, and inherited .90 criterion. Diagnostic controls may remove one demand at a time but may not expand the substrate.

ARMS
A: exact B28.
B: READ-1-only objective with identical examples and budget.
C: two-read objective with intervening overwrite neutralized while token count/order is preserved.

SUCCESS
Classify READ1_INTRINSIC, MULTI_OUTPUT_OPTIMIZATION_INTERFERENCE, OVERWRITE_INTERFERENCE, MIXED_INTERFERENCE, or NO_LOCALIZATION. Seal negatives unchanged.

BOUNDARY
Synthetic sequence task only. No language corpus, architecture expansion, online adaptation, or recursive self-modification.

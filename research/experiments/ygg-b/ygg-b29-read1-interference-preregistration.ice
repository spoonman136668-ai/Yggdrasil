TITLE: YGG-B29 READ-1 Interference Attribution Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_RESULT: YGG-B28 READ1_LIMITED

QUESTION
Is B28's READ-1 deficit intrinsic to the first query, caused by multi-output optimization interference, or caused by the intervening overwrite before READ-2?

FROZEN
Exact B27/B28 task family, state=32, parameters=120, seeds, held-out rules, optimizer, epochs, batch, deterministic CPU execution, and inherited .90 capability threshold. No architecture expansion or post-result threshold change.

ARMS
A: exact B28 sequence and two-loss training.
B: same sequence/data but score READ-1 immediately at its original read point before the intervening overwrite.
C: same training examples/substrate with READ-1-only loss, evaluated at the same original read point.
All non-target factors remain frozen.

CLASSIFICATION
OVERWRITE_INTERFERENCE if A READ1<.90 and B>=.90.
MULTIOUTPUT_OPTIMIZATION_INTERFERENCE if B<.90 and C>=.90.
INTRINSIC_READ1_LIMIT if C<.90.
NO_REPRODUCED_LIMIT if A>=.90.
OTHER_VALID_PATTERN otherwise.

SUCCESS
YGG_B29_READ1_INTERFERENCE_ATTRIBUTION=true iff mechanical/integrity/duplicate gates pass and exactly one classification is produced.

BOUNDARY
Diagnostic only; synthetic sequence task; no language corpus, architecture expansion, online adaptation, or recursive self-modification.

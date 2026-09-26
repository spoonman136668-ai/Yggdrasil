TITLE: YGG-B29 READ-1 Interference Attribution Closure
DATE: 2026-09-26
STATUS: CLOSED / VALID ATTRIBUTION
LANE: YGG-B
PREREGISTRATION: ce2b20b3962fc6b006c5c71407dedf6887dfceee
PARENT_RUN: 0faacaae883e1e5ee2dbb040cea335fdf88098e3
EXECUTION_HEAD: 5abe12359354c535591eeabfd2d969a373ca0d75
WORKFLOW_RUN_ID: 36228902036
DUPLICATE_SHA256: 14b355c382334faaad64cb06057ebf502c447fe2bbcc8023abdc4962d269b05c

RESULT
YGG_B29_READ1_INTERFERENCE_ATTRIBUTION=true
classification=INTRINSIC_READ1_LIMIT

Across all five frozen seeds:
- exact two-output READ-1 accuracy remained approximately .726-.740;
- scoring READ-1 immediately at its original read point produced byte-identical logits;
- READ-1-only training remained approximately .733-.742;
- READ-2 accuracy remained 1.0 in the exact two-output arm;
- all causal, held-out, state=32, and parameter=120 gates passed.

INTERPRETATION
The READ-1 boundary is not caused by the intervening overwrite and is not rescued by removing the READ-2 optimization objective. The deficit is already present when retrieving an original binding from the seven-write prefix. The next causal seam is therefore the age/position of the queried binding inside that prefix, before changing the substrate.

NEXT QUESTION
Holding the exact B29 substrate, data family, seeds, optimizer, state, parameters, and inherited .90 threshold fixed, attribute READ-1 accuracy by the original write-event position 0..6. Determine whether the intrinsic limit is position/age-dependent or distributed across all seven prefix bindings.

BOUNDARY
Diagnostic continuation only.
No architecture expansion.
No language corpus yet.
No online adaptation.
No recursive self-modification.

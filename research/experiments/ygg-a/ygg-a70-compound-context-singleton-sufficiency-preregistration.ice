YGG-A70 PREREGISTRATION — COMPOUND-CONTEXT SINGLETON SUFFICIENCY
Parent A69 valid COMPOUND_CONTEXT_ROUTE.
Question: is the A69 rescue produced specifically by the joint context {99,107}, or is either context member individually sufficient without any original causal-pair member?

Freeze exact A69 substrate:
- replicate6 runtime/programs/native arrivals;
- donor3 corruption [16,38,146,118];
- alpha=.25;
- modes U_A0 and U_A25;
- target cell2;
- exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules;
- repair off;
- deterministic execution;
- no original A57 causal-pair members in any A70 arm.

For each mode evaluate exactly four context-only arms:
EMPTY = {}
CTX99 = {99}
CTX107 = {107}
CTX99_107 = {99,107}

Inherited anchor: CTX99_107 must reproduce A69 non-collapse in both modes.
No other request labels may change.

Report collapse state for all four arms in both modes.

Per-mode classification:
BOTH_CONTEXT_MEMBERS_REQUIRED if EMPTY, CTX99, and CTX107 collapse while CTX99_107 abolishes collapse.
CTX99_SINGLETON_SUFFICIENT if CTX99 abolishes collapse and CTX107 does not.
CTX107_SINGLETON_SUFFICIENT if CTX107 abolishes collapse and CTX99 does not.
EITHER_SINGLETON_SUFFICIENT if both CTX99 and CTX107 abolish collapse.
BASELINE_ALREADY_RESCUED if EMPTY already abolishes collapse.
OTHER_VALID_PATTERN otherwise.

Overall classification:
CROSS_MODE_CONTEXT_DIFFERENCE if the two modes have different per-mode classifications.
Otherwise use the shared per-mode classification.
ANCHOR_NOT_REPRODUCED if CTX99_107 fails in either mode.

Validity: exact four arms per mode; exact context labels; no original causal-pair labels; only registered stream changes; corruption fixed; []/[2] lesions exact; deterministic duplicate; runtime/program/global state restored.
Scientific negatives are valid. No post-result tuning.

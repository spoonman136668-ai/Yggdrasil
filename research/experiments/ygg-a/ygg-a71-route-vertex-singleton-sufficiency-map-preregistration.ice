YGG-A71 PREREGISTRATION — ROUTE-VERTEX SINGLETON SUFFICIENCY MAP
Parent A70 valid EITHER_SINGLETON_SUFFICIENT.

Question: are context vertices 99 and 107 uniquely capable of singleton rescue, or is singleton rescue broadly redundant across the already-registered route/context vertex set?

Freeze exact A70 substrate:
- replicate6 runtime/programs/native arrivals;
- donor3 corruption [16,38,146,118];
- alpha=.25;
- modes U_A0 and U_A25;
- target cell2;
- exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules;
- repair off;
- deterministic execution.

Frozen singleton candidate set exactly:
V={99,103,105,106,107,111,117,121,123}

For each mode evaluate exactly:
EMPTY={}
and one singleton arm {v} for every v in V.

Inherited anchors:
- EMPTY must collapse in both modes.
- {99} and {107} must each abolish collapse in both modes, reproducing A70.

No pair, compound, or higher-order arm is permitted.
No request label outside the selected singleton may change.

Report collapse state for all ten arms per mode and the exact singleton rescue set.

Classification:
CONTEXT_ONLY_SINGLETON_RESCUE if the rescue set is exactly {99,107}.
ALL_ROUTE_VERTICES_SINGLETON_RESCUE if every v in V rescues.
BROAD_ROUTE_SINGLETON_REDUNDANCY if {99,107} rescue and one or more additional route vertices rescue.
CROSS_MODE_SINGLETON_MAP if the two modes have different singleton rescue sets.
ANCHOR_NOT_REPRODUCED if EMPTY/{99}/{107} fails to reproduce A70.
OTHER_VALID_PATTERN otherwise.

Validity: exact V; exact ten arms per mode; singleton membership change only; no pair/compound arms; inherited A70 anchors exact; corruption fixed; []/[2] lesions exact; only registered stream changes; deterministic duplicate; runtime/program/global state restored.
Scientific negatives are valid. No post-result tuning.

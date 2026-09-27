YGG-A45 PREREGISTRATION — DONOR3 SINGLE PHASE-PAIR SWAP
Parent A44 run 36283331102 valid PHASE_SENSITIVE.
Selection rule frozen from A44: choose the lowest donor whose k0 collapse outcome changes under at least one phase rotation. This selects donor3, whose rotation pattern is [collapse, no-collapse, no-collapse, no-collapse, no-collapse] in both modes.
Question: can exchanging only one pair of developmental phase blocks in donor3's corruption schedule abolish singleton-cell2 collapse?
Freeze exact A44 substrate: replicate6 runtime/programs/arrival stream, donor3 k0 corruption schedule, alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic, no retraining/adaptation/threshold/topology/baseline changes.
Five phases are exact request-ID blocks [0..31],[32..63],[64..95],[96..127],[128..159].
For each unordered phase pair (a,b), 0<=a<b<=4, construct a bijective phase-block swap:
- every corruption id in phase a moves to phase b at the same within-phase offset;
- every corruption id in phase b moves to phase a at the same within-phase offset;
- all other corruption ids remain unchanged.
This preserves total corruption count exactly and preserves the multiset of within-phase offsets across the swapped pair. Ten pair-swap arms total.
Anchors:
- unmodified donor3 k0 schedule must collapse;
- donor3 full +1 phase rotation from A44 must not collapse.
Classification:
ANY_PAIR_SWAP_BREAKS if all ten pair swaps abolish collapse in both modes.
MIXED_PHASE_PAIR_SENSITIVITY if at least one pair abolishes collapse and at least one pair retains collapse, with identical pair outcomes across modes.
PAIR_SWAP_ROBUST if all ten pair swaps retain collapse.
CROSS_MODE_PAIR_DIFFERENCE if pair outcomes differ by mode.
ANCHOR_NOT_REPRODUCED if either inherited anchor fails.
OTHER_VALID_PATTERN otherwise.
Validity: donor3 exact; all ten unordered phase pairs exact; bijection exact; corruption count preserved; fixed runtime/program/arrivals exact; []/[2] exact; scientific integrity; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.

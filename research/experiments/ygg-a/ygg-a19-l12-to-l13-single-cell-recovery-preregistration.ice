TITLE: YGG-A19 Integrated L12-to-L13 Single-Cell Recovery Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: b6b2a6c6726c7786946239b9658d24f5976f685c
PARENT_EXPERIMENT: YGG-A18
CROSS-LINEAGE_EVIDENCE: YGG-C5

QUESTION
Under the fully integrated alpha=1.0 plus 58-event branch-repair regime, does adding exactly the single C5-ranked lesion cell that transforms the failing L12 configuration into L13 restore stream noncollapse?

NORTH-STAR TARGET
Test whether the developmental reorganization threshold discovered in C5 survives integration with full learned control and maximum branch repair.

FROZEN
- exact ten A15/A17 manifests except lesion field/hash;
- alpha=1.0;
- exact 58-event branch-repair schedule with 29 B and 29 C;
- exact repair and terminal-integrity semantics;
- exact task, programs, arrivals, corruptions, anchors, horizon, scheduler, service capacity, maturity rules, thresholds, and learned weights;
- deterministic duplicate execution.

LESION CONSTRUCTION
Use exact C5 nested hash-ranked construction from the inherited L8 lesion:
rank remaining cells by h64("YGG-C3-RESOURCE-PRESSURE", seed, cell), then cell.

L12:
inherited L8 + first 4 ranked cells.

L13:
same exact L12 set + the fifth ranked cell.

Thus L12 is a strict subset of L13 and differs by exactly one preregistered cell per replicate.

CONDITIONS
At alpha=1.0 with damage ON at 58 repairs:
1. L12
2. L13

ANCHOR / REPRODUCTION
L12 must reproduce the accepted A17 failure:
- stream_noncollapse=false;
- exactly one failure cell:
  replicate=6, phase=4, stream=S, L8 count=5, L12 count=3, ratio=0.6.

L13 RECOVERY
Use the exact C3 stream-noncollapse rule against the A15 alpha=1.0 L8 damage-ON anchor:
for every replicate, phase, and stream, if L8 count >=4 then L13 count must be >=75% of L8 count.

INTEGRITY / CAPABILITY
For both L12 and L13:
- exact nested lesion cardinality and lineage;
- all non-lesion manifest fields frozen;
- scheduled/applied/repaired=58;
- scheduled_b=29 and scheduled_c=29;
- all repairs before D;
- unrepaired_terminal=0;
- d_while_branch_incorrect=0;
- incorrect_done=0;
- matching integrity exact;
- maturity.pass=true;
- horizon-aware terminal integrity=true;
- aggregate damage-ON correct_done / matched damage-OFF >=.95;
- every-world damage ratio >=.90;
- damage-ON aggregate / A15 L8 damage-ON >=.90;
- learned arm materially exercised.

DUPLICATION / RESTORATION
Complete L12+L13 execution must be byte-identical.
Runtime alpha, validator, lesion_set, and damage_schedule must be restored exactly.

SUCCESS
YGG_A19_L12_TO_L13_SINGLE_CELL_RECOVERY=true iff:
- accepted L12 failure is reproduced exactly;
- L13 stream noncollapse is globally restored;
- every frozen lineage, integrity, capability, duplication, and restoration gate passes.

INTERPRETATION
Positive:
The single C5-ranked L13 addition triggers recovery even under full integration, supporting a genuine developmental reorganization threshold.

Negative:
The C5 L13 recovery does not survive the integrated alpha=1.0 + repair regime.

FAILURE
Do not alter lesion ranking, count, alpha, repair schedule, thresholds, task, weights, scheduler, horizon, or service capacity after observing results.

BOUNDARY
No accepted baseline mutation.
No weight update.
No online adaptation.
No recursive self-modification.

TITLE: YGG-A17 L12 Topology-Failure Rescue Integration Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: 1f22fb884b4329a1627da406204f9a5de2d1a2ea
PARENT_EXPERIMENT: YGG-A16
CROSS_MECHANISM_EVIDENCE: YGG-C3 L12 stream_noncollapse=false

QUESTION
Can the integrated full learned-control plus maximum branch-repair regime rescue the exact topology-sensitive L12 resource-pressure condition that failed the frozen C3 stream-noncollapse criterion?

NORTH-STAR TARGET
Test whether mechanism integration restores capability under a known topology-specific failure, not merely under a favorable lesion cardinality.

FROZEN
- exact ten A15/A16 manifests except lesion field/hash;
- full learned-control alpha=1.0;
- exact 58-event branch-repair schedule, 29 B + 29 C;
- exact repair, terminal-integrity, task, program, arrival, corruption, anchor, horizon, scheduler, service-capacity, maturity, and threshold semantics;
- exact learned weights;
- deterministic duplicate execution.

SCIENTIFIC CHANGE
Use the exact C3 nested L12 lesion construction:
1. inherited L8 lesion;
2. rank remaining cells by h64("YGG-C3-RESOURCE-PRESSURE", seed, cell), then cell;
3. append first four ranked cells;
4. sort final 12-cell lesion.

KNOWN PARENT FAILURE
Under YGG-C3 with the frozen alpha=.25 parent, this exact L12 geometry had:
retained=false
failure=stream_noncollapse
aggregate retention remained near baseline.

HARNESS ADAPTER
As in A16, normalize lesion to inherited L8 only for the frozen validator, execute the real L12 lesion using a temporary lesion_set override, and restore validator/lesion_set exactly.

ANCHOR
A15 alpha=1.0 L8 complete evidence SHA must equal:
c094f01f6d5c3ae5987cab5215da3ce0146f84a44bce967f042d23cd474595a7

RESCUE GATES
At L12 alpha=1.0:
- exact C3 L12 nested lesion;
- non-lesion fields frozen;
- scheduled/applied/repaired=58;
- 29 B + 29 C;
- all repairs before D;
- no unrepaired terminal branch;
- d_while_branch_incorrect=0;
- incorrect_done=0;
- matching integrity exact;
- maturity.pass=true;
- horizon-aware terminal integrity=true;
- aggregate damage-ON / damage-OFF correct_done >=.95;
- every-world damage ratio >=.90;
- damage-ON aggregate correct_done / A15 L8 damage-ON >=.90;
- learned arm materially exercised.

STREAM-NONCOLLAPSE RESCUE
Use the exact C3 rule against the A15 alpha=1.0 L8 damage-ON anchor:
for each replicate, phase, and stream, if L8 completed count >=4 then L12 completed count must be >=75% of the L8 count.
The integrated regime qualifies as a topology-failure rescue only if this is true globally.

DUPLICATION / RESTORATION
Complete L12 paired execution must be byte-identical.
Runtime alpha, validator, lesion_set, and damage_schedule must be restored exactly.

SUCCESS
YGG_A17_L12_TOPOLOGY_FAILURE_RESCUE=true iff every lineage, integrity, capability, stream-noncollapse, duplication, and restoration gate passes.

FAILURE
Do not alter topology, lesion count, thresholds, repair count, alpha, task, weights, scheduler, horizon, or service capacity after results.

BOUNDARY
No accepted baseline mutation.
No weight update.
No online adaptation.
No recursive self-modification.

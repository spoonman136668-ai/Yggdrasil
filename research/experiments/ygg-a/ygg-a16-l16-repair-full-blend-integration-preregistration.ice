TITLE: YGG-A16 L16 Pressure + Maximum Repair + Full Blend Integration Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: 5c0ea0d9a61d961fb87dcb992166ba11fab6785b
PARENT_EXPERIMENT: YGG-A15
CROSS_MECHANISM_EVIDENCE: YGG-C3 L16 retained

QUESTION
Does the fully integrated A15 regime remain capability-preserving when substrate lesion pressure is doubled from the inherited L8 lesion to the accepted nested L16 lesion construction?

NORTH-STAR TARGET
Integrate repair, learned developmental control, and stronger resource pressure before moving to broader capability.

FROZEN
- exact ten A15 manifests and non-lesion fields;
- exact full learned-control alpha=1.0;
- exact 58-event branch-repair schedule, 29 B and 29 C;
- exact repair and terminal-integrity semantics;
- exact task, programs, arrivals, corruptions, anchors, horizon, scheduler, service capacity, maturity, thresholds, and weights;
- deterministic duplicate execution.

SCIENTIFIC CHANGE
Lesion cardinality only:
L8 -> L16.

L16 construction is exactly the accepted C3 nested rule:
1. start with the inherited sorted L8 lesion;
2. rank every remaining cell by
   h64("YGG-C3-RESOURCE-PRESSURE", seed, cell), then cell;
3. append the first eight ranked remaining cells;
4. sort the final 16-cell lesion.

HARNESS ADAPTER
The frozen parent validator hard-codes lesion cardinality 8.
For validation only, normalize the candidate manifest lesion back to its inherited L8 set and recompute manifest hash.
The scored execution must use the real preregistered L16 lesion and a temporary lesion_set override.
Restore validator and lesion_set exactly after every scored execution.

CONDITIONS
1. L8 alpha=1.0 A15 anchor
2. L16 alpha=1.0 with damage OFF
3. L16 alpha=1.0 with damage ON at 58 repairs

ANCHOR
The complete A15 alpha=1.0 A13-derived evidence SHA must equal:
c094f01f6d5c3ae5987cab5215da3ce0146f84a44bce967f042d23cd474595a7

L16 INTEGRITY GATES
For every damaged U_A25 world:
- lesion cardinality exactly 16 and exact C3 nested construction;
- scheduled/applied/repaired=58;
- scheduled_b=29 and scheduled_c=29;
- all repaired before D;
- unrepaired_terminal=0;
- d_while_branch_incorrect=0;
- incorrect_done=0;
- matching duplicate cell/request violations=0;
- maturity.pass=true;
- horizon-aware terminal integrity=true.

CAPABILITY GATES
- L16 U_A25 damage-ON aggregate correct_done / L16 U_A25 damage-OFF aggregate correct_done >=0.95;
- every-world L16 damage ratio >=0.90;
- L16 U_A25 damage-ON aggregate correct_done / A15 L8 U_A25 damage-ON aggregate correct_done >=0.90;
- learned arm materially exercised.

LINEAGE / DUPLICATION
- all non-lesion manifest bytes equal L8 parent after removing lesion/hash;
- L8 subset of L16 for every world;
- runtime alpha remains 1.0 during scored conditions and is restored afterward;
- validator and lesion_set restored exactly;
- complete L16 paired execution byte-identical across duplicates.

SUCCESS
YGG_A16_L16_REPAIR_FULL_BLEND_INTEGRATION=true iff every frozen lineage, integrity, capability, duplication, and restoration gate passes.

FAILURE
Do not alter lesion construction, alpha, repair count, thresholds, task, horizon, scheduler, service capacity, or weights after observing results.

BOUNDARY
No accepted baseline mutation.
No weight update.
No online adaptation.
No shared-baseline promotion from A16 alone.
No recursive self-modification.

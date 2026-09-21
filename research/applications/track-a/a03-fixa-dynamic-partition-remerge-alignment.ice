TITLE: YGG-A03-FIXA — Dynamic Partition Re-Merge Alignment
DATE: 2026-09-20
STATUS: PREREGISTERED / CORRECTIVE APPLICATION REPLICATION / NON-CANONICAL
TRACK: YGGDRASIL APPLICATION TRACK A
PARENT: A03 Held-Out Adaptive Generalization R1
BRANCH: dg1a-ar

PURPOSE

A03 R1 produced a reproducible positive blind held-out task / adaptation result.

Post-run implementation audit found one protocol-alignment defect:

the A03 wrapper patched the random partition window,
but inherited A02's fixed _remerge() trigger at epoch 152.

Because every A03 primary partition occurred after epoch 152,
the explicit causal re-merge / provisional-clear transaction did not execute.

A03-FIXA asks:

DO THE EXACT SAME BLIND WORKLOADS,
WITH THE EXACT SAME FROZEN A02 POLICY,
RETAIN THE A03 TASK / ADAPTATION RESULT
WHEN THE CLOSED A02 RE-MERGE TRANSACTION
IS EXECUTED AT EACH SCHEDULE'S ACTUAL PARTITION END + 1?

BOUNDARY

Synthetic software only.
No production mutation.
No canonical DG-1R-05 execution.
No STAB-18-R1 execution.

ALLOWED CHANGE

The only allowed organism semantic change is:

HeldoutOrganism._remerge(epoch)

must execute the inherited closed A02 merge transaction when:

epoch == heldout_schedule.partition_end + 1.

The transaction must preserve A02 semantics:

- inspect accumulated provisional transitions;
- identify repeated same-cell conflicting targets;
- count such conflicts as rolled-back transitions;
- clear provisional transaction records;
- advance causal history with one re-merge commit.

A03's primary family has disjoint physical cell ownership
and R1 observed zero same-cell rollback conflicts.

FORBIDDEN CHANGES

Do not change:

- A02 dependency;
- A03 primary seeds;
- A03 schedule manifest;
- request payloads;
- demand regimes;
- budget windows;
- damage epochs / selectors;
- partition starts / ends;
- restart points;
- migration policy;
- governance / registry qualification;
- hibernation / reactivation;
- repair timing;
- task transform functions;
- static baseline;
- oracle;
- fault / reallocation scoring;
- primary thresholds.

FROZEN R1 ENVIRONMENT

Freeze F:

6f010ce561d958a324664b2d3e0c04e3e113d91b.

Schedule manifest SHA-256:

842d8f03f1f1229e633c783a895b5b6ceb81f813c2fb104a81000c25baa40848.

Use the exact 12 seeds already recorded in the parent A03 spec.

R1 OUTPUT EQUIVALENCE GUARD

Aggregate candidate task-output stream SHA-256:

3ee64e5ab63df92056c0b68e7b8f372d37656310476e5c4c0aef358c2e22bd2f.

FIXA candidate task outputs MUST match this exactly.

R1 aggregate task observations MUST remain:

total requests = 55296;
candidate served = 52273;
candidate correct = 52273;
candidate incorrect = 0;
static served = 37801;
oracle served = 52655;
task coverage = 0.9453305844907407;
static coverage = 0.6836118344907407;
static gain = 0.26171875;
oracle efficiency = 0.9927452283733739;
maximum fault recovery = 1;
maximum non-partition reallocation = 2;
scenarios beating static = 12;
environment impossibilities = 0.

R1 final provisional counts were:

(6,5,5,5,5,4,12,7,10,8,9,12).

FIXA REQUIREMENTS

For every scenario:

- re-merge event executes exactly once at partition_end + 1;
- final provisional transition count = 0;
- task output stream equals R1;
- candidate / static / oracle service counts equal R1;
- fault and reallocation observations equal R1;
- restarted and uninterrupted FIXA runs remain equivalent;
- all safety totals remain zero.

PRIMARY CORRECTIVE SIGNAL

A03_FIXA_REMERGE_ALIGNMENT_VALID

TRUE iff:

schedule manifest unchanged
AND
task-output aggregate SHA matches R1
AND
all 12 final provisional counts are zero
AND
all 12 dynamic re-merge events execute exactly once
AND
all R1 task / adaptation aggregate observations are unchanged
AND
all restarts remain equivalent
AND
all safety totals remain zero.

CORRECTED GENERALIZATION STATUS

A03_GENERALIZATION_ACCEPTED

TRUE iff:

A03_FIXA_REMERGE_ALIGNMENT_VALID
AND
all original A03 primary generalization thresholds remain TRUE.

REPRODUCIBILITY

Two complete deterministic FIXA sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After first FIXA primary request begins,
no further semantic change is permitted.

PLAIN-SPEAK PREREGISTERED QUESTION

The first blind test showed that Yggdrasil adapted very well,
but we discovered that the program forgot to formally close the partition transaction afterward.

The cells had already made the local changes,
so the service kept working,
but the bookkeeping still said those changes were provisional.

FIXA is not allowed to make the organism smarter.

It only makes the scheduled re-merge actually happen where the experiment said it would.

If the service outputs remain identical,
all safety checks remain clean,
and every provisional record is properly closed,
then the original generalization result survives with the partition protocol correctly executed.

canonical_scientific_execution = false.
stab18_r1_touched = false.

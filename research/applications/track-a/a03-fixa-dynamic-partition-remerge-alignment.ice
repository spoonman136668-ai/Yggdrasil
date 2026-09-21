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


PRE-RUN IMPLEMENTATION FREEZE 01 — A03-FIXA DYNAMIC RE-MERGE

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST FIXA PRIMARY REQUEST.

IMPLEMENTATION COMMIT

05fb530c9fe984fe0c8559c4f61a873ac7b2023d.

SOURCE BUNDLE

Loader:

research/applications/track-a/a03_fixa_dynamic_remerge_v1.py

Loader Git blob:

a0880d9e42d931980b758d385b7e873641e846da.

Payload:

research/applications/track-a/a03_fixa_dynamic_remerge_v1.py.gz

Payload Git blob:

7d3e22db6eb123374cdf1a44e508fda4e0858e5b.

Compressed payload SHA-256:

e0b2fa6da50a061b47ca9af1700bafef390b3fc9e777a4ef56cb73bbb65907ce.

Compressed payload bytes:

7400.

Decompressed source SHA-256:

f38fbe4823c6f8e3093a45b701cc39054c3bc814a67a97053d180bacb5087234.

Decompressed source bytes:

25934.

SEMANTIC DIFF FROM A03 R1

One organism-semantic correction only:

_remerge(epoch)

now triggers when:

epoch == heldout_schedule.partition_end + 1.

Its transaction body carries forward the inherited A02 re-merge semantics.

Additional code only records:

dynamic re-merge count;
final provisional count;
R1 output / aggregate equivalence.

Those fields do not participate in organism decisions.

MECHANICAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical-seed task outputs identical to A03 R1:

TRUE.

Mechanical-seed task metrics identical to A03 R1:

TRUE.

Mechanical-seed final provisional count:

0.

Mechanical-seed dynamic re-merge count:

1.

Mechanical-seed restarted / uninterrupted authoritative state:

equivalent.

Mechanical-seed restarted / uninterrupted output / metrics:

equivalent.

PRIMARY ENVIRONMENT REMAINS FROZEN

Original A03 freeze F:

6f010ce561d958a324664b2d3e0c04e3e113d91b.

Original A03 schedule manifest SHA-256:

842d8f03f1f1229e633c783a895b5b6ceb81f813c2fb104a81000c25baa40848.

The exact same 12 recorded primary seeds are used.

No primary schedule is regenerated,
redrawn,
or replaced.

R1 task-output equivalence anchor:

3ee64e5ab63df92056c0b68e7b8f372d37656310476e5c4c0aef358c2e22bd2f.

No FIXA primary request has been executed before this freeze.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-RUN CLOSURE — A03-FIXA DYNAMIC PARTITION RE-MERGE ALIGNMENT

DATE:
2026-09-20.

STATUS:
CLOSED / POSITIVE CORRECTIVE PRIMARY / REPRODUCIBLE / A03 GENERALIZATION ACCEPTED.

FROZEN HARNESS

Implementation commit:

05fb530c9fe984fe0c8559c4f61a873ac7b2023d.

Freeze commit:

c86b3d6504cae038da29136cb627bec08d70091e.

Decompressed source SHA-256:

f38fbe4823c6f8e3093a45b701cc39054c3bc814a67a97053d180bacb5087234.

Source bytes:

25934.

Original A03 environment freeze F:

6f010ce561d958a324664b2d3e0c04e3e113d91b.

Original schedule manifest SHA-256:

842d8f03f1f1229e633c783a895b5b6ceb81f813c2fb104a81000c25baa40848.

The same 12 original A03 seeds and schedules were used.

REPRODUCIBILITY

Two complete deterministic corrective sweeps.

Sweep 1 output SHA-256:

091f7d48ac289947bca85e13b106ac29e7df5e295d606ca8c2ef5ccdd3163f8f.

Sweep 2 output SHA-256:

091f7d48ac289947bca85e13b106ac29e7df5e295d606ca8c2ef5ccdd3163f8f.

Byte-identical:

TRUE.

CORRECTIVE PRIMARY

A03_FIXA_REMERGE_ALIGNMENT_VALID:

TRUE.

A03_GENERALIZATION_ACCEPTED:

TRUE.

RE-MERGE EVIDENCE

Dynamic re-merge executions per scenario:

(1,1,1,1,1,1,1,1,1,1,1,1).

Final provisional transition counts:

(0,0,0,0,0,0,0,0,0,0,0,0).

Thus every randomized partition window executed one explicit causal re-merge
at its actual partition end + 1
and no provisional transaction state remained at scenario completion.

R1 TASK OUTPUT EQUIVALENCE

Expected R1 task-output stream SHA-256:

3ee64e5ab63df92056c0b68e7b8f372d37656310476e5c4c0aef358c2e22bd2f.

FIXA task-output stream SHA-256:

3ee64e5ab63df92056c0b68e7b8f372d37656310476e5c4c0aef358c2e22bd2f.

Exact match:

TRUE.

R1 aggregate task / adaptation observations unchanged:

TRUE.

Total requests:

55296.

Candidate served / correct:

52273 / 52273.

Candidate incorrect:

0.

Static served:

37801.

Oracle served:

52655.

Task coverage:

0.9453305844907407.

Static coverage:

0.6836118344907407.

Static gain:

0.26171875.

Oracle efficiency:

0.9927452283733739.

Maximum fault recovery:

1 epoch.

Maximum non-partition reallocation:

2 epochs.

Scenarios beating static:

12 / 12.

Environment impossibilities:

0.

RESTART / SAFETY

All FIXA restarted / uninterrupted scenarios equivalent:

TRUE.

All aggregate safety totals zero:

TRUE.

TECHNICAL INTERPRETATION

A03 R1's task / adaptation measurements were not caused by the missing re-merge transaction.

When the preregistered re-merge was executed correctly:

- the service output stream did not change;
- service counts did not change;
- adaptation latency did not change;
- fault recovery did not change;
- static / oracle comparisons did not change;
- restart reproducibility remained exact;
- safety totals remained zero.

The correction changed the causal / transactional closure that R1 had failed to execute:

provisional partition transitions are now formally closed at re-merge
instead of remaining indefinitely provisional.

Therefore the corrected evidence supports the original intended A03 claim:

THE SAME FROZEN DEVELOPMENTAL POLICY
GENERALIZED ACROSS THE BLIND POST-FREEZE ENVIRONMENT FAMILY
WHILE ALSO EXECUTING THE CLOSED PARTITION / RE-MERGE CONTRACT.

PLAIN-SPEAK INTERPRETATION

The earlier test really did show useful generalization,
but we found that the program had left the partition paperwork open.

FIXA closed that paperwork exactly where it should have.

Nothing about the work the organism performed changed.

It served exactly the same requests,
made exactly the same task decisions,
recovered at the same speed,
and still beat the static population in every blind world.

The difference is that now every split population formally rejoined
and cleared its provisional state before continuing.

So A03 is no longer provisional.

It is accepted as a positive blind-generalization result.

ACCEPTED APPLICATION FRONTIER

YGG-A01:
positive via FIXA.

A02:
positive adaptive transform service.

A03:
positive blind held-out generalization,
accepted via dynamic re-merge FIXA.

NEXT

A04 remains separately preregistered as a fixed-public-seed replication family
with a different environment generator.

Execute A04 unchanged.

canonical_scientific_execution = false.
stab18_r1_touched = false.

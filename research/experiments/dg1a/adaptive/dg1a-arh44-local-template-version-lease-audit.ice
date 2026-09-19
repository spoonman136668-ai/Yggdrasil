TITLE: DG-1A-AR-H44 — Local Lease for Unpromoted Template Versions During Partition
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE REVERSIBLE-LOCAL-AUTHORITY RESULT + LEASE-REVALIDATION REQUIREMENT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh43-decentralized-shared-template-version-convergence-audit.ice

PURPOSE
H43 showed that family template versions can diverge during a temporary communication partition
and later converge safely through provenance-aware functional validation.

But a long-lived partition creates another problem:

WHAT SHOULD A FRAGMENT DO BEFORE FAMILY-WIDE PROMOTION IS POSSIBLE?

If the local niche genuinely changes,
waiting for reconnection may preserve stale function.

If the local candidate is poisoned,
immediate local adoption expands the blast radius.

H44 tests a reversible middle state:

LOCAL PROVISIONAL AUTHORITY LEASE.

BOUNDARY
This is synthetic.

It does not:
- freeze a production lease duration;
- freeze local challenge thresholds;
- authorize unvalidated family-wide template promotion;
- prove real Yggdrasil partition topology;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

FOCUSED LOCAL TEMPLATE AXIS
Current family live value:
0.

Local candidate:
0.8.

Partition duration:
200 synthetic blocks.

Functional lineage variation SD:
0.55.

Local functional consequence noise SD:
0.25.

Each validation block receives:
4 paired local functional samples.

POLICIES

NEVER USE UNPROMOTED VERSION
Continue using family live template:
0

for the entire partition.

IMMEDIATE LOCAL USE
Use candidate:
0.8

as soon as it appears.

No local rollback requirement.

REVERSIBLE LOCAL LEASE
Maintain a local candidate-benefit EMA.

EMA rate:
0.35.

Activation requires:
2 consecutive positive-trust blocks

above exploratory threshold:
0.18.

Once active,
local candidate authority is leased for:

8 blocks.

The lease is:
- local;
- reversible;
- not family-wide promotion.

Candidate authority is revoked if:
local benefit trust falls below:
-0.05

or
the lease expires without renewed evidence.

Constants are synthetic discriminating values only.

SCENARIO A — POISONED LOCAL CANDIDATE
True local family remains:
0.

Candidate:
0.8
is wrong.

500 matched partition runs.

NEVER USE

candidate use fraction:
0%.

functional excess loss:
0.

IMMEDIATE LOCAL USE

candidate use:
100%.

mean excess loss:
0.64 per block.

REVERSIBLE LEASE
Primary activation threshold:
0.18.

candidate use fraction:
0%.

mean excess loss:
0.

Across nearby threshold sweep:

activation threshold 0.10

candidate use:
0.005%.

loss:
0.000032.

threshold 0.15

use:
0.001%.

loss:
0.0000064.

threshold 0.18+

no poisoned lease activations were observed in the tested 500-run primary sweep.

PRIMARY POISON POSITIVE
The local candidate may exist in memory
without receiving:
local expression authority.

This bounds the blast radius of a poisoned partition-local version.

SCENARIO B — GENUINE LOCAL NICHE SHIFT
True local family has moved to:
0.8.

Family-wide live version remains:
0
because the fragment is partitioned.

500 matched runs.

NEVER USE

local excess loss:
0.64 per block.

IMMEDIATE LOCAL USE

excess loss:
0.

REVERSIBLE LEASE

candidate use fraction:
79.45%.

mean excess loss:
0.13149.

The lease does not match immediate oracle use,
but recovers most of the local benefit while retaining reversibility.

PRIMARY LOCAL-ADAPTATION POSITIVE
A fragment can temporarily adapt to a real local niche shift
without waiting for:
family-wide promotion

and
without granting:
permanent shared-template authority.

SCENARIO C — TEMPORARY LOCAL SHIFT / RETURN
200-block run.

True local context:

blocks 0..39:
old family 0.

40..99:
local shift to 0.8.

100..199:
return to 0.

Candidate 0.8 remains available throughout.

1,000 matched runs.

REVERSIBLE LEASE

mean total mismatch loss:
0.04569.

median:
0.0448.

LEASE-ON LATENCY after real shift:

mean:
3.17 blocks.

median:
3.

5th–95th percentile:
2..5.

LEASE-OFF LATENCY after return:

mean:
0.84 blocks.

median:
1.

5th–95th:
0..2.

POST-RETURN STALE CANDIDATE USE:

mean:
0.81%
of post-return blocks.

PRIMARY REVERSIBILITY POSITIVE
The local lease turns on quickly enough to exploit a genuine local change,
but drops almost immediately when the old niche returns.

Thus:
temporary local specialization
does not need to become:
permanent family-template divergence.

RELATION TO H6 / H25
H6 established:

STORED PRIOR
!=
CURRENT EXPRESSION AUTHORITY.

H25 generalized:

STORED CAPABILITY/TRUST STATE
!=
CURRENT AUTHORITY.

H44 applies the same distinction to:
distributed shared-template versions.

A candidate can remain:
stored
and
locally testable

without:
family-wide
or even local
continuous authority.

LOCAL LEASE IS NOT PROMOTION
The lease must not:
- increment family-wide promotion authority by itself;
- overwrite clean replicas;
- create last-writer-wins priority;
- bypass H41/H42 functional promotion logic after reconnection.

It is:
temporary local phenotype/template expression.

Not:
shared hereditary commit.

CURRENT VERSION LIFECYCLE
LOCAL CANDIDATE CREATED

->
stored as:
UNPROMOTED VERSION.

If family connectivity exists:

H43 distributed validation.

If partitioned:

bounded local functional evidence

->
LOCAL LEASE
or
NO LOCAL AUTHORITY.

During lease:

continue local revalidation.

On negative evidence:
revoke.

On reconnection:

candidate enters normal family validation.

Possible outcomes:

PROMOTE FAMILY-WIDE

ROLL BACK

or

remain:
LOCAL SPECIALIZATION.

GENERAL PRINCIPLE
DISTRIBUTED ADAPTATION NEEDS
MORE THAN TWO AUTHORITY STATES.

Not only:

UNTRUSTED
vs
GLOBAL.

Useful hierarchy:

STORED CANDIDATE

->
LOCAL PROVISIONAL LEASE

->
FAMILY PROMOTED VERSION.

This allows:
fast local adaptation
with
bounded systemic blast radius.

DECISION
AR-H44 is POSITIVE.

Supported synthetically:

- never using partition-local candidate versions protects against poison but blocks legitimate local adaptation;
- immediate local use adapts instantly but gives poisoned candidates full local blast radius;
- reversible local leases preserve most legitimate local adaptation benefit;
- poisoned candidates remain effectively suppressed at the tested working point;
- local leases deactivate quickly when the niche reverts;
- local provisional authority can remain separate from family-wide promotion.

Not demonstrated:

- real Yggdrasil local lease representation;
- multiple competing local candidates;
- spatial spread of a locally leased candidate;
- lease propagation across daughter cells;
- lease behavior during long-lived genuine specialization;
- family merge when a local specialization persists.

NEXT CLEAN QUESTION
AR-H45 — PERSISTENT LOCAL SPECIALIZATION VS FAMILY SPLIT

H44 treats local specialization as provisional.

Question:

What if one partition-local specialization persists for a very long time
and repeatedly proves useful?

When should it remain:
a local leased variant

vs
become:
a new generative family branch?

Compare:

A.
permanent local lease only;

B.
immediate family split;

C.
persistence + recurrence + resource-price gated split;

D.
specialization that disappears after a long transient;

E.
specialization that recurs after dormancy.

Desired:

temporary local niche
->
stay local and reversible.

persistent reusable niche
->
eventually earn a compact family branch.

rare recurring specialization
->
retain generative capability without forcing permanent active divergence.

This connects:
H44 local authority
with
H37 family split
and
H34-H36 dormant/generative retirement.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
partition_blocks = 200
primary_partition_runs = 500
temporary_shift_runs = 1000
local_validation_samples_per_block = 4
lease_ema_alpha = 0.35
lease_activation_persistence = 2
lease_duration_blocks = 8

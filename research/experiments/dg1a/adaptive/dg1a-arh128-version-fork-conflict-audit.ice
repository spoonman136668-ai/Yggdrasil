TITLE: DG-1A-AR-H128 — Concurrent Family Updates / Version-Fork Conflict Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE FORK-FIRST CHALLENGE-GATED RECONCILIATION RESULT + SILENT-OVERWRITE / BLIND-MERGE LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh127-staggered-family-version-rollout-audit.ice

PURPOSE
H127 assumes:
one candidate shared translator version
at a time.

H128 asks:

WHAT IF
TWO REGIONS
INDEPENDENTLY DEVELOP:

N+1a

and

N+1b

before:
either update
has:
finished rollout?

The branches may be:

COMPLEMENTARY

or:

SEMANTICALLY INCOMPATIBLE.

BOUNDARY
This is synthetic.

It does not:
- freeze two concurrent branches;
- prove region identity should control version routing;
- freeze the reconciliation challenge;
- establish a production merge algorithm;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

FAMILY
80 members.

Two equal spatial / functional regions.

BASE VERSION
N.

LOCAL BRANCHES

N+1a
developed from:
region A evidence.

N+1b
developed from:
region B evidence.

TWO REGIME TYPES

COMPLEMENTARY BRANCHES
55%
of synthetic worlds.

N+1a improves:
one subset
of translator semantics.

N+1b improves:
a different subset.

The correct reconciled version
contains:
both changes.

REGIONALLY INCOMPATIBLE BRANCHES
45%
of worlds.

N+1a
and
N+1b
modify:
the same semantic dimensions
in:
different directions.

Each branch is:
locally correct
for:
its own region.

There is:
no single merged translator
that is:
globally correct.

COMPARATORS

LAST-WRITER-WINS
N+1a rolls out,
then:
N+1b silently overwrites:
the shared family version.

GLOBAL SERIALIZATION
One global update lock.

N+1a completes,
then:
N+1b is evaluated / installed.

VERSION FORK RETENTION
Region A uses:
N+1a.

Region B:
N+1b.

Cross-branch interaction
uses:
temporary version shims.

No merge attempt.

BLIND AUTO-MERGE
Build:
one combined candidate
from:
both branches

without:
functional compatibility testing.

FORK-FIRST CHALLENGE-GATED RECONCILIATION
First:
allow:
region-specific branch authority.

Then:
run:
a joint functional merge challenge.

If:
combined semantics validate,

promote:
one merged shared version.

If:
not,

retain:
the regional fork.

PRIMARY STREAM
100 steps.

20,000 matched concurrent-update worlds.

LAST-WRITER-WINS

mean value:
5390.16.

10th percentile:
4115.71.

1st:
4019.25.

complementary worlds:
6082.86.

incompatible worlds:
4528.33.

PRIMARY OVERWRITE NEGATIVE
Silent overwrite turns:
local adaptation
into:
shared-state data loss.

N+1b can:
erase:
useful N+1a structure

even when:
the branches are:
complementary.

GLOBAL SERIALIZATION

mean:
5414.16.

10th:
4228.94.

1st:
4100.33.

complementary:
6036.44.

incompatible:
4639.95.

PRIMARY GLOBAL-LOCK LIMIT
Serialization prevents:
concurrent write conflict

but:
throws away:
regional concurrency
and:
delays:
useful local adaptation.

Safety through:
one global update lock
has:
real opportunity cost.

VERSION FORK RETENTION

mean:
6588.67.

10th:
5610.07.

1st:
5221.64.

complementary:
5924.13.

incompatible:
7415.46.

PRIMARY FORK POSITIVE
Temporary region-specific branch authority
strongly improves:
incompatible worlds.

Each region keeps:
its locally valid semantics.

However:
complementary worlds
remain:
under-integrated.

The branches fail to:
share:
useful independent improvements.

BLIND AUTO-MERGE

mean:
6742.89.

10th:
5750.96.

1st:
5172.74.

complementary:
7261.44.

incompatible:
6097.72.

PRIMARY BLIND-MERGE NEGATIVE
Automatic reconciliation
works well
when:
the branches truly compose.

But:
merging incompatible regional semantics
creates:
a false shared version.

The result is:
worse
than:
keeping:
the fork.

FORK-FIRST CHALLENGE-GATED RECONCILIATION

mean:
7197.44.

10th:
6975.05.

1st:
5738.16.

complementary worlds:
7088.12.

incompatible:
7333.45.

PRIMARY RECONCILIATION POSITIVE
The strongest policy does not:

force:
one version

and does not:

keep:
every fork forever.

It permits:
temporary branch-local authority

then:
tests
whether:
the branches can:
safely reconcile.

MERGE CHALLENGE
Primary synthetic merge test:

true complementary branch
accepted:
96.28%.

incompatible branch
falsely merged:
3.77%.

Thus:
the reconciliation stage
strongly separates:

COMPOSABLE DIVERGENCE

from:

LEGITIMATE REGIONAL SPECIALIZATION.

VERSION-FORK OBJECT
A shared translator family may temporarily contain:

COMMON ANCESTOR VERSION

+

BRANCH A

+

BRANCH B

+

REGION / CONTEXT AUTHORITY

+

CROSS-BRANCH SHIM

+

MERGE-CANDIDATE STATE

+

RECONCILIATION CANARY SUPPORT

+

BRANCH EXPIRY / RETENTION VALUE.

The fork is:
explicit state.

Not:
write corruption.

RELATION TO H39
H39:
shared memory benefits from:
candidate versioning.

H128:
one candidate is not always enough.

Concurrent local adaptation
can produce:
multiple:
legitimate descendants.

RELATION TO H83
H83:
functional equivalence is:
context-bounded.

H128:
version authority
can also be:
context-bounded.

Two versions may both be:
correct

under:
different local regimes.

RELATION TO H100
H100:
causal theories can:
recombine
when:
their modules are:
compatible.

H128:
shared interface versions
can also:
reconcile

only after:
composition evidence.

GENERAL PRINCIPLE
WHEN:
CONCURRENT LOCAL ADAPTATION
CREATES:
VERSION FORKS,

DO NOT:

LAST-WRITER-WINS

and do not:

AUTO-MERGE.

Prefer:

FORK

->
LOCAL AUTHORITY

->
FUNCTIONAL RECONCILIATION CHALLENGE

->
MERGE
OR
RETAIN SPECIALIZATION.

DECISION
AR-H128 is POSITIVE
for:
FORK-FIRST CHALLENGE-GATED VERSION RECONCILIATION

WITH:
SILENT-OVERWRITE
AND
BLIND-MERGE LIMITS.

Supported synthetically:

- last-writer-wins destroys useful concurrent adaptation;
- global serialization sacrifices local adaptation speed;
- explicit version forks preserve regionally incompatible semantics;
- permanent forks leave complementary improvements fragmented;
- blind merge fails on incompatible branches;
- functional merge challenge successfully distinguishes most composable from incompatible branch pairs;
- branch-local authority can coexist with later shared reconciliation.

Not demonstrated:

- more than two concurrent branches;
- deep branch ancestry;
- distributed merge authority;
- branch memory pricing;
- region migration;
- malicious branch generation.

NEXT HIGH-VALUE MOVE
AR-H129 — VERSION-FORK ECOLOGY / BRANCH PROLIFERATION AND SPECIATION AUDIT

H128 permits:
temporary version forks.

Question:

WHAT HAPPENS
WHEN:
MANY REGIONS
KEEP CREATING
LOCAL DESCENDANTS?

Potential failure:

the shared translator family
becomes:
a branching version tree
with:
ever-growing:
memory,
shims,
and:
reconciliation cost.

Compare:

A.
retain every branch;

B.
force early merge;

C.
memory-priced branch ecology;

D.
merge:
compatible branches;

E.
speciate:
persistently incompatible branches
into:
separate translator families;

F.
old regional regime returns.

Desired:

TEMPORARY FORK
should either:

RECONCILE

or:

BECOME
A JUSTIFIED NEW FAMILY.

It should not remain:
permanent ambiguous version debt.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
matched_worlds = 20000
complementary_fraction = 0.55
last_writer_mean = 5390.1624
fork_mean = 6588.6683
blind_merge_mean = 6742.8858
gated_reconciliation_mean = 7197.4393
true_merge_acceptance = 0.96284
false_merge_acceptance = 0.03770
